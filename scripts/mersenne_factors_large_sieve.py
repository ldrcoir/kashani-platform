#!/usr/bin/env python3
"""
Larger sieve approach: sieve primes up to 10^8, compute multiplicative orders.
This finds smallest factors up to 10^8.
"""

import sys
import time
import numpy as np

MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607,
    1279, 2203, 2281, 3217, 4253, 4423
}

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

# Find not-found primes (these have smallest factor > 10^7)
not_found_primes = sorted([n for n, v in results.items() if v == -1])
print(f"Not-found primes: {len(not_found_primes)}", file=sys.stderr)

# Sieve primes up to 10^8 using numpy for speed
LIMIT = 10**8
t0 = time.time()
print(f"Sieving primes up to {LIMIT} using numpy...", file=sys.stderr)

# Use numpy bytearray for sieve
sieve_size = LIMIT + 1
is_prime = np.ones(sieve_size, dtype=np.bool_)
is_prime[0] = is_prime[1] = False
for i in range(2, int(LIMIT**0.5) + 1):
    if is_prime[i]:
        is_prime[i*i::i] = False
# Get list of primes
prime_indices = np.flatnonzero(is_prime)
all_primes = prime_indices.tolist()
print(f"  {len(all_primes)} primes found in {time.time()-t0:.1f}s.", file=sys.stderr)

# Small primes for factoring q-1
small_primes_for_trial = [p for p in all_primes if p <= 4000]

# For each prime q, compute ord_q(2) and record smallest q for each order
t0 = time.time()
print("Computing multiplicative orders...", file=sys.stderr)
smallest_prime_with_order = {}
count = 0
for q in all_primes:
    if q == 2:
        continue
    q_minus_1 = q - 1
    # Factor q-1
    factors = set()
    n = q_minus_1
    for sp in small_primes_for_trial:
        if sp * sp > n:
            break
        if n % sp == 0:
            factors.add(sp)
            while n % sp == 0:
                n //= sp
    if n > 1:
        factors.add(n)
    # Compute ord_q(2)
    order = q_minus_1
    for p in factors:
        while order % p == 0:
            if pow(2, order // p, q) == 1:
                order //= p
            else:
                break
    if order <= 8000:
        if order not in smallest_prime_with_order or q < smallest_prime_with_order[order]:
            smallest_prime_with_order[order] = q
    count += 1
    if count % 500000 == 0:
        print(f"  Processed {count}/{len(all_primes)} in {time.time()-t0:.1f}s", file=sys.stderr)
print(f"  Done in {time.time()-t0:.1f}s.", file=sys.stderr)

# Update results for not-found primes
found_count = 0
for p in not_found_primes:
    if p in smallest_prime_with_order:
        results[p] = smallest_prime_with_order[p]
        found_count += 1

print(f"Found {found_count} more factors.", file=sys.stderr)
remaining_nf = sum(1 for v in results.values() if v == -1)
print(f"Remaining -1: {remaining_nf}", file=sys.stderr)

# Save
output_path = '/home/z/my-project/download/A136030_factors_1_to_8000.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("# Series A136030: Smallest prime factor of Mersenne number M(n) = 2^n - 1\n")
    f.write("# n from 1 to 8000\n")
    f.write("# Value: 1 if n=1; 0 if M(n) is a Mersenne prime; else smallest prime factor; -1 if not found\n")
    f.write("# Format: n<TAB>value\n")
    for n in range(1, 8001):
        f.write(f"{n}\t{results[n]}\n")

print(f"Saved to {output_path}", file=sys.stderr)
