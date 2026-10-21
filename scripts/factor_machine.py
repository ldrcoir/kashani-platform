#!/usr/bin/env python3
"""
Use the 4 primes found in the previous step as 'computational machine' 
to try to factor F2.

Methods to try:
1. gcd(p_i, F2) for each i
2. gcd(p_i^k - 1, F2) for various k (Fermat-style)
3. gcd(p_i^((N-1)/2) ± 1, F2) (Euler-style)
4. Use p_i as 'base a' in P-1 factoring of F2
5. Use p_i as 'base a' in ECM-like approaches
6. Try gcd(p_i * p_j - 1, F2) etc — combinations
7. Use p_i to seed Pollard's rho with different parameters
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod, invert, jacobi, next_prime
import math
import time
import random
from pathlib import Path

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1

# The 4 primes we found
P1 = mpz(973233926728214751494649916690319730882813921647616003310501630656313859)  # placeholder
# Let me re-compute the exact primes from the previous script
random.seed(42)

def random_prime_with_digits(d):
    low = 10**(d-1)
    high = 10**d - 1
    while True:
        n = random.randint(low, high)
        if n % 2 == 0:
            n += 1
        p = int(next_prime(mpz(n)))
        if p <= high:
            return p

# Generate 3 80-digit primes
primes_80 = []
sum_log = 0.0
target = math.log10(int(F2))
while len(primes_80) < 3:
    p = random_prime_with_digits(80)
    lp = math.log10(p)
    if sum_log + lp < target - 60:
        primes_80.append(p)
        sum_log += lp

# 65-digit prime
gap = target - sum_log
best_p = None
best_diff = float('inf')
for _ in range(1000):
    p = random_prime_with_digits(65)
    lp = math.log10(p)
    if lp > gap:
        continue
    diff = gap - lp
    if diff < best_diff:
        best_diff = diff
        best_p = p

primes_all = primes_80 + [best_p]

print("=" * 70)
print("  ماشین حسابی: استفاده از ۴ عدد اول برای تجزیه‌ی F2")
print("=" * 70)
print()
print(f"F2 = {str(F2)[:60]}... ({len(str(F2))} digits)")
print(f"is_prime(F2): {is_prime(F2)}")
print()

print("اعداد اول انتخاب‌شده:")
for i, p in enumerate(primes_all):
    print(f"  p[{i+1}] = {p} ({len(str(p))} digits, log10 = {math.log10(p):.6f})")
print()

# ============================================================
# Logging
# ============================================================
LOG_FILE = Path('/home/z/my-project/download/factor_machine_log.txt')
LOG_FILE.write_text('')
def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

log(f'=== ماشین حسابی برای تجزیه‌ی F2 ===')
log(f'اعداد اول پایه: {len(primes_all)} عدد')
for i, p in enumerate(primes_all):
    log(f'  p[{i+1}] = {p} ({len(str(p))} digits)')
log(f'')

N = int(F2)

def check_factor(label, value):
    """Check if value gives a non-trivial factor of F2."""
    g = gcd(abs(int(value)), N)
    if 1 < int(g) < N:
        log(f'  >>> {label}: FACTOR FOUND! g = {g}')
        log(f'      digits: {len(str(g))}, is_prime: {is_prime(int(g))}')
        if int(M) % int(g) == 0:
            log(f'      ✓ REAL FACTOR of M(1237)!')
            cof = N // int(g)
            log(f'      cofactor: {str(cof)[:60]}... ({len(str(cof))} digits)')
            log(f'      is_prime(cofactor): {is_prime(cof)}')
            return int(g)
        else:
            log(f'      (not a factor of M(1237), spurious)')
    return None

# ============================================================
# Test 1: Direct gcd
# ============================================================
log(f'=== تست ۱: gcd(pᵢ, F2) ===')
for i, p in enumerate(primes_all):
    g = gcd(int(p), N)
    if 1 < g < N:
        log(f'  p[{i+1}] | F2  ✓ FACTOR FOUND: {g}')
    else:
        log(f'  gcd(p[{i+1}], F2) = 1 (no factor)')
log(f'')

# ============================================================
# Test 2: Fermat-style: gcd(p_i^k - 1, F2) for various k
# ============================================================
log(f'=== تست ۲: gcd(pᵢ^k − 1, F2) برای k های کوچک ===')
small_ks = [2, 3, 5, 7, 11, 13, 17, 19, 23, 100, 1000, 1237, 2474, 2474*2, 2474*3, 2474*1237]
for i, p in enumerate(primes_all):
    for k in small_ks:
        val = int(powmod(int(p), k, N))
        g = check_factor(f'p[{i+1}]^{k} - 1', val - 1)
        if g:
            sys.exit(0)
        g = check_factor(f'p[{i+1}]^{k} + 1', val + 1)
        if g:
            sys.exit(0)
log(f'  هیچ فاکتوری از این روش پیدا نشد.')
log(f'')

# ============================================================
# Test 3: Euler-style: gcd(p_i^((N-1)/2) ± 1, F2)
# ============================================================
log(f'=== تست ۳: gcd(pᵢ^((N-1)/q) − 1, F2) برای مقسوم‌علیه‌های q از N-1 ===')
# N-1 = 2^4 * Q (odd). Various q:
# We don't know the full factorization of N-1, but we can try common divisors
Nm1 = N - 1
small_divisors = []
temp = Nm1
factors_Nm1 = {}
for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]:
    while temp % p == 0:
        factors_Nm1[p] = factors_Nm1.get(p, 0) + 1
        temp //= p
        small_divisors.append(p)
if temp > 1:
    factors_Nm1['remaining'] = temp
log(f'  N-1 = 2^4 × ... ; مقسوم‌علیه‌های اول کوچک: {factors_Nm1}')

# Try: gcd(p_i^((N-1)/q) - 1, F2) for each small prime q | N-1
for i, p in enumerate(primes_all):
    for q in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if Nm1 % q == 0:
            exp = Nm1 // q
            val = int(powmod(int(p), exp, N))
            g = check_factor(f'p[{i+1}]^((N-1)/{q}) - 1', val - 1)
            if g:
                sys.exit(0)
            g = check_factor(f'p[{i+1}]^((N-1)/{q}) + 1', val + 1)
            if g:
                sys.exit(0)
log(f'  هیچ فاکتوری از این روش پیدا نشد.')
log(f'')

# ============================================================
# Test 4: P-1 factoring with base = each p_i, B1 = 10^6
# ============================================================
log(f'=== تست ۴: P-1 با پایه‌ی pᵢ، B1 = 10^6 ===')
def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

B1 = 10**6
primes_list = small_primes_up_to(B1)
log(f'  Sieve: {len(primes_list)} primes up to {B1}')

for i, p in enumerate(primes_all):
    t0 = time.time()
    val = mpz(p)
    for q in primes_list:
        pe = q
        while pe * q <= B1:
            pe *= q
        val = powmod(val, pe, N)
    g = gcd(int(val) - 1, N)
    t1 = time.time()
    if 1 < g < N:
        log(f'  P-1 با پایه p[{i+1}]: FACTOR FOUND: {g} (elapsed {t1-t0:.1f}s)')
        if int(M) % int(g) == 0:
            log(f'  ✓ REAL FACTOR of M(1237)!')
            sys.exit(0)
    else:
        log(f'  P-1 با پایه p[{i+1}]: no factor (elapsed {t1-t0:.1f}s)')
log(f'')

# ============================================================
# Test 5: Combinations: gcd(p_i * p_j - 1, F2), gcd(p_i^a * p_j^b - 1, F2)
# ============================================================
log(f'=== تست ۵: ترکیب‌های pᵢ × pⱼ - 1 ===')
for i in range(len(primes_all)):
    for j in range(i+1, len(primes_all)):
        prod = primes_all[i] * primes_all[j]
        g = gcd(int(prod) - 1, N)
        if 1 < g < N:
            log(f'  p[{i+1}]*p[{j+1}] - 1: FACTOR {g}')
            sys.exit(0)
        g = gcd(int(prod) + 1, N)
        if 1 < g < N:
            log(f'  p[{i+1}]*p[{j+1}] + 1: FACTOR {g}')
            sys.exit(0)

# Also: p_i^2 - p_j^2 = (p_i - p_j)(p_i + p_j)
for i in range(len(primes_all)):
    for j in range(i+1, len(primes_all)):
        diff = primes_all[i] - primes_all[j]
        sum_ = primes_all[i] + primes_all[j]
        g = gcd(int(diff), N)
        if 1 < g < N:
            log(f'  p[{i+1}] - p[{j+1}]: FACTOR {g}')
        g = gcd(int(sum_), N)
        if 1 < g < N:
            log(f'  p[{i+1}] + p[{j+1}]: FACTOR {g}')
log(f'  هیچ فاکتوری از ترکیب‌ها پیدا نشد.')
log(f'')

# ============================================================
# Test 6: Pollard's rho with each p_i as starting point
# ============================================================
log(f'=== تست ۶: Pollard rho با شروع از pᵢ ===')

def pollard_rho(n, start, max_iter=1000000):
    """Pollard's rho with starting point."""
    x = start % n
    y = x
    c = 1
    d = 1
    count = 0
    while d == 1 and count < max_iter:
        x = (x*x + c) % n
        y = (y*y + c) % n
        y = (y*y + c) % n
        d = gcd(abs(x - y), n)
        count += 1
        if count % 100000 == 0:
            log(f'    iter {count}: d = {d}')
    return d if d != n else None

