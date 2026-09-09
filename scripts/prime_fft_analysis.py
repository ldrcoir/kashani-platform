#!/usr/bin/env python3
"""
تحلیل طیفی اعداد اول با تبدیل فوریه (FFT)
==========================================
ایده: اعداد اول رو به‌عنوان سیگنال باینری در نظر بگیریم
و با FFT تحلیل طیفی کنیم.

سیگنال: x[n] = 1 اگه n اول باشه، 0 در غیر این صورت
طول: N = 2^k

سپس FFT رو محاسبه می‌کنیم و:
1. طیف فرکانس رو بررسی کنیم
2. الگوهای پنهار رو پیدا کنیم
3. فرکانس‌های غالب رو شناسایی کنیم
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

# ============================================================
#  تولید اعداد اول با sieve
# ============================================================
def sieve_primes(n):
    """تولید اعداد اول تا n"""
    sieve = bytearray([1]) * (n + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n + 1, i):
                sieve[j] = 0
    return sieve

# ============================================================
#  ساخت سیگنال باینری اعداد اول
# ============================================================
def prime_signal(sieve, N):
    """ساخت سیگنال: x[n] = 1 اگه n اول، 0 در غیر این صورت"""
    signal = np.zeros(N, dtype=np.float64)
    for i in range(min(N, len(sieve))):
        if sieve[i]:
            signal[i] = 1.0
    return signal

# ============================================================
#  محاسبه FFT و تحلیل
# ============================================================
def analyze_spectrum(signal, N, title, save_path):
    """محاسبه FFT و رسم طیف"""
    # محاسبه FFT
    fft_result = np.fft.fft(signal)
    magnitude = np.abs(fft_result)
    power = magnitude**2
    
    # فرکانس‌ها
    freqs = np.fft.fftfreq(N, d=1.0)
    
    # فقط نیمه مثبت (به دلیل تقارن)
    half = N // 2
    freqs_pos = freqs[:half]
    mag_pos = magnitude[:half]
    power_pos = power[:half]
    
    # پیدا کردن فرکانس‌های غالب (peak)
    # حذف فرکانس 0 (DC component)
    mag_for_peaks = mag_pos.copy()
    mag_for_peaks[0] = 0
    
    # پیدا کردن 10 فرکانس غالب
    peak_indices = np.argsort(mag_for_peaks)[-10:][::-1]
    
    print(f"\n=== {title} ===")
    print(f"N = {N}")
    print(f"تعداد اعداد اول: {int(np.sum(signal))}")
    print(f"\n10 فرکانس غالب:")
    print(f"{'فرکانس':>15} {'دوره':>15} {'قدرت':>15}")
    print("-" * 50)
    
    for idx in peak_indices:
        freq = freqs_pos[idx]
        period = 1.0 / freq if freq > 0 else float('inf')
        mag = mag_pos[idx]
        print(f"{freq:>15.6f} {period:>15.2f} {mag:>15.2f}")
    
    # رسم نمودار
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    # سیگنال
    axes[0].plot(signal[:200], 'b-', linewidth=0.8)
    axes[0].set_title(f'سیگنال اعداد اول (200 نمونه اول) - N={N}')
    axes[0].set_xlabel('n')
    axes[0].set_ylabel('x[n]')
    axes[0].grid(True, alpha=0.3)
    
    # طیف قدرت (log scale)
    axes[1].semilogy(freqs_pos[1:], power_pos[1:], 'r-', linewidth=0.5)
    axes[1].set_title('طیف قدرت (Power Spectrum)')
    axes[1].set_xlabel('فرکانس')
    axes[1].set_ylabel('قدرت (log)')
    axes[1].grid(True, alpha=0.3)
    
    # فرکانس‌های غالب
    axes[2].bar(range(len(peak_indices)), mag_pos[peak_indices], color='green')
    axes[2].set_title('10 فرکانس غالب')
    axes[2].set_xlabel('اندیس')
    axes[2].set_ylabel('دامنه')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()
    print(f"نمودار ذخیره شد: {save_path}")
    
    return freqs_pos, mag_pos, peak_indices


# ============================================================
#  تحلیل فرکانس‌های اول
# ============================================================
def analyze_prime_frequencies():
    """تحلیل فرکانس‌های اعداد اول کوچک"""
    print("\n" + "=" * 70)
    print("  تحلیل فرکانس‌های اعداد اول")
    print("=" * 70)
    
    # اعداد اول کوچک
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
    
    print(f"\nاعداد اول کوچک: {small_primes}")
    
    # فاصله‌های بین اعداد اول متوالی
    gaps = [small_primes[i+1] - small_primes[i] for i in range(len(small_primes)-1)]
    print(f"فاصله‌ها: {gaps}")
    
    # میانگین فاصله
    avg_gap = np.mean(gaps)
    print(f"میانگین فاصله: {avg_gap:.2f}")
    
    # فرکانس تقریبی (1/میانگین فاصله)
    approx_freq = 1.0 / avg_gap
    print(f"فرکانس تقریبی: {approx_freq:.6f}")
    
    # بررسی الگوهای دوره‌ای
    print(f"\nبررسی الگوهای دوره‌ای:")
    for period in [2, 3, 4, 5, 6, 7, 8]:
        count = 0
        for p in small_primes:
            if (p - 2) % period == 0:  # اعداد اول فرد → p-2 زوج
                count += 1
        pct = 100 * count / len(small_primes)
        print(f"  دوره {period}: {count}/{len(small_primes)} ({pct:.1f}%) در p ≡ 2 (mod {period})")


# ============================================================
#  تحلیل برای N های مختلف
# ============================================================
def main():
    print("=" * 70)
    print("  تحلیل طیفی اعداد اول با FFT")
    print("=" * 70)
    
    # تحلیل فرکانس‌های اول
    analyze_prime_frequencies()
    
    # تحلیل برای N های مختلف (توان‌های 2)
    N_values = [256, 1024, 4096, 16384, 65536]
    
    results = {}
    
    for N in N_values:
        print(f"\n{'='*70}")
        print(f"  تحلیل برای N = {N}")
        print(f"{'='*70}")
        
        t0 = time.time()
        sieve = sieve_primes(N)
        signal = prime_signal(sieve, N)
        
        save_path = f"/home/z/my-project/download/prime_fft_N{N}.png"
        freqs, mags, peaks = analyze_spectrum(signal, N, f"اعداد اول تا {N}", save_path)
        
        results[N] = {
            'freqs': freqs,
            'mags': mags,
            'peaks': peaks
        }
        
        elapsed = time.time() - t0
        print(f"زمان: {elapsed:.2f}s")
    
    # ============================================================
    #  مقایسه فرکانس‌های غالب برای N های مختلف
    # ============================================================
    print(f"\n{'='*70}")
    print(f"  مقایسه فرکانس‌های غالب")
    print(f"{'='*70}")
    
    print(f"\n{'N':>10} | {'فرکانس غالب':>15} | {'دوره':>10} | {'قدرت':>10}")
    print("-" * 60)
    
    for N in N_values:
        peaks = results[N]['peaks']
        freqs = results[N]['freqs']
        mags = results[N]['mags']
        
        # فرکانس غالب (به جز DC)
        top_peak = peaks[0]
        freq = freqs[top_peak]
        period = 1.0 / freq if freq > 0 else 0
        mag = mags[top_peak]
        
        print(f"{N:>10} | {freq:>15.6f} | {period:>10.2f} | {mag:>10.2f}")
    
    # ============================================================
    #  تحلیل خاص: آیا فرکانس 1/ln(N) مشاهده می‌شه؟
    # ============================================================
    print(f"\n{'='*70}")
    print(f"  بررسی فرکانس نظری 1/ln(N)")
    print(f"{'='*70}")
    
    import math
    
    print(f"\nطبق قضیه اعداد اول، چگالی اعداد اول حول N برابر است با 1/ln(N)")
    print(f"پس فرکانس تقریبی اعداد اول = 1/ln(N)")
    print()
    
    print(f"{'N':>10} | {'فرکانس نظری 1/ln(N)':>20} | {'فرکانس غالب FFT':>20} | {'نسبت':>10}")
    print("-" * 70)
    
    for N in N_values:
        theoretical_freq = 1.0 / math.log(N)
        
        peaks = results[N]['peaks']
        freqs = results[N]['freqs']
        top_peak = peaks[0]
        fft_freq = freqs[top_peak]
        
        ratio = fft_freq / theoretical_freq if theoretical_freq > 0 else 0
        
        print(f"{N:>10} | {theoretical_freq:>20.6f} | {fft_freq:>20.6f} | {ratio:>10.3f}")
    
    # ============================================================
    #  نمودار مقایسه‌ای
    # ============================================================
    fig, axes = plt.subplots(len(N_values), 1, figsize=(14, 2*len(N_values)))
    
    for i, N in enumerate(N_values):
        freqs = results[N]['freqs']
        mags = results[N]['mags']
        
        axes[i].semilogy(freqs[1:], mags[1:], 'b-', linewidth=0.5)
        axes[i].set_title(f'طیف FFT اعداد اول - N={N}')
        axes[i].set_xlabel('فرکانس')
        axes[i].set_ylabel('دامنه (log)')
        axes[i].grid(True, alpha=0.3)
        
        # علامت‌گذاری فرکانس نظری
        theoretical_freq = 1.0 / math.log(N)
        axes[i].axvline(x=theoretical_freq, color='r', linestyle='--', alpha=0.7, 
                       label=f'1/ln(N) = {theoretical_freq:.4f}')
        axes[i].legend()
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/download/prime_fft_comparison.png', dpi=100, bbox_inches='tight')
    plt.close()
    print(f"\nنمودار مقایسه‌ای ذخیره شد: /home/z/my-project/download/prime_fft_comparison.png")


if __name__ == "__main__":
    main()
