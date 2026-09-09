#!/usr/bin/env python3
"""
روش ترکیبی: FFT + Pollard Rho + Trial Division
==============================================
چون ECM مشکل داره، از Pollard Rho استفاده می‌کنیم
"""

import numpy as np
import gmpy2
from gmpy2 import mpz, gcd, is_prime
import time
import random

def fft_spectral_factor(N, max_k=131072, num_peaks=1000):
    """FFT طیفی"""
    N_mpz = mpz(N)
    
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
    peak_indices = np.argsort(mag_for_peaks)[-num_peaks:][::-1]
    
    candidates = set()
    for idx in peak_indices:
        freq = freqs[idx]
        if freq == 0:
            continue
        period = 1.0 / freq
        period_int = int(round(period))
        
        for mult in range(1, 2000):
            candidate = period_int * mult
            if candidate > 1 and candidate < N:
                candidates.add(candidate)
        
        for offset in range(-500, 501):
            candidate = period_int + offset
            if candidate > 1 and candidate < N:
                candidates.add(candidate)
    
    for candidate in candidates:
        g = gcd(N_mpz, candidate)
        if g > 1 and g < N_mpz:
            return g, N_mpz // g, 'FFT'
    
    return None, None, None

def pollard_rho(N, max_iter=1000000):
    """Pollard Rho"""
    if N % 2 == 0:
        return 2, N // 2, 'Rho'
    
    N_mpz = mpz(N)
    
    for c in range(1, 100):
        x = mpz(2)
        y = mpz(2)
        d = mpz(1)
        f = lambda x: (x * x + c) % N_mpz
        
        for _ in range(max_iter):
            x = f(x)
            y = f(f(y))
            d = gcd(abs(x - y), N_mpz)
            
            if d > 1 and d < N_mpz:
                return d, N_mpz // d, 'Rho'
            if d == N_mpz:
                break
    
    return None, None, None

def trial_division(N, limit=100000):
    """Trial Division"""
    N_mpz = mpz(N)
    
    # اعداد اول کوچک
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]:
        if N_mpz % p == 0:
            return p, N_mpz // p, 'Trial'
    
    # اعداد فرد
    for p in range(101, min(limit, int(N**0.5) + 1), 2):
        if N_mpz % p == 0:
            return p, N_mpz // p, 'Trial'
    
    return None, None, None

def combined_factor(N, max_k=131072):
    """
    روش ترکیبی:
    1. Trial Division (سریع برای فاکتورهای کوچک)
    2. FFT (برای فاکتورهای متوسط)
    3. Pollard Rho (برای فاکتورهای بزرگ‌تر)
    """
    methods_tried = []
    
    # مرحله 1: Trial Division
    t0 = time.time()
    factor, cofactor, method = trial_division(N, limit=10000)
    elapsed = time.time() - t0
    methods_tried.append(('Trial', elapsed, factor is not None))
    
    if factor is not None:
        return factor, cofactor, 'Trial', methods_tried
    
    # مرحله 2: FFT
    t0 = time.time()
    factor, cofactor, method = fft_spectral_factor(N, max_k=max_k)
    elapsed = time.time() - t0
    methods_tried.append(('FFT', elapsed, factor is not None))
    
    if factor is not None:
        return factor, cofactor, 'FFT', methods_tried
    
    # مرحله 3: Pollard Rho
    t0 = time.time()
    factor, cofactor, method = pollard_rho(N, max_iter=100000)
    elapsed = time.time() - t0
    methods_tried.append(('Rho', elapsed, factor is not None))
    
    if factor is not None:
        return factor, cofactor, 'Rho', methods_tried
    
    # مرحله 4: Pollard Rho با iterations بیشتر
    t0 = time.time()
    factor, cofactor, method = pollard_rho(N, max_iter=1000000)
    elapsed = time.time() - t0
    methods_tried.append(('Rho-long', elapsed, factor is not None))
    
    if factor is not None:
        return factor, cofactor, 'Rho', methods_tried
    
    return None, None, None, methods_tried

def test_combined():
    print("=" * 70)
    print("  تست روش ترکیبی: Trial + FFT + Pollard Rho")
    print("=" * 70)
    
    random.seed(42)
    
    test_groups = [
        ("5 digit", [10007, 10009, 10037, 10039, 10061, 10067, 10069, 10079, 10091, 10093]),
        ("6 digit", [100003, 100019, 100043, 100049, 100057, 100069, 100103, 100109, 100129, 100151]),
        ("7 digit", [1000003, 1000033, 1000037, 1000039, 1000081, 1000099]),
        ("8 digit", [10000019, 10000079, 10000103, 10000121, 10000139, 10000141]),
    ]
    
    for group_name, primes in test_groups:
        print(f"\n--- {group_name} ---")
        
        test_cases = []
        for _ in range(10):
            p = random.choice(primes)
            q = random.choice(primes)
            if p != q:
                test_cases.append((p*q, min(p,q), max(p,q)))
        
        success = 0
        method_stats = {}
        total_time = 0
        
        for N, p, q in test_cases:
            t0 = time.time()
            factor, cofactor, method, methods_tried = combined_factor(N)
            elapsed = time.time() - t0
            total_time += elapsed
            
            if factor is not None and factor * cofactor == N:
                success += 1
                method_stats[method] = method_stats.get(method, 0) + 1
        
        print(f"  موفق: {success}/{len(test_cases)} ({100*success/len(test_cases):.1f}%)")
        print(f"  زمان: {total_time:.1f}s ({total_time/len(test_cases)*1000:.0f}ms/test)")
        print(f"  روش‌ها: {method_stats}")

if __name__ == "__main__":
    test_combined()
