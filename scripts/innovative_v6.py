#!/usr/bin/env python3
"""
روش‌های ابتکاری جدید برای فاکتوریزاسیون F2
==========================================
۱. Batch GCD: استفاده از GCD گروهی
۲. روش ترکیبی ECM + Fermat + Pollard Rho
۳. تحلیل ساختار F2 با ضرایب دوجمله‌ای
۴. جستجوی هوشمند با استفاده از F1
۵. روش lattice-based
"""

import gmpy2
from gmpy2 import mpz, is_prime, gcd, isqrt, iroot, powmod, next_prime
import numpy as np
import time
import os
import subprocess
import json

P = 1237
M_1237 = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M_1237 // F1

ECM = "/home/z/my-project/ecm-extract/usr/bin/ecm"
LD_PATH = "/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"

WORKDIR = "/home/z/my-project/A136030_innovative_v6"
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
#  روش ۱: Batch GCD
# ============================================================
def batch_gcd_method():
    """
    روش ابتکاری: Batch GCD
    
    ایده: اگه N = p × q، و ما چندین عدد مرتبط داشته باشیم،
    می‌تونیم با GCD گروهی فاکتور رو پیدا کنیم.
    
    برای F2: استفاده از اعداد به فرم 2^k - 1 برای k های مختلف
    """
    log("\n=== روش ۱: Batch GCD ===")
    
    # تولید اعداد به فرم 2^k - 1
    candidates = []
    for k in range(2, 5000):
        if is_prime(k):
            candidates.append(mpz(2)**k - 1)
    
    log(f"تعداد کاندید‌ها: {len(candidates)}")
    
    # GCD هر کاندید با F2
    for i, c in enumerate(candidates):
        g = gcd(c, F2)
        if g > 1 and g < F2:
            log(f"✓✓✓ FACTOR FOUND با Batch GCD!")
            if verify_and_save(g, 'Batch-GCD', candidate_index=i):
                return g
    
    log("فاکتوری پیدا نشد")
    return None


# ============================================================
#  روش ۲: ترکیبی ECM + Fermat + Pollard Rho
# ============================================================
def hybrid_method():
    """
    روش ابتکاری: ترکیبی
    
    ۱. Pollard Rho با پارامترهای مختلف
    ۲. Fermat با delta بزرگ
    ۳. ECM با B1 متوسط
    """
    log("\n=== روش ۲: ترکیبی ECM + Fermat + Rho ===")
    
    # Pollard Rho با چندین نقطه شروع
    log("Pollard Rho با 10 نقطه شروع...")
    import random
    random.seed(42)
    
    for trial in range(10):
        x = mpz(random.randint(2, 10**6))
        y = x
        c = mpz(random.randint(1, 10**6))
        d = mpz(1)
        
        for _ in range(100000):
            x = (x * x + c) % F2
            y = (y * y + c) % F2
            y = (y * y + c) % F2
            d = gcd(abs(x - y), F2)
            
            if d > 1 and d < F2:
                log(f"✓✓✓ FACTOR FOUND با Pollard Rho!")
                if verify_and_save(d, 'Pollard-Rho', trial=trial):
                    return d
            if d == F2:
                break
    
    log("Pollard Rho جواب نداد")
    
    # Fermat با delta بزرگ‌تر
    log("Fermat با delta تا 10^7...")
    a = isqrt(F2)
    if a * a < F2:
        a += 1
    
    for delta in range(10**7):
        a_test = a + delta
        b_squared = a_test * a_test - F2
        if b_squared >= 0:
            b, is_perfect = iroot(b_squared, 2)
            if is_perfect:
                f1 = a_test + b
                f2 = a_test - b
                if f1 > 1 and f2 > 1:
                    log(f"✓✓✓ FACTOR FOUND با Fermat!")
                    if verify_and_save(f1, 'Fermat', delta=delta):
                        return f1
        
        if delta % 1000000 == 0 and delta > 0:
            log(f"  delta={delta:,}")
    
    log("Fermat جواب نداد")
    return None


# ============================================================
#  روش ۳: تحلیل ضرایب دوجمله‌ای
# ============================================================
def binomial_coefficient_method():
    """
    روش ابتکاری: تحلیل ضرایب دوجمله‌ای
    
    ایده: اگه F2 = p × q، شاید ضرایب (F2 choose k)
    الگوی p یا q رو نشون بدن
    """
    log("\n=== روش ۳: ضرایب دوجمله‌ای ===")
    
    # محاسبه gcd(F2, k!) برای k های مختلف
    for k in range(2, 10000):
        # k! mod F2
        factorial = mpz(1)
        for i in range(2, k + 1):
            factorial = (factorial * i) % F2
        
        g = gcd(factorial, F2)
        if g > 1 and g < F2:
            log(f"✓✓✓ FACTOR FOUND با k={k}!")
            if verify_and_save(g, 'Binomial', k=k):
                return g
    
    log("فاکتوری پیدا نشد")
    return None


