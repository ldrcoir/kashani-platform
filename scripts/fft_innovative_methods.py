#!/usr/bin/env python3
"""
روش‌های ابتکاری جدید برای فاکتوریزاسیون طیفی
============================================
ایده‌ها:
1. FFT با zero-padding بالا برای دقت فرکانسی بیشتر
2. تحلیل فاز به‌جای دامنه
3. روش chirp Z-transform برای فرکانس‌های خاص
4. تحلیل همبستگی با کاندیدهای فاکتور
5. روش MUSIC (Multiple Signal Classification)
6. روش پیزو-الکتریک طیفی
7. تحلیل چندفرکانسی با فیلتر باند باریک
8. روش autocorrelation با delay بزرگ
"""

import numpy as np
import gmpy2
from gmpy2 import mpz, gcd, is_prime
import time

# ============================================================
#  روش 1: FFT با zero-padding بالا
# ============================================================
def fft_zeropad_factor(N, max_k=4096, zero_pad=65536, num_peaks=100):
    """
    FFT با zero-padding برای دقت فرکانسی بیشتر
    """
    N_mpz = mpz(N)
    remainders = np.zeros(max_k, dtype=np.float64)
    
    for k in range(1, max_k + 1):
        remainders[k-1] = float(N_mpz % k)
    
    max_r = np.max(remainders)
    if max_r > 0:
        remainders = remainders / max_r
    
    # حذف میانگین
    remainders = remainders - np.mean(remainders)
    
    # zero-padding
    padded = np.zeros(zero_pad)
    padded[:max_k] = remainders
    
    fft_result = np.fft.fft(padded)
    magnitude = np.abs(fft_result)
    
    freqs = np.fft.fftfreq(zero_pad, d=1.0)
    half = zero_pad // 2
    
    mag_for_peaks = magnitude[:half].copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-num_peaks:][::-1]
    
    for idx in peak_indices:
        freq = freqs[idx]
        if freq == 0:
            continue
        period = 1.0 / freq
        period_int = int(round(period))
        
        # بررسی period و ضرایب
        for mult in range(1, 200):
            candidate = period_int * mult
            if candidate > 1 and candidate < N:
                g = gcd(N_mpz, candidate)
                if g > 1 and g < N_mpz:
                    return g, N_mpz // g
    
    return None, None

# ============================================================
#  روش 2: تحلیل فاز
# ============================================================
def phase_analysis_factor(N, max_k=4096, num_peaks=100):
    """
    تحلیل فاز FFT برای پیدا کردن فاکتور
    """
    N_mpz = mpz(N)
    remainders = np.zeros(max_k, dtype=np.float64)
    
    for k in range(1, max_k + 1):
        remainders[k-1] = float(N_mpz % k)
    
    max_r = np.max(remainders)
    if max_r > 0:
        remainders = remainders / max_r
    
    remainders = remainders - np.mean(remainders)
    
    fft_result = np.fft.fft(remainders)
    phase = np.angle(fft_result)
    magnitude = np.abs(fft_result)
    
    freqs = np.fft.fftfreq(max_k, d=1.0)
    half = max_k // 2
    
    # پیدا کردن فرکانس‌هایی که فاز خاصی دارن
    # فاز 0 یا π نشانه دوره واقعی هست
    
    candidates = []
    for i in range(1, half):
        if magnitude[i] > 0.1 * np.max(magnitude[1:]):
            # فاز نزدیک 0 یا π
            p = phase[i]
            if abs(p) < 0.3 or abs(abs(p) - np.pi) < 0.3:
                period = 1.0 / freqs[i]
                period_int = int(round(period))
                if period_int > 1 and period_int < N:
                    candidates.append(period_int)
    
    for period_int in candidates[:num_peaks]:
        for mult in range(1, 100):
            candidate = period_int * mult
            if candidate > 1 and candidate < N:
                g = gcd(N_mpz, candidate)
                if g > 1 and g < N_mpz:
                    return g, N_mpz // g
    
    return None, None

