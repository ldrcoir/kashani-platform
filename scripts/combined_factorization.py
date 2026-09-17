#!/usr/bin/env python3
"""
روش ترکیبی: FFT + ECM + P-1
============================
ایده:
1. FFT طیفی برای پیدا کردن کاندیداهای فاکتور
2. ECM برای تأیید و پیدا کردن فاکتورهای بزرگ
3. P-1 برای فاکتورهای با k smooth
4. ترکیب همه برای حداکثر شانس

استراتژی:
- FFT سریع کاندیدها رو پیدا می‌کنه
- ECM اگه FFT جواب نده، فاکتورهای بزرگ رو پیدا می‌کنه
- P-1 اگه k smooth باشه
"""

import numpy as np
import gmpy2
from gmpy2 import mpz, gcd, is_prime
import time
import subprocess
import os

ECM = "/home/z/my-project/ecm-extract/usr/bin/ecm"
LD_PATH = "/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"

# ============================================================
#  روش 1: FFT طیفی
# ============================================================
def fft_spectral_factor(N, max_k=131072, num_peaks=1000):
    """
    FFT طیفی برای پیدا کردن کاندیدهای فاکتور
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
        
        # period و ضرایب
        for mult in range(1, 2000):
            candidate = period_int * mult
            if candidate > 1 and candidate < N:
                candidates.add(candidate)
        
        # period ± offset
        for offset in range(-500, 501):
            candidate = period_int + offset
            if candidate > 1 and candidate < N:
                candidates.add(candidate)
    
    # بررسی کاندیدها
    for candidate in candidates:
        g = gcd(N_mpz, candidate)
        if g > 1 and g < N_mpz:
            return g, N_mpz // g, 'FFT'
    
    return None, None, None

# ============================================================
#  روش 2: P-1
# ============================================================
def pm1_factor(N, B1=1000000):
    """P-1 با gmp-ecm"""
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    try:
        with open('/tmp/pm1_test.log', 'w') as out:
            proc = subprocess.Popen(
                [ECM, '-pm1', '-v', str(B1)],
                stdin=subprocess.PIPE,
                stdout=out,
                stderr=subprocess.STDOUT,
                env=env,
                timeout=30
            )
            proc.communicate(input=str(N).encode())
        
        with open('/tmp/pm1_test.log') as f:
            content = f.read()
        
        if 'Factor found' in content or 'found' in content.lower():
            import re
            matches = re.findall(r'(\d{10,})', content)
            for m in matches:
                f = mpz(m)
                if f > 1 and f < N and N % f == 0:
                    return f, N // f, 'P-1'
    except:
        pass
    
    return None, None, None

# ============================================================
#  روش 3: ECM
# ============================================================
def ecm_factor(N, B1=1000000, curves=100):
    """ECM با gmp-ecm"""
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    try:
        with open('/tmp/ecm_test.log', 'w') as out:
            proc = subprocess.Popen(
                [ECM, '-c', str(curves), str(B1)],
                stdin=subprocess.PIPE,
                stdout=out,
                stderr=subprocess.STDOUT,
                env=env,
                timeout=30
            )
            proc.communicate(input=str(N).encode())
        
        with open('/tmp/ecm_test.log') as f:
            content = f.read()
        
        if 'Factor found' in content or 'found' in content.lower():
            import re
            matches = re.findall(r'(\d{10,})', content)
            for m in matches:
                f = mpz(m)
                if f > 1 and f < N and N % f == 0:
                    return f, N // f, 'ECM'
    except:
        pass
    
    return None, None, None

# ============================================================
#  روش 4: ترکیبی
# ============================================================
def combined_factor(N, max_k=131072):
    """
    روش ترکیبی:
    1. FFT سریع (اگه فاکتور کوچک باشه)
    2. P-1 (اگه k smooth باشه)
    3. ECM (برای فاکتورهای متوسط)
    """
    methods_tried = []
    
    # مرحله 1: FFT
    t0 = time.time()
    factor, cofactor, method = fft_spectral_factor(N, max_k=max_k)
    elapsed = time.time() - t0
    methods_tried.append(('FFT', elapsed, factor is not None))
    
    if factor is not None:
        return factor, cofactor, 'FFT', methods_tried
    
    # مرحله 2: P-1 با B1 کوچک
    t0 = time.time()
    factor, cofactor, method = pm1_factor(N, B1=100000)
    elapsed = time.time() - t0
    methods_tried.append(('P-1 B1=1e5', elapsed, factor is not None))
    
    if factor is not None:
        return factor, cofactor, 'P-1', methods_tried
    
    # مرحله 3: ECM با B1 کوچک
    t0 = time.time()
    factor, cofactor, method = ecm_factor(N, B1=50000, curves=50)
    elapsed = time.time() - t0
    methods_tried.append(('ECM B1=5e4', elapsed, factor is not None))
    
    if factor is not None:
        return factor, cofactor, 'ECM', methods_tried
    
    # مرحله 4: P-1 با B1 بزرگ‌تر
    t0 = time.time()
    factor, cofactor, method = pm1_factor(N, B1=1000000)
    elapsed = time.time() - t0
    methods_tried.append(('P-1 B1=1e6', elapsed, factor is not None))
    
    if factor is not None:
        return factor, cofactor, 'P-1', methods_tried
    
    # مرحله 5: ECM با B1 بزرگ‌تر
    t0 = time.time()
    factor, cofactor, method = ecm_factor(N, B1=1000000, curves=100)
    elapsed = time.time() - t0
    methods_tried.append(('ECM B1=1e6', elapsed, factor is not None))
    
    if factor is not None:
        return factor, cofactor, 'ECM', methods_tried
    
    return None, None, None, methods_tried

# ============================================================
#  تست
# ============================================================
def test_combined():
    print("=" * 70)
    print("  تست روش ترکیبی: FFT + P-1 + ECM")
    print("=" * 70)
    
    import random
    random.seed(42)
    
    # اعداد اول با اندازه‌های مختلف
    test_groups = [
        ("5 digit (10007-10193)", [10007, 10009, 10037, 10039, 10061, 10067, 10069, 10079, 10091, 10093, 10099, 10103, 10111, 10133, 10139, 10141, 10151, 10159, 10163, 10169, 10177, 10181, 10193]),
        ("6 digit (100003-100151)", [100003, 100019, 100043, 100049, 100057, 100069, 100103, 100109, 100129, 100151]),
        ("7 digit (1000003-1000099)", [1000003, 1000033, 1000037, 1000039, 1000081, 1000099]),
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
        fail = 0
        method_stats = {}
        total_time = 0
        
        for N, p, q in test_cases:
            t0 = time.time()
            factor, cofactor, method, methods_tried = combined_factor(N, max_k=131072)
            elapsed = time.time() - t0
            total_time += elapsed
            
            if factor is not None and factor * cofactor == N:
                success += 1
                method_stats[method] = method_stats.get(method, 0) + 1
            else:
                fail += 1
        
        print(f"  موفق: {success}/{len(test_cases)} ({100*success/len(test_cases):.1f}%)")
        print(f"  زمان کل: {total_time:.1f}s ({total_time/len(test_cases)*1000:.0f}ms/test)")
        print(f"  روش‌های موفق: {method_stats}")

if __name__ == "__main__":
    test_combined()
