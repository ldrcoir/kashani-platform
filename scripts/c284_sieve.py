#!/usr/bin/env python3
"""
Smart sieve for C284 = M(1229) / (87-digit cofactor).

Key insight from user's analysis:
- C284 ≡ 3 (mod 4) — negative discriminant!
- This means factors must be one 1 mod 4 and one 3 mod 4
- Standard Mersenne structure: q = 2*1229*k + 1 = 2458*k + 1

User's filter: q1 % 4 != q2 % 4 (one 1, one 3 mod 4)
This is a GOOD constraint, but can be strengthened.

Better approach:
- For C284 with C284 ≡ 3 (mod 4):
  - All factors q of M(1229) satisfy q ≡ 1 (mod 2458)
  - 2458 = 2 * 1229, 1229 ≡ 1 (mod 4)
  - So q = 2458*k + 1 = (2 * 1229) * k + 1
  - q mod 4 = (2458 * k + 1) mod 4 = (2 * k + 1) mod 4
  - If k even: q ≡ 1 (mod 4) (1 mod 4)
  - If k odd: q ≡ 3 (mod 4) (3 mod 4)
  - So: parity of k determines q mod 4!

For C284 ≡ 3 (mod 4), factors come in pairs (1 mod 4, 3 mod 4):
- One factor has even k, the other has odd k
- This is automatic from the structure!

So user's filter is REDUNDANT — it's already implied by the structure.
We don't need to test q1 % 4 != q2 % 4.

BUT we can use it as a fast filter to SKIP k values:
- For each k, q = 2458*k + 1 has q mod 4 = (2k + 1) mod 4
- We know that pairs (1 mod 4, 3 mod 4) must exist
- But we don't know which one is the factor

Actually, the user's filter only checks AFTER finding q | C. So it's a post-filter.

A better optimization:
1. Use wheel sieve to skip k values where q is composite
2. Use the smart sieve approach (like v5) for speed
3. The factor will be found when we test all k

Let me write an optimized version.
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
import bisect

# Constants
P = 1229  # Mersenne exponent
TWO_P = 2 * P  # 2458
M = mpz(2)**P - 1

# C284 = M(1229) / (87-digit cofactor)
C284 = mpz(53392955842462906502525256206896237530607657681405452248628829538140335056019091833139309039691476989536595672486245741799613486059460767317912672601233477410458189253022780891585730123223883909898404934891596729489833819787859139386557550548823481244976333432522178629028656984007087)

# Files
BASE_DIR = Path('/home/z/my-project/download')
CHECKPOINT_FILE = BASE_DIR / 'c284_sieve_checkpoint.json'
RESULTS_FILE = BASE_DIR / 'c284_sieve_results.txt'
LOG_FILE = BASE_DIR / 'c284_sieve.log'

# Wheel setup — primes [3, 5, 7, 11, 13, 17, 19] — these don't include 2 or P
WHEEL_PRIMES = [3, 5, 7, 11, 13, 17, 19]
WHEEL_MOD = 1
for p in WHEEL_PRIMES:
    WHEEL_MOD *= p  # = 4849845

# Generate wheel good residues for this specific Mersenne number
def gen_good_residues():
    print(f"Computing good residues mod {WHEEL_MOD} for p={P}...")
    wheel_blocked = {}
    for r in WHEEL_PRIMES:
        inv_two_p = pow(TWO_P, -1, r)
        blocked = (-inv_two_p) % r
        wheel_blocked[r] = blocked
    
    good = []
    for k0 in range(WHEEL_MOD):
        is_good = True
        for r in WHEEL_PRIMES:
            if k0 % r == wheel_blocked[r]:
                is_good = False
                break
        if is_good:
            good.append(k0)
    return good

GOOD_RESIDUES_FILE = BASE_DIR / f'good_residues_p{P}.pkl'
if GOOD_RESIDUES_FILE.exists():
    with open(GOOD_RESIDUES_FILE, 'rb') as f:
        GOOD_RESIDUES = pickle.load(f)
    print(f"Loaded {len(GOOD_RESIDUES)} good residues from cache")
else:
    GOOD_RESIDUES = gen_good_residues()
    with open(GOOD_RESIDUES_FILE, 'wb') as f:
        pickle.dump(GOOD_RESIDUES, f)
    print(f"Saved {len(GOOD_RESIDUES)} good residues")

# Extra sieve rules (primes 23..1000)
def gen_extra_rules(bound):
    sieve = bytearray([1]) * (bound + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(bound**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    primes = [i for i in range(2, bound + 1) if sieve[i]]
    rules = []
    for r in primes:
        if r == 2 or r == P: continue
        if r in WHEEL_PRIMES: continue
        inv_two_p = pow(TWO_P, -1, r)
        blocked = (-inv_two_p) % r
        rules.append((r, blocked))
    return rules

EXTRA_RULES = gen_extra_rules(1000)
print(f"Wheel: {len(GOOD_RESIDUES)} good residues mod {WHEEL_MOD}, {len(EXTRA_RULES)} extra rules")

# Build sorted good residues and step array
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

# Pre-convert rules to numpy
RULES_R = np.array([r for r, _ in EXTRA_RULES], dtype=np.int64)
RULES_BLOCKED = np.array([b for _, b in EXTRA_RULES], dtype=np.int64)

def log_msg(msg):
    print(msg, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")

def worker_main(args):
    worker_id, k_start, k_end = args
    worker_progress_file = BASE_DIR / f'c284_w{worker_id}_progress.json'
    
    print(f"[W{worker_id}] START k=[{k_start:,}, {k_end:,})", flush=True)
    
    # Find starting residue index
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
    local_factors = 0
    last_save = time.time()
    last_log = time.time()
    t_start = time.time()
    
    BLOCK_SIZE = 100_000
    
    while k < k_end:
        if RESULTS_FILE.exists():
            try:
                if 'FACTOR FOUND' in RESULTS_FILE.read_text():
                    return
            except:
                pass
        
        # Collect BLOCK_SIZE good k values
        block_ks = []
        for _ in range(BLOCK_SIZE):
            if k >= k_end:
                break
            block_ks.append(k)
            k += STEPS[idx]
            idx = (idx + 1) % N_GOOD
        
        if not block_ks:
            continue
        
        k_arr = np.array(block_ks, dtype=np.int64)
        
        # Apply extra rules (vectorized)
        mask = np.ones(len(k_arr), dtype=bool)
        for i in range(len(EXTRA_RULES)):
            r = int(RULES_R[i])
            blocked = int(RULES_BLOCKED[i])
            mask &= (k_arr % r) != blocked
            if not mask.any():
                break
        
        good_indices = np.where(mask)[0]
        
        for gi in good_indices:
            actual_k = int(k_arr[gi])
            local_tested += 1
            q = TWO_P * actual_k + 1
            
            # Primality check
            if not is_prime(q):
                continue
            local_primes += 1
            
            # Check if q | C284 (the fast way: pow(2, 1229, q) == 1)
            # This is faster than C284 % q for large q
            if powmod(2, P, q) == 1:
                # Verify q | C284
                if C284 % q == 0:
                    local_factors += 1
                    cofactor = int(C284) // q
                    with open(RESULTS_FILE, 'a') as f:
                        f.write(f"=== FACTOR FOUND ===\n")
                        f.write(f"Worker: {worker_id}\n")
                        f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"k = {actual_k}\n")
                        f.write(f"q = {q}\n")
                        f.write(f"q digits: {len(str(q))}\n")
                        f.write(f"q mod 4 = {q % 4}\n")
                        f.write(f"cofactor = {cofactor}\n")
                        f.write(f"cofactor digits: {len(str(cofactor))}\n")
                        f.write(f"cofactor mod 4 = {cofactor % 4}\n")
                        f.write(f"is_prime(cofactor): {is_prime(cofactor)}\n")
                        f.write(f"===\n")
                    print(f"\n!!! FACTOR FOUND by W{worker_id} !!! k={actual_k}, q={q}", flush=True)
                    print(f"q mod 4 = {q % 4}, cofactor mod 4 = {cofactor % 4}", flush=True)
                    print(f"is_prime(cofactor): {is_prime(cofactor)}", flush=True)
                    return
        
        now = time.time()
        if now - last_save > 30:
            with open(worker_progress_file, 'w') as f:
                json.dump({
                    'worker_id': worker_id,
                    'last_k': k,
                    'tested': local_tested,
                    'primes': local_primes,
                    'factors': local_factors,
                    'elapsed': now - t_start,
                }, f, indent=2)
            last_save = now
        
        if now - last_log > 15:
            elapsed = now - t_start
            worker_processed = k - k_start
            worker_rate = worker_processed / elapsed if elapsed > 0 else 0
            print(f"[W{worker_id}] k={k:,}, tested={local_tested:,}, primes={local_primes:,}, factors={local_factors}, rate={worker_rate:.0f} k/s, elapsed={elapsed:.0f}s", flush=True)
            last_log = now
    
    with open(worker_progress_file, 'w') as f:
        json.dump({
            'worker_id': worker_id,
            'last_k': k,
            'tested': local_tested,
            'primes': local_primes,
            'factors': local_factors,
            'elapsed': time.time() - t_start,
            'done': True,
        }, f, indent=2)
    print(f"[W{worker_id}] DONE at k={k:,}", flush=True)

def main():
    log_msg("=" * 70)
    log_msg(f"  Smart Sieve for C284 = M({P}) / (87-digit cofactor)")
    log_msg("=" * 70)
    
    # Verify C284
    log_msg(f"C284 digits: {len(str(C284))}")
    log_msg(f"C284 mod 4 = {C284 % 4}")
    log_msg(f"C284 mod 12 = {C284 % 12}")
    log_msg(f"C284 mod 24 = {C284 % 24}")
    log_msg(f"")
    log_msg(f"Structure: q = {TWO_P}*k + 1 = 2458*k + 1")
    log_msg(f"q mod 4 = (2k+1) mod 4 (k even → q≡1, k odd → q≡3)")
    log_msg(f"Since C284 ≡ 3 (mod 4), factors come in (1 mod 4, 3 mod 4) pairs")
    log_msg(f"")
    
    NUM_WORKERS = 2
    K_START = 1
    K_END = 10_000_000_000  # 10 billion — should be plenty for C284
    
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
    
    for i in range(NUM_WORKERS):
        wp_file = BASE_DIR / f'c284_w{i}_progress.json'
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
            log_msg("!!! FACTOR FOUND !!! Stopping...")
            for p in workers:
                if p.is_alive():
                    p.terminate()
            break
        
        total_k_processed = 0
        total_tested = 0
        total_primes = 0
        for i in range(NUM_WORKERS):
            wp_file = BASE_DIR / f'c284_w{i}_progress.json'
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
    
    if RESULTS_FILE.exists() and 'FACTOR FOUND' in RESULTS_FILE.read_text():
        log_msg("!!! FACTOR FOUND !!!")
        log_msg(RESULTS_FILE.read_text())
    else:
        log_msg("No factor found in this range.")

if __name__ == '__main__':
    main()
