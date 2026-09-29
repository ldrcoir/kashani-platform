#!/usr/bin/env python3
"""Quick test: run the multi-threaded sieve for 30 seconds to verify it works."""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, powmod
import time
import json
import multiprocessing as mp
from pathlib import Path

P = 1237
TWO_P = 2474
M = mpz(2)**P - 1
P70 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
C303 = M // P70

def generate_sieve_rules(bound=1000):
    sieve = bytearray([1]) * (bound + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(bound**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    primes = [i for i in range(2, bound + 1) if sieve[i]]
    rules = []
    for r in primes:
        if r == 2 or r == 1237: continue
        inv_2474 = pow(TWO_P, -1, r)
        blocked_residue = (-inv_2474) % r
        rules.append((r, blocked_residue))
    return rules

RULES = generate_sieve_rules(1000)
print(f"Generated {len(RULES)} rules")

def check_k_range(args):
    worker_id, k_start, k_end, progress_dict, stop_event = args
    local_tested = 0
    local_skipped = 0
    rules = RULES
    last_print = time.time()
    
    k = k_start
    while k < k_end and not stop_event.is_set():
        passes = True
        for r, blocked in rules:
            if k % r == blocked:
                passes = False
                break
        if not passes:
            local_skipped += 1
            k += 1
            continue
        local_tested += 1
        q = TWO_P * k + 1
        if not is_prime(q):
            k += 1
            continue
        if powmod(2, P, q) == 1:
            if C303 % q == 0:
                print(f"\n!!! FACTOR FOUND by W{worker_id} at k={k}: q={q}", flush=True)
                stop_event.set()
                return (k, local_tested, local_skipped, [(k, q)])
        if (k - k_start) % 50_000 == 0 and k > k_start:
            progress_dict[worker_id] = (k, local_tested, local_skipped)
            now = time.time()
            if now - last_print > 5:
                elapsed = now - last_print
                worker_processed = (k - k_start)
                worker_rate = worker_processed / elapsed
                print(f"[W{worker_id}] k={k:,}, tested={local_tested:,}, skip={local_skipped:,}, rate={worker_rate:.0f} k/s", flush=True)
                last_print = now
        k += 1
    progress_dict[worker_id] = (k, local_tested, local_skipped)
    print(f"[W{worker_id}] DONE at k={k:,}, tested={local_tested:,}, skip={local_skipped:,}", flush=True)
    return (k, local_tested, local_skipped, [])

# Run for 30 seconds
NUM_WORKERS = 8
K_START = 15_000_000
K_END = 100_000_000_000
total_k = K_END - K_START
chunk_size = total_k // NUM_WORKERS

manager = mp.Manager()
progress_dict = manager.dict()
stop_event = manager.Event()
for i in range(NUM_WORKERS):
    progress_dict[i] = (K_START + i * chunk_size, 0, 0)

# Start workers
ctx = mp.get_context('fork')
workers = []
worker_args = []
for i in range(NUM_WORKERS):
    w_start = K_START + i * chunk_size
    w_end = K_END if i == NUM_WORKERS - 1 else w_start + chunk_size
    args = (i, w_start, w_end, progress_dict, stop_event)
    worker_args.append(args)
    p = ctx.Process(target=check_k_range, args=(args,))
    p.start()
    workers.append(p)
    print(f"  W{i}: k=[{w_start:,}, {w_end:,})")

print("Workers started. Running for 30 seconds...")
print("=" * 70)

t_start = time.time()
last_log = t_start
while time.time() - t_start < 30 and any(p.is_alive() for p in workers):
    time.sleep(5)
    total_tested = sum(progress_dict.get(i, (0, 0, 0))[1] for i in range(NUM_WORKERS))
    total_skipped = sum(progress_dict.get(i, (0, 0, 0))[2] for i in range(NUM_WORKERS))
    elapsed = time.time() - t_start
    rate = (total_tested + total_skipped) / elapsed if elapsed > 0 else 0
    print(f"[{time.strftime('%H:%M:%S')}] elapsed={elapsed:.0f}s, tested={total_tested:,}, skipped={total_skipped:,}, rate={rate:.0f} k/s")

# Stop and wait
print("\nStopping workers...")
stop_event.set()
for p in workers:
    p.join(timeout=5)

# Final stats
total_tested = sum(progress_dict.get(i, (0, 0, 0))[1] for i in range(NUM_WORKERS))
total_skipped = sum(progress_dict.get(i, (0, 0, 0))[2] for i in range(NUM_WORKERS))
elapsed = time.time() - t_start
print(f"\nFinal: elapsed={elapsed:.1f}s, tested={total_tested:,}, skipped={total_skipped:,}")
print(f"Rate: {(total_tested + total_skipped) / elapsed:.0f} k/s")
print(f"Test rate: {total_tested / elapsed:.0f} tests/s")
print(f"Estimated time to reach k=100B: {(100_000_000_000 - 15_000_000) / ((total_tested + total_skipped) / elapsed):.0f}s = {(100_000_000_000 - 15_000_000) / ((total_tested + total_skipped) / elapsed) / 3600:.1f} hours")
