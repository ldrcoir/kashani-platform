import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, powmod
import time
import json
import pickle
import os
import signal
import multiprocessing as mp
from pathlib import Path
import bisect

# Constants
P = 1237
TWO_P = 2474
M = mpz(2)**P - 1
P70 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
C303 = M // P70

# Files
BASE_DIR = Path('/home/z/my-project/download')
CHECKPOINT_FILE = BASE_DIR / 'c303_sieve_checkpoint.json'
RESULTS_FILE = BASE_DIR / 'c303_sieve_results.txt'
WATCHDOG_FILE = BASE_DIR / 'c303_sieve_watchdog.log'
GOOD_RESIDUES_FILE = BASE_DIR / 'good_residues.pkl'
LOG_FILE = BASE_DIR / 'c303_sieve_log.txt'

# Wheel setup
WHEEL_PRIMES = [3, 5, 7, 11, 13, 17, 19]
WHEEL_MOD = 1
for p in WHEEL_PRIMES:
    WHEEL_MOD *= p

# Load good residues
with open(GOOD_RESIDUES_FILE, 'rb') as f:
    GOOD_RESIDUES = pickle.load(f)

# Generate extra sieve rules
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

SORTED_GOOD = sorted(GOOD_RESIDUES)
N_GOOD = len(SORTED_GOOD)

STEPS = []
for i in range(N_GOOD):
    next_idx = (i + 1) % N_GOOD
    if next_idx == 0:
        step = (WHEEL_MOD - SORTED_GOOD[i]) + SORTED_GOOD[0]
    else:
        step = SORTED_GOOD[next_idx] - SORTED_GOOD[i]
    STEPS.append(step)

def log_msg(msg):
    print(msg, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")

def worker_main(args):
    worker_id, k_start, k_end = args
    worker_progress_file = BASE_DIR / f'c303_w{worker_id}_progress.json'
    
    # Setup
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
    
    while k < k_end:
        # Check if any factor found
        if RESULTS_FILE.exists():
            try:
                if 'FACTOR FOUND' in RESULTS_FILE.read_text():
                    return
            except:
                pass
        
        # Extra sieve check
        passes = True
        for r, blocked in EXTRA_RULES:
            if k % r == blocked:
                passes = False
                break
        if not passes:
            k += STEPS[idx]
            idx = (idx + 1) % N_GOOD
            continue
        
        local_tested += 1
        q = TWO_P * k + 1
        if not is_prime(q):
            k += STEPS[idx]
            idx = (idx + 1) % N_GOOD
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
                    f.write(f"Elapsed (s): {time.time() - t_start:.1f}\n")
                    f.write(f"k = {k}\n")
                    f.write(f"q = {q}\n")
                    f.write(f"q digits: {len(str(q))}\n")
                    f.write(f"cofactor: {cofactor}\n")
                    f.write(f"cofactor digits: {len(str(cofactor))}\n")
                    f.write(f"is_prime(cofactor): {is_prime(cofactor)}\n")
                    f.write(f"===\n")
                
                print(f"\n!!! FACTOR FOUND by W{worker_id} !!! k={k}, q={q}", flush=True)
                print(f"cofactor = {str(cofactor)[:60]}... ({len(str(cofactor))} digits)", flush=True)
                print(f"is_prime(cofactor): {is_prime(cofactor)}", flush=True)
                return
        
        k += STEPS[idx]
        idx = (idx + 1) % N_GOOD
        
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
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
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
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'done': True,
        }, f, indent=2)
    print(f"[W{worker_id}] DONE at k={k:,}, tested={local_tested:,}, primes={local_primes:,}", flush=True)