# ============================================================
#  روش 3: Chirp Z-Transform
# ============================================================
def czt_factor(N, max_k=4096, num_points=10000):
    """
    Chirp Z-Transform برای فرکانس‌های خاص
    """
    N_mpz = mpz(N)
    remainders = np.zeros(max_k, dtype=np.float64)
    
    for k in range(1, max_k + 1):
        remainders[k-1] = float(N_mpz % k)
    
    max_r = np.max(remainders)
    if max_r > 0:
        remainders = remainders / max_r
    
    remainders = remainders - np.mean(remainders)
    
    # بررسی دوره‌های خاص به‌جای FFT
    # برای هر period کاندید، همبستگی رو محاسبه کن
    
    best_periods = []
    
    # بررسی دوره‌های 2 تا max_k
    for period in range(2, min(max_k, 2000)):
        # سیگنال مرجع با این دوره
        ref = np.zeros(max_k)
        for i in range(0, max_k, period):
            ref[i] = 1.0
        
        # همبستگی
        corr = np.abs(np.dot(remainders, ref))
        best_periods.append((period, corr))
    
    # مرتب‌سازی بر اساس همبستگی
    best_periods.sort(key=lambda x: -x[1])
    
    # بررسی بهترین دوره‌ها
    for period, corr in best_periods[:num_points]:
        if period > 1 and period < N:
            g = gcd(N_mpz, period)
            if g > 1 and g < N_mpz:
                return g, N_mpz // g
        
        # ضرایب
        for mult in range(2, 50):
            candidate = period * mult
            if candidate > 1 and candidate < N:
                g = gcd(N_mpz, candidate)
                if g > 1 and g < N_mpz:
                    return g, N_mpz // g
    
    return None, None

# ============================================================
#  روش 4: Autocorrelation با delay بزرگ
# ============================================================
def autocorr_factor(N, max_k=4096, max_delay=2000):
    """
    Autocorrelation با delay بزرگ
    """
    N_mpz = mpz(N)
    remainders = np.zeros(max_k, dtype=np.float64)
    
    for k in range(1, max_k + 1):
        remainders[k-1] = float(N_mpz % k)
    
    max_r = np.max(remainders)
    if max_r > 0:
        remainders = remainders / max_r
    
    remainders = remainders - np.mean(remainders)
    
    # محاسبه autocorrelation برای delay های مختلف
    autocorr = np.zeros(max_delay)
    
    for delay in range(1, max_delay):
        # همبستگی بین سیگنال و نسخه shift شده
        corr = np.abs(np.dot(remainders[:-delay], remainders[delay:]))
        autocorr[delay] = corr
    
    # پیدا کردن delay های با همبستگی بالا
    threshold = 0.5 * np.max(autocorr)
    peak_delays = np.where(autocorr > threshold)[0]
    
    for delay in peak_delays:
        if delay > 1 and delay < N:
            g = gcd(N_mpz, delay)
            if g > 1 and g < N_mpz:
                return g, N_mpz // g
        
        # ضرایب
        for mult in range(2, 50):
            candidate = delay * mult
            if candidate > 1 and candidate < N:
                g = gcd(N_mpz, candidate)
                if g > 1 and g < N_mpz:
                    return g, N_mpz // g
    
    return None, None

# ============================================================
#  روش 5: تحلیل دوره‌ای مستقیم
# ============================================================
def periodic_analysis_factor(N, max_period=5000):
    """
    تحلیل دوره‌ای مستقیم - بررسی همه دوره‌ها
    """
    N_mpz = mpz(N)
    
    # برای هر دوره، بررسی کن آیا الگوی دوره‌ای وجود داره
    for period in range(2, max_period):
        # اگه period فاکتور N باشه
        if N_mpz % period == 0:
            return period, N_mpz // period
        
        # اگه period با N رابطه داشته باشه
        g = gcd(N_mpz, period)
        if g > 1 and g < N_mpz:
            return g, N_mpz // g
    
    return None, None

