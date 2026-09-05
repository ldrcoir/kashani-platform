#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A136030 Factor Finder - 4-Thread Work Division
==============================================
Searches for prime factors of Mersenne numbers M(p) = 2^p - 1
for missing values in A136030_1_to_8000.txt

Features:
- 4 threads (work DIVISION, not parallel on same number)
- Each thread works on a DIFFERENT number
- UTF-8 encoded logs and output
- Checkpoint in JSON (resume from saved point)
- idle.txt updated every 10 seconds
- Separate log for each thread
- Saves results immediately when found

Files created in E:\A136030_Search\:
    - checkpoint.json    checkpoint
    - idle.txt           alive indicator
    - main.log           main log
    - thread_1.log ... thread_4.log   per-thread logs
    - results.txt        found factors
    - A136030_1_to_8000.txt   output file
"""

import os
import sys
import time
import json
import threading
import gmpy2
from gmpy2 import is_prime as gmpy_is_prime
import numpy as np
from datetime import datetime

# Force UTF-8 output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# ===== CONFIG =====
# Windows path
WORK_DIR_WIN = r"E:\A136030_Search"
# Linux path (for testing here)
WORK_DIR_LINUX = "/home/z/my-project/A136030_Search"

if sys.platform == 'win32':
    WORK_DIR = WORK_DIR_WIN
else:
    WORK_DIR = WORK_DIR_LINUX

NUM_THREADS = 4
CHUNK_SIZE = 10_000_000  # 10M k per chunk
K_LIMIT = 10_000_000_000  # 10 billion
IDLE_UPDATE_SEC = 10

# Target values: (idx, p) - first 4 missing values
# Each thread gets ONE of these (work division)
TARGETS = [
    (192, 1277),  # thread 1
    (241, 1619),  # thread 2
    (258, 1753),  # thread 3
    (320, 2267),  # thread 4
]

MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607,
    1279, 2203, 2281, 3217, 4253, 4423
}


def log(msg, file=None):
    """Log with timestamp, UTF-8 encoded."""
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = "[{}] {}".format(ts, msg)
    if file:
        with open(file, 'a', encoding='utf-8') as f:
            f.write(line + "\n")
    else:
        print(line, flush=True)


def build_small_primes(limit=5000):
    """Build sieve of small primes."""
    sa = np.ones(limit + 1, dtype=bool)
    sa[0] = sa[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sa[i]:
            sa[i*i::i] = False
    return [int(i) for i in np.flatnonzero(sa)]


def search_chunk(p, k_start, k_end, small_primes):
    """Search one chunk for factor of M(p).
    Returns: (factor, last_k_checked)
    """
    p_mod4 = p & 3
    valid_residues = (0, 3) if p_mod4 == 1 else (0, 1)
    two_p = 2 * p
    size = k_end - k_start
    is_composite = np.zeros(size, dtype=bool)

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


def worker_thread(thread_id, target, result_dict, checkpoint_lock,
                  small_primes, work_dir, stop_event):
    """Worker thread - works on ONE specific target (work division)."""
    idx, p = target
    thread_log = os.path.join(work_dir, "thread_{}.log".format(thread_id))
    ckpt_file = os.path.join(work_dir, "checkpoint.json")

    log("Thread {}: starting M({}) [idx={}]".format(thread_id, p, idx), thread_log)

    # Load checkpoint
    with checkpoint_lock:
        try:
            with open(ckpt_file, 'r', encoding='utf-8') as f:
                ckpt = json.load(f)
        except:
            ckpt = {}

    k_start = ckpt.get("{}_k".format(idx), 1)
    log("Thread {}: resuming from k={:,}".format(thread_id, k_start), thread_log)
    log("Thread {}: target K_LIMIT={:,}".format(thread_id, K_LIMIT), thread_log)
    log("Thread {}: max q to test = {:.2e}".format(
        thread_id, 2 * K_LIMIT * p + 1), thread_log)

    chunk_count = 0
    t_start = time.time()

    for chunk_start in range(k_start, K_LIMIT + 1, CHUNK_SIZE):
        if stop_event.is_set():
            log("Thread {}: stopped by user".format(thread_id), thread_log)
            return

        chunk_end = min(chunk_start + CHUNK_SIZE, K_LIMIT + 1)

        factor, last_k = search_chunk(p, chunk_start, chunk_end, small_primes)
        chunk_count += 1

        if factor:
            elapsed = time.time() - t_start
            log("Thread {}: *** FACTOR FOUND! ***".format(thread_id), thread_log)
            log("  M({}) = {}".format(p, factor), thread_log)
            log("  k = {:,}".format(last_k), thread_log)
            log("  time = {:.1f}s".format(elapsed), thread_log)

            with checkpoint_lock:
                result_dict[idx] = factor
                # Save to results.txt
                results_file = os.path.join(work_dir, "results.txt")
                with open(results_file, 'a', encoding='utf-8') as f:
                    f.write("M({}) [idx={}] = {}\n".format(p, idx, factor))
                    f.write("  found by thread {}, k={:,}, time={:.1f}s\n".format(
                        thread_id, last_k, elapsed))
                    f.write("  timestamp: {}\n\n".format(datetime.now().isoformat()))

                # Update output file
                update_output_file(work_dir, idx, factor)

                # Update checkpoint
                try:
                    with open(ckpt_file, 'r', encoding='utf-8') as f:
                        ckpt = json.load(f)
                except:
                    ckpt = {}
                ckpt["{}".format(idx)] = factor
                with open(ckpt_file, 'w', encoding='utf-8') as f:
                    json.dump(ckpt, f, indent=2, ensure_ascii=False)

            return

        # Save checkpoint
        with checkpoint_lock:
            try:
                with open(ckpt_file, 'r', encoding='utf-8') as f:
                    ckpt = json.load(f)
            except:
                ckpt = {}
            ckpt["{}_k".format(idx)] = chunk_end - 1
            with open(ckpt_file, 'w', encoding='utf-8') as f:
                json.dump(ckpt, f, indent=2, ensure_ascii=False)

        # Log progress
        elapsed = time.time() - t_start
        max_q = 2 * (chunk_end - 1) * p + 1
        log("Thread {}: M({}) chunk {}: k={:,}, max_q={:.2e}, time={:.0f}s".format(
            thread_id, p, chunk_count, chunk_end - 1, max_q, elapsed), thread_log)

    # Finished without finding factor
    log("Thread {}: M({}) finished, no factor found (up to k={:,})".format(
        thread_id, p, K_LIMIT), thread_log)


def update_output_file(work_dir, idx, factor):
    """Update A136030_1_to_8000.txt with found factor."""
    output_file = os.path.join(work_dir, "A136030_1_to_8000.txt")

    if not os.path.exists(output_file):
        log("Warning: A136030_1_to_8000.txt not found in {}".format(work_dir))
        return

    with open(output_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if idx <= len(lines):
        parts = lines[idx-1].strip().split('\t')
        if len(parts) == 2:
            lines[idx-1] = "{}\t{}\n".format(idx, factor)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    log("Output file updated: idx {} = {}".format(idx, factor))


def idle_updater(work_dir, stop_event, threads_info):
    """Update idle.txt every 10 seconds."""
    idle_file = os.path.join(work_dir, "idle.txt")
    ckpt_file = os.path.join(work_dir, "checkpoint.json")
    results_file = os.path.join(work_dir, "results.txt")

    while not stop_event.is_set():
        with open(idle_file, 'w', encoding='utf-8') as f:
            f.write("=== Program is ALIVE ===\n")
            f.write("Time: {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            f.write("Threads: {}\n".format(NUM_THREADS))
            f.write("Work directory: {}\n".format(work_dir))
            f.write("\n")

            # Checkpoint
            try:
                with open(ckpt_file, 'r', encoding='utf-8') as cf:
                    ckpt = json.load(cf)
                f.write("--- Progress ---\n")
                for idx, p in TARGETS:
                    k = ckpt.get("{}_k".format(idx), 0)
                    factor = ckpt.get("{}".format(idx))
                    if factor:
                        f.write("  idx {} (M{}): FOUND = {}\n".format(idx, p, factor))
                    else:
                        max_q = 2 * k * p + 1 if k > 0 else 0
                        pct = k / K_LIMIT * 100 if K_LIMIT > 0 else 0
                        f.write("  idx {} (M{}): k = {:,} ({:.1f}%), max_q = {:.2e}\n".format(
                            idx, p, k, pct, max_q))
            except Exception as e:
                f.write("  (checkpoint error: {})\n".format(e))

            f.write("\n")

            # Results
            try:
                with open(results_file, 'r', encoding='utf-8') as rf:
                    results = rf.read().strip()
                if results:
                    f.write("--- Found Factors ---\n")
                    f.write(results + "\n")
                else:
                    f.write("--- No factors found yet ---\n")
            except:
                f.write("--- No results file yet ---\n")

        stop_event.wait(IDLE_UPDATE_SEC)


def main():
    print("=" * 60)
    print("A136030 Factor Finder - 4-Thread Work Division")
    print("=" * 60)
    print("Work directory: {}".format(WORK_DIR))
    print("Threads: {}".format(NUM_THREADS))
    print("K_LIMIT: {:,}".format(K_LIMIT))
    print("Targets (work division):")
    for i, (idx, p) in enumerate(TARGETS, 1):
        print("  Thread {} -> idx={}, M({})".format(i, idx, p))
    print("=" * 60)

    os.makedirs(WORK_DIR, exist_ok=True)

    main_log = os.path.join(WORK_DIR, "main.log")
    log("Program started with {} threads (work division mode)".format(NUM_THREADS), main_log)
    log("Work directory: {}".format(WORK_DIR), main_log)

    # Build small primes
    log("Building small primes sieve...", main_log)
    small_primes = build_small_primes(5000)
    log("  {} small primes".format(len(small_primes)), main_log)

    # Copy output file if not exists
    if sys.platform != 'win32':
        import shutil
        src = "/home/z/my-project/download/A136030_1_to_8000.txt"
        dst = os.path.join(WORK_DIR, "A136030_1_to_8000.txt")
        if not os.path.exists(dst) and os.path.exists(src):
            shutil.copy(src, dst)
            log("Output file copied: {}".format(dst), main_log)

    result_dict = {}
    checkpoint_lock = threading.Lock()
    threads_info = {}
    stop_event = threading.Event()

    # Start idle updater
    idle_thread = threading.Thread(
        target=idle_updater,
        args=(WORK_DIR, stop_event, threads_info),
        daemon=True
    )
    idle_thread.start()
    log("Idle thread started", main_log)

    # Start worker threads (each on a different target = work division)
    threads = []
    for i, target in enumerate(TARGETS):
        if i >= NUM_THREADS:
            break
        t = threading.Thread(
            target=worker_thread,
            args=(i+1, target, result_dict, checkpoint_lock,
                  small_primes, WORK_DIR, stop_event),
            daemon=True
        )
        t.start()
        threads.append(t)
        log("Thread {} started on M({}) [idx={}]".format(i+1, target[1], target[0]), main_log)

    # Wait for all threads to finish
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(60)
            alive = sum(1 for t in threads if t.is_alive())
            log("Active threads: {}/{}".format(alive, NUM_THREADS), main_log)
    except KeyboardInterrupt:
        log("Stopped by user (Ctrl+C)", main_log)
        stop_event.set()

    stop_event.set()
    log("=" * 60, main_log)
    log("Program finished", main_log)
    log("Factors found: {}".format(len(result_dict)), main_log)
    for idx, factor in result_dict.items():
        log("  idx {}: {}".format(idx, factor), main_log)
    log("=" * 60, main_log)


if __name__ == "__main__":
    main()
