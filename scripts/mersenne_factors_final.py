#!/usr/bin/env python3
"""
Final pass: targeted search for remaining not-found primes.
Saves results incrementally so partial progress is preserved.
"""

import sys
import time
import numpy as np
import gmpy2
from gmpy2 import is_prime as gmpy_is_prime

MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607,
    1279, 2203, 2281, 3217, 4253, 4423
}

def sieve_primes_list(limit):
    is_prime = bytearray([1]) * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]

small_primes_for_sieve = sieve_primes_list(500)

# Load current results
results = {}
with open('/home/z/my-project/download/A136030_factors_1_to_8000.txt') as f:
    for line in f:
        if line.startswith('#'):
            continue
        parts = line.strip().split('\t')
        if len(parts) == 2:
            n, val = int(parts[0]), int(parts[1])
            results[n] = val

# Find not-found primes
not_found_primes = sorted([n for n, v in results.items() if v == -1])
print(f"Not-found primes: {len(not_found_primes)}", file=sys.stderr)

K_LIMIT = 10**7  # search k up to 10M

def targeted_search(p, k_limit):
    p_mod4 = p & 3
    if p_mod4 == 1:
        valid_residues = {0, 3}
    else:
        valid_residues = {0, 1}
    
    # Numpy sieve
    is_composite = np.zeros(k_limit + 1, dtype=bool)
    for r in small_primes_for_sieve:
        if r == 2:
            continue
        two_p_mod_r = (2 * p) % r
        if two_p_mod_r == 0:
            continue
        try:
            inv = pow(two_p_mod_r, -1, r)
        except ValueError:
            continue
        k_0 = (-inv) % r
        if k_0 == 0:
            k_0 = r
        is_composite[k_0::r] = True
    
    # Iterate over valid, unmarked k
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
    return None

# Process not-found primes with incremental save
t0 = time.time()
found_count = 0
output_path = '/home/z/my-project/download/A136030_factors_1_to_8000.txt'

for idx, p in enumerate(not_found_primes):
    # Check time budget
    elapsed = time.time() - t0
    if elapsed > 480:  # 8 minute budget
        print(f"Time budget exceeded. Stopping at {idx}/{len(not_found_primes)}.", file=sys.stderr)
        break
    
    found = targeted_search(p, K_LIMIT)
    if found:
        results[p] = found
        found_count += 1
    
    if (idx + 1) % 10 == 0:
        elapsed = time.time() - t0
        print(f"  {idx+1}/{len(not_found_primes)} in {elapsed:.1f}s. Found: {found_count}", file=sys.stderr)
        # Save incrementally
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Series A136030: Smallest prime factor of Mersenne number M(n) = 2^n - 1\n")
            f.write("# n from 1 to 8000\n")
            f.write("# Value: 1 if n=1; 0 if M(n) is a Mersenne prime; else smallest prime factor; -1 if not found\n")
            f.write("# Format: n<TAB>value\n")
            for n in range(1, 8001):
                f.write(f"{n}\t{results[n]}\n")

# Final save
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("# Series A136030: Smallest prime factor of Mersenne number M(n) = 2^n - 1\n")
    f.write("# n from 1 to 8000\n")
    f.write("# Value: 1 if n=1; 0 if M(n) is a Mersenne prime; else smallest prime factor; -1 if not found\n")
    f.write("# Format: n<TAB>value\n")
    for n in range(1, 8001):
        f.write(f"{n}\t{results[n]}\n")

elapsed = time.time() - t0
nf_remaining = sum(1 for v in results.values() if v == -1)
print(f"\nDone in {elapsed:.1f}s.", file=sys.stderr)
print(f"Found: {found_count}", file=sys.stderr)
print(f"Still -1: {nf_remaining}", file=sys.stderr)
print(f"Output: {output_path}", file=sys.stderr)
