#!/usr/bin/env python3
"""
تحلیل کامل M(1237) = 2^1237 - 1
- بررسی اول/مرکب بودن دو فاکتور
- محاسبه تعداد ارقام
- Trial Division با اعداد اول شناخته‌شده
- استفاده از شرط Mersenne: q = 2*k*p + 1
- اعمال P-1 و ECM برای پیدا کردن فاکتورهای فاکتور مرکب
- ارائه نتایج از بزرگ‌ترین به کوچک‌ترین
"""

import sys
import time
import math

import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod
gmpy2.get_context().precision = 1000

P = 1237
M = mpz(2)**P - 1

FACTOR1_STR = "2538207129840687799335203259492870476186248896616401346500027311795983"
FACTOR2_STR = "932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281199369604215535391846857906233364905825622441048803673998858526737"

F1 = mpz(FACTOR1_STR)
F2 = mpz(FACTOR2_STR)


def digits(n):
    return len(str(n))


def fmt(n, w=80):
    s = str(n)
    if len(s) <= w:
        return s
    return s[:w] + "...(" + str(len(s) - w) + " char more)"


print("=" * 78)
print(f"  M({P}) = 2^{P} - 1   —   تعداد ارقام: {digits(M)}")
print("=" * 78)
print()

# ============================================================
#  مرحله ۱: بررسی صحت فاکتوریزاسیون
# ============================================================
print("[مرحله ۱] بررسی صحت فاکتورها")
print("-" * 78)
assert F1 * F2 == M, "فاکتوریزاسیون نادرست!"
print(f"  فاکتور ۱ (F1): {digits(F1)} رقم")
print(f"  فاکتور ۲ (F2): {digits(F2)} رقم")
print(f"  F1 × F2 == M({P}) ✓")
print()

# ============================================================
#  مرحله ۲: تست اول بودن قطعی
# ============================================================
print("[مرحله ۲] تست اول بودن با gmpy2 (BPSW + probabilistic)")
print("-" * 78)
t0 = time.time()
f1_prime = bool(is_prime(F1))
t1 = time.time()
f2_prime = bool(is_prime(F2))
t2 = time.time()
print(f"  F1 (70 رقم):  is_prime = {f1_prime}   ({t1-t0:.3f}s)  -> {'اول ✓' if f1_prime else 'مرکب ✗'}")
print(f"  F2 (303 رقم): is_prime = {f2_prime}   ({t2-t1:.3f}s)  -> {'اول ✓' if f2_prime else 'مرکب ✗'}")
print()

# ============================================================
#  مرحله ۳: بررسی شرط Mersenne (q = 2*k*p + 1)
# ============================================================
print("[مرحله ۳] بررسی شرط Mersenne: هر فاکتور اول q باید q = 2·k·p + 1 باشد")
print("-" * 78)
for name, F in [("F1", F1), ("F2", F2)]:
    r = (F - 1) % (2 * P)
    k = (F - 1) // (2 * P)
    mod8 = int(F % 8)
    print(f"  {name}: (F-1) mod (2·{P}) = {r}")
    print(f"     {name} ≡ {mod8} (mod 8)  — باید 1 یا 7 باشد ({'✓' if mod8 in (1,7) else '✗'})")
    if r == 0:
        print(f"     k = (F-1)/(2·{P}) = یک عدد {digits(k)} رقمی")
print()

# ============================================================
#  مرحله ۴: Trial Division فاکتور ۲
# ============================================================
print("[مرحله ۴] Trial Division فاکتور ۲ بر اعداد اول کوچک (تا 10⁷)")
print("-" * 78)

