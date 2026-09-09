#!/usr/bin/env python3
"""
روش‌های ابتکاری + NFS برای فاکتوریزاسیون
========================================
1. sympy factorint (شامل NFS برای اعداد بزرگ)
2. روش ابتکاری: FFT + Pollard Rho ترکیبی
3. روش ابتکاری: استفاده از ساختار اعداد
4. روش ابتکاری: تحلیل دوره‌ای پیشرفته
"""

import gmpy2
from gmpy2 import mpz, gcd, is_prime, isqrt, iroot, powmod
import numpy as np
import time
import random
from sympy.ntheory import factorint as sympy_factorint

# ============================================================
#  روش 1: sympy factorint (شامل QS/NFS)
# ============================================================
def sympy_factor(N):
    """استفاده از sympy که شامل QS و روش‌های پیشرفته هست"""
    t0 = time.time()
    try:
        factors = sympy_factorint(N)
        elapsed = time.time() - t0
        
        if len(factors) > 1 or (len(factors) == 1 and list(factors.values())[0] > 1):
            # تبدیل به فرمت (factor, cofactor)
            factor_list = []
            for p, e in factors.items():
                factor_list.extend([p] * e)
            
            if len(factor_list) >= 2:
                f1 = factor_list[0]
                f2 = N // f1
                return f1, f2, elapsed
        
        return None, None, elapsed
    except Exception as e:
        return None, None, time.time() - t0

# ============================================================
#  روش 2: Pollard Rho بهبود یافته
# ============================================================
def pollard_rho_brent(N, max_iter=1000000):
    """
    Pollard Rho با الگوریتم Brent (سریع‌تر)
    """
    if N % 2 == 0:
        return 2, N // 2
    if N % 3 == 0:
        return 3, N // 3
    
    N_mpz = mpz(N)
    
    for c in range(1, 200):
        y = mpz(random.randint(1, N-1))
        m = random.randint(100, 1000)
        g = mpz(1)
        r = mpz(1)
        q = mpz(1)
        x = ys = y
        
        while g == 1:
            x = (x * x + c) % N_mpz
            ys = y
            for _ in range(r):
                y = (y * y + c) % N_mpz
                q = (q * abs(x - y)) % N_mpz
            
            g = gcd(q, N_mpz)
            r *= 2
            if r > max_iter:
                break
        
        if g > 1 and g < N_mpz:
            return g, N_mpz // g
    
    return None, None

