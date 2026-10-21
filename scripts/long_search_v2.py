#!/usr/bin/env python3
"""
Long search for smallest factor of M(1277), M(1619), M(1753).
Reports progress every chunk and saves checkpoint.
"""
import time
import sys
import json
import os
import gmpy2
from gmpy2 import is_prime as gmpy_is_prime
import numpy as np
from sympy import primerange

LOG = '/home/z/my-project/scripts/long_search.log'
OUTPUT = '/home/z/my-project/download/A136030_1_to_8000.txt'
CHECKPOINT = '/home/z/my-project/scripts/search_checkpoint.json'

MERSENNE_PRIME_EXPONENTS = {2,3,5,7,13,17,19,31,61,89,107,127,521,607,1279,2203,2281,3217,4253,4423}

# (idx, p) for the 3 small missing values
TARGETS = [(192, 1277), (241, 1619), (258, 1753)]

# Total time budget
TOTAL_BUDGET = 1700  # ~28 min

def log(msg):
    ts = time.strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    with open(LOG, 'a') as f:
        f.write(line + "\n")
    print(line, file=sys.stderr)
    sys.stderr.flush()

def search_factor(p, k_start, k_end, t_start, time_budget):
    """Search k in [k_start, k_end) for smallest factor of M(p)."""
    # Build sieve primes (up to 5000 for better filtering)
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
    chunk_count = 0
    
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
        chunk_count += 1
        elapsed = time.time() - t_start
        max_q = 2 * last_k * p + 1
        log(f"    M({p}): chunk {chunk_count} done, k={last_k:,}, max_q={max_q:.2e}, elapsed={elapsed:.0f}s")
        
        if elapsed > time_budget:
            return None, last_k
    
    return None, last_k

def main():
    # Clear log
    open(LOG, 'w').close()
    log("=" * 60)
    log("Long search for missing Mersenne factors")
    log(f"Targets: M(1277), M(1619), M(1753)")
    log(f"Total time budget: {TOTAL_BUDGET}s ({TOTAL_BUDGET/60:.1f} min)")
    log("=" * 60)
    
    # Load current sequence
    seq = {}
    with open(OUTPUT) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                seq[int(parts[0])] = int(parts[1])
    
    # Load checkpoint
    cp = {}
    try:
        with open(CHECKPOINT) as f:
            cp = json.load(f)
    except:
        pass
    
    t_start = time.time()
    
    for idx, p in TARGETS:
        elapsed = time.time() - t_start
        if elapsed > TOTAL_BUDGET:
            log(f"Total budget exceeded, stopping")
            break
        
        # Per-prime budget
        remaining = TOTAL_BUDGET - elapsed
        per_prime = remaining / (len(TARGETS) - TARGETS.index((idx, p)))
        
        # Check checkpoint - skip already-found
        cp_key = str(idx)
        if cp_key in cp and cp[cp_key] not in (None, "-1", -1):
            log(f"M({p}) [idx={idx}]: already found = {cp[cp_key]}")
            seq[idx] = int(cp[cp_key])
            continue
        
        # Start search from checkpoint if exists
        k_start = cp.get(f"{idx}_k", 1)
        K_LIMIT = 10**10
        
        log(f"M({p}) [idx={idx}]: searching k=[{k_start:,}, {K_LIMIT:,}], budget={per_prime:.0f}s")
        log(f"  Max q to test: ~{2*K_LIMIT*p+1:.2e}")
        
        factor, last_k = search_factor(p, k_start, K_LIMIT, t_start, elapsed + per_prime)
        
        if factor:
            log(f"  *** FOUND! M({p}) = factor {factor}")
            log(f"      (k = {last_k}, q = {factor})")
            seq[idx] = factor
            cp[cp_key] = factor
            # Save immediately
            with open(OUTPUT, 'w') as f:
                for i in range(1, 8001):
                    f.write(f"{i}\t{seq[i]}\n")
            with open(CHECKPOINT, 'w') as f:
                json.dump(cp, f)
        else:
            log(f"  NOT FOUND (last k={last_k:,}, max q={2*last_k*p+1:.2e})")
            cp[f"{idx}_k"] = last_k
            with open(CHECKPOINT, 'w') as f:
                json.dump(cp, f)
    
    # Final save
    with open(OUTPUT, 'w') as f:
        for i in range(1, 8001):
            f.write(f"{i}\t{seq[i]}\n")
    
    log("=" * 60)
    log(f"Done. Total time: {time.time()-t_start:.0f}s")
    log(f"idx 192: {seq[192]}")
    log(f"idx 241: {seq[241]}")
    log(f"idx 258: {seq[258]}")
    log("=" * 60)

if __name__ == "__main__":
    main()