# ============================================================
#  روش ۴: جستجوی هوشمند با استفاده از F1
# ============================================================
def f1_guided_search():
    """
    روش ابتکاری: استفاده از ساختار F1 برای پیدا کردن F2
    
    ایده: F1 - 1 = 2 × 3 × 7 × 1237 × X1 × X2
    شاید فاکتورهای F2 با X1 یا X2 رابطه داشته باشن
    """
    log("\n=== روش ۴: جستجوی هدایت‌شده با F1 ===")
    
    X1 = mpz("110421384041193593117465987")
    X2 = mpz("442440509040507330087115446251753610709")
    
    # بررسی: آیا X1 ± k فاکتور F2 هست؟
    log("بررسی X1 ± k...")
    for k in range(-1000, 1001):
        candidate = X1 + k
        if candidate > 1 and candidate < F2:
            if F2 % candidate == 0:
                log(f"✓✓✓ FACTOR FOUND! X1 + {k}")
                if verify_and_save(candidate, 'F1-guided-X1', offset=k):
                    return candidate
    
    # بررسی: آیا X2 ± k فاکتور F2 هست؟
    log("بررسی X2 ± k...")
    for k in range(-1000, 1001):
        candidate = X2 + k
        if candidate > 1 and candidate < F2:
            if F2 % candidate == 0:
                log(f"✓✓✓ FACTOR FOUND! X2 + {k}")
                if verify_and_save(candidate, 'F1-guided-X2', offset=k):
                    return candidate
    
    # بررسی: آیا X1 × k + 1 فاکتور F2 هست؟
    log("بررسی X1 × k + 1...")
    for k in range(1, 10000):
        candidate = X1 * k + 1
        if candidate > 1 and candidate < F2:
            if F2 % candidate == 0:
                log(f"✓✓✓ FACTOR FOUND! X1 × {k} + 1")
                if verify_and_save(candidate, 'F1-guided-X1-mult', k=k):
                    return candidate
    
    # بررسی: آیا X2 × k + 1 فاکتور F2 هست؟
    log("بررسی X2 × k + 1...")
    for k in range(1, 10000):
        candidate = X2 * k + 1
        if candidate > 1 and candidate < F2:
            if F2 % candidate == 0:
                log(f"✓✓✓ FACTOR FOUND! X2 × {k} + 1")
                if verify_and_save(candidate, 'F1-guided-X2-mult', k=k):
                    return candidate
    
    log("فاکتوری پیدا نشد")
    return None


# ============================================================
#  روش ۵: استفاده از powers of 2
# ============================================================
def power_of_2_method():
    """
    روش ابتکاری: استفاده از powers of 2
    
    ایده: F2 | (2^1237 - 1) / F1
    پس 2^1237 ≡ 1 (mod F2)
    شاید 2^k برای k های دیگر هم الگوی فاکتور رو نشون بده
    """
    log("\n=== روش ۵: powers of 2 ===")
    
    # محاسبه 2^k mod F2 برای k های مختلف
    # اگه gcd(2^k - 1, F2) > 1، فاکتور پیدا شد
    
    log("بررسی gcd(2^k - 1, F2) برای k های مختلف...")
    
    # k های مهم: مقسوم‌علیه‌های 1237
    # 1237 اول هست، پس فقط k = 1 و k = 1237
    
    # ولی بررسی k های دیگر
    for k in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 
              53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
              127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193,
              197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271,
              277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359,
              367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443,
              449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541,
              547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619,
              631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719,
              727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821,
              823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911,
              919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997,
              1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051,
              1237]:
        val = powmod(2, k, F2)
        g = gcd(val - 1, F2)
        if g > 1 and g < F2:
            log(f"✓✓✓ FACTOR FOUND! k={k}")
            if verify_and_save(g, 'Power-of-2', k=k):
                return g
    
    log("فاکتوری پیدا نشد")
    return None


# ============================================================
#  روش ۶: ECM با sigma های خاص
# ============================================================
def ecm_special_sigma():
    """
    روش ابتکاری: ECM با sigma های خاص
    
    به‌جای sigma تصادفی، از sigma های مرتبط با F1 استفاده کنیم
    """
    log("\n=== روش ۶: ECM با sigma خاص ===")
    
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    X1 = 110421384041193593117465987
    X2 = 442440509040507330087115446251753610709
    
    # sigma های خاص
    sigmas = [
        1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31,
        1237, 2474,
        X1 % (2**31), X2 % (2**31),
        123456789, 987654321,
    ]
    
    for sigma in sigmas:
        log(f"  ECM با sigma={sigma}, B1=1e8...")
        
        log_file = f"{WORKDIR}/ecm_sigma_{sigma}.log"
        
        try:
            with open(log_file, 'w') as out:
                proc = subprocess.run(
                    [ECM, '-sigma', str(sigma), '-v', '1e8'],
                    input=str(F2).encode(),
                    stdout=out, stderr=subprocess.STDOUT, env=env, timeout=60
                )
            
            with open(log_file) as f:
                content = f.read()
            
            if 'Factor found' in content:
                import re
                matches = re.findall(r'(\d{10,})', content)
                for m in matches:
                    f = mpz(m)
                    if f > 1 and f < F2 and F2 % f == 0:
                        log(f"  ✓✓✓ FACTOR FOUND!")
                        if verify_and_save(f, 'ECM-special-sigma', sigma=sigma):
                            return f
        except:
            pass
    
    log("فاکتوری پیدا نشد")
    return None


# ============================================================
#  main
# ============================================================
def main():
    log("=" * 70)
    log("  روش‌های ابتکاری v6 برای فاکتوریزاسیون F2")
    log("=" * 70)
    log(f"F2 = {str(F2)[:50]}... ({len(str(F2))} رقم)")
    log("")
    
    # روش ۱: Batch GCD
    result = batch_gcd_method()
    if result:
        return
    
    # روش ۲: ترکیبی
    result = hybrid_method()
    if result:
        return
    
    # روش ۳: ضرایب دوجمله‌ای
    result = binomial_coefficient_method()
    if result:
        return
    
    # روش ۴: جستجوی هدایت‌شده با F1
    result = f1_guided_search()
    if result:
        return
    
    # روش ۵: powers of 2
    result = power_of_2_method()
    if result:
        return
    
    # روش ۶: ECM با sigma خاص
    result = ecm_special_sigma()
    if result:
        return
    
    log("\n=== همه روش‌ها تموم شد ===")
    log("فاکتور F2 پیدا نشده")


if __name__ == "__main__":
    main()
