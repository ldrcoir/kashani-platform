#!/usr/bin/env python3
"""
ساختن جدول کامل از 1 تا N (پیش‌فرض 10000) و گزارش "تاریخچه فکتورینگ"

این جدول نشون می‌ده:
- کجا تا الان تجزیه شده
- کجا "جای خالی" داریم (عدد مرکب بزرگ که با روش‌های ساده تجزیه نشده)
- کجا "بسته شد" (آخرین عدد پیوسته که تجزیه شده)

خروجی‌ها:
- table_complete.json: جدول کامل
- gaps.txt: لیست جای خالی‌ها
- frontier.txt: مرز فعلی (آخرین عدد پیوسته‌ای که تجزیه شده)
"""
import sys
import os
import json
import time
import argparse

sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime

OUTPUT_DIR = "/home/z/my-project/download/number_table"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def factor_with_rho(n, max_iter=200000):
    """Pollard rho با 200K iterations"""
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    x = mpz(2); y = mpz(2); d = mpz(1)
    f = lambda x: (x*x + 1) % n
    for _ in range(max_iter):
        x = f(x); y = f(f(y))
        d = gmpy2.gcd(abs(x - y), n)
        if d != 1:
            break
    if d != n and d > 1:
        return int(d)
    return None


def factor_full(n, max_rho_iter=200000):
    """تجزیه‌ی کامل با trial division + rho"""
    if n == 1:
        return []
    if is_prime(n):
        return [int(n)]
    
    factors = []
    remaining = n
    
    # trial division تا 10^6
    p = 2
    while p * p <= remaining and p < 1000000:
        while remaining % p == 0:
            factors.append(p)
            remaining //= p
        p = p + 1 if p == 2 else p + 2
    
    if remaining == 1:
        return sorted(factors)
    
    if is_prime(remaining):
        factors.append(int(remaining))
        return sorted(factors)
    
    # Pollard rho
    while remaining > 1 and not is_prime(remaining):
        d = factor_with_rho(remaining, max_rho_iter)
        if d is None:
            break
        factors.append(d)
        remaining //= d
        while remaining % d == 0:
            factors.append(d)
            remaining //= d
    
    if remaining > 1 and is_prime(remaining):
        factors.append(int(remaining))
        return sorted(factors)
    
    if remaining > 1:
        # تجزیه نشد
        return sorted(factors) + [None]  # None = unfactored
    
    return sorted(factors)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--N', type=int, default=10000, help='جدول از 1 تا N')
    parser.add_argument('--start', type=int, default=1, help='شروع (پیش‌فرض 1)')
    parser.add_argument('--verbose', action='store_true', default=True)
    args = parser.parse_args()
    
    start = args.start
    end = args.N
    
    print(f"ساختن جدول {start} تا {end} ({end - start + 1} عدد)...")
    
    results = []
    gaps = []  # اعداد تجزیه‌نشده
    frontier = start - 1  # آخرین عدد پیوسته تجزیه‌شده
    
    t0 = time.time()
    
    for n in range(start, end + 1):
        n_mpz = mpz(n)
        if n == 1:
            results.append({'n': 1, 'type': '1', 'factors': []})
            frontier = 1
            continue
        
        if is_prime(n_mpz):
            results.append({'n': n, 'type': 'P', 'factors': [n]})
            if n == frontier + 1:
                frontier = n
            continue
        
        factors = factor_full(n_mpz)
        
        if None in factors:
            # تجزیه‌نشده
            results.append({'n': n, 'type': '?', 'factors': factors, 'note': 'unfactored'})
            gaps.append(n)
        else:
            results.append({'n': n, 'type': 'C', 'factors': factors})
            # frontier فقط تا جایی که پیوسته تجزیه شده
            if n == frontier + 1:
                frontier = n
            else:
                # اگه از قبل جای خالی بوده، frontier نمی‌ره جلو
                pass
        
        if args.verbose and n % 1000 == 0:
            elapsed = time.time() - t0
            rate = (n - start + 1) / elapsed
            print(f"  n={n} ({rate:.0f}/s, elapsed={elapsed:.1f}s, frontier={frontier})")
    
    elapsed = time.time() - t0
    print(f"\nتمام در {elapsed:.1f}s")
    
    # نوشتن خروجی‌ها
    base = os.path.join(OUTPUT_DIR, f"complete_{start}_to_{end}")
    
    with open(f"{base}.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    with open(f"{base}.txt", 'w') as f:
        f.write(f"# جدول اعداد {start} تا {end}\n")
        f.write(f"# P = اول، C = مرکب تجزیه‌شده، ? = مرکب تجزیه‌نشده\n\n")
        for r in results:
            factors_str = ';'.join(str(x) if x is not None else '?' for x in r['factors'])
            type_symbol = {'1': '1', 'P': 'P', 'C': 'C', '?': '?'}[r['type']]
            f.write(f"{r['n']:>8d}  [{type_symbol}]  {factors_str}\n")
    
    with open(f"{base}_gaps.txt", 'w') as f:
        f.write(f"# اعداد تجزیه‌نشده (gaps) در بازه {start}-{end}\n")
        f.write(f"# تعداد: {len(gaps)}\n\n")
        for n in gaps:
            f.write(f"{n}\n")
    
    with open(f"{base}_summary.txt", 'w') as f:
        counts = {'1': 0, 'P': 0, 'C': 0, '?': 0}
        for r in results:
            counts[r['type']] += 1
        f.write(f"خلاصه جدول {start}-{end}:\n")
        f.write(f"  کل: {len(results)}\n")
        for k, v in counts.items():
            f.write(f"  {k}: {v}\n")
        f.write(f"\n  مرز فعلی (frontier): {frontier}\n")
        f.write(f"  تعداد gap: {len(gaps)}\n")
        if gaps:
            f.write(f"  اولین gap: {gaps[0]}\n")
            f.write(f"  آخرین gap: {gaps[-1]}\n")
    
    print(f"\n=== خلاصه ===")
    counts = {'1': 0, 'P': 0, 'C': 0, '?': 0}
    for r in results:
        counts[r['type']] += 1
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print(f"\n  مرز فعلی: {frontier}")
    print(f"  تعداد gap: {len(gaps)}")
    if gaps:
        print(f"  اولین gap: {gaps[0]}")
    
    print(f"\nفایل‌ها در: {OUTPUT_DIR}/")


if __name__ == '__main__':
    main()
