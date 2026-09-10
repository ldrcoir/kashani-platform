#!/usr/bin/env python3
"""
روش‌های ابتکاری برای حالت 150×150
================================
تحلیل کاربر: 150 × 150 = 300 ≈ 303 رقم

روش‌های جدید:
۱. Fermat با delta بسیار بزرگ (10^10+)
۲. روش LEHMAN (بهبود Fermat)
۳. استفاده از ساختار Mersenne
۴. Batch GCD با اعداد مرتبط
۵. جستجوی هوشمند k = (q-1)/(2×1237)
"""

import gmpy2
from gmpy2 import mpz, is_prime, gcd, isqrt, iroot, powmod, next_prime
import time
import os
import subprocess
import json

P = 1237
M_1237 = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M_1237 // F1
F2_STR = str(F2)

WORKDIR = "/home/z/my-project/A136030_innovative_v7"
os.makedirs(WORKDIR, exist_ok=True)

LOG_FILE = f"{WORKDIR}/search.log"
FOUND_FILE = f"{WORKDIR}/FOUND_factors.txt"


def log(msg):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")


def verify_and_save(factor, method, **kwargs):
    f = mpz(factor)
    if f <= 1 or f >= F2:
        return False
    if F2 % f != 0:
        return False
    cofactor = F2 // f
    if f * cofactor != F2:
        return False
    
    log(f"✓✓✓ FACTOR OF F2 FOUND!")
    log(f"  method: {method}")
    log(f"  factor: {f}")
    log(f"  factor digits: {len(str(f))}")
    log(f"  factor prime: {is_prime(f)}")
    log(f"  cofactor: {cofactor}")
    log(f"  cofactor digits: {len(str(cofactor))}")
    log(f"  cofactor prime: {is_prime(cofactor)}")
    
    with open(FOUND_FILE, 'w') as out:
        out.write(f"=== FACTOR OF F2 FOUND ===\n")
        out.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"method: {method}\n")
        for k, v in kwargs.items():
            out.write(f"{k}: {v}\n")
        out.write(f"factor: {f}\n")
        out.write(f"factor digits: {len(str(f))}\n")
        out.write(f"factor prime: {is_prime(f)}\n")
        out.write(f"cofactor: {cofactor}\n")
        out.write(f"cofactor digits: {len(str(cofactor))}\n")
        out.write(f"cofactor prime: {is_prime(cofactor)}\n")
    
    return True


# ============================================================
#  روش ۱: Fermat با delta بسیار بزرگ
# ============================================================
def fermat_large_delta(max_delta=10**10, time_limit=3600):
    """
    Fermat با delta تا 10^10
    
    اگه فاکتورها نزدیک باشن ولی نه خیلی نزدیک،
    delta بزرگ لازم هست
    """
    log("=== روش ۱: Fermat با delta بزرگ ===")
    
    a = isqrt(F2)
    if a * a < F2:
        a += 1
    
    t0 = time.time()
    
    for delta in range(max_delta):
        a_test = a + delta
        b_squared = a_test * a_test - F2
        if b_squared >= 0:
            b, is_perfect = iroot(b_squared, 2)
            if is_perfect:
                f1 = a_test + b
                f2 = a_test - b
                if f1 > 1 and f2 > 1:
                    log(f"✓✓✓ FACTOR FOUND! delta={delta}")
                    if verify_and_save(f1, 'Fermat-large', delta=delta):
                        return f1
        
        if delta % 10000000 == 0 and delta > 0:
            elapsed = time.time() - t0
            if elapsed > time_limit:
                log(f"  توقف بعد از {elapsed:.0f}s در delta={delta:,}")
                break
            log(f"  delta={delta:,}, زمان={elapsed:.1f}s, سرعت={delta/elapsed:,.0f} delta/s")
    
    log("Fermat جواب نداد")
    return None


