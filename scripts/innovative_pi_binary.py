#!/usr/bin/env python3
"""
روش‌های ابتکاری پیشرفته:
1. اعداد اول/مرکب مرسن در مبنای ۲ و سایر مبنا
2. جستجوی اعداد اول در دنباله اعشاری π
3. استفاده از π برای فاکتوریزاسیون
4. روش‌های ابتکاری جدید
"""

import gmpy2
from gmpy2 import mpz, is_prime, gcd, isqrt, iroot, powmod
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpmath import mp, mpf, pi as mpi, floor, power, log, sqrt
import time
import json
import os

# دقت بالا برای محاسبه π
mp.dps = 10000  # 10000 رقم اعشار

# ============================================================
#  ۱. اعداد مرسن در مبنای ۲ و سایر مبنا
# ============================================================
def analyze_mersenne_bases():
    """
    تحلیل اعداد مرسن در مبانی مختلف
    M(p) = 2^p - 1 در مبنای ۲
    M(p, b) = b^p - 1 در مبنای b
    """
    print("=" * 70)
    print("  ۱. اعداد مرسن در مبانی مختلف")
    print("=" * 70)
    
    bases = [2, 3, 5, 7, 10, 16]  # مبناهای مختلف
    
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        print(f"\np = {p}:")
        for b in bases:
            val = mpz(b)**p - 1
            is_p = is_prime(val)
            digits = len(str(val))
            
            # نمایش در مبنای b
            if b <= 16:
                rep = ''
                temp = val
                while temp > 0:
                    digit = int(temp % b)
                    if digit < 10:
                        rep = str(digit) + rep
                    else:
                        rep = chr(55 + digit) + rep
                    temp //= b
                rep = rep.lstrip('0') or '0'
                
                # تعداد 1 ها در مبنای b (برای مبنای ۲، همه 1 هستن)
                ones_count = rep.count('1') if b == 2 else len(rep)
                
                print(f"  {b}^{p}-1 = {val} ({digits} رقم, اول={is_p}, در مبنای {b}: {rep[:30]}{'...' if len(rep)>30 else ''})")
    
    # تحلیل الگوی باینری
    print(f"\n{'='*70}")
    print("  الگوی باینری اعداد مرسن")
    print(f"{'='*70}")
    
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        M = mpz(2)**p - 1
        binary = bin(M)[2:]
        # در مبنای ۲، M(p) = p تا 1
        print(f"  M({p}) = {'1'*p} ({p} تا 1)")
        
        # بررسی الگوهای دیگر
        # تعداد 0 و 1
        ones = binary.count('1')
        zeros = binary.count('0')
        
        # مبنای ۳
        val3 = ''
        temp = M
        while temp > 0:
            val3 = str(int(temp % 3)) + val3
            temp //= 3
        ones3 = val3.count('1')
        twos3 = val3.count('2')
        zeros3 = val3.count('0')
        
        print(f"    مبنای ۳: {val3[:40]}{'...' if len(val3)>40 else ''} (0:{zeros3}, 1:{ones3}, 2:{twos3})")

# ============================================================
#  ۲. جستجوی اعداد اول در دنباله اعشاری π
# ============================================================
def find_primes_in_pi(num_digits=10000):
    """
    جستجوی اعداد اول در دنباله اعشاری π
    """
    print(f"\n{'='*70}")
    print(f"  ۲. جستجوی اعداد اول در دنباله اعشاری π")
    print(f"{'='*70}")
    
    # محاسبه π با دقت بالا
    print(f"محاسبه π با {num_digits} رقم اعشار...")
    t0 = time.time()
    pi_str = str(mpi)[:num_digits + 2]  # +2 برای "3."
    pi_digits = pi_str.replace('.', '')
    print(f"زمان: {time.time()-t0:.2f}s")
    
    print(f"اولین ۱۰۰ رقم π: {pi_digits[:100]}")
    print()
    
    # جستجوی اعداد اول با طول‌های مختلف
    primes_found = []
    
    for length in [2, 3, 4, 5, 6, 7, 8, 10, 15, 20]:
        found = []
        for start in range(len(pi_digits) - length + 1):
            candidate_str = pi_digits[start:start+length]
            # حذف صفرهای ابتدایی
            candidate_str = candidate_str.lstrip('0')
            if len(candidate_str) < 2:
                continue
            
            candidate = int(candidate_str)
            if candidate > 1 and is_prime(candidate):
                found.append((start, candidate))
        
        primes_found.append((length, found))
        print(f"  اعداد اول {length} رقمی در π: {len(found)} عدد")
        if found:
            # اولین ۵ مورد
            for pos, prime in found[:5]:
                print(f"    موقعیت {pos}: {prime}")
    
    return pi_digits, primes_found

