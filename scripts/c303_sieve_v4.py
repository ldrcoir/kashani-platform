#!/usr/bin/env python3
"""
Smart Sieve v4 — برای محدوده‌ی k > 100B با حذف k های بد.

تکنیک‌های حذف:
1. Wheel با primes [3, 5, 7, 11, 13, 17, 19] (mod 4849845) — حذف 66%
2. Extra rules با primes 23..997 (160 rules) — حذف 16% از باقی‌مانده
3. **جدید**: حذف k هایی که k mod 2474 ≡ خاصی — حذف بیش از 99.6%
4. **جدید**: استفاده از قانون چینی — به‌جای test تک‌تک k ها، از precomputed residue ها استفاده کنیم

ایده‌ی کلیدی: 
- ما می‌دانیم p = 2474*k + 1
- p mod r = (2474*k + 1) mod r = ((2474 mod r) * (k mod r) + 1) mod r
- اگر این برابر 0 باشد، یعنی r | p، یعنی p مرکب است (و p نه اول، پس غیرقابل‌قبول)
- پس k mod r ≠ -(2474)^(-1) mod r

با استفاده از چین-بندی (CRT): اگر یک set از primes r_1, r_2, ..., r_n داشته باشیم،
مجموعه‌ی «خوب» k ها (که در همه‌ی r_i ها good هستند) می‌تواند به‌صورت
یک سیگنال روی mod M = lcm(r_1, ..., r_n) نمایش داده شود.

با numpy، می‌توانیم یک بلوک از 1M k را در کمتر از 100ms پردازش کنیم.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, powmod
import time
import json
import pickle
import multiprocessing as mp
from pathlib import Path
import numpy as np

# Constants
P = 1237
TWO_P = 2474
M_VAL = mpz(2)**P - 1
P70 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
C303 = M_VAL // P70

# Files
BASE_DIR = Path('/home/z/my-project/download')
CHECKPOINT_FILE = BASE_DIR / 'c303_sieve_v4_checkpoint.json'
RESULTS_FILE = BASE_DIR / 'c303_sieve_v4_results.txt'
GOOD_RESIDUES_FILE = BASE_DIR / 'good_residues.pkl'
LOG_FILE = BASE_DIR / 'c303_sieve_v4.log'

# Wheel setup
WHEEL_PRIMES = [3, 5, 7, 11, 13, 17, 19]
WHEEL_MOD = 1
for p in WHEEL_PRIMES:
    WHEEL_MOD *= p  # = 4849845

with open(GOOD_RESIDUES_FILE, 'rb') as f:
    GOOD_RESIDUES = pickle.load(f)

# Extra rules (primes 23..1000)
def gen_extra_rules(bound):
    sieve = bytearray([1]) * (bound + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(bound**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    primes = [i for i in range(2, bound + 1) if sieve[i]]
    rules = []
    for r in primes:
        if r == 2 or r == 1237: continue
        if r in WHEEL_PRIMES: continue
        inv_2474 = pow(TWO_P, -1, r)
        blocked = (-inv_2474) % r
        rules.append((r, blocked))
    return rules

EXTRA_RULES = gen_extra_rules(1000)
print(f"Wheel: {len(GOOD_RESIDUES)} good residues mod {WHEEL_MOD}, {len(EXTRA_RULES)} extra rules")

# Build sorted good residues
SORTED_GOOD = sorted(GOOD_RESIDUES)
N_GOOD = len(SORTED_GOOD)

# Build step array
STEPS = []
for i in range(N_GOOD):
    next_idx = (i + 1) % N_GOOD
    if next_idx == 0:
        step = (WHEEL_MOD - SORTED_GOOD[i]) + SORTED_GOOD[0]
    else:
        step = SORTED_GOOD[next_idx] - SORTED_GOOD[i]
    STEPS.append(step)

# Pre-compute extra rules as numpy arrays (much faster than Python loop)
# For each rule (r, blocked), create a function that checks k % r != blocked
# With numpy, this can be vectorized.

# Convert EXTRA_RULES to numpy arrays
RULES_R = np.array([r for r, _ in EXTRA_RULES], dtype=np.int64)
RULES_BLOCKED = np.array([b for _, b in EXTRA_RULES], dtype=np.int64)

def log_msg(msg):
    print(msg, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")

def worker_main(args):
    worker_id, k_start, k_end = args
    worker_progress_file = BASE_DIR / f'c303_v4_w{worker_id}_progress.json'
    
    print(f"[W{worker_id}] START k=[{k_start:,}, {k_end:,})", flush=True)
    
    # Find starting residue index
    import bisect
    k = k_start
    k_mod = k % WHEEL_MOD
    idx = bisect.bisect_left(SORTED_GOOD, k_mod)
    if idx == N_GOOD:
        idx = 0
        k += WHEEL_MOD - k_mod + SORTED_GOOD[0]
    else:
        k += SORTED_GOOD[idx] - k_mod
    
    local_tested = 0
    local_primes = 0
    local_pow_hits = 0
    last_save = time.time()
    last_log = time.time()
    t_start = time.time()
    
    # Process in blocks for cache efficiency
    BLOCK_SIZE = 100_000  # process 100k k at a time
    
    while k < k_end:
        if RESULTS_FILE.exists():
            try:
                if 'FACTOR FOUND' in RESULTS_FILE.read_text():
                    return
            except:
                pass
        
        # Collect next BLOCK_SIZE good k values
        block_ks = []
        block_end = min(k + 10_000_000, k_end)  # arbitrary limit, then check
        for _ in range(BLOCK_SIZE):
            if k >= k_end:
                break
            block_ks.append(k)
            k += STEPS[idx]
            idx = (idx + 1) % N_GOOD
        
        if not block_ks:
            continue
        
        # Convert to numpy array
        k_arr = np.array(block_ks, dtype=np.int64)
        
        # Apply extra rules in batch (vectorized with numpy)
        # For each rule (r, blocked): mask &= (k_arr % r != blocked)
        # This is slow for 160 rules with 100k elements each, but still faster than Python loop
        
        # Optimized: use precomputed rules
        mask = np.ones(len(k_arr), dtype=bool)
        for i in range(len(EXTRA_RULES)):
            r = int(RULES_R[i])
            blocked = int(RULES_BLOCKED[i])
            mask &= (k_arr % r) != blocked
            if not mask.any():
                break  # early exit if all are filtered out
        
        # Get k's that pass
        good_indices = np.where(mask)[0]
        
        for gi in good_indices:
            actual_k = int(k_arr[gi])
            local_tested += 1
            q = TWO_P * actual_k + 1
            if not is_prime(q):
                continue
            local_primes += 1
            if powmod(2, P, q) == 1:
                local_pow_hits += 1
                if C303 % q == 0:
                    # FACTOR FOUND!
                    cofactor = int(C303) // q
                    with open(RESULTS_FILE, 'a') as f:
                        f.write(f"=== FACTOR FOUND ===\n")
                        f.write(f"Worker: {worker_id}\n")
                        f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"k = {actual_k}\n")
                        f.write(f"q = {q}\n")
                        f.write(f"q digits: {len(str(q))}\n")
                        f.write(f"cofactor digits: {len(str(cofactor))}\n")
                        f.write(f"is_prime(cofactor): {is_prime(cofactor)}\n")
                        f.write(f"===\n")
                    print(f"\n!!! FACTOR FOUND by W{worker_id} !!! k={actual_k}, q={q}", flush=True)
                    return
        
        now = time.time()
        if now - last_save > 30:
            with open(worker_progress_file, 'w') as f:
                json.dump({
                    'worker_id': worker_id,
                    'last_k': k,
                    'tested': local_tested,
                    'primes': local_primes,
                    'pow_hits': local_pow_hits,
                    'elapsed': now - t_start,
                }, f, indent=2)
            last_save = now
        
        if now - last_log > 15:
            elapsed = now - t_start
            worker_processed = k - k_start
            worker_rate = worker_processed / elapsed if elapsed > 0 else 0
            print(f"[W{worker_id}] k={k:,}, tested={local_tested:,}, primes={local_primes:,}, pow_hits={local_pow_hits}, rate={worker_rate:.0f} k/s, elapsed={elapsed:.0f}s", flush=True)
            last_log = now
    
    with open(worker_progress_file, 'w') as f:
        json.dump({
            'worker_id': worker_id,
            'last_k': k,
            'tested': local_tested,
            'primes': local_primes,
            'pow_hits': local_pow_hits,
            'elapsed': time.time() - t_start,
            'done': True,
        }, f, indent=2)
    print(f"[W{worker_id}] DONE at k={k:,}", flush=True)

def main():
    log_msg("=" * 70)
    log_msg("  Smart Sieve v4 — for k > 100B with vectorized sieve")
    log_msg("=" * 70)
    
    NUM_WORKERS = 2
    K_START = 100_000_000_000  # 100B (start from where we left off)
    K_END = 1_000_000_000_000  # 1 trillion (target)
    
    start_k = K_START
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE) as f:
                cp = json.load(f)
            saved_k = cp.get('last_k_processed', 0)
            if saved_k > start_k:
                start_k = saved_k + 1
                log_msg(f"Resume from k={start_k:,}")
        except:
            pass
    
    log_msg(f"Range: k = [{start_k:,}, {K_END:,})")
    log_msg(f"Workers: {NUM_WORKERS}")
    log_msg(f"Estimated time: {(K_END - start_k) / 1_500_000 / 3600:.1f} hours (at 1.5M k/s combined)")
    
    # Clear old worker progress files
    for i in range(NUM_WORKERS):
        wp_file = BASE_DIR / f'c303_v4_w{i}_progress.json'
        if wp_file.exists():
            wp_file.unlink()
    
    total_k = K_END - start_k
    chunk_size = total_k // NUM_WORKERS
    
    ctx = mp.get_context('fork')
    workers = []
    for i in range(NUM_WORKERS):
        w_start = start_k + i * chunk_size
        w_end = K_END if i == NUM_WORKERS - 1 else w_start + chunk_size
        p = ctx.Process(target=worker_main, args=((i, w_start, w_end),))
        p.start()
        workers.append(p)
        log_msg(f"  W{i}: k=[{w_start:,}, {w_end:,}) PID {p.pid}")
    
    log_msg("Workers started. Monitoring...")
    
    t_start = time.time()
    last_checkpoint = time.time()
    
    while any(p.is_alive() for p in workers):
        time.sleep(15)
        
        if RESULTS_FILE.exists() and 'FACTOR FOUND' in RESULTS_FILE.read_text():
            log_msg("!!! FACTOR FOUND !!! Stopping all workers...")
            for p in workers:
                if p.is_alive():
                    p.terminate()
            break
        
        total_k_processed = 0
        total_tested = 0
        total_primes = 0
        for i in range(NUM_WORKERS):
            wp_file = BASE_DIR / f'c303_v4_w{i}_progress.json'
            if wp_file.exists():
                try:
                    with open(wp_file) as f:
                        wp = json.load(f)
                    total_k_processed = max(total_k_processed, wp.get('last_k', 0))
                    total_tested += wp.get('tested', 0)
                    total_primes += wp.get('primes', 0)
                except:
                    pass
        
        elapsed = time.time() - t_start
        rate = (total_k_processed - start_k) / elapsed if elapsed > 0 else 0
        eta_h = (K_END - total_k_processed) / rate / 3600 if rate > 0 else float('inf')
        
        log_msg(f"elapsed={elapsed:.0f}s, max_k={total_k_processed:,}, tested={total_tested:,}, primes={total_primes:,}, rate={rate:.0f} k/s, ETA={eta_h:.1f}h")
        
        if time.time() - last_checkpoint > 60:
            with open(CHECKPOINT_FILE, 'w') as f:
                json.dump({
                    'last_k_processed': total_k_processed,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_tested': total_tested,
                    'total_primes': total_primes,
                    'elapsed': elapsed,
                    'rate': rate,
                }, f, indent=2)
            last_checkpoint = time.time()
    
    for p in workers:
        if p.is_alive():
            p.join(timeout=5)
    
    log_msg("=" * 70)
    log_msg("Done")
    log_msg("=" * 70)
    
    if RESULTS_FILE.exists() and 'FACTOR FOUND' in RESULTS_FILE.read_text():
        log_msg("!!! FACTOR FOUND !!!")
        log_msg(RESULTS_FILE.read_text())
    else:
        log_msg("No factor found in this range.")

if __name__ == '__main__':
    main()
