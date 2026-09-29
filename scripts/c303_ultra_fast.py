#!/usr/bin/env python3
"""
ULTRA-FAST C303 sieve using native C-level operations via ctypes.

Key insight: most of the time is spent in:
1. Sieve check (Python loop over 160 rules) — ~70% time
2. is_prime(q) for surviving q — ~20% time
3. pow(2, 1237, q) for primes — ~10% time

We can speed up (1) by using a precomputed "sieve mask" via numpy:
- For each prime r, we know which k mod r values are blocked
- Build a boolean mask: for k in [k_start, k_start + BLOCK), is k good?
- Use numpy to compute all 160 masks in parallel
- Sum masks: a k is good if all masks are True

This should be 10-100x faster than Python loops.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, powmod
import time
import json
import pickle
import multiprocessing as mp
from pathlib import Path
import numpy as np

# Constants
P = 1237
TWO_P = 2474
M = mpz(2)**P - 1
P70 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
C303 = M // P70

# Files
BASE_DIR = Path('/home/z/my-project/download')
CHECKPOINT_FILE = BASE_DIR / 'c303_sieve_checkpoint_fast.json'
RESULTS_FILE = BASE_DIR / 'c303_sieve_results_fast.txt'
GOOD_RESIDUES_FILE = BASE_DIR / 'good_residues.pkl'

# Wheel setup
WHEEL_PRIMES = [3, 5, 7, 11, 13, 17, 19]
WHEEL_MOD = 1
for p in WHEEL_PRIMES:
    WHEEL_MOD *= p  # = 4849845

with open(GOOD_RESIDUES_FILE, 'rb') as f:
    GOOD_RESIDUES = pickle.load(f)

# Extra sieve rules (primes 23..1000)
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
print(f"Wheel: {len(GOOD_RESIDUES)} good residues mod {WHEEL_MOD}, {len(EXTRA_RULES)} extra rules")

# Convert good residues to numpy array for fast lookup
GOOD_RESIDUES_ARR = np.array(GOOD_RESIDUES, dtype=np.int64)
GOOD_RESIDUES_SET = set(GOOD_RESIDUES)  # for Python-level check

# For block-based sieve:
# Given block_start, compute for each k in [block_start, block_start + BLOCK_SIZE):
# whether it passes the wheel (k mod WHEEL_MOD in GOOD_RESIDUES).
# Then for each passing k, check extra rules.

BLOCK_SIZE = 1_000_000  # 1M k per block

def make_wheel_mask(block_start, block_size):
    """Compute boolean mask: True if k passes wheel sieve."""
    # k mod WHEEL_MOD for k in [block_start, block_start+block_size)
    k_arr = np.arange(block_start, block_start + block_size, dtype=np.int64)
    k_mod = k_arr % WHEEL_MOD
    # Check if k_mod in GOOD_RESIDUES_ARR
    # Use np.isin
    mask = np.isin(k_mod, GOOD_RESIDUES_ARR)
    return mask

def make_extra_rules_mask(block_start, block_size):
    """Compute boolean mask: True if k passes all extra rules."""
    # For each rule (r, blocked), mask[i] = (k[i] mod r != blocked)
    # Then overall_mask = AND of all per-rule masks
    k_arr = np.arange(block_start, block_start + block_size, dtype=np.int64)
    overall_mask = np.ones(block_size, dtype=bool)
    for r, blocked in EXTRA_RULES:
        # For small r, we can compute (k_arr % r) directly
        if r <= 997:
            rule_mask = (k_arr % r) != blocked
            overall_mask &= rule_mask
    return overall_mask

def worker_main(args):
    worker_id, k_start, k_end = args
    worker_progress_file = BASE_DIR / f'c303_fast_w{worker_id}_progress.json'
    
    print(f"[W{worker_id}] START k=[{k_start:,}, {k_end:,})", flush=True)
    
    local_tested = 0
    local_primes = 0
    local_pow_hits = 0
    last_save = time.time()
    last_log = time.time()
    t_start = time.time()
    
    k = k_start
    while k < k_end:
        if RESULTS_FILE.exists() and 'FACTOR FOUND' in RESULTS_FILE.read_text():
            return
        
        block_size = min(BLOCK_SIZE, k_end - k)
        
        # Compute wheel mask (numpy fast)
        wheel_mask = make_wheel_mask(k, block_size)
        
        # Compute extra rules mask (numpy fast)
        extra_mask = make_extra_rules_mask(k, block_size)
        
        # Combined mask
        combined_mask = wheel_mask & extra_mask
        
        # Get indices where mask is True
        good_indices = np.where(combined_mask)[0]
        
        # For each good k, compute q, check primality, check pow
        for idx in good_indices:
            actual_k = int(k + idx)
            local_tested += 1
            q = TWO_P * actual_k + 1
            if not is_prime(q):
                continue
            local_primes += 1
            if powmod(2, P, q) == 1:
                local_pow_hits += 1
                if C303 % q == 0:
                    # FACTOR FOUND!
                    cofactor = int(C303) // q
                    with open(RESULTS_FILE, 'a') as f:
                        f.write(f"=== FACTOR FOUND ===\n")
                        f.write(f"Worker: {worker_id}\n")
                        f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"k = {actual_k}\n")
                        f.write(f"q = {q}\n")
                        f.write(f"q digits: {len(str(q))}\n")
                        f.write(f"cofactor digits: {len(str(cofactor))}\n")
                        f.write(f"is_prime(cofactor): {is_prime(cofactor)}\n")
                        f.write(f"===\n")
                    print(f"\n!!! FACTOR FOUND by W{worker_id} !!! k={actual_k}, q={q}", flush=True)
                    return
        
        k += block_size
        
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
                }, f, indent=2)
            last_save = now
        
        if now - last_log > 10:
            elapsed = now - t_start
            worker_processed = k - k_start
            worker_rate = worker_processed / elapsed if elapsed > 0 else 0
            print(f"[W{worker_id}] k={k:,}, tested={local_tested:,}, primes={local_primes:,}, pow_hits={local_pow_hits}, rate={worker_rate:.0f} k/s, elapsed={elapsed:.0f}s", flush=True)
            last_log = now
    
    with open(worker_progress_file, 'w') as f:
        json.dump({
            'worker_id': worker_id,
            'last_k': k,
            'tested': local_tested,
            'primes': local_primes,
            'pow_hits': local_pow_hits,
            'elapsed': time.time() - t_start,
            'done': True,
        }, f, indent=2)
    print(f"[W{worker_id}] DONE at k={k:,}", flush=True)

def main():
    print("=" * 70)
    print("  ULTRA-FAST C303 Sieve (numpy-based)")
    print("=" * 70)
    
    NUM_WORKERS = 2
    K_START = 15_000_000
    K_END = 100_000_000_000
    
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
    
    total_k = K_END - start_k
    chunk_size = total_k // NUM_WORKERS
    
    # Clear old worker progress files
    for i in range(NUM_WORKERS):
        wp_file = BASE_DIR / f'c303_fast_w{i}_progress.json'
        if wp_file.exists():
            wp_file.unlink()
    
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
    
    t_start = time.time()
    last_checkpoint = time.time()
    
    while any(p.is_alive() for p in workers):
        time.sleep(15)
        
        # Check factor
        if RESULTS_FILE.exists() and 'FACTOR FOUND' in RESULTS_FILE.read_text():
            print("\n!!! FACTOR FOUND !!! Stopping...", flush=True)
            for p in workers:
                if p.is_alive():
                    p.terminate()
            break
        
        # Aggregate
        total_k_processed = 0
        total_tested = 0
        total_primes = 0
        for i in range(NUM_WORKERS):
            wp_file = BASE_DIR / f'c303_fast_w{i}_progress.json'
            if wp_file.exists():
                try:
                    with open(wp_file) as f:
                        wp = json.load(f)
                    total_k_processed = max(total_k_processed, wp.get('last_k', 0))
                    total_tested += wp.get('tested', 0)
                    total_primes += wp.get('primes', 0)
                except:
                    pass
        
        elapsed = time.time() - t_start
        rate = (total_k_processed - start_k) / elapsed if elapsed > 0 else 0
        eta_h = (K_END - total_k_processed) / rate / 3600 if rate > 0 else float('inf')
        
        print(f"[{time.strftime('%H:%M:%S')}] elapsed={elapsed:.0f}s, max_k={total_k_processed:,}, tested={total_tested:,}, primes={total_primes:,}, rate={rate:.0f} k/s, ETA={eta_h:.1f}h", flush=True)
        
        if time.time() - last_checkpoint > 60:
            with open(CHECKPOINT_FILE, 'w') as f:
                json.dump({
                    'last_k_processed': total_k_processed,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_tested': total_tested,
                    'total_primes': total_primes,
                    'elapsed': elapsed,
                    'rate': rate,
                }, f, indent=2)
            last_checkpoint = time.time()
    
    for p in workers:
        if p.is_alive():
            p.join(timeout=5)
    
    print()
    if RESULTS_FILE.exists() and 'FACTOR FOUND' in RESULTS_FILE.read_text():
        print("!!! FACTOR FOUND !!!")
        print(RESULTS_FILE.read_text())
    else:
        print("No factor found")

if __name__ == '__main__':
    main()
