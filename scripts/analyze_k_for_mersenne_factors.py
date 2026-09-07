#!/usr/bin/env python3
"""
تحلیل k برای فاکتورهای اول اعداد مرسن مرکب
==========================================
برای هر فاکتور اول q از M(p):
- محاسبه k = (q-1) / (2*p)
- محاسبه تعداد ارقام k
- بررسی آیا k اول هست یا مرکب
- بررسی الگوی افزایشی: آیا k با بزرگ‌تر شدن p بزرگ‌تر می‌شه؟

خروجی: جدول با ستون‌های:
- p (توان مرسن)
- index (شماره در لیست composite)
- q (فاکتور اول)
- ارقام q
- k
- ارقام k
- k اول؟
"""

import json
import gmpy2
from gmpy2 import mpz, is_prime
import os

CACHE_FILE = "/home/z/my-project/download/Mersenne_factordb_cache.json"
OUTPUT_FILE = "/home/z/my-project/download/Mersenne_factors_k_analysis.txt"
JSON_FILE = "/home/z/my-project/download/Mersenne_factors_k_analysis.json"

MERSENNE_PRIME_P = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279, 2203, 2281,
    3217, 4253, 4423, 9689, 9941, 11213, 19937, 21701, 23209, 44497, 86243,
    110503, 132049, 216091, 756839, 859433, 1257787, 1398269, 2976221, 3021377
}


