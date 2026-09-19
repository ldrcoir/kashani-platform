#!/usr/bin/env python3
"""
Final test: log10 trick that ACTUALLY works on a known composite.

The CORRECT way to make the log10 trick work:
- Use ALL primes up to a bound B (not greedy asc which stops early).
- The product of ALL primes ≤ B is the "primorial" of B.
- gcd(primorial(B), N) gives all factors of N that are ≤ B.

This is just trial division, expressed as primorial.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, next_prime, gcd
import math
import time
import random

print("=" * 70)
print("  تست نهایی: تکنیک log10 که واقعاً کار می‌کند")
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

def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

# ============================================================
# Case 1: ASYMMETRIC — small factor × large factor
# ============================================================
print("=== حالت ۱: 7-digit × 40-digit ===")
p1 = random_prime_with_digits(7)
p2 = random_prime_with_digits(40)
N1 = p1 * p2
log10_N1 = math.log10(N1)
print(f"p1 = {p1} (7 digits, small)")
print(f"p2 = {p2} (40 digits, large)")
print(f"N1 = p1 × p2 ({len(str(N1))} digits)")
print(f"log10(N1) = {log10_N1:.6f}")
print()

# Method 1: Greedy ascending — stops before reaching p1
print("روش ۱: حریصانه صعودی (همان روش قبلی)")
primes_pool = small_primes_up_to(10**7)
selected = []
sum_log = 0.0
for p in primes_pool:
    lp = math.log10(p)
    if sum_log + lp <= log10_N1 + 1e-9:
        selected.append(p)
        sum_log += lp
print(f"  تعداد: {len(selected)}, آخرین: {selected[-1]}, جمع log10: {sum_log:.4f}")
print(f"  p1 = {p1} در selected؟ {p1 in selected}")
product = mpz(1)
for p in selected:
    product *= mpz(p)
g = gcd(int(product), int(N1))
print(f"  gcd = {g}  {'✓ فاکتور' if 1 < g < N1 else '✗ شکست'}")
print()

# Method 2: Use ALL primes up to where greedy stops + a bit more
# Actually the right way: include ALL primes up to bound, not greedy.
# Let's include ALL primes up to 10^7 (full primorial), not greedy.
print("روش ۲: primorial کامل (همه‌ی اعداد اول تا 10^7)")
# Don't compute primorial(10^7) directly — too big. Use incremental gcd.
# Compute gcd(N1, p) for each prime p in primes_pool.
# If any p divides N1, we have a factor.
t0 = time.time()
factor_found = None
for p in primes_pool:
    if N1 % p == 0:
        factor_found = p
        break
t1 = time.time()
if factor_found:
    print(f"  ✓✓✓ فاکتور پیدا شد: {factor_found} (در زمان {t1-t0:.2f}s)")
    print(f"  is_prime: {is_prime(factor_found)}")
    cof = N1 // factor_found
    print(f"  cofactor = {cof}")
    print(f"  is_prime(cofactor): {is_prime(cof)}")
    print(f"  تجزیه کامل: N1 = {factor_found} × {cof}")
else:
    print(f"  ✗ فاکتور پیدا نشد")
print()

# ============================================================
# Case 2: SYMMETRIC — 30-digit × 30-digit
# ============================================================
print("=== حالت ۲: 30-digit × 30-digit (مانند وضعیت F2) ===")
p1 = random_prime_with_digits(30)
p2 = random_prime_with_digits(30)
N2 = p1 * p2
log10_N2 = math.log10(N2)
print(f"p1 = {p1} (30 digits)")
print(f"p2 = {p2} (30 digits)")
print(f"N2 = p1 × p2 ({len(str(N2))} digits)")
print(f"log10(N2) = {log10_N2:.6f}")
print()

print("روش ۲: primorial(10^7) کامل")
t0 = time.time()
factor_found = None
for p in primes_pool:
    if N2 % p == 0:
        factor_found = p
        break
t1 = time.time()
if factor_found:
    print(f"  ✓ فاکتور: {factor_found} (در زمان {t1-t0:.2f}s)")
else:
    print(f"  ✗ فاکتور پیدا نشد (در زمان {t1-t0:.2f}s)")
    print(f"  دلیل: p1 و p2 هر دو > 10^7 هستند، پس در primorial(10^7) نیستند")
    print(f"  این دقیقاً همان وضعیت F2 است!")
print()

# ============================================================
# Case 3: Three primes, one small
# ============================================================
print("=== حالت ۳: 5-digit × 15-digit × 25-digit ===")
p1 = random_prime_with_digits(5)
p2 = random_prime_with_digits(15)
p3 = random_prime_with_digits(25)
N3 = p1 * p2 * p3
log10_N3 = math.log10(N3)
print(f"p1 = {p1} (5 digits)")
print(f"p2 = {p2} (15 digits)")
print(f"p3 = {p3} (25 digits)")
print(f"N3 = p1 × p2 × p3 ({len(str(N3))} digits)")
print(f"log10(N3) = {log10_N3:.6f}")
print()

print("روش ۲: primorial(10^7) کامل")
t0 = time.time()
factor_found = None
for p in primes_pool:
    if N3 % p == 0:
        factor_found = p
        break
t1 = time.time()
if factor_found:
    print(f"  ✓✓✓ فاکتور پیدا شد: {factor_found} (در زمان {t1-t0:.2f}s)")
    print(f"  is_prime: {is_prime(factor_found)}")
    cof = N3 // factor_found
    print(f"  cofactor = {cof} ({len(str(cof))} digits)")
    print(f"  is_prime(cofactor): {is_prime(cof)}")
    # Check if cofactor itself factors further (might have p2 or p3 as factor)
    # Note: primorial(10^7) covers all primes up to 10^7, including p2 if p2 is 15-digit (which is < 10^7)
    # p2 is 15-digit, so p2 < 10^15, but not necessarily < 10^7.
    # Let's test if cofactor has p2 as factor:
    if cof % p2 == 0:
        print(f"  ✓ cofactor also has p2 = {p2} as factor!")
        cof2 = cof // p2
        if cof2 == p3:
            print(f"  ✓✓✓ تجزیه کامل: N3 = p1 × p2 × p3 = {p1} × {p2} × {p3}")
else:
    print(f"  ✗ فاکتور پیدا نشد")
print()

# ============================================================
# Case 4: Even smaller factor (3-digit)
# ============================================================
print("=== حالت ۴: 3-digit × 50-digit (عامل خیلی کوچک) ===")
p1 = random_prime_with_digits(3)
p2 = random_prime_with_digits(50)
N4 = p1 * p2
log10_N4 = math.log10(N4)
print(f"p1 = {p1} (3 digits)")
print(f"p2 = {p2} (50 digits)")
print(f"N4 = p1 × p2 ({len(str(N4))} digits)")
print(f"log10(N4) = {log10_N4:.6f}")
print()

print("روش ۲: primorial(10^7) کامل")
t0 = time.time()
factor_found = None
for p in primes_pool:
    if N4 % p == 0:
        factor_found = p
        break
t1 = time.time()
if factor_found:
    print(f"  ✓✓✓ فاکتور پیدا شد: {factor_found} (در زمان {t1-t0:.4f}s)")
    cof = N4 // factor_found
    print(f"  cofactor = {cof}")
    print(f"  is_prime(cofactor): {is_prime(cof)}")
    print(f"  تجزیه کامل: N4 = {factor_found} × {cof}")
else:
    print(f"  ✗ فاکتور پیدا نشد")
print()

# ============================================================
# Summary
# ============================================================
print("=" * 70)
print("  جمع‌بندی نهایی")
print("=" * 70)
print("""
تکنیک «log10 trick» در واقع فقط همان «تقسیم آزمایشی» است.

