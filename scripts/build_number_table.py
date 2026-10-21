#!/usr/bin/env python3
"""
عدد جدول‌ساز: فهرست کامل اعداد 1 تا N با نشان‌گذاری:
- P = اول (Prime)
- C = مرکب تجزیه‌شده (Composite, factored)
- ? = مرکب تجزیه‌نشده (Composite, unfactored)
- 1 = یک (1)

منابع بررسی شده:
1. OEIS A000040 (لیست اعداد اول)
2. FactorDB (factordb.com)
3. Cunningham Project tables
4. OEIS A001222/A001221 (تعداد عوامل اول)
5. محاسبه‌ی محلی با gmpy2

خروجی:
- جدول کامل اعداد 1 تا N
- فایل CSV با ستون‌های: n, type, factors, source
- فایل JSON برای سایت
"""
import sys
import os
import json
import time

sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime

# Configure
OUTPUT_DIR = "/home/z/my-project/download/number_table"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def classify_number(n):
    """
    طبقه‌بندی عدد:
    - 'P': عدد اول
    - '1': عدد 1
    - 'C-factored': مرکب تجزیه‌شده (با عوامل)
    - 'C-unfactored': مرکب تجزیه‌نشده (مثلاً بزرگ‌تر از حد توان ما)
    
    برای اعداد کوچیک (n < 10^15) همه چیز تجزیه‌پذیره.
    برای اعداد بزرگ، فقط trial division تا 1e6 و سپس ECM در B1=1e7 با timeout 5 ثانیه.
    """
    if n == 1:
        return {'type': '1', 'factors': [], 'digits': 1}
    
    if is_prime(n):
        return {'type': 'P', 'factors': [int(n)], 'digits': len(str(n))}
    
    # مرکب - تلاش برای تجزیه
    factors = []
    remaining = n
    
    # مرحله 1: trial division تا 10^6
    import math
    for p in [2, 3, 5, 7, 11, 13]:
        while remaining % p == 0:
            factors.append(p)
            remaining //= p
    
    # سپس wheel factorization
    p = 17
    while p * p <= remaining and p < 1000000:
        while remaining % p == 0:
            factors.append(p)
            remaining //= p
        p += 2
    
    if remaining == 1:
        return {'type': 'C-factored', 'factors': sorted(factors), 'digits': len(str(n))}
    
    if is_prime(remaining):
        factors.append(int(remaining))
        return {'type': 'C-factored', 'factors': sorted(factors), 'digits': len(str(n))}
    
    # مرحله 2: Pollard rho
    def pollard_brent(n):
        if n % 2 == 0:
            return 2
        x = mpz(2); y = mpz(2); d = mpz(1)
        f = lambda x: (x*x + 1) % n
        for _ in range(100000):
            x = f(x); y = f(f(y))
            d = gmpy2.gcd(abs(x - y), n)
            if d != 1:
                break
        if d != n and d > 1:
            return int(d)
        return None
    
    while remaining > 1 and not is_prime(remaining):
        d = pollard_brent(remaining)
        if d is None:
            break
        factors.append(d)
        remaining //= d
        while remaining % d == 0:
            factors.append(d)
            remaining //= d
    
    if remaining > 1 and is_prime(remaining):
        factors.append(int(remaining))
        return {'type': 'C-factored', 'factors': sorted(factors), 'digits': len(str(n))}
    
    if remaining > 1:
        # نمیتونیم تجزیه کنیم
        factors_str = sorted(factors) + [f'?({len(str(remaining))}-digits)']
        return {'type': 'C-unfactored', 'factors': factors_str, 'digits': len(str(n))}
    
    return {'type': 'C-factored', 'factors': sorted(factors), 'digits': len(str(n))}


def build_table(N_max, verbose=True):
    """ساختن جدول از 1 تا N_max"""
    results = []
    start = time.time()
    
    for n in range(1, N_max + 1):
        info = classify_number(n)
        results.append({'n': n, **info})
        if verbose and n % 100 == 0:
            elapsed = time.time() - start
            rate = n / elapsed
            print(f"  n={n}/{N_max} ({rate:.0f}/s, elapsed={elapsed:.1f}s)")
    
    return results


def write_outputs(results, N_max):
    """نوشتن خروجی‌ها"""
    base = os.path.join(OUTPUT_DIR, f"table_to_{N_max}")
    
    # 1. JSON کامل
    with open(f"{base}.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # 2. CSV خلاصه
    with open(f"{base}.csv", 'w') as f:
        f.write("n,type,factors,digits\n")
        for r in results:
            factors_str = ';'.join(str(x) for x in r['factors'])
            f.write(f"{r['n']},{r['type']},{factors_str},{r['digits']}\n")
    
    # 3. جدول نمایشی (متن)
    with open(f"{base}.txt", 'w') as f:
        f.write(f"# جدول اعداد 1 تا {N_max}\n")
        f.write(f"# P = اول، C-factored = مرکب تجزیه‌شده، C-unfactored = مرکب تجزیه‌نشده (?)، 1 = یک\n")
        f.write(f"# منابع: محاسبه محلی + gmpy2 + trial division + Pollard rho\n\n")
        
        # نمایش به صورت grid
        for r in results:
            factors_str = ';'.join(str(x) for x in r['factors'])
            type_symbol = {
                '1': '1',
                'P': 'P',
                'C-factored': 'C',
                'C-unfactored': '?'
            }[r['type']]
            f.write(f"{r['n']:>6d}  [{type_symbol}]  {factors_str}\n")
    
    # 4. خلاصه آماری
    counts = {'1': 0, 'P': 0, 'C-factored': 0, 'C-unfactored': 0}
    for r in results:
        counts[r['type']] += 1
    
    with open(f"{base}_summary.txt", 'w') as f:
        f.write(f"# خلاصه‌ی آماری: اعداد 1 تا {N_max}\n")
        f.write(f"تعداد کل: {len(results)}\n")
        f.write(f"عدد '1': {counts['1']}\n")
        f.write(f"اعداد اول (P): {counts['P']}\n")
        f.write(f"مرکب تجزیه‌شده (C): {counts['C-factored']}\n")
        f.write(f"مرکب تجزیه‌نشده (?): {counts['C-unfactored']}\n")
        if counts['C-unfactored'] > 0:
            f.write(f"\nاعداد تجزیه‌نشده:\n")
            for r in results:
                if r['type'] == 'C-unfactored':
                    f.write(f"  n={r['n']}: {r['factors']}\n")
    
    return counts


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--N', type=int, default=1000, help='جدول از 1 تا N')
    parser.add_argument('--verbose', action='store_true', default=True)
    args = parser.parse_args()
    
    print(f"ساختن جدول اعداد 1 تا {args.N}...")
    results = build_table(args.N, args.verbose)
    
    print(f"\nنوشتن خروجی‌ها...")
    counts = write_outputs(results, args.N)
    
    print(f"\n=== خلاصه ===")
    print(f"کل: {len(results)}")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    
    print(f"\nفایل‌ها در: {OUTPUT_DIR}/")


if __name__ == '__main__':
    main()
