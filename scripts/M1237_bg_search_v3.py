#!/usr/bin/env python3
"""
جستجوی پس‌زمینه v3 - نسخه بهینه شده
=====================================
بهبودها نسبت به v2:
- هر worker یک بازه بزرگ (10M k) می‌گیره و مستقل کار می‌کنه
- بدون Pool.apply_async overhead
- گزارش‌گیری مستقیم از طریق فایل (هر worker خودش progress می‌نویسه)
- main loop فقط worker ها رو spawn و monitor می‌کنه
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

K_START = 10**9 + 1
K_END = 10**18

NUM_WORKERS = 4
CHUNK_SIZE = 10_000_000  # هر worker 10M k می‌گیره

WORKDIR = Path("/home/z/my-project/A136030_Search_M1237_bg")
WORKDIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_FILE = WORKDIR / "checkpoint.json"
LOG_FILE = WORKDIR / "search.log"
FOUND_FILE = WORKDIR / "FOUND_factors.txt"
PROGRESS_FILE = WORKDIR / "progress.txt"
WORKER_PROGRESS_DIR = WORKDIR / "worker_progress"
WORKER_PROGRESS_DIR.mkdir(exist_ok=True)

# ============================================================
#  worker - مستقل، یک بازه بزرگ کار می‌کنه
# ============================================================
def worker_run(k_lo, k_hi, worker_id, f2_str, result_file):
    """یک worker مستقل که یک بازه بزرگ [k_lo, k_hi] را بررسی می‌کند.
       پیشرفت را در فایل می‌نویسد.
       اگر فاکتور پیدا کرد، در FOUND_FILE می‌نویسد.
       در پایان، نتیجه را در result_file می‌نویسد."""
    f2 = mpz(f2_str)
    primes_tested = 0
    candidates_tested = 0
    factors_found = []
    
    progress_file = WORKER_PROGRESS_DIR / f"worker_{worker_id}.txt"
    last_progress_save = time.time()
    
    for k in range(k_lo, k_hi + 1):
        # شرط mod 8: k ≡ 0 یا 3 (mod 4)
        if (k & 3) != 0 and (k & 3) != 3:
            continue
        
        candidates_tested += 1
        q = TWO_P * k + 1
        
        if q > f2:
            break
        
        # تست اول بودن
        if not is_prime(q):
            continue
        
        primes_tested += 1
        
        # تقسیم F2 بر q
        if f2 % q == 0:
            factors_found.append((int(k), int(q)))
            # ذخیره در FOUND file
            with open(FOUND_FILE, 'a') as fout:
                fout.write(f"\n=== FACTOR FOUND (worker {worker_id}) ===\n")
                fout.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                fout.write(f"k = {k}\n")
                fout.write(f"q = {q}\n")
                fout.write(f"digits = {len(str(q))}\n")
                fout.write(f"q = 2 * {P} * {k} + 1\n\n")
            
            # کاهش F2
            while f2 % q == 0:
                f2 //= q
            
            # اگر باقی‌مانده 1 شد
            if f2 == 1:
                with open(FOUND_FILE, 'a') as fout:
                    fout.write(f"=== FACTORIZATION COMPLETE ===\n")
                    fout.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                break
            
            # اگر باقی‌مانده اول شد
            if is_prime(f2):
                with open(FOUND_FILE, 'a') as fout:
                    fout.write(f"\n=== COFACTOR PRIME ===\n")
                    fout.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    fout.write(f"cofactor = {f2}\n")
                    fout.write(f"digits = {len(str(f2))}\n\n")
                factors_found.append((0, int(f2)))
                break
        
        # گزارش پیشرفت هر 30 ثانیه
        if time.time() - last_progress_save > 30:
            with open(progress_file, 'w') as pf:
                pf.write(f"worker_id: {worker_id}\n")
                pf.write(f"k_current: {k}\n")
                pf.write(f"k_lo: {k_lo}\n")
                pf.write(f"k_hi: {k_hi}\n")
                pf.write(f"primes_tested: {primes_tested}\n")
                pf.write(f"candidates_tested: {candidates_tested}\n")
                pf.write(f"factors_found: {len(factors_found)}\n")
                pf.write(f"f2_digits: {len(str(f2))}\n")
                pf.write(f"progress_pct: {(k - k_lo) / (k_hi - k_lo) * 100:.1f}\n")
                pf.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            last_progress_save = time.time()
    
    # ذخیره پیشرفت نهایی worker
    with open(progress_file, 'w') as pf:
        pf.write(f"worker_id: {worker_id}\n")
        pf.write(f"k_current: {k_hi}\n")
        pf.write(f"k_lo: {k_lo}\n")
        pf.write(f"k_hi: {k_hi}\n")
        pf.write(f"primes_tested: {primes_tested}\n")
        pf.write(f"candidates_tested: {candidates_tested}\n")
        pf.write(f"factors_found: {len(factors_found)}\n")
        pf.write(f"f2_digits: {len(str(f2))}\n")
        pf.write(f"progress_pct: 100.0\n")
        pf.write(f"status: done\n")
        pf.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # ذخیره نتیجه نهایی
    with open(result_file, 'w') as rf:
        json.dump({
            'worker_id': worker_id,
            'k_lo': k_lo,
            'k_hi': k_hi,
            'primes_tested': primes_tested,
            'candidates_tested': candidates_tested,
            'factors_found': [(k, str(q)) for k, q in factors_found],
            'remaining_f2': str(f2),
            'remaining_is_prime': (f2 > 1 and is_prime(f2)),
            'remaining_is_one': (f2 == 1),
            'time': time.strftime('%Y-%m-%d %H:%M:%S')
        }, rf, indent=2)


# ============================================================
#  main loop
# ============================================================
running = True

def signal_handler(signum, frame):
    global running
    print("\n[signal] در حال توقف ایمن...", flush=True)
    running = False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


def load_checkpoint():
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
        "version": 3
    }


def save_checkpoint(state):
    state["last_update"] = time.time()
    tmp = CHECKPOINT_FILE.with_suffix('.json.tmp')
    with open(tmp, 'w') as f:
        json.dump(state, f, indent=2)
    tmp.replace(CHECKPOINT_FILE)


def main():
    global running
    
    state = load_checkpoint()
    current_f2 = mpz(state.get("remaining_F2", F2_STR))
    
    print(f"[main v3] شروع از k = {state['k_done'] + 1:,}", flush=True)
    print(f"[main v3] F2 = {str(current_f2)[:60]}... ({len(str(current_f2))} رقم)", flush=True)
    print(f"[main v3] workers = {NUM_WORKERS}, chunk = {CHUNK_SIZE:,}", flush=True)
    print(f"[main v3] " + "=" * 60, flush=True)
    
    log_fp = open(LOG_FILE, 'a', buffering=1)
    log_fp.write(f"\n{'=' * 60}\n")
    log_fp.write(f"شروع v3: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_fp.write(f"k_start = {state['k_done'] + 1}\n")
    log_fp.write(f"workers = {NUM_WORKERS}\n")
    log_fp.write(f"chunk_size = {CHUNK_SIZE}\n")
    log_fp.write(f"{'=' * 60}\n")
    
    next_k = state['k_done'] + 1
    last_save = time.time()
    last_report = time.time()
    last_progress_k = state['k_done']
    
    # پاکسازی worker progress های قدیمی
    for f in WORKER_PROGRESS_DIR.glob("worker_*.txt"):
        f.unlink()
    
    active_workers = []  # list of (proc, result_file, k_lo, k_hi)
    results_dir = WORKDIR / "results"
    results_dir.mkdir(exist_ok=True)
    # پاکسازی نتایج قدیمی
    for f in results_dir.glob("result_*.json"):
        f.unlink()
    
    result_counter = 0
    
    while running:
        # شروع worker های جدید اگر کم داریم
        while len(active_workers) < NUM_WORKERS and running:
            k_lo = next_k
            k_hi = min(next_k + CHUNK_SIZE - 1, K_END)
            
            result_counter += 1
            result_file = str(results_dir / f"result_{result_counter}.json")
            
            proc = mp.Process(
                target=worker_run,
                args=(k_lo, k_hi, result_counter, str(current_f2), result_file),
                daemon=False
            )
            proc.start()
            active_workers.append((proc, result_file, k_lo, k_hi))
            next_k = k_hi + 1
            
            print(f"[main] worker {result_counter} شروع شد: k=[{k_lo:,}, {k_hi:,}]", flush=True)
            log_fp.write(f"worker {result_counter} start: k=[{k_lo}, {k_hi}]\n")
        
        # چک کردن worker های تمام‌شده
        new_active = []
        for proc, result_file, k_lo, k_hi in active_workers:
            if not proc.is_alive():
                proc.join()
                # خواندن نتیجه
                try:
                    with open(result_file) as rf:
                        result = json.load(rf)
                    
                    # به‌روزرسانی state
                    state['k_done'] = max(state['k_done'], result['k_hi'])
                    state['total_primes_tested'] += result['primes_tested']
                    state['total_candidates_tested'] += result['candidates_tested']
                    
                    # فاکتورهای پیدا شده
                    if result['factors_found']:
                        for k, q in result['factors_found']:
                            if k == 0:
                                # cofactor
                                print(f"\n!!! COFACTOR PRIME !!! {q[:50]}... ({len(q)} رقم)", flush=True)
                                log_fp.write(f"\n*** COFACTOR PRIME *** digits={len(q)}\n")
                                state['factors_found'].append({
                                    'k': 0, 'q': q, 'type': 'cofactor_prime',
                                    'time': time.strftime('%Y-%m-%d %H:%M:%S')
                                })
                            else:
                                print(f"\n!!! FACTOR FOUND !!! k={k}, q={q} ({len(q)} رقم)", flush=True)
                                log_fp.write(f"\n*** FACTOR *** k={k} q={q} digits={len(q)}\n")
                                state['factors_found'].append({
                                    'k': int(k), 'q': q, 'type': 'mersenne_factor',
                                    'time': time.strftime('%Y-%m-%d %H:%M:%S')
                                })
                        
                        # به‌روزرسانی F2
                        current_f2 = mpz(result['remaining_f2'])
                        state['remaining_F2'] = str(current_f2)
                        state['remaining_digits'] = len(str(current_f2))
                        save_checkpoint(state)
                        
                        if result['remaining_is_one']:
                            print(f"\n[main] FACTORIZATION COMPLETE!", flush=True)
                            log_fp.write(f"*** FACTORIZATION COMPLETE ***\n")
                            running = False
                            break
                        if result['remaining_is_prime']:
                            print(f"\n[main] COFACTOR IS PRIME!", flush=True)
                            log_fp.write(f"*** COFACTOR IS PRIME ***\n")
                            running = False
                            break
                    
                    print(f"[main] worker {result['worker_id']} تمام شد: k_hi={result['k_hi']:,}, "
                          f"primes={result['primes_tested']:,}, factors={len(result['factors_found'])}", 
                          flush=True)
                except Exception as e:
                    print(f"[main] خطا در خواندن نتیجه: {e}", flush=True)
                    log_fp.write(f"ERROR: {e}\n")
            else:
                new_active.append((proc, result_file, k_lo, k_hi))
        
        active_workers = new_active
        
        # ذخیره چک‌پوینت هر 30 ثانیه
        if time.time() - last_save > 30:
            save_checkpoint(state)
            last_save = time.time()
        
        # گزارش دوره‌ای هر 60 ثانیه
        if time.time() - last_report > 60:
            elapsed = time.time() - last_report
            delta_k = state['k_done'] - last_progress_k
            speed = delta_k / max(1, elapsed)
            
            # محاسله میانگین پیشرفت worker ها
            worker_progress = []
            for wf in WORKER_PROGRESS_DIR.glob("worker_*.txt"):
                try:
                    content = wf.read_text()
                    wf_data = {}
                    for line in content.split('\n'):
                        if ':' in line:
                            key, val = line.split(':', 1)
                            wf_data[key.strip()] = val.strip()
                    worker_progress.append(wf_data)
                except Exception:
                    pass
            
            print(f"[main] k={state['k_done']:,} (+{delta_k:,} در {elapsed:.0f}s) "
                  f"speed={speed:,.0f} k/s primes={state['total_primes_tested']:,} "
                  f"factors={len(state['factors_found'])} F2_digits={len(str(current_f2))} "
                  f"workers_active={len(active_workers)}", flush=True)
            log_fp.write(f"progress: k={state['k_done']} speed={speed:.0f} primes={state['total_primes_tested']} "
                        f"factors={len(state['factors_found'])}\n")
            
            # به‌روزرسانی progress file
            with open(PROGRESS_FILE, 'w') as pf:
                pf.write(f"version = 3\n")
                pf.write(f"k_done = {state['k_done']:,}\n")
                pf.write(f"primes_tested = {state['total_primes_tested']:,}\n")
                pf.write(f"candidates_tested = {state['total_candidates_tested']:,}\n")
                pf.write(f"factors_found = {len(state['factors_found'])}\n")
                pf.write(f"F2_digits_remaining = {len(str(current_f2))}\n")
                pf.write(f"last_update = {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                pf.write(f"speed = {speed:,.0f} k/sec\n")
                pf.write(f"workers = {NUM_WORKERS}\n")
                pf.write(f"workers_active = {len(active_workers)}\n")
                if state['factors_found']:
                    pf.write(f"\n=== factors so far ===\n")
                    for f in state['factors_found']:
                        pf.write(f"  k={f.get('k')}, digits={len(f.get('q',''))}, type={f.get('type')}, time={f.get('time')}\n")
                
                # اضافه کردن جزئیات worker ها
                if worker_progress:
                    pf.write(f"\n=== worker details ===\n")
                    for w in worker_progress:
                        pf.write(f"  worker {w.get('worker_id','?')}: k={w.get('k_current','?')} "
                               f"({w.get('progress_pct','?')}%) primes={w.get('primes_tested','?')} "
                               f"factors={w.get('factors_found','?')}\n")
            
            last_progress_k = state['k_done']
            last_report = time.time()
        
        # خواب کوتاه
        if active_workers:
            time.sleep(2)
    
    # توقف ایمن
    print("\n[main] در حال توقف worker ها...", flush=True)
    for proc, _, _, _ in active_workers:
        if proc.is_alive():
            proc.terminate()
            proc.join(timeout=5)
    
    save_checkpoint(state)
    log_fp.write(f"\nپایان: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_fp.write(f"k_done = {state['k_done']}\n")
    log_fp.write(f"primes_tested = {state['total_primes_tested']}\n")
    log_fp.write(f"factors_found = {len(state['factors_found'])}\n")
    log_fp.close()
    
    print(f"[main] چک‌پوینت نهایی: k = {state['k_done']:,}", flush=True)
    print(f"[main] primes tested: {state['total_primes_tested']:,}", flush=True)
    print(f"[main] factors found: {len(state['factors_found'])}", flush=True)
    print(f"[main] F2 باقی‌مانده: {len(str(current_f2))} رقم", flush=True)


if __name__ == "__main__":
    try:
        mp.set_start_method('fork', force=True)
    except RuntimeError:
        mp.set_start_method('spawn', force=True)
    main()