def main():
    with open(CACHE_FILE) as f:
        cache = json.load(f)
    
    # تولید اعداد اول تا 8000
    sieve = bytearray([1]) * 8001
    sieve[0] = sieve[1] = 0
    for i in range(2, 90):
        if sieve[i]:
            for j in range(i*i, 8001, i):
                sieve[j] = 0
    primes = [i for i in range(2, 8001) if sieve[i]]
    composite_mersenne_p = [p for p in primes if p not in MERSENNE_PRIME_P]
    
    print(f"Total composites: {len(composite_mersenne_p)}", flush=True)
    
    # برای هر M(p)، فاکتورهای اول رو استخراج کن
    all_factors = []  # list of (index, p, q_str, q_digits, k_str, k_digits, k_is_prime)
    
    for idx, p in enumerate(composite_mersenne_p, 1):
        M = mpz(2)**p - 1
        M_str = str(M)
        data = cache.get(M_str, {'status': 'U', 'factors': []})
        factors = data.get('factors', [])
        
        for f_str, exp in factors:
            q = mpz(f_str)
            if not is_prime(q):
                continue  # فقط فاکتورهای اول
            
            # محاسبه k = (q-1) / (2*p)
            # اول چک کن q-1 بر 2p بخش‌پذیر هست
            q_minus_1 = q - 1
            if q_minus_1 % (2 * p) != 0:
                # این نباید اتفاق بیفته برای فاکتور Mersenne
                continue
            
            k = q_minus_1 // (2 * p)
            k_str = str(k)
            k_digits = len(k_str)
            k_is_prime = is_prime(k) if k_digits < 100 else False  # برای k های خیلی بزرگ، skip
            
            all_factors.append({
                'index': idx,
                'p': p,
                'q': f_str,
                'q_digits': len(f_str),
                'k': k_str,
                'k_digits': k_digits,
                'k_is_prime': k_is_prime,
                'q_exp': exp
            })
        
        if idx % 100 == 0:
            print(f"[{idx}/{len(composite_mersenne_p)}] factors so far: {len(all_factors)}", flush=True)
    
    print(f"\nTotal prime factors found: {len(all_factors)}", flush=True)
    
    # ذخیره JSON
    with open(JSON_FILE, 'w') as f:
        json.dump(all_factors, f, indent=2)
    
    # نوشتن فایل متنی
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        out.write("=" * 100 + "\n")
        out.write("  تحلیل k برای فاکتورهای اول اعداد مرسن مرکب M(p) = 2^p - 1\n")
        out.write("  برای p اول ≤ 8000\n")
        out.write("  هر فاکتور اول q از M(p) به فرم q = 2·k·p + 1 هست\n")
        out.write("  این فایل k و تعداد ارقامش رو برای همه فاکتورهای اول نشون می‌ده\n")
        out.write("=" * 100 + "\n\n")
        
        out.write("Legend:\n")
        out.write("  Index = شماره M(p) در لیست Mersenne composites\n")
        out.write("  p     = توان مرسن\n")
        out.write("  q     = فاکتور اول M(p)\n")
        out.write("  digits q = تعداد ارقام q\n")
        out.write("  k     = (q-1)/(2·p)\n")
        out.write("  digits k = تعداد ارقام k\n")
        out.write("  k prime? = آیا k اول هست\n\n")
        
        # آمار کلی
        total = len(all_factors)
        k_prime_count = sum(1 for f in all_factors if f['k_is_prime'])
        k_composite_count = total - k_prime_count
        
        # توزیع ارقام k
        k_digits_dist = {}
        for f in all_factors:
            d = f['k_digits']
            k_digits_dist[d] = k_digits_dist.get(d, 0) + 1
        
        out.write("=" * 100 + "\n")
        out.write("  آمار کلی\n")
        out.write("=" * 100 + "\n\n")
        out.write(f"تعداد کل فاکتورهای اول: {total}\n")
        out.write(f"k اول: {k_prime_count}\n")
        out.write(f"k مرکب: {k_composite_count}\n\n")
        
        out.write("توزیع ارقام k:\n")
        for d in sorted(k_digits_dist.keys()):
            count = k_digits_dist[d]
            bar = '█' * min(50, count)
            out.write(f"  {d:>3} رقم: {count:>5} {bar}\n")
        out.write("\n")
        
        # تحلیل الگوی افزایشی
        out.write("=" * 100 + "\n")
        out.write("  تحلیل الگوی افزایشی: آیا k با بزرگ‌تر شدن p بزرگ‌تر می‌شه؟\n")
        out.write("=" * 100 + "\n\n")
        
        # گروه‌بندی بر اساس بازه p
        p_ranges = [(0, 200), (200, 500), (500, 1000), (1000, 2000), (2000, 4000), (4000, 8000)]
        out.write(f"{'بازه p':>15} {'تعداد فاکتور':>15} {'میانگین ارقام k':>20} {'حداکثر ارقام k':>20} {'حداقل ارقام k':>20}\n")
        out.write("-" * 100 + "\n")
        
        for lo, hi in p_ranges:
            in_range = [f for f in all_factors if lo < f['p'] <= hi]
            if not in_range:
                continue
            count = len(in_range)
            avg_k_d = sum(f['k_digits'] for f in in_range) / count
            max_k_d = max(f['k_digits'] for f in in_range)
            min_k_d = min(f['k_digits'] for f in in_range)
            out.write(f"  p in ({lo}, {hi}]    {count:>10}        {avg_k_d:>15.1f}        {max_k_d:>15}        {min_k_d:>15}\n")
        
        out.write("\n")
        
        # جدول کامل
        out.write("=" * 100 + "\n")
        out.write("  جدول کامل: همه فاکتورهای اول با k\n")
        out.write("=" * 100 + "\n\n")
        
        out.write(f"{'Index':>6} {'p':>6} {'digits q':>10} {'digits k':>10} {'k prime?':>10} {'q (compact)':>30} {'k (compact)':>30}\n")
        out.write("-" * 110 + "\n")
        
        for f in all_factors:
            q_compact = f['q'][:25] + '...' if len(f['q']) > 25 else f['q']
            k_compact = f['k'][:25] + '...' if len(f['k']) > 25 else f['k']
            k_p_label = '✓' if f['k_is_prime'] else '✗'
            out.write(f"{f['index']:>6} {f['p']:>6} {f['q_digits']:>10} {f['k_digits']:>10} {k_p_label:>10} {q_compact:>30} {k_compact:>30}\n")
        
        # نمونه‌های جالب
        out.write("\n" + "=" * 100 + "\n")
        out.write("  نمونه‌های جالب: کوچک‌ترین و بزرگ‌ترین k ها\n")
        out.write("=" * 100 + "\n\n")
        
        sorted_by_k_digits = sorted(all_factors, key=lambda x: x['k_digits'])
        
        out.write("10 مورد با کوچک‌ترین k (احتمالاً P-1 با B1 کوچیک پیدا می‌کنه):\n")
        for f in sorted_by_k_digits[:10]:
            out.write(f"  Index {f['index']}, p={f['p']}: k = {f['k']} ({f['k_digits']} رقم)\n")
            out.write(f"    q = {f['q'][:60]}{'...' if len(f['q'])>60 else ''} ({f['q_digits']} رقم)\n")
            out.write(f"    k اول؟ {'بله' if f['k_is_prime'] else 'خیر'}\n\n")
        
        out.write("\n10 مورد با بزرگ‌ترین k (P-1 به B1 خیلی بزرگ نیاز داره):\n")
        for f in sorted_by_k_digits[-10:]:
            out.write(f"  Index {f['index']}, p={f['p']}: k has {f['k_digits']} digits\n")
            out.write(f"    q digits: {f['q_digits']}\n")
            out.write(f"    k اول؟ {'بله' if f['k_is_prime'] else 'خیر/خیلی بزرگ'}\n\n")
    
    print(f"✓ Done! Output: {OUTPUT_FILE}", flush=True)
    print(f"  Total factors: {total}", flush=True)
    print(f"  k prime: {k_prime_count}", flush=True)
    print(f"  k composite: {k_composite_count}", flush=True)


if __name__ == "__main__":
    main()
