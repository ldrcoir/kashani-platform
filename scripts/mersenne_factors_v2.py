#!/usr/bin/env python3
"""
Extended search for smallest prime factor of M(p) for primes p where
the initial sieve (up to 10^7) did not find a factor.

Uses a segmented sieve over k values (q = 2*k*p + 1) with Miller-Rabin
primality testing for candidates that pass the sieve.
"""

import sys
import time

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

def miller_rabin(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    if n < 10000:
        # trial division
        i = 3
        while i * i <= n:
            if n % i == 0:
                return False
            i += 2
        return True
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    # Deterministic witnesses for n < 3.3e24
    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for a in witnesses:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

# Step 1: Sieve primes up to LIMIT
LIMIT = 10**7
t0 = time.time()
print(f"Sieving primes up to {LIMIT}...", file=sys.stderr)
prime_set = sieve_primes_set(LIMIT)
small_primes_for_sieve = sieve_primes_list(1000)  # for segmented sieve
print(f"  {len(prime_set)} primes found in {time.time()-t0:.1f}s.", file=sys.stderr)

primes_up_to_8000 = sieve_primes_list(8000)

# Step 2: For each prime p <= 8000, find smallest factor of M(p)
# First pass: use prime_set (fast lookup for q <= 10^7)
t0 = time.time()
print("Pass 1: Finding factors using sieve set (q <= 10^7)...", file=sys.stderr)
prime_factors = {}
not_found = []
for p in primes_up_to_8000:
    if p in MERSENNE_PRIME_EXPONENTS:
        prime_factors[p] = "PRIME"
        continue
    found = None
    k = 1
    two_p = 2 * p
    while True:
        q = two_p * k + 1
        if q > LIMIT:
            break
        if q in prime_set:
            r = q & 7
            if r == 1 or r == 7:
                if pow(2, p, q) == 1:
                    found = q
                    break
        k += 1
    if found:
        prime_factors[p] = found
    else:
        prime_factors[p] = None
        not_found.append(p)
print(f"  Pass 1 done in {time.time()-t0:.1f}s. Not found: {len(not_found)}", file=sys.stderr)

# Step 3: Second pass - targeted search with segmented sieve for not-found primes
K_LIMIT = 2 * 10**6  # search k up to 2M, so q up to 4M*p
print(f"Pass 2: Targeted search with k_limit={K_LIMIT} for {len(not_found)} primes...", file=sys.stderr)
t0 = time.time()
still_not_found = []

def targeted_search(p, k_limit):
    """Find smallest prime factor of M(p) using segmented sieve over k."""
    p_mod4 = p & 3
    # Valid k residues mod 4 for q ≡ ±1 (mod 8)
    if p_mod4 == 1:
        # k ≡ 0 or 3 (mod 4)
        valid_residues = {0, 3}
    else:
        # k ≡ 0 or 1 (mod 4)
        valid_residues = {0, 1}
    
    # Sieve: mark k as composite if 2*k*p+1 has a small prime factor
    is_composite = bytearray(k_limit + 1)
    for r in small_primes_for_sieve:
        if r == 2:
            continue
        # Find k_0 such that 2*k_0*p + 1 ≡ 0 (mod r)
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
        for k in range(k_0, k_limit + 1, r):
            is_composite[k] = 1
    
    # Iterate over valid k in increasing order
    for k in range(1, k_limit + 1):
        if (k & 3) not in valid_residues:
            continue
        if is_composite[k]:
            continue
        q = 2 * k * p + 1
        # Primality check
        if q <= LIMIT:
            if q not in prime_set:
                continue
        else:
            if not miller_rabin(q):
                continue
        # Check if q divides M(p)
        if pow(2, p, q) == 1:
            return q
    return None

for idx, p in enumerate(not_found):
    found = targeted_search(p, K_LIMIT)
    if found:
        prime_factors[p] = found
    else:
        still_not_found.append(p)
    if (idx + 1) % 50 == 0:
        print(f"  Processed {idx+1}/{len(not_found)} in {time.time()-t0:.1f}s. Still not found: {len(still_not_found)}", file=sys.stderr)

print(f"  Pass 2 done in {time.time()-t0:.1f}s.", file=sys.stderr)
print(f"  Still not found: {len(still_not_found)} primes", file=sys.stderr)
print(f"  Examples: {still_not_found[:20]}", file=sys.stderr)

# Step 4: For each n from 1 to 8000, compute smallest prime factor of M(n)
print("Computing smallest factors for all n=1..8000...", file=sys.stderr)
results = []
for n in range(1, 8001):
    if n == 1:
        results.append((n, 1))
        continue

    if n in MERSENNE_PRIME_EXPONENTS:
        results.append((n, 0))
        continue

    # Find prime factors of n
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

    # Collect candidates
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

# Step 5: Write to file
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
print(f"\nRows with -1 (factor not found): {len(nf_rows)}", file=sys.stderr)
if nf_rows:
    print(f"  First 30: {nf_rows[:30]}", file=sys.stderr)
