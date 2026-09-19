#!/usr/bin/env python3
"""
Compute ratio R = F2 / (F1 * product_of_primes) and check divisibility by primes.

We have F1 * product(primes) ≈ F2.
The exact relation: F2 = F1 * product(primes) * R for some R.
R = F2 / (F1 * product(primes)) should be close to 1 (within 10^error).

Check if R (or F2 - F1*prod(primes)) is divisible by small primes.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, invert, powmod, jacobi
import math
import time
from pathlib import Path

# Load best strategy primes from JSON
import json
with open('/home/z/my-project/download/log10_factorization_results.json') as f:
    data = json.load(f)

best_idx = data['best_strategy_index']
best = data['strategies'][best_idx]
primes = best['primes']
print(f"Best strategy: {best['name']}")
print(f"Number of primes: {len(primes)}")
print(f"Sum log10: {best['sum']:.10f}")
print(f"Target log10: {data['metadata']['target']:.10f}")
print(f"Error log10: {best['error']:.10e}")
print()

# Setup
P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1

# Compute product of selected primes
product = mpz(1)
for p in primes:
    product *= mpz(p)

log10_product = math.log10(int(product))
print(f"F1 = {F1}")
print(f"   ({len(str(F1))} digits)")
print(f"product of {len(primes)} primes = {str(product)[:60]}...")
print(f"   ({len(str(product))} digits)")
print(f"log10(product) = {log10_product:.10f}")
print()

# Compute F1 * product
F1_times_product = F1 * product
print(f"F1 * product = {str(F1_times_product)[:60]}...")
print(f"   ({len(str(F1_times_product))} digits)")
print()

# Compute difference F2 - F1 * product
diff_int = F2 - F1_times_product
print(f"F2 - F1*product = {diff_int}")
print(f"   ({len(str(abs(diff_int)))} digits, sign={'+'if diff_int>0 else '-' if diff_int<0 else '0'})")
print(f"log10|diff| = {math.log10(abs(int(diff_int))):.10f}")
print()

# Compute ratio R = F2 / (F1 * product) as a rational number
# Note: F1 * product may not divide F2. Let's see if it does.
print("=" * 70)
print("Checking: is F2 divisible by F1 * product?")
g = gcd(F1 * product, F2)
print(f"gcd(F1*product, F2) = {g}")
print(f"   ({len(str(g))} digits)")
if F2 % (F1 * product) == 0:
    R = F2 // (F1 * product)
    print(f"YES! R = F2 / (F1*product) = {R}")
    print(f"   R has {len(str(R))} digits")
    print(f"   is_prime(R): {is_prime(R)}")
else:
    print(f"NO, F1*product does not divide F2 exactly")
    # Compute fractional R
    # R = F2 / (F1 * product). As a real number, R = 10^(log10(F2) - log10(F1) - log10(product))
    log10_R = math.log10(int(F2)) - math.log10(int(F1)) - log10_product
    print(f"log10(R) = {log10_R:.15f}")
    print(f"R ≈ 10^({log10_R:.6f}) ≈ {10**log10_R:.10f}")
    print()
    # Check if R is close to a small integer or simple fraction
    R_float = 10**log10_R
    print(f"R = {R_float!r}")
    # If R ≈ 1, then F1*product is essentially F2 (off by a small factor)
    # Check if F2 - F1*product is divisible by small primes
    print()
    print("=" * 70)
    print(f"Checking: F2 - F1*product = {diff_int}")
    print(f"  |diff| digits = {len(str(abs(diff_int)))}")
    print(f"  Is diff prime? {is_prime(diff_int) if abs(diff_int) > 1 else 'No (too small)'}")
    print()
    
    # Trial divide diff by small primes
    print("Trial-dividing |diff| by small primes up to 10^7:")
    diff_abs = abs(diff_int)
    factors = []
    remaining = diff_abs
    # Small primes via sieve
    LIMIT = 10**7
    sieve = bytearray([1]) * (LIMIT + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(LIMIT**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    
    for p in range(2, LIMIT + 1):
        if sieve[p]:
            while remaining % p == 0:
                factors.append(p)
                remaining //= p
            if remaining == 1:
                break
    
    if factors:
        print(f"  Found factors: {factors}")
        print(f"  Remaining after trial division: {remaining}")
        if remaining > 1:
            print(f"  Remaining has {len(str(remaining))} digits, is_prime: {is_prime(remaining)}")
    else:
        print(f"  No small factor found up to 10^7")
        print(f"  Remaining: {remaining} ({len(str(remaining))} digits)")
        print(f"  is_prime(remaining): {is_prime(remaining) if remaining > 1 else 'n/a'}")
    
    print()
    # Also: gcd(diff, F2) might be interesting
    g_diff_F2 = gcd(diff_abs, F2)
    print(f"gcd(|diff|, F2) = {g_diff_F2}")
    print(f"  ({len(str(g_diff_F2))} digits, == F2? {g_diff_F2 == F2}, is_prime: {is_prime(g_diff_F2) if g_diff_F2 > 1 else 'n/a'})")
    
    g_diff_F1 = gcd(diff_abs, F1)
    print(f"gcd(|diff|, F1) = {g_diff_F1}")
    print(f"  (== F1? {g_diff_F1 == F1}, is_prime: {is_prime(g_diff_F1) if g_diff_F1 > 1 else 'n/a'})")
    
    g_diff_M = gcd(diff_abs, M)
    print(f"gcd(|diff|, M) = {g_diff_M}")
    print(f"  (== M? {g_diff_M == M}, is_prime: {is_prime(g_diff_M) if g_diff_M > 1 else 'n/a'})")

# ============================================================
# Now: the more interesting question
# We have F1 * product ≈ F2 with relative error 10^(-0.000146)
# So R = F2/(F1*product) ≈ 1.000336
# 
# Question: is R close to a "simple" prime number or 1/prime or some rational?
# 1.000336... ≈ 1 + 1/2976
# 1/2976 = 1/(2^5 * 3 * 31) — not prime
# Hmm.
# 
# Actually, the more meaningful question:
# Does F2 / F1 reduce? gcd(F2, F1) should be 1 (they're both prime factors of M).
# Does F2 % product == 0? Or F2 / product (integer div) gives something interesting?
# 
# Let's also try: F2 mod each prime in the selection
# ============================================================
print()
print("=" * 70)
print("Checking F2 mod (each selected prime):")
non_zero_mods = []
for p in primes:
    r = int(F2 % p)
    if r != 0:
        non_zero_mods.append((p, r))

print(f"  Of {len(primes)} primes, {len(non_zero_mods)} do NOT divide F2 (as expected, since F2 is huge)")
print(f"  (None of these small primes should divide F2 — F2's factors are all very large)")

# More interesting: try to find if F2 has small factors we missed
# F2 = M(1237)/F1. F1 is the 70-digit factor. Are there factors of F2 between, say, 2 and 10^9?
# We've done P-1, but let's also trial-divide F2 (just to confirm no small factor).
print()
print("=" * 70)
print("Trial-dividing F2 by primes up to 10^7 (sanity check):")
F2_remaining = F2
small_factors_F2 = []
LIMIT = 10**7
for p in range(2, LIMIT + 1):
    if sieve[p]:
        while F2_remaining % p == 0:
            small_factors_F2.append(p)
            F2_remaining //= p

if small_factors_F2:
    print(f"  Small factors of F2: {small_factors_F2}")
else:
    print(f"  No small factors of F2 below 10^7 (expected — all factors of F2 are huge)")
print(f"  F2_remaining after trial div: {len(str(F2_remaining))} digits, is_prime: {is_prime(F2_remaining)}")

# ============================================================
# The REAL question: which prime, when multiplied with F1*product, divides F2?
# i.e., find prime q such that (F1 * product * q) | F2
# Equivalently: q | (F2 / (F1 * product)) — but this is a fraction.
# Better: find prime q such that (F1 * product * q) divides F2*something
# OR: find prime q such that F2 ≡ 0 mod (F1 * product * q / d) for some d
# 
# Actually the cleanest version:
# Define D = gcd(F1 * product, F2). 
# F2 / D is what's left of F2 after removing the "matched" part with F1*product.
# This quotient should be a divisor of F2. If it's prime, we win!
# ============================================================
print()
print("=" * 70)
print("Real test: gcd(F1 * product, F2)")
print(f"  F1*product has {len(str(F1*product))} digits")
print(f"  F2 has {len(str(F2))} digits")
g_big = gcd(F1 * product, F2)
print(f"  gcd(F1*product, F2) = {g_big}")
print(f"  ({len(str(g_big))} digits)")
print(f"  == F1? {g_big == F1}")
print(f"  == product? {g_big == product}")
print(f"  is_prime: {is_prime(g_big) if g_big > 1 else 'n/a'}")

# So: gcd(F1*product, F2) tells us what fraction of F1*product actually divides F2.
# If it's F1 only (since F1 | F2 is FALSE — F2 = M/F1, gcd(F1, F2) = 1):
# Actually gcd(F1, F2) = 1 (since F1 is a prime factor and F2 = M/F1, coprime).
# So gcd(F1*product, F2) = gcd(product, F2) (since gcd(F1, F2)=1).
print()
print("Note: gcd(F1, F2) should be 1 since F1 is a prime factor and F2 = M/F1.")
print(f"gcd(F1, F2) = {gcd(F1, F2)}")
print(f"So gcd(F1*product, F2) = gcd(product, F2) = {gcd(product, F2)}")

# None of the small primes in our selection divide F2 (they're all small)
# So gcd(product, F2) = 1
# This means: F1*product is COPRIME to F2! 
# So no simple "q divides both" exists.

# ============================================================
# The user's question re-interpreted:
# "bebin bar zarbe kodom adade aval bakhsh paziri mide" 
#   = "see for multiplication by which prime it gives divisibility"
# 
# Maybe they mean: for which prime q does (F1 * product * q) divide (F2 * something)?
# OR: for which prime q does q divide (F2 - F1*product)? — diff_int
# ============================================================
print()
print("=" * 70)
print("User question: which prime q divides (F2 - F1*product)?")
print(f"diff = F2 - F1*product = {diff_int}")
print(f"  digits: {len(str(abs(diff_int)))}")
print(f"  sign: {'+' if diff_int > 0 else '-' if diff_int < 0 else '0'}")
print()
print("Trial dividing diff by primes up to 10^7:")
print(f"  Factors found: {factors if 'factors' in locals() else 'none'}")
print(f"  Remaining: {remaining if 'remaining' in locals() else 'diff'}")
if 'remaining' in locals() and remaining > 1:
    print(f"  Remaining digits: {len(str(remaining))}")
    print(f"  is_prime(remaining): {is_prime(remaining)}")
    # Try a few more divisibility tests
    print()
    print("  Testing divisibility by next primes 10^7 to 10^8 (first 1000):")
    # Generate primes in (10^7, 10^8) via segmented sieve (small segment)
    found_more = False
    for seg_start in range(10**7 + 1, 10**8, 10**6):
        seg_end = seg_start + 10**6 - 1
        seg_sieve = bytearray([1]) * (10**6)
        for p in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]:
            start = ((seg_start + p - 1) // p) * p
            for j in range(start - seg_start, 10**6, p):
                seg_sieve[j] = 0
        # Also use primes up to sqrt(10^8) = 10^4
        for p in range(101, 10001):
            if sieve[p]:
                start = ((seg_start + p - 1) // p) * p
                for j in range(start - seg_start, 10**6, p):
                    seg_sieve[j] = 0
        for i, is_p in enumerate(seg_sieve):
            if is_p:
                p = seg_start + i
                if p > 10**8: break
                while remaining % p == 0:
                    print(f"    Found factor: {p}")
                    factors.append(p)
                    remaining //= p
                    found_more = True
        if remaining == 1 or time.time() - time_start > 60:
            break
    print(f"  After more trial div: remaining = {remaining} ({len(str(remaining))} digits)")
    print(f"  is_prime(remaining): {is_prime(remaining)}")

time_start = time.time()
