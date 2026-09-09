#!/usr/bin/env python3
"""
تست: آیا FFT می‌تونه اعداد مرکب رو فاکتور کنه؟
============================================
ایده: اگه N = p × q باشه، شاید در طیف فرکانسی N
الگوی p یا q دیده بشه.

روش‌های تست:
1. FFT روی نمایش باینری N
2. FFT روی digits های N
3. FFT روی باقی‌مانده‌های N mod k
4. تحلیل طیفی باقی‌مانده‌ها
"""

import numpy as np
import gmpy2
from gmpy2 import mpz, is_prime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

# ============================================================
#  اعداد تست شناخته شده
# ============================================================
test_cases = [
    # (N, p, q, توضیح)
    (15, 3, 5, "ساده: 3 × 5"),
    (77, 7, 11, "ساده: 7 × 11"),
    (91, 7, 13, "ساده: 7 × 13"),
    (1001, 7, 143, "متوسط: 7 × 143 = 7 × 11 × 13"),
    (10403, 101, 103, "متوسط: 101 × 103"),
    (1000007, 7, 142858, "متوسط"),
    (9999991, 7, 1428570, "متوسط"),
    # اعداد بزرگ‌تر
    (1000000007, 1000000007, 1, "عدد اول"),
]

# ============================================================
#  روش 1: FFT روی نمایش باینری N
# ============================================================
def fft_binary_representation(N, max_bits=1024):
    """FFT روی نمایش باینری N"""
    binary = bin(N)[2:]  # حذف '0b'
    
    # pad to max_bits
    if len(binary) > max_bits:
        binary = binary[-max_bits:]
    else:
        binary = binary.zfill(max_bits)
    
    signal = np.array([int(b) for b in binary], dtype=np.float64)
    
    # FFT
    fft_result = np.fft.fft(signal)
    magnitude = np.abs(fft_result)
    power = magnitude**2
    
    # فرکانس‌ها
    freqs = np.fft.fftfreq(max_bits, d=1.0)
    half = max_bits // 2
    
    return freqs[:half], magnitude[:half], power[:half]

# ============================================================
#  روش 2: FFT روی digits ده‌دهی N
# ============================================================
def fft_digits(N, max_digits=512):
    """FFT روی digits ده‌دهی N"""
    digits = str(N)
    
    if len(digits) > max_digits:
        digits = digits[-max_digits:]
    else:
        digits = digits.zfill(max_digits)
    
    signal = np.array([int(d) for d in digits], dtype=np.float64)
    
    # FFT
    fft_result = np.fft.fft(signal)
    magnitude = np.abs(fft_result)
    power = magnitude**2
    
    freqs = np.fft.fftfreq(max_digits, d=1.0)
    half = max_digits // 2
    
    return freqs[:half], magnitude[:half], power[:half]

# ============================================================
#  روش 3: FFT روی باقی‌مانده‌های N mod k
# ============================================================
def fft_remainders(N, max_k=1024):
    """FFT روی باقی‌مانده‌های N mod k برای k = 1, 2, ..., max_k"""
    N_mpz = mpz(N)
    remainders = np.zeros(max_k, dtype=np.float64)
    
    for k in range(1, max_k + 1):
        remainders[k-1] = float(N_mpz % k)
    
    # نرمال‌سازی
    remainders = remainders / np.max(remainders)
    
    # FFT
    fft_result = np.fft.fft(remainders)
    magnitude = np.abs(fft_result)
    power = magnitude**2
    
    freqs = np.fft.fftfreq(max_k, d=1.0)
    half = max_k // 2
    
    return freqs[:half], magnitude[:half], power[:half]

