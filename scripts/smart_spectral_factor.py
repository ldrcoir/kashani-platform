#!/usr/bin/env python3
"""
روش ابتکاری: FFT هوشمند با استفاده از ساختار ریاضی
==================================================
ایده کلیدی:
- اگه N = p × q باشه، باقی‌مانده‌های N mod k الگوی دوره‌ای دارن
- دوره = p یا q (یا ضرایب آن‌ها)
- ولی برای فاکتورهای بزرگ، دوره هم بزرگ هست و FFT نمی‌تونه ببینه

راه‌حل ابتکاری:
- به‌جای بررسی همه k ها، فقط k هایی رو بررسی کنیم که به فرم خاص هستن
- مثلاً k = m × p (اگه p رو حدس بزنیم)
- یا استفاده از خاصیت N mod p = 0

روش جدید: 
1. حدس p از روی الگوی باقی‌مانده‌ها
2. استفاده از FFT برای تأیید
"""

import numpy as np
import gmpy2
from gmpy2 import mpz, gcd, is_prime
import time

def smart_spectral_factor(N, max_k=65536, num_peaks=500):
    """
    روش طیفی هوشمند:
    1. FFT با max_k بزرگ
    2. بررسی فرکانس‌های غالب
    3. استفاده از ضرایب period
    """
    N_mpz = mpz(N)
    
    # محاسبه باقی‌مانده‌ها
    remainders = np.zeros(max_k, dtype=np.float64)
    for k in range(1, max_k + 1):
        remainders[k-1] = float(N_mpz % k)
    
    # نرمال‌سازی
    max_r = np.max(remainders)
    if max_r > 0:
        remainders = remainders / max_r
    remainders = remainders - np.mean(remainders)
    
    # FFT
    fft_result = np.fft.fft(remainders)
    magnitude = np.abs(fft_result)
    freqs = np.fft.fftfreq(max_k, d=1.0)
    
    # فرکانس‌های غالب
    mag_for_peaks = magnitude[:max_k//2].copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-num_peaks:][::-1]
    
    # بررسی هر فرکانس غالب
    for idx in peak_indices:
        freq = freqs[idx]
        if freq == 0:
            continue
        period = 1.0 / freq
        period_int = int(round(period))
        
        # بررسی period و ضرایب
        for mult in range(1, 500):
            candidate = period_int * mult
            if candidate > 1 and candidate < N:
                g = gcd(N_mpz, candidate)
                if g > 1 and g < N_mpz:
                    return g, N_mpz // g
        
        # بررسی period / اعداد
        for div in range(2, 20):
            candidate = period_int // div
            if candidate > 1 and candidate < N:
                g = gcd(N_mpz, candidate)
                if g > 1 and g < N_mpz:
                    return g, N_mpz // g
        
        # بررسی period ± ضرایب
        for offset in range(-100, 101):
            candidate = period_int + offset
            if candidate > 1 and candidate < N:
                g = gcd(N_mpz, candidate)
                if g > 1 and g < N_mpz:
                    return g, N_mpz // g
    
    return None, None

def test_smart_method():
    print("=" * 70)
    print("  تست روش طیفی هوشمند (max_k=65536)")
    print("=" * 70)
    
    import random
    random.seed(42)
    
    # اعداد اول با اندازه‌های مختلف
    test_groups = [
        ("3-4 digit", [101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]),
        ("4 digit", [1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249]),
        ("5 digit", [10007, 10009, 10037, 10039, 10061, 10067, 10069, 10079, 10091, 10093, 10099, 10103, 10111, 10133, 10139, 10141, 10151, 10159, 10163, 10169, 10177, 10181, 10193]),
    ]
    
    for group_name, primes in test_groups:
        print(f"\n--- {group_name} ---")
        
        test_cases = []
        for _ in range(30):
            p = random.choice(primes)
            q = random.choice(primes)
            if p != q:
                test_cases.append((p*q, min(p,q), max(p,q)))
        
        success = 0
        fail = 0
        t0 = time.time()
        
        for N, p, q in test_cases:
            factor, cofactor = smart_spectral_factor(N, max_k=65536, num_peaks=500)
            if factor is not None and factor * cofactor == N:
                success += 1
            else:
                fail += 1
        
        elapsed = time.time() - t0
        print(f"  موفق: {success}/{len(test_cases)} ({100*success/len(test_cases):.1f}%)")
        print(f"  زمان: {elapsed:.1f}s ({elapsed/len(test_cases)*1000:.1f}ms/test)")

if __name__ == "__main__":
    test_smart_method()