# ============================================================
#  ۳. استفاده از π برای فاکتوریزاسیون
# ============================================================
def pi_based_factorization(N, pi_digits, max_search=10000):
    """
    روش ابتکاری: استفاده از ارقام π به‌عنوان کاندید فاکتور
    
    ایده:
    - ارقام π ممکنه شامل فاکتورهای N باشن
    - بررسی اعداد اول استخراج شده از π
    """
    N_mpz = mpz(N)
    
    # Trial
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N_mpz % p == 0:
            return p, N_mpz // p, 'Trial'
    
    # جستجوی ارقام π به‌عنوان کاندید فاکتور
    for length in range(2, min(20, len(str(N)))):
        for start in range(min(max_search, len(pi_digits) - length + 1)):
            candidate_str = pi_digits[start:start+length].lstrip('0')
            if len(candidate_str) < 2:
                continue
            
            candidate = int(candidate_str)
            if candidate > 1 and candidate < N:
                if N_mpz % candidate == 0:
                    return candidate, N_mpz // candidate, 'Pi-digit'
    
    # ترکیب: ارقام π × اعداد اول کوچک
    for start in range(min(1000, len(pi_digits) - 5)):
        for length in [3, 4, 5]:
            if start + length > len(pi_digits):
                continue
            candidate_str = pi_digits[start:start+length].lstrip('0')
            if len(candidate_str) < 2:
                continue
            
            base = int(candidate_str)
            for mult in range(2, 100):
                candidate = base * mult
                if candidate > 1 and candidate < N:
                    if N_mpz % candidate == 0:
                        return candidate, N_mpz // candidate, 'Pi-digit×mult'
    
    return None, None, None

# ============================================================
#  ۴. روش ابتکاری: تحلیل باینری اعداد مرسن
# ============================================================
def binary_pattern_factorization(N):
    """
    روش ابتکاری: تحلیل الگوی باینری N
    
    ایده:
    - اگه N = p × q، الگوی باینری N ممکنه الگوی p یا q رو نشون بده
    - بررسی تعداد 1 ها، 0 ها، و الگوهای تکراری
    """
    N_mpz = mpz(N)
    
    # Trial
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N_mpz % p == 0:
            return p, N_mpz // p, 'Trial'
    
    # الگوی باینری
    binary = bin(N)[2:]
    num_bits = len(binary)
    ones = binary.count('1')
    zeros = binary.count('0')
    
    # بررسی آیا تعداد بیت‌ها فاکتور N هست
    candidates = [num_bits, ones, zeros, num_bits - ones, ones + zeros]
    
    for c in candidates:
        if c > 1 and c < N and N_mpz % c == 0:
            return c, N_mpz // c, 'Binary-pattern'
    
    # الگوی باینری در مبنای ۳
    val3 = ''
    temp = N_mpz
    while temp > 0:
        val3 = str(int(temp % 3)) + val3
        temp //= 3
    
    for digit in [0, 1, 2]:
        count = val3.count(str(digit))
        if count > 1 and count < N and N_mpz % count == 0:
            return count, N_mpz // count, 'Base3-pattern'
    
    return None, None, None

# ============================================================
#  ۵. روش ابتکاری: استفاده از ضرایب π
# ============================================================
def pi_coefficient_factorization(N, pi_digits):
    """
    روش ابتکاری: استفاده از ضرایب π
    
    ایده:
    - π = 3.14159...
    - ضرایب آن (3, 1, 4, 1, 5, 9, ...) ممکنه فاکتور N باشن
    - ترکیب ارقام π برای ساخت کاندیدهای بزرگ‌تر
    """
    N_mpz = mpz(N)
    
    # Trial
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N_mpz % p == 0:
            return p, N_mpz // p, 'Trial'
    
    # تک تک ارقام π
    for i, digit in enumerate(pi_digits[:1000]):
        d = int(digit)
        if d > 1 and d < N and N_mpz % d == 0:
            return d, N_mpz // d, 'Pi-single-digit'
    
    # ترکیب دو رقم
    for i in range(len(pi_digits) - 1):
        for j in range(i+1, min(i+10, len(pi_digits))):
            candidate = int(pi_digits[i:j+1].lstrip('0') or '0')
            if candidate > 1 and candidate < N and N_mpz % candidate == 0:
                return candidate, N_mpz // candidate, 'Pi-multi-digit'
    
    return None, None, None

# ============================================================
#  ۶. تست همه روش‌ها
# ============================================================
def test_all_methods(pi_digits):
    print(f"\n{'='*70}")
    print(f"  تست همه روش‌های ابتکاری")
    print(f"{'='*70}")
    
    test_cases = [
        (77, 7, 11),
        (91, 7, 13),
        (143, 11, 13),
        (221, 13, 17),
        (667, 23, 29),
        (1147, 31, 37),
        (1763, 41, 43),
        (3599, 59, 61),
        (1001, 7, 143),
        (10002200057, 100003, 100019),
    ]
    
    methods = [
        ('Pi-based', lambda N: pi_based_factorization(N, pi_digits)),
        ('Binary-pattern', lambda N: binary_pattern_factorization(N)),
        ('Pi-coefficient', lambda N: pi_coefficient_factorization(N, pi_digits)),
    ]
    
    for method_name, method_func in methods:
        print(f"\n--- {method_name} ---")
        success = 0
        total_time = 0
        
        for N, p, q in test_cases:
            t0 = time.time()
            try:
                f, c, method = method_func(N)
            except:
                f, c, method = None, None, None
            elapsed = time.time() - t0
            total_time += elapsed
            
            if f is not None and f * c == N:
                success += 1
                print(f"  ✓ N={N} = {f} × {c} (روش: {method}, {elapsed:.3f}s)")
            else:
                print(f"  ✗ N={N} = {p}×{q} ({elapsed:.3f}s)")
        
        print(f"  موفق: {success}/{len(test_cases)} ({100*success/len(test_cases):.0f}%)")
        print(f"  زمان کل: {total_time:.2f}s")

