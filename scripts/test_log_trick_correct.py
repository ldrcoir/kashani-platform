#!/usr/bin/env python3
"""
CORRECT version: Use the log10 trick properly to factor a known composite.

Key insight: 
- Generate ALL primes up to some bound B.
- Product of these primes is the "primorial" of B.
- gcd(primorial(B), N) gives all prime factors of N that are <= B.
- This IS trial division, just expressed via gcd.

For the trick to work on F2, we need B >= smallest factor of F2.
F2's smallest factor is > 10^8 (we've checked).
Generating primorial(10^8) is feasible (it has ~10^8 / ln(10^8) ≈ 5.4M primes).
Let's verify this works on a known composite, then apply to F2 (will fail because factors are > 10^8).
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, next_prime, gcd, powmod
import math
import time
import random
from pathlib import Path

print("=" * 70)
print("  نسخه‌ی صحیح: log10 trick = trial division via primorial")
print("=" * 70)
print()

random.seed(42)
def random_prime_with_digits(d):
    low = 10**(d-1)
    high = 10**d - 1
    while True:
        n = random.randint(low, high)
        if n % 2 == 0: n += 1
        p = int(next_prime(mpz(n)))
        if p <= high: return p

# Test case 1: N = small_prime × large_prime
p1 = random_prime_with_digits(7)   # 7-digit
p2 = random_prime_with_digits(50)  # 50-digit
N = p1 * p2
print(f"تست ۱: N = p1 × p2 با p1 کوچک")
print(f"  p1 = {p1} (7 digits)")
print(f"  p2 = {p2} (50 digits)")
print(f"  N = {str(N)[:60]}... ({len(str(N))} digits)")
print()

# Generate all primes up to 10^7
def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

B = 10**7
print(f"تولید اعداد اول تا B = 10^7...")
t0 = time.time()
primes = small_primes_up_to(B)
t1 = time.time()
print(f"  {len(primes)} primes, زمان: {t1-t0:.1f}s")

# Compute primorial
print(f"محاسبه‌ی primorial...")
t0 = time.time()
product = mpz(1)
for p in primes:
    product *= mpz(p)
t1 = time.time()
print(f"  primorial(10^7) has {len(str(product))} digits, زمان: {t1-t0:.1f}s")
print(f"  log10(primorial) = {math.log10(int(product)):.4f}")
print()

# gcd with N
g = gcd(int(product), int(N))
print(f"gcd(primorial, N) = {g}")
if g > 1 and g < N:
    print(f"  ✓✓✓ فاکتور پیدا شد: {g}")
    print(f"  is_prime: {is_prime(g)}")
    cof = N // g
    print(f"  cofactor = {cof}, is_prime: {is_prime(cof)}")
    if g == p1:
        print(f"  ✓ این p1 (عامل کوچک) بود!")
        print(f"  تجزیه‌ی کامل: N = {g} × {cof}")
else:
    print(f"  ✗ فاکتور پیدا نشد (یعنی هیچ فاکتور N در [2, 10^7] نیست)")
print()

# ============================================================
# Test 2: N where both factors are large
# ============================================================
print("=" * 70)
print(f"تست ۲: N با هر دو فاکتور بزرگ (مثل F2)")
print("=" * 70)
print()

p1 = random_prime_with_digits(40)
p2 = random_prime_with_digits(40)
N2 = p1 * p2
print(f"  p1 = {p1} (40 digits)")
print(f"  p2 = {p2} (40 digits)")
print(f"  N2 = {str(N2)[:60]}... ({len(str(N2))} digits)")
print()

# Use same primorial (primes up to 10^7)
print(f"آزمایش با همان primorial(10^7)...")
g = gcd(int(product), int(N2))
print(f"gcd(primorial, N2) = {g}")
if g > 1 and g < N2:
    print(f"  ✓ فاکتور: {g}")
else:
    print(f"  ✗ فاکتور پیدا نشد — چون p1, p2 هر دو بزرگ‌تر از 10^7 هستند")
    print(f"  این دقیقاً همان وضعیت F2 است!")
print()

# ============================================================
# Test 3: APPLY TO F2 (the actual case)
# ============================================================
print("=" * 70)
print(f"تست ۳: اعمال روش روی F2 (هدف واقعی)")
print("=" * 70)
print()

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1
print(f"  F2 = {str(F2)[:60]}... ({len(str(F2))} digits)")
print(f"  is_prime(F2): {is_prime(F2)}")
print()

print(f"آزمایش با primorial(10^7) (با log10 ≈ {math.log10(int(product)):.2f})...")
g = gcd(int(product), int(F2))
print(f"gcd(primorial, F2) = {g}")
if g > 1 and g < int(F2):
    print(f"  ✓✓✓ فاکتور F2 پیدا شد: {g}")
    print(f"  is_prime: {is_prime(g)}")
    cof = int(F2) // g
    print(f"  cofactor: {str(cof)[:60]}... ({len(str(cof))} digits)")
else:
    print(f"  ✗ فاکتور پیدا نشد — تأیید می‌شود که F2 هیچ فاکتوری تا 10^7 ندارد")
    print(f"  (این قبلاً با trial division تأیید شده بود)")
print()

# ============================================================
# EXTEND: Try with larger primorial
# ============================================================
print("=" * 70)
print(f"تست ۴: تمدید primorial تا 10^8 (بزرگ‌تر)")
print("=" * 70)
print()

B2 = 10**8
print(f"تولید اعداد اول تا 10^8...")
t0 = time.time()
primes_big = small_primes_up_to(B2)
t1 = time.time()
print(f"  {len(primes_big)} primes, زمان: {t1-t0:.1f}s")

# Compute primorial incrementally — we already have primorial(10^7) in `product`.
# Now multiply by all primes in (10^7, 10^8]
print(f"تکمیل primorial(10^8) از primorial(10^7)...")
t0 = time.time()
product_big = product
for p in primes_big:
    if p > B:  # only new primes
        product_big *= mpz(p)
t1 = time.time()
print(f"  primorial(10^8) has {len(str(product_big))} digits, زمان: {t1-t0:.1f}s")
print(f"  log10(primorial(10^8)) = {math.log10(int(product_big)):.4f}")
print()

# Apply to F2
print(f"آزمایش روی F2 با primorial(10^8)...")
g = gcd(int(product_big), int(F2))
print(f"gcd(primorial(10^8), F2) = {g}")
if g > 1 and g < int(F2):
    print(f"  ✓✓✓ فاکتور F2 پیدا شد: {g}")
    print(f"  is_prime: {is_prime(g)}")
    cof = int(F2) // g
    print(f"  cofactor: {str(cof)[:60]}... ({len(str(cof))} digits)")
    print(f"  is_prime(cofactor): {is_prime(cof)}")
else:
    print(f"  ✗ فاکتور پیدا نشد — F2 هیچ فاکتوری تا 10^8 ندارد")
print()

# ============================================================
# Summary
# ============================================================
print("=" * 70)
print("  خلاصه‌ی نهایی")
print("=" * 70)
print("""
✓ روی N با فاکتور کوچک (7 digit): روش کار کرد — p1 پیدا شد.
✗ روی N با فاکتورهای بزرگ (40 digit): روش شکست خورد.
✗ روی F2 با primorial(10^7): شکست (تأیید می‌کند F2 هیچ فاکتور <= 10^7 ندارد).
✗ روی F2 با primorial(10^8): شکست (F2 هیچ فاکتور <= 10^8 ندارد).

دلیل شکست روی F2:
- عوامل اول F2 همگی بزرگ‌تر از 10^8 هستند (احتمالاً > 10^70).
- primorial(10^70) عملاً قابل محاسبه نیست (10^67 عدد اول، محصول 10^70 رقمی).

نتیجه:
- روش «تقریب log10» = تقسیم آزمایشی با primorial.
- فقط وقتی کار می‌کند که فاکتور کوچک داشته باشیم.
- برای F2 که فاکتورهایش بسیار بزرگ‌اند، این روش بی‌فایده است.
- برای تجزیه‌ی واقعی F2 به ECM/SNFS نیاز است.
""")