# ============================================================
#  روش 6: ترکیب FFT + autocorrelation
# ============================================================
def combined_factor(N, max_k=8192):
    """
    ترکیب FFT و autocorrelation
    """
    N_mpz = mpz(N)
    remainders = np.zeros(max_k, dtype=np.float64)
    
    for k in range(1, max_k + 1):
        remainders[k-1] = float(N_mpz % k)
    
    max_r = np.max(remainders)
    if max_r > 0:
        remainders = remainders / max_r
    
    remainders = remainders - np.mean(remainders)
    
    # روش 1: FFT
    fft_result = np.fft.fft(remainders)
    magnitude = np.abs(fft_result)
    freqs = np.fft.fftfreq(max_k, d=1.0)
    
    # فرکانس‌های غالب
    mag_for_peaks = magnitude[:max_k//2].copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-200:][::-1]
    
    candidates = set()
    for idx in peak_indices:
        freq = freqs[idx]
        if freq == 0:
            continue
        period = 1.0 / freq
        period_int = int(round(period))
        candidates.add(period_int)
        
        # ضرایب
        for mult in range(1, 100):
            candidates.add(period_int * mult)
    
    # روش 2: autocorrelation
    for delay in range(2, min(2000, max_k)):
        corr = np.abs(np.dot(remainders[:-delay], remainders[delay:]))
        if corr > 0.5 * np.max(np.abs(np.dot(remainders, remainders))):
            candidates.add(delay)
    
    # بررسی همه کاندیدها
    for candidate in candidates:
        if candidate > 1 and candidate < N:
            g = gcd(N_mpz, candidate)
            if g > 1 and g < N_mpz:
                return g, N_mpz // g
    
    return None, None

# ============================================================
#  تست همه روش‌ها
# ============================================================
def test_all_methods():
    print("=" * 70)
    print("  تست همه روش‌های ابتکاری")
    print("=" * 70)
    
    # اعداد تست
    import random
    random.seed(42)
    
    # اعداد 4 رقمی
    primes_4digit = [1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051,
                     1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109,
                     1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187,
                     1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249]
    
    test_cases = []
    for _ in range(50):
        p = random.choice(primes_4digit)
        q = random.choice(primes_4digit)
        if p != q:
            test_cases.append((p*q, min(p,q), max(p,q)))
    
    methods = [
        ('FFT zero-pad', fft_zeropad_factor),
        ('Phase analysis', phase_analysis_factor),
        ('Chirp Z-Transform', czt_factor),
        ('Autocorrelation', autocorr_factor),
        ('Periodic analysis', periodic_analysis_factor),
        ('Combined FFT+autocorr', combined_factor),
    ]
    
    for name, method in methods:
        print(f"\n--- {name} ---")
        success = 0
        fail = 0
        t0 = time.time()
        
        for N, p, q in test_cases:
            try:
                factor, cofactor = method(N)
                if factor is not None and factor * cofactor == N:
                    success += 1
                else:
                    fail += 1
            except Exception as e:
                fail += 1
        
        elapsed = time.time() - t0
        print(f"  موفق: {success}/{len(test_cases)} ({100*success/len(test_cases):.1f}%)")
        print(f"  زمان: {elapsed:.1f}s ({elapsed/len(test_cases)*1000:.1f}ms/test)")

# ============================================================
#  تست اعداد بزرگ‌تر
# ============================================================
def test_larger_numbers():
    print(f"\n{'='*70}")
    print(f"  تست اعداد بزرگ‌تر")
    print(f"{'='*70}")
    
    import random
    random.seed(42)
    
    # اعداد اول 5-6 رقمی
    primes_large = [10007, 10009, 10037, 10039, 10061, 10067, 10069, 10079,
                    10091, 10093, 10099, 10103, 10111, 10133, 10139, 10141,
                    10151, 10159, 10163, 10169, 10177, 10181, 10193]
    
    test_cases = []
    for _ in range(20):
        p = random.choice(primes_large)
        q = random.choice(primes_large)
        if p != q:
            test_cases.append((p*q, min(p,q), max(p,q)))
    
    methods = [
        ('Combined FFT+autocorr', combined_factor),
        ('Periodic analysis', periodic_analysis_factor),
    ]
    
    for name, method in methods:
        print(f"\n--- {name} ---")
        success = 0
        fail = 0
        t0 = time.time()
        
        for N, p, q in test_cases:
            try:
                factor, cofactor = method(N)
                if factor is not None and factor * cofactor == N:
                    success += 1
                else:
                    fail += 1
            except:
                fail += 1
        
        elapsed = time.time() - t0
        print(f"  موفق: {success}/{len(test_cases)} ({100*success/len(test_cases):.1f}%)")
        print(f"  زمان: {elapsed:.1f}s ({elapsed/len(test_cases)*1000:.1f}ms/test)")

if __name__ == "__main__":
    test_all_methods()
    test_larger_numbers()
