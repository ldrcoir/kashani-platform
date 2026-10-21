#!/usr/bin/env python3
"""
Half-GCD trick: accumulate product of (a^((N-1)/2) - 1) mod N for many a,
then gcd with N. If any a is a 'split' (gives 1 mod q1, something else mod q2),
the product will catch that factor.
"""

import gmpy2
from gmpy2 import mpz, powmod, gcd, jacobi
import random
import time

p = 1237
M = mpz(2)**p - 1
F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
N = M // F1

print("Distribution of a^((N-1)/2) mod N over 200 samples:")
counts = {}
for _ in range(200):
    a = mpz(random.randint(2, int(N) - 1))
    val = powmod(a, (N - 1) // 2, N)
    bucket = '1' if val == 1 else ('-1' if val == N - 1 else 'other')
    counts[bucket] = counts.get(bucket, 0) + 1
print(f"  Counts: {counts}")

# Try the half-GCD trick
print()
print("Half-GCD trick: 100 witnesses")
t0 = time.time()
P = mpz(1)
for _ in range(100):
    a = mpz(random.randint(2, int(N) - 1))
    val = powmod(a, (N - 1) // 2, N)
    P = (P * (val - 1)) % N
g = gcd(P, N)
elapsed = time.time() - t0
print(f"  gcd(prod, N) = {g}")
print(f"  Elapsed: {elapsed:.1f}s")

# 1000 witnesses
print()
print("1000 witnesses:")
t0 = time.time()
P = mpz(1)
for _ in range(1000):
    a = mpz(random.randint(2, int(N) - 1))
    val = powmod(a, (N - 1) // 2, N)
    P = (P * (val - 1)) % N
g = gcd(P, N)
elapsed = time.time() - t0
print(f"  gcd(prod, N) = {g}")
print(f"  Elapsed: {elapsed:.1f}s")

# Try with N-1/4 instead
print()
print("Using (N-1)/4 (might catch different structure):")
t0 = time.time()
P = mpz(1)
for _ in range(1000):
    a = mpz(random.randint(2, int(N) - 1))
    val = powmod(a, (N - 1) // 4, N)
    # val^2 should be a^((N-1)/2). Use val-1 and val+1
    P = (P * (val - 1)) % N
    P = (P * (val + 1)) % N
g = gcd(P, N)
elapsed = time.time() - t0
print(f"  gcd(prod, N) = {g}")
print(f"  Elapsed: {elapsed:.1f}s")

# Now try a^((N-1)/4) directly (with val^2 - 1, val^2 + 1)
print()
print("Using a^((N-1)/4) squared (Euler for half):")
t0 = time.time()
P = mpz(1)
for _ in range(100):
    a = mpz(random.randint(2, int(N) - 1))
    val = powmod(a, (N - 1) // 4, N)
    val_sq = (val * val) % N
    P = (P * (val_sq - 1)) % N
    P = (P * (val_sq + 1)) % N
g = gcd(P, N)
elapsed = time.time() - t0
print(f"  gcd(prod, N) = {g}")
print(f"  Elapsed: {elapsed:.1f}s")

# Try with (N-1)/8 powers (8th roots structure)
print()
print("Using a^((N-1)/8) with 8th roots of unity search:")
t0 = time.time()
P = mpz(1)
for _ in range(100):
    a = mpz(random.randint(2, int(N) - 1))
    val = powmod(a, (N - 1) // 8, N)
    # val^8 = a^(N-1) = 1 if N is "Fermat-pseudoprime to base a"
    # val^4 = a^((N-1)/2) (Euler criterion, should be ±1 mod q_i)
    # val^2 = a^((N-1)/4)
    val_sq = (val * val) % N
    val_q = (val_sq * val_sq) % N
    val_oct = (val_q * val_q) % N
    # gcd(val_oct - 1, N): catches cases where val^8 ≡ 1 mod q_i for some i but not all
    P = (P * (val_oct - 1)) % N
    # Also try val^4 - 1 and val^2 - 1
    P = (P * (val_q - 1)) % N
    P = (P * (val_sq - 1)) % N
    P = (P * (val - 1)) % N
g = gcd(P, N)
elapsed = time.time() - t0
print(f"  gcd(prod, N) = {g}")
print(f"  Elapsed: {elapsed:.1f}s")

# What's a^(N-1) mod N for some a?
print()
print("Test a^(N-1) mod N for 10 random a:")
for _ in range(10):
    a = mpz(random.randint(2, int(N) - 1))
    val = powmod(a, N - 1, N)
    print(f"  a^{{N-1}} mod N = {'1' if val == 1 else f'other ({len(str(val))} digits, ends in {str(val)[-5:]})'}")
