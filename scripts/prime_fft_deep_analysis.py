#!/usr/bin/env python3
"""
تحلیل عمیق‌تر طیفی اعداد اول
============================
1. تحلیل برای N بزرگ‌تر (تا 2^20)
2. تحلیل فاصله‌های بین اعداد اول (prime gaps)
3. تبدیل موجک (Wavelet)
4. تحلیل autocorrelation
5. بررسی الگوهای پنهان
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math
import time

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
    return [i for i in range(n+1) if sieve[i]]

# ============================================================
#  1. تحلیل طیفی برای N بزرگ‌تر
# ============================================================
def analyze_large_N():
    print("=" * 70)
    print("  1. تحلیل طیفی برای N بزرگ‌تر")
    print("=" * 70)
    
    N_values = [2**16, 2**18, 2**20]  # 65536, 262144, 1048576
    results = {}
    
    for N in N_values:
        print(f"\nN = {N} ({N:,})")
        t0 = time.time()
        
        sieve = sieve_primes(N)
        signal = np.zeros(N, dtype=np.float64)
        for i in range(N):
            if sieve[i]:
                signal[i] = 1.0
        
        prime_count = int(np.sum(signal))
        print(f"  تعداد اعداد اول: {prime_count:,}")
        print(f"  چگالی: {prime_count/N:.6f}")
        print(f"  1/ln(N): {1/math.log(N):.6f}")
        
        # FFT
        fft = np.fft.fft(signal)
        mag = np.abs(fft)
        power = mag**2
        
        half = N // 2
        freqs = np.fft.fftfreq(N, d=1.0)[:half]
        mag_pos = mag[:half]
        power_pos = power[:half]
        
        # فرکانس‌های غالب (به جز DC)
        mag_for_peaks = mag_pos.copy()
        mag_for_peaks[0] = 0
        peak_indices = np.argsort(mag_for_peaks)[-20:][::-1]
        
        print(f"\n  10 فرکانس غالب:")
        print(f"  {'فرکانس':>12} {'دوره':>10} {'قدرت':>12}")
        for idx in peak_indices[:10]:
            freq = freqs[idx]
            period = 1.0 / freq if freq > 0 else float('inf')
            p = power_pos[idx]
            print(f"  {freq:>12.6f} {period:>10.2f} {p:>12.2f}")
        
        results[N] = {
            'freqs': freqs,
            'mag': mag_pos,
            'power': power_pos,
            'peaks': peak_indices,
            'prime_count': prime_count
        }
        
        elapsed = time.time() - t0
        print(f"  زمان: {elapsed:.2f}s")
    
    # نمودار مقایسه‌ای
    fig, axes = plt.subplots(len(N_values), 1, figsize=(14, 3*len(N_values)))
    
    for i, N in enumerate(N_values):
        freqs = results[N]['freqs']
        power = results[N]['power']
        
        # فقط فرکانس‌های کوچک (الگوهای بزرگ)
        limit = min(1000, len(freqs))
        axes[i].semilogy(freqs[1:limit], power[1:limit], 'b-', linewidth=0.5)
        axes[i].set_title(f'طیف قدرت - N={N:,} (اولین {limit} فرکانس)')
        axes[i].set_xlabel('فرکانس')
        axes[i].set_ylabel('قدرت (log)')
        axes[i].grid(True, alpha=0.3)
        
        # علامت‌گذاری فرکانس‌های مهم
        for frac, label in [(1/6, '1/6'), (1/3, '1/3'), (1/5, '1/5'), 
                            (1/10, '1/10'), (1/30, '1/30')]:
            axes[i].axvline(x=frac, color='r', linestyle='--', alpha=0.5)
            axes[i].text(frac, axes[i].get_ylim()[1]*0.5, label, 
                        color='red', fontsize=8, ha='center')
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/download/prime_fft_large_N.png', dpi=100, bbox_inches='tight')
    plt.close()
    print(f"\nنمودار ذخیره شد: /home/z/my-project/download/prime_fft_large_N.png")
    
    return results

# ============================================================
#  2. تحلیل فاصله‌های بین اعداد اول (prime gaps)
# ============================================================
def analyze_prime_gaps():
    print("\n" + "=" * 70)
    print("  2. تحلیل فاصله‌های بین اعداد اول (prime gaps)")
    print("=" * 70)
    
    N = 10**6
    print(f"\nN = {N:,}")
    
    t0 = time.time()
    primes = get_primes(N)
    gaps = [primes[i+1] - primes[i] for i in range(len(primes)-1)]
    elapsed = time.time() - t0
    
    print(f"تعداد اعداد اول: {len(primes):,}")
    print(f"تعداد فاصله‌ها: {len(gaps):,}")
    print(f"زمان: {elapsed:.2f}s")
    
    print(f"\nآمار فاصله‌ها:")
    print(f"  میانگین: {np.mean(gaps):.2f}")
    print(f"  میانه: {np.median(gaps):.2f}")
    print(f"  انحراف معیار: {np.std(gaps):.2f}")
    print(f"  حداقل: {min(gaps)}")
    print(f"  حداکثر: {max(gaps)}")
    
    # توزیع فاصله‌ها
    print(f"\nتوزیع فاصله‌ها (10 فاصله پرتکرار):")
    from collections import Counter
    gap_counts = Counter(gaps)
    for gap, count in gap_counts.most_common(10):
        pct = 100 * count / len(gaps)
        print(f"  فاصله {gap}: {count:,} ({pct:.2f}%)")
    
    # FFT روی فاصله‌ها
    print(f"\nتحلیل FFT روی فاصله‌ها:")
    gaps_array = np.array(gaps, dtype=np.float64)
    
    # استفاده از N توان 2
    N_fft = 2**17  # 131072
    if len(gaps_array) > N_fft:
        gaps_trunc = gaps_array[:N_fft]
    else:
        gaps_trunc = gaps_array
    
    fft_gaps = np.fft.fft(gaps_trunc)
    mag_gaps = np.abs(fft_gaps)
    power_gaps = mag_gaps**2
    
    half = N_fft // 2
    freqs_gaps = np.fft.fftfreq(N_fft, d=1.0)[:half]
    mag_gaps_pos = mag_gaps[:half]
    
    # فرکانس‌های غالب
    mag_for_peaks = mag_gaps_pos.copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-10:][::-1]
    
    print(f"\n10 فرکانس غالب در فاصله‌ها:")
    print(f"  {'فرکانس':>12} {'دوره':>10} {'دامنه':>12}")
    for idx in peak_indices:
        freq = freqs_gaps[idx]
        period = 1.0 / freq if freq > 0 else float('inf')
        mag = mag_gaps_pos[idx]
        print(f"  {freq:>12.6f} {period:>10.2f} {mag:>12.2f}")
    
    # نمودار
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    # فاصله‌های اول 1000
    axes[0].plot(gaps[:1000], 'b-', linewidth=0.8)
    axes[0].set_title('فاصله‌های بین اعداد اول (1000 فاصله اول)')
    axes[0].set_xlabel('اندیس')
    axes[0].set_ylabel('فاصله')
    axes[0].grid(True, alpha=0.3)
    
    # هیستوگرام فاصله‌ها
    axes[1].hist(gaps, bins=range(0, 100), color='green', alpha=0.7, edgecolor='black')
    axes[1].set_title('توزیع فاصله‌های بین اعداد اول')
    axes[1].set_xlabel('فاصله')
    axes[1].set_ylabel('تعداد')
    axes[1].grid(True, alpha=0.3)
    
    # طیف FFT فاصله‌ها
    limit = 500
    axes[2].semilogy(freqs_gaps[1:limit], mag_gaps_pos[1:limit], 'r-', linewidth=0.5)
    axes[2].set_title(f'طیف FFT فاصله‌ها (اولین {limit} فرکانس)')
    axes[2].set_xlabel('فرکانس')
    axes[2].set_ylabel('دامنه (log)')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/download/prime_gaps_analysis.png', dpi=100, bbox_inches='tight')
    plt.close()
    print(f"\nنمودار ذخیره شد: /home/z/my-project/download/prime_gaps_analysis.png")
    
    return gaps

# ============================================================
#  3. تحلیل autocorrelation
# ============================================================
def analyze_autocorrelation():
    print("\n" + "=" * 70)
    print("  3. تحلیل Autocorrelation اعداد اول")
    print("=" * 70)
    
    N = 10**5
    print(f"\nN = {N:,}")
    
    sieve = sieve_primes(N)
    signal = np.zeros(N, dtype=np.float64)
    for i in range(N):
        if sieve[i]:
            signal[i] = 1.0
    
    # محاسبه autocorrelation
    print("محاسبه autocorrelation...")
    t0 = time.time()
    
    # استفاده از FFT برای محاسبه سریع
    fft_signal = np.fft.fft(signal)
    power = np.abs(fft_signal)**2
    autocorr = np.fft.ifft(power).real
    autocorr = autocorr / autocorr[0]  # نرمال‌سازی
    
    elapsed = time.time() - t0
    print(f"زمان: {elapsed:.2f}s")
    
    # بررسی autocorrelation در دوره‌های خاص
    print(f"\nAutocorrelation در دوره‌های خاص:")
    print(f"  {'دوره':>10} {'autocorrelation':>20}")
    for period in [2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 30, 60, 100]:
        if period < len(autocorr):
            ac = autocorr[period]
            print(f"  {period:>10} {ac:>20.6f}")
    
    # نمودار
    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    
    # autocorrelation کامل
    limit = 1000
    axes[0].plot(autocorr[:limit], 'b-', linewidth=0.8)
    axes[0].set_title(f'Autocorrelation اعداد اول (اولین {limit} دوره)')
    axes[0].set_xlabel('دوره (lag)')
    axes[0].set_ylabel('Autocorrelation')
    axes[0].grid(True, alpha=0.3)
    
    # علامت‌گذاری دوره‌های مهم
    for period in [6, 30, 210]:  # 2×3, 2×3×5, 2×3×5×7
        if period < limit:
            axes[0].axvline(x=period, color='r', linestyle='--', alpha=0.5)
            axes[0].text(period, axes[0].get_ylim()[1]*0.9, str(period), 
                        color='red', fontsize=10, ha='center')
    
    # autocorrelation برای دوره‌های بزرگ
    axes[1].plot(range(1, limit), autocorr[1:limit], 'r-', linewidth=0.5)
    axes[1].set_title('Autocorrelation (بزرگ‌نمایی)')
    axes[1].set_xlabel('دوره (lag)')
    axes[1].set_ylabel('Autocorrelation')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/download/prime_autocorrelation.png', dpi=100, bbox_inches='tight')
    plt.close()
    print(f"\nنمودار ذخیره شد: /home/z/my-project/download/prime_autocorrelation.png")

# ============================================================
#  4. بررسی الگوی primorial (2×3×5×7×...)
# ============================================================
def analyze_primorial_pattern():
    print("\n" + "=" * 70)
    print("  4. بررسی الگوی primorial (2×3×5×7×...)")
    print("=" * 70)
    
    # primorial ها: 2, 6, 30, 210, 2310, 30030, ...
    primorials = [2, 6, 30, 210, 2310, 30030]
    
    N = 10**6
    sieve = sieve_primes(N)
    primes = [i for i in range(N+1) if sieve[i]]
    
    print(f"\nN = {N:,}, تعداد اعداد اول: {len(primes):,}")
    
    for prim in primorials:
        # شمارش اعداد اول در هر کلاس mod prim
        counts = {}
        for p in primes:
            if p < prim:
                continue
            r = p % prim
            counts[r] = counts.get(r, 0) + 1
        
        # تعداد کلاس‌های با اعداد اول
        non_empty = len(counts)
        total_classes = prim
        
        # کلاس با بیشترین اعداد اول
        max_class = max(counts, key=counts.get)
        max_count = counts[max_class]
        
        # میانگین
        avg = len([p for p in primes if p >= prim]) / total_classes
        
        print(f"\nprimorial = {prim} (2×3×{'×'.join(str(x) for x in range(5, prim+1) if all(x%j!=0 for j in range(2,x)))})")
        print(f"  کلاس‌های با اعداد اول: {non_empty}/{total_classes}")
        print(f"  کلاس با بیشترین: {max_class} با {max_count} عدد")
        print(f"  میانگین: {avg:.2f}")
        
        # نمایش 5 کلاس با بیشترین
        sorted_classes = sorted(counts.items(), key=lambda x: -x[1])[:5]
        print(f"  5 کلاس با بیشترین اعداد اول:")
        for cls, cnt in sorted_classes:
            print(f"    {cls} (mod {prim}): {cnt}")

# ============================================================
#  5. تحلیل توان طیفی در فرکانس‌های خاص
# ============================================================
def analyze_spectral_power():
    print("\n" + "=" * 70)
    print("  5. تحلیل توان طیفی در فرکانس‌های خاص")
    print("=" * 70)
    
    N = 2**17  # 131072
    sieve = sieve_primes(N)
    signal = np.zeros(N, dtype=np.float64)
    for i in range(N):
        if sieve[i]:
            signal[i] = 1.0
    
    fft = np.fft.fft(signal)
    power = np.abs(fft)**2
    
    # فرکانس‌های خاص
    special_freqs = {
        '1/2 (دوره 2)': 1/2,
        '1/3 (دوره 3)': 1/3,
        '1/5 (دوره 5)': 1/5,
        '1/6 (دوره 6)': 1/6,
        '1/7 (دوره 7)': 1/7,
        '1/10 (دوره 10)': 1/10,
        '1/14 (دوره 14)': 1/14,
        '1/15 (دوره 15)': 1/15,
        '1/30 (دوره 30)': 1/30,
        '1/210 (دوره 210)': 1/210,
        '1/2310 (دوره 2310)': 1/2310,
    }
    
    print(f"\nN = {N}")
    print(f"\nتوان در فرکانس‌های خاص:")
    print(f"  {'فرکانس':>20} {'قدرت':>15} {'نرمال‌شده':>15}")
    print("-" * 55)
    
    total_power = np.sum(power[1:])  # به جز DC
    
    for name, freq in special_freqs.items():
        # پیدا کردن نزدیک‌ترین فرکانس
        idx = int(round(freq * N))
        if idx < len(power):
            p = power[idx]
            pct = 100 * p / total_power
            print(f"  {name:>20} {p:>15.2f} {pct:>14.4f}%")
    
    # نمودار
    fig, ax = plt.subplots(figsize=(14, 6))
    
    freqs = np.fft.fftfreq(N, d=1.0)[:N//2]
    power_pos = power[:N//2]
    
    limit = 200
    ax.semilogy(freqs[1:limit], power_pos[1:limit], 'b-', linewidth=1)
    ax.set_title(f'طیف قدرت اعداد اول - N={N} (اولین {limit} فرکانس)')
    ax.set_xlabel('فرکانس')
    ax.set_ylabel('قدرت (log)')
    ax.grid(True, alpha=0.3)
    
    # علامت‌گذاری فرکانس‌های خاص
    for name, freq in special_freqs.items():
        if freq < limit/N * N:  # در محدوده نمایش
            idx = int(round(freq * N))
            if idx < len(power_pos):
                ax.axvline(x=freq, color='r', linestyle='--', alpha=0.5)
                ax.text(freq, power_pos[idx], name.split(' ')[0], 
                       color='red', fontsize=8, ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/download/prime_spectral_power.png', dpi=100, bbox_inches='tight')
    plt.close()
    print(f"\nنمودار ذخیره شد: /home/z/my-project/download/prime_spectral_power.png")

# ============================================================
#  main
# ============================================================
def main():
    print("=" * 70)
    print("  تحلیل عمیق‌تر طیفی اعداد اول")
    print("=" * 70)
    
    # 1. تحلیل برای N بزرگ‌تر
    results = analyze_large_N()
    
    # 2. تحلیل فاصله‌ها
    gaps = analyze_prime_gaps()
    
    # 3. تحلیل autocorrelation
    analyze_autocorrelation()
    
    # 4. الگوی primorial
    analyze_primorial_pattern()
    
    # 5. تحلیل توان طیفی
    analyze_spectral_power()
    
    print("\n" + "=" * 70)
    print("  تحلیل کامل شد!")
    print("=" * 70)

if __name__ == "__main__":
    main()
