#!/usr/bin/env python3
"""
Test the log10-approximation factorization technique on a KNOWN composite number.

Setup:
- Generate N = p1 * p2 * p3 where each pi is a known prime with specific digit count.
- Now pretend we don't know the factorization.
- Try the "log10 trick":
  - Generate random primes qi with log10 sum ≈ log10(N)
  - Test gcd(qi, N) — does any qi happen to divide N?

Expected outcome:
- With random 80-digit primes, probability that any of them equals one of the
  factors of N is essentially zero (even though log10 sums match).
- So the trick won't work — confirming our analysis.

But let's try with more "structured" primes to demonstrate this.

ALSO: Try the "right" version of the trick:
- If we have a number c that's KNOWN to be a product of two primes of similar size,
  AND we know the rough size, can we generate primes near sqrt(c) and try them?
  - Yes! This is "trial division with size hint" — works if factor is in known size range.
  - For M(1237)/F1, we don't know the size range of factors, so this doesn't apply.

Let's run BOTH experiments to demonstrate the principle.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, next_prime, gcd
import math
import time
import random
from pathlib import Path

# ============================================================
# EXPERIMENT 1: Naive log10-trick on a known composite
# ============================================================
print("=" * 70)
print("  تجربه ۱: روش «تقریب log10» روی یک عدد مرکب شناخته‌شده")
print("=" * 70)
print()

# Generate a known composite: N = p1 * p2 (both 30-digit primes)
random.seed(123)
def random_prime_with_digits(d):
    low = 10**(d-1)
    high = 10**d - 1
    while True:
        n = random.randint(low, high)
        if n % 2 == 0: n += 1
        p = int(next_prime(mpz(n)))
        if p <= high: return p

p1 = random_prime_with_digits(30)
p2 = random_prime_with_digits(30)
N = p1 * p2
print(f"تولید عدد مرکب شناخته‌شده:")
print(f"  p1 = {p1} ({len(str(p1))} digits, prime: {is_prime(p1)})")
print(f"  p2 = {p2} ({len(str(p2))} digits, prime: {is_prime(p2)})")
print(f"  N = p1 × p2 = {N}")
print(f"  N has {len(str(N))} digits")
print(f"  log10(N) = {math.log10(N):.10f}")
print()

# Now pretend we don't know p1, p2. Try log10-trick:
# Generate random primes with log10 sum ≈ log10(N).
# Since log10(N) ≈ 60, we need primes whose log10 sum to 60.
# Try: 1 random 60-digit prime, or 2 30-digit primes (like the real factors!), or 6 10-digit primes.

print("=" * 70)
print("  روش ۱: تولید ۱ عدد اول ۶۰ رقمی (log10 ≈ 60) و gcd با N")
print("=" * 70)

log10_N = math.log10(N)
print(f"هدف: log10(N) = {log10_N:.10f}")
print()

# Try 1000 random 60-digit primes and check gcd
print(f"آزمایش ۱۰۰۰ عدد اول ۶۰ رقمی تصادفی...")
t0 = time.time()
found_count = 0
for trial in range(1000):
    q = random_prime_with_digits(60)
    g = gcd(q, N)
    if g > 1:
        print(f"  >>> trial {trial+1}: gcd(q, N) = {g} — فاکتور پیدا شد!")
        found_count += 1
        break
t1 = time.time()
print(f"  زمان: {t1-t0:.1f}s")
print(f"  فاکتور پیدا شده: {found_count}")
print(f"  احتمال تئوری: ۱۰۰۰ / ۱۰⁵۸ ≈ ۱۰⁻⁵⁵ (عملاً صفر)")
print()

# ============================================================
# METHOD 2: Use 2 30-digit primes (matching actual structure)
# ============================================================
print("=" * 70)
print("  روش ۲: تولید ۲ عدد اول ۳۰ رقمی (مانند ساختار واقعی N)")
print("=" * 70)
print()

print(f"آزمایش ۱۰۰۰ جفت عدد اول ۳۰ رقمی تصادفی...")
t0 = time.time()
found_count = 0
for trial in range(1000):
    q1 = random_prime_with_digits(30)
    g = gcd(q1, N)
    if g > 1:
        print(f"  >>> trial {trial+1}: gcd(q1, N) = {g} — فاکتور پیدا شد!")
        found_count += 1
        if g == p1:
            print(f"      (این p1 است!)")
        elif g == p2:
            print(f"      (این p2 است!)")
        break
t1 = time.time()
print(f"  زمان: {t1-t0:.1f}s")
print(f"  فاکتور پیدا شده: {found_count}")
print(f"  احتمال تئوری: ۱۰۰۰ × ۲ / ۱۰²⁸ ≈ ۱۰⁻۲۵ (باز هم عملاً صفر)")
print()

# ============================================================
# METHOD 3: Trial division in the right range
# ============================================================
print("=" * 70)
print("  روش ۳: تقسیم آزمایشی در محدوده‌ی صحیح")
print("=" * 70)
print()

# Now use the "size hint" — we know (assume) the factors are 30-digit.
# Pick primes near sqrt(N) and test sequentially.
# This is essentially "trial division near sqrt" — but for N = p1*p2 with both 30-digit,
# this would take ~10^30 / log(10^30) attempts in worst case = 10^28 attempts.
# Too slow.

# Better: pick 1000 primes from a small "search range" near sqrt(N) where we know one of them is a factor.
# But this is cheating — let's pick from a RANDOM small range of 1000 consecutive primes near sqrt(N).
sqrt_N = int(math.isqrt(N))
print(f"sqrt(N) = {str(sqrt_N)[:30]}... ({len(str(sqrt_N))} digits)")

# Find prime near sqrt(N)
print(f"  یافتن عدد اول نزدیک sqrt(N)...")
q = int(next_prime(mpz(sqrt_N)))
print(f"  اولین عدد اول بزرگ‌تر از sqrt(N): {q}")
print()

# Now scan 1000 primes starting from q, check each
print(f"  آزمایش ۱۰۰۰ عدد اول متوالی شروع از sqrt(N)...")
t0 = time.time()
found_count = 0
trial = 0
cur = q
while trial < 1000:
    if N % cur == 0:
        print(f"  >>> trial {trial+1}: {cur} | N  ✓✓✓ فاکتور پیدا شد!")
        found_count += 1
        cof = N // cur
        print(f"      cofactor = {cof}")
        print(f"      is_prime(cofactor): {is_prime(cof)}")
        break
    cur = int(next_prime(mpz(cur + 1)))
    trial += 1
t1 = time.time()
print(f"  زمان: {t1-t0:.3f}s, trials: {trial+1}")
if found_count == 0:
    print(f"  ✗ فاکتور پیدا نشد (طبیعی — چون p1, p2 تصادفی هستند، نزدیک sqrt(N) نیستند لزوماً)")
print()

# ============================================================
# EXPERIMENT 2: A "lucky" case where the log10 trick MIGHT work
# ============================================================
print("=" * 70)
print("  تجربه ۲: یک حالت شانس‌آور که در آن روش ممکن است کار کند")
print("=" * 70)
print()

# Setup: choose a prime p_target with d digits. Compute N = p_target * q (q another prime).
# Generate a list of d-digit primes and check if any of them equals p_target.
# This shows that "if you happen to generate the same prime", the trick works.
# Otherwise it doesn't.

p_target = random_prime_with_digits(20)
q_other = random_prime_with_digits(20)
N2 = p_target * q_other
print(f"تولید N2 با عامل مشخص p_target:")
print(f"  p_target = {p_target} (20 digits)")
print(f"  q_other  = {q_other} (20 digits)")
print(f"  N2 = {N2} ({len(str(N2))} digits)")
print()

# Now try generating 100 random 20-digit primes — could one of them equal p_target?
print(f"آزمایش: ۱۰۰ عدد اول ۲۰ رقمی تصادفی، آیا یکی برابر p_target است؟")
t0 = time.time()
match_count = 0
for trial in range(100):
    q = random_prime_with_digits(20)
    if q == p_target or q == q_other:
        print(f"  >>> trial {trial+1}: {q} برابر یکی از فاکتورها!")
        match_count += 1
        break
    g = gcd(q, N2)
    if g > 1:
        print(f"  >>> trial {trial+1}: gcd({q}, N2) = {g}")
        match_count += 1
        break
t1 = time.time()
print(f"  زمان: {t1-t0:.2f}s")
print(f"  تعداد تطابق: {match_count}")
print(f"  احتمال تئوری: ۱۰۰ × ۲ / (۱۰²⁰ / ln(10²⁰)) ≈ ۱۰۰ × ۲ / ۲.۲×10¹⁸ ≈ 10⁻¹⁶")
print()

# ============================================================
# Summary - the principle
# ============================================================
print("=" * 70)
print("  نتیجه‌گیری اصل")
print("=" * 70)
print("""
روش «تقریب log10» برای تجزیه‌ی عدد مرکب c303 (مثل F2) به این دلیل کار نمی‌کند:

