#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A136030 Factor Finder - 4-Thread Work Division on M(1277)
=========================================================
Searches for the smallest prime factor of M(1277) = 2^1277 - 1
which is the missing value at index 192 in A136030.

Work Division Strategy:
- Divide the k-range [1, K_LIMIT] into 4 chunks
- Each thread searches a DIFFERENT k-range (no overlap)
- Thread 1: k = [1,                  K_LIMIT/4)
- Thread 2: k = [K_LIMIT/4,          K_LIMIT/2)
- Thread 3: k = [K_LIMIT/2,          3*K_LIMIT/4)
- Thread 4: k = [3*K_LIMIT/4,        K_LIMIT]
- All threads work on the SAME number (M(1277))

This way we get 4x speedup on a single number.

Files created in E:\A136030_Search\:
    - checkpoint.json    checkpoint
    - idle.txt           alive indicator
    - main.log           main log
    - thread_1.log ... thread_4.log   per-thread logs
    - results.txt        found factors
    - A136030_1_to_8000.txt   output file (updated when factor found)
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

# ============================================================
# ===== CONFIG - YOU CAN CHANGE THESE VALUES ================
# ============================================================
# Work directory
if sys.platform == 'win32':
    WORK_DIR = r"E:\A136030_Search"
else:
    WORK_DIR = "/home/z/my-project/A136030_Search"

# *** CHANGE NUM_THREADS IF YOUR CPU IS OVERLOADED ***
# 4 = default (uses 4 cores, full speed but high CPU)
# 2 = light load (uses 2 cores, slower but PC stays responsive)
# 1 = minimum load (uses 1 core, slowest but no pressure on PC)
NUM_THREADS = 2
CHUNK_SIZE = 10_000_000  # 10M k per chunk
IDLE_UPDATE_SEC = 10
# Sleep between chunks to reduce CPU load (seconds)
# 0 = no sleep (full speed)
# 0.5 = light sleep (slight slowdown)
# 1.0 = gentle mode (PC stays cool)
SLEEP_BETWEEN_CHUNKS = 0.5

# *** CHANGE THIS VARIABLE TO EXTEND THE SEARCH ***
# If the search finishes without finding a factor, increase K_LIMIT and rerun.
# The program will automatically resume from the checkpoint.
# Examples:
#   K_LIMIT = 10_000_000_000       # 10 billion  -> ~40 min
#   K_LIMIT = 100_000_000_000      # 100 billion -> ~6.5 hours
#   K_LIMIT = 1_000_000_000_000    # 1 trillion  -> ~2.5 days
#   K_LIMIT = 10_000_000_000_000   # 10 trillion -> ~25 days
#   K_LIMIT = 100_000_000_000_000  # 100 trillion-> ~8 months
K_LIMIT = 10_000_000_000  # 10 billion
# ============================================================

# Target: M(1277) at idx 192 (the FIRST missing value)
TARGET_IDX = 192
TARGET_P = 1277


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


