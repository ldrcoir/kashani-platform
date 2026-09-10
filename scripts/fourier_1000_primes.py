#!/usr/bin/env python3
"""
سری فوریه ۱۰۰۰ عدد اول + روش‌های ابتکاری
========================================
1. تولید ۱۰۰۰ عدد اول
2. محاسبه سری فوریه (DFT/FFT)
3. رسم شکل موج و طیف
4. روش‌های ابتکاری:
   - تحلیل هارمونیک‌ها
   - پیش‌بینی عدد اول بعدی
   - فاکتوریزاسیون طیفی
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import gmpy2
from gmpy2 import mpz, is_prime, gcd, isqrt, iroot
import time
import json
import os

# ============================================================
#  تولید ۱۰۰۰ عدد اول
# ============================================================
def generate_primes(n):
    """تولید n عدد اول"""
    primes = []
    candidate = 2
    while len(primes) < n:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 1
    return np.array(primes, dtype=np.float64)

# ============================================================
#  محاسبه سری فوریه
# ============================================================
def compute_fourier_series(signal, num_harmonics=50):
    """
    محاسبه سری فوریه:
    x(t) = a0/2 + Σ [an*cos(2πnt/T) + bn*sin(2πnt/T)]
    """
    N = len(signal)
    T = N  # دوره
    
    # ضرایب
    a0 = 2 * np.mean(signal)
    an = np.zeros(num_harmonics)
    bn = np.zeros(num_harmonics)
    
    t = np.arange(N)
    
    for n in range(1, num_harmonics + 1):
        cos_n = np.cos(2 * np.pi * n * t / T)
        sin_n = np.sin(2 * np.pi * n * t / T)
        an[n-1] = (2/N) * np.sum(signal * cos_n)
        bn[n-1] = (2/N) * np.sum(signal * sin_n)
    
    # توان هر هارمونیک
    power = (an**2 + bn**2) / 2
    
    # بازسازی سیگنال
    reconstructed = np.full(N, a0/2)
    for n in range(1, num_harmonics + 1):
        reconstructed += an[n-1] * np.cos(2 * np.pi * n * t / T)
        reconstructed += bn[n-1] * np.sin(2 * np.pi * n * t / T)
    
    return a0, an, bn, power, reconstructed

# ============================================================
#  رسم شکل‌ها
# ============================================================
def plot_fourier_analysis(primes, a0, an, bn, power, reconstructed, save_dir):
    """رسم شکل‌های تحلیل فوریه"""
    
    # شکل ۱: ۱۰۰۰ عدد اول و بازسازی فوریه
    fig, axes = plt.subplots(3, 1, figsize=(16, 12))
    
    # اعداد اول اصلی
    axes[0].plot(primes, 'b-', linewidth=0.8, label='اعداد اول')
    axes[0].set_title('۱۰۰۰ عدد اول پشت سر هم', fontsize=14)
    axes[0].set_xlabel('اندیس (n)')
    axes[0].set_ylabel('عدد اول')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # بازسازی با سری فوریه
    axes[1].plot(primes, 'b-', linewidth=0.5, alpha=0.5, label='اصلی')
    axes[1].plot(reconstructed, 'r-', linewidth=1.5, label=f'بازسازی ({len(an)} هارمونیک)')
    axes[1].set_title('بازسازی با سری فوریه', fontsize=14)
    axes[1].set_xlabel('اندیس (n)')
    axes[1].set_ylabel('مقدار')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # خطا
    error = primes - reconstructed
    axes[2].plot(error, 'g-', linewidth=0.5)
    axes[2].set_title('خطای بازسازی', fontsize=14)
    axes[2].set_xlabel('اندیس (n)')
    axes[2].set_ylabel('خطا')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{save_dir}/fourier_1000_primes.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    # شکل ۲: طیف توان هارمونیک‌ها
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    # طیف توان
    axes[0,0].bar(range(1, len(power)+1), power, color='red', alpha=0.7)
    axes[0,0].set_title('طیف توان هارمونیک‌ها', fontsize=14)
    axes[0,0].set_xlabel('شماره هارمونیک (n)')
    axes[0,0].set_ylabel('توان')
    axes[0,0].grid(True, alpha=0.3)
    axes[0,0].set_yscale('log')
    
    # ضرایب an
    axes[0,1].bar(range(1, len(an)+1), an, color='blue', alpha=0.7)
    axes[0,1].set_title('ضرایب an (cosine)', fontsize=14)
    axes[0,1].set_xlabel('n')
    axes[0,1].set_ylabel('an')
    axes[0,1].grid(True, alpha=0.3)
    
    # ضرایب bn
    axes[1,0].bar(range(1, len(bn)+1), bn, color='green', alpha=0.7)
    axes[1,0].set_title('ضرایب bn (sine)', fontsize=14)
    axes[1,0].set_xlabel('n')
    axes[1,0].set_ylabel('bn')
    axes[1,0].grid(True, alpha=0.3)
    
    # فاز
    phase = np.arctan2(bn, an)
    axes[1,1].scatter(range(1, len(phase)+1), phase, c='purple', alpha=0.7)
    axes[1,1].set_title('فاز هارمونیک‌ها', fontsize=14)
    axes[1,1].set_xlabel('n')
    axes[1,1].set_ylabel('فاز (رادیان)')
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{save_dir}/fourier_spectrum.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    # شکل ۳: شکل موج اصلی (موج)
    fig, axes = plt.subplots(2, 1, figsize=(16, 8))
    
    # ۱۰۰ عدد اول به‌عنوان شکل موج
    axes[0].plot(primes[:100], 'b-o', linewidth=2, markersize=3)
    axes[0].set_title('شکل موج ۱۰۰ عدد اول', fontsize=14)
    axes[0].set_xlabel('n')
    axes[0].set_ylabel('عدد اول')
    axes[0].grid(True, alpha=0.3)
    
    # فاصله‌ها به‌عنوان شکل موج
    gaps = np.diff(primes[:100])
    axes[1].plot(gaps, 'r-o', linewidth=2, markersize=3)
    axes[1].set_title('شکل موج فاصله‌های بین اعداد اول', fontsize=14)
    axes[1].set_xlabel('n')
    axes[1].set_ylabel('فاصله')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{save_dir}/prime_waveform.png', dpi=100, bbox_inches='tight')
    plt.close()

# ============================================================
#  روش ابتکاری ۱: پیش‌بینی عدد اول بعدی
# ============================================================
def predict_next_prime(primes, num_harmonics=20):
    """
    پیش‌بینی عدد اول بعدی با سری فوریه
    """
    N = len(primes)
    signal = primes.astype(np.float64)
    
    a0, an, bn, power, reconstructed = compute_fourier_series(signal, num_harmonics)
    
    # پیش‌بینی مقدار بعدی
    t_next = N
    prediction = a0 / 2
    for n in range(1, num_harmonics + 1):
        prediction += an[n-1] * np.cos(2 * np.pi * n * t_next / N)
        prediction += bn[n-1] * np.sin(2 * np.pi * n * t_next / N)
    
    # عدد اول واقعی بعدی
    actual_next = int(primes[-1])
    while True:
        actual_next += 1
        if is_prime(actual_next):
            break
    
    error = abs(prediction - actual_next)
    pct_error = 100 * error / actual_next
    
    return prediction, actual_next, error, pct_error

# ============================================================
#  روش ابتکاری ۲: فاکتوریزاسیون طیفی پیشرفته
# ============================================================
def spectral_factorization_innovative(N, max_k=65536):
    """
    روش ابتکاری: فاکتوریزاسیون با تحلیل طیفی پیشرفته
    
    ایده: 
    - اگه N = p × q، باقی‌مانده‌های N mod k الگوی دوره‌ای دارن
    - دوره = p یا q
    - با FFT دوره رو پیدا می‌کنیم
    - سپس با GCD فاکتور رو استخراج می‌کنیم
    
    بهبود:
    - بررسی دوره‌های کسری
    - استفاده از همبستگی متقابل
    - ترکیب با Fermat
    """
    N_mpz = mpz(N)
    
    # Trial Division سریع
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N_mpz % p == 0:
            return p, N_mpz // p, 'Trial', 0
    
    t0 = time.time()
    
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
    
    # پیدا کردن فرکانس‌های غالب
    mag_for_peaks = magnitude[:max_k//2].copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-500:][::-1]
    
    # روش ابتکاری ۱: بررسی period و ضرایب
    for idx in peak_indices:
        freq = freqs[idx]
        if freq == 0:
            continue
        period = 1.0 / freq
        period_int = int(round(period))
        
        # بررسی period × mult
        for mult in range(1, 500):
            candidate = period_int * mult
            if candidate > 1 and candidate < N:
                g = gcd(N_mpz, candidate)
                if g > 1 and g < N_mpz:
                    return g, N_mpz // g, 'FFT', time.time() - t0
        
        # بررسی period ± offset
        for offset in range(-500, 501):
            candidate = period_int + offset
            if candidate > 1 and candidate < N:
                g = gcd(N_mpz, candidate)
                if g > 1 and g < N_mpz:
                    return g, N_mpz // g, 'FFT', time.time() - t0
    
    # روش ابتکاری ۲: Fermat (اگه فاکتورها نزدیک باشن)
    a = isqrt(N_mpz)
    if a * a < N_mpz:
        a += 1
    
    for delta in range(100000):
        a_test = a + delta
        b_squared = a_test * a_test - N_mpz
        if b_squared >= 0:
            b, is_perfect = iroot(b_squared, 2)
            if is_perfect:
                f1 = a_test + b
                f2 = a_test - b
                if f1 > 1 and f2 > 1:
                    return f1, f2, 'Fermat', time.time() - t0
    
    return None, None, None, time.time() - t0

# ============================================================
#  روش ابتکاری ۳: تحلیل هارمونیک اعداد اول
# ============================================================
def harmonic_analysis_primes(primes):
    """
    تحلیل هارمونیک اعداد اول
    - پیدا کردن فرکانس‌های غالب
    - بررسی الگوهای پنهان
    """
    N = len(primes)
    signal = primes.astype(np.float64)
    
    # FFT
    fft_result = np.fft.fft(signal - np.mean(signal))
    magnitude = np.abs(fft_result)
    power = magnitude**2
    freqs = np.fft.fftfreq(N, d=1.0)
    
    # ۱۰ فرکانس غالب
    mag_for_peaks = magnitude[:N//2].copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-20:][::-1]
    
    print(f"\n۲۰ فرکانس غالب در طیف اعداد اول:")
    print(f"  {'فرکانس':>12} {'دوره':>10} {'توان':>15} {'نسبت':>10}")
    print("-" * 55)
    
    total_power = np.sum(power[1:N//2])
    
    for idx in peak_indices[:20]:
        freq = freqs[idx]
        period = 1.0 / freq if freq > 0 else float('inf')
        p = power[idx]
        ratio = p / total_power * 100
        print(f"  {freq:>12.6f} {period:>10.2f} {p:>15.2f} {ratio:>9.4f}%")
    
    return peak_indices, power

# ============================================================
#  روش ابتکاری ۴: فاکتوریزاسیون با استفاده از سری فوریه
# ============================================================
def fourier_based_factorization(N, num_primes=500):
    """
    روش ابتکاری: استفاده از سری فوریه اعداد اول برای فاکتوریزاسیون
    
    ایده:
    - تولید اعداد اول تا num_primes
    - محاسبه سری فوریه
    - استفاده از هارمونیک‌ها به‌عنوان کاندید فاکتور
    """
    N_mpz = mpz(N)
    
    # Trial
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N_mpz % p == 0:
            return p, N_mpz // p, 'Trial', 0
    
    t0 = time.time()
    
    # تولید اعداد اول
    primes = []
    candidate = 2
    while len(primes) < num_primes:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 1
    
    # بررسی اعداد اول به‌عنوان فاکتور
    for p in primes:
        if p >= N:
            break
        if N_mpz % p == 0:
            return p, N_mpz // p, 'Prime-list', time.time() - t0
    
    # محاسبه سری فوریه
    signal = np.array(primes, dtype=np.float64)
    a0, an, bn, power, _ = compute_fourier_series(signal, num_harmonics=50)
    
    # استفاده از هارمونیک‌ها به‌عنوان کاندید
    candidates = set()
    
    # a0
    candidates.add(int(abs(a0)))
    
    # an, bn
    for i in range(len(an)):
        candidates.add(int(abs(an[i])))
        candidates.add(int(abs(bn[i])))
        # ترکیب
        candidates.add(int(abs(an[i] + bn[i])))
        candidates.add(int(abs(an[i] - bn[i])))
    
    # بررسی کاندیدها
    for candidate in candidates:
        if candidate > 1 and candidate < N:
            g = gcd(N_mpz, candidate)
            if g > 1 and g < N_mpz:
                return g, N_mpz // g, 'Fourier', time.time() - t0
    
    # بررسی ضرایب × اعداد اول
    for p in primes[:100]:
        for i in range(min(20, len(an))):
            for candidate in [int(abs(an[i] * p)), int(abs(bn[i] * p))]:
                if candidate > 1 and candidate < N:
                    g = gcd(N_mpz, candidate)
                    if g > 1 and g < N_mpz:
                        return g, N_mpz // g, 'Fourier×Prime', time.time() - t0
    
    return None, None, None, time.time() - t0

# ============================================================
#  main
# ============================================================
def main():
    print("=" * 70)
    print("  سری فوریه ۱۰۰۰ عدد اول + روش‌های ابتکاری")
    print("=" * 70)
    
    save_dir = "/home/z/my-project/download"
    
    # ۱. تولید ۱۰۰۰ عدد اول
    print("\n۱. تولید ۱۰۰۰ عدد اول...")
    t0 = time.time()
    primes = generate_primes(1000)
    print(f"   زمان: {time.time()-t0:.2f}s")
    print(f"   اولین: {primes[0]}, آخرین: {primes[-1]}")
    
    # ۲. محاسبه سری فوریه
    print("\n۲. محاسبه سری فوریه (۵۰ هارمونیک)...")
    t0 = time.time()
    a0, an, bn, power, reconstructed = compute_fourier_series(primes, num_harmonics=50)
    print(f"   زمان: {time.time()-t0:.2f}s")
    print(f"   a0 = {a0:.2f}")
    print(f"   قوی‌ترین هارمونیک: n={np.argmax(power)+1}, توان={np.max(power):.2f}")
    
    # ۳. رسم شکل‌ها
    print("\n۳. رسم شکل‌ها...")
    plot_fourier_analysis(primes, a0, an, bn, power, reconstructed, save_dir)
    print(f"   شکل‌ها ذخیره شدند در {save_dir}/")
    
    # ۴. پیش‌بینی عدد اول بعدی
    print("\n۴. پیش‌بینی عدد اول بعدی...")
    prediction, actual, error, pct = predict_next_prime(primes, num_harmonics=20)
    print(f"   پیش‌بینی: {prediction:.2f}")
    print(f"   واقعی: {actual}")
    print(f"   خطا: {error:.2f} ({pct:.2f}%)")
    
    # ۵. تحلیل هارمونیک
    print("\n۵. تحلیل هارمونیک اعداد اول...")
    peak_indices, peak_power = harmonic_analysis_primes(primes)
    
    # ۶. تست فاکتوریزاسیون طیفی
    print("\n۶. تست فاکتوریزاسیون طیفی...")
    
    test_cases = [
        (77, 7, 11),
        (91, 7, 13),
        (143, 11, 13),
        (221, 13, 17),
        (667, 23, 29),
        (1147, 31, 37),
        (1763, 41, 43),
        (3599, 59, 61),
        (10002200057, 100003, 100019),
    ]
    
    print(f"\n{'N':>15} {'p':>10} {'q':>10} {'روش':>12} {'زمان':>8} {'موفق':>6}")
    print("-" * 65)
    
    for N, p, q in test_cases:
        f, c, method, elapsed = spectral_factorization_innovative(N)
        success = "✓" if f is not None and f * c == N else "✗"
        method_str = method or "ناموفق"
        print(f"{N:>15} {p:>10} {q:>10} {method_str:>12} {elapsed:>7.3f}s {success:>6}")
    
    # ۷. تست فاکتوریزاسیون مبتنی بر فوریه
    print(f"\n۷. فاکتوریزاسیون مبتنی بر سری فوریه...")
    
    print(f"\n{'N':>15} {'p':>10} {'q':>10} {'روش':>15} {'زمان':>8} {'موفق':>6}")
    print("-" * 68)
    
    for N, p, q in test_cases:
        f, c, method, elapsed = fourier_based_factorization(N)
        success = "✓" if f is not None and f * c == N else "✗"
        method_str = method or "ناموفق"
        print(f"{N:>15} {p:>10} {q:>10} {method_str:>15} {elapsed:>7.3f}s {success:>6}")
    
    # ۸. ذخیره داده‌ها
    print(f"\n۸. ذخیره داده‌ها...")
    data = {
        'num_primes': len(primes),
        'first_prime': int(primes[0]),
        'last_prime': int(primes[-1]),
        'a0': float(a0),
        'top_harmonics': [
            {
                'n': int(idx + 1),
                'an': float(an[idx]),
                'bn': float(bn[idx]),
                'power': float(power[idx])
            }
            for idx in np.argsort(power)[-10:][::-1]
        ],
        'prediction': {
            'predicted': float(prediction),
            'actual': int(actual),
            'error': float(error),
            'pct_error': float(pct)
        }
    }
    
    with open(f'{save_dir}/fourier_1000_primes_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    # ذخیره ۱۰۰۰ عدد اول
    np.savetxt(f'{save_dir}/first_1000_primes.txt', primes, fmt='%d')
    
    print(f"   داده‌ها ذخیره شدند:")
    print(f"   - {save_dir}/fourier_1000_primes_data.json")
    print(f"   - {save_dir}/first_1000_primes.txt")
    
    print(f"\n{'='*70}")
    print(f"  کامل شد!")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
