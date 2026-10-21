#!/usr/bin/env python3
"""
Final optimized version: 
- Use multiplicative order computation for primes q <= 10^7 (fast).
- Use numpy-sliced sieve + gmpy2 for targeted search (k_limit = 10^7).
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

def sieve_primes_set(limit):
    is_prime = bytearray([1]) * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return set(i for i in range(2, limit + 1) if is_prime[i])

def sieve_primes_list(limit):
    is_prime = bytearray([1]) * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]

# Step 1: Sieve primes up to LIMIT
LIMIT = 10**7
t0 = time.time()
print(f"Sieving primes up to {LIMIT}...", file=sys.stderr)
prime_set = sieve_primes_set(LIMIT)
all_primes = sorted(prime_set)
small_primes_for_trial = sieve_primes_list(4000)
small_primes_for_sieve = sieve_primes_list(500)  # smaller for faster numpy sieve
print(f"  {len(all_primes)} primes found in {time.time()-t0:.1f}s.", file=sys.stderr)

# Step 2: Compute multiplicative orders for all primes q <= 10^7
t0 = time.time()
print("Computing multiplicative orders...", file=sys.stderr)
smallest_prime_with_order = {}
count = 0
for q in all_primes:
    if q == 2:
        continue
    q_minus_1 = q - 1
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
    if count % 200000 == 0:
        print(f"  Processed {count}/{len(all_primes)} in {time.time()-t0:.1f}s", file=sys.stderr)
print(f"  Done in {time.time()-t0:.1f}s.", file=sys.stderr)

# Step 3: Look up smallest factor for each prime p <= 8000
primes_up_to_8000 = sieve_primes_list(8000)
prime_factors = {}
not_found = []
for p in primes_up_to_8000:
    if p in MERSENNE_PRIME_EXPONENTS:
        prime_factors[p] = "PRIME"
    elif p in smallest_prime_with_order:
        prime_factors[p] = smallest_prime_with_order[p]
    else:
        prime_factors[p] = None
        not_found.append(p)
print(f"After order computation: not found = {len(not_found)}", file=sys.stderr)

# Step 4: Targeted search with numpy sieve + gmpy2
K_LIMIT = 10**7
print(f"Pass 2: Targeted search with k_limit={K_LIMIT} for {len(not_found)} primes...", file=sys.stderr)
t0 = time.time()
still_not_found = []

def targeted_search_v2(p, k_limit):
    """Numpy-sieved targeted search with gmpy2 primality testing."""
    p_mod4 = p & 3
    if p_mod4 == 1:
        valid_residues = {0, 3}
    else:
        valid_residues = {0, 1}
    
    # Numpy sieve: mark k values where 2*k*p+1 has a small prime factor
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
        # Fast numpy slice assignment
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

for idx, p in enumerate(not_found):
    found = targeted_search_v2(p, K_LIMIT)
    if found:
        prime_factors[p] = found
    else:
        still_not_found.append(p)
    if (idx + 1) % 20 == 0:
        elapsed = time.time()-t0
        rate = (idx + 1) / elapsed
        remaining = (len(not_found) - idx - 1) / rate
        found_count = len(not_found) - len(still_not_found)
        print(f"  {idx+1}/{len(not_found)} in {elapsed:.1f}s. Found: {found_count}, missing: {len(still_not_found)}. ETA: {remaining:.1f}s", file=sys.stderr)

print(f"  Pass 2 done in {time.time()-t0:.1f}s.", file=sys.stderr)
print(f"  Still not found: {len(still_not_found)} primes", file=sys.stderr)

# Step 5: Compute smallest factor of M(n) for all n=1..8000
print("Computing smallest factors for all n=1..8000...", file=sys.stderr)
results = []
for n in range(1, 8001):
    if n == 1:
        results.append((n, 1))
        continue
    if n in MERSENNE_PRIME_EXPONENTS:
        results.append((n, 0))
        continue
    
    prime_divs = []
    temp = n
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            prime_divs.append(d)
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        prime_divs.append(temp)
    
    candidates = []
    for p in prime_divs:
        v = prime_factors.get(p)
        if v == "PRIME":
            candidates.append((1 << p) - 1)
        elif v is None:
            pass
        else:
            candidates.append(v)
    
    if candidates:
        results.append((n, min(candidates)))
    else:
        results.append((n, -1))

# Step 6: Write to file
output_path = "/home/z/my-project/download/A136030_factors_1_to_8000.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("# Series A136030: Smallest prime factor of Mersenne number M(n) = 2^n - 1\n")
    f.write("# n from 1 to 8000\n")
    f.write("# Value: 1 if n=1; 0 if M(n) is a Mersenne prime; else smallest prime factor; -1 if not found\n")
    f.write("# Format: n<TAB>value\n")
    for n, val in results:
        f.write(f"{n}\t{val}\n")

print(f"\nWritten to {output_path}", file=sys.stderr)
print(f"\nFirst 30 rows:", file=sys.stderr)
for n, val in results[:30]:
    print(f"  {n}: {val}", file=sys.stderr)
print(f"\nLast 5 rows:", file=sys.stderr)
for n, val in results[-5:]:
    print(f"  {n}: {val}", file=sys.stderr)

nf_rows = [n for n, v in results if v == -1]
print(f"\nTotal rows with -1: {len(nf_rows)}", file=sys.stderr)
if nf_rows:
    print(f"  -1 rows (first 50): {nf_rows[:50]}", file=sys.stderr)
