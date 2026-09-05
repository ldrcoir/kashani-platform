#!/usr/bin/env python3
"""Long search for smallest factor of M(p) for p in missing_primes.
Uses chunked sieve up to K=10^10 (q up to ~2.5*10^13).
"""
import time
import sys
import json
import gmpy2
from gmpy2 import is_prime as gmpy_is_prime
import numpy as np

LOG = '/home/z/my-project/scripts/long_search.log'
OUTPUT = '/home/z/my-project/download/A136030_1_to_8000.txt'

# Missing small primes to search
TARGETS = [1277, 1619, 1753]

def log(msg):
    with open(LOG, 'a') as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    print(msg, file=sys.stderr)

def search_factor(p, k_start, k_end, time_budget):
    """Search k in [k_start, k_end) for smallest factor of M(p)."""
    t0 = time.time()
    
    # Sieve small primes (up to 5000)
    sa = np.ones(5001, dtype=bool)
    sa[0] = sa[1] = False
    for i in range(2, 71):
        if sa[i]:
            sa[i*i::i] = False
    small_primes = [int(i) for i in np.flatnonzero(sa)]
    
    p_mod4 = p & 3
    valid_residues = (0, 3) if p_mod4 == 1 else (0, 1)
    two_p = 2 * p
    
    chunk_size = 10**8
    last_k = k_start - 1
    
    for chunk_start in range(k_start, k_end + 1, chunk_size):
        chunk_end = min(chunk_start + chunk_size, k_end + 1)
        size = chunk_end - chunk_start
        is_composite = np.zeros(size, dtype=bool)
        
        for r in small_primes:
            if r == 2: continue
            t = two_p % r
            if t == 0: continue
            try:
                inv = pow(int(t), -1, r)
            except: continue
            k_0 = (-inv) % r
            if k_0 < chunk_start:
                offset = (chunk_start - k_0 + r - 1) // r
                k_0 = k_0 + offset * r
            if k_0 >= chunk_end: continue
            idx = k_0 - chunk_start
            is_composite[idx::r] = True
        
        for i in range(size):
            k = chunk_start + i
            if (k & 3) not in valid_residues: continue
            if is_composite[i]: continue
            q = 2 * k * p + 1
            if gmpy_is_prime(q) and pow(2, p, q) == 1:
                return q, k
        
        last_k = chunk_end - 1
        elapsed = time.time() - t0
        if elapsed > time_budget:
            return None, last_k
    
    return None, last_k

def main():
    log("Starting long search for missing factors...")
    
    # Load current file
    seq = {}
    with open(OUTPUT) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                seq[int(parts[0])] = int(parts[1])
    
    from sympy import primerange
    MERSENNE_PRIME_EXPONENTS = {2,3,5,7,13,17,19,31,61,89,107,127,521,607,1279,2203,2281,3217,4253,4423}
    all_primes = list(primerange(2, 100000))
    candidate_primes = [p for p in all_primes if p not in MERSENNE_PRIME_EXPONENTS]
    target_primes = candidate_primes[:8000]
    
    # Search each target
    K_LIMIT = 10**10  # q up to ~2.5*10^13
    TIME_BUDGET_PER_PRIME = 1500  # 25 min per prime
    
    for p in TARGETS:
        # Find the index
        try:
            idx = target_primes.index(p) + 1
        except ValueError:
            log(f"  p={p} not in target primes, skipping")
            continue
        
        log(f"Searching M({p}) [idx={idx}], K_LIMIT={K_LIMIT}...")
        t_start = time.time()
        
        factor, last_k = search_factor(p, 1, K_LIMIT, TIME_BUDGET_PER_PRIME)
        elapsed = time.time() - t_start
        
        if factor:
            log(f"  FOUND! M({p}) smallest factor = {factor} (k={last_k}, time={elapsed:.1f}s)")
            seq[idx] = factor
            # Save immediately
            with open(OUTPUT, 'w') as f:
                for i in range(1, 8001):
                    f.write(f"{i}\t{seq[i]}\n")
        else:
            log(f"  NOT FOUND for M({p}) (last k={last_k}, time={elapsed:.1f}s)")
    
    # Final save
    with open(OUTPUT, 'w') as f:
        for i in range(1, 8001):
            f.write(f"{i}\t{seq[i]}\n")
    
    log("Done.")

if __name__ == "__main__":
    main()