def worker_thread(thread_id, k_start, k_end, p, target_idx,
                  result_dict, checkpoint_lock, found_event,
                  small_primes, work_dir, stop_event):
    """Worker thread - searches a SPECIFIC k-range for M(p).
    This is work division: each thread handles a different k-range.
    """
    thread_log = os.path.join(work_dir, "thread_{}.log".format(thread_id))
    ckpt_file = os.path.join(work_dir, "checkpoint.json")

    log("Thread {}: k-range = [{:,}, {:,})".format(thread_id, k_start, k_end), thread_log)
    log("Thread {}: searching M({}) [idx={}]".format(thread_id, p, target_idx), thread_log)
    log("Thread {}: max q in this range = {:.2e}".format(
        thread_id, 2 * k_end * p), thread_log)

    # Load checkpoint
    with checkpoint_lock:
        try:
            with open(ckpt_file, 'r', encoding='utf-8') as f:
                ckpt = json.load(f)
        except:
            ckpt = {}

    # Resume from checkpoint (per thread)
    saved_k = ckpt.get("thread_{}_k".format(thread_id), k_start)
    if saved_k > k_start:
        k_start = saved_k
        log("Thread {}: resuming from k={:,}".format(thread_id, k_start), thread_log)

    chunk_count = 0
    t_start = time.time()

    for chunk_start in range(k_start, k_end + 1, CHUNK_SIZE):
        if stop_event.is_set() or found_event.is_set():
            log("Thread {}: stopping (found={} stopped={})".format(
                thread_id, found_event.is_set(), stop_event.is_set()), thread_log)
            return

        chunk_end = min(chunk_start + CHUNK_SIZE, k_end + 1)

        factor, last_k = search_chunk(p, chunk_start, chunk_end, small_primes)
        chunk_count += 1

        if factor:
            elapsed = time.time() - t_start
            log("Thread {}: *** FACTOR FOUND! ***".format(thread_id), thread_log)
            log("  M({}) = {}".format(p, factor), thread_log)
            log("  k = {:,}".format(last_k), thread_log)
            log("  time = {:.1f}s".format(elapsed), thread_log)

            with checkpoint_lock:
                result_dict['factor'] = factor
                result_dict['thread'] = thread_id
                result_dict['k'] = last_k
                # Save to results.txt
                results_file = os.path.join(work_dir, "results.txt")
                with open(results_file, 'a', encoding='utf-8') as f:
                    f.write("M({}) [idx={}] = {}\n".format(p, target_idx, factor))
                    f.write("  found by thread {}, k={:,}, time={:.1f}s\n".format(
                        thread_id, last_k, elapsed))
                    f.write("  timestamp: {}\n\n".format(datetime.now().isoformat()))

                # Update output file
                update_output_file(work_dir, target_idx, factor)

                # Update checkpoint
                try:
                    with open(ckpt_file, 'r', encoding='utf-8') as f:
                        ckpt = json.load(f)
                except:
                    ckpt = {}
                ckpt["factor"] = factor
                ckpt["found_by_thread"] = thread_id
                with open(ckpt_file, 'w', encoding='utf-8') as f:
                    json.dump(ckpt, f, indent=2, ensure_ascii=False)

            # Signal other threads to stop
            found_event.set()
            return

        # Save checkpoint
        with checkpoint_lock:
            try:
                with open(ckpt_file, 'r', encoding='utf-8') as f:
                    ckpt = json.load(f)
            except:
                ckpt = {}
            ckpt["thread_{}_k".format(thread_id)] = chunk_end - 1
            with open(ckpt_file, 'w', encoding='utf-8') as f:
                json.dump(ckpt, f, indent=2, ensure_ascii=False)

        # Log progress
        elapsed = time.time() - t_start
        max_q = 2 * (chunk_end - 1) * p + 1
        pct = (chunk_end - 1 - k_start) / (k_end - k_start) * 100 if k_end > k_start else 100
        log("Thread {}: chunk {}: k={:,} ({:.1f}% of range), max_q={:.2e}, time={:.0f}s".format(
            thread_id, chunk_count, chunk_end - 1, pct, max_q, elapsed), thread_log)

        # Sleep to reduce CPU load
        if SLEEP_BETWEEN_CHUNKS > 0:
            time.sleep(SLEEP_BETWEEN_CHUNKS)

    # Finished range without finding factor
    log("Thread {}: range finished, no factor found in [{:,}, {:,})".format(
        thread_id, k_start, k_end), thread_log)


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


