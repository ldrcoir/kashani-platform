#!/usr/bin/env python3
"""
جستجوی هوشمندانه فاکتورهای F2 = M(1237)/F1
==========================================
based on the structural discovery:

F1 - 1 = 2 × 3 × 7 × 1237 × X1 × X2
F2 - 1 = 2^4 × 3 × 7 × 1237 × Y1 × Y2

Both k values contain 3 × 7 as small factors.
This suggests future factors of F2 might also have:
  k = 3 × 7 × Y1 × m  (or similar small-factor structure)

Strategy: instead of trying all k, only try k = 3 × 7 × Y1 × m for m = 1, 2, 3, ...
This is 10^14 times faster than naive trial division.

But wait - the user's point is correct: for LARGER factors, k itself is LARGER.
So we need to find factors whose k has small prime factors (B-smooth).
This is exactly what P-1 method does!
"""

import sys
import os
import time
import json
import signal
import multiprocessing as mp
from pathlib import Path
import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod

# ============================================================
#  ثابت‌ها
# ============================================================
P = 1237
TWO_P = 2 * P  # 2474

F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = mpz("932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281199369604215535391846857906233364905825622441048803673998858526737")

# فاکتورهای کشف‌شده از تحلیل (هر دو k شامل اینهاست)
SMALL_FACTORS = [3, 7]
Y1 = mpz("18641439966407")  # 14 رقم - فاکتور کشف‌شده از k_F2

# استراتژی: جستجوی k به فرم‌های مختلف
# 1. k = 3 × 7 × m (ساده‌ترین حالت)
# 2. k = 3 × 7 × Y1 × m (با Y1)
# 3. k = 2^a × 3 × 7 × m (با توان‌های 2)

WORKDIR = Path("/home/z/my-project/A136030_Search_M1237_smart")
WORKDIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_FILE = WORKDIR / "checkpoint.json"
LOG_FILE = WORKDIR / "search.log"
FOUND_FILE = WORKDIR / "FOUND_factors.txt"
PROGRESS_FILE = WORKDIR / "progress.txt"

# ============================================================
#  تابع جستجوی هوشمند
# ============================================================
def search_smart_pattern(worker_id, pattern_name, k_template_factor, m_start, m_end, f2_str, result_file):
    """
    جستجوی q = 2 × p × k + 1 که در آن k = k_template_factor × m
    pattern_name: نام الگو (مثلاً "3*7*m" یا "3*7*Y1*m")
    k_template_factor: مقدار ثابت (مثلاً 21 برای 3*7، یا 21*Y1 برای 3*7*Y1)
    m_start, m_end: بازه m
    """
    f2 = mpz(f2_str)
    p = P
    two_p = TWO_P
    template = mpz(k_template_factor)
    
    primes_tested = 0
    candidates_tested = 0
    factors_found = []
    
    progress_file = WORKDIR / f"worker_{worker_id}.txt"
    last_progress_save = time.time()
    
    # برای هر m، k = template × m
    # q = 2 × p × template × m + 1
    # یعنی q = base × m + 1 که base = 2 × p × template
    
    base = two_p * template
    
    for m in range(m_start, m_end + 1):
        q = base * m + 1
        
        # شرط mod 8: q ≡ 1 یا 7 (mod 8)
        # q = base × m + 1
        # base mod 8 = (2 × 1237 × template) mod 8
        # اگر template شامل 4 باشه، base mod 8 = 0، پس q mod 8 = 1 ✓
        # در غیر این صورت باید چک کنیم
        q_mod_8 = q % 8
        if q_mod_8 != 1 and q_mod_8 != 7:
            continue
        
        candidates_tested += 1
        
        # اگر q^2 > f2 یعنی دیگر لازم نیست بگردیم
        if q > f2:
            break
        
        # تست اول بودن
        if not is_prime(q):
            continue
        
        primes_tested += 1
        
        # تقسیم f2 بر q
        if f2 % q == 0:
            factors_found.append((int(m), int(q), pattern_name))
            with open(FOUND_FILE, 'a') as fout:
                fout.write(f"\n=== FACTOR FOUND (smart search - {pattern_name}) ===\n")
                fout.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                fout.write(f"pattern: {pattern_name}\n")
                fout.write(f"m = {m}\n")
                fout.write(f"k = {template} × {m} = {template * m}\n")
                fout.write(f"q = 2 × {p} × k + 1 = {q}\n")
                fout.write(f"q digits = {len(str(q))}\n\n")
            
            while f2 % q == 0:
                f2 //= q
            
            if f2 == 1:
                with open(FOUND_FILE, 'a') as fout:
                    fout.write(f"=== FACTORIZATION COMPLETE ===\n")
                break
            
            if is_prime(f2):
                with open(FOUND_FILE, 'a') as fout:
                    fout.write(f"\n=== COFACTOR PRIME ===\n")
                    fout.write(f"cofactor = {f2}\n")
                    fout.write(f"digits = {len(str(f2))}\n\n")
                factors_found.append((0, int(f2), "cofactor"))
                break
        
        # گزارش پیشرفت هر 30 ثانیه
        if time.time() - last_progress_save > 30:
            with open(progress_file, 'w') as pf:
                pf.write(f"worker_id: {worker_id}\n")
                pf.write(f"pattern: {pattern_name}\n")
                pf.write(f"m_current: {m}\n")
                pf.write(f"m_range: [{m_start}, {m_end}]\n")
                pf.write(f"primes_tested: {primes_tested}\n")
                pf.write(f"candidates_tested: {candidates_tested}\n")
                pf.write(f"factors_found: {len(factors_found)}\n")
                pf.write(f"f2_digits: {len(str(f2))}\n")
                pf.write(f"progress_pct: {(m - m_start) / max(1, m_end - m_start) * 100:.1f}\n")
                pf.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            last_progress_save = time.time()
    
    # ذخیره پیشرفت نهایی
    with open(progress_file, 'w') as pf:
        pf.write(f"worker_id: {worker_id}\n")
        pf.write(f"pattern: {pattern_name}\n")
        pf.write(f"m_current: {m_end}\n")
        pf.write(f"primes_tested: {primes_tested}\n")
        pf.write(f"candidates_tested: {candidates_tested}\n")
        pf.write(f"factors_found: {len(factors_found)}\n")
        pf.write(f"status: done\n")
        pf.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # ذخیره نتیجه نهایی
    with open(result_file, 'w') as rf:
        json.dump({
            'worker_id': worker_id,
            'pattern': pattern_name,
            'template': str(template),
            'm_start': m_start,
            'm_end': m_end,
            'primes_tested': primes_tested,
            'candidates_tested': candidates_tested,
            'factors_found': [(m, str(q), p_name) for m, q, p_name in factors_found],
            'remaining_f2': str(f2),
            'remaining_is_prime': (f2 > 1 and is_prime(f2)),
            'remaining_is_one': (f2 == 1),
            'time': time.strftime('%Y-%m-%d %H:%M:%S')
        }, rf, indent=2)


