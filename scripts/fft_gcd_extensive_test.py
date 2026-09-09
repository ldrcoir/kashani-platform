#!/usr/bin/env python3
"""
تست گسترده روش GCD طیفی
========================
روش:
1. FFT روی باقی‌مانده‌های N mod k (k = 1, 2, ..., max_k)
2. پیدا کردن فرکانس‌های غالب
3. تبدیل فرکانس به دوره
4. GCD(N, period) = فاکتور
"""

import numpy as np
import gmpy2
from gmpy2 import mpz, is_prime, gcd
import time

def fft_remainders(N, max_k=4096):
    """FFT روی باقی‌مانده‌های N mod k"""
    N_mpz = mpz(N)
    remainders = np.zeros(max_k, dtype=np.float64)
    
    for k in range(1, max_k + 1):
        remainders[k-1] = float(N_mpz % k)
    
    # نرمال‌سازی
    max_r = np.max(remainders)
    if max_r > 0:
        remainders = remainders / max_r
    
    # FFT
    fft_result = np.fft.fft(remainders)
    magnitude = np.abs(fft_result)
    
    freqs = np.fft.fftfreq(max_k, d=1.0)
    half = max_k // 2
    
    return freqs[:half], magnitude[:half]

def gcd_spectral_factor(N, max_k=4096, num_peaks=100):
    """
    فاکتوریزاسیون با روش GCD طیفی
    """
    N_mpz = mpz(N)
    
    # FFT روی باقی‌مانده‌ها
    freqs, mag = fft_remainders(N, max_k)
    
    # فرکانس‌های غالب
    mag_for_peaks = mag.copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-num_peaks:][::-1]
    
    # بررسی هر فرکانس غالب
    for idx in peak_indices:
        freq = freqs[idx]
        if freq == 0:
            continue
        period = 1.0 / freq
        period_int = int(round(period))
        
        if period_int > 1 and period_int < N:
            g = gcd(N_mpz, period_int)
            if g > 1 and g < N_mpz:
                return g, N_mpz // g
    
    return None, None

def test_method():
    """تست گسترده"""
    print("=" * 70)
    print("  تست گسترده روش GCD طیفی")
    print("=" * 70)
    
    # اعداد مرکب با فاکتورهای مختلف
    test_cases = []
    
    # اعداد ساده
    for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]:
        for q in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]:
            if p < q:
                N = p * q
                test_cases.append((N, p, q))
    
    # اعداد متوسط
    for p in [101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]:
        for q in [101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]:
            if p < q:
                N = p * q
                test_cases.append((N, p, q))
    
    print(f"تعداد تست‌ها: {len(test_cases)}")
    
    success = 0
    fail = 0
    failures = []
    
    t0 = time.time()
    
    for N, p, q in test_cases:
        factor, cofactor = gcd_spectral_factor(N, max_k=4096, num_peaks=100)
        
        if factor is not None:
            # تأیید
            if factor * cofactor == N:
                success += 1
            else:
                fail += 1
                failures.append((N, p, q, "تأیید ناموفق"))
        else:
            fail += 1
            failures.append((N, p, q, "فاکتور پیدا نشد"))
    
    elapsed = time.time() - t0
    
    print(f"\nنتایج:")
    print(f"  موفق: {success}")
    print(f"  ناموفق: {fail}")
    print(f"  درصد موفقیت: {100*success/len(test_cases):.1f}%")
    print(f"  زمان کل: {elapsed:.1f}s")
    print(f"  زمان هر تست: {elapsed/len(test_cases)*1000:.1f}ms")
    
    # نمایش چند مورد ناموفق
    if failures:
        print(f"\nمورد‌های ناموفق (10 تای اول):")
        for N, p, q, reason in failures[:10]:
            print(f"  N={N} = {p}×{q}: {reason}")
    
    return success, fail, failures

def test_large_numbers():
    """تست اعداد بزرگ‌تر"""
    print(f"\n{'='*70}")
    print(f"  تست اعداد بزرگ‌تر")
    print(f"{'='*70}")
    
    # اعداد با فاکتورهای بزرگ‌تر
    test_cases = []
    for p in [211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293]:
        for q in [211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293]:
            if p < q:
                N = p * q
                test_cases.append((N, p, q))
    
    # اعداد خیلی بزرگ‌تر
    import random
    random.seed(42)
    for _ in range(50):
        p = random.choice([1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051])
        q = random.choice([1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109])
        if p != q:
            test_cases.append((p*q, p, q))
    
    print(f"تعداد تست‌ها: {len(test_cases)}")
    
    success = 0
    fail = 0
    failures = []
    
    for N, p, q in test_cases:
        factor, cofactor = gcd_spectral_factor(N, max_k=8192, num_peaks=200)
        
        if factor is not None and factor * cofactor == N:
            success += 1
        else:
            fail += 1
            failures.append((N, p, q))
    
    print(f"\nنتایج:")
    print(f"  موفق: {success}")
    print(f"  ناموفق: {fail}")
    print(f"  درصد موفقیت: {100*success/len(test_cases):.1f}%")
    
    if failures:
        print(f"\nمورد‌های ناموفق (10 تای اول):")
        for N, p, q in failures[:10]:
            print(f"  N={N} = {p}×{q}")
    
    return success, fail

def test_semiprime_with_close_factors():
    """تست اعداد با فاکتورهای نزدیک (سخت‌ترین حالت)"""
    print(f"\n{'='*70}")
    print(f"  تست اعداد با فاکتورهای نزدیک (سخت‌ترین)")
    print(f"{'='*70}")
    
    test_cases = []
    # اعداد اول دوقلو (twin primes)
    twin_primes = [(3,5), (5,7), (11,13), (17,19), (29,31), (41,43), (59,61), (71,73),
                   (101,103), (107,109), (137,139), (149,151), (179,181), (191,193),
                   (197,199), (227,229), (239,241), (269,271), (281,283), (311,313),
                   (347,349), (419,421), (431,433), (461,463), (521,523), (569,571),
                   (599,601), (617,619), (641,643), (659,661), (809,811), (821,823),
                   (827,829), (857,859), (881,883)]
    
    for p, q in twin_primes:
        test_cases.append((p*q, p, q))
    
    print(f"تعداد تست‌ها: {len(test_cases)}")
    
    success = 0
    fail = 0
    failures = []
    
    for N, p, q in test_cases:
        factor, cofactor = gcd_spectral_factor(N, max_k=8192, num_peaks=200)
        
        if factor is not None and factor * cofactor == N:
            success += 1
        else:
            fail += 1
            failures.append((N, p, q))
    
    print(f"\nنتایج:")
    print(f"  موفق: {success}")
    print(f"  ناموفق: {fail}")
    print(f"  درصد موفقیت: {100*success/len(test_cases):.1f}%")
    
    if failures:
        print(f"\nمورد‌های ناموفق:")
        for N, p, q in failures:
            print(f"  N={N} = {p}×{q}")

if __name__ == "__main__":
    # تست اصلی
    success, fail, failures = test_method()
    
    # تست اعداد بزرگ
    test_large_numbers()
    
    # تست فاکتورهای نزدیک
    test_semiprime_with_close_factors()
