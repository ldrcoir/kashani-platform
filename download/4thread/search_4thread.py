#!/usr/bin/env python3
"""
A136030 Factor Finder - 4-Thread Version
==========================================
جستجوی عوامل اول اعداد مرسن M(p) = 2^p - 1
برای مقادیر گمشده در فایل A136030_1_to_8000.txt

ویژگی‌ها:
- 4 نخ همزمان (هر نخ روی یک عدد)
- چک‌پوینت در فایل JSON (resume از جا مونده)
- فایل idle.txt که هر 10 ثانیه آپدیت می‌شه
- لاگ‌های جداگانه برای هر نخ
- ذخیره نتایج به محض پیدا شدن

طریقه اجرا:
    python search_4thread.py

فایل‌های ساخته شده در E:\A136030_Search\:
    - checkpoint.json    چک‌پوینت
    - idle.txt           نشانه زنده بودن
    - main.log           لاگ اصلی
    - thread_1.log ... thread_4.log   لاگ هر نخ
    - results.txt        عوامل پیدا شده
    - A136030_1_to_8000.txt   فایل خروجی نهایی
"""

import os
import sys
import time
import json
import threading
import multiprocessing as mp
import gmpy2
from gmpy2 import is_prime as gmpy_is_prime
import numpy as np
from datetime import datetime

# ===== تنظیمات =====
# مسیر درایو E - ویندوز
WORK_DIR_WIN = r"E:\A136030_Search"
# مسیر لینوکس (برای تست اینجا)
WORK_DIR_LINUX = "/home/z/my-project/A136030_Search"

# تشخیص پلتفرم
if sys.platform == 'win32':
    WORK_DIR = WORK_DIR_WIN
else:
    WORK_DIR = WORK_DIR_LINUX

# تعداد نخ‌ها
NUM_THREADS = 4

# فاصله چانک (k هر چانک)
CHUNK_SIZE = 10_000_000  # 10M

# حداکثر k برای هر عدد (10 میلیارد = q تا ~2.5*10^13)
K_LIMIT = 10_000_000_000

# زمان آپدیت idle
IDLE_UPDATE_SEC = 10

# ===== اعداد هدف =====
# (idx, p) - ترتیب بر اساس اهمیت
TARGETS = [
    (192, 1277),  # اولویت 1
    (241, 1619),  # اولویت 2
    (258, 1753),  # اولویت 3
]

# اعداد اول مرسن (که خودشون prime هستن، از لیست خارج می‌شن)
MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607,
    1279, 2203, 2281, 3217, 4253, 4423
}


def log(msg, file=None):
    """لاگ با timestamp."""
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    if file:
        with open(file, 'a', encoding='utf-8') as f:
            f.write(line + "\n")
    else:
        print(line, flush=True)


