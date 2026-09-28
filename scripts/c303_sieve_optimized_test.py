#!/usr/bin/env python3
"""
Optimized smart sieve for C303.

Key optimizations:
1. Use a larger sieve (up to 100,000) to filter more k values
2. Use gmpy2.is_prime (which is Miller-Rabin) — already fast
3. Use pow(2, 1237, q) == 1 as the final test (fast, ~11 modular squarings)

Test results show ~29k k/s with sieve(1000).
With sieve(10000), should be ~50-100% faster.
With sieve(100000), even more.

Let's also try: instead of iterating k and computing q, precompute q and use gmpy2.next_prime(q) 
to jump to the next prime candidate.
"""

import sys
sys.set_int_max_str_digits(1000000)
import gmpy2
from gmpy2 import mpz, is_prime, powmod, next_prime
import time
import json
import multiprocessing as mp
from pathlib import Path

P = 1237
TWO_P = 2474
M = mpz(2)**P - 1
P70 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
C303 = M // P70

def generate_sieve_rules(bound=10000):
    """Generate sieve rules for primes up to bound."""
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

RULES = generate_sieve_rules(10000)
print(f"Generated {len(RULES)} sieve rules")

def check_k_range(args):
    worker_id, k_start, k_end, progress_dict, stop_event = args
    local_tested = 0
    local_skipped = 0
    local_primes = 0
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
        local_primes += 1
        if powmod(2, P, q) == 1:
            if C303 % q == 0:
                print(f"\n!!! FACTOR FOUND by W{worker_id} at k={k}: q={q}", flush=True)
                stop_event.set()
                return (k, local_tested, local_skipped, local_primes, [(k, q)])
        if (k - k_start) % 50_000 == 0 and k > k_start:
            progress_dict[worker_id] = (k, local_tested, local_skipped, local_primes)
            now = time.time()
            if now - last_print > 5:
                elapsed = now - last_print
                worker_processed = (k - k_start)
                worker_rate = worker_processed / elapsed
                print(f"[W{worker_id}] k={k:,}, tested={local_tested:,}, skip={local_skipped:,}, primes={local_primes:,}, rate={worker_rate:.0f} k/s", flush=True)
                last_print = now
        k += 1
    progress_dict[worker_id] = (k, local_tested, local_skipped, local_primes)
    print(f"[W{worker_id}] DONE at k={k:,}, tested={local_tested:,}, skip={local_skipped:,}, primes={local_primes:,}", flush=True)
    return (k, local_tested, local_skipped, local_primes, [])

# Run for 60 seconds
NUM_WORKERS = 8
K_START = 15_000_000
K_END = 100_000_000_000
total_k = K_END - K_START
chunk_size = total_k // NUM_WORKERS

manager = mp.Manager()
progress_dict = manager.dict()
stop_event = manager.Event()
for i in range(NUM_WORKERS):
    progress_dict[i] = (K_START + i * chunk_size, 0, 0, 0)

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

print("Workers started. Running for 60 seconds...")
print("=" * 70)

t_start = time.time()
while time.time() - t_start < 60 and any(p.is_alive() for p in workers):
    time.sleep(10)
    total_tested = sum(progress_dict.get(i, (0, 0, 0, 0))[1] for i in range(NUM_WORKERS))
    total_skipped = sum(progress_dict.get(i, (0, 0, 0, 0))[2] for i in range(NUM_WORKERS))
    total_primes = sum(progress_dict.get(i, (0, 0, 0, 0))[3] for i in range(NUM_WORKERS))
    elapsed = time.time() - t_start
    rate = (total_tested + total_skipped) / elapsed if elapsed > 0 else 0
    print(f"[{time.strftime('%H:%M:%S')}] elapsed={elapsed:.0f}s, tested={total_tested:,}, skipped={total_skipped:,}, primes={total_primes:,}, rate={rate:.0f} k/s")

stop_event.set()
for p in workers:
    p.join(timeout=10)

total_tested = sum(progress_dict.get(i, (0, 0, 0, 0))[1] for i in range(NUM_WORKERS))
total_skipped = sum(progress_dict.get(i, (0, 0, 0, 0))[2] for i in range(NUM_WORKERS))
total_primes = sum(progress_dict.get(i, (0, 0, 0, 0))[3] for i in range(NUM_WORKERS))
elapsed = time.time() - t_start
print(f"\nFinal: elapsed={elapsed:.1f}s, tested={total_tested:,}, skipped={total_skipped:,}, primes={total_primes:,}")
print(f"Rate: {(total_tested + total_skipped) / elapsed:.0f} k/s")
print(f"Estimated time to reach k=100B: {(100_000_000_000 - 15_000_000) / ((total_tested + total_skipped) / elapsed):.0f}s = {(100_000_000_000 - 15_000_000) / ((total_tested + total_skipped) / elapsed) / 3600:.1f} hours")
