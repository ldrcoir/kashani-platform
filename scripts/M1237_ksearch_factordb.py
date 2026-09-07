#!/usr/bin/env python3
"""
جستجوی فاکتورهای M(1237) با k های بزرگ
==========================================
برای k های بزرگ (مثلاً 10^14 به بالا):
1. تولید q = 2·1237·k + 1
2. بررسی شرط Mersenne: q ≡ ±1 (mod 8)
3. استعلام FactorDB برای اول بودن q
4. اگه q اول بود، تست F2 mod q

مزیت: به‌جای تست همه اعداد، فقط اعداد به فرم Mersenne رو چک می‌کنیم.
FactorDB به ما میگه کدوم اول هستن (بدون نیاز به محاسبه محلی).
"""

import json
import time
import urllib.request
import urllib.parse
import sys
import os
import gmpy2
from gmpy2 import mpz, is_prime

P = 1237
TWO_P = 2 * P  # 2474

F2 = mpz("932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281199369604215535391846857906233364905825622441048803673998858526737")
M_1237 = mpz(2)**P - 1

WORKDIR = "/home/z/my-project/A136030_M1237_ksearch"
os.makedirs(WORKDIR, exist_ok=True)

OUTPUT_FILE = f"{WORKDIR}/candidates_checked.txt"
FOUND_FILE = f"{WORKDIR}/FOUND_factors.txt"
PROGRESS_FILE = f"{WORKDIR}/progress.txt"
CACHE_FILE = f"{WORKDIR}/factordb_cache.json"


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
    """استعلام FactorDB"""
    if n_str in cache:
        return cache[n_str]
    
    try:
        url = f"http://factordb.com/api?query={urllib.parse.quote(n_str)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        
        result = {
            'status': data.get('status', 'U'),
            'factors': data.get('factors', [])
        }
        cache[n_str] = result
        # ذخیره cache هر 10 درخواست
        if len(cache) % 10 == 0:
            save_cache(cache)
        return result
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e), 'factors': []}


