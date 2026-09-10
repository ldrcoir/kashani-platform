#!/usr/bin/env python3
"""
روش‌های ابتکاری + msieve (NFS/QS)
=================================
1. msieve برای فاکتوریزاسیون (QS/NFS)
2. روش‌های ابتکاری:
   a. FFT هوشمند
   b. Fermat تطبیقی
   c. تحلیل ساختار N
   d. ترکیب همه
"""

import gmpy2
from gmpy2 import mpz, gcd, isqrt, iroot, is_prime, powmod
import numpy as np
import subprocess
import os
import time
import random
import json

MSIEVE = "/tmp/msieve-master/msieve"
LD_PATH = "/tmp/gmp-dev/usr/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu"

WORKDIR = "/home/z/my-project/A136030_factorization_tests"
os.makedirs(WORKDIR, exist_ok=True)

LOG_FILE = f"{WORKDIR}/test.log"
RESULTS_FILE = f"{WORKDIR}/results.json"

def log(msg):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")

# ============================================================
#  روش 1: msieve (QS/NFS)
# ============================================================
def msieve_factor(N, timeout=300):
    """فاکتوریزاسیون با msieve"""
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    t0 = time.time()
    try:
        proc = subprocess.run(
            [MSIEVE, '-v', '-e', str(N)],
            capture_output=True,
            env=env,
            timeout=timeout
        )
        output = proc.stdout.decode() + proc.stderr.decode()
        elapsed = time.time() - t0
        
        # استخراج فاکتورها
        factors = []
        for line in output.split('\n'):
            if 'factor:' in line:
                parts = line.split('factor:')
                if len(parts) > 1:
                    f = parts[1].strip()
                    if f.isdigit():
                        factors.append(int(f))
        
        if len(factors) >= 2:
            return factors[0], N // factors[0], elapsed
        
        return None, None, elapsed
    except subprocess.TimeoutExpired:
        return None, None, time.time() - t0
    except Exception as e:
        return None, None, time.time() - t0

# ============================================================
#  روش 2: FFT طیفی هوشمند
# ============================================================
def fft_smart_factor(N, max_k=65536):
    """FFT طیفی هوشمند"""
    N_mpz = mpz(N)
    
    # Trial Division سریع
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N_mpz % p == 0:
            return p, N_mpz // p, 0
    
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
                    return g, N_mpz // g, time.time() - t0
        
        for offset in range(-200, 201):
            candidate = period_int + offset
            if candidate > 1 and candidate < N:
                g = gcd(N_mpz, candidate)
                if g > 1 and g < N_mpz:
                    return g, N_mpz // g, time.time() - t0
    
    return None, None, time.time() - t0

# ============================================================
#  روش 3: Fermat تطبیقی
# ============================================================
def fermat_adaptive_factor(N, max_delta=1000000):
    """Fermat با delta تطبیقی"""
    N_mpz = mpz(N)
    
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N_mpz % p == 0:
            return p, N_mpz // p, 0
    
    t0 = time.time()
    a = isqrt(N_mpz)
    if a * a < N_mpz:
        a += 1
    
    for delta in range(max_delta):
        a_test = a + delta
        b_squared = a_test * a_test - N_mpz
        if b_squared >= 0:
            b, is_perfect = iroot(b_squared, 2)
            if is_perfect:
                f1 = a_test + b
                f2 = a_test - b
                if f1 > 1 and f2 > 1:
                    return f1, f2, time.time() - t0
    
    return None, None, time.time() - t0

# ============================================================
#  روش 4: ابتکاری - تحلیل ساختار N
# ============================================================
def structural_factor(N):
    """
    روش ابتکاری: تحلیل ساختار N
    - بررسی N mod (اعداد به فرم خاص)
    - استفاده از الگوی Cunningham
    - بررسی فاکتورهای به فرم 6k±1
    """
    N_mpz = mpz(N)
    t0 = time.time()
    
    # اعداد اول کوچک
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N_mpz % p == 0:
            return p, N_mpz // p, 0
    
    # اعداد به فرم 6k±1 (برای فاکتورهای متوسط)
    for k in range(1, 1000000):
        for candidate in [6*k - 1, 6*k + 1]:
            if candidate > 1 and candidate < N and N_mpz % candidate == 0:
                return candidate, N_mpz // candidate, time.time() - t0
    
    return None, None, time.time() - t0

