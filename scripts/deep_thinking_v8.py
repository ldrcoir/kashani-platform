#!/usr/bin/env python3
"""
تفکر عمیق: روش‌های ابتکاری برای کاهش زمان فاکتوریزاسیون
=====================================================

مسئله: F2 (303 رقم) فاکتور نشده
ECM: 1000+ سال با 2 CPU
NFS: 50,000+ سال

ایده‌های ابتکاری:
۱. استفاده از ساختار خاص F2 (مرسن)
۲. ترکیب روش‌های موجود به‌صورت هوشمند
۳. استفاده از الگوهای فاکتورهای شناخته‌شده
۴. روش‌های مبتنی بر یادگیری ماشین
۵. استفاده از quantum-inspired algorithms
۶. روش ترکیبی ECM + P-1 + ساختار
"""

import gmpy2
from gmpy2 import mpz, is_prime, gcd, isqrt, iroot, powmod, next_prime
import numpy as np
import time
import os
import json

# ============================================================
#  داده‌ها
# ============================================================
P = 1237
M_1237 = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M_1237 // F1

# فاکتورهای شناخته‌شده از F1 - 1
X1 = mpz("110421384041193593117465987")
X2 = mpz("442440509040507330087115446251753610709")

# F2 - 1 = 2^4 × 3 × 7 × 1237 × Z
Z = (F2 - 1) // (2**4 * 3 * 7 * 1237)

# ============================================================
#  روش ۱: ECM هدایت‌شده با ساختار (Guided ECM)
# ============================================================
def guided_ecm_idea():
    """
    ایده: به‌جای منحنی‌های تصادفی، منحنی‌های با torsion خاص
    
    اگر فاکتور q از F2 به فرم q = 2×1237×k + 1 باشه
    و k شامل فاکتورهای شناخته‌شده (X1, X2, Z) باشه
    آنوقت می‌تونیم منحنی با torsion متناسب بسازیم
    
    torsion = X1 یا X2 یا Z1 (فاکتورهای Z)
    این کار شانس پیدا کردن فاکتور رو زیاد می‌کنه
    """
    print("=== روش ۱: ECM هدایت‌شده با ساختار ===")
    print()
    print("ایده: به‌جای منحنی تصادفی، منحنی با torsion متناسب با k")
    print()
    
    # محاسبه k برای فاکتورهای احتمالی
    # q = 2×1237×k + 1
    # k باید شامل فاکتورهای smooth باشه
    
    # اگه k = X1 × m باشه:
    # q = 2×1237×X1×m + 1
    # و q ≈ 150 رقم، پس m ≈ 10^(150-67) = 10^83
    
    # اگه k = X2 × m باشه:
    # q = 2×1237×X2×m + 1
    # m ≈ 10^(150-79) = 10^71
    
    # اگه k = X1 × X2 × m باشه:
    # q = 2×1237×X1×X2×m + 1 (69 رقم × m)
    # m ≈ 10^(150-69) = 10^81
    
    print("ساختار k برای فاکتورهای احتمالی:")
    print(f"  k = X1 × m → m ≈ 10^{150 - len(str(X1))}")
    print(f"  k = X2 × m → m ≈ 10^{150 - len(str(X2))}")
    print(f"  k = X1×X2 × m → m ≈ 10^{150 - len(str(X1*X2))}")
    print()
    
    # محاسبه: آیا k می‌تونه شامل فاکتورهای Z باشه؟
    print(f"Z = {str(Z)[:40]}... ({len(str(Z))} رقم)")
    print(f"Z مرکب → می‌تونه فاکتورهای کوچک‌تر داشته باشه")
    print()
    
    # اگر Z رو فاکتور کنیم، فاکتورهای Z ممکنه به k فاکتورهای F2 مربوط باشن
    print("اگه Z رو فاکتور کنیم:")
    print("  Z = Z1 × Z2 × ... × Zn")
    print("  ممکنه k = Z1 × Z2 × ... × Zj × m باشه")
    print("  این کار ECM رو هدایت می‌کنه به سمت فاکتورهای احتمالی")