# ============================================================
#  روش 3: FFT هوشمند + Pollard Rho
# ============================================================
def fft_smart_plus_rho(N, max_k=65536):
    """
    ترکیب FFT و Pollard Rho
    FFT برای فاکتورهای متوسط
    Pollard Rho برای بقیه
    """
    # مرحله 1: Trial Division سریع
    N_mpz = mpz(N)
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N_mpz % p == 0:
            return p, N_mpz // p, 'Trial'
    
    # مرحله 2: FFT برای فاکتورهای متوسط
    remainders = np.zeros(max_k, dtype=np.float64)
    for k in range(1, max_k + 1):
        remainders[k-1] = float(N_mpz % k)
    
    max_r = np.max(remainders)
    if max_r > 0:
        remainders = remainders / max_r
    remainders = remainders - np.mean(remainders)
    
    fft_result = np.fft.fft(remainders)
    magnitude = np.abs(fft_result)
    freqs = np.fft.fftfreq(max_k, d=1.0)
    
    mag_for_peaks = magnitude[:max_k//2].copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-500:][::-1]
    
    for idx in peak_indices:
        freq = freqs[idx]
        if freq == 0:
            continue
        period = 1.0 / freq
        period_int = int(round(period))
        
        for mult in range(1, 500):
            candidate = period_int * mult
            if candidate > 1 and candidate < N:
                g = gcd(N_mpz, candidate)
                if g > 1 and g < N_mpz:
                    return g, N_mpz // g, 'FFT'
        
        for offset in range(-200, 201):
            candidate = period_int + offset
            if candidate > 1 and candidate < N:
                g = gcd(N_mpz, candidate)
                if g > 1 and g < N_mpz:
                    return g, N_mpz // g, 'FFT'
    
    # مرحله 3: Pollard Rho برای فاکتورهای بزرگ‌تر
    f, c = pollard_rho_brent(N, max_iter=500000)
    if f is not None:
        return f, c, 'Rho'
    
    return None, None, None

# ============================================================
#  روش 4: ابتکاری - تحلیل ساختار N
# ============================================================
def structural_analysis(N):
    """
    روش ابتکاری: تحلیل ساختار N
    - بررسی N mod (اعداد خاص)
    - استفاده از خاصیت N = a² - b²
    - استفاده از الگوی باقی‌مانده‌ها
    """
    N_mpz = mpz(N)
    
    # روش Fermat (اگه فاکتورها نزدیک باشن)
    a = isqrt(N_mpz)
    if a * a < N_mpz:
        a += 1
    
    # بررسی delta های مختلف
    for delta in range(10000):
        a_test = a + delta
        b_squared = a_test * a_test - N_mpz
        if b_squared >= 0:
            b, is_perfect = iroot(b_squared, 2)
            if is_perfect:
                f1 = a_test + b
                f2 = a_test - b
                if f1 > 1 and f2 > 1:
                    return f1, f2, 'Fermat'
    
    # روش: بررسی N mod k برای k های خاص
    # اگه N = p × q، ممکنه p یا q به فرم خاص باشن
    
    # بررسی اعداد به فرم 6k±1
    for k in range(1, 100000):
        for candidate in [6*k - 1, 6*k + 1]:
            if candidate > 1 and candidate < N and N_mpz % candidate == 0:
                return candidate, N_mpz // candidate, '6k±1'
    
    return None, None, None

# ============================================================
#  روش 5: ترکیب همه روش‌ها
# ============================================================
def ultimate_factor(N, max_k=65536):
    """
    ترکیب همه روش‌ها:
    1. Trial Division
    2. FFT هوشمند
    3. Pollard Rho (Brent)
    4. Fermat
    5. sympy (شامل QS/NFS)
    """
    N_mpz = mpz(N)
    methods_tried = []
    
    # 1. Trial Division
    t0 = time.time()
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]:
        if N_mpz % p == 0:
            elapsed = time.time() - t0
            methods_tried.append(('Trial', elapsed, True))
            return p, N_mpz // p, 'Trial', methods_tried
    methods_tried.append(('Trial', time.time() - t0, False))
    
    # 2. FFT هوشمند + Pollard Rho
    t0 = time.time()
    f, c, method = fft_smart_plus_rho(N, max_k=max_k)
    elapsed = time.time() - t0
    methods_tried.append((method or 'FFT+Rho', elapsed, f is not None))
    
    if f is not None:
        return f, c, method, methods_tried
    
    # 3. Fermat (اگه فاکتورها نزدیک باشن)
    t0 = time.time()
    f, c, method = structural_analysis(N)
    elapsed = time.time() - t0
    methods_tried.append(('Fermat', elapsed, f is not None))
    
    if f is not None:
        return f, c, method, methods_tried
    
    # 4. sympy (شامل QS)
    t0 = time.time()
    f, c, elapsed = sympy_factor(N)
    methods_tried.append(('sympy/QS', elapsed, f is not None))
    
    if f is not None:
        return f, c, 'sympy', methods_tried
    
    return None, None, None, methods_tried

# ============================================================
#  تست
# ============================================================
def test_ultimate():
    print("=" * 70)
    print("  تست روش نهایی: Trial + FFT + Rho + Fermat + sympy")
    print("=" * 70)
    
    random.seed(42)
    
    test_groups = [
        ("5 digit", [10007, 10009, 10037, 10039, 10061]),
        ("6 digit", [100003, 100019, 100043, 100049, 100057]),
        ("7 digit", [1000003, 1000033, 1000037, 1000039, 1000081]),
        ("8 digit", [10000019, 10000079, 10000103, 10000121]),
        ("10 digit", [1000000007, 1000000009, 1000000021, 1000000033]),
        ("12 digit", [1000000000039, 1000000000061, 1000000000063]),
        ("15 digit", [1000000000000037, 1000000000000091, 1000000000000159]),
    ]
    
    for group_name, primes in test_groups:
        print(f"\n--- {group_name} ---")
        
        test_cases = []
        for _ in range(5):
            p = random.choice(primes)
            q = random.choice(primes)
            if p != q:
                test_cases.append((p*q, min(p,q), max(p,q)))
        
        success = 0
        method_stats = {}
        total_time = 0
        
        for N, p, q in test_cases:
            t0 = time.time()
            factor, cofactor, method, methods_tried = ultimate_factor(N)
            elapsed = time.time() - t0
            total_time += elapsed
            
            if factor is not None and factor * cofactor == N:
                success += 1
                method_stats[method] = method_stats.get(method, 0) + 1
        
        print(f"  موفق: {success}/{len(test_cases)} ({100*success/len(test_cases):.1f}%)")
        print(f"  زمان: {total_time:.1f}s ({total_time/len(test_cases)*1000:.0f}ms/test)")
        print(f"  روش‌ها: {method_stats}")

if __name__ == "__main__":
    test_ultimate()
