#!/usr/bin/env python3
"""
Final version: Wheel-based smart sieve for C303.

Setup:
- Wheel with primes [3, 5, 7, 11, 13, 17, 19] (mod 4849845)
- Good residues: 1,658,880 of 4,849,845 (34.20%)
- Plus 160 extra sieve rules for primes 23..997

Speed gain:
- Sieve check skips a Python loop of 167 (or 1227) rules
- Just iterate over good residues directly
- Use extra rules as a second filter for primes > 19

Algorithm per worker:
- Start at k_start
- Find the smallest k >= k_start such that k mod WHEEL_MOD is in good_residues
- Then iterate: k, k + step, k + 2*step, ...
  where step is the difference between consecutive good residues
- For each k: check 160 extra rules (fast Python loop)
- If passes: compute q = 2474*k + 1, check is_prime, then pow(2, 1237, q) == 1
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, powmod
import math
import time
import json
import pickle
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
GOOD_RESIDUES_FILE = BASE_DIR / 'good_residues.pkl'

# Wheel setup
WHEEL_PRIMES = [3, 5, 7, 11, 13, 17, 19]
WHEEL_MOD = 1
for p in WHEEL_PRIMES:
    WHEEL_MOD *= p  # = 4849845

# Generate good residues if not cached
if not GOOD_RESIDUES_FILE.exists():
    print(f"Computing good residues mod {WHEEL_MOD}...")
    wheel_blocked = {}
    for r in WHEEL_PRIMES:
        inv_2474 = pow(TWO_P, -1, r)
        blocked = (-inv_2474) % r
        wheel_blocked[r] = blocked
    
    good_residues = []
    for k0 in range(WHEEL_MOD):
        is_good = True
        for r in WHEEL_PRIMES:
            if k0 % r == wheel_blocked[r]:
                is_good = False
                break
        if is_good:
            good_residues.append(k0)
    
    with open(GOOD_RESIDUES_FILE, 'wb') as f:
        pickle.dump(good_residues, f)
    print(f"Saved {len(good_residues)} good residues")
else:
    with open(GOOD_RESIDUES_FILE, 'rb') as f:
        good_residues = pickle.load(f)
    print(f"Loaded {len(good_residues)} good residues from cache")

# Generate extra sieve rules (primes 23..1000)
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

EXTRA_RULES = gen_extra_rules(bound=1000)
print(f"Extra sieve rules (bound=1000): {len(EXTRA_RULES)}")

# Globals for workers (set in main before fork)
GOOD_RESIDUES_SET = None  # set of good residues mod WHEEL_MOD
EXTRA_RULES_GLOBAL = None

def check_k_range(args):
    """Worker: check k values in [k_start, k_end) using wheel + extra sieve."""
    worker_id, k_start, k_end, progress_dict, stop_event, start_time, good_residues_list, extra_rules_list = args
    
    # Use the passed good_residues list
    good_set = set(good_residues_list)  # local set, fast lookup
    rules = extra_rules_list
    
    # Find the first k >= k_start that is a good residue
    k = k_start
    k_mod = k % WHEEL_MOD
    
    # Binary search for first good residue >= k_mod
    import bisect
    sorted_good = sorted(good_residues)
    idx = bisect.bisect_left(sorted_good, k_mod)
    if idx == len(sorted_good):
        # wrap around
        idx = 0
        k += WHEEL_MOD - k_mod + sorted_good[0]
    else:
        k += sorted_good[idx] - k_mod
    
    # Compute step array: differences between consecutive good residues
    # This lets us iterate fast without sieve check
    # Actually, simpler: iterate k, and use set lookup
    good_set = GOOD_RESIDUES_SET  # use set for O(1) check
    
    local_tested = 0
    local_skipped_wheel = 0
    local_skipped_extra = 0
    local_primes = 0
    last_print = time.time()
    
    while k < k_end and not stop_event.is_set():
        # Wheel check (fast set lookup)
        if (k % WHEEL_MOD) not in good_set:
            local_skipped_wheel += 1
            k += 1
            continue
        
        # Extra sieve check
        passes = True
        for r, blocked in rules:
            if k % r == blocked:
                passes = False
                break
        if not passes:
            local_skipped_extra += 1
            k += 1
            continue
        
        # Compute q and check primality
        local_tested += 1
        q = TWO_P * k + 1
        if not is_prime(q):
            k += 1
            continue
        local_primes += 1
        
        # Check if q | M(1237) via Fermat
        if powmod(2, P, q) == 1:
            # Verify q | C303
            if C303 % q == 0:
                # FACTOR FOUND!
                with open(RESULTS_FILE, 'a') as f:
                    cofactor = int(C303) // q
                    f.write(f"=== FACTOR FOUND ===\n")
                    f.write(f"Worker: {worker_id}\n")
                    f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"k = {k}\n")
                    f.write(f"q = {q}\n")
                    f.write(f"q digits: {len(str(q))}\n")
                    f.write(f"cofactor: {cofactor}\n")
                    f.write(f"cofactor digits: {len(str(cofactor))}\n")
                    f.write(f"is_prime(cofactor): {is_prime(cofactor)}\n")
                    f.write(f"===\n")
                
                stop_event.set()
                msg = f"\n!!! FACTOR FOUND by worker {worker_id} !!!\n"
                msg += f"k = {k}\n"
                msg += f"q = {q}\n"
                msg += f"q digits: {len(str(q))}\n"
                cofactor = int(C303) // q
                msg += f"cofactor = {str(cofactor)[:60]}... ({len(str(cofactor))} digits)\n"
                msg += f"is_prime(cofactor): {is_prime(cofactor)}\n"
                print(msg, flush=True)
                return (k, local_tested, local_skipped_wheel + local_skipped_extra, local_primes, [(k, q)])
            # else: pow(2, 1237, q) == 1 but q does not divide C303 → q divides P70
            # But q < P70, so this shouldn't happen
        
        # Progress update
        if (k - k_start) % 100_000 == 0 and k > k_start:
            progress_dict[worker_id] = (k, local_tested, local_skipped_wheel + local_skipped_extra, local_primes)
            now = time.time()
            if now - last_print > 15:
                elapsed = now - start_time
                worker_processed = k - k_start
                worker_rate = worker_processed / elapsed if elapsed > 0 else 0
                print(f"[W{worker_id}] k={k:,}, tested={local_tested:,}, skipW={local_skipped_wheel:,}, skipE={local_skipped_extra:,}, primes={local_primes:,}, rate={worker_rate:.0f} k/s", flush=True)
                last_print = now
        
        k += 1
    
    progress_dict[worker_id] = (k, local_tested, local_skipped_wheel + local_skipped_extra, local_primes)
    print(f"[W{worker_id}] DONE at k={k:,}, tested={local_tested:,}, skipW={local_skipped_wheel:,}, skipE={local_skipped_extra:,}, primes={local_primes:,}", flush=True)
    return (k, local_tested, local_skipped_wheel + local_skipped_extra, local_primes, [])

def main():
    print("=" * 70)
    print("  Smart Sieve v3 (Wheel-based) for C303")
    print("=" * 70)
    print()
    print(f"C303 = (2^1237 - 1) / P70")
    print(f"C303 digits: {len(str(C303))}")
    print()
    
    K_START_DEFAULT = 15_000_000
    K_END = 100_000_000_000
    NUM_WORKERS = 8
    CHECKPOINT_EVERY_SEC = 60
    
    # Load checkpoint
    start_k = K_START_DEFAULT
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE) as f:
                cp = json.load(f)
            saved_k = cp.get('last_k_processed', 0)
            if saved_k > start_k:
                start_k = saved_k + 1
                print(f"Checkpoint loaded: resuming from k = {start_k:,}")
            else:
                print(f"Starting fresh from k = {start_k:,}")
        except Exception as e:
            print(f"Checkpoint load failed: {e}")
    
    print(f"Range: k from {start_k:,} to {K_END:,}")
    print(f"Workers: {NUM_WORKERS}")
    print()
    
    # Divide work
    total_k = K_END - start_k
    chunk_size = total_k // NUM_WORKERS
    
    manager = mp.Manager()
    progress_dict = manager.dict()
    stop_event = manager.Event()
    for i in range(NUM_WORKERS):
        progress_dict[i] = (start_k + i * chunk_size, 0, 0, 0)
    
    worker_args = []
    for i in range(NUM_WORKERS):
        w_start = start_k + i * chunk_size
        w_end = K_END if i == NUM_WORKERS - 1 else w_start + chunk_size
        worker_args.append((i, w_start, w_end, progress_dict, stop_event, time.time(), good_residues, EXTRA_RULES))
        print(f"  W{i}: k = [{w_start:,}, {w_end:,})")
    
    print()
    print("Starting workers...")
    print("=" * 70)
    
    ctx = mp.get_context('fork')
    workers = []
    for args in worker_args:
        p = ctx.Process(target=check_k_range, args=(args,))
        p.start()
        workers.append(p)
    
    last_checkpoint_time = time.time()
    t_start = time.time()
    
    try:
        while any(p.is_alive() for p in workers):
            time.sleep(5)
            
            total_tested = 0
            total_skipped = 0
            total_primes = 0
            max_k = 0
            for i in range(NUM_WORKERS):
                if i in progress_dict:
                    k_val, tested, skipped, primes = progress_dict[i]
                    total_tested += tested
                    total_skipped += skipped
                    total_primes += primes
                    if k_val > max_k:
                        max_k = k_val
            
            elapsed = time.time() - t_start
            total_processed = total_tested + total_skipped
            rate = total_processed / elapsed if elapsed > 0 else 0
            
            print(f"[{time.strftime('%H:%M:%S')}] elapsed={elapsed:.0f}s, processed={total_processed:,}, tested={total_tested:,}, primes={total_primes:,}, rate={rate:.0f} k/s, max_k={max_k:,}")
            
            # Save checkpoint
            if time.time() - last_checkpoint_time > CHECKPOINT_EVERY_SEC:
                with open(CHECKPOINT_FILE, 'w') as f:
                    json.dump({
                        'last_k_processed': max_k,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'total_tested': total_tested,
                        'total_skipped': total_skipped,
                        'elapsed_seconds': elapsed,
                    }, f, indent=2)
                last_checkpoint_time = time.time()
    
    except KeyboardInterrupt:
        print("\nInterrupted. Stopping...")
        stop_event.set()
        for p in workers:
            p.join(timeout=10)
        max_k = max((progress_dict.get(i, (0,))[0] for i in range(NUM_WORKERS)), default=0)
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({'last_k_processed': max_k, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'interrupted': True}, f, indent=2)
        print(f"Checkpoint saved: k = {max_k:,}")
        return
    
    for p in workers:
        p.join()
    
    print()
    print("=" * 70)
    print("Done")
    print("=" * 70)
    
    total_tested = sum(progress_dict.get(i, (0, 0, 0, 0))[1] for i in range(NUM_WORKERS))
    total_skipped = sum(progress_dict.get(i, (0, 0, 0, 0))[2] for i in range(NUM_WORKERS))
    total_primes = sum(progress_dict.get(i, (0, 0, 0, 0))[3] for i in range(NUM_WORKERS))
    elapsed = time.time() - t_start
    
    print(f"Elapsed: {elapsed:.0f}s ({elapsed/3600:.2f} hours)")
    print(f"Tested: {total_tested:,}")
    print(f"Skipped (wheel+extra): {total_skipped:,}")
    print(f"Total processed: {total_tested + total_skipped:,}")
    print(f"Primes found: {total_primes:,}")
    print(f"Rate: {(total_tested + total_skipped) / elapsed:.0f} k/s")
    print()
    
    if total_primes > 0 and not stop_event.is_set():
        print("No factor found in this range.")
        max_k = max((progress_dict.get(i, (0,))[0] for i in range(NUM_WORKERS)), default=0)
        print(f"Last k: {max_k:,}")
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({'last_k_processed': max_k, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'final': True, 'no_factor_found': True}, f, indent=2)
    elif stop_event.is_set():
        print("!!! FACTOR FOUND !!!")
        if RESULTS_FILE.exists():
            with open(RESULTS_FILE) as f:
                print(f.read())

if __name__ == '__main__':
    main()