# ============================================================
#  روش ۲: Lehman's method (بهبود Fermat)
# ============================================================
def lehman_method(k_max=1000, time_limit=3600):
    """
    روش Lehman: بهبود Fermat
    
    برای هر k، بررسی کن:
    a = ceil(sqrt(k × N))
    b² = a² - k×N
    اگه b² مربع کامل باشه، فاکتور پیدا شد
    """
    log("=== روش ۲: Lehman's method ===")
    
    t0 = time.time()
    
    for k in range(1, k_max + 1):
        kN = k * F2
        a = isqrt(kN)
        if a * a < kN:
            a += 1
        
        # بررسی چند a
        for delta in range(100):
            a_test = a + delta
            b_squared = a_test * a_test - kN
            if b_squared >= 0:
                b, is_perfect = iroot(b_squared, 2)
                if is_perfect:
                    # فاکتور ممکن: gcd(a_test - b, N)
                    g = gcd(a_test - b, F2)
                    if g > 1 and g < F2:
                        log(f"✓✓✓ FACTOR FOUND! k={k}, delta={delta}")
                        if verify_and_save(g, 'Lehman', k=k, delta=delta):
                            return g
                    g = gcd(a_test + b, F2)
                    if g > 1 and g < F2:
                        log(f"✓✓✓ FACTOR FOUND! k={k}, delta={delta}")
                        if verify_and_save(g, 'Lehman', k=k, delta=delta):
                            return g
        
        if k % 100 == 0:
            elapsed = time.time() - t0
            if elapsed > time_limit:
                log(f"  توقف بعد از {elapsed:.0f}s در k={k}")
                break
            log(f"  k={k}, زمان={elapsed:.1f}s")
    
    log("Lehman جواب نداد")
    return None


# ============================================================
#  روش ۳: استفاده از خاصیت Mersenne
# ============================================================
def mersenne_property_method():
    """
    روش ابتکاری: استفاده از خاصیت Mersenne
    
    2^1237 ≡ 1 (mod F2)
    پس order of 2 mod F2 = 1237 (یا مقسوم‌علیه آن)
    
    اگه F2 = p × q:
    2^1237 ≡ 1 (mod p) و 2^1237 ≡ 1 (mod q)
    پس order of 2 mod p | 1237
    و order of 2 mod q | 1237
    
    چون 1237 اول، order = 1 یا 1237
    order = 1 یعنی 2 ≡ 1 (mod p) یعنی p | 1 - غیرممکن
    پس order = 1237
    
    یعنی 1237 | (p-1) و 1237 | (q-1)
    پس p ≡ 1 (mod 1237) و q ≡ 1 (mod 1237)
    
    همچنین p ≡ ±1 (mod 8) و q ≡ ±1 (mod 8)
    """
    log("=== روش ۳: خاصیت Mersenne ===")
    log("فاکتورهای F2 باید:")
    log("  p ≡ 1 (mod 2474)  [فرم Mersenne]")
    log("  p ≡ ±1 (mod 8)   [شرط Lucas]")
    log("  پس p mod 19792 ∈ {1, 2475, 9896, 12373}")
    
    # محاسبه 2^(1237/d) - 1 برای d های مختلف
    # اگه gcd(2^(1237/d) - 1, F2) > 1، فاکتور پیدا شد
    # ولی 1237 اول، پس d = 1 یا 1237
    
    # روش دیگر: محاسبه 2^k - 1 برای k های غیر اول
    # اگه k | 1237، پس 2^k - 1 | 2^1237 - 1
    # ولی 1237 اول، پس فقط k = 1 و k = 1237
    
    # روش جدید: استفاده از ضرایب دوجمله‌ای
    # (2^1237 - 1) = F1 × F2
    # 2^1237 ≡ 1 (mod F2)
    # 2^619 ≡ ±1 (mod F2)؟ (اگه 619 | (p-1))
    
    log("بررسی 2^k mod F2 برای k های مختلف...")
    
    # اگه gcd(2^k - 1, F2) > 1 برای k < 1237
    # یعنی order of 2 mod p | k
    
    for k in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 
              47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
              101, 103, 107, 109, 113, 127, 131, 137, 139, 149,
              151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
              # مقسوم‌علیه‌های 1236 = 4 × 3 × 103
              2, 3, 4, 6, 12, 103, 206, 309, 412, 618, 1236]:
        val = powmod(2, k, F2)
        g = gcd(val - 1, F2)
        if g > 1 and g < F2:
            log(f"✓✓✓ FACTOR FOUND! k={k}")
            if verify_and_save(g, 'Mersenne-order', k=k):
                return g
        g = gcd(val + 1, F2)
        if g > 1 and g < F2:
            log(f"✓✓✓ FACTOR FOUND! k={k} (val+1)")
            if verify_and_save(g, 'Mersenne-order', k=k, type='plus'):
                return g
    
    log("فاکتوری پیدا نشد")
    return None