# ============================================================
#  روش ۲: P-1 با اطلاعات ساختاری
# ============================================================
def structured_pm1_idea():
    """
    ایده: P-1 با اضافه کردن فاکتورهای Z به stage 1
    
    F2 - 1 = 2^4 × 3 × 7 × 1237 × Z
    Z (298 رقم) مرکب
    
    اگه فاکتور q از F2 به فرم q = 2×1237×k + 1 باشه
    و k شامل فاکتورهای Z باشه
    آنوقت P-1 با extra_factors = فاکتورهای Z پیدا می‌کنه
    
    ولی Z خودش فاکتور نشده!
    پس اول باید Z رو فاکتور کنیم
    Z (298 رقم) کوچک‌تر از F2 (303 رقم) هست
    """
    print("\n=== روش ۲: P-1 با اطلاعات ساختاری ===")
    print()
    print("ایده: فاکتوریزاسیون Z (298 رقم) → P-1 برای F2")
    print()
    print(f"Z = {str(Z)[:50]}... ({len(str(Z))} رقم)")
    print(f"F2 = {str(F2)[:50]}... ({len(str(F2))} رقم)")
    print(f"Z کوچک‌تر از F2 → راحت‌تر فاکتور می‌شه")
    print()
    
    # بررسی فاکتورهای کوچک Z
    print("فاکتورهای کوچک Z (تا 10^6):")
    temp = Z
    z_small = []
    for p in range(2, 10**6):
        if temp == 1:
            break
        if temp % p == 0:
            count = 0
            while temp % p == 0:
                temp //= p
                count += 1
            z_small.append((p, count))
            print(f"  {p}^{count}")
    
    if temp > 1:
        print(f"  باقی‌مانده: {str(temp)[:50]}... ({len(str(temp))} رقم)")
        print(f"  باقی‌مانده اول؟ {is_prime(temp)}")
    
    return temp

# ============================================================
#  روش ۳: فاکتوریزاسیون Z با ECM
# ============================================================
def factorize_Z_idea():
    """
    ایده کلیدی: Z (298 رقم) رو فاکتور کنیم
    Z کوچک‌تر از F2 (303 رقم) هست
    اگر Z رو فاکتور کنیم، فاکتورهای Z رو در P-1 برای F2 استفاده می‌کنیم
    """
    print("\n=== روش ۳: فاکتوریزاسیون Z ===")
    print()
    
    temp = Z
    
    # فاکتورهای کوچک
    small_factors = []
    for p in range(2, 10**6):
        if temp == 1:
            break
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            small_factors.append(p)
    
    print(f"فاکتورهای کوچک Z: {small_factors}")
    print(f"باقی‌مانده Z: {len(str(temp))} رقم")
    print(f"باقی‌مانده اول؟ {is_prime(temp)}")
    print()
    
    # اگه باقی‌مانده مرکب باشه، ECM رو روش اجرا کنیم
    if not is_prime(temp) and temp > 1:
        print(f"باقی‌مانده Z مرکب ({len(str(temp))} رقم) → ECM اجرا می‌کنیم")
        print(f"این کوچک‌تر از F2 ({len(str(F2))} رقم) هست")
        print(f"→ شانس فاکتوریزاسیون بیشتر")
    
    return temp

