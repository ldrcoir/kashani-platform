#!/usr/bin/env python3
"""
تست primefac (شامل QS/NFS) + روش‌های ابتکاری
============================================
primefac شامل:
- Trial Division
- Pollard Rho
- Pollard p-1
- Williams p+1
- ECM
- Quadratic Sieve
- Number Field Sieve (برای اعداد بزرگ)
"""

import primefac
import gmpy2
from gmpy2 import mpz, gcd, isqrt, iroot, is_prime
import numpy as np
import time
import random

# ============================================================
#  روش 1: primefac (شامل QS/NFS)
# ============================================================
def primefac_factor(N, timeout=300):
    """استفاده از primefac که شامل QS/NFS هست"""
    t0 = time.time()
    try:
        factors = list(primefac.primefac(N))
        elapsed = time.time() - t0
        
        if len(factors) >= 2:
            f1 = factors[0]
            f2 = N // f1
            return f1, f2, elapsed
        
        return None, None, elapsed
    except Exception as e:
        return None, None, time.time() - t0

# ============================================================
#  روش 2: ابتکاری - FFT + primefac
# ============================================================
def fft_plus_primefac(N, max_k=65536):
    """
    ترکیب FFT و primefac
    FFT برای فاکتورهای متوسط
    primefac برای بقیه
    """
    N_mpz = mpz(N)
    
    # مرحله 1: Trial Division سریع
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N_mpz % p == 0:
            return p, N_mpz // p, 'Trial', 0
    
    # مرحله 2: FFT
    t0 = time.time()
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
                    return g, N_mpz // g, 'FFT', time.time() - t0
        
        for offset in range(-200, 201):
            candidate = period_int + offset
            if candidate > 1 and candidate < N:
                g = gcd(N_mpz, candidate)
                if g > 1 and g < N_mpz:
                    return g, N_mpz // g, 'FFT', time.time() - t0
    
    # مرحله 3: primefac (شامل QS/NFS)
    f, c, elapsed = primefac_factor(N)
    if f is not None:
        return f, c, 'primefac', elapsed
    
    return None, None, None, time.time() - t0

# ============================================================
#  روش 3: ابتکاری - Fermat + FFT + primefac
# ============================================================
def fermat_fft_primefac(N, max_k=65536):
    """
    ترکیب Fermat + FFT + primefac
    Fermat برای فاکتورهای نزدیک
    """
    N_mpz = mpz(N)
    
    # Trial
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N_mpz % p == 0:
            return p, N_mpz // p, 'Trial', 0
    
    # Fermat (برای فاکتورهای نزدیک)
    t0 = time.time()
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
    
    # FFT
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
                    return g, N_mpz // g, 'FFT', time.time() - t0
    
    # primefac (QS/NFS)
    f, c, elapsed = primefac_factor(N)
    if f is not None:
        return f, c, 'primefac', elapsed
    
    return None, None, None, time.time() - t0

# ============================================================
#  تست
# ============================================================
def test_all():
    print("=" * 70)
    print("  تست primefac + روش‌های ابتکاری")
    print("=" * 70)
    
    random.seed(42)
    
    test_groups = [
        ("10 digit", [1000000007, 1000000009, 1000000021, 1000000033]),
        ("12 digit", [1000000000039, 1000000000061, 1000000000063]),
        ("15 digit", [1000000000000037, 1000000000000091, 1000000000000159]),
        ("18 digit", [1000000000000000003, 1000000000000000009, 1000000000000000031]),
        ("20 digit", [10000000000000000039, 10000000000000000051, 10000000000000000061]),
    ]
    
    for group_name, primes in test_groups:
        print(f"\n--- {group_name} ---")
        
        test_cases = []
        for _ in range(3):
            p = random.choice(primes)
            q = random.choice(primes)
            if p != q:
                test_cases.append((p*q, min(p,q), max(p,q)))
        
        for method_name, method_func in [
            ("primefac", lambda N: primefac_factor(N)),
            ("FFT+primefac", lambda N: fft_plus_primefac(N)),
            ("Fermat+FFT+primefac", lambda N: fermat_fft_primefac(N)),
        ]:
            print(f"\n  روش: {method_name}")
            success = 0
            total_time = 0
            
            for N, p, q in test_cases:
                t0 = time.time()
                try:
                    result = method_func(N)
                    if len(result) == 3:
                        f, c, elapsed = result
                        method = method_name
                    else:
                        f, c, method, elapsed = result
                except:
                    f, c, elapsed = None, None, time.time() - t0
                    method = 'error'
                
                total_time += elapsed
                
                if f is not None and f * c == N:
                    success += 1
            
            print(f"    موفق: {success}/{len(test_cases)} ({100*success/len(test_cases):.1f}%)")
            print(f"    زمان: {total_time:.1f}s ({total_time/len(test_cases)*1000:.0f}ms/test)")

if __name__ == "__main__":
    test_all()
