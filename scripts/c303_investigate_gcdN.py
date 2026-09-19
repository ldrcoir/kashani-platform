#!/usr/bin/env python3
"""
Investigate the gcd = N result from method 8.
This means 2^E ≡ 1 mod N where E = primorial(10^7) × primorial(2474k+1, 10^9).
This is unexpected unless... 

Wait: since 2^1237 ≡ 1 mod N (because N | M(1237)), if 1237 | E, then 2^E = (2^1237)^(E/1237) ≡ 1 mod N.
1237 divides 2474 = 2*1237, so 1237 | E automatically (since E includes primes 2474k+1, and their primorial's
exponent will have 1237 as a factor since 2474k+1 ≥ 2475 means at least one of them is divisible by 1237... no wait).

Actually the simple fact: 1237 | (2474) so 1237 | (2474*k+1 - 1) = 2474*k for any k. So 1237 | (q-1) for any 
prime q of form 2474k+1. So primorial(2474k+1) makes 2^primorial ≡ 2^(1237*something) ≡ 1^(something) ≡ 1 mod N.
This is a trivial result! 2^E ≡ 1 mod N always because 1237 | E.

So the gcd = N is not useful. We need a different exponent.

Try: use base a = 3 or other random base. Then a^E mod N for a != 2 might give non-trivial gcd.

OR: split the exponent. Use E1 = primorial(10^7) (without the 2474k+1 part), then a^E1 - 1 mod N.
If (p-1) is smooth over primes ≤ 10^7 for some prime p | N, we'd find a factor.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod
import math
import time
from pathlib import Path

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1
N = int(F2)

print(f"F2 = {str(F2)[:50]}... ({len(str(N))} digits)")
print()

# Verify: 2^1237 ≡ 1 mod N (should be true since N | M(1237))
print("بررسی: 2^1237 mod F2 ==", powmod(2, 1237, N))
print("اگر 1 باشد، پس 2^E ≡ 1 mod N برای هر E که 1237 | E")
print()

# Use a DIFFERENT base (not 2). Try a = 3.
def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

# Test P-1 with different bases
print("P-1 با پایه‌های مختلف، B1=10^7:")
primes_1e7 = small_primes_up_to(10**7)
print(f"  Generated {len(primes_1e7)} primes")

for base_a in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
    t0 = time.time()
    val = mpz(base_a)
    for p in primes_1e7:
        pe = p
        while pe * p <= 10**7:
            pe *= p
        val = powmod(val, pe, N)
    g = gcd(int(val) - 1, N)
    elapsed = time.time() - t0
    if 1 < g < N:
        print(f"  base a={base_a}: ✓ FACTOR FOUND: {g} (elapsed {elapsed:.1f}s)")
        print(f"    is_prime: {is_prime(g)}")
        cof = N // g
        print(f"    cofactor: {str(cof)[:60]}... ({len(str(cof))} digits)")
        print(f"    is_prime(cofactor): {is_prime(cof)}")
        sys.exit(0)
    elif g == N:
        # Trivial (means all factors p have (p-1) smooth over our primes)
        print(f"  base a={base_a}: gcd = N (trivial, (p-1) smooth for all p | N?) (elapsed {elapsed:.1f}s)")
    else:
        print(f"  base a={base_a}: gcd = 1 (no factor) (elapsed {elapsed:.1f}s)")

# Now try with B1=10^8
print()
print("P-1 با پایه‌های مختلف، B1=10^8 (بزرگ‌تر):")
primes_1e8 = small_primes_up_to(10**8)
print(f"  Generated {len(primes_1e8)} primes")

for base_a in [3, 5, 7, 11, 13]:
    t0 = time.time()
    val = mpz(base_a)
    for p in primes_1e8:
        pe = p
        while pe * p <= 10**8:
            pe *= p
        val = powmod(val, pe, N)
    g = gcd(int(val) - 1, N)
    elapsed = time.time() - t0
    if 1 < g < N:
        print(f"  base a={base_a}: ✓✓✓ FACTOR FOUND: {g} (elapsed {elapsed:.1f}s)")
        print(f"    is_prime: {is_prime(g)}")
        cof = N // g
        print(f"    cofactor: {str(cof)[:60]}... ({len(str(cof))} digits)")
        print(f"    is_prime(cofactor): {is_prime(cof)}")
        sys.exit(0)
    elif g == N:
        print(f"  base a={base_a}: gcd = N (trivial) (elapsed {elapsed:.1f}s)")
    else:
        print(f"  base a={base_a}: gcd = 1 (elapsed {elapsed:.1f}s)")

# Now try P+1 with various starting P values
print()
print("P+1 با P_param های مختلف، exponent = primorial(10^7):")

def lucas_v_mod(k, P_param, N):
    if k == 0: return 2 % N
    if k == 1: return P_param % N
    bits = bin(k)[2:]
    a, b = mpz(P_param) % N, (P_param*P_param - 2) % N
    for bit in bits[1:]:
        c = (a*a - 2) % N
        d = (a*b - P_param) % N
        if bit == '0':
            a, b = c, d
        else:
            e = (b*b - 2) % N
            a, b = d, e
    return int(a)

for P_param in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
    t0 = time.time()
    val = mpz(P_param)
    for p in primes_1e7:
        pe = p
        while pe * p <= 10**7:
            pe *= p
        # V_E(P) where E = pe
        val = mpz(lucas_v_mod(pe, int(val), N))
        # Check gcd(val - 2, N) periodically
    g = gcd(int(val) - 2, N)
    elapsed = time.time() - t0
    if 1 < g < N:
        print(f"  P={P_param}: ✓ FACTOR FOUND: {g} (elapsed {elapsed:.1f}s)")
        sys.exit(0)
    elif g == N:
        print(f"  P={P_param}: gcd = N (trivial) (elapsed {elapsed:.1f}s)")
    else:
        print(f"  P={P_param}: gcd = 1 (elapsed {elapsed:.1f}s)")

print()
print("=== پایان ===")