def idle_updater(work_dir, stop_event, threads_info, k_ranges):
    """Update idle.txt every 10 seconds."""
    idle_file = os.path.join(work_dir, "idle.txt")
    ckpt_file = os.path.join(work_dir, "checkpoint.json")
    results_file = os.path.join(work_dir, "results.txt")

    while not stop_event.is_set():
        with open(idle_file, 'w', encoding='utf-8') as f:
            f.write("=== Program is ALIVE ===\n")
            f.write("Time: {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            f.write("Target: M({}) [idx={}]\n".format(TARGET_P, TARGET_IDX))
            f.write("Threads: {} (work division on same number)\n".format(NUM_THREADS))
            f.write("K_LIMIT: {:,}\n".format(K_LIMIT))
            f.write("\n")

            # Checkpoint
            try:
                with open(ckpt_file, 'r', encoding='utf-8') as cf:
                    ckpt = json.load(cf)

                factor = ckpt.get("factor")
                if factor:
                    f.write("*** FACTOR FOUND! ***\n")
                    f.write("  M({}) = {}\n".format(TARGET_P, factor))
                    f.write("  found by thread {}\n\n".format(ckpt.get("found_by_thread", "?")))
                else:
                    f.write("--- Progress (each thread searches a k-range) ---\n")
                    for i in range(NUM_THREADS):
                        k_start, k_end = k_ranges[i]
                        k = ckpt.get("thread_{}_k".format(i+1), k_start)
                        max_q = 2 * k * TARGET_P + 1 if k > 0 else 0
                        pct = (k - k_start) / (k_end - k_start) * 100 if k_end > k_start else 0
                        f.write("  Thread {}: k = {:,} ({:.1f}% of [{:,}-{:,}]), max_q = {:.2e}\n".format(
                            i+1, k, pct, k_start, k_end, max_q))
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
    print("A136030 Factor Finder - 4-Thread on M(1277)")
    print("=" * 60)
    print("Work directory: {}".format(WORK_DIR))
    print("Threads: {}".format(NUM_THREADS))
    print("Target: M({}) [idx={}]".format(TARGET_P, TARGET_IDX))
    print("K_LIMIT: {:,}".format(K_LIMIT))
    print("Strategy: divide k-range into 4 chunks (work division)")
    print("=" * 60)

    os.makedirs(WORK_DIR, exist_ok=True)

    main_log = os.path.join(WORK_DIR, "main.log")
    log("Program started - {} threads on M({})".format(NUM_THREADS, TARGET_P), main_log)
    log("Work directory: {}".format(WORK_DIR), main_log)
    log("Strategy: work division (each thread searches a different k-range)", main_log)

    # Build small primes
    log("Building small primes sieve...", main_log)
    small_primes = build_small_primes(5000)
    log("  {} small primes".format(len(small_primes)), main_log)

    # Copy output file if not exists (Linux only)
    if sys.platform != 'win32':
        import shutil
        src = "/home/z/my-project/download/A136030_1_to_8000.txt"
        dst = os.path.join(WORK_DIR, "A136030_1_to_8000.txt")
        if not os.path.exists(dst) and os.path.exists(src):
            shutil.copy(src, dst)
            log("Output file copied: {}".format(dst), main_log)

    # Divide k-range into 4 chunks
    chunk_size = K_LIMIT // NUM_THREADS
    k_ranges = []
    for i in range(NUM_THREADS):
        k_start = i * chunk_size + 1
        k_end = (i + 1) * chunk_size if i < NUM_THREADS - 1 else K_LIMIT
        k_ranges.append((k_start, k_end))
        log("Thread {} k-range: [{:,}, {:,})".format(i+1, k_start, k_end), main_log)

    result_dict = {}
    checkpoint_lock = threading.Lock()
    found_event = threading.Event()
    stop_event = threading.Event()

    # Start idle updater
    idle_thread = threading.Thread(
        target=idle_updater,
        args=(WORK_DIR, stop_event, {}, k_ranges),
        daemon=True
    )
    idle_thread.start()
    log("Idle thread started", main_log)

    # Start worker threads - each on a different k-range of M(1277)
    threads = []
    for i in range(NUM_THREADS):
        k_start, k_end = k_ranges[i]
        t = threading.Thread(
            target=worker_thread,
            args=(i+1, k_start, k_end, TARGET_P, TARGET_IDX,
                  result_dict, checkpoint_lock, found_event,
                  small_primes, WORK_DIR, stop_event),
            daemon=True
        )
        t.start()
        threads.append(t)
        log("Thread {} started on k-range [{:,}, {:,})".format(i+1, k_start, k_end), main_log)

    # Wait for all threads
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(60)
            alive = sum(1 for t in threads if t.is_alive())
            log("Active threads: {}/{}".format(alive, NUM_THREADS), main_log)
            if found_event.is_set():
                log("Factor found! Waiting for other threads to stop...", main_log)
                # Give other threads time to stop
                time.sleep(5)
                break
    except KeyboardInterrupt:
        log("Stopped by user (Ctrl+C)", main_log)
        stop_event.set()

    stop_event.set()
    log("=" * 60, main_log)
    log("Program finished", main_log)
    if 'factor' in result_dict:
        log("FACTOR FOUND: M({}) = {}".format(TARGET_P, result_dict['factor']), main_log)
        log("  by thread {}, k={:,}".format(result_dict['thread'], result_dict['k']), main_log)
    else:
        log("No factor found in k-range [1, {:,}]".format(K_LIMIT), main_log)
    log("=" * 60, main_log)


if __name__ == "__main__":
    main()