۱. فضای اعداد اول با d رقم بسیار بزرگ است:
   - تعداد اعداد اول 80 رقمی ≈ 10^80 / ln(10^80) ≈ 5.4 × 10^77
   - تعداد اعداد اول 30 رقمی ≈ 10^30 / ln(10^30) ≈ 1.4 × 10^28

۲. تعداد اعدادی که «log10 جمعشان» به هدف نزدیک است نیز بسیار زیاد است.
   - ترکیب‌های 4 عدد اول 80 رقمی: (10^77)^4 = 10^308 حالت.
   - فقط بخش کوچکی از این‌ها جمع log10 نزدیک 303 دارند.

۳. برای تجزیه‌ی واقعی، لازم است که حداقل یکی از اعداد تولیدشده
   دقیقاً برابر با یکی از فاکتورهای اول c303 باشد.
   - تعداد فاکتورهای اول c303: فرض کنیم 2-3 عدد.
   - احتمال تطابق تصادفی: 3 / 10^77 ≈ 10^-77 (عملاً صفر).

۴. در تجربه‌های بالا، حتی با 1000 تلاش روی عدد مرکب 60 رقمی (که
   فقط دو فاکتور 30 رقمی دارد)، هیچ تطابقی پیدا نشد.

۵. تنها راه که این روش «می‌توانست» کار کند:
   - اگر فاکتورهای c303 تعداد بسیار زیادی داشته باشند (مثلاً 10^20 فاکتور)
     و همه‌ی آن‌ها در یک محدوده‌ی کوچک از اعداد اول باشند.
   - اما این برخلاف ساختار اعداد Mersenne است: آنها معمولاً تعداد کمی
     فاکتور اول بزرگ دارند.

