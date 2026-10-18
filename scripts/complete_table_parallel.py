#!/usr/bin/env python3
"""
ساختن جدول کامل از 1 تا N (پیش‌فرض 1,000,000) با workerهای چند نخی
================================================================
خروجی:
- تعداد اعداد اول شناخته‌شده
- تعداد اعداد مرکب فاکتور شده
- تعداد شکست‌ها
- frontier پیوسته (آخرین عددی که 1..N همه یا اولن یا فاکتور شدن)

روش:
- چند نخی (4 worker با multiprocessing)
- هر worker یه بلاک از اعداد رو می‌گیره و فاکتور می‌کنه
- استفاده از gmpy2 برای اول بودن و Pollard rho
"""
import sys
import os
import time
import json
from multiprocessing import Pool, Value
import ctypes

sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime


def factor_with_rho(n, max_iter=200000):
    """فاکتور کردن با rho"""
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


def process_chunk(args):
    """پردازش یه بلاک از اعداد - برای multiprocessing"""
    start, end = args
    primes_count = 0
    composites_factored = 0
    unfactored = []
    
    for n in range(start, end):
        if n == 1:
            continue
        n_mpz = mpz(n)
        if is_prime(n_mpz):
            primes_count += 1
        else:
            factors = factor_with_rho(n)
            if None in factors:
                unfactored.append(n)
            else:
                composites_factored += 1
    
    return {
        'range': f"{start}-{end-1}",
        'count': end - start,
        'primes': primes_count,
        'composites_factored': composites_factored,
        'unfactored': unfactored,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--N', type=int, default=100000, help='جدول 1 تا N')
    parser.add_argument('--workers', type=int, default=4, help='تعداد worker')
    args = parser.parse_args()
    
    N = args.N
    num_workers = args.workers
    
    print(f"🚀 ساختن جدول ۱ تا {N} با {num_workers} worker")
    print(f"⏱️  شروع: {time.strftime('%H:%M:%S')}")
    print()
    
    # Dividir el rango en chunks
    chunk_size = max(1000, N // (num_workers * 10))
    chunks = []
    for start in range(1, N + 1, chunk_size):
        end = min(start + chunk_size, N + 1)
        chunks.append((start, end))
    
    print(f"📦 تعداد بلاک‌ها: {len(chunks)}")
    print()
    
    t0 = time.time()
    
    # Run with multiprocessing Pool
    total_primes = 0
    total_composites = 0
    total_unfactored = []
    
    with Pool(num_workers) as pool:
        # Process chunks and show progress
        for i, result in enumerate(pool.imap_unordered(process_chunk, chunks), 1):
            total_primes += result['primes']
            total_composites += result['composites_factored']
            total_unfactored.extend(result['unfactored'])
            
            elapsed = time.time() - t0
            done = i * chunk_size
            rate = done / elapsed if elapsed > 0 else 0
            print(f"  [{i}/{len(chunks)}] {result['range']}: primes={result['primes']}, composites={result['composites_factored']}, unfactored={len(result['unfactored'])} | rate={rate:.0f}/s, elapsed={elapsed:.1f}s")
    
    elapsed = time.time() - t0
    total_count = N
    total_one = 1  # just "1"
    
    print()
    print("=" * 70)
    print(f"📊 نتیجه نهایی جدول ۱ تا {N}")
    print("=" * 70)
    print(f"  ⏱️  زمان کل: {elapsed:.1f}s")
    print(f"  📦 اعداد پردازش‌شده: {total_count}")
    print(f"  🔵 عدد '1': {total_one}")
    print(f"  ✅ اعداد اول (P): {total_primes}")
    print(f"  ✅ اعداد مرکب فاکتور شده (C): {total_composites}")
    print(f"  ❌ شکست‌ها (gap): {len(total_unfactored)}")
    print(f"  📈 Frontier پیوسته: {N if not total_unfactored else '(شکست وجود دارد)'}")
    if total_unfactored:
        print(f"  🔴 اولین شکست: {total_unfactored[0]}")
    print()
    
    # Save summary
    OUTPUT_DIR = "/home/z/my-project/download/complete_table"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summary = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'range': f'1 to {N}',
        'total_processed': total_count,
        'primes': total_primes,
        'composites_factored': total_composites,
        'unfactored_count': len(total_unfactored),
        'unfactored_first': total_unfactored[:100] if total_unfactored else [],
        'frontier_continuous': N if not total_unfactored else None,
        'time_seconds': elapsed,
        'workers': num_workers,
        'method': 'Pollard rho with 200k iterations, multiprocessing',
    }
    with open(f"{OUTPUT_DIR}/table_1_to_{N}.json", 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"  💾 ذخیره شد: {OUTPUT_DIR}/table_1_to_{N}.json")


if __name__ == '__main__':
    main()
