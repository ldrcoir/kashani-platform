#!/usr/bin/env python3
"""
تحلیل پیشرفته طیفی اعداد اول
============================
روش‌های مختلف:
1. FFT روی خود اعداد اول (نه باینری)
2. FFT روی فاصله‌های بین اعداد اول
3. FFT روی log اعداد اول
4. تحلیل موجک (Wavelet)
5. تبدیل هیلبرت-هوانگ (HHT)
6. تحلیل چندفرکانسی (Multi-taper)
7. تبدیل زیمن-فرکشنال (Z-transform)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math
import time
from scipy import signal as scipy_signal
from scipy.fft import fft, fftfreq

# ============================================================
#  تولید اعداد اول
# ============================================================
def sieve_primes(n):
    sieve = bytearray([1]) * (n + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n + 1, i):
                sieve[j] = 0
    return sieve

def get_primes(n):
    sieve = sieve_primes(n)
    return np.array([i for i in range(n+1) if sieve[i]], dtype=np.float64)

# ============================================================
#  1. FFT روی خود اعداد اول
# ============================================================
def fft_on_primes_themselves():
    print("=" * 70)
    print("  1. FFT روی خود اعداد اول")
    print("=" * 70)
    
    N = 10**5
    primes = get_primes(N)
    print(f"تعداد اعداد اول تا {N}: {len(primes)}")
    
    # روش 1: FFT روی خود اعداد اول
    print("\nروش 1: FFT روی خود اعداد اول")
    fft_primes = fft(primes)
    mag = np.abs(fft_primes)
    power = mag**2
    
    half = len(primes) // 2
    freqs = fftfreq(len(primes), d=1.0)[:half]
    mag_pos = mag[:half]
    power_pos = power[:half]
    
    # فرکانس‌های غالب
    mag_for_peaks = mag_pos.copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-10:][::-1]
    
    print(f"\n10 فرکانس غالب (FFT روی اعداد اول):")
    print(f"  {'فرکانس':>12} {'دوره':>10} {'دامنه':>12}")
    for idx in peak_indices:
        freq = freqs[idx]
        period = 1.0 / freq if freq > 0 else float('inf')
        print(f"  {freq:>12.6f} {period:>10.2f} {mag_pos[idx]:>12.2f}")
    
    # رسم
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # خود اعداد اول
    axes[0,0].plot(primes[:200], 'b-', linewidth=0.8)
    axes[0,0].set_title('اعداد اول (200 عدد اول)')
    axes[0,0].set_xlabel('اندیس')
    axes[0,0].set_ylabel('عدد اول')
    axes[0,0].grid(True, alpha=0.3)
    
    # طیف قدرت
    limit = 200
    axes[0,1].semilogy(freqs[1:limit], power_pos[1:limit], 'r-', linewidth=0.5)
    axes[0,1].set_title('طیف قدرت FFT اعداد اول')
    axes[0,1].set_xlabel('فرکانس')
    axes[0,1].set_ylabel('قدرت (log)')
    axes[0,1].grid(True, alpha=0.3)
    
    # روش 2: FFT روی log اعداد اول
    print("\nروش 2: FFT روی log اعداد اول")
    log_primes = np.log(primes)
    fft_log = fft(log_primes)
    mag_log = np.abs(fft_log)
    power_log = mag_log**2
    
    # log_primes رو رسم کن
    axes[1,0].plot(log_primes[:200], 'g-', linewidth=0.8)
    axes[1,0].set_title('log(اعداد اول) (200 عدد اول)')
    axes[1,0].set_xlabel('اندیس')
    axes[1,0].set_ylabel('log(عدد اول)')
    axes[1,0].grid(True, alpha=0.3)
    
    axes[1,1].semilogy(freqs[1:limit], power_log[1:limit], 'm-', linewidth=0.5)
    axes[1,1].set_title('طیف قدرت FFT log اعداد اول')
    axes[1,1].set_xlabel('فرکانس')
    axes[1,1].set_ylabel('قدرت (log)')
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/download/fft_on_primes_themselves.png', dpi=100, bbox_inches='tight')
    plt.close()
    print(f"\nنمودار ذخیره شد: /home/z/my-project/download/fft_on_primes_themselves.png")

# ============================================================
#  2. FFT روی فاصله‌های بین اعداد اول
# ============================================================
def fft_on_prime_gaps():
    print("\n" + "=" * 70)
    print("  2. FFT روی فاصله‌های بین اعداد اول")
    print("=" * 70)
    
    N = 10**6
    primes = get_primes(N)
    gaps = np.diff(primes)
    
    print(f"تعداد فاصله‌ها: {len(gaps)}")
    print(f"میانگین فاصله: {np.mean(gaps):.2f}")
    print(f"انحراف معیار: {np.std(gaps):.2f}")
    
    # FFT روی فاصله‌ها
    N_fft = 2**17  # 131072
    gaps_trunc = gaps[:N_fft]
    
    fft_gaps = fft(gaps_trunc - np.mean(gaps_trunc))  # حذف DC
    mag = np.abs(fft_gaps)
    power = mag**2
    
    half = N_fft // 2
    freqs = fftfreq(N_fft, d=1.0)[:half]
    mag_pos = mag[:half]
    power_pos = power[:half]
    
    # فرکانس‌های غالب
    mag_for_peaks = mag_pos.copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-10:][::-1]
    
    print(f"\n10 فرکانس غالب در فاصله‌ها:")
    print(f"  {'فرکانس':>12} {'دوره':>10} {'دامنه':>12}")
    for idx in peak_indices:
        freq = freqs[idx]
        period = 1.0 / freq if freq > 0 else float('inf')
        print(f"  {freq:>12.6f} {period:>10.2f} {mag_pos[idx]:>12.2f}")
    
    # رسم
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # فاصله‌ها
    axes[0,0].plot(gaps_trunc[:500], 'b-', linewidth=0.8)
    axes[0,0].set_title('فاصله‌های بین اعداد اول (500 فاصله اول)')
    axes[0,0].set_xlabel('اندیس')
    axes[0,0].set_ylabel('فاصله')
    axes[0,0].grid(True, alpha=0.3)
    
    # هیستوگرام
    axes[0,1].hist(gaps, bins=range(0, 80), color='green', alpha=0.7, edgecolor='black')
    axes[0,1].set_title('توزیع فاصله‌ها')
    axes[0,1].set_xlabel('فاصله')
    axes[0,1].set_ylabel('تعداد')
    axes[0,1].grid(True, alpha=0.3)
    
    # طیف قدرت
    limit = 300
    axes[1,0].semilogy(freqs[1:limit], power_pos[1:limit], 'r-', linewidth=0.5)
    axes[1,0].set_title(f'طیف قدرت FFT فاصله‌ها (اولین {limit} فرکانس)')
    axes[1,0].set_xlabel('فرکانس')
    axes[1,0].set_ylabel('قدرت (log)')
    axes[1,0].grid(True, alpha=0.3)
    
    # علامت‌گذاری فرکانس‌های خاص
    for frac, label in [(1/6, '1/6'), (1/2, '1/2'), (1/3, '1/3'), (1/30, '1/30')]:
        axes[1,0].axvline(x=frac, color='g', linestyle='--', alpha=0.7)
        axes[1,0].text(frac, axes[1,0].get_ylim()[1]*0.5, label, color='green', fontsize=9)
    
    # فاز
    phase = np.angle(fft_gaps[:half])
    axes[1,1].plot(freqs[1:limit], phase[1:limit], 'm-', linewidth=0.5)
    axes[1,1].set_title('فاز FFT فاصله‌ها')
    axes[1,1].set_xlabel('فرکانس')
    axes[1,1].set_ylabel('فاز (رادیان)')
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/download/fft_on_prime_gaps.png', dpi=100, bbox_inches='tight')
    plt.close()
    print(f"\nنمودار ذخیره شد: /home/z/my-project/download/fft_on_prime_gaps.png")

# ============================================================
#  3. تحلیل موجک (Wavelet)
# ============================================================
def wavelet_analysis():
    print("\n" + "=" * 70)
    print("  3. تحلیل موجک (Wavelet) اعداد اول")
    print("=" * 70)
    
    N = 10**4
    sieve = sieve_primes(N)
    signal_binary = np.zeros(N, dtype=np.float64)
    for i in range(N):
        if sieve[i]:
            signal_binary[i] = 1.0
    
    # محاسبه موجک پیوسته (CWT) با روش دستی
    print("محاسبه CWT با موجک Morlet (روش دستی)...")
    
    widths = np.arange(1, 31)  # مقیاس‌های 1 تا 30
    
    # محاسبه CWT با روش کانولوشن
    cwt_mat = np.zeros((len(widths), N), dtype=complex)
    for i, w in enumerate(widths):
        # موجک Morlet: exp(-t²/2) * exp(i*ω*t)
        t = np.arange(-3*w, 3*w+1) / w
        wavelet = np.exp(-t**2/2) * np.exp(1j*5*t) / np.sqrt(w)
        cwt_mat[i] = np.convolve(signal_binary, wavelet, mode='same')
    
    print(f"شکل ماتریس CWT: {cwt_mat.shape}")
    
    # توان در هر مقیاس
    power_per_scale = np.sum(np.abs(cwt_mat)**2, axis=1)
    
    print(f"\nتوان در هر مقیاس (دوره تقریبی):")
    print(f"  {'مقیاس':>8} {'دوره تقریبی':>15} {'توان':>15}")
    for i, w in enumerate(widths):
        period = w  # تقریبی
        print(f"  {w:>8} {period:>15} {power_per_scale[i]:>15.2f}")
    
    # مقیاس با بیشترین توان
    max_scale_idx = np.argmax(power_per_scale)
    print(f"\nمقیاس با بیشترین توان: {widths[max_scale_idx]} (دوره ~{widths[max_scale_idx]})")
    
    # رسم
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # سیگنال
    axes[0,0].plot(signal_binary[:500], 'b-', linewidth=0.8)
    axes[0,0].set_title('سیگنال اعداد اول (500 نمونه)')
    axes[0,0].set_xlabel('n')
    axes[0,0].set_ylabel('x[n]')
    axes[0,0].grid(True, alpha=0.3)
    
    # ماتریس CWT
    im = axes[0,1].imshow(np.abs(cwt_mat), aspect='auto', cmap='viridis',
                          extent=[0, N, widths[-1], widths[0]])
    axes[0,1].set_title('ماتریس CWT (|W(n, scale)|)')
    axes[0,1].set_xlabel('n')
    axes[0,1].set_ylabel('مقیاس')
    plt.colorbar(im, ax=axes[0,1])
    
    # توان در هر مقیاس
    axes[1,0].bar(widths, power_per_scale, color='green', alpha=0.7)
    axes[1,0].set_title('توان در هر مقیاس')
    axes[1,0].set_xlabel('مقیاس (دوره تقریبی)')
    axes[1,0].set_ylabel('توان')
    axes[1,0].grid(True, alpha=0.3)
    
    # علامت‌گذاری دوره‌های خاص
    for period in [6, 30, 210]:
        if period <= widths[-1]:
            axes[1,0].axvline(x=period, color='r', linestyle='--', alpha=0.7)
            axes[1,0].text(period, axes[1,0].get_ylim()[1]*0.9, str(period), 
                          color='red', fontsize=10, ha='center')
    
    # طیف زمان-فرکانس (برای 1000 نمونه اول)
    cwt_subset = np.abs(cwt_mat[:, :1000])
    im2 = axes[1,1].imshow(cwt_subset, aspect='auto', cmap='inferno',
                           extent=[0, 1000, widths[-1], widths[0]])
    axes[1,1].set_title('طیف زمان-فرکانس (1000 نمونه اول)')
    axes[1,1].set_xlabel('n')
    axes[1,1].set_ylabel('مقیاس')
    plt.colorbar(im2, ax=axes[1,1])
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/download/wavelet_analysis.png', dpi=100, bbox_inches='tight')
    plt.close()
    print(f"\nنمودار ذخیره شد: /home/z/my-project/download/wavelet_analysis.png")

# ============================================================
#  4. تحلیل چندفرکانسی (Multi-taper)
# ============================================================
def multitaper_analysis():
    print("\n" + "=" * 70)
    print("  4. تحلیل چندفرکانسی (Multi-taper)")
    print("=" * 70)
    
    N = 10**5
    sieve = sieve_primes(N)
    signal = np.zeros(N, dtype=np.float64)
    for i in range(N):
        if sieve[i]:
            signal[i] = 1.0
    
    # حذف میانگین
    signal = signal - np.mean(signal)
    
    # روش ساده: استفاده از چند پنجره متفاوت
    print("استفاده از پنجره‌های متفاوت (Hann, Hamming, Blackman)...")
    
    windows = {
        'Hann': np.hanning(N),
        'Hamming': np.hamming(N),
        'Blackman': np.blackman(N),
    }
    
    fig, axes = plt.subplots(len(windows)+1, 1, figsize=(14, 12))
    
    # بدون پنجره
    fft_plain = fft(signal)
    power_plain = np.abs(fft_plain)**2
    freqs = fftfreq(N, d=1.0)[:N//2]
    
    limit = 300
    axes[0].semilogy(freqs[1:limit], power_plain[1:limit], 'b-', linewidth=0.5)
    axes[0].set_title('طیف قدرت (بدون پنجره)')
    axes[0].set_xlabel('فرکانس')
    axes[0].set_ylabel('قدرت (log)')
    axes[0].grid(True, alpha=0.3)
    
    # با پنجره‌های مختلف
    for i, (name, window) in enumerate(windows.items(), 1):
        signal_windowed = signal * window
        fft_windowed = fft(signal_windowed)
        power_windowed = np.abs(fft_windowed)**2
        
        axes[i].semilogy(freqs[1:limit], power_windowed[1:limit], 'r-', linewidth=0.5)
        axes[i].set_title(f'طیف قدرت (پنجره {name})')
        axes[i].set_xlabel('فرکانس')
        axes[i].set_ylabel('قدرت (log)')
        axes[i].grid(True, alpha=0.3)
        
        # پیدا کردن فرکانس‌های غالب
        power_pos = power_windowed[:N//2]
        power_for_peaks = power_pos.copy()
        power_for_peaks[0] = 0
        peak_indices = np.argsort(power_for_peaks)[-5:][::-1]
        
        print(f"\n{name} - 5 فرکانس غالب:")
        for idx in peak_indices:
            freq = freqs[idx]
            period = 1.0 / freq if freq > 0 else 0
            print(f"  فرکانس: {freq:.6f}, دوره: {period:.2f}")
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/download/multitaper_analysis.png', dpi=100, bbox_inches='tight')
    plt.close()
    print(f"\nنمودار ذخیره شد: /home/z/my-project/download/multitaper_analysis.png")

# ============================================================
#  5. تحلیل طیفی با روش Welch
# ============================================================
def welch_psd_analysis():
    print("\n" + "=" * 70)
    print("  5. تحلیل طیفی با روش Welch")
    print("=" * 70)
    
    N = 10**5
    sieve = sieve_primes(N)
    signal = np.zeros(N, dtype=np.float64)
    for i in range(N):
        if sieve[i]:
            signal[i] = 1.0
    
    # روش Welch
    print("محاسبه PSD با روش Welch...")
    
    # پارامترهای مختلف
    nperseg_values = [1024, 4096, 16384]
    
    fig, axes = plt.subplots(len(nperseg_values), 1, figsize=(14, 3*len(nperseg_values)))
    
    for i, nperseg in enumerate(nperseg_values):
        freqs_w, psd_w = scipy_signal.welch(signal, fs=1.0, nperseg=nperseg)
        
        limit = 300
        axes[i].semilogy(freqs_w[1:limit], psd_w[1:limit], 'b-', linewidth=0.8)
        axes[i].set_title(f'PSD Welch (nperseg={nperseg})')
        axes[i].set_xlabel('فرکانس')
        axes[i].set_ylabel('PSD (log)')
        axes[i].grid(True, alpha=0.3)
        
        # علامت‌گذاری فرکانس‌های خاص
        for frac, label in [(1/6, '1/6'), (1/30, '1/30'), (1/210, '1/210')]:
            axes[i].axvline(x=frac, color='r', linestyle='--', alpha=0.5)
            axes[i].text(frac, axes[i].get_ylim()[1]*0.5, label, 
                        color='red', fontsize=8, ha='center')
        
        # پیدا کردن فرکانس‌های غالب
        psd_for_peaks = psd_w.copy()
        psd_for_peaks[0] = 0
        peak_indices = np.argsort(psd_for_peaks)[-5:][::-1]
        
        print(f"\nnperseg={nperseg} - 5 فرکانس غالب:")
        for idx in peak_indices:
            freq = freqs_w[idx]
            period = 1.0 / freq if freq > 0 else 0
            print(f"  فرکانس: {freq:.6f}, دوره: {period:.2f}, PSD: {psd_w[idx]:.4f}")
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/download/welch_psd_analysis.png', dpi=100, bbox_inches='tight')
    plt.close()
    print(f"\nنمودار ذخیره شد: /home/z/my-project/download/welch_psd_analysis.png")

# ============================================================
#  6. تحلیل همبستگی متقابل (Cross-correlation)
# ============================================================
def cross_correlation_analysis():
    print("\n" + "=" * 70)
    print("  6. تحلیل همبستگی متقابل")
    print("=" * 70)
    
    N = 10**5
    sieve = sieve_primes(N)
    signal = np.zeros(N, dtype=np.float64)
    for i in range(N):
        if sieve[i]:
            signal[i] = 1.0
    
    # ساخت سیگنال‌های مرجع با دوره‌های خاص
    print("محاسبه همبستگی متقابل با سیگنال‌های مرجع...")
    
    periods = [2, 3, 5, 6, 7, 10, 14, 30, 60, 210, 2310]
    
    print(f"\n{'دوره':>8} {'همبستگی ماکزیمم':>20} {'نرمال‌شده':>15}")
    print("-" * 50)
    
    correlations = []
    for period in periods:
        # سیگنال مرجع: 1 در موقعیت‌های 0, period, 2*period, ...
        ref_signal = np.zeros(N)
        for i in range(0, N, period):
            ref_signal[i] = 1.0
        
        # cross-correlation
        corr = np.correlate(signal - np.mean(signal), ref_signal - np.mean(ref_signal), mode='full')
        
        # پیدا کردن ماکزیمم
        max_corr = np.max(np.abs(corr))
        
        # نرمال‌سازی
        norm_factor = np.sqrt(np.sum((signal - np.mean(signal))**2) * np.sum((ref_signal - np.mean(ref_signal))**2))
        norm_corr = max_corr / norm_factor if norm_factor > 0 else 0
        
        correlations.append((period, max_corr, norm_corr))
        print(f"{period:>8} {max_corr:>20.2f} {norm_corr:>15.6f}")
    
    # رسم
    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    
    periods_list = [c[0] for c in correlations]
    norm_corrs = [c[2] for c in correlations]
    
    axes[0].bar(range(len(periods_list)), norm_corrs, color='green', alpha=0.7)
    axes[0].set_xticks(range(len(periods_list)))
    axes[0].set_xticklabels(periods_list)
    axes[0].set_title('همبستگی متقابل نرمال‌شده با دوره‌های مختلف')
    axes[0].set_xlabel('دوره')
    axes[0].set_ylabel('همبستگی نرمال‌شده')
    axes[0].grid(True, alpha=0.3)
    
    # همبستگی برای دوره 6
    ref_signal_6 = np.zeros(N)
    for i in range(0, N, 6):
        ref_signal_6[i] = 1.0
    
    corr_6 = np.correlate(signal - np.mean(signal), ref_signal_6 - np.mean(ref_signal_6), mode='full')
    
    # فقط lags مثبت
    half = len(corr_6) // 2
    lags = np.arange(-100, 101)
    corr_subset = corr_6[half-100:half+101]
    
    axes[1].plot(lags, corr_subset, 'b-', linewidth=0.8)
    axes[1].set_title('همبستگی متقابل با دوره 6 (lags -100 تا 100)')
    axes[1].set_xlabel('lag')
    axes[1].set_ylabel('همبستگی')
    axes[1].grid(True, alpha=0.3)
    
    # علامت‌گذاری lags خاص
    for lag in [0, 6, 12, -6, -12]:
        if lag >= -100 and lag <= 100:
            axes[1].axvline(x=lag, color='r', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/download/cross_correlation_analysis.png', dpi=100, bbox_inches='tight')
    plt.close()
    print(f"\nنمودار ذخیره شد: /home/z/my-project/download/cross_correlation_analysis.png")

# ============================================================
#  main
# ============================================================
def main():
    print("=" * 70)
    print("  تحلیل پیشرفته طیفی اعداد اول")
    print("=" * 70)
    
    # 1. FFT روی خود اعداد اول
    fft_on_primes_themselves()
    
    # 2. FFT روی فاصله‌ها
    fft_on_prime_gaps()
    
    # 3. تحلیل موجک
    wavelet_analysis()
    
    # 4. تحلیل چندفرکانسی
    multitaper_analysis()
    
    # 5. روش Welch
    welch_psd_analysis()
    
    # 6. همبستگی متقابل
    cross_correlation_analysis()
    
    print("\n" + "=" * 70)
    print("  تحلیل پیشرفته کامل شد!")
    print("=" * 70)

if __name__ == "__main__":
    main()
