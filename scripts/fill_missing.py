#!/usr/bin/env python3
"""
Fill in -1 entries in A136030_1_to_8000.txt by direct computation.
Reads existing file, only computes missing entries, preserves all known values.
Runs in background with periodic checkpoint saves.
"""

import sys
import time
import json
import numpy as np
import gmpy2
from gmpy2 import is_prime as gmpy_is_prime
from sympy import primerange

MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607,
    1279, 2203, 2281, 3217, 4253, 4423
}

INPUT_OUTPUT_PATH = "/home/z/my-project/download/A136030_1_to_8000.txt"
CHECKPOINT_PATH = "/home/z/my-project/scripts/a136030_checkpoint2.json"
LOG_PATH = "/home/z/my-project/scripts/a136030_compute.log"

K_LIMIT = 10**7  # search k up to 10M
TIME_BUDGET = 7200  # 2 hours total

def sieve_small_primes(limit):
    is_prime_arr = np.ones(limit + 1, dtype=bool)
    is_prime_arr[0] = is_prime_arr[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime_arr[i]:
            is_prime_arr[i*i::i] = False
    return [int(i) for i in np.flatnonzero(is_prime_arr)]

def find_smallest_factor(p, k_limit, small_primes, t_start, time_budget):
    p_mod4 = p & 3
    if p_mod4 == 1:
        valid_residues = (0, 3)
    else:
        valid_residues = (0, 1)
    
    is_composite = np.zeros(k_limit + 1, dtype=bool)
    two_p = 2 * p
    for r in small_primes:
        if r == 2:
            continue
        two_p_mod_r = two_p % r
        if two_p_mod_r == 0:
            continue
        try:
            inv = pow(int(two_p_mod_r), -1, r)
        except ValueError:
            continue
        k_0 = (-inv) % r
        if k_0 == 0:
            k_0 = r
        is_composite[k_0::r] = True
    
    last_check = 0
    for k in range(1, k_limit + 1):
        if (k & 3) not in valid_residues:
            continue
        if is_composite[k]:
            continue
        q = 2 * k * p + 1
        if not gmpy_is_prime(q):
            continue
        if pow(2, p, q) == 1:
            return q
        if k - last_check > 100000:
            if time.time() - t_start > time_budget:
                return None
            last_check = k
    return None

def log(msg):
    with open(LOG_PATH, 'a') as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    print(msg, file=sys.stderr)

def main():
    t_start = time.time()
    log("Starting A136030 missing value computation...")
    
    # Load current file
    seq = {}
    with open(INPUT_OUTPUT_PATH) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                seq[int(parts[0])] = int(parts[1])
    
    # Get primes (same as original)
    all_primes = list(primerange(2, 100000))
    candidate_primes = [p for p in all_primes if p not in MERSENNE_PRIME_EXPONENTS]
    target_primes = candidate_primes[:8000]
    
    # Find missing entries
    missing = [(idx, target_primes[idx-1]) for idx in range(1, 8001) if seq[idx] == -1]
    log(f"Missing entries to compute: {len(missing)}")
    
    # Load checkpoint (already-computed values from previous runs)
    cp = {}
    try:
        with open(CHECKPOINT_PATH) as f:
            cp = {int(k): int(v) for k, v in json.load(f).items()}
        log(f"Loaded checkpoint with {len(cp)} entries")
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    # Apply checkpoint first
    for idx, val in cp.items():
        if val != -1 and seq.get(idx) == -1:
            seq[idx] = val
    
    # Recompute missing list
    missing = [(idx, target_primes[idx-1]) for idx in range(1, 8001) if seq[idx] == -1]
    log(f"Still missing after checkpoint: {len(missing)}")
    
    # Small primes for sieve
    small_primes = sieve_small_primes(1000)
    
    # Process missing entries
    found_count = 0
    for i, (idx, p) in enumerate(missing):
        elapsed = time.time() - t_start
        if elapsed > TIME_BUDGET:
            log(f"Time budget exceeded at idx={idx}")
            break
        
        factor = find_smallest_factor(p, K_LIMIT, small_primes, t_start, TIME_BUDGET)
        if factor is not None:
            seq[idx] = factor
            cp[idx] = factor
            found_count += 1
            log(f"[{i+1}/{len(missing)}] idx={idx} M({p}): FOUND {factor} (elapsed {elapsed:.1f}s)")
        else:
            cp[idx] = -1
            log(f"[{i+1}/{len(missing)}] idx={idx} M({p}): not found (elapsed {elapsed:.1f}s)")
        
        # Checkpoint every 10 entries
        if (i + 1) % 10 == 0:
            with open(CHECKPOINT_PATH, 'w') as f:
                json.dump(cp, f)
            # Also update main file
            with open(INPUT_OUTPUT_PATH, 'w') as f:
                for j in range(1, 8001):
                    f.write(f"{j}\t{seq[j]}\n")
            log(f"  Checkpoint saved. Found so far: {found_count}")
    
    # Final save
    with open(INPUT_OUTPUT_PATH, 'w') as f:
        for j in range(1, 8001):
            f.write(f"{j}\t{seq[j]}\n")
    with open(CHECKPOINT_PATH, 'w') as f:
        json.dump(cp, f)
    
    found = sum(1 for v in seq.values() if v != -1)
    missing_count = sum(1 for v in seq.values() if v == -1)
    log(f"\n=== DONE ===")
    log(f"Found: {found} ({found/8000*100:.1f}%)")
    log(f"Missing: {missing_count}")
    log(f"Total time: {time.time()-t_start:.1f}s")

if __name__ == "__main__":
    main()