# ============================================================
#  روش 4: بررسی آیا فاکتور در فرکانس‌ها دیده می‌شه
# ============================================================
def check_factor_in_spectrum(N, p, q):
    """بررسی آیا p یا q در فرکانس‌های غالب دیده می‌شه"""
    print(f"\nN = {N} = {p} × {q}")
    
    # روش 1: باینری
    freqs_b, mag_b, power_b = fft_binary_representation(N)
    
    # فرکانس‌های غالب
    mag_for_peaks = mag_b.copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-5:][::-1]
    
    print(f"\nروش باینری - 5 فرکانس غالب:")
    for idx in peak_indices:
        freq = freqs_b[idx]
        period = 1.0 / freq if freq > 0 else 0
        # بررسی آیا period به p یا q نزدیک هست
        close_to_p = abs(period - p) / p < 0.1 if p > 0 else False
        close_to_q = abs(period - q) / q < 0.1 if q > 0 else False
        marker = ""
        if close_to_p:
            marker += " ← نزدیک p!"
        if close_to_q:
            marker += " ← نزدیک q!"
        print(f"  فرکانس: {freq:.6f}, دوره: {period:.2f}{marker}")
    
    # روش 2: digits
    freqs_d, mag_d, power_d = fft_digits(N)
    
    mag_for_peaks = mag_d.copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-5:][::-1]
    
    print(f"\nروش digits - 5 فرکانس غالب:")
    for idx in peak_indices:
        freq = freqs_d[idx]
        period = 1.0 / freq if freq > 0 else 0
        close_to_p = abs(period - p) / p < 0.1 if p > 0 else False
        close_to_q = abs(period - q) / q < 0.1 if q > 0 else False
        marker = ""
        if close_to_p:
            marker += " ← نزدیک p!"
        if close_to_q:
            marker += " ← نزدیک q!"
        print(f"  فرکانس: {freq:.6f}, دوره: {period:.2f}{marker}")
    
    # روش 3: باقی‌مانده‌ها
    freqs_r, mag_r, power_r = fft_remainders(N)
    
    mag_for_peaks = mag_r.copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-5:][::-1]
    
    print(f"\nروش باقی‌مانده‌ها - 5 فرکانس غالب:")
    for idx in peak_indices:
        freq = freqs_r[idx]
        period = 1.0 / freq if freq > 0 else 0
        close_to_p = abs(period - p) / p < 0.1 if p > 0 else False
        close_to_q = abs(period - q) / q < 0.1 if q > 0 else False
        marker = ""
        if close_to_p:
            marker += " ← نزدیک p!"
        if close_to_q:
            marker += " ← نزدیک q!"
        print(f"  فرکانس: {freq:.6f}, دوره: {period:.2f}{marker}")

# ============================================================
#  روش 5: تحلیل طیفی برای پیدا کردن فاکتور
# ============================================================
def spectral_factorization_attempt(N):
    """تلاش برای فاکتوریزاسیون با تحلیل طیفی"""
    print(f"\n{'='*70}")
    print(f"  تلاش فاکتوریزاسیون طیفی N = {N}")
    print(f"{'='*70}")
    
    N_mpz = mpz(N)
    
    # روش: برای هر فرکانس غالب، دوره رو به‌عنوان کاندید فاکتور بررسی کن
    
    # 1. FFT روی باقی‌مانده‌ها
    freqs, mag, power = fft_remainders(N, max_k=2048)
    
    # فرکانس‌های غالب
    mag_for_peaks = mag.copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-20:][::-1]
    
    print(f"\nبررسی 20 فرکانس غالب به‌عنوان فاکتور کاندید:")
    
    candidates = []
    for idx in peak_indices:
        freq = freqs[idx]
        if freq == 0:
            continue
        period = 1.0 / freq
        
        # بررسی period و ضرایب آن
        for mult in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            candidate = int(round(period * mult))
            if candidate > 1 and candidate < N:
                if N_mpz % candidate == 0:
                    cofactor = N_mpz // candidate
                    if cofactor > 1:
                        candidates.append((candidate, cofactor, idx, mult))
                        print(f"  ✓✓✓ فاکتور پیدا شد! دوره={period:.2f}, mult={mult}")
                        print(f"      فاکتور: {candidate}")
                        print(f"      ضریب: {cofactor}")
                        return candidate, cofactor
    
    print(f"  ✗ هیچ فاکتوری پیدا نشد")
    return None, None