# ============================================================
#  روش ۴: ترکیب Mersenne + Fibonacci
# ============================================================
def mersenne_fibonacci_idea():
    """
    ایده: استفاده از اعداد فیبوناچی برای فاکتوریزاسیون
    
    اگر q فاکتور F2 باشه:
    2^1237 ≡ 1 (mod q)
    
    همچنین اعداد فیبوناچی هم خاصیت مشابه دارن:
    اگر q ≡ ±1 (mod 5)، آنوقت Fib(q-1) ≡ 0 (mod q)
    
    ممکنه الگوی مشترکی بین مرسن و فیبوناچی باشه
    """
    print("\n=== روش ۴: Mersenne + Fibonacci ===")
    print()
    print("ایده: بررسی gcd(Fibonacci(k), F2) برای k های مختلف")
    print()
    
    # محاسبه اعداد فیبوناچی
    a, b = mpz(0), mpz(1)
    
    found = False
    for k in range(2, 10000):
        a, b = b, a + b
        # Fibonacci(k) = b
        # gcd(Fibonacci(k), F2)
        g = gcd(b, F2)
        if g > 1 and g < F2:
            print(f"✓✓✓ FACTOR FOUND! Fib({k})")
            print(f"  factor = {g}")
            found = True
            break
    
    if not found:
        print("✗ در 10000 عدد فیبوناچی اول فاکتور پیدا نشد")
    
    return None

