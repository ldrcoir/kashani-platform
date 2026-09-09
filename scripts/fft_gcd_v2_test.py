#!/usr/bin/env python3
"""
روش GCD طیفی بهبود یافته
========================
بهبودها:
1. استفاده از max_k بزرگ‌تر
2. بررسی period و ضرایب آن
3. استفاده از فرکانس‌های مختلف
4. ترکیب با روش‌های دیگر
"""

import numpy as np
import gmpy2
from gmpy2 import mpz, is_prime, gcd
import time

def fft_remainders(N, max_k):
    """FFT روی باقی‌مانده‌های N mod k"""
    N_mpz = mpz(N)
    remainders = np.zeros(max_k, dtype=np.float64)
    
    for k in range(1, max_k + 1):
        remainders[k-1] = float(N_mpz % k)
    
    max_r = np.max(remainders)
    if max_r > 0:
        remainders = remainders / max_r
    
    fft_result = np.fft.fft(remainders)
    magnitude = np.abs(fft_result)
    
    freqs = np.fft.fftfreq(max_k, d=1.0)
    half = max_k // 2
    
    return freqs[:half], magnitude[:half]

def gcd_spectral_factor_v2(N, max_k=16384, num_peaks=500):
    """
    نسخه بهبود یافته:
    - max_k بزرگ‌تر
    - بررسی period و ضرایب آن
    """
    N_mpz = mpz(N)
    
    freqs, mag = fft_remainders(N, max_k)
    
    mag_for_peaks = mag.copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-num_peaks:][::-1]
    
    for idx in peak_indices:
        freq = freqs[idx]
        if freq == 0:
            continue
        period = 1.0 / freq
        period_int = int(round(period))
        
        # بررسی period و ضرایب آن
        for mult in range(1, 100):
            candidate = period_int * mult
            if candidate > 1 and candidate < N and candidate < max_k * 10:
                g = gcd(N_mpz, candidate)
                if g > 1 and g < N_mpz:
                    return g, N_mpz // g
        
        # همچنین period / اعداد صحیح
        for div in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
            candidate = period_int // div
            if candidate > 1 and candidate < N:
                g = gcd(N_mpz, candidate)
                if g > 1 and g < N_mpz:
                    return g, N_mpz // g
    
    return None, None

def test_v2():
    """تست نسخه بهبود یافته"""
    print("=" * 70)
    print("  تست نسخه بهبود یافته GCD طیفی v2")
    print("=" * 70)
    
    # اعداد تست
    test_cases = []
    
    # اعداد ساده
    for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]:
        for q in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]:
            if p < q:
                test_cases.append((p*q, p, q))
    
    # اعداد متوسط
    for p in [101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]:
        for q in [101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]:
            if p < q:
                test_cases.append((p*q, p, q))
    
    # اعداد بزرگ‌تر
    for p in [211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293]:
        for q in [211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293]:
            if p < q:
                test_cases.append((p*q, p, q))
    
    print(f"تعداد تست‌ها: {len(test_cases)}")
    
    success = 0
    fail = 0
    failures = []
    
    t0 = time.time()
    
    for N, p, q in test_cases:
        factor, cofactor = gcd_spectral_factor_v2(N, max_k=16384, num_peaks=500)
        
        if factor is not None and factor * cofactor == N:
            success += 1
        else:
            fail += 1
            failures.append((N, p, q))
    
    elapsed = time.time() - t0
    
    print(f"\nنتایج:")
    print(f"  موفق: {success}")
    print(f"  ناموفق: {fail}")
    print(f"  درصد موفقیت: {100*success/len(test_cases):.1f}%")
    print(f"  زمان کل: {elapsed:.1f}s")
    print(f"  زمان هر تست: {elapsed/len(test_cases)*1000:.1f}ms")
    
    # تحلیل موارد ناموفق
    if failures:
        print(f"\nتحلیل موارد ناموفق:")
        print(f"  تعداد: {len(failures)}")
        
        # دسته‌بندی بر اساس اندازه فاکتور کوچک‌تر
        small_factor_fail = sum(1 for N, p, q in failures if p < 50)
        medium_factor_fail = sum(1 for N, p, q in failures if 50 <= p < 200)
        large_factor_fail = sum(1 for N, p, q in failures if p >= 200)
        
        print(f"  فاکتور کوچک (<50): {small_factor_fail}")
        print(f"  فاکتور متوسط (50-200): {medium_factor_fail}")
        print(f"  فاکتور بزرگ (200+): {large_factor_fail}")
        
        # چند نمونه
        print(f"\nنمونه‌های ناموفق:")
        for N, p, q in failures[:10]:
            print(f"  N={N} = {p}×{q}")

def test_with_rsa_like():
    """تست اعداد شبیه RSA"""
    print(f"\n{'='*70}")
    print(f"  تست اعداد شبیه RSA")
    print(f"{'='*70}")
    
    # اعداد اول بزرگ‌تر
    import random
    random.seed(42)
    
    primes_4digit = [1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051,
                     1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109,
                     1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187,
                     1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249]
    
    test_cases = []
    for _ in range(100):
        p = random.choice(primes_4digit)
        q = random.choice(primes_4digit)
        if p != q:
            test_cases.append((p*q, min(p,q), max(p,q)))
    
    print(f"تعداد تست‌ها: {len(test_cases)}")
    
    success = 0
    fail = 0
    
    t0 = time.time()
    
    for N, p, q in test_cases:
        factor, cofactor = gcd_spectral_factor_v2(N, max_k=16384, num_peaks=500)
        
        if factor is not None and factor * cofactor == N:
            success += 1
        else:
            fail += 1
    
    elapsed = time.time() - t0
    
    print(f"\nنتایج:")
    print(f"  موفق: {success}")
    print(f"  ناموفق: {fail}")
    print(f"  درصد موفقیت: {100*success/len(test_cases):.1f}%")
    print(f"  زمان کل: {elapsed:.1f}s")
    print(f"  زمان هر تست: {elapsed/len(test_cases)*1000:.1f}ms")

if __name__ == "__main__":
    test_v2()
    test_with_rsa_like()
