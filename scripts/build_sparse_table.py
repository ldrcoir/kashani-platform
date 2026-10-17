#!/usr/bin/env python3
"""
جدول اعداد بزرگ با نشان‌گذاری جای خالی
- برای اعداد کوچیک‌تر از 10^12: کاملاً تجزیه می‌شه (P یا C)
- برای اعداد بزرگ‌تر: با trial division تا 10^6 و Pollard rho با 100K iters
- اگه فاکتور پیدا نشد، علامت ? می‌ذاریم

مثال: برای جدول اعداد 10^60 تا 10^60 + 100
"""
import sys
import os
import json
import time
import argparse

sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod

OUTPUT_DIR = "/home/z/my-project/download/number_table"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def classify_with_ecm(n, max_effort='medium'):
    """طبقه‌بندی با تلاش بیشتر برای اعداد بزرگ"""
    if n == 1:
        return {'type': '1', 'factors': [], 'digits': 1, 'note': ''}
    if is_prime(n):
        return {'type': 'P', 'factors': [int(n)], 'digits': len(str(n)), 'note': 'prime'}
    
    factors = []
    remaining = n
    
    # trial division تا 10^6
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        while remaining % p == 0:
            factors.append(p)
            remaining //= p
    
    # wheel
    p = 37
    while p * p <= remaining and p < 1000000:
        while remaining % p == 0:
            factors.append(p)
            remaining //= p
        p += 2
    
    if remaining == 1:
        return {'type': 'C', 'factors': sorted(set(factors)), 'digits': len(str(n)), 'note': 'factored-trial'}
    
    if is_prime(remaining):
        factors.append(int(remaining))
        return {'type': 'C', 'factors': sorted(set(factors)), 'digits': len(str(n)), 'note': 'factored'}
    
    # Pollard rho
    def pollard_brent(n, max_iter=200000):
        if n % 2 == 0:
            return 2
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
    
    while remaining > 1 and not is_prime(remaining):
        d = pollard_brent(remaining, 200000)
        if d is None:
            break
        factors.append(d)
        remaining //= d
        while remaining % d == 0:
            factors.append(d)
            remaining //= d
    
    if remaining > 1 and is_prime(remaining):
        factors.append(int(remaining))
        return {'type': 'C', 'factors': sorted(set(factors)), 'digits': len(str(n)), 'note': 'factored-rho'}
    
    if remaining > 1:
        # تجزیه‌نشده
        factors_str = sorted(set(factors)) + [f'?({len(str(remaining))}-digits)']
        return {'type': '?', 'factors': factors_str, 'digits': len(str(n)), 'note': 'unfactored'}
    
    return {'type': 'C', 'factors': sorted(set(factors)), 'digits': len(str(n)), 'note': 'factored'}


def build_sparse_table(start, count, verbose=True):
    """ساختن جدول برای اعداد بزرگ [start, start + count)"""
    results = []
    t0 = time.time()
    
    for i in range(count):
        n = start + i
        info = classify_with_ecm(n)
        results.append({'n': n, **info})
        if verbose and (i + 1) % 10 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            print(f"  i={i+1}/{count}, n={n}, rate={rate:.2f}/s, elapsed={elapsed:.1f}s")
    
    return results


def write_sparse_outputs(results, start, count):
    base = os.path.join(OUTPUT_DIR, f"sparse_{start}_to_{start + count - 1}")
    
    with open(f"{base}.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    with open(f"{base}.txt", 'w') as f:
        f.write(f"# جدول اعداد {start} تا {start + count - 1}\n")
        f.write(f"# P = اول، C = مرکب تجزیه‌شده، ? = مرکب تجزیه‌نشده\n\n")
        for r in results:
            factors_str = ';'.join(str(x) for x in r['factors'])
            type_symbol = {'1': '1', 'P': 'P', 'C': 'C', '?': '?'}[r['type']]
            f.write(f"{r['n']}  [{type_symbol}]  {r['digits']} digits  {factors_str}\n")
    
    # آمار
    counts = {'1': 0, 'P': 0, 'C': 0, '?': 0}
    for r in results:
        counts[r['type']] += 1
    
    with open(f"{base}_summary.txt", 'w') as f:
        f.write(f"خلاصه اعداد {start} تا {start + count - 1}:\n")
        for k, v in counts.items():
            f.write(f"  {k}: {v}\n")
    
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, required=True, help='عدد شروع')
    parser.add_argument('--count', type=int, default=100, help='تعداد اعداد')
    args = parser.parse_args()
    
    print(f"ساختن جدول اعداد {args.start} تا {args.start + args.count - 1}...")
    results = build_sparse_table(args.start, args.count)
    counts = write_sparse_outputs(results, args.start, args.count)
    
    print(f"\n=== خلاصه ===")
    for k, v in counts.items():
        print(f"  {k}: {v}")


if __name__ == '__main__':
    main()