def main():
    log_msg("=" * 70)
    log_msg("  Multi-process C303 Smart Sieve (4 workers + watchdog)")
    log_msg("=" * 70)
    
    NUM_WORKERS = 2
    K_START = 15_000_000
    K_END = 100_000_000_000  # 100 billion
    
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
    log_msg(f"Estimated time: {(K_END - start_k) / 783_000 / 3600:.1f} hours")
    
    # Clear old worker progress files
    for i in range(NUM_WORKERS):
        wp_file = BASE_DIR / f'c303_w{i}_progress.json'
        if wp_file.exists():
            wp_file.unlink()
    
    # Divide work
    total_k = K_END - start_k
    chunk_size = total_k // NUM_WORKERS
    
    # Start workers
    ctx = mp.get_context('fork')
    workers = []
    for i in range(NUM_WORKERS):
        w_start = start_k + i * chunk_size
        w_end = K_END if i == NUM_WORKERS - 1 else w_start + chunk_size
        p = ctx.Process(target=worker_main, args=((i, w_start, w_end),))
        p.start()
        workers.append(p)
        log_msg(f"  W{i}: k=[{w_start:,}, {w_end:,}) — PID {p.pid}")
    
    log_msg("Workers started. Watchdog monitoring...")
    
    t_start = time.time()
    last_checkpoint = time.time()
    
    while True:
        alive = sum(1 for p in workers if p.is_alive())
        if alive == 0:
            log_msg("All workers exited.")
            break
        
        # Check factor found
        factor_found = False
        if RESULTS_FILE.exists():
            try:
                if 'FACTOR FOUND' in RESULTS_FILE.read_text():
                    log_msg("!!! FACTOR FOUND !!! Stopping all workers...")
                    for p in workers:
                        if p.is_alive():
                            p.terminate()
                    factor_found = True
                    break
            except:
                pass
        
        # Aggregate progress
        total_k_processed = 0
        total_tested = 0
        total_primes = 0
        total_pow_hits = 0
        for i in range(NUM_WORKERS):
            wp_file = BASE_DIR / f'c303_w{i}_progress.json'
            if wp_file.exists():
                try:
                    with open(wp_file) as f:
                        wp = json.load(f)
                    total_k_processed = max(total_k_processed, wp.get('last_k', 0))
                    total_tested += wp.get('tested', 0)
                    total_primes += wp.get('primes', 0)
                    total_pow_hits += wp.get('pow_hits', 0)
                except:
                    pass
        
        elapsed = time.time() - t_start
        # Compute effective k rate from worker progress files
        # The actual k progress depends on which worker is furthest
        rate = (total_k_processed - start_k) / elapsed if elapsed > 0 else 0
        eta_h = (K_END - total_k_processed) / rate / 3600 if rate > 0 else float('inf')
        
        log_msg(f"alive={alive}/{NUM_WORKERS}, elapsed={elapsed:.0f}s, max_k={total_k_processed:,}, tested={total_tested:,}, primes={total_primes:,}, pow_hits={total_pow_hits}, rate={rate:.0f} k/s, ETA={eta_h:.1f}h")
        
        if time.time() - last_checkpoint > 60:
            with open(CHECKPOINT_FILE, 'w') as f:
                json.dump({
                    'last_k_processed': total_k_processed,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_tested': total_tested,
                    'total_primes': total_primes,
                    'total_pow_hits': total_pow_hits,
                    'elapsed': elapsed,
                    'rate': rate,
                }, f, indent=2)
            last_checkpoint = time.time()
        
        # Write watchdog log
        with open(WATCHDOG_FILE, 'a') as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] alive={alive}/{NUM_WORKERS}, max_k={total_k_processed:,}, rate={rate:.0f} k/s, ETA={eta_h:.1f}h\n")
        
        time.sleep(15)
    
    for p in workers:
        if p.is_alive():
            p.join(timeout=5)
    
    log_msg("=" * 70)
    log_msg("Done")
    log_msg("=" * 70)
    
    if RESULTS_FILE.exists():
        content = RESULTS_FILE.read_text()
        if 'FACTOR FOUND' in content:
            log_msg("!!! FACTOR FOUND !!!")
            log_msg(content)
        else:
            log_msg("No factor found (results file exists but no factor)")
    else:
        log_msg("No factor found")
    
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({
            'last_k_processed': total_k_processed,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'final': True,
            'total_tested': total_tested,
            'total_primes': total_primes,
            'no_factor_found': not factor_found,
        }, f, indent=2)

if __name__ == '__main__':
    main()