نتیجه: روش «ماشین حسابی log10» در حالت کلی غیرقابل اجرا است.
روش‌های واقعی تجزیه (ECM، SNFS) از ساختار گروهی و جبری استفاده
می‌کنند، نه فقط تقریب عددی.
""")

# ============================================================
# Final: Demonstrate ECM working on the smaller test case
# ============================================================
print("=" * 70)
print("  نمایش: ECM واقعی روی N = p1 × p2 (60 digits)")
print("=" * 70)
print()

# Simple P-1 (since one of p1-1, p2-1 might be smooth)
def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

print(f"اجرای P-1 با B1 = 10^6 روی N...")
t0 = time.time()
B1 = 10**6
primes = small_primes_up_to(B1)
val = mpz(2)
for p in primes:
    pe = p
    while pe * p <= B1:
        pe *= p
    val = powmod(val, pe, N) if 'powmod' in dir() else pow(int(val), pe, N)
g = gcd(int(val) - 1, N)
t1 = time.time()
print(f"  زمان: {t1-t0:.2f}s")
if 1 < g < N:
    print(f"  ✓ P-1 FOUND FACTOR: {g}")
    print(f"  is_prime: {is_prime(g)}")
    cof = N // g
    print(f"  cofactor = {cof}, is_prime: {is_prime(cof)}")
else:
    print(f"  ✗ P-1 با B1 = 10^6 فاکتور پیدا نکرد")
    print(f"  (یعنی نه p1-1 و نه p2-1، 10^6-smooth نیستند)")
