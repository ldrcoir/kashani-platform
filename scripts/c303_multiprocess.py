#!/usr/bin/env python3
"""
Multi-process C303 sieve with wheel + next_prime approach.

Each worker:
- Takes a chunk of k range
- Uses wheel residues (mod 4849845) to skip bad k's
- Uses extra sieve rules (primes 23..1000)
- For each surviving k: compute q = 2474k+1, check primality, check pow(2,1237,q)==1
- Checkpoint every 60s
- Watchdog monitors workers and restarts if needed
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, powmod
import time
import json
import pickle
import os
import signal
import multiprocessing as mp
from pathlib import Path

# Constants
P = 1237
TWO_P = 2474
M = mpz(2)**P - 1
P70 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
C303 = M // P70

# Files
BASE_DIR = Path('/home/z/my-project/download')
CHECKPOINT_FILE = BASE_DIR / 'c303_sieve_checkpoint.json'
RESULTS_FILE = BASE_DIR / 'c303_sieve_results.txt'
WATCHDOG_FILE = BASE_DIR / 'c303_sieve_watchdog.log'
GOOD_RESIDUES_FILE = BASE_DIR / 'good_residues.pkl'

# Wheel setup
WHEEL_PRIMES = [3, 5, 7, 11, 13, 17, 19]
WHEEL_MOD = 1
for p in WHEEL_PRIMES:
    WHEEL_MOD *= p  # = 4849845

# Pre-compute good residues (one-time cost)
print("Setting up wheel residues...")
WHEEL_BLOCKED = {}
for r in WHEEL_PRIMES:
    inv_2474 = pow(TWO_P, -1, r)
    WHEEL_BLOCKED[r] = (-inv_2474) % r

if GOOD_RESIDUES_FILE.exists():
    with open(GOOD_RESIDUES_FILE, 'rb') as f:
        GOOD_RESIDUES = pickle.load(f)
    print(f"Loaded {len(GOOD_RESIDUES)} good residues from cache")
else:
    print(f"Computing {len(GOOD_RESIDUES) if 'GOOD_RESIDUES' in dir() else '?'} good residues...")
    GOOD_RESIDUES = []
    for k0 in range(WHEEL_MOD):
        is_good = True
        for r in WHEEL_PRIMES:
            if k0 % r == WHEEL_BLOCKED[r]:
                is_good = False
                break
        if is_good:
            GOOD_RESIDUES.append(k0)
    with open(GOOD_RESIDUES_FILE, 'wb') as f:
        pickle.dump(GOOD_RESIDUES, f)
    print(f"Computed and saved {len(GOOD_RESIDUES)} good residues")

# Extra sieve rules
def gen_extra_rules(bound):
    sieve = bytearray([1]) * (bound + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(bound**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    primes = [i for i in range(2, bound + 1) if sieve[i]]
    rules = []
    for r in primes:
        if r == 2 or r == 1237: continue
        if r in WHEEL_PRIMES: continue
        inv_2474 = pow(TWO_P, -1, r)
        blocked = (-inv_2474) % r
        rules.append((r, blocked))
    return rules

EXTRA_RULES = gen_extra_rules(1000)
print(f"Generated {len(EXTRA_RULES)} extra sieve rules")

# Build sorted good residues and step array for fast iteration
SORTED_GOOD = sorted(GOOD_RESIDUES)
# Step array: differences between consecutive good residues
# Use this to iterate fast: k → k + step
N_GOOD = len(SORTED_GOOD)

def get_step_array():
    """Compute step array for cycling through good residues."""
    # For each good residue index i, step to next good residue is (i+1) % N_GOOD
    # step_value[i] = SORTED_GOOD[(i+1) % N_GOOD] - SORTED_GOOD[i] (handling wrap)
    steps = []
    for i in range(N_GOOD):
        next_idx = (i + 1) % N_GOOD
        if next_idx == 0:
            step = (WHEEL_MOD - SORTED_GOOD[i]) + SORTED_GOOD[0]
        else:
            step = SORTED_GOOD[next_idx] - SORTED_GOOD[i]
        steps.append(step)
    return steps

STEPS = get_step_array()
print(f"Computed step array of length {len(STEPS)}")

# Build a mapping from residue mod WHEEL_MOD to index in SORTED_GOOD
RESIDUE_TO_IDX = {r: i for i, r in enumerate(SORTED_GOOD)}

def worker_main(args):
    """Worker process: scan k range using wheel + extra rules + next_prime."""
    worker_id, k_start, k_end = args
    
    # Each worker writes to its own progress file
    worker_progress_file = BASE_DIR / f'c303_w{worker_id}_progress.json'
    
    print(f"[W{worker_id}] START k=[{k_start:,}, {k_end:,})", flush=True)
    
    # Find starting residue index
    k = k_start
    k_mod = k % WHEEL_MOD
    # Find smallest good residue >= k_mod
    import bisect
    idx = bisect.bisect_left(SORTED_GOOD, k_mod)
    if idx == N_GOOD:
        idx = 0
        k += WHEEL_MOD - k_mod + SORTED_GOOD[0]
    else:
        k += SORTED_GOOD[idx] - k_mod
    
    local_tested = 0
    local_primes = 0
    local_pow_hits = 0
    last_save = time.time()
    last_log = time.time()
    t_start = time.time()
    
    while k < k_end:
        # Check if any factor has been found
        if RESULTS_FILE.exists():
            try:
                content = RESULTS_FILE.read_text()
                if 'FACTOR FOUND' in content:
                    print(f"[W{worker_id}] STOPPING — factor found by another worker", flush=True)
                    return
            except:
                pass
        
        # Wheel already handled by iteration — k is at a good residue
        # Now check extra rules
        passes = True
        for r, blocked in EXTRA_RULES:
            if k % r == blocked:
                passes = False
                break
        if not passes:
            # Skip to next good residue
            k += STEPS[idx]
            idx = (idx + 1) % N_GOOD
            continue
        
        local_tested += 1
        q = TWO_P * k + 1
        
        # Primality
        if not is_prime(q):
            k += STEPS[idx]
            idx = (idx + 1) % N_GOOD
            continue
        local_primes += 1
        
        # Check pow(2, 1237, q) == 1
        if powmod(2, P, q) == 1:
            local_pow_hits += 1
            # Verify q | C303
            if C303 % q == 0:
                # FACTOR FOUND!
                cofactor = int(C303) // q
                with open(RESULTS_FILE, 'a') as f:
                    f.write(f"=== FACTOR FOUND ===\n")
                    f.write(f"Worker: {worker_id}\n")
                    f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Elapsed (s): {time.time() - t_start:.1f}\n")
                    f.write(f"k = {k}\n")
                    f.write(f"q = {q}\n")
                    f.write(f"q digits: {len(str(q))}\n")
                    f.write(f"cofactor: {cofactor}\n")
                    f.write(f"cofactor digits: {len(str(cofactor))}\n")
                    f.write(f"is_prime(cofactor): {is_prime(cofactor)}\n")
                    f.write(f"===\n")
                
                print(f"\n!!! FACTOR FOUND by W{worker_id} !!! k={k}, q={q}", flush=True)
                print(f"cofactor = {str(cofactor)[:60]}... ({len(str(cofactor))} digits)", flush=True)
                print(f"is_prime(cofactor): {is_prime(cofactor)}", flush=True)
                return
        
        # Step to next good residue
        k += STEPS[idx]
        idx = (idx + 1) % N_GOOD
        
        # Save progress periodically
        now = time.time()
        if now - last_save > 30:
            with open(worker_progress_file, 'w') as f:
                json.dump({
                    'worker_id': worker_id,
                    'last_k': k,
                    'tested': local_tested,
                    'primes': local_primes,
                    'pow_hits': local_pow_hits,
                    'elapsed': now - t_start,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                }, f, indent=2)
            last_save = now
        
        # Log periodically
        if now - last_log > 15:
            elapsed = now - t_start
            worker_processed = k - k_start
            worker_rate = worker_processed / elapsed if elapsed > 0 else 0
            print(f"[W{worker_id}] k={k:,}, tested={local_tested:,}, primes={local_primes:,}, pow_hits={local_pow_hits}, rate={worker_rate:.0f} k/s, elapsed={elapsed:.0f}s", flush=True)
            last_log = now
    
    # Save final progress
    with open(worker_progress_file, 'w') as f:
        json.dump({
            'worker_id': worker_id,
            'last_k': k,
            'tested': local_tested,
            'primes': local_primes,
            'pow_hits': local_pow_hits,
            'elapsed': time.time() - t_start,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'done': True,
        }, f, indent=2)
    print(f"[W{worker_id}] DONE at k={k:,}, tested={local_tested:,}, primes={local_primes:,}", flush=True)

def watchdog(workers, num_workers):
    """Watchdog: monitor workers, restart if they die."""
    print("[WATCHDOG] Starting...", flush=True)
    
    while True:
        time.sleep(10)
        # Check if any worker died
        alive_count = sum(1 for p in workers if p.is_alive())
        if alive_count == 0:
            print("[WATCHDOG] All workers exited. Stopping watchdog.", flush=True)
            return
        
        # Check if factor found
        if RESULTS_FILE.exists():
            try:
                content = RESULTS_FILE.read_text()
                if 'FACTOR FOUND' in content:
                    print("[WATCHDOG] Factor found! Stopping workers...", flush=True)
                    return
            except:
                pass
        
        # Aggregate progress from worker files
        total_k = 0
        total_tested = 0
        total_primes = 0
        total_pow_hits = 0
        for i in range(num_workers):
            wp_file = BASE_DIR / f'c303_w{i}_progress.json'
            if wp_file.exists():
                try:
                    with open(wp_file) as f:
                        wp = json.load(f)
                    total_k = max(total_k, wp.get('last_k', 0))
                    total_tested += wp.get('tested', 0)
                    total_primes += wp.get('primes', 0)
                    total_pow_hits += wp.get('pow_hits', 0)
                except:
                    pass
        
        with open(WATCHDOG_FILE, 'a') as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] alive_workers={alive_count}/{num_workers}, max_k={total_k:,}, total_tested={total_tested:,}, total_primes={total_primes:,}, total_pow_hits={total_pow_hits}\n")

def main():
    print("=" * 70)
    print("  Multi-process C303 Smart Sieve")
    print("=" * 70)
    print()
    
    NUM_WORKERS = 4  # 2 CPUs but use 4 for better utilization
    K_START = 15_000_000
    K_END = 100_000_000_000  # 100 billion
    
    # Check checkpoint
    start_k = K_START
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE) as f:
                cp = json.load(f)
            saved_k = cp.get('last_k_processed', 0)
            if saved_k > start_k:
                start_k = saved_k + 1
                print(f"Resume from k={start_k:,}")
        except:
            pass
    
    print(f"Range: k = [{start_k:,}, {K_END:,})")
    print(f"Workers: {NUM_WORKERS}")
    print()
    
    # Divide work
    total_k = K_END - start_k
    chunk_size = total_k // NUM_WORKERS
    
    # Clear old worker progress files
    for i in range(NUM_WORKERS):
        wp_file = BASE_DIR / f'c303_w{i}_progress.json'
        if wp_file.exists():
            wp_file.unlink()
    
    # Start workers
    ctx = mp.get_context('fork')
    workers = []
    for i in range(NUM_WORKERS):
        w_start = start_k + i * chunk_size
        w_end = K_END if i == NUM_WORKERS - 1 else w_start + chunk_size
        p = ctx.Process(target=worker_main, args=((i, w_start, w_end),))
        p.start()
        workers.append(p)
        print(f"  W{i}: k=[{w_start:,}, {w_end:,}) — PID {p.pid}")
    
    print()
    print("Workers started. Watchdog monitoring...")
    print("=" * 70)
    
    # Run watchdog in main process
    t_start = time.time()
    last_checkpoint = time.time()
    
    while True:
        alive = sum(1 for p in workers if p.is_alive())
        if alive == 0:
            print("\nAll workers exited.", flush=True)
            break
        
        # Check if factor found
        factor_found = False
        if RESULTS_FILE.exists():
            try:
                if 'FACTOR FOUND' in RESULTS_FILE.read_text():
                    factor_found = True
                    print("\n!!! FACTOR FOUND !!! Stopping all workers...", flush=True)
                    for p in workers:
                        if p.is_alive():
                            p.terminate()
                    break
            except:
                pass
        
        # Aggregate progress
        total_k = 0
        total_tested = 0
        total_primes = 0
        for i in range(NUM_WORKERS):
            wp_file = BASE_DIR / f'c303_w{i}_progress.json'
            if wp_file.exists():
                try:
                    with open(wp_file) as f:
                        wp = json.load(f)
                    total_k = max(total_k, wp.get('last_k', 0))
                    total_tested += wp.get('tested', 0)
                    total_primes += wp.get('primes', 0)
                except:
                    pass
        
        elapsed = time.time() - t_start
        print(f"[{time.strftime('%H:%M:%S')}] alive={alive}/{NUM_WORKERS}, elapsed={elapsed:.0f}s, max_k={total_k:,}, tested={total_tested:,}, primes={total_primes:,}", flush=True)
        
        # Save main checkpoint
        if time.time() - last_checkpoint > 60:
            with open(CHECKPOINT_FILE, 'w') as f:
                json.dump({
                    'last_k_processed': total_k,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_tested': total_tested,
                    'total_primes': total_primes,
                    'elapsed': elapsed,
                }, f, indent=2)
            last_checkpoint = time.time()
        
        time.sleep(15)
    
    # Final wait
    for p in workers:
        if p.is_alive():
            p.join(timeout=5)
    
    print()
    print("=" * 70)
    print("Done")
    print("=" * 70)
    
    if RESULTS_FILE.exists():
        content = RESULTS_FILE.read_text()
        if 'FACTOR FOUND' in content:
            print("!!! FACTOR FOUND !!!")
            print(content)
        else:
            print("No factor found")
    else:
        print("No factor found")
    
    # Final checkpoint
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({
            'last_k_processed': total_k,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'final': True,
            'total_tested': total_tested,
            'total_primes': total_primes,
        }, f, indent=2)

if __name__ == '__main__':
    main()