# ============================================================
#  روش 6: تحلیل خاص برای اعداد مرکب متوسط
# ============================================================
def analyze_composite_numbers():
    """تحلیل طیفی اعداد مرکب متوسط"""
    print(f"\n{'='*70}")
    print(f"  تحلیل طیفی اعداد مرکب")
    print(f"{'='*70}")
    
    # اعداد مرکب شناخته شده
    composites = [
        (15, 3, 5),
        (21, 3, 7),
        (35, 5, 7),
        (77, 7, 11),
        (91, 7, 13),
        (143, 11, 13),
        (187, 11, 17),
        (209, 11, 19),
        (221, 13, 17),
        (323, 17, 19),
        (437, 19, 23),
        (667, 23, 29),
        (899, 29, 31),
        (1147, 31, 37),
        (1517, 37, 41),
        (1763, 41, 43),
        (2021, 43, 47),
        (2491, 47, 53),
        (3127, 53, 59),
        (3599, 59, 61),
    ]
    
    print(f"\nتست {len(composites)} عدد مرکب:")
    print(f"{'N':>10} {'p':>6} {'q':>6} {'فاکتور پیدا شد؟':>20}")
    print("-" * 50)
    
    success_count = 0
    
    for N, p, q in composites:
        factor, cofactor = spectral_factorization_attempt(N)
        if factor is not None:
            success_count += 1
            print(f"{N:>10} {p:>6} {q:>6} {'✓ بله':>20}")
        else:
            print(f"{N:>10} {p:>6} {q:>6} {'✗ خیر':>20}")
    
    print(f"\nنتیجه: {success_count}/{len(composites)} موفق")
    print(f"درصد موفقیت: {100*success_count/len(composites):.1f}%")

# ============================================================
#  روش 7: تحلیل GCD با فرکانس‌ها
# ============================================================
def gcd_spectral_method(N):
    """
    روش ابتکاری: 
    1. FFT روی باقی‌مانده‌های N mod k
    2. فرکانس‌های غالب رو پیدا کن
    3. دوره‌ها رو به‌عنوان کاندید در نظر بگیر
    4. GCD(N, period) رو بررسی کن
    """
    print(f"\n{'='*70}")
    print(f"  روش GCD طیفی برای N = {N}")
    print(f"{'='*70}")
    
    N_mpz = mpz(N)
    
    # FFT روی باقی‌مانده‌ها
    max_k = 4096
    freqs, mag, power = fft_remainders(N, max_k)
    
    # فرکانس‌های غالب
    mag_for_peaks = mag.copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-50:][::-1]
    
    print(f"\nبررسی 50 فرکانس غالب:")
    
    for idx in peak_indices:
        freq = freqs[idx]
        if freq == 0:
            continue
        period = 1.0 / freq
        period_int = int(round(period))
        
        if period_int > 1 and period_int < N:
            # GCD
            g = gmpy2.gcd(N_mpz, period_int)
            if g > 1 and g < N_mpz:
                cofactor = N_mpz // g
                print(f"  ✓✓✓ فاکتور پیدا شد!")
                print(f"  دوره: {period_int}")
                print(f"  GCD(N, period) = {g}")
                print(f"  cofactor = {cofactor}")
                return g, cofactor
    
    print(f"  ✗ فاکتوری پیدا نشد")
    return None, None

# ============================================================
#  main
# ============================================================
def main():
    print("=" * 70)
    print("  تست: آیا FFT می‌تونه اعداد مرکب رو فاکتور کنه؟")
    print("=" * 70)
    
    # تست اعداد ساده
    for N, p, q, desc in test_cases[:5]:
        check_factor_in_spectrum(N, p, q)
    
    # تحلیل اعداد مرکب متوسط
    analyze_composite_numbers()
    
    # روش GCD طیفی
    print(f"\n{'='*70}")
    print(f"  روش GCD طیفی")
    print(f"{'='*70}")
    
    test_Ns = [77, 91, 143, 221, 667, 1147, 1763, 3599]
    for N in test_Ns:
        factor, cofactor = gcd_spectral_method(N)
        print()

if __name__ == "__main__":
    main()
