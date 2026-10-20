#!/usr/bin/env python3
"""
🔧 ابزار کلی ساختن و فاکتور کردن اعداد هر بازه
================================================
ورودی: بازه‌ی [start, end)
خروجی: جدول کامل با اعداد اول و فاکتور شده

به افتخار غیاث‌الدین جمشید کاشانی
"""
import sys, os, time, json, random
from multiprocessing import Pool

sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime

OUTPUT_DIR = "/home/z/my-project/download/range_builder"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def factor_with_rho(n, max_iter=200000):
    if n == 1: return []
    if n % 2 == 0:
        return [2] + factor_with_rho(n // 2, max_iter)
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
    start, end = args
    primes_count = 0
    composites_factored = 0
    unfactored = []
    
    for n in range(start, end):
        if n == 1: continue
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


def build_range(start, end, workers=2):
    """ساختن و فاکتور کردن بازه‌ی [start, end)"""
    print(f"🚀 بازه: {start:,} تا {end:,}")
    print(f"⏱️  شروع: {time.strftime('%H:%M:%S')}")
    
    chunk_size = max(1000000, (end - start) // (workers * 10))
    chunks = []
    for s in range(start, end, chunk_size):
        e = min(s + chunk_size, end)
        chunks.append((s, e))
    
    print(f"📦 تعداد بلاک‌ها: {len(chunks)}")
    print()
    
    t0 = time.time()
    total_primes = 0
    total_composites = 0
    all_unfactored = []
    
    with Pool(workers) as pool:
        for i, result in enumerate(pool.imap_unordered(process_chunk, chunks), 1):
            total_primes += result['primes']
            total_composites += result['composites_factored']
            all_unfactored.extend(result['unfactored'])
            
            elapsed = time.time() - t0
            done = i * chunk_size
            rate = done / elapsed if elapsed > 0 else 0
            print(f"  [{i}/{len(chunks)}] {result['range']}: P={result['primes']:,}, C={result['composites_factored']:,}, gaps={len(result['unfactored'])} | {rate:.0f}/s, {elapsed:.1f}s")
    
    elapsed = time.time() - t0
    total_count = end - start
    
    print()
    print("=" * 70)
    print(f"📊 نتیجه: {start:,} تا {end:,}")
    print("=" * 70)
    print(f"  ⏱️  زمان: {elapsed:.1f}s")
    print(f"  📦 اعداد: {total_count:,}")
    print(f"  ✅ اعداد اول: {total_primes:,}")
    print(f"  ✅ مرکب فاکتور شده: {total_composites:,}")
    print(f"  ❌ شکست‌ها: {len(all_unfactored)}")
    
    # Count digits
    start_digits = len(str(start))
    end_digits = len(str(end))
    
    summary = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'range': f'{start} to {end}',
        'digits': f'{start_digits}-{end_digits}',
        'total_processed': total_count,
        'primes': total_primes,
        'composites_factored': total_composites,
        'unfactored_count': len(all_unfactored),
        'unfactored_list': all_unfactored[:100],
        'frontier_continuous': end if not all_unfactored else None,
        'time_seconds': elapsed,
        'workers': workers,
    }
    
    fname = f"{OUTPUT_DIR}/range_{start}_to_{end}.json"
    with open(fname, 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"  💾 ذخیره شد: {fname}")
    return summary


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='ابزار ساختن و فاکتور کردن بازه')
    parser.add_argument('--start', type=int, required=True, help='شروع بازه')
    parser.add_argument('--end', type=int, required=True, help='پایان بازه')
    parser.add_argument('--workers', type=int, default=2, help='تعداد worker')
    args = parser.parse_args()
    
    build_range(args.start, args.end, args.workers)
