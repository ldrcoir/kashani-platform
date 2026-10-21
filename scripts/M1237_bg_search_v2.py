#!/usr/bin/env python3
"""
جستجوی پس‌زمینه v2 - نسخه سریع‌تر و هوشمندتر
================================================
F2 = 932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281199369604215535391846857906233364905825622441048803673998858526737
                                                                                              (303 رقم — مرکب، فاکتور نشده)

بهبودها نسبت به v1:
- چندین worker موازی (به جای 2)
- chunk های کوچک‌تر برای توزیع بهتر کار
- وقتی فاکتور پیدا شد، F2 رو کاهش بده و جستجو ادامه بده
- وقتی باقی‌مانده اول شد، اعلام کنه و متوقف بشه
- چک‌پوینت هر ۳۰ ثانیه
- گزارش پیشرفت هر ۶۰ ثانیه
- فاکتورها در فایل FOUND_factors.txt با timestamp ذخیره می‌شن
- گزارش‌های قابل خواندن در progress.txt
"""

import sys
import os
import time
import json
import signal
import multiprocessing as mp
from pathlib import Path
import gmpy2
from gmpy2 import mpz, is_prime

# ============================================================
#  ثابت‌ها
# ============================================================
P = 1237
TWO_P = 2 * P  # 2474

F2_STR = "932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281199369604215535391846857906233364905825622441048803673998858526737"
F2 = mpz(F2_STR)

# شروع از آخرین checkpoint
K_START = 10**9 + 1
K_END = 10**18  # یک هدف خیلی دور

# تعداد worker - به جای 2، تعداد هسته‌ها × 2 (به خاطر I/O-bound بودن نسبی)
NUM_WORKERS = max(4, (os.cpu_count() or 4) * 2)
CHUNK_SIZE = 50_000  # chunk های کوچک‌تر برای توزیع بهتر

WORKDIR = Path("/home/z/my-project/A136030_Search_M1237_bg")
WORKDIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_FILE = WORKDIR / "checkpoint.json"
LOG_FILE = WORKDIR / "search.log"
FOUND_FILE = WORKDIR / "FOUND_factors.txt"
PROGRESS_FILE = WORKDIR / "progress.txt"
ALL_FACTORS_FILE = WORKDIR / "ALL_factors.json"  # همه فاکتورهای پیدا شده در JSON

# ============================================================
#  مدیریت چک‌پوینت
# ============================================================
def load_checkpoint():
    """بارگذاری آخرین پیشرفت"""
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "k_start": K_START,
        "k_done": K_START - 1,
        "total_primes_tested": 0,
        "total_candidates_tested": 0,
        "factors_found": [],
        "remaining_F2": F2_STR,
        "remaining_digits": len(F2_STR),
        "last_update": time.time(),
        "version": 2
    }

def save_checkpoint(state):
    """ذخیره پیشرفت (atomic)"""
    state["last_update"] = time.time()
    tmp = CHECKPOINT_FILE.with_suffix('.json.tmp')
    with open(tmp, 'w') as f:
        json.dump(state, f, indent=2)
    tmp.replace(CHECKPOINT_FILE)

# ============================================================
#  worker - بررسی یک تکه از k
# ============================================================
def worker_chunk(args):
    """یک worker که یک بازه [k_lo, k_hi] را بررسی می‌کند.
       args: (k_lo, k_hi, worker_id, f2_str, p, two_p)"""
    k_lo, k_hi, worker_id, f2_str, p, two_p = args
    
    f2 = mpz(f2_str)
    primes_tested = 0
    candidates_tested = 0
    factors_found = []
    
    for k in range(k_lo, k_hi + 1):
        # شرط mod 8: k ≡ 0 یا 3 (mod 4)
        if (k & 3) != 0 and (k & 3) != 3:
            continue
        
        candidates_tested += 1
        q = two_p * k + 1
        
        # اگر q^2 > f2 یعنی دیگر فاکتور ممکن نیست
        # (mpz مقایسه داره)
        if q > f2:
            break
        
        # تست اول بودن با Miller-Rabin (سریع)
        if not is_prime(q):
            continue
        
        primes_tested += 1
        
        # تقسیم f2 بر q
        if f2 % q == 0:
            factors_found.append((int(k), int(q)))
            # فاکتور رو از f2 کم می‌کنیم و ادامه می‌دیم
            while f2 % q == 0:
                f2 //= q
            # اگر باقی‌مانده 1 شد، تموم
            if f2 == 1:
                break
            # اگر باقی‌مانده اول شد، تموم
            if is_prime(f2):
                factors_found.append((0, int(f2)))  # k=0 یعنی cofactor
                break
    
    return {
        "worker_id": worker_id,
        "k_hi": k_hi,
        "primes_tested": primes_tested,
        "candidates_tested": candidates_tested,
        "factors_found": factors_found,
        "remaining_f2": str(f2),
        "remaining_is_prime": (f2 > 1 and is_prime(f2)),
        "remaining_is_one": (f2 == 1)
    }