def main():
    cache = load_cache()
    
    # باز کردن فایل‌ها
    out_fp = open(OUTPUT_FILE, 'w', encoding='utf-8')
    found_fp = open(FOUND_FILE, 'w', encoding='utf-8')
    
    # پارامترهای جستجو - از ورودی بخون
    if len(sys.argv) >= 3:
        k_start = int(sys.argv[1])
        k_end = int(sys.argv[2])
    else:
        # پیش‌فرض: از 10^14 تا 10^14 + 10^6
        k_start = 10**14
        k_end = k_start + 10**6
    
    step = 1  # گام پیش‌فرض
    
    print(f"جستجوی فاکتورهای M(1237) با k های بزرگ")
    print(f"k_start = {k_start:,}")
    print(f"k_end   = {k_end:,}")
    print(f"تعداد k برای بررسی: {k_end - k_start:,}")
    print()
    
    out_fp.write(f"=== جستجوی فاکتورهای M(1237) با k بزرگ ===\n")
    out_fp.write(f"تاریخ: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    out_fp.write(f"k_range: [{k_start}, {k_end}]\n\n")
    
    stats = {
        'total_k': 0,
        'form_ok': 0,        # شرط mod 8 برقرار
        'prime_count': 0,    # اعداد اول پیدا شده
        'factor_count': 0,   # فاکتور پیدا شده
        'factordb_calls': 0,
    }
    
    start_time = time.time()
    last_progress = time.time()
    last_save = time.time()
    
    for k in range(k_start, k_end + 1, step):
        stats['total_k'] += 1
        
        # تولید q = 2·1237·k + 1
        q = TWO_P * k + 1
        
        # شرط Mersenne: q ≡ ±1 (mod 8)
        # q = 2474·k + 1
        # q mod 8 = (2474·k + 1) mod 8 = (2·k + 1) mod 8
        # باید 1 یا 7 باشه
        q_mod_8 = (2 * k + 1) % 8  # ساده‌سازی برای سرعت
        if q_mod_8 != 1 and q_mod_8 != 7:
            continue
        
        stats['form_ok'] += 1
        
        # تبدیل به string برای FactorDB
        q_str = str(q)
        
        # استعلام FactorDB
        result = query_factordb(q_str, cache)
        stats['factordb_calls'] += 1
        
        status = result.get('status', 'U')
        
        # فقط اگه اول (P یا Prp) باشه، تست فاکتور بودن
        if status in ('P', 'Prp'):
            stats['prime_count'] += 1
            
            # تست فاکتور بودن F2
            r_f2 = F2 % q
            r_m = M_1237 % q
            
            out_fp.write(f"k={k}\n")
            out_fp.write(f"  q = {q_str}\n")
            out_fp.write(f"  ارقام: {len(q_str)}\n")
            out_fp.write(f"  وضعیت FactorDB: {status}\n")
            out_fp.write(f"  F2 mod q = {r_f2}\n")
            out_fp.write(f"  M(1237) mod q = {r_m}\n")
            
            if r_f2 == 0:
                stats['factor_count'] += 1
                other = F2 // q
                out_fp.write(f"  ✓✓✓ فاکتور F2 پیدا شد!\n")
                out_fp.write(f"  F2 = q × {other}\n")
                out_fp.write(f"  ارقام ضریب: {len(str(other))}\n")
                
                found_fp.write(f"\n=== FACTOR FOUND! ===\n")
                found_fp.write(f"زمان: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                found_fp.write(f"k = {k}\n")
                found_fp.write(f"q = {q_str}\n")
                found_fp.write(f"ارقام q: {len(q_str)}\n")
                found_fp.write(f"F2 = q × {other}\n")
                found_fp.write(f"ارقام ضریب: {len(str(other))}\n")
                found_fp.write(f"ضریب اول: {is_prime(other)}\n\n")
                found_fp.flush()
                
                print(f"\n✓✓✓ فاکتور پیدا شد! k={k}, q has {len(q_str)} digits")
            
            elif r_m == 0:
                # فاکتور M(1237) ولی نه F2 - یعنی فاکتور F1
                out_fp.write(f"  ✓ فاکتور M(1237) ولی نه F2 (احتمالاً فاکتور F1)\n")
            
            out_fp.flush()
        
        # گزارش دوره‌ای
        now = time.time()
        if now - last_progress > 30:
            elapsed = now - start_time
            speed = stats['total_k'] / max(1, elapsed)
            
            progress_msg = (f"k={k:,} | total={stats['total_k']:,} | "
                          f"form_ok={stats['form_ok']:,} | "
                          f"primes={stats['prime_count']:,} | "
                          f"factors={stats['factor_count']} | "
                          f"speed={speed:,.0f} k/s | "
                          f"factordb={stats['factordb_calls']}")
            
            print(progress_msg, flush=True)
            
            with open(PROGRESS_FILE, 'w') as pf:
                pf.write(f"k_current: {k}\n")
                pf.write(f"k_range: [{k_start}, {k_end}]\n")
                pf.write(f"total_checked: {stats['total_k']}\n")
                pf.write(f"form_ok: {stats['form_ok']}\n")
                pf.write(f"primes: {stats['prime_count']}\n")
                pf.write(f"factors: {stats['factor_count']}\n")
                pf.write(f"speed: {speed:.0f} k/s\n")
                pf.write(f"elapsed: {elapsed:.0f}s\n")
                pf.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            last_progress = now
        
        # ذخیره cache هر 60 ثانیه
        if now - last_save > 60:
            save_cache(cache)
            last_save = now
    
    # ذخیره نهایی cache
    save_cache(cache)
    
    # آمار نهایی
    elapsed = time.time() - start_time
    out_fp.write(f"\n=== آمار نهایی ===\n")
    out_fp.write(f"کل k بررسی شده: {stats['total_k']:,}\n")
    out_fp.write(f"شرط mod 8 برقرار: {stats['form_ok']:,}\n")
    out_fp.write(f"اعداد اول: {stats['prime_count']:,}\n")
    out_fp.write(f"فاکتور پیدا شده: {stats['factor_count']}\n")
    out_fp.write(f"زمان: {elapsed:.0f} ثانیه\n")
    out_fp.write(f"سرعت: {stats['total_k']/max(1,elapsed):,.0f} k/s\n")
    
    print(f"\n✓ تمام شد!")
    print(f"  کل: {stats['total_k']:,}")
    print(f"  اول: {stats['prime_count']:,}")
    print(f"  فاکتور: {stats['factor_count']}")
    print(f"  زمان: {elapsed:.0f}s")
    
    out_fp.close()
    found_fp.close()


if __name__ == "__main__":
    main()