نتایج:
✓ حالت ۱ (7-digit × 40-digit):     فاکتور پیدا شد (p1 چون < 10^7 بود)
✗ حالت ۲ (30-digit × 30-digit):    شکست (هیچ فاکتور < 10^7 نبود)
✓ حالت ۳ (5-digit × 15-digit × 25-digit): فاکتور پیدا شد (p1 چون < 10^7 بود)
✓ حالت ۴ (3-digit × 50-digit):     فاکتور پیدا شد (p1 چون < 10^7 بود)

نکته کلیدی:
- تکنیک log10 وقتی کار می‌کند که کوچک‌ترین فاکتور N در محدوده‌ی
  تولید اعداد اول ما (یعنی ≤ B که B حدود 10^7 است) باشد.
- برای F2 که کوچک‌ترین فاکتور آن > 10^8 (احتمالاً > 10^50) است،
  این تکنیک نمی‌تواند فاکتور پیدا کند.

نتیجه‌ی قطعی برای F2:
- تکنیک log10 برای F2 بی‌فایده است (تأیید شد).
- برای تجزیه‌ی F2 به ECM/SNFS نیاز است.

جمله‌ی نهایی:
«تکنیک log10 فقط یک تقسیم آزمایشی است که با واژه‌های متفاوت بیان شده.»
""")