def build_small_primes(limit=5000):
    """ساخت سیو اعداد اول کوچک."""
    sa = np.ones(limit + 1, dtype=bool)
    sa[0] = sa[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sa[i]:
            sa[i*i::i] = False
    return [int(i) for i in np.flatnonzero(sa)]


def search_chunk(p, k_start, k_end, small_primes):
    """جستجوی یک چانک برای عامل M(p).
    بازگشتی: (factor, last_k_checked)
    """
    p_mod4 = p & 3
    valid_residues = (0, 3) if p_mod4 == 1 else (0, 1)
    two_p = 2 * p
    size = k_end - k_start
    is_composite = np.zeros(size, dtype=bool)
    
    # سیو چانک
    for r in small_primes:
        if r == 2:
            continue
        t = two_p % r
        if t == 0:
            continue
        try:
            inv = pow(int(t), -1, r)
        except ValueError:
            continue
        k_0 = (-inv) % r
        if k_0 < k_start:
            offset = (k_start - k_0 + r - 1) // r
            k_0 = k_0 + offset * r
        if k_0 >= k_end:
            continue
        idx = k_0 - k_start
        is_composite[idx::r] = True
    
    # بررسی هر k
    for i in range(size):
        k = k_start + i
        if (k & 3) not in valid_residues:
            continue
        if is_composite[i]:
            continue
        q = 2 * k * p + 1
        if gmpy_is_prime(q) and pow(2, p, q) == 1:
            return q, k
    
    return None, k_end - 1


def worker_thread(thread_id, target_queue, result_dict, checkpoint_lock, 
                  small_primes, work_dir):
    """نخ کارگر - اعداد رو از صف می‌گیره و جستجو می‌کنه."""
    thread_log = os.path.join(work_dir, f"thread_{thread_id}.log")
    
    while True:
        try:
            target = target_queue.get_nowait()
        except:
            log(f"نخ {thread_id}: صف خالی است، خارج می‌شوم", thread_log)
            return
        
        idx, p = target
        log(f"نخ {thread_id}: شروع M({p}) [idx={idx}]", thread_log)
        
        # بارگذاری چک‌پوینت
        ckpt_file = os.path.join(work_dir, "checkpoint.json")
        with checkpoint_lock:
            try:
                with open(ckpt_file, 'r') as f:
                    ckpt = json.load(f)
            except:
                ckpt = {}
        
        k_start = ckpt.get(f"{idx}_k", 1)
        log(f"نخ {thread_id}: ادامه از k={k_start:,}", thread_log)
        log(f"نخ {thread_id}: هدف K_LIMIT={K_LIMIT:,}", thread_log)
        
        chunk_count = 0
        t_start = time.time()
        
        # جستجوی چانک به چانک
        for chunk_start in range(k_start, K_LIMIT + 1, CHUNK_SIZE):
            chunk_end = min(chunk_start + CHUNK_SIZE, K_LIMIT + 1)
            
            factor, last_k = search_chunk(p, chunk_start, chunk_end, small_primes)
            chunk_count += 1
            
            if factor:
                # عامل پیدا شد!
                elapsed = time.time() - t_start
                log(f"نخ {thread_id}: *** عامل پیدا شد! ***", thread_log)
                log(f"  M({p}) = {factor}", thread_log)
                log(f"  k = {last_k:,}", thread_log)
                log(f"  زمان = {elapsed:.1f}s", thread_log)
                
                with checkpoint_lock:
                    result_dict[idx] = factor
                    # ذخیره در results.txt
                    results_file = os.path.join(work_dir, "results.txt")
                    with open(results_file, 'a', encoding='utf-8') as f:
                        f.write(f"M({p}) [idx={idx}] = {factor}\n")
                        f.write(f"  found by thread {thread_id}, k={last_k}, time={elapsed:.1f}s\n")
                        f.write(f"  timestamp: {datetime.now().isoformat()}\n\n")
                
                # آپدیت فایل خروجی اصلی
                with checkpoint_lock:
                    update_output_file(work_dir, idx, factor)
                
                return
            
            # ذخیره چک‌پوینت
            with checkpoint_lock:
                try:
                    with open(ckpt_file, 'r') as f:
                        ckpt = json.load(f)
                except:
                    ckpt = {}
                ckpt[f"{idx}_k"] = chunk_end - 1
                with open(ckpt_file, 'w') as f:
                    json.dump(ckpt, f, indent=2)
            
            # لاگ پیشرفت
            elapsed = time.time() - t_start
            max_q = 2 * (chunk_end - 1) * p + 1
            log(f"نخ {thread_id}: M({p}) چانک {chunk_count}: k={chunk_end-1:,}, max_q={max_q:.2e}, زمان={elapsed:.0f}s", thread_log)
        
        # اتمام جستجو بدون نتیجه
        log(f"نخ {thread_id}: M({p}) تمام شد، عامل پیدا نشد (تا k={K_LIMIT:,})", thread_log)


def update_output_file(work_dir, idx, factor):
    """آپدیت فایل A136030_1_to_8000.txt با عامل پیدا شده."""
    output_file = os.path.join(work_dir, "A136030_1_to_8000.txt")
    
    # اگه فایل وجود نداره، از فایل اصلی کپی کن
    if not os.path.exists(output_file):
        src = "/home/z/my-project/download/A136030_1_to_8000.txt"
        if sys.platform == 'win32':
            # در ویندوز، کاربر باید فایل رو کپی کنه
            log(f"هشدار: فایل A136030_1_to_8000.txt در {work_dir} نیست!")
            log(f"لطفاً فایل را از مسیر اصلی کپی کنید.")
            return
        else:
            import shutil
            shutil.copy(src, output_file)
    
    # خوندن فایل
    lines = []
    with open(output_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # آپدیت خط idx
    if idx <= len(lines):
        parts = lines[idx-1].strip().split('\t')
        if len(parts) == 2:
            lines[idx-1] = f"{idx}\t{factor}\n"
    
    # نوشتن
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    log(f"فایل خروجی آپدیت شد: idx {idx} = {factor}")


def idle_updater(work_dir, stop_event):
    """هر 10 ثانیه فایل idle.txt رو آپدیت می‌کنه."""
    idle_file = os.path.join(work_dir, "idle.txt")
    while not stop_event.is_set():
        with open(idle_file, 'w', encoding='utf-8') as f:
            f.write(f"برنامه زنده است\n")
            f.write(f"زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Threads: {NUM_THREADS}\n")
            
            # خوندن چک‌پوینت
            try:
                with open(os.path.join(work_dir, "checkpoint.json"), 'r') as cf:
                    ckpt = json.load(cf)
                f.write(f"\nپیشرفت:\n")
                for key, val in sorted(ckpt.items()):
                    if key.endswith('_k'):
                        idx = key.replace('_k', '')
                        f.write(f"  idx {idx}: k = {val:,}\n")
            except:
                pass
            
            # خوندن نتایج
            try:
                with open(os.path.join(work_dir, "results.txt"), 'r') as rf:
                    results = rf.read().strip()
                if results:
                    f.write(f"\nعوامل پیدا شده:\n{results}\n")
            except:
                pass
        
        stop_event.wait(IDLE_UPDATE_SEC)


def main():
    print("=" * 60)
    print("A136030 Factor Finder - 4-Thread Version")
    print("=" * 60)
    print(f"Work directory: {WORK_DIR}")
    print(f"Threads: {NUM_THREADS}")
    print(f"K_LIMIT: {K_LIMIT:,}")
    print(f"Targets: {[(i,p) for i,p in TARGETS]}")
    print("=" * 60)
    
    # ساخت پوشه کاری
    os.makedirs(WORK_DIR, exist_ok=True)
    
    main_log = os.path.join(WORK_DIR, "main.log")
    log(f"شروع برنامه با {NUM_THREADS} نخ", main_log)
    log(f"پوشه کاری: {WORK_DIR}", main_log)
    
    # ساخت سیو اعداد اول
    log("ساخت سیو اعداد اول...", main_log)
    small_primes = build_small_primes(5000)
    log(f"  {len(small_primes)} عدد اول", main_log)
    
    # کپی فایل خروجی اصلی (لینوکس فقط)
    if sys.platform != 'win32':
        import shutil
        src = "/home/z/my-project/download/A136030_1_to_8000.txt"
        dst = os.path.join(WORK_DIR, "A136030_1_to_8000.txt")
        if not os.path.exists(dst):
            shutil.copy(src, dst)
            log(f"فایل خروجی کپی شد: {dst}", main_log)
    
    # ساخت صف کار
    target_queue = mp.Queue()
    for target in TARGETS:
        target_queue.put(target)
    
    # اضافه کردن اعداد بیشتر برای نخ‌های اضافی
    # اگه 4 نخ داریم ولی 3 هدف، نخ 4 رو idle می‌ذاریم یا کاری بدیم
    # بذار اعداد اول بعدی رو اضافه کنیم
    from sympy import primerange
    all_primes = list(primerange(2, 100000))
    candidate_primes = [p for p in all_primes if p not in MERSENNE_PRIME_EXPONENTS]
    
    # اعداد بعدی که -1 هستن
    output_file = os.path.join(WORK_DIR, "A136030_1_to_8000.txt")
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                parts = line.strip().split('\t')
                if len(parts) == 2 and parts[1] == '-1':
                    p = candidate_primes[line_num - 1]
                    if (line_num, p) not in TARGETS:
                        target_queue.put((line_num, p))
                        if target_queue.qsize() >= 20:  # محدودیت صف
                            break
    
    log(f"تعداد کار در صف: {target_queue.qsize()}", main_log)
    
    # اشیاء به اشتراک گذاشته شده
    result_dict = {}
    checkpoint_lock = threading.Lock()
    
    # شروع به‌روزرسانی idle
    stop_event = threading.Event()
    idle_thread = threading.Thread(
        target=idle_updater, 
        args=(WORK_DIR, stop_event),
        daemon=True
    )
    idle_thread.start()
    log("نخ idle شروع شد", main_log)
    
    # شروع نخ‌های کارگر
    threads = []
    for i in range(NUM_THREADS):
        t = threading.Thread(
            target=worker_thread,
            args=(i+1, target_queue, result_dict, checkpoint_lock, 
                  small_primes, WORK_DIR),
            daemon=True
        )
        t.start()
        threads.append(t)
        log(f"نخ {i+1} شروع شد", main_log)
    
    # منتظر تموم شدن نخ‌ها
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(60)
            alive = sum(1 for t in threads if t.is_alive())
            log(f"نخ‌های فعال: {alive}/{NUM_THREADS}", main_log)
    except KeyboardInterrupt:
        log("توقف توسط کاربر", main_log)
        stop_event.set()
    
    # پایان
    stop_event.set()
    log("=" * 60, main_log)
    log("برنامه تمام شد", main_log)
    log(f"عوامل پیدا شده: {len(result_dict)}", main_log)
    for idx, factor in result_dict.items():
        log(f"  idx {idx}: {factor}", main_log)
    log("=" * 60, main_log)


if __name__ == "__main__":
    main()