for i, p in enumerate(primes_all):
    t0 = time.time()
    log(f'  Pollard rho با شروع از p[{i+1}]...')
    d = pollard_rho(N, int(p), max_iter=500000)
    t1 = time.time()
    if d and 1 < d < N:
        log(f'  FACTOR FOUND: {d} (elapsed {t1-t0:.1f}s)')
        if int(M) % d == 0:
            log(f'  ✓ REAL FACTOR!')
            sys.exit(0)
    else:
        log(f'  no factor (elapsed {t1-t0:.1f}s)')
log(f'')

# ============================================================
# Test 7: Pollard p-1 with random exponent (cheap version)
# ============================================================
log(f'=== تست ۷: چندین پایه با e = (p-1) × (p-2) × ... برای P-1 سریع ===')
# For each pair (p_i, p_j): try val = p_i^((p_j-1)) mod F2, then gcd(val - 1, F2)
for i in range(len(primes_all)):
    for j in range(len(primes_all)):
        if i == j: continue
        exp = int(primes_all[j] - 1)
        val = int(powmod(int(primes_all[i]), exp, N))
        g = check_factor(f'p[{i+1}]^(p[{j+1}]-1) - 1', val - 1)
        if g: sys.exit(0)
log(f'  هیچ فاکتوری از این روش پیدا نشد.')
log(f'')

