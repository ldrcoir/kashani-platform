#!/usr/bin/env python3
"""
۱۰۰ عدد اول در مبنای باینری + تحلیل نویز + پله رو به بالا
"""

import gmpy2
from gmpy2 import mpz, is_prime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# فونت فارسی
try:
    fm.fontManager.addfont('/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf')
except:
    pass
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
#  تولید 100 عدد اول
# ============================================================
def generate_primes(n):
    primes = []
    candidate = 2
    while len(primes) < n:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 1
    return primes

# ============================================================
#  نمایش باینری
# ============================================================
def print_binary_table(primes):
    print("=" * 80)
    print("  ۱۰۰ عدد اول - مبنای ۱۰ و مبنای ۲")
    print("=" * 80)
    print()
    print(f"{'#':>4} {'مبنای ۱۰':>10} {'مبنای ۲ (باینری)':>50} {'تعداد ۱':>8} {'تعداد ۰':>8}")
    print("-" * 85)
    
    for i, p in enumerate(primes, 1):
        binary = bin(p)[2:]
        ones = binary.count('1')
        zeros = binary.count('0')
        print(f"{i:>4} {p:>10} {binary:>50} {ones:>8} {zeros:>8}")
    
    print()

# ============================================================
#  تحلیل نویز و پله رو به بالا
# ============================================================
def plot_analysis(primes):
    """رسم نمودارهای تحلیلی"""
    
    fig, axes = plt.subplots(4, 2, figsize=(18, 20))
    
    # ============================================================
    #  ۱. پله رو به بالا (Staircase) - اعداد اول در مبنای ۱۰
    # ============================================================
    axes[0,0].step(range(1, 101), primes, where='mid', color='blue', linewidth=2)
    axes[0,0].set_title('Staircase - 100 Prime Numbers (Base 10)', fontsize=14)
    axes[0,0].set_xlabel('Index')
    axes[0,0].set_ylabel('Prime Value')
    axes[0,0].grid(True, alpha=0.3)
    
    # ============================================================
    #  ۲. پله رو به بالا - مبنای باینری (طول بیت‌ها)
    # ============================================================
    bit_lengths = [len(bin(p)[2:]) for p in primes]
    axes[0,1].step(range(1, 101), bit_lengths, where='mid', color='red', linewidth=2)
    axes[0,1].set_title('Staircase - Bit Length of Primes (Binary)', fontsize=14)
    axes[0,1].set_xlabel('Index')
    axes[0,1].set_ylabel('Bit Length')
    axes[0,1].grid(True, alpha=0.3)
    
    # ============================================================
    #  ۳. سیگنال باینری - هر بیت به‌عنوان 0 یا 1
    # ============================================================
    # ساخت ماتریس باینری: سطر = عدد اول، ستون = بیت
    max_bits = max(bit_lengths)
    binary_matrix = np.zeros((100, max_bits))
    
    for i, p in enumerate(primes):
        binary = bin(p)[2:]
        # pad از چپ
        padded = binary.zfill(max_bits)
        for j, bit in enumerate(padded):
            binary_matrix[i, j] = int(bit)
    
    # نمایش به‌عنوان heatmap
    im = axes[1,0].imshow(binary_matrix, aspect='auto', cmap='binary', interpolation='nearest')
    axes[1,0].set_title('Binary Matrix - 100 Primes (rows) × Bits (columns)', fontsize=14)
    axes[1,0].set_xlabel('Bit Position (MSB → LSB)')
    axes[1,0].set_ylabel('Prime Index')
    plt.colorbar(im, ax=axes[1,0], label='Bit Value')
    
    # ============================================================
    #  ۴. تحلیل نویز - باقی‌مانده پس از حذف روند
    # ============================================================
    # روند = تقریب خطی
    x = np.arange(100)
    primes_array = np.array(primes, dtype=np.float64)
    
    # حذف روند (detrending)
    coeffs = np.polyfit(x, primes_array, 1)
    trend = np.polyval(coeffs, x)
    noise = primes_array - trend
    
    axes[1,1].plot(x, noise, 'g-', linewidth=0.8)
    axes[1,1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    axes[1,1].set_title('Noise - Residual after Linear Detrend', fontsize=14)
    axes[1,1].set_xlabel('Index')
    axes[1,1].set_ylabel('Residual')
    axes[1,1].grid(True, alpha=0.3)
    
    # ============================================================
    #  ۵. طیف توان نویز (Power Spectrum)
    # ============================================================
    fft_noise = np.fft.fft(noise)
    power_noise = np.abs(fft_noise)**2
    freqs = np.fft.fftfreq(100, d=1.0)
    
    axes[2,0].semilogy(freqs[:50], power_noise[:50], 'm-', linewidth=1)
    axes[2,0].set_title('Power Spectrum of Noise', fontsize=14)
    axes[2,0].set_xlabel('Frequency')
    axes[2,0].set_ylabel('Power (log)')
    axes[2,0].grid(True, alpha=0.3)
    
    # ============================================================
    #  ۶. توزیع تعداد 1 ها در باینری
    # ============================================================
    ones_count = [bin(p)[2:].count('1') for p in primes]
    zeros_count = [bin(p)[2:].count('0') for p in primes]
    
    axes[2,1].bar(range(1, 101), ones_count, color='blue', alpha=0.7, label='1s')
    axes[2,1].bar(range(1, 101), zeros_count, bottom=ones_count, color='red', alpha=0.7, label='0s')
    axes[2,1].set_title('Count of 1s and 0s in Binary Representation', fontsize=14)
    axes[2,1].set_xlabel('Prime Index')
    axes[2,1].set_ylabel('Count')
    axes[2,1].legend()
    axes[2,1].grid(True, alpha=0.3)
    
    # ============================================================
    #  ۷. پله رو به بالا برای فاصله‌های بین اعداد اول
    # ============================================================
    gaps = np.diff(primes)
    axes[3,0].step(range(1, 100), gaps, where='mid', color='purple', linewidth=2)
    axes[3,0].set_title('Staircase - Prime Gaps', fontsize=14)
    axes[3,0].set_xlabel('Index')
    axes[3,0].set_ylabel('Gap')
    axes[3,0].grid(True, alpha=0.3)
    
    # ============================================================
    #  ۸. نمودار لگاریتمی - log(prime) vs index
    # ============================================================
    log_primes = np.log(primes_array)
    axes[3,1].plot(x, log_primes, 'b-o', markersize=3, linewidth=1)
    axes[3,1].set_title('log(Prime) vs Index', fontsize=14)
    axes[3,1].set_xlabel('Index')
    axes[3,1].set_ylabel('log(Prime)')
    axes[3,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/download/primes_binary_noise_analysis.png', dpi=100, bbox_inches='tight')
    plt.close()
    print("نمودار ذخیره شد: download/primes_binary_noise_analysis.png")

# ============================================================
#  تحلیل نویز پیشرفته
# ============================================================
def advanced_noise_analysis(primes):
    """تحلیل نویز پیشرفته - مثل مقالات تحقیقاتی"""
    
    print("\n" + "=" * 70)
    print("  تحلیل نویز پیشرفته")
    print("=" * 70)
    
    primes_array = np.array(primes, dtype=np.float64)
    x = np.arange(100)
    
    # ۱. حذف روند خطی
    coeffs1 = np.polyfit(x, primes_array, 1)
    trend1 = np.polyval(coeffs1, x)
    noise1 = primes_array - trend1
    
    # ۲. حذف روند درجه ۲
    coeffs2 = np.polyfit(x, primes_array, 2)
    trend2 = np.polyval(coeffs2, x)
    noise2 = primes_array - trend2
    
    # ۳. حذف روند log (طبق قضیه اعداد اول)
    log_trend = x * np.log(x)  # تقریب p_n ≈ n log n
    noise3 = primes_array - log_trend
    
    print(f"\n۱. حذف روند خطی:")
    print(f"   میانگین نویز: {np.mean(noise1):.2f}")
    print(f"   انحراف معیار: {np.std(noise1):.2f}")
    print(f"   حداقل: {np.min(noise1):.2f}, حداکثر: {np.max(noise1):.2f}")
    
    print(f"\n۲. حذف روند درجه ۲:")
    print(f"   میانگین نویز: {np.mean(noise2):.2f}")
    print(f"   انحراف معیار: {np.std(noise2):.2f}")
    print(f"   حداقل: {np.min(noise2):.2f}, حداکثر: {np.max(noise2):.2f}")
    
    print(f"\n۳. حذف روند n×log(n) (قضیه اعداد اول):")
    print(f"   میانگین نویز: {np.mean(noise3):.2f}")
    print(f"   انحراف معیار: {np.std(noise3):.2f}")
    print(f"   حداقل: {np.min(noise3):.2f}, حداکثر: {np.max(noise3):.2f}")
    
    # ۴. تحلیل طیفی نویز
    print(f"\n۴. تحلیل طیفی نویز (پس از حذف روند log):")
    fft_noise = np.fft.fft(noise3)
    power = np.abs(fft_noise)**2
    freqs = np.fft.fftfreq(100, d=1.0)
    
    # ۵ فرکانس غالب
    power_for_peaks = power[:50].copy()
    power_for_peaks[0] = 0
    peak_indices = np.argsort(power_for_peaks)[-5:][::-1]
    
    print(f"   ۵ فرکانس غالب:")
    for idx in peak_indices:
        freq = freqs[idx]
        period = 1.0 / freq if freq > 0 else 0
        p = power[idx]
        print(f"     فرکانس={freq:.4f}, دوره={period:.2f}, توان={p:.2f}")
    
    # ۴. توزیع نویز
    print(f"\n۵. توزیع نویز (آیا گوسی هست؟):")
    print(f"   میانگین: {np.mean(noise3):.2f}")
    print(f"   میانه: {np.median(noise3):.2f}")
    print(f"   چولگی (skewness): {float(np.mean((noise3 - np.mean(noise3))**3) / np.std(noise3)**3):.4f}")
    print(f"   کشیدگی (kurtosis): {float(np.mean((noise3 - np.mean(noise3))**4) / np.std(noise3)**4) - 3:.4f}")
    print(f"   (کشیدگی گوسی = 0، چولگی گوسی = 0)")
    
    # ۵. autocorrelation نویز
    print(f"\n۶. Autocorrelation نویز:")
    autocorr = np.correlate(noise3 - np.mean(noise3), noise3 - np.mean(noise3), mode='full')
    autocorr = autocorr / autocorr[len(autocorr)//2]  # نرمال‌سازی
    
    for lag in [1, 2, 3, 5, 10, 20, 50]:
        idx = len(autocorr)//2 + lag
        print(f"   lag={lag}: {autocorr[idx]:.4f}")
    
    return noise1, noise2, noise3

# ============================================================
#  main
# ============================================================
def main():
    print("=" * 70)
    print("  ۱۰۰ عدد اول - باینری + نویز + پله رو به بالا")
    print("=" * 70)
    
    # تولید اعداد اول
    primes = generate_primes(100)
    print(f"۱۰۰ عدد اول تولید شد: {primes[0]} تا {primes[-1]}")
    
    # نمایش باینری
    print_binary_table(primes)
    
    # رسم نمودار
    plot_analysis(primes)
    
    # تحلیل نویز پیشرفته
    noise1, noise2, noise3 = advanced_noise_analysis(primes)
    
    # ذخیره داده‌ها
    with open('/home/z/my-project/download/primes_100_binary.txt', 'w') as f:
        f.write("# 100 Prime Numbers - Base 10 and Base 2\n")
        f.write(f"{'#':>4} {'Base 10':>10} {'Binary':>50} {'1s':>6} {'0s':>6}\n")
        f.write("-" * 80 + "\n")
        for i, p in enumerate(primes, 1):
            binary = bin(p)[2:]
            ones = binary.count('1')
            zeros = binary.count('0')
            f.write(f"{i:>4} {p:>10} {binary:>50} {ones:>6} {zeros:>6}\n")
    
    print(f"\nداده‌ها ذخیره شد: download/primes_100_binary.txt")
    print(f"نمودار ذخیره شد: download/primes_binary_noise_analysis.png")

if __name__ == "__main__":
    main()