# ============================================================
#  روش ۴: Batch GCD با اعداد مرسن
# ============================================================
def batch_gcd_mersenne():
    """
    روش ابتکاری: Batch GCD با اعداد مرسن
    
    اگه F2 فاکتور مشترک با M(k) = 2^k - 1 داشته باشه
    برای k ≠ 1237، آنوقت فاکتور پیدا شد
    """
    log("=== روش ۴: Batch GCD با اعداد مرسن ===")
    
    # بررسی M(k) برای k های اول تا 5000
    for k in range(2, 5000):
        if not is_prime(k):
            continue
        
        M_k = mpz(2)**k - 1
        g = gcd(M_k, F2)
        
        if g > 1 and g < F2:
            log(f"✓✓✓ FACTOR FOUND! M({k})")
            if verify_and_save(g, 'Batch-Mersenne', k=k):
                return g
    
    log("فاکتوری پیدا نشد")
    return None


# ============================================================
#  روش ۵: جستجوی k = (q-1)/(2×1237)
# ============================================================
def search_k_for_150_digit():
    """
    روش ابتکاری: اگه q ≈ 150 رقم، آنوقت:
    q = 2 × 1237 × k + 1
    k ≈ 10^150 / 2474 ≈ 10^146
    
    نمی‌تونیم همه k رو بررسی کنیم، ولی می‌تونیم
    k هایی با ساختار خاص رو امتحان کنیم
    """
    log("=== روش ۵: جستجوی k برای فاکتور 150 رقمی ===")
    
    # k ≈ 10^146 - خیلی بزرگ
    # ولی اگه k شامل فاکتورهای شناخته شده باشه...
    
    X1 = mpz("110421384041193593117465987")
    X2 = mpz("442440509040507330087115446251753610709")
    
    # ایده: اگه k = X1 × X2 × m باشه
    # q = 2 × 1237 × X1 × X2 × m + 1
    
    base = 2 * 1237 * X1 * X2  # 71 رقم
    log(f"base = 2 × 1237 × X1 × X2 = {base}")
    log(f"base ارقام: {len(str(base))}")
    log(f"برای q = 150 رقم: m ≈ 10^{150 - len(str(base))}")
    log("")
    
    # برای q = 150 رقم، m ≈ 10^79
    # نمی‌تونیم همه m رو بررسی کنیم
    # ولی می‌تونیم m های خاص رو امتحان کنیم
    
    # m = 1, 2, 3, ... تا 1000
    for m in range(1, 1001):
        q = base * m + 1
        if is_prime(q) and F2 % q == 0:
            log(f"✓✓✓ FACTOR FOUND! m={m}")
            if verify_and_save(q, 'k-search-X1X2', m=m):
                return q
    
    # m = اعداد اول
    p = 2
    for _ in range(1000):
        q = base * p + 1
        if is_prime(q) and F2 % q == 0:
            log(f"✓✓✓ FACTOR FOUND! m=prime({p})")
            if verify_and_save(q, 'k-search-X1X2-prime', m=p):
                return q
        p = int(next_prime(p))
    
    log("فاکتوری پیدا نشد")
    return None


# ============================================================
#  main
# ============================================================
def main():
    log("=" * 70)
    log("  روش‌های ابتکاری v7 - حالت 150×150")
    log("=" * 70)
    log(f"F2 = {F2_STR[:50]}... ({len(F2_STR)} رقم)")
    log(f"sqrt(F2) ارقام: {len(str(isqrt(F2)))}")
    log("تحلیل: 150 × 150 ≈ 303 رقم")
    log("")
    
    # روش ۱: Fermat بزرگ
    result = fermat_large_delta(max_delta=10**9, time_limit=300)
    if result:
        return
    
    # روش ۲: Lehman
    result = lehman_method(k_max=10000, time_limit=300)
    if result:
        return
    
    # روش ۳: خاصیت Mersenne
    result = mersenne_property_method()
    if result:
        return
    
    # روش ۴: Batch GCD
    result = batch_gcd_mersenne()
    if result:
        return
    
    # روش ۵: جستجوی k
    result = search_k_for_150_digit()
    if result:
        return
    
    log("\n=== همه روش‌ها تموم شد ===")
    log("فاکتور F2 پیدا نشده")


if __name__ == "__main__":
    main()
