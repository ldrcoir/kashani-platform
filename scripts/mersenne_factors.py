#!/usr/bin/env python3
"""
Compute smallest prime factor of Mersenne number M(n) = 2^n - 1
for n = 1 to 8000.

Output values:
  - 1            if n=1 (M_1 = 1, no prime factors)
  - 0            if M(n) is a Mersenne prime (n in MERSENNE_PRIME_EXPONENTS)
  - smallest prime factor of M(n)  if M(n) is composite
  - -1           if factor not found in search range

Method:
  For prime p (not Mersenne exponent), smallest prime factor q of M(p) satisfies:
    q = 2*k*p + 1, q prime, q ≡ ±1 (mod 8), 2^p ≡ 1 (mod q)
  For composite n, smallest prime factor of M(n) = min over prime p | n of
  (smallest prime factor of M(p)), because M(p) | M(n) when p | n.
"""

import sys
import time

MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607,
    1279, 2203, 2281, 3217, 4253, 4423
}

def sieve_primes_set(limit):
    """Sieve of Eratosthenes returning a set of primes up to limit."""
    is_prime = bytearray([1]) * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return set(i for i in range(2, limit + 1) if is_prime[i])

def sieve_primes_list(limit):
    """Sieve of Eratosthenes returning a list of primes up to limit."""
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
print(f"  {len(prime_set)} primes found in {time.time()-t0:.1f}s.", file=sys.stderr)

primes_up_to_8000 = sieve_primes_list(8000)
print(f"  {len(primes_up_to_8000)} primes up to 8000.", file=sys.stderr)

# Step 2: For each prime p <= 8000, find smallest factor of M(p)
t0 = time.time()
print("Finding smallest factors for prime exponents...", file=sys.stderr)
prime_factors = {}  # p -> smallest factor of M(p), or "PRIME", or None
not_found = []
for idx, p in enumerate(primes_up_to_8000):
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
    if (idx + 1) % 200 == 0:
        print(f"  Processed {idx+1}/{len(primes_up_to_8000)} primes in {time.time()-t0:.1f}s", file=sys.stderr)

print(f"  Done in {time.time()-t0:.1f}s.", file=sys.stderr)
print(f"  Primes with no factor found (smallest factor > {LIMIT}): {not_found}", file=sys.stderr)
print(f"  Total not found: {len(not_found)}", file=sys.stderr)

# Step 3: For each n from 1 to 8000, compute smallest prime factor of M(n)
print("Computing smallest factors for all n=1..8000...", file=sys.stderr)
results = []
for n in range(1, 8001):
    if n == 1:
        results.append((n, 1))  # M(1) = 1
        continue

    if n in MERSENNE_PRIME_EXPONENTS:
        results.append((n, 0))  # M(n) is prime (Mersenne prime)
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

    # Smallest prime factor of M(n) = min over prime p | n of (smallest prime factor of M(p))
    # Because M(p) | M(n) when p | n
    candidates = []
    for p in prime_divs:
        v = prime_factors.get(p)
        if v == "PRIME":
            # M(p) is a Mersenne prime and divides M(n). It's a (huge) prime factor.
            candidates.append((1 << p) - 1)
        elif v is None:
            pass  # Skip (factor not found in search range)
        else:
            candidates.append(v)

    if candidates:
        results.append((n, min(candidates)))
    else:
        results.append((n, -1))

# Step 4: Write to file
output_path = "/home/z/my-project/download/A136030_factors_1_to_8000.txt"
with open(output_path, "w", encoding="utf-8") as f:
    # Header comment
    f.write("# Series A136030: Smallest prime factor of Mersenne number M(n) = 2^n - 1\n")
    f.write("# n from 1 to 8000\n")
    f.write("# Value: 1 if n=1; 0 if M(n) is a Mersenne prime; else smallest prime factor\n")
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

# Report -1 rows
nf_rows = [n for n, v in results if v == -1]
print(f"\nRows with -1 (smallest factor > {LIMIT}, search range exceeded): {nf_rows}", file=sys.stderr)
print(f"Total -1 rows: {len(nf_rows)}", file=sys.stderr)

# Report large Mersenne prime factor rows (where smallest factor is a Mersenne prime)
large_rows = [(n, v) for n, v in results if isinstance(v, int) and v > 10**6 and v != -1]
print(f"\nRows where smallest factor is a large Mersenne prime (>10^6):", file=sys.stderr)
for n, v in large_rows[:20]:
    print(f"  {n}: {v}", file=sys.stderr)
print(f"Total such rows: {len(large_rows)}", file=sys.stderr)
