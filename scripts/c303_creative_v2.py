#!/usr/bin/env python3
"""
More creative approaches on F2 (c303):

5. Use ECM with Mersenne-aware curve selection
6. Try Williams P+1 with structured smoothness bounds
7. Try Fermat-like: search for x such that x^2 ≡ y^2 mod N, gcd(x-y, N) is factor
   - For Mersenne, x = 2^(some_special_k) gives structured differences
8. Apply ECM with base from a Mersenne-related elliptic curve
9. Try Williams P+1 with the 2474k+1 primes
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, next_prime, gcd, powmod, invert, jacobi
import math
import time
import random
from pathlib import Path

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1
N = int(F2)

LOG = Path('/home/z/my-project/download/c303_creative_v2.log')
LOG.write_text('')
def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')

log(f'=== روش‌های ابداعی پیشرفته روی F2 (c303) ===')
log(f'N = F2, {len(str(N))} digits')
log(f'')

# Generate structure-aware primes (Mersenne form: q = 2474k+1)
def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

log(f'تولید primes of form 2474k+1 تا 10^9...')
t0 = time.time()
mersenne_primes = []
for k in range(1, (10**9 - 1) // 2474 + 1):
    q = 2474 * k + 1
    # Quick compositeness filter
    if q % 3 == 0 or q % 5 == 0 or q % 7 == 0 or q % 11 == 0 or q % 13 == 0:
        continue
    if q % 17 == 0 or q % 19 == 0 or q % 23 == 0 or q % 29 == 0 or q % 31 == 0:
        continue
    if q % 37 == 0 or q % 41 == 0 or q % 43 == 0 or q % 47 == 0 or q % 53 == 0:
        continue
    if q % 59 == 0 or q % 61 == 0 or q % 67 == 0 or q % 71 == 0 or q % 73 == 0:
        continue
    if q % 79 == 0 or q % 83 == 0 or q % 89 == 0 or q % 97 == 0:
        continue
    if is_prime(q):
        mersenne_primes.append(q)
t1 = time.time()
log(f'  {len(mersenne_primes)} primes in {t1-t0:.1f}s, بزرگ‌ترین: {mersenne_primes[-1]}')
log(f'')

# ============================================================
# روش ۵: P+1 با exponent = primorial(2474k+1)
# ============================================================
log(f'=== روش ۵: P+1 با exponent = primorial(2474k+1) تا 10^9 ===')
log(f'')

def lucas_v_mod(k, P_param, N):
    """Compute V_k(P, 1) mod N using fast doubling."""
    if k == 0: return 2 % N
    if k == 1: return P_param % N
    # Fast doubling with (V_n, V_{n+1})
    # V_2n = V_n^2 - 2 (since Q=1)
    # V_2n+1 = V_n * V_{n+1} - P * Q^n = V_n * V_{n+1} - P (Q=1)
    bits = bin(k)[2:]
    a, b = mpz(P_param) % N, (P_param*P_param - 2) % N  # V_1, V_2
    for bit in bits[1:]:
        c = (a*a - 2) % N  # V_2n
        d = (a*b - P_param) % N  # V_2n+1
        if bit == '0':
            a, b = c, d
        else:
            e = (b*b - 2) % N  # V_2n+2
            a, b = d, e
    return int(a)

t0 = time.time()
# Try several P_param values
for P_param in [3, 5, 7, 11, 13, 17]:
    log(f'  P+1 with P_param = {P_param}, exponent = ∏ q_i for {len(mersenne_primes)} primes of form 2474k+1')
    # Compute V_E mod N incrementally
    # V_{k1*k2} = some function of V_k1, V_k2... complex
    # Simpler: use the property V_{k1*k2}(P) = V_{k2}(V_{k1}(P))
    # So V_(∏ q_i)(P) = V_(∏ q_i from i=1 to n)(P) = compose via V_{q_i}
    
    val = mpz(P_param)
    for i, q in enumerate(mersenne_primes[:200]):  # use first 200 for speed
        val = mpz(lucas_v_mod(q, int(val), N))
        # Check gcd(val - 2, N)
        g = gcd(int(val) - 2, N)
        if 1 < g < N:
            log(f'  >>> FACTOR FOUND at prime #{i+1} (q={q}): {g}')
            log(f'  is_prime: {is_prime(g)}')
            cof = N // g
            log(f'  cofactor: {str(cof)[:60]}... ({len(str(cof))} digits)')
            sys.exit(0)
        if (i+1) % 50 == 0:
            elapsed = time.time() - t0
            log(f'    P={P_param}: progress i={i+1}/200, elapsed={elapsed:.1f}s')
    elapsed = time.time() - t0
    log(f'  P={P_param}: no factor after 200 primes (elapsed {elapsed:.1f}s)')
log(f'')

# ============================================================
# روش ۶: Fermat-like with Mersenne structure
# ============================================================
log(f'=== روش ۶: Fermat-like با ساختار Mersenne ===')
log(f'ایده: برای هر q از فرم 2474k+1، بررسی کنیم آیا 2^(q-1)/2 ≡ ±1 mod q (Euler)')
log(f'و اگر +1 باشد، آیا 2^((q-1)/4) مقدار خاصی می‌دهد')
log(f'')

# Actually a more interesting idea: 
# Use the "Aurifeuillean" structure. We know F1 = 2474*k+1 with k ≈ 10^66.
# What if other factors of F2 have similar structure? Try k with specific form.

# Idea: try k = 1237 * m + c for small c. This ensures q = 2474*(1237*m + c) + 1
#                                                       = 3062338*m + 2474*c + 1
# These are primes q ≡ 1 mod 3062338 (which is 2*1237^2). More restrictive.

t0 = time.time()
small_primes = small_primes_up_to(10**6)
factor_found = None
tested = 0
prime_count = 0
# Try q = 2*1237*1237*m + 1 = 3062338*m + 1 for m up to 100k
# But this is a more restrictive subset of 2474k+1 (k = 1237*m)
for m in range(1, 100001):
    q = 3062338 * m + 1  # = 2474 * (1237*m) + 1
    tested += 1
    # Quick check
    if q % 3 == 0 or q % 5 == 0 or q % 7 == 0 or q % 11 == 0 or q % 13 == 0:
        continue
    if not is_prime(q):
        continue
    prime_count += 1
    if N % q == 0:
        factor_found = q
        log(f'  >>> FACTOR FOUND at m={m}: {q}')
        log(f'  is_prime: True')
        cof = N // q
        log(f'  cofactor: {cof}')
        break
    if m % 10000 == 0:
        elapsed = time.time() - t0
        log(f'    progress: m={m}/100000, tested={tested}, primes={prime_count}, elapsed={elapsed:.1f}s')

elapsed = time.time() - t0
if not factor_found:
    log(f'  ✗ هیچ فاکتور در فرم q = 3062338*m + 1 با m ≤ 100000 پیدا نشد')
    log(f'  (elapsed {elapsed:.1f}s, tested {tested}, primes {prime_count})')
log(f'')

# ============================================================
# روش ۷: Use 2 as base, check 2^((q-1)/2) mod q for structured q
# ============================================================
log(f'=== روش ۷: بررسی 2^((q-1)/2) mod q برای q از فرم 2474k+1 ===')
log(f'ایده: q | F2 و q اول، پس 2^1237 ≡ 1 mod q، یعنی 2^619 = ±1 mod q')
log(f'بررسی کنیم آیا 2^619 mod q با کاندیدهای ما چطور است')
log(f'')

# For each candidate q (prime of form 2474k+1), check if 2^1237 ≡ 1 mod q
# If yes, q is a factor of M(1237) — could be F1, F2's factors, etc.

# We've already done this in the trial division, so let's think differently.
# 
# New idea: What if F2's factor q has q-1 with specific structure?
# q = 2474*k + 1 where k itself has special form (e.g., k = some prime power)

# Test q = 2474*p + 1 where p is a prime up to 10^6
log(f'  آزمایش q = 2474*p + 1 برای p اول تا 10^6...')
t0 = time.time()
factor_found = None
prime_count = 0
tested = 0
for p in small_primes:
    q = 2474 * p + 1
    tested += 1
    if q % 3 == 0 or q % 5 == 0 or q % 7 == 0 or q % 11 == 0 or q % 13 == 0:
        continue
    if not is_prime(q):
        continue
    prime_count += 1
    if N % q == 0:
        factor_found = q
        log(f'  >>> FACTOR FOUND at p={p}: q = {q}')
        log(f'  cofactor: {N // q}')
        break

elapsed = time.time() - t0
if not factor_found:
    log(f'  ✗ هیچ فاکتور در فرم q = 2474*p + 1 با p ≤ 10^6 پیدا نشد')
    log(f'  (elapsed {elapsed:.1f}s, tested {tested}, primes {prime_count})')
log(f'')

# ============================================================
# روش ۸: Pollard's p-1 with exponent including large primes of form 2474k+1
# ============================================================
log(f'=== روش ۸: P-1 با B1=10^7 + اضافه کردن primes 2474k+1 بزرگ‌تر تا 10^9 ===')
log(f'')

t0 = time.time()
all_primes_1e7 = small_primes_up_to(10**7)
log(f'  Generated {len(all_primes_1e7)} primes up to 10^7 in {time.time()-t0:.1f}s')

# P-1 with B1=10^7 + structured primes up to 10^9
val = mpz(2)
log(f'  مرحله ۱: P-1 استاندارد با B1=10^7...')
t0 = time.time()
for p in all_primes_1e7:
    pe = p
    while pe * p <= 10**7:
        pe *= p
    val = powmod(val, pe, N)
g = gcd(int(val) - 1, N)
log(f'  بعد از مرحله ۱: gcd = {g} (elapsed {time.time()-t0:.1f}s)')
if 1 < g < N:
    log(f'  ✓✓✓ FACTOR: {g}')
    sys.exit(0)

log(f'  مرحله ۲: اضافه کردن primes 2474k+1 تا 10^9 به exponent...')
t0 = time.time()
for q in mersenne_primes:
    if q > 10**7:  # only new ones
        val = powmod(val, q, N)
g = gcd(int(val) - 1, N)
log(f'  بعد از مرحله ۲: gcd = {g} (elapsed {time.time()-t0:.1f}s)')
if 1 < g < N:
    log(f'  ✓✓✓ FACTOR: {g}')
log(f'')

# ============================================================
# روش ۹: ECM-style با استفاده از σ که primes 2474k+1 هستند
# ============================================================
log(f'=== روش ۹: ECM با sigmas از فرم 2474k+1 (simulated, single curve each) ===')
log(f'  (این فقط یک منحنی برای هر sigma آزمایش می‌کند)')
log(f'')

# Use first 10 primes 2474k+1 as sigmas in a simple ECM
def simple_ecm_one_curve(N, sigma, B1=10**5):
    """One simple Weierstrass ECM curve. Returns factor or None."""
    # Suyama parameterization
    s = sigma
    u = (s*s - 5) % N
    v = (4*s) % N
    X = (u*u*u) % N
    Z = (v*v*v) % N
    den = (u*u*u * v) % N
    try:
        A = (int(((v - u) ** 3 * (3*u + v)) % N) * int(invert(den, N)) - 2) % N
        # Check gcd(A, N) — might give factor
        g = gcd(A, N)
        if 1 < g < N:
            return int(g)
    except:
        g = gcd(int(den), N)
        if 1 < g < N:
            return int(g)
        return None
    # Quick stage 1: compute multiples of base point
    # Use B1 = 10^5 for speed
    return None

# Test with several sigmas
for sigma in mersenne_primes[:20]:
    result = simple_ecm_one_curve(N, sigma)
    if result:
        log(f'  sigma = {sigma}: FACTOR {result}')
        sys.exit(0)
log(f'  ✗ هیچ فاکتوری از این روش پیدا نشد')
log(f'')

# ============================================================
# روش ۱۰: Use 2 as base and a Mersenne-specific exponent
# For M(1237) factors q: ord_q(2) | 1237 (since 2^1237 ≡ 1 mod q)
# So q ≡ 1 mod ord_q(2) which is 1 or 1237.
# If ord_q(2) = 1237, then 1237 | (q-1), so q ≡ 1 mod 1237.
# If ord_q(2) = 1, then q | (2-1) = 1, impossible for q > 1.
# So q ≡ 1 mod 1237 (we already know).
# But we want q ≡ 1 mod 2474 (since q is odd, q-1 even, so 2 | (q-1)).
# ============================================================
log(f'=== روش ۱۰: استفاده از ord_q(2) = 1237 — آزمایش فرم‌های ساده‌تر ===')
log(f'بررسی: آیا فاکتور q از F2 در فرم ساده‌تری هست؟ مثلاً q = 2 * 1237 * k + 1 با k کوچک')
log(f'')

# Already tested up to k = 400k in method 1
# Try larger k values (up to 10^10 = 10 billion) with a different strategy:
# Focus on k = prime numbers (might be more likely for factored k-1)
# Or k = smooth numbers (where k has small prime factors)

# Strategy: pick k that's prime, since prime k is "least structured"
# This isn't necessarily good, but let's try.

# Also: pick k = 1237*m + 1 (already done as 3062338*m + 1 form)

# Different idea: pick k such that 2474*k+1 is of form a^2 + 1 or similar (algebraic)
# Hard to enumerate, skip.

# Let's just try a quick burst up to k = 5*10^6 to see if any factor in that range
log(f'آزمایش سریع: k از 404203 (محل توقف قبلی) تا 5*10^6...')
t0 = time.time()
factor_found = None
tested = 0
prime_count = 0
for k in range(404204, 5*10**6 + 1):
    q = 2474 * k + 1
    tested += 1
    if q % 3 == 0 or q % 5 == 0 or q % 7 == 0 or q % 11 == 0 or q % 13 == 0:
        continue
    if not is_prime(q):
        continue
    prime_count += 1
    if N % q == 0:
        factor_found = q
        log(f'  >>> FACTOR FOUND at k={k}: {q}')
        cof = N // q
        log(f'  cofactor: {cof}')
        break
    if k % 1000000 == 0:
        elapsed = time.time() - t0
        log(f'    progress: k={k}/5M, tested={tested}, primes={prime_count}, elapsed={elapsed:.1f}s')
    if time.time() - t0 > 30:
        log(f'    time budget exceeded, stopping at k={k}')
        break

elapsed = time.time() - t0
if not factor_found:
    log(f'  ✗ هیچ فاکتور با k ≤ {k} پیدا نشد (elapsed {elapsed:.1f}s)')
log(f'')

log(f'=== پایان ===')