# ============================================================
#  مدیریت چرخه حیات
# ============================================================
running = True

def signal_handler(signum, frame):
    global running
    print("\n[signal] در حال توقف ایمن...", flush=True)
    running = False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# ============================================================
#  main loop - با pool از worker ها
# ============================================================
def main():
    global running
    
    state = load_checkpoint()
    
    # F2 فعلی رو از state بارگذاری کن (اگر قبلاً فاکتور پیدا شده)
    current_f2 = mpz(state.get("remaining_F2", F2_STR))
    
    print(f"[main] شروع جستجو از k = {state['k_done'] + 1:,}", flush=True)
    print(f"[main] F2 فعلی = {str(current_f2)[:60]}... ({len(str(current_f2))} رقم)", flush=True)
    print(f"[main] تعداد worker: {NUM_WORKERS}", flush=True)
    print(f"[main] chunk size: {CHUNK_SIZE:,}", flush=True)
    print(f"[main] چک‌پوینت: {CHECKPOINT_FILE}", flush=True)
    print(f"[main] فاکتورهای پیدا شده در: {FOUND_FILE}", flush=True)
    print(f"[main] Ctrl+C/Z برای توقف ایمن", flush=True)
    print(f"[main] " + "=" * 60, flush=True)
    
    # باز کردن فایل لاگ
    log_fp = open(LOG_FILE, 'a', buffering=1)
    log_fp.write(f"\n{'=' * 60}\n")
    log_fp.write(f"شروع: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_fp.write(f"k_start = {state['k_done'] + 1}\n")
    log_fp.write(f"F2 digits = {len(str(current_f2))}\n")
    log_fp.write(f"workers = {NUM_WORKERS}\n")
    log_fp.write(f"chunk_size = {CHUNK_SIZE}\n")
    log_fp.write(f"{'=' * 60}\n")
    
    # pool از worker ها
    pool = mp.Pool(processes=NUM_WORKERS)
    
    next_k = state['k_done'] + 1
    last_save = time.time()
    last_report = time.time()
    last_progress_k = state['k_done']
    
    # صف وظایف
    pending = []
    chunks_in_flight = 0
    max_pending = NUM_WORKERS * 2  # دو برابر worker ها در صف
    
    sqrt_f2 = gmpy2.isqrt(current_f2)
    max_useful_k = int(sqrt_f2) // TWO_P
    print(f"[main] sqrt(F2) ≈ 10^{len(str(sqrt_f2))-1} — حداکثر k مفید ≈ {max_useful_k:,}", flush=True)
    log_fp.write(f"sqrt(F2) digits = {len(str(sqrt_f2))}\n")
    log_fp.write(f"max useful k ≈ {max_useful_k}\n\n")
    
    while running:
        # اگر F2 فاکتور شد، جدید رو جایگزین کن
        if state.get("remaining_F2") and state["remaining_F2"] != str(current_f2):
            current_f2 = mpz(state["remaining_F2"])
            sqrt_f2 = gmpy2.isqrt(current_f2)
            max_useful_k = int(sqrt_f2) // TWO_P
            print(f"\n[main] F2 به‌روزرسانی شد! ارقام جدید: {len(str(current_f2))}", flush=True)
            log_fp.write(f"\n*** F2 UPDATED *** digits = {len(str(current_f2))}\n")
        
        # اگر F2 اول شد یا 1 شد، تموم
        if current_f2 == 1:
            print("\n[main] F2 کاملاً فاکتور شد! ✅", flush=True)
            log_fp.write("\n*** FACTORIZATION COMPLETE ***\n")
            break
        if is_prime(current_f2):
            print(f"\n[main] باقی‌مانده اول است! {str(current_f2)[:50]}... ({len(str(current_f2))} رقم)", flush=True)
            log_fp.write(f"\n*** COFACTOR IS PRIME *** digits={len(str(current_f2))}\n")
            # اعلام فاکتور نهایی
            with open(FOUND_FILE, 'a') as fout:
                fout.write(f"\n=== COFACTOR PRIME ===\n")
                fout.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                fout.write(f"cofactor = {current_f2}\n")
                fout.write(f"digits = {len(str(current_f2))}\n")
            state['factors_found'].append({
                'k': 0,
                'q': str(current_f2),
                'type': 'cofactor_prime',
                'time': time.strftime('%Y-%m-%d %H:%M:%S')
            })
            save_checkpoint(state)
            break
        
        # پر کردن صف وظایف
        while len(pending) < max_pending and next_k <= K_END and running:
            k_lo = next_k
            k_hi = min(next_k + CHUNK_SIZE - 1, K_END)
            # اگر k_hi از max_useful_k بیشتر شد، محدود کن
            if k_hi > max_useful_k:
                k_hi = max_useful_k
                if k_lo > max_useful_k:
                    print(f"\n[main] به max_useful_k رسیدیم! خروج.", flush=True)
                    running = False
                    break
            
            args = (k_lo, k_hi, len(pending), str(current_f2), P, TWO_P)
            res = pool.apply_async(worker_chunk, (args,))
            pending.append((k_lo, k_hi, res))
            next_k = k_hi + 1
            chunks_in_flight += 1
        
        # چک کردن نتایج آماده
        new_pending = []
        for k_lo, k_hi, res in pending:
            if res.ready():
                try:
                    result = res.get(timeout=1)
                except Exception as e:
                    print(f"[main] خطا در worker: {e}", flush=True)
                    log_fp.write(f"ERROR: {e}\n")
                    continue
                
                # به‌روزرسانی state
                state['k_done'] = max(state['k_done'], result['k_hi'])
                state['total_primes_tested'] += result['primes_tested']
                state['total_candidates_tested'] += result['candidates_tested']
                
                # فاکتورهای پیدا شده
                if result['factors_found']:
                    for k, q in result['factors_found']:
                        if k == 0:
                            # cofactor اول
                            print(f"\n!!! COFACTOR PRIME !!! q={q} ({len(str(q))} رقم)", flush=True)
                            log_fp.write(f"\n*** COFACTOR PRIME *** q={q} digits={len(str(q))}\n")
                            with open(FOUND_FILE, 'a') as fout:
                                fout.write(f"\n=== COFACTOR PRIME ===\n")
                                fout.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                                fout.write(f"k = N/A (cofactor)\n")
                                fout.write(f"q = {q}\n")
                                fout.write(f"digits = {len(str(q))}\n\n")
                            state['factors_found'].append({
                                'k': 0,
                                'q': str(q),
                                'type': 'cofactor_prime',
                                'time': time.strftime('%Y-%m-%d %H:%M:%S')
                            })
                        else:
                            print(f"\n!!! FACTOR FOUND !!! k={k}, q={q} ({len(str(q))} رقم)", flush=True)
                            log_fp.write(f"\n*** FACTOR FOUND *** k={k} q={q} digits={len(str(q))}\n")
                            with open(FOUND_FILE, 'a') as fout:
                                fout.write(f"\n=== FACTOR FOUND ===\n")
                                fout.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                                fout.write(f"k = {k}\n")
                                fout.write(f"q = {q}\n")
                                fout.write(f"digits = {len(str(q))}\n")
                                fout.write(f"q = 2 * {P} * {k} + 1\n\n")
                            state['factors_found'].append({
                                'k': int(k),
                                'q': str(q),
                                'type': 'mersenne_factor',
                                'time': time.strftime('%Y-%m-%d %H:%M:%S')
                            })
                    
                    # F2 فعلی رو به‌روزرسانی
                    current_f2 = mpz(result['remaining_f2'])
                    state['remaining_F2'] = str(current_f2)
                    state['remaining_digits'] = len(str(current_f2))
                    save_checkpoint(state)
                    
                    # اگر F2 کامل فاکتور شد یا باقی‌مانده اول شد
                    if result['remaining_is_one']:
                        print(f"\n[main] F2 کاملاً فاکتور شد!", flush=True)
                        running = False
                        break
                    if result['remaining_is_prime']:
                        print(f"\n[main] باقی‌مانده اول است! ارقام: {len(str(current_f2))}", flush=True)
                        # گزارش و ذخیره
                        with open(FOUND_FILE, 'a') as fout:
                            fout.write(f"\n=== COFACTOR PRIME (final) ===\n")
                            fout.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                            fout.write(f"q = {current_f2}\n")
                            fout.write(f"digits = {len(str(current_f2))}\n\n")
                        state['factors_found'].append({
                            'k': 0,
                            'q': str(current_f2),
                            'type': 'cofactor_prime',
                            'time': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
                        save_checkpoint(state)
                        running = False
                        break
            else:
                new_pending.append((k_lo, k_hi, res))
        
        pending = new_pending
        
        # ذخیره چک‌پوینت هر ۳۰ ثانیه
        if time.time() - last_save > 30:
            save_checkpoint(state)
            last_save = time.time()
        
        # گزارش دوره‌ای هر ۶۰ ثانیه
        if time.time() - last_report > 60:
            elapsed = time.time() - last_report
            delta_k = state['k_done'] - last_progress_k
            speed = delta_k / max(1, elapsed)
            print(f"[main] k={state['k_done']:,} (+{delta_k:,} در {elapsed:.0f}s) "
                  f"speed={speed:,.0f} k/s primes={state['total_primes_tested']:,} "
                  f"factors={len(state['factors_found'])} F2_digits={len(str(current_f2))}", 
                  flush=True)
            log_fp.write(f"progress: k={state['k_done']} primes={state['total_primes_tested']} "
                        f"factors={len(state['factors_found'])} F2_digits={len(str(current_f2))}\n")
            
            # به‌روزرسانی progress file
            with open(PROGRESS_FILE, 'w') as pf:
                pf.write(f"version = 2\n")
                pf.write(f"k_done = {state['k_done']:,}\n")
                pf.write(f"primes_tested = {state['total_primes_tested']:,}\n")
                pf.write(f"candidates_tested = {state['total_candidates_tested']:,}\n")
                pf.write(f"factors_found = {len(state['factors_found'])}\n")
                pf.write(f"F2_digits_remaining = {len(str(current_f2))}\n")
                pf.write(f"last_update = {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                pf.write(f"speed = {speed:,.0f} k/sec\n")
                pf.write(f"workers = {NUM_WORKERS}\n")
                if state['factors_found']:
                    pf.write(f"\n=== factors so far ===\n")
                    for f in state['factors_found']:
                        pf.write(f"  k={f.get('k')}, digits={len(f.get('q',''))}, type={f.get('type')}, time={f.get('time')}\n")
            
            last_progress_k = state['k_done']
            last_report = time.time()
        
        # خواب کوتاه برای کاهش CPU مصرفی main loop
        if pending and not running == False:
            time.sleep(0.5)
    
    # توقف ایمن
    print("\n[main] در حال توقف...", flush=True)
    pool.close()
    pool.join()
    
    save_checkpoint(state)
    
    # ذخیره همه فاکتورها در JSON
    with open(ALL_FACTORS_FILE, 'w') as f:
        json.dump({
            'F2_original': F2_STR,
            'F2_remaining': str(current_f2),
            'factors_found': state['factors_found'],
            'k_done': state['k_done'],
            'primes_tested': state['total_primes_tested'],
            'final_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }, f, indent=2)
    
    log_fp.write(f"\nپایان: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_fp.write(f"k_done = {state['k_done']}\n")
    log_fp.write(f"primes_tested = {state['total_primes_tested']}\n")
    log_fp.write(f"factors_found = {len(state['factors_found'])}\n")
    log_fp.write(f"F2_remaining_digits = {len(str(current_f2))}\n")
    log_fp.close()
    
    print(f"[main] چک‌پوینت نهایی: k = {state['k_done']:,}", flush=True)
    print(f"[main] primes tested: {state['total_primes_tested']:,}", flush=True)
    print(f"[main] factors found: {len(state['factors_found'])}", flush=True)
    print(f"[main] F2 باقی‌مانده: {len(str(current_f2))} رقم", flush=True)


if __name__ == "__main__":
    # تنظیم multiprocessing - fork برای پایداری بیشتر
    try:
        mp.set_start_method('fork', force=True)
    except RuntimeError:
        mp.set_start_method('spawn', force=True)
    main()
