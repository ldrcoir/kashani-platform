#!/usr/bin/env python3
"""
پُر کردن شکست‌های frontier با ECM
استراتژی: 
- بازه‌های ۱۰^23 تا ۱۰^26 (که شکستشون کم‌تر از ۱۰٪ است)
- هر شکست رو با ECM B1=1e7 امتحان می‌کنیم
- اگه پُر شد، frontier رو به جلو می‌بریم
- گزارش کامل ذخیره می‌کنیم
"""
import sys
import os
import time
import json
import subprocess
import random

sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime

ECM_PATH = "/home/z/my-project/ecm-extract/usr/bin/ecm"
LD_PATH = "/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"
OUTPUT_DIR = "/home/z/my-project/download/frontier_fill"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def factor_with_rho(n, max_iter=300000):
    """rho-based factorization"""
    if n == 1: return []
    if n % 2 == 0:
        sub = factor_with_rho(n // 2, max_iter)
        return [2] + sub if sub != [None] else [2, None]
    if is_prime(n): return [int(n)]
    
    factors = []
    remaining = n
    p = 2
    while p * p <= remaining and p < 100000:
        while remaining % p == 0:
            factors.append(p)
            remaining //= p
        p += 1 if p == 2 else 2
    
    if remaining == 1: return sorted(factors)
    if is_prime(remaining):
        factors.append(int(remaining))
        return sorted(factors)
    
    while remaining > 1 and not is_prime(remaining):
        x = mpz(2); y = mpz(2); d = mpz(1)
        f = lambda x: (x*x + 1) % remaining
        for _ in range(max_iter):
            x = f(x); y = f(f(y))
            d = gmpy2.gcd(abs(x - y), remaining)
            if d != 1: break
        if d == remaining or d == 1:
            return sorted(factors) + [None]
        factors.append(int(d))
        remaining //= d
        while remaining % d == 0:
            factors.append(int(d))
            remaining //= d
    
    if remaining > 1:
        factors.append(int(remaining))
    return sorted(factors)


def is_factored_rho(n):
    if n == 1: return True
    if is_prime(n): return True
    return None not in factor_with_rho(n)


def run_ecm(n, B1=10000000, max_curves=60, timeout_per_curve=30):
    """اجرای ECM روی عدد"""
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = LD_PATH + ":" + env.get("LD_LIBRARY_PATH", "")
    
    for i in range(max_curves):
        sigma = random.randint(1, 2**31)
        try:
            result = subprocess.run(
                [ECM_PATH, "-sigma", str(sigma), str(B1)],
                input=str(n),
                capture_output=True, text=True,
                timeout=timeout_per_curve, env=env
            )
            output = result.stdout + result.stderr
            if "Factor found" in output:
                for line in output.split('\n'):
                    if "Factor found" in line:
                        parts = line.strip().split()
                        if parts:
                            try:
                                factor = int(parts[-1])
                                if 1 < factor < n:
                                    return factor, sigma, i + 1
                            except ValueError:
                                pass
        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue
    return None, None, max_curves


def factor_full_ecm(n, max_total_time=180):
    """تلاش کامل: rho + ECM (B1=1e7) + ECM (B1=1e8)"""
    # First try rho
    if is_factored_rho(n):
        return True, factor_with_rho(n), 'rho', 0
    
    # Try ECM B1=1e7
    t0 = time.time()
    f1, sigma, curves = run_ecm(n, B1=10000000, max_curves=60, timeout_per_curve=30)
    if f1:
        cof = n // f1
        if is_prime(cof):
            return True, sorted([f1, int(cof)]), f'ECM B1=1e7 (σ={sigma}, c={curves})', time.time() - t0
        # Recursively factor cofactor
        ok, sub_factors, _, _ = factor_full_ecm(cof, max_total_time - (time.time() - t0))
        if ok:
            return True, [f1] + sub_factors, f'ECM B1=1e7 (σ={sigma}, c={curves})', time.time() - t0
    
    if time.time() - t0 > max_total_time:
        return False, [], 'timeout', time.time() - t0
    
    # Try ECM B1=1e8
    f1, sigma, curves = run_ecm(n, B1=100000000, max_curves=10, timeout_per_curve=120)
    if f1:
        cof = n // f1
        if is_prime(cof):
            return True, sorted([f1, int(cof)]), f'ECM B1=1e8 (σ={sigma}, c={curves})', time.time() - t0
        ok, sub_factors, _, _ = factor_full_ecm(cof, max_total_time - (time.time() - t0))
        if ok:
            return True, [f1] + sub_factors, f'ECM B1=1e8 (σ={sigma}, c={curves})', time.time() - t0
    
    return False, [], 'failed', time.time() - t0


def build_dense_frontier(N_start, N_end, log_file):
    """ساختن frontier متراکم از N_start تا N_end با ECM fallback"""
    t0 = time.time()
    frontier = N_start - 1
    gaps = []
    filled = []
    failed = []
    
    print(f"شروع از {N_start} تا {N_end}")
    with open(log_file, 'w') as log:
        log.write(f"# Frontier fill log\n")
        log.write(f"# Range: {N_start} to {N_end}\n")
        log.write(f"# Start: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for n in range(N_start, N_end + 1):
            n_mpz = mpz(n)
            
            # Quick check: prime?
            if is_prime(n_mpz):
                if n == frontier + 1:
                    frontier = n
                continue
            
            # Try factoring
            ok, factors, method, t_factor = factor_full_ecm(n)
            
            if ok:
                if n == frontier + 1:
                    frontier = n
                filled.append({
                    'n': n,
                    'factors': factors,
                    'method': method,
                    'time': t_factor
                })
                log.write(f"✅ {n} = {' × '.join(map(str, factors))} ({method}, {t_factor:.1f}s)\n")
            else:
                gaps.append(n)
                failed.append({'n': n, 'method': method, 'time': t_factor})
                log.write(f"❌ {n} = unfactored ({method}, {t_factor:.1f}s)\n")
            
            if (n - N_start) % 100 == 0:
                elapsed = time.time() - t0
                print(f"  n={n} ({n - N_start + 1}/{N_end - N_start + 1}, frontier={frontier}, filled={len(filled)}, gaps={len(gaps)}, time={elapsed:.1f}s)")
    
    return frontier, filled, gaps, failed


def main():
    # Build frontier at 10^23 (200 numbers):最容易, ~0.5% gaps
    # Actually let's do MORE numbers (1000) at 10^23 to get a meaningful frontier
    
    print("=" * 80)
    print("پروژه‌ی پُر کردن Frontier — به افتخار Jamshid al-Kashi")
    print("=" * 80)
    
    # Stage 1: Build dense frontier at 10^23 (1000 numbers)
    print("\n--- مرحله ۱: ۱۰۰۰ عدد از ۱۰^23 ---")
    log_file = os.path.join(OUTPUT_DIR, "fill_10to23.log")
    frontier_23, filled_23, gaps_23, failed_23 = build_dense_frontier(
        10**23, 10**23 + 1000, log_file
    )
    print(f"\nنتایج ۱۰^23:")
    print(f"  Frontier: {frontier_23}")
    print(f"  شکست‌های پُر شده: {len(filled_23)}")
    print(f"  شکست‌های باقی‌مانده: {len(gaps_23)}")
    
    # Stage 2: Build dense frontier at 10^24 (1000 numbers)
    print("\n--- مرحله ۲: ۱۰۰۰ عدد از ۱۰^24 ---")
    log_file = os.path.join(OUTPUT_DIR, "fill_10to24.log")
    frontier_24, filled_24, gaps_24, failed_24 = build_dense_frontier(
        10**24, 10**24 + 1000, log_file
    )
    print(f"\nنتایج ۱۰^24:")
    print(f"  Frontier: {frontier_24}")
    print(f"  شکست‌های پُر شده: {len(filled_24)}")
    print(f"  شکست‌های باقی‌مانده: {len(gaps_24)}")
    
    # Save summary
    summary = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'stages': {
            '10^23': {
                'range': f"{10**23} to {10**23 + 1000}",
                'frontier': str(frontier_23),
                'filled_count': len(filled_23),
                'remaining_gaps': len(gaps_23),
                'sample_filled': filled_23[:5],
                'sample_gaps': [str(g) for g in gaps_23[:5]],
            },
            '10^24': {
                'range': f"{10**24} to {10**24 + 1000}",
                'frontier': str(frontier_24),
                'filled_count': len(filled_24),
                'remaining_gaps': len(gaps_24),
                'sample_filled': filled_24[:5],
                'sample_gaps': [str(g) for g in gaps_24[:5]],
            },
        },
        'credited_to': 'EhsanMoradMaryamAlasvandi (FactorDB user: ehsanmorad) — به افتخار Jamshid al-Kashi',
    }
    
    with open(os.path.join(OUTPUT_DIR, "fill_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Final report
    print("\n" + "=" * 80)
    print("گزارش نهایی")
    print("=" * 80)
    print(f"10^23: Frontier = {frontier_23}, پُر شد: {len(filled_23)}, باقی: {len(gaps_23)}")
    print(f"10^24: Frontier = {frontier_24}, پُر شد: {len(filled_24)}, باقی: {len(gaps_24)}")
    print(f"\nفایل‌ها در: {OUTPUT_DIR}/")


if __name__ == '__main__':
    main()