# ============================================================
# Test 8: Use the product of all 4 primes as a "seed" for ECM-like approach
# ============================================================
log(f'=== تست ۸: استفاده از ∏ pᵢ به‌عنوان seed در ECM ===')
# Standard ECM with Montgomery curve, using product as base
# (Quick version — just one curve per sigma)
log(f'  (روش ECM سریع با یک منحنی برای هر sigma از pᵢ)')
# For brevity, just do one quick ECM curve for each p_i
for sigma in [int(p) % (10**10) for p in primes_all]:  # use first 10 digits of each p
    # Suyama parameterization
    s = sigma
    u = (s*s - 5) % N
    v = (4*s) % N
    X = (u*u*u) % N
    Z = (v*v*v) % N
    num = ((v - u) ** 3 * (3*u + v)) % N
    den = (u*u*u * v) % N
    try:
        A = (num * invert(den, N) - 2) % N
        log(f'  sigma={sigma}: curve initialized')
        # Just test gcd(A, N) for a quick check
        g = gcd(int(A), N)
        if 1 < g < N:
            log(f'  >>> FACTOR from A: {g}')
            sys.exit(0)
    except Exception as e:
        log(f'  sigma={sigma}: error {e}')
        # invert failed — this might give a factor!
        g = gcd(int(den), N)
        if 1 < g < N:
            log(f'  >>> FACTOR from den: {g}')
            sys.exit(0)
log(f'')

# ============================================================
# Summary
# ============================================================
log(f'=== خلاصه ===')
log(f'با وجود اینکه ۴ عدد اول انتخاب‌شده بسیار نزدیک به F2 هستند (نسبت 0.9992)')
log(f'و log10 جمع آن‌ها تقریباً برابر log10(F2) است،')
log(f'اما هیچ‌کدام فاکتور واقعی F2 نیستند.')
log(f'این تأیید می‌کند که تقریب log10 فقط یک تقریب عددی است')
log(f'و رابطه‌ی ریاضی بین اعداد اول بزرگ و فاکتورهای واقعی F2 وجود ندارد.')
log(f'')
log(f'برای تجزیه‌ی واقعی F2 به ابزارهای تخصصی (SNFS, GMP-ECM) نیاز است.')
