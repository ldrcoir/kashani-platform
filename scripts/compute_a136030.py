#!/usr/bin/env python3
"""
Compute A136030: Smallest prime factor of Mersenne number M(p) = 2^p - 1
for prime p, excluding Mersenne prime exponents (where M(p) is itself prime).
Indexed sequentially from 1 to 8000.

Mathematical basis:
  For prime p, any prime factor q of M(p) satisfies:
    q = 2*k*p + 1  for some integer k >= 1
    q ≡ ±1 (mod 8)
    2^p ≡ 1 (mod q)
  The smallest such q is the smallest prime factor of M(p).

Algorithm:
  1. Generate primes p in order (skip Mersenne prime exponents).
  2. For each prime p, search k = 1, 2, 3, ... and test q = 2*k*p + 1.
  3. Use a numpy sieve to skip composite q values quickly.
  4. Use gmpy2 for fast primality testing of remaining candidates.
  5. Verify 2^p ≡ 1 (mod q) using fast modular exponentiation.
"""

import sys
import time
import json
import numpy as np
import gmpy2
from gmpy2 import is_prime as gmpy_is_prime
from sympy import primerange

# Known Mersenne prime exponents (M(p) is itself prime for these p)
MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607,
    1279, 2203, 2281, 3217, 4253, 4423
}

OUTPUT_PATH = "/home/z/my-project/download/A136030_1_to_8000.txt"
CHECKPOINT_PATH = "/home/z/my-project/scripts/a136030_checkpoint.json"

# Sieve small primes (for filtering q candidates)
def sieve_small_primes(limit):
    is_prime_arr = np.ones(limit + 1, dtype=bool)
    is_prime_arr[0] = is_prime_arr[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime_arr[i]:
            is_prime_arr[i*i::i] = False
    return [int(i) for i in np.flatnonzero(is_prime_arr)]

# Maximum k value to search (q = 2*k*p + 1)
# Larger k means slower per-prime but finds larger smallest-factors
K_LIMIT = 5 * 10**6

# Time budget (seconds) - leave margin for saving
TIME_BUDGET = 480

def find_smallest_factor(p, k_limit, small_primes, t_start, time_budget):
    """Find smallest prime factor of M(p) = 2^p - 1.
    
    Searches q = 2*k*p + 1 for k = 1, 2, ..., k_limit.
    Uses numpy sieve to skip composite q values.
    Returns q if found, None otherwise.
    """
    p_mod4 = p & 3
    # For q ≡ ±1 (mod 8): if p ≡ 1 (mod 4), then k ≡ 0 or 3 (mod 4)
    #                   if p ≡ 3 (mod 4), then k ≡ 0 or 1 (mod 4)
    if p_mod4 == 1:
        valid_residues = (0, 3)
    else:
        valid_residues = (0, 1)
    
    # Build sieve: mark k as "skip" if 2*k*p+1 has a small prime factor
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
    
    # Iterate over valid, unmarked k in increasing order
    for k in range(1, k_limit + 1):
        if (k & 3) not in valid_residues:
            continue
        if is_composite[k]:
            continue
        q = 2 * k * p + 1
        # Primality test (gmpy2 is fast)
        if not gmpy_is_prime(q):
            continue
        # Verify q divides M(p)
        if pow(2, p, q) == 1:
            return q
        # Periodic time check
        if (k & 0xFFFF) == 0:
            if time.time() - t_start > time_budget:
                return None
    return None

def main():
    t_start = time.time()
    print(f"Computing A136030 sequence (1 to 8000)...", file=sys.stderr)
    print(f"  K_LIMIT = {K_LIMIT}", file=sys.stderr)
    print(f"  TIME_BUDGET = {TIME_BUDGET}s", file=sys.stderr)
    
    # Build small primes for sieve (primes up to 1000)
    print("Sieving small primes...", file=sys.stderr)
    small_primes = sieve_small_primes(1000)
    print(f"  {len(small_primes)} small primes", file=sys.stderr)
    
    # Load checkpoint if exists
    results = {}
    try:
        with open(CHECKPOINT_PATH) as f:
            results = {int(k): int(v) for k, v in json.load(f).items()}
        print(f"Loaded checkpoint with {len(results)} entries", file=sys.stderr)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    # Generate primes up to 100000 (enough for 8000 entries after excluding MP exponents)
    print("Generating primes...", file=sys.stderr)
    all_primes = list(primerange(2, 100000))
    candidate_primes = [p for p in all_primes if p not in MERSENNE_PRIME_EXPONENTS]
    target_primes = candidate_primes[:8000]
    print(f"  {len(target_primes)} target primes (from {target_primes[0]} to {target_primes[-1]})", file=sys.stderr)
    
    # Compute smallest factor for each prime
    found_count = 0
    missing_count = 0
    
    for idx, p in enumerate(target_primes, 1):
        # Check time budget
        elapsed = time.time() - t_start
        if elapsed > TIME_BUDGET:
            print(f"Time budget exceeded at idx={idx}", file=sys.stderr)
            # Fill remaining with -1
            for j in range(idx, 8001):
                if j not in results:
                    results[j] = -1
            break
        
        # Skip if already in checkpoint
        if idx in results:
            if results[idx] != -1:
                found_count += 1
            else:
                missing_count += 1
            if idx % 100 == 0:
                print(f"  [{idx}/{8000}] M({p}): cached = {results[idx]} (elapsed {elapsed:.1f}s)", file=sys.stderr)
            continue
        
        # Compute smallest factor
        factor = find_smallest_factor(p, K_LIMIT, small_primes, t_start, TIME_BUDGET)
        if factor is not None:
            results[idx] = factor
            found_count += 1
            if idx <= 200 or idx % 50 == 0:
                print(f"  [{idx}/{8000}] M({p}): {factor} (elapsed {elapsed:.1f}s)", file=sys.stderr)
        else:
            results[idx] = -1
            missing_count += 1
            if idx <= 200 or idx % 50 == 0:
                print(f"  [{idx}/{8000}] M({p}): NOT FOUND (elapsed {elapsed:.1f}s)", file=sys.stderr)
        
        # Checkpoint every 25 entries
        if idx % 25 == 0:
            with open(CHECKPOINT_PATH, 'w') as f:
                json.dump(results, f)
    
    # Final save
    print(f"\nWriting output to {OUTPUT_PATH}...", file=sys.stderr)
    with open(OUTPUT_PATH, 'w') as f:
        for idx in range(1, 8001):
            f.write(f"{idx}\t{results.get(idx, -1)}\n")
    
    # Final checkpoint
    with open(CHECKPOINT_PATH, 'w') as f:
        json.dump(results, f)
    
    # Summary
    found = sum(1 for v in results.values() if v != -1)
    missing = sum(1 for v in results.values() if v == -1)
    print(f"\n=== Summary ===", file=sys.stderr)
    print(f"Total: {len(results)}", file=sys.stderr)
    print(f"Found: {found} ({found/8000*100:.1f}%)", file=sys.stderr)
    print(f"Missing: {missing}", file=sys.stderr)
    print(f"Total time: {time.time()-t_start:.1f}s", file=sys.stderr)

if __name__ == "__main__":
    main()