# تولید اعداد اول کوچک با sieve
def sieve_primes(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    return [i for i in range(2, limit + 1) if sieve[i]]

t0 = time.time()
limit = 10**7
primes = sieve_primes(limit)
t_sieve = time.time() - t0
print(f"  تعداد اعداد اول تا {limit}: {len(primes):,}  (ساخت غربال: {t_sieve:.1f}s)")

t0 = time.time()
small_factors = []
remaining = F2
for p in primes:
    if remaining % p == 0:
        small_factors.append(p)
        while remaining % p == 0:
            remaining //= p
    if remaining == 1:
        break
elapsed = time.time() - t0
print(f"  زمان تقسیم: {elapsed:.1f}s")
print(f"  فاکتورهای کوچک پیدا شده: {len(small_factors)}")
if small_factors:
    for f in small_factors:
        print(f"    • {f}")
else:
    print(f"    (هیچ فاکتور اولی کمتر از 10⁷ برای F2 وجود ندارد)")
print(f"  باقی‌مانده F2 پس از این مرحله: {digits(remaining)} رقم")
print()

# ============================================================
#  مرحله ۵: Trial Division مخصوص Mersenne (q = 2·p·k + 1)
# ============================================================
print("[مرحله ۵] Trial Division فقط اعداد به فرم 2·1237·k + 1 (تا k = 10⁹)")
print("-" * 78)

t0 = time.time()
kmax = 10**9
found_mersenne = []
checked_primes = 0
checked_candidates = 0
last_progress = 0

# فقط k هایی که q = 2*p*k+1 ≡ 1 یا 7 (mod 8)
# 2*1237 = 2474
# q = 2474*k + 1
# q mod 8 = (2474*k + 1) mod 8 = (2*k + 1) mod 8
# 2*k+1 ≡ 1 (mod 8) => 2k ≡ 0 (mod 8) => k ≡ 0 (mod 4)
# 2*k+1 ≡ 7 (mod 8) => 2k ≡ 6 (mod 8) => k ≡ 3 (mod 4)
# پس k باید 0 یا 3 (mod 4) باشد

for k in range(1, kmax + 1):
    if k % 4 != 0 and k % 4 != 3:
        continue
    q = 2 * P * k + 1
    if q * q > remaining:
        print(f"  [توقف] به sqrt(F2) رسیدیم در k={k:,}")
        break
    checked_candidates += 1
    # تست Miller-Rabin سریع
    if is_prime(q):
        checked_primes += 1
        if remaining % q == 0:
            found_mersenne.append((k, int(q)))
            print(f"  [FOUND] فاکتور! k={k:,}, q={q}")
            while remaining % q == 0:
                remaining //= q
            if is_prime(remaining):
                print(f"  [باقی‌مانده اول است] {digits(remaining)} رقم")
                found_mersenne.append((None, int(remaining)))
                remaining = mpz(1)
                break
        if checked_primes % 100000 == 0 and checked_primes > last_progress:
            print(f"  ... پیشرفت: {checked_primes:,} عدد اول بررسی شده، k={k:,}")
            last_progress = checked_primes
    if k % 10_000_000 == 0:
        print(f"  ... k = {k:,}")

elapsed = time.time() - t0
print(f"  زمان: {elapsed:.1f}s")
print(f"  کاندیداهای بررسی شده: {checked_candidates:,}")
print(f"  اعداد اول بررسی شده: {checked_primes:,}")
print(f"  فاکتورهای پیدا شده: {len(found_mersenne)}")
if found_mersenne:
    for k, q in found_mersenne:
        if k is None:
            print(f"    • باقی‌مانده اول: {digits(q)} رقم")
        else:
            print(f"    • k={k}, q={q} ({digits(q)} رقم)")
print(f"  باقی‌مانده F2: {digits(remaining)} رقم")
print()

# ============================================================
#  مرحله ۶: P-1 روش برای پیدا کردن فاکتور بزرگ
# ============================================================
if remaining > 1 and not is_prime(remaining):
    print("[مرحله ۶] P-1 روش (Stage 1 با B1=1M, Stage 2 با B2=10M)")
    print("-" * 78)
    
    def pm1_stage1(n, B1):
        """Stage 1 P-1: محاسبه a^M mod n که M = lcm(1..B1)"""
        # تولید توان‌های اول
        a = mpz(2)
        # محاسبه a^(q^e) برای هر توان اول q^e <= B1
        primes_b1 = sieve_primes(B1)
        for p in primes_b1:
            e = 1
            pe = p
            while pe * p <= B1:
                pe *= p
                e += 1
            a = powmod(a, pe, n)
        g = gcd(a - 1, n)
        return g
    
    B1 = 1_000_000
    t0 = time.time()
    print(f"  اجرای Stage 1 با B1 = {B1:,}...")
    g = pm1_stage1(int(remaining), B1)
    elapsed = time.time() - t0
    print(f"  زمان Stage 1: {elapsed:.1f}s")
    print(f"  gcd = {g}")
    if g != 1 and g != remaining:
        print(f"  [FOUND] فاکتور پیدا شد! {g} ({digits(g)} رقم)")
        print(f"  بررسی اول بودن: {is_prime(g)}")
        found_mersenne.append(('P-1', int(g)))
        remaining //= g
        print(f"  باقی‌مانده: {digits(remaining)} رقم")
        if is_prime(remaining):
            print(f"  باقی‌مانده اول است ✓")
            found_mersenne.append(('cofactor', int(remaining)))
            remaining = mpz(1)
    else:
        print(f"  فاکتوری در Stage 1 پیدا نشد (g={g})")
    print()

# ============================================================
#  مرحله ۷: ECM (اگر sympy موجود باشد)
# ============================================================
if remaining > 1 and not is_prime(remaining):
    print("[مرحله ۷] ECM (Elliptic Curve Method)")
    print("-" * 78)
    try:
        from sympy.ntheory import ecm as sympy_ecm
        t0 = time.time()
        print(f"  اجرای ECM روی باقی‌مانده ({digits(remaining)} رقم)...")
        # محدودیت زمانی
        ecm_factors = []
        try:
            for f in sympy_ecm(int(remaining), B1=10000, B2=100000, max_curve=50):
                ecm_factors.append(f)
                print(f"  [FOUND] {f}")
        except Exception as e:
            print(f"  ECM خطا: {e}")
        elapsed = time.time() - t0
        print(f"  زمان ECM: {elapsed:.1f}s")
        print(f"  فاکتورهای پیدا شده: {len(ecm_factors)}")
        for f in ecm_factors:
            print(f"    • {f} ({digits(mpz(f))} رقم)")
            found_mersenne.append(('ECM', f))
    except ImportError:
        print("  sympy.ntheory.ecm موجود نیست")

# ============================================================
#  خلاصه نهایی
# ============================================================
print()
print("=" * 78)
print("  خلاصه نهایی تحلیل M(1237) = 2^1237 - 1")
print("=" * 78)
print()
print(f"M({P}) = 2^{P} - 1")
print(f"تعداد ارقام M({P}): {digits(M)}")
print()
print(f"فاکتور ۱ (F1):")
print(f"  مقدار:      {FACTOR1_STR}")
print(f"  ارقام:      {digits(F1)}")
print(f"  نوع:        {'عدد اول ✓' if f1_prime else 'عدد مرکب ✗'}")
print()
print(f"فاکتور ۲ (F2):")
print(f"  مقدار:      {FACTOR2_STR[:80]}...")
print(f"  ارقام:      {digits(F2)}")
print(f"  نوع:        {'عدد اول ✓' if f2_prime else 'عدد مرکب ✗ (تأیید شد!)'}")
print()

if found_mersenne:
    print("=" * 78)
    print("  فاکتورهای پیدا شده برای F2 (از بزرگ‌ترین به کوچک‌ترین):")
    print("=" * 78)
    sorted_factors = sorted([(int(q) if isinstance(q, int) else int(q)) for _, q in found_mersenne], reverse=True)
    for i, q in enumerate(sorted_factors, 1):
        print(f"  {i}. {q}")
        print(f"     ارقام: {digits(mpz(q))}, اول: {is_prime(mpz(q))}")
    print()
    print(f"  باقی‌مانده نهایی: {digits(remaining)} رقم")
    if remaining > 1:
        print(f"  مقدار: {str(remaining)[:80]}...")
        print(f"  اول: {is_prime(remaining)}")
else:
    print("  هیچ فاکتور اولی برای F2 در محدوده جستجو پیدا نشد.")
    print(f"  F2 همچنان مرکب است با {digits(remaining)} رقم.")
    print(f"  (محدوده جستجو: اعداد اول تا 10⁷، و اعداد به فرم 2·1237·k+1 تا k=10⁹)")
print()

# ذخیره نتایج در فایل
with open('/home/z/my-project/download/M1237_analysis_results.txt', 'w', encoding='utf-8') as out:
    out.write("=" * 78 + "\n")
    out.write(f"  تحلیل کامل فاکتوریزاسیون M({P}) = 2^{P} - 1\n")
    out.write("=" * 78 + "\n\n")
    out.write(f"M({P}) = 2^{P} - 1\n")
    out.write(f"تعداد ارقام M({P}): {digits(M)}\n\n")
    
    out.write("فاکتور ۱ (F1):\n")
    out.write(f"  مقدار: {FACTOR1_STR}\n")
    out.write(f"  ارقام: {digits(F1)}\n")
    out.write(f"  نوع: {'عدد اول' if f1_prime else 'عدد مرکب'}\n\n")
    
    out.write("فاکتور ۲ (F2):\n")
    out.write(f"  مقدار: {FACTOR2_STR}\n")
    out.write(f"  ارقام: {digits(F2)}\n")
    out.write(f"  نوع: {'عدد اول' if f2_prime else 'عدد مرکب'}\n\n")
    
    if found_mersenne:
        out.write("فاکتورهای پیدا شده برای F2 (از بزرگ‌ترین به کوچک‌ترین):\n")
        sorted_factors = sorted([(int(q) if isinstance(q, int) else int(q)) for _, q in found_mersenne], reverse=True)
        for i, q in enumerate(sorted_factors, 1):
            out.write(f"  {i}. {q}\n")
            out.write(f"     ارقام: {digits(mpz(q))}, اول: {is_prime(mpz(q))}\n")
        out.write(f"\nباقی‌مانده نهایی: {digits(remaining)} رقم\n")
        if remaining > 1:
            out.write(f"  مقدار: {str(remaining)}\n")
            out.write(f"  اول: {is_prime(remaining)}\n")
    else:
        out.write("هیچ فاکتور اولی برای F2 در محدوده جستجو پیدا نشد.\n")
        out.write(f"F2 همچنان مرکب است با {digits(remaining)} رقم.\n")

print("نتایج در download/M1237_analysis_results.txt ذخیره شد")
