#!/usr/bin/env python3
"""
جستجوی پس‌زمینه برای فاکتورهای اول M(1237)
==========================================
F2 = 932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281199369604215535391846857906233364905825622441048803673998858526737
                                                                                              (303 رقم — مرکب، فاکتور نشده)

روش کار:
- هر فاکتور اول q از M(p) باید به فرم q = 2·p·k + 1 باشد و q ≡ ±1 (mod 8)
- برای p = 1237: q = 2474·k + 1
- شرط mod 8: k ≡ 0 یا 3 (mod 4)
- کاندیدها رو موازی چک می‌کنیم، و اگر اول بودن، F2 رو برشون تقسیم می‌کنیم

پیشرفت در فایل checkpoint ذخیره می‌شود تا اگر切断 شد از همانجا ادامه دهیم.
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

# شروع از k = 10^9 + 1 (قبلاً تا 10^9 چک شده)
K_START = 10**9 + 1
# پایان: تا وقتی q^2 <= F2 یعنی q <= sqrt(F2) ≈ 10^151.5
# 2474 * k + 1 <= 10^151 => k <= 4·10^147
# اما عملاً بی‌نهایت می‌تونه باشه، فقط یک حد بزرگ
K_END = 10**15  # یک هدف میانی — در عمل تا برخورد به فاکتور یا قطع دستی

NUM_WORKERS = 2  # تعداد هسته‌ها
CHUNK_SIZE = 100_000  # هر کار یک تکه از این اندازه برمیداره

WORKDIR = Path("/home/z/my-project/A136030_Search_M1237_bg")
WORKDIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_FILE = WORKDIR / "checkpoint.json"
LOG_FILE = WORKDIR / "search.log"
FOUND_FILE = WORKDIR / "FOUND_factors.txt"
PROGRESS_FILE = WORKDIR / "progress.txt"

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
        "last_update": time.time()
    }

def save_checkpoint(state):
    """ذخیره پیشرفت"""
    state["last_update"] = time.time()
    tmp = CHECKPOINT_FILE.with_suffix('.json.tmp')
    with open(tmp, 'w') as f:
        json.dump(state, f, indent=2)
    tmp.replace(CHECKPOINT_FILE)

# ============================================================
#  worker - بررسی یک تکه از k
# ============================================================
def worker_chunk(k_lo, k_hi, worker_id, result_queue):
    """یک worker که یک بازه [k_lo, k_hi] را بررسی می‌کند"""
    f2 = F2
    p = P
    two_p = TWO_P
    
    primes_tested = 0
    candidates_tested = 0
    factors_found = []
    last_report = time.time()
    
    for k in range(k_lo, k_hi + 1):
        # شرط mod 8: k ≡ 0 یا 3 (mod 4)
        if (k & 3) != 0 and (k & 3) != 3:
            continue
        
        candidates_tested += 1
        q = two_p * k + 1
        
        # اگر q^2 > F2 یعنی دیگر لازم نیست بگردیم
        # در worker نمی‌توانیم به راحتی چک کنیم، چون mpz مقایسه داره
        # به جایش در main loop چک می‌کنیم
        
        # تست اول بودن با Miller-Rabin (سریع)
        if not is_prime(q):
            continue
        
        primes_tested += 1
        
        # تقسیم F2 بر q
        if f2 % q == 0:
            factors_found.append((int(k), int(q)))
            # سریع به main گزارش بده
            result_queue.put(("factor", int(k), int(q), worker_id))
            # بنویس در فایل
            with open(FOUND_FILE, 'a') as fout:
                fout.write(f"FACTOR FOUND! k={k}, q={q}\n")
                fout.write(f"  q has {len(str(q))} digits\n")
                fout.write(f"  worker_id={worker_id}\n")
                fout.write(f"  time={time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            # فاکتور رو از F2 کم می‌کنیم و ادامه می‌دیم
            f2 = f2 // q
            # اگر باقی‌مانده 1 شد، تموم
            if f2 == 1:
                result_queue.put(("done", 0, 0, worker_id))
                break
            # اگر باقی‌مانده اول شد، تموم
            if is_prime(f2):
                result_queue.put(("cofactor_prime", 0, int(f2), worker_id))
                with open(FOUND_FILE, 'a') as fout:
                    fout.write(f"REMAINING COFACTOR IS PRIME!\n")
                    fout.write(f"  cofactor = {f2}\n")
                    fout.write(f"  digits = {len(str(f2))}\n")
                break
        
        # گزارش دوره‌ای
        if time.time() - last_report > 30:
            result_queue.put(("progress", k, primes_tested, worker_id))
            last_report = time.time()
    
    # پایان تکه
    result_queue.put(("chunk_done", k_hi, primes_tested, worker_id))


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
#  main loop
# ============================================================
def main():
    global running
    
    state = load_checkpoint()
    
    print(f"[main] شروع جستجو از k = {state['k_done'] + 1:,}", flush=True)
    print(f"[main] F2 = {F2_STR[:60]}... ({len(F2_STR)} رقم)", flush=True)
    print(f"[main] تعداد worker: {NUM_WORKERS}", flush=True)
    print(f"[main] چک‌پوینت: {CHECKPOINT_FILE}", flush=True)
    print(f"[main] لاگ: {LOG_FILE}", flush=True)
    print(f"[main] فاکتورهای پیدا شده در: {FOUND_FILE}", flush=True)
    print(f"[main] Ctrl+C/Z برای توقف ایمن", flush=True)
    print(f"[main] " + "=" * 60, flush=True)
    
    # باز کردن فایل لاگ
    log_fp = open(LOG_FILE, 'a', buffering=1)
    log_fp.write(f"\n{'=' * 60}\n")
    log_fp.write(f"شروع: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_fp.write(f"k_start = {state['k_done'] + 1}\n")
    log_fp.write(f"F2 digits = {len(F2_STR)}\n")
    log_fp.write(f"workers = {NUM_WORKERS}\n")
    log_fp.write(f"{'=' * 60}\n")
    
    result_queue = mp.Queue()
    processes = []
    
    next_k = state['k_done'] + 1
    chunks_in_flight = 0
    last_save = time.time()
    
    # نگه داشتن یک pool از worker ها
    active_workers = {}  # pid -> chunk_info
    
    def start_chunk(k_start):
        """شروع یک worker جدید برای تکه [k_start, k_start + CHUNK_SIZE - 1]"""
        k_end = min(k_start + CHUNK_SIZE - 1, K_END)
        proc = mp.Process(
            target=worker_chunk,
            args=(k_start, k_end, len(active_workers), result_queue),
            daemon=True
        )
        proc.start()
        active_workers[proc.pid] = (k_start, k_end, proc)
        return k_end + 1
    
    # شروع اولیه worker ها
    for _ in range(NUM_WORKERS):
        next_k = start_chunk(next_k)
        chunks_in_flight += 1
    
    sqrt_f2 = gmpy2.isqrt(F2)
    print(f"[main] sqrt(F2) ≈ 10^{len(str(sqrt_f2))-1} — حداکثر k مفید ≈ {int(sqrt_f2) // TWO_P:,}", flush=True)
    log_fp.write(f"sqrt(F2) digits = {len(str(sqrt_f2))}\n")
    log_fp.write(f"max useful k ≈ {int(sqrt_f2) // TWO_P}\n\n")
    
    last_progress_k = state['k_done']
    last_progress_time = time.time()
    
    while running and (chunks_in_flight > 0 or next_k <= K_END):
        # اگر worker کم داریم، یکی شروع کن
        while len(active_workers) < NUM_WORKERS and next_k <= K_END and running:
            next_k = start_chunk(next_k)
            chunks_in_flight += 1
        
        # چک کردن پیام‌ها بدون block
        try:
            msg = result_queue.get(timeout=1)
        except Exception:
            msg = None
        
        if msg is not None:
            msg_type = msg[0]
            if msg_type == "factor":
                _, k, q, wid = msg
                print(f"\n!!! فاکتور پیدا شد !!! k={k}, q={q} ({len(str(q))} رقم)", flush=True)
                log_fp.write(f"\n*** FACTOR FOUND *** k={k}, q={q}, digits={len(str(q))}\n")
                state['factors_found'].append({'k': k, 'q': str(q)})
                save_checkpoint(state)
            elif msg_type == "cofactor_prime":
                _, _, cofactor, wid = msg
                print(f"\n!!! باقی‌مانده اول است !!! {cofactor} ({len(str(cofactor))} رقم)", flush=True)
                log_fp.write(f"*** COFACTOR PRIME *** {cofactor}\n")
                state['factors_found'].append({'cofactor_prime': str(cofactor)})
                save_checkpoint(state)
                running = False
            elif msg_type == "done":
                print("\n!!! فاکتوریزاسیون کامل شد !!!", flush=True)
                running = False
            elif msg_type == "progress":
                _, k, primes_tested, wid = msg
                # فقط لاگ
                pass
            elif msg_type == "chunk_done":
                _, k_hi, primes_tested, wid = msg
                state['k_done'] = max(state['k_done'], k_hi)
                state['total_primes_tested'] += primes_tested
                chunks_in_flight -= 1
                # پیدا کردن و حذف worker از active
                for pid in list(active_workers.keys()):
                    proc = active_workers[pid][2]
                    if not proc.is_alive():
                        proc.join()
                        del active_workers[pid]
        
        # چک کردن worker های تمام‌شده
        for pid in list(active_workers.keys()):
            proc = active_workers[pid][2]
            if not proc.is_alive():
                proc.join()
                del active_workers[pid]
                chunks_in_flight -= 1
        
        # ذخیره چک‌پوینت هر 60 ثانیه
        if time.time() - last_save > 60:
            save_checkpoint(state)
            last_save = time.time()
            # به‌روزرسانی progress file
            with open(PROGRESS_FILE, 'w') as pf:
                pf.write(f"k_done = {state['k_done']:,}\n")
                pf.write(f"primes_tested = {state['total_primes_tested']:,}\n")
                pf.write(f"factors_found = {len(state['factors_found'])}\n")
                pf.write(f"last_update = {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                elapsed = time.time() - last_progress_time
                k_per_sec = (state['k_done'] - last_progress_k) / max(1, elapsed)
                pf.write(f"speed = {k_per_sec:,.0f} k/sec\n")
                last_progress_k = state['k_done']
                last_progress_time = time.time()
        
        # گزارش دوره‌ای به stdout
        if int(time.time()) % 60 == 0:
            elapsed = time.time() - last_progress_time
            if elapsed > 60:
                k_done_now = state['k_done']
                delta = k_done_now - last_progress_k
                print(f"[main] k={k_done_now:,} (+{delta:,} در {elapsed:.0f}s) "
                      f"primes_tested={state['total_primes_tested']:,} "
                      f"factors={len(state['factors_found'])}", flush=True)
                last_progress_k = k_done_now
                last_progress_time = time.time()
    
    # توقف ایمن
    print("\n[main] در حال توقف...", flush=True)
    for pid, (k_lo, k_hi, proc) in active_workers.items():
        proc.terminate()
        proc.join(timeout=5)
    
    save_checkpoint(state)
    log_fp.write(f"\nپایان: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_fp.write(f"k_done = {state['k_done']}\n")
    log_fp.write(f"primes_tested = {state['total_primes_tested']}\n")
    log_fp.close()
    
    print(f"[main] چک‌پوینت نهایی: k = {state['k_done']:,}", flush=True)
    print(f"[main] primes tested: {state['total_primes_tested']:,}", flush=True)
    print(f"[main] factors found: {len(state['factors_found'])}", flush=True)


if __name__ == "__main__":
    # تنظیم multiprocessing - fork برای پایداری بیشتر
    try:
        mp.set_start_method('fork', force=True)
    except RuntimeError:
        mp.set_start_method('spawn', force=True)
    main()