# ============================================================
#  روش ۵: استفاده از Quadratic Residues
# ============================================================
def quadratic_residue_idea():
    """
    ایده: استفاده از Quadratic Residues برای پیدا کردن فاکتور
    
    اگر N = p × q، آنوقت:
    Legendre symbol (a/N) = (a/p) × (a/q)
    
    اگر (a/N) = -1 ولی (a/p) = 1
    آنوقت gcd(a^((N-1)/2) + 1, N) ممکنه فاکتور بده
    
    این روش ترکیب قانون reciprocity درجه دوم هست
    """
    print("\n=== روش ۵: Quadratic Residues ===")
    print()
    print("ایده: بررسی quadratic residues برای F2")
    print()
    
    # بررسی چندین a
    for a in range(2, 1000):
        # محاسبه a^((F2-1)/2) mod F2
        # اگر ≡ 1 (mod F2)، a quadratic residue هست
        # اگر ≡ -1 (mod F2)، quadratic non-residue هست
        # اگر ≠ ±1، فاکتور پیدا شد!
        
        val = powmod(mpz(a), (F2 - 1) // 2, F2)
        
        if val != 1 and val != F2 - 1:
            g = gcd(val - 1, F2)
            if g > 1 and g < F2:
                print(f"✓✓✓ FACTOR FOUND! a={a}")
                print(f"  factor = {g}")
                return g
            g = gcd(val + 1, F2)
            if g > 1 and g < F2:
                print(f"✓✓✓ FACTOR FOUND! a={a}")
                print(f"  factor = {g}")
                return g
    
    print("✗ در 1000 مقدار a فاکتور پیدا نشد")
    return None

# ============================================================
#  روش ۶: استفاده از continued fractions
# ============================================================
def continued_fraction_idea():
    """
    ایده: استفاده از continued fraction های sqrt(F2)
    
    CFRAC method: 
    - محاسبه continued fraction sqrt(N)
    - پیدا کردن convergents
    - بررسی gcd(convergent^2 - N, N)
    """
    print("\n=== روش ۶: Continued Fractions ===")
    print()
    print("ایده: CFRAC روی F2")
    print("محاسبه sqrt(F2) به‌عنوان continued fraction")
    print()
    
    # محاسبه continued fraction sqrt(F2)
    a = isqrt(F2)
    if a * a < F2:
        a += 1
    
    # روش: a0, a1, a2, ...
    # sqrt(N) = a0 + 1/(a1 + 1/(a2 + ...))
    
    m = mpz(0)
    d = mpz(1)
    a0 = isqrt(F2)
    
    convergents = []
    p_prev, p_curr = mpz(1), a0
    q_prev, q_curr = mpz(0), mpz(1)
    
    for i in range(1000):
        m = d * a - m
        d = (F2 - m * m) // d
        a = (a0 + m) // d
        
        # convergent بعدی
        p_next = a * p_curr + p_prev
        q_next = a * q_curr + q_prev
        
        # بررسی: p_next^2 - F2 * q_next^2
        # اگه این smooth باشه، ممکنه فاکتور بده
        val = p_next * p_next - F2 * q_next * q_next
        
        # gcd
        g = gcd(abs(val), F2)
        if g > 1 and g < F2:
            print(f"✓✓✓ FACTOR FOUND! convergent {i}")
            print(f"  factor = {g}")
            return g
        
        p_prev, p_curr = p_curr, p_next
        q_prev, q_curr = q_curr, q_next
    
    print("✗ در 1000 convergent فاکتور پیدا نشد")
    return None

# ============================================================
#  روش ۷: استفاده از Pollard p-1 با stage 2 هوشمند
# ============================================================
def smart_pm1_stage2():
    """
    ایده: P-1 با stage 2 هوشمند
    
    stage 1: محاسبه a = 2^M mod F2 (M = حاصلضرب اعداد اول تا B1)
    stage 2: برای هر عدد اول p بین B1 و B2:
      بررسی gcd(a^p - 1, F2)
    
    بهبود: به‌جای بررسی همه اعداد اول، فقط اعداد اول به فرم
    2×1237×k + 1 رو بررسی کنیم (فرم Mersenne)
    """
    print("\n=== روش ۷: P-1 با stage 2 هوشمند ===")
    print()
    
    # P-1 با B1=10^8
    B1 = 10**8
    print(f"Stage 1: B1={B1}")
    
    # تولید اعداد اول تا B1
    sieve = bytearray([1]) * (B1 + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(B1**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, B1 + 1, i):
                sieve[j] = 0
    primes = [i for i in range(2, B1 + 1) if sieve[i]]
    
    # اضافه کردن X1, X2
    extra = [int(X1), int(X2)]
    for e in extra:
        if is_prime(e) and e not in primes:
            primes.append(e)
    
    print(f"تعداد اعداد اول: {len(primes)}")
    
    # stage 1
    a = mpz(2)
    for p in primes:
        pe = p
        while pe * p <= B1:
            pe *= p
        a = powmod(a, pe, F2)
    
    g = gcd(a - 1, F2)
    print(f"Stage 1: gcd = {g}")
    
    if g > 1 and g < F2:
        print(f"✓✓✓ FACTOR FOUND!")
        return g
    
    # stage 2 هوشمند: فقط اعداد به فرم 2×1237×k + 1
    print("Stage 2: بررسی اعداد به فرم 2×1237×k + 1")
    
    for k in range(B1 // (2*1237), (10*B1) // (2*1237)):
        q = 2 * 1237 * k + 1
        if q > 10 * B1:
            break
        if not is_prime(q):
            continue
        val = powmod(a, q, F2)
        g = gcd(val - 1, F2)
        if g > 1 and g < F2:
            print(f"✓✓✓ FACTOR FOUND! k={k}, q={q}")
            return g
    
    print("✗ فاکتور پیدا نشد")
    return None

# ============================================================
#  main
# ============================================================
def main():
    print("=" * 70)
    print("  تفکر عمیق: روش‌های ابتکاری برای فاکتوریزاسیون F2")
    print("=" * 70)
    print()
    print(f"F2 = {str(F2)[:50]}... ({len(str(F2))} رقم)")
    print(f"sqrt(F2) ≈ 10^{len(str(isqrt(F2)))}")
    print()
    
    # روش ۱
    guided_ecm_idea()
    
    # روش ۲
    Z_remainder = structured_pm1_idea()
    
    # روش ۳
    factorize_Z_idea()
    
    # روش ۴
    mersenne_fibonacci_idea()
    
    # روش ۵
    quadratic_residue_idea()
    
    # روش ۶
    continued_fraction_idea()
    
    # روش ۷
    smart_pm1_stage2()
    
    print("\n" + "=" * 70)
    print("  نتیجه تفکر عمیق")
    print("=" * 70)
    print()
    print("بهترین ایده: فاکتوریزاسیون Z (298 رقم)")
    print("Z کوچک‌تر از F2 → راحت‌تر فاکتور می‌شه")
    print("سپس فاکتورهای Z رو در P-1 برای F2 استفاده کنیم")
    print()
    print("ایده دوم: ECM هدایت‌شده با torsion متناسب با X1/X2")
    print("ایده سوم: continued fractions روی F2")

if __name__ == "__main__":
    main()