# ============================================================
#  ۷. رسم نمودار
# ============================================================
def plot_pi_analysis(pi_digits, primes_found, save_dir):
    """رسم نمودار تحلیل π"""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    # توزیع ارقام π
    digit_counts = [pi_digits.count(str(d)) for d in range(10)]
    axes[0,0].bar(range(10), digit_counts, color='blue', alpha=0.7)
    axes[0,0].set_title('توزیع ارقام π (10000 رقم)')
    axes[0,0].set_xlabel('رقم')
    axes[0,0].set_ylabel('تعداد')
    axes[0,0].set_xticks(range(10))
    axes[0,0].grid(True, alpha=0.3)
    
    # تعداد اعداد اول در π بر اساس طول
    lengths = [l for l, _ in primes_found]
    counts = [len(found) for _, found in primes_found]
    axes[0,1].bar(lengths, counts, color='red', alpha=0.7)
    axes[0,1].set_title('تعداد اعداد اول در π بر اساس طول')
    axes[0,1].set_xlabel('تعداد ارقام')
    axes[0,1].set_ylabel('تعداد اعداد اول')
    axes[0,1].grid(True, alpha=0.3)
    
    # اولین 1000 رقم π به‌عنوان موج
    pi_wave = [int(d) for d in pi_digits[:1000]]
    axes[1,0].plot(pi_wave[:200], 'g-', linewidth=0.8)
    axes[1,0].set_title('ارقام π به‌عنوان شکل موج (200 رقم اول)')
    axes[1,0].set_xlabel('موقعیت')
    axes[1,0].set_ylabel('رقم')
    axes[1,0].grid(True, alpha=0.3)
    
    # طیف فرکانسی ارقام π
    pi_array = np.array(pi_wave, dtype=np.float64)
    fft_result = np.fft.fft(pi_array - np.mean(pi_array))
    magnitude = np.abs(fft_result)
    freqs = np.fft.fftfreq(1000, d=1.0)
    axes[1,1].semilogy(freqs[:500], magnitude[:500], 'm-', linewidth=0.5)
    axes[1,1].set_title('طیف فرکانسی ارقام π')
    axes[1,1].set_xlabel('فرکانس')
    axes[1,1].set_ylabel('دامنه (log)')
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{save_dir}/pi_analysis.png', dpi=100, bbox_inches='tight')
    plt.close()
    print(f"نمودار ذخیره شد: {save_dir}/pi_analysis.png")

# ============================================================
#  main
# ============================================================
def main():
    print("=" * 70)
    print("  روش‌های ابتکاری: مبنای ۲، π، و فاکتوریزاسیون")
    print("=" * 70)
    
    save_dir = "/home/z/my-project/download"
    
    # ۱. تحلیل اعداد مرسن در مبانی مختلف
    analyze_mersenne_bases()
    
    # ۲. جستجوی اعداد اول در π
    pi_digits, primes_found = find_primes_in_pi(num_digits=10000)
    
    # ۳. تست روش‌های ابتکاری
    test_all_methods(pi_digits)
    
    # ۴. رسم نمودار
    print(f"\nرسم نمودار...")
    plot_pi_analysis(pi_digits, primes_found, save_dir)
    
    # ۵. ذخیره داده‌ها
    print(f"\nذخیره داده‌ها...")
    
    # اعداد اول پیدا شده در π
    pi_primes_data = {}
    for length, found in primes_found:
        pi_primes_data[length] = {
            'count': len(found),
            'first_5': [p for _, p in found[:5]],
            'positions': [pos for pos, _ in found[:10]]
        }
    
    with open(f'{save_dir}/pi_primes_data.json', 'w') as f:
        json.dump(pi_primes_data, f, indent=2)
    
    # ذخیره 1000 رقم اول π
    with open(f'{save_dir}/pi_10000_digits.txt', 'w') as f:
        f.write(pi_digits)
    
    print(f"داده‌ها ذخیره شدند:")
    print(f"  - {save_dir}/pi_primes_data.json")
    print(f"  - {save_dir}/pi_10000_digits.txt")
    print(f"  - {save_dir}/pi_analysis.png")
    
    print(f"\n{'='*70}")
    print(f"  کامل شد!")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
