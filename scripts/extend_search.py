#!/usr/bin/env python3
"""
Extended search for missing factors using gmpy2 + numpy sieve.
Targeted search for missing prime exponents.
"""

import sys
import time
import json
import gmpy2
from gmpy2 import is_prime as gmpy_is_prime
import numpy as np
from sympy import primerange

MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607,
    1279, 2203, 2281, 3217, 4253, 4423
}

# Small primes for sieve
def sieve_primes_list(limit):
    is_prime = bytearray([1]) * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]

small_primes_for_sieve = sieve_primes_list(1000)

# Load current sequence
sequence = []
with open('/home/z/my-project/download/A136030_1_to_8000.txt') as f:
    for line in f:
        if line.startswith('#'):
            continue
        parts = line.strip().split('\t')
        if len(parts) == 2:
            idx = int(parts[0])
            val = int(parts[1])
            sequence.append((idx, val))

# Get primes (need to recompute the same prime list)
all_primes = list(primerange(2, 100000))
candidate_primes = [p for p in all_primes if p not in MERSENNE_PRIME_EXPONENTS]
target_primes = candidate_primes[:8000]

# Find missing entries
missing = []
for idx, p in enumerate(target_primes, 1):
    if sequence[idx-1][1] == -1:
        missing.append((idx, p))

print(f"Missing entries: {len(missing)}", file=sys.stderr)
print(f"First 10: {missing[:10]}", file=sys.stderr)

# Targeted search using numpy sieve
K_LIMIT = 5 * 10**6  # search k up to 5M, so q up to 10M*p
print(f"Searching with k_limit={K_LIMIT} for missing primes...", file=sys.stderr)

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
    
    # Iterate over valid, unmarked k in increasing order
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

t_start = time.time()
time_budget = 480  # 8 minutes
found_count = 0

results = dict(sequence)  # idx -> value

for idx, p in missing:
    elapsed = time.time() - t_start
    if elapsed > time_budget:
        print(f"Time budget exceeded at idx={idx}", file=sys.stderr)
        break
    
    found = targeted_search(p, K_LIMIT)
    if found:
        results[idx] = found
        found_count += 1
        print(f"  [{idx}] M({p}): {found}", file=sys.stderr)
    
    if (idx % 50 == 0 or idx == missing[-1][0]):
        elapsed = time.time() - t_start
        print(f"  Progress: idx={idx}, found={found_count}, elapsed={elapsed:.1f}s", file=sys.stderr)

print(f"\nFound {found_count} additional factors", file=sys.stderr)
print(f"Total time: {time.time()-t_start:.1f}s", file=sys.stderr)

# Save incrementally
output_path = '/home/z/my-project/download/A136030_1_to_8000.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("# A136030: Smallest prime factor of Mersenne number M(p) = 2^p - 1\n")
    f.write("# For prime p, excluding Mersenne prime exponents (where M(p) is itself prime)\n")
    f.write("# Indexed sequentially by prime p (skipping Mersenne prime exponents)\n")
    f.write("# Format: index<TAB>smallest_prime_factor\n")
    f.write("# Value -1 means no factor is known\n")
    for idx in range(1, 8001):
        f.write(f"{idx}\t{results[idx]}\n")

# Stats
found = sum(1 for idx in range(1, 8001) if results[idx] != -1)
missing_count = sum(1 for idx in range(1, 8001) if results[idx] == -1)
print(f"\nFinal stats:", file=sys.stderr)
print(f"  Found: {found} ({found/8000*100:.1f}%)", file=sys.stderr)
print(f"  Missing: {missing_count}", file=sys.stderr)
print(f"Written to {output_path}", file=sys.stderr)