# ============================================================
#  main
# ============================================================
running = True

def signal_handler(signum, frame):
    global running
    print("\n[signal] در حال توقف ایمن...", flush=True)
    running = False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


def main():
    global running
    
    print("=" * 70, flush=True)
    print("  جستجوی هوشمند فاکتورهای F2 - بر اساس الگوی کشف‌شده", flush=True)
    print("=" * 70, flush=True)
    print(flush=True)
    
    print(f"F2 = {str(F2)[:60]}... ({len(str(F2))} رقم)", flush=True)
    print(flush=True)
    
    # تعریف الگوهای جستجو
    # هر الگو: (نام, template, توضیح)
    patterns = [
        ("3*7*m",         3 * 7,                       "k = 3 × 7 × m"),
        ("3*7*Y1*m",      3 * 7 * int(Y1),             "k = 3 × 7 × Y1 × m"),
        ("3*7*2^a*m_a4",  3 * 7 * 16,                  "k = 3 × 7 × 16 × m (a=4 مثل F2)"),
        ("3*7*2^a*m_a3",  3 * 7 * 8,                   "k = 3 × 7 × 8 × m (a=3)"),
        ("3*7*2^a*m_a2",  3 * 7 * 4,                   "k = 3 × 7 × 4 × m (a=2)"),
        ("3*7*2^a*m_a5",  3 * 7 * 32,                  "k = 3 × 7 × 32 × m (a=5)"),
    ]
    
    print("الگوهای جستجو:", flush=True)
    for name, tmpl, desc in patterns:
        print(f"  {name}: {desc}  (template={tmpl})", flush=True)
    print(flush=True)
    
    # محاسبه m_max برای هر الگو
    # q = 2 × p × template × m + 1 ≤ sqrt(F2)
    # m ≤ (sqrt(F2) - 1) / (2 × p × template)
    sqrt_F2 = gmpy2.isqrt(F2)
    print(f"sqrt(F2) ≈ 10^{len(str(sqrt_F2))}", flush=True)
    print(flush=True)
    
    # شروع جستجو - هر الگو رو به چند worker تقسیم می‌کنیم
    NUM_WORKERS_PER_PATTERN = 1  # در ابتدا یک worker برای هر الگو
    
    log_fp = open(LOG_FILE, 'a', buffering=1)
    log_fp.write(f"\n{'=' * 70}\n")
    log_fp.write(f"شروع جستجوی هوشمند: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_fp.write(f"{'=' * 70}\n")
    
    results_dir = WORKDIR / "results"
    results_dir.mkdir(exist_ok=True)
    for f in results_dir.glob("result_*.json"):
        f.unlink()
    
    active_workers = []
    worker_counter = 0
    
    # شروع worker ها - هر کدوم یک الگو رو با m از 1 تا 10^12 بررسی می‌کنن
    M_CHUNK = 10**12  # هر worker تا 10^12 m رو بررسی می‌کنه
    
    for pattern_name, template, desc in patterns:
        worker_counter += 1
        m_start = 1
        m_end = M_CHUNK
        result_file = str(results_dir / f"result_{worker_counter}.json")
        
        proc = mp.Process(
            target=search_smart_pattern,
            args=(worker_counter, pattern_name, template, m_start, m_end, str(F2), result_file),
            daemon=False
        )
        proc.start()
        active_workers.append((proc, result_file, pattern_name, worker_counter))
        
        print(f"[main] worker {worker_counter} شروع شد: {pattern_name}, m=[{m_start}, {m_end}]", flush=True)
        log_fp.write(f"worker {worker_counter} start: {pattern_name} m=[{m_start}, {m_end}]\n")
    
    print(flush=True)
    print(f"[main] {len(active_workers)} worker در حال اجراست", flush=True)
    print(flush=True)
    
    last_save = time.time()
    last_report = time.time()
    
    while running and active_workers:
        # چک کردن worker های تمام‌شده
        new_active = []
        for proc, result_file, pattern_name, wid in active_workers:
            if not proc.is_alive():
                proc.join()
                try:
                    with open(result_file) as rf:
                        result = json.load(rf)
                    
                    print(f"\n[main] worker {wid} ({pattern_name}) تمام شد:", flush=True)
                    print(f"  m بررسی شده: {result['m_end'] - result['m_start'] + 1:,}", flush=True)
                    print(f"  primes tested: {result['primes_tested']:,}", flush=True)
                    print(f"  candidates: {result['candidates_tested']:,}", flush=True)
                    print(f"  factors found: {len(result['factors_found'])}", flush=True)
                    
                    if result['factors_found']:
                        for m, q, p_name in result['factors_found']:
                            if m == 0:
                                print(f"  ✓ COFACTOR PRIME: {q[:60]}... ({len(q)} رقم)", flush=True)
                            else:
                                print(f"  ✓ FACTOR: m={m}, q={q} ({len(q)} رقم, pattern={p_name})", flush=True)
                        log_fp.write(f"worker {wid}: {len(result['factors_found'])} factors found\n")
                    
                    if result['remaining_is_one']:
                        print(f"\n[main] FACTORIZATION COMPLETE!", flush=True)
                        running = False
                    elif result['remaining_is_prime']:
                        print(f"\n[main] COFACTOR IS PRIME!", flush=True)
                        running = False
                    
                    log_fp.write(f"worker {wid} done: primes={result['primes_tested']} factors={len(result['factors_found'])}\n")
                except Exception as e:
                    print(f"[main] خطا در خواندن نتیجه worker {wid}: {e}", flush=True)
            else:
                new_active.append((proc, result_file, pattern_name, wid))
        
        active_workers = new_active
        
        # گزارش دوره‌ای هر 60 ثانیه
        if time.time() - last_report > 60:
            elapsed = time.time() - last_report
            print(f"[main] workers_active={len(active_workers)}", flush=True)
            
            # جمع‌آوری آمار از فایل‌های worker
            total_primes = 0
            total_candidates = 0
            with open(PROGRESS_FILE, 'w') as pf:
                pf.write(f"smart search v1\n")
                pf.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                pf.write(f"workers_active: {len(active_workers)}\n\n")
                
                for wf in (WORKDIR).glob("worker_*.txt"):
                    try:
                        content = wf.read_text()
                        wf_data = {}
                        for line in content.split('\n'):
                            if ':' in line:
                                key, val = line.split(':', 1)
                                wf_data[key.strip()] = val.strip()
                        
                        pf.write(f"worker {wf_data.get('worker_id','?')} ({wf_data.get('pattern','?')}):\n")
                        pf.write(f"  m_current: {wf_data.get('m_current','?')}\n")
                        pf.write(f"  primes: {wf_data.get('primes_tested','?')}\n")
                        pf.write(f"  candidates: {wf_data.get('candidates_tested','?')}\n")
                        pf.write(f"  factors: {wf_data.get('factors_found','?')}\n")
                        pf.write(f"  progress: {wf_data.get('progress_pct','?')}%\n\n")
                        
                        try:
                            total_primes += int(wf_data.get('primes_tested', 0))
                            total_candidates += int(wf_data.get('candidates_tested', 0))
                        except:
                            pass
                    except Exception:
                        pass
                
                pf.write(f"\n=== totals ===\n")
                pf.write(f"total_primes_tested: {total_primes:,}\n")
                pf.write(f"total_candidates_tested: {total_candidates:,}\n")
            
            last_report = time.time()
        
        if active_workers:
            time.sleep(2)
    
    # توقف ایمن
    print("\n[main] در حال توقف...", flush=True)
    for proc, _, _, _ in active_workers:
        if proc.is_alive():
            proc.terminate()
            proc.join(timeout=5)
    
    log_fp.write(f"\nپایان: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_fp.close()
    
    print("[main] جستجو تمام شد", flush=True)


if __name__ == "__main__":
    try:
        mp.set_start_method('fork', force=True)
    except RuntimeError:
        mp.set_start_method('spawn', force=True)
    main()
