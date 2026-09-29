import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, powmod
import time
import json
import pickle
import os
import multiprocessing as mp
from pathlib import Path
import bisect

P = 1237
TWO_P = 2474
M = mpz(2)**P - 1
P70 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
C303 = M // P70

BASE_DIR = Path('/home/z/my-project/download')
GOOD_RESIDUES_FILE = BASE_DIR / 'good_residues.pkl'

WHEEL_PRIMES = [3, 5, 7, 11, 13, 17, 19]
WHEEL_MOD = 1
for p in WHEEL_PRIMES:
    WHEEL_MOD *= p

with open(GOOD_RESIDUES_FILE, 'rb') as f:
    GOOD_RESIDUES = pickle.load(f)

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

def worker_main(args):
    worker_id, k_start, k_end = args
    
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
    last_log = time.time()
    t_start = time.time()
    
    while k < k_end:
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
            if C303 % q == 0:
                print(f"FACTOR! W{worker_id} k={k} q={q}", flush=True)
                return (k, q)
        
        k += STEPS[idx]
        idx = (idx + 1) % N_GOOD
        
        now = time.time()
        if now - last_log > 5:
            elapsed = now - t_start
            rate = (k - k_start) / elapsed if elapsed > 0 else 0
            print(f"[W{worker_id}] k={k:,}, tested={local_tested:,}, primes={local_primes:,}, rate={rate:.0f} k/s, elapsed={elapsed:.0f}s", flush=True)
            last_log = now
    
    print(f"[W{worker_id}] DONE k={k:,} tested={local_tested:,} primes={local_primes:,}", flush=True)

# Test: 1M k, 4 workers
NUM_WORKERS = 4
K_START = 15_000_000
K_END = 15_000_000 + 1_000_000
chunk = (K_END - K_START) // NUM_WORKERS

ctx = mp.get_context('fork')
workers = []
for i in range(NUM_WORKERS):
    w_start = K_START + i * chunk
    w_end = K_END if i == NUM_WORKERS - 1 else w_start + chunk
    p = ctx.Process(target=worker_main, args=((i, w_start, w_end),))
    p.start()
    workers.append(p)
    print(f"Started W{i}: k=[{w_start:,}, {w_end:,}) PID {p.pid}", flush=True)

t0 = time.time()
for p in workers:
    p.join()
elapsed = time.time() - t0
print(f"\n4 workers, 1M k total, elapsed={elapsed:.1f}s, rate={1_000_000/elapsed:.0f} k/s combined")
print(f"Per worker: {1_000_000/elapsed/NUM_WORKERS:.0f} k/s")
print(f"Extrapolated time to k=100B: {(100_000_000_000 - 15_000_000) / (1_000_000/elapsed):.0f}s = {(100_000_000_000 - 15_000_000) / (1_000_000/elapsed) / 3600:.1f} hours")
