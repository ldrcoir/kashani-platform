#!/usr/bin/env python3
"""
فاکتوریزاسیون کامل و نهایی اعداد مرسن مرکب M(p) = 2^p - 1 برای p ≤ 8000
================================================================
اصلاحیه نسخه قبلی:
1. همه p های اول تا 8000 رو پوشش می‌ده (حتی اگه قبلاً جا افتاده باشن)
2. موارد PARTIAL و NO FACTORS رو دوباره با FactorDB چک می‌کنه
3. خروجی مرتب و کامل
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import gmpy2
from gmpy2 import mpz, is_prime

OUTPUT_FILE = "/home/z/my-project/download/A136030_Mersenne_composite_factorizations_to_8000.txt"
CACHE_FILE = "/home/z/my-project/download/Mersenne_factordb_cache.json"


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {}

def save_cache(cache):
    tmp = CACHE_FILE + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(cache, f, indent=2)
    os.rename(tmp, CACHE_FILE)

def query_factordb(n_str, cache):
    """استعلام FactorDB با cache"""
    if n_str in cache:
        return cache[n_str]
    
    # تأخیر کوتاه برای جلوگیری از rate-limit
    time.sleep(0.3)
    
    try:
        url = f"http://factordb.com/api?query={urllib.parse.quote(n_str)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
        
        result = {
            'status': data.get('status', 'U'),
            'factors': data.get('factors', [])
        }
        cache[n_str] = result
        # ذخیره cache هر 20 درخواست
        if len(cache) % 20 == 0:
            save_cache(cache)
        return result
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e), 'factors': []}

MERSENNE_PRIME_P = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279, 2203, 2281,
    3217, 4253, 4423, 9689, 9941, 11213, 19937, 21701, 23209, 44497, 86243,
    110503, 132049, 216091, 756839, 859433, 1257787, 1398269, 2976221, 3021377,
    6972593, 13466917, 20996011, 24036583, 25964951, 30402457, 32582657
}

def format_factors(factors_list):
    if not factors_list:
        return "?"
    parts = []
    for f_str, exp in factors_list:
        f = mpz(f_str)
        if is_prime(f):
            label = f"P{len(f_str)}"
        else:
            label = f"C{len(f_str)}"
        if exp == 1:
            parts.append(label)
        else:
            parts.append(f"{label}^{exp}")
    return " * ".join(parts)

def format_full_factors(factors_list):
    if not factors_list:
        return "?"
    parts = []
    for f_str, exp in factors_list:
        f = mpz(f_str)
        prime_status = "P" if is_prime(f) else "C"
        if exp == 1:
            parts.append(f"{f_str}({prime_status}{len(f_str)})")
        else:
            parts.append(f"{f_str}({prime_status}{len(f_str)})^{exp}")
    return " * ".join(parts)

def main():
    cache = load_cache()
    
    # تولید اعداد اول تا 8000
    sieve = bytearray([1]) * 8001
    sieve[0] = sieve[1] = 0
    for i in range(2, 90):
        if sieve[i]:
            for j in range(i*i, 8001, i):
                sieve[j] = 0
    primes = [i for i in range(2, 8001) if sieve[i]]
    
    # فقط p هایی که M(p) مرکب است
    composite_mersenne_p = [p for p in primes if p not in MERSENNE_PRIME_P]
    print(f"Total composite Mersenne primes p ≤ 8000: {len(composite_mersenne_p)}", flush=True)
    
    out = open(OUTPUT_FILE, 'w', encoding='utf-8')
    out.write("=" * 80 + "\n")
    out.write("  Complete factorizations of composite Mersenne numbers M(p) = 2^p - 1\n")
    out.write("  for prime p ≤ 8000 (excluding Mersenne primes)\n")
    out.write("  Source: FactorDB + local gmpy2 verification\n")
    out.write(f"  Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    out.write("=" * 80 + "\n\n")
    
    out.write("Legend:\n")
    out.write("  Pn  = prime factor with n digits\n")
    out.write("  Cn  = composite factor with n digits (NOT fully factored)\n")
    out.write("  FF  = fully factored (all factors prime)\n")
    out.write("  CF  = composite, factors known but not all prime\n")
    out.write("  C   = composite, no factors known\n\n")
    
    stats = {
        'total': 0,
        'ff': 0,
        'cf': 0,
        'c': 0,
    }
    
    for idx, p in enumerate(composite_mersenne_p, 1):
        stats['total'] += 1
        
        M = mpz(2)**p - 1
        M_str = str(M)
        M_digits = len(M_str)
        
        # استعلام FactorDB
        result = query_factordb(M_str, cache)
        status = result.get('status', 'U')
        factors_list = result.get('factors', [])
        
        if status == 'FF':
            stats['ff'] += 1
        elif status == 'CF':
            stats['cf'] += 1
        elif status == 'C':
            stats['c'] += 1
        elif status in ('P', 'Prp'):
            # این نباید اتفاق بیفته چون p در MERSENNE_PRIME_P نیست
            # ولی اگه FactorDB بتونه بگه، احتمالاً یه Mersenne prime جدید پیدا شده
            stats['ff'] += 1
        
        factors_short = format_factors(factors_list)
        factors_full = format_full_factors(factors_list)
        
        status_label = {
            'FF': '[FULLY FACTORED]',
            'CF': '[PARTIAL]',
            'C': '[NO FACTORS]',
            'P': '[MERSENNE PRIME!]',
            'Prp': '[PROBABLE PRIME]',
            'U': '[UNKNOWN]'
        }.get(status, f'[{status}]')
        
        out.write(f"M({p}): {status_label}  ({M_digits} digits)\n")
        out.write(f"  M({p}) = 2^{p} - 1\n")
        out.write(f"  digits = {M_digits}\n")
        out.write(f"  factors (compact): {factors_short}\n")
        if status in ('FF', 'CF'):
            out.write(f"  factors (full):    {factors_full}\n")
        out.write("\n")
        
        # گزارش دوره‌ای
        if idx % 50 == 0 or idx == len(composite_mersenne_p):
            print(f"[{idx}/{len(composite_mersenne_p)}] M({p}) done - FF={stats['ff']}, CF={stats['cf']}, C={stats['c']}", flush=True)
        
        # flush هر 10 مورد
        if idx % 10 == 0:
            out.flush()
    
    # ذخیره نهایی cache
    save_cache(cache)
    
    # آمار نهایی
    out.write("\n" + "=" * 80 + "\n")
    out.write("  Summary Statistics\n")
    out.write("=" * 80 + "\n\n")
    out.write(f"Total composite Mersenne numbers (prime p ≤ 8000): {stats['total']}\n\n")
    out.write(f"  Fully factored (FF): {stats['ff']}\n")
    out.write(f"  Partial (CF):        {stats['cf']}\n")
    out.write(f"  No factors (C):      {stats['c']}\n\n")
    
    out.close()
    
    print(f"\n✓ Done!", flush=True)
    print(f"  Total: {stats['total']}", flush=True)
    print(f"  FF (fully factored): {stats['ff']}", flush=True)
    print(f"  CF (partial): {stats['cf']}", flush=True)
    print(f"  C (no factors): {stats['c']}", flush=True)
    print(f"  Output: {OUTPUT_FILE}", flush=True)

if __name__ == "__main__":
    main()