# ============================================================
#  روش 5: ترکیب نهایی
# ============================================================
def ultimate_factor_v2(N, timeout=300):
    """
    ترکیب نهایی:
    1. Trial Division
    2. FFT طیفی
    3. Fermat تطبیقی
    4. msieve (QS/NFS)
    """
    N_mpz = mpz(N)
    methods_tried = []
    
    # 1. Trial
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N_mpz % p == 0:
            methods_tried.append(('Trial', 0, True))
            return p, N_mpz // p, 'Trial', methods_tried
    
    # 2. FFT
    t0 = time.time()
    f, c, elapsed = fft_smart_factor(N)
    methods_tried.append(('FFT', elapsed, f is not None))
    if f is not None:
        return f, c, 'FFT', methods_tried
    
    # 3. Fermat
    t0 = time.time()
    f, c, elapsed = fermat_adaptive_factor(N, max_delta=100000)
    methods_tried.append(('Fermat', elapsed, f is not None))
    if f is not None:
        return f, c, 'Fermat', methods_tried
    
    # 4. msieve
    t0 = time.time()
    f, c, elapsed = msieve_factor(N, timeout=timeout)
    methods_tried.append(('msieve', elapsed, f is not None))
    if f is not None:
        return f, c, 'msieve', methods_tried
    
    return None, None, None, methods_tried

# ============================================================
#  تست همه روش‌ها
# ============================================================
def test_all_methods():
    log("=" * 70)
    log("  تست همه روش‌ها: msieve + FFT + Fermat + ساختاری")
    log("=" * 70)
    
    random.seed(42)
    
    # اعداد تست با اندازه‌های مختلف
    test_groups = [
        ("10 digit", [1000000007, 1000000009, 1000000021, 1000000033]),
        ("15 digit", [1000000000000037, 1000000000000091, 1000000000000159]),
        ("20 digit", [10000000000000000039, 10000000000000000051]),
        ("25 digit", [10000000000000000000000061, 10000000000000000000000097]),
        ("30 digit", [1000000000000000000000000000037, 1000000000000000000000000000091]),
    ]
    
    all_results = {}
    
    for group_name, primes in test_groups:
        log(f"\n--- {group_name} ---")
        
        test_cases = []
        for _ in range(3):
            p = random.choice(primes)
            q = random.choice(primes)
            if p != q:
                test_cases.append((p*q, min(p,q), max(p,q)))
        
        group_results = {
            'test_cases': len(test_cases),
            'methods': {}
        }
        
        for method_name, method_func in [
            ("msieve", lambda N: msieve_factor(N, timeout=60)),
            ("FFT", lambda N: fft_smart_factor(N)),
            ("Fermat", lambda N: fermat_adaptive_factor(N, max_delta=100000)),
            ("Ultimate", lambda N: ultimate_factor_v2(N, timeout=60)),
        ]:
            success = 0
            total_time = 0
            
            for N, p, q in test_cases:
                try:
                    result = method_func(N)
                    if isinstance(result, tuple) and len(result) == 3:
                        f, c, elapsed = result
                    elif isinstance(result, tuple) and len(result) == 4:
                        f, c, method, methods_tried = result
                        elapsed = sum(m[1] for m in methods_tried)
                    else:
                        f, c, elapsed = None, None, 0
                except:
                    f, c, elapsed = None, None, 0
                
                total_time += elapsed
                
                if f is not None and f * c == N:
                    success += 1
            
            pct = 100 * success / len(test_cases) if test_cases else 0
            avg_time = total_time / len(test_cases) if test_cases else 0
            
            group_results['methods'][method_name] = {
                'success': success,
                'total': len(test_cases),
                'percentage': pct,
                'avg_time': avg_time
            }
            
            log(f"  {method_name}: {success}/{len(test_cases)} ({pct:.0f}%) - {avg_time:.2f}s/test")
        
        all_results[group_name] = group_results
    
    # ذخیره نتایج
    with open(RESULTS_FILE, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    log(f"\nنتایج ذخیره شد: {RESULTS_FILE}")
    
    # خلاصه
    log(f"\n{'='*70}")
    log(f"  خلاصه نتایج")
    log(f"{'='*70}")
    log(f"\n{'گروه':<15} {'روش':<12} {'موفقیت':<10} {'زمان':<10}")
    log(f"{'-'*50}")
    
    for group_name, group_data in all_results.items():
        for method_name, method_data in group_data['methods'].items():
            log(f"{group_name:<15} {method_name:<12} "
                f"{method_data['success']}/{method_data['total']} ({method_data['percentage']:.0f}%)   "
                f"{method_data['avg_time']:.2f}s")

if __name__ == "__main__":
    test_all_methods()
