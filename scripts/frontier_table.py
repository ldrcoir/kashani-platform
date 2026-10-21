#!/usr/bin/env python3
"""
ساختن جدول پیوسته‌ی اعداد اول و مرکب
- Frontier = آخرین عددی که همه‌ی اعداد 1..N یا اول هستن یا تجزیه شدن
- روش: rho با 100K iterations
- اعداد 1 تا 1M رو با rho کامل تجزیه می‌کنیم (سریع)
- اعداد 10^10 تا 10^50 رو با rho تست می‌کنیم (نمونه‌گیری)

خروجی: جدول کامل با frontier و gaps
"""
import sys
import os
import json
import time

sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime

OUTPUT_DIR = "/home/z/my-project/download/frontier_table"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def factor_with_rho(n, max_iter=100000):
    if n == 1: return []
    if n % 2 == 0:
        sub = factor_with_rho(n // 2, max_iter)
        return [2] + sub if sub != [None] else [2, None]
    if is_prime(n): return [int(n)]
    
    factors = []
    remaining = n
    
    # trial division تا 10^5
    p = 2
    while p * p <= remaining and p < 100000:
        while remaining % p == 0:
            factors.append(p)
            remaining //= p
        p += 1 if p == 2 else 2
    
    if remaining == 1:
        return sorted(factors)
    if is_prime(remaining):
        factors.append(int(remaining))
        return sorted(factors)
    
    # Pollard rho
    while remaining > 1 and not is_prime(remaining):
        x = mpz(2); y = mpz(2); d = mpz(1)
        f = lambda x: (x*x + 1) % remaining
        for _ in range(max_iter):
            x = f(x); y = f(f(y))
            d = gmpy2.gcd(abs(x - y), remaining)
            if d != 1:
                break
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


def classify(n):
    """طبقه‌بندی: 'P', 'C-fact', 'C-unfact', '1'"""
    if n == 1:
        return '1', []
    if is_prime(n):
        return 'P', [int(n)]
    factors = factor_with_rho(n)
    if None in factors:
        return '?', [f for f in factors if f is not None]
    return 'C', factors


def build_dense_table(N_max):
    """جدول 1 تا N_max با frontier tracking"""
    results = []
    frontier = 0
    gaps = []
    
    for n in range(1, N_max + 1):
        type_, factors = classify(n)
        results.append({'n': n, 'type': type_, 'factors': factors})
        
        if type_ != '?':
            if n == frontier + 1 or n == 1:
                frontier = n
        else:
            gaps.append(n)
    
    return results, frontier, gaps


def build_sparse_table(start, count):
    """جدول برای [start, start+count)"""
    results = []
    frontier = 0
    gaps = []
    
    for i in range(count):
        n = start + i
        type_, factors = classify(n)
        results.append({'n': n, 'type': type_, 'factors': factors})
        
        if type_ != '?':
            if i == 0 or frontier == i:
                frontier = i + 1
        else:
            gaps.append((i, n))
    
    return results, frontier, gaps


def main():
    print("=" * 70)
    print("جدول پیوسته‌ی اعداد ۱ تا ۱ میلیون")
    print("=" * 70)
    t0 = time.time()
    results, frontier, gaps = build_dense_table(1000000)
    print(f"تمام در {time.time()-t0:.1f}s")
    print(f"Frontier: {frontier}")
    print(f"Gaps: {len(gaps)}")
    
    # ذخیره
    base = os.path.join(OUTPUT_DIR, "table_1_to_1M")
    with open(f"{base}.json", 'w') as f:
        json.dump({'frontier': frontier, 'gaps': gaps, 'sample_results': results[:200], 'total_count': len(results)}, f, indent=2)
    
    with open(f"{base}_summary.txt", 'w') as f:
        counts = {'1': 0, 'P': 0, 'C': 0, '?': 0}
        for r in results:
            counts[r['type']] += 1
        f.write(f"جدول اعداد ۱ تا ۱,۰۰۰,۰۰۰\n")
        f.write(f"============================\n")
        f.write(f"تعداد کل: {len(results)}\n")
        f.write(f"  عدد '1': {counts['1']}\n")
        f.write(f"  اعداد اول (P): {counts['P']}\n")
        f.write(f"  مرکب تجزیه‌شده (C): {counts['C']}\n")
        f.write(f"  مرکب تجزیه‌نشده (?): {counts['?']}\n")
        f.write(f"\nFrontier (پیوستگی): {frontier}\n")
        f.write(f"Gaps: {len(gaps)}\n")
    
    print(f"\nفایل‌ها در: {OUTPUT_DIR}/")
    
    # حالا اعداد بزرگ‌تر رو تست کن
    print("\n" + "=" * 70)
    print("تست frontier در اعداد بزرگ (۳۰ نمونه در هر ۱۰^k)")
    print("=" * 70)
    
    sparse_results = {}
    for k in [10, 15, 20, 25, 30, 35, 40, 45, 50]:
        start = 10 ** k
        t0 = time.time()
        res, frontier, gaps = build_sparse_table(start, 30)
        sparse_results[k] = {
            'start': str(start),
            'frontier_in_30': frontier,
            'gaps_count': len(gaps),
            'first_gap': str(gaps[0][1]) if gaps else None,
            'time': time.time() - t0,
        }
        print(f"10^{k}: frontier={frontier}/30, gaps={len(gaps)}, time={time.time()-t0:.2f}s")
    
    with open(os.path.join(OUTPUT_DIR, "sparse_frontiers.json"), 'w') as f:
        json.dump(sparse_results, f, indent=2)


if __name__ == '__main__':
    main()
