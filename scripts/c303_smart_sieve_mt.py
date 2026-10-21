#!/usr/bin/env python3
"""
Smart sieve for finding smallest prime factor of C303 = M(1237)/P70.

Multi-threaded version with checkpointing.

Strategy:
- Each prime factor q of C303 satisfies q = 2474*k + 1 (Mersenne structure)
- Use modular sieve: for small primes r, find k residues that make q composite, skip them
- For each surviving k: check if q=2474k+1 is prime, then check if q | M(1237) via pow(2,1237,q)==1
- If q | M(1237) and q < P70, then q | C303 (since q != P70)
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, powmod
import math
import time
import json
import os
import multiprocessing as mp
from pathlib import Path

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
PROGRESS_FILE = BASE_DIR / 'c303_sieve_progress.txt'

def generate_sieve_rules(bound=1000):
    """Generate sieve rules for small primes up to bound."""
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

# Global rules (set in main, shared via inheritance after fork)
RULES = None

def check_k_range(args):
    """Worker: check all k in [k_start, k_end)."""
    worker_id, k_start, k_end, progress_dict, stop_event, start_time = args
    
    # Local counters
    local_tested = 0
    local_skipped = 0
    local_found = []
    last_print = time.time()
    
    rules = RULES  # use global
    
    k = k_start
    while k < k_end and not stop_event.is_set():
        # Fast sieve check
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
        
        # Primality test
        if not is_prime(q):
            k += 1
            continue
        
        # Check if q | M(1237) via Fermat-like test
        # pow(2, 1237, q) == 1 means q | M(1237)
        if powmod(2, P, q) == 1:
            # q | M(1237). Verify q | C303 (q != P70 trivially for our range)
            if C303 % q == 0:
                local_found.append((k, q))
                # Save to results file
                with open(RESULTS_FILE, 'a') as f:
                    f.write(f"=== FACTOR FOUND ===\n")
                    f.write(f"Worker: {worker_id}\n")
                    f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"k = {k}\n")
                    f.write(f"q = {q}\n")
                    f.write(f"q digits: {len(str(q))}\n")
                    cofactor = int(C303) // q
                    f.write(f"cofactor digits: {len(str(cofactor))}\n")
                    f.write(f"is_prime(cofactor): {is_prime(cofactor)}\n")
                    f.write(f"===\n")
                
                # Signal stop
                stop_event.set()
                
                # Print to stdout
                msg = f"\n!!! FACTOR FOUND by worker {worker_id} !!!\n"
                msg += f"k = {k}\n"
                msg += f"q = {q}\n"
                msg += f"q digits: {len(str(q))}\n"
                cofactor = int(C303) // q
                msg += f"cofactor = {str(cofactor)[:60]}... ({len(str(cofactor))} digits)\n"
                msg += f"is_prime(cofactor): {is_prime(cofactor)}\n"
                print(msg, flush=True)
                
                return (k, local_tested, local_skipped, local_found)
            else:
                # q | M(1237) but q does NOT divide C303 — means q | P70
                # But q < P70 in our range, so this shouldn't happen
                print(f"[W{worker_id}] Note: q = {q} divides M(1237) but not C303", flush=True)
        
        # Progress update every 100,000 k
        if (k - k_start) % 100_000 == 0 and k > k_start:
            progress_dict[worker_id] = (k, local_tested, local_skipped, len(local_found))
            now = time.time()
            if now - last_print > 15:
                elapsed = now - start_time
                worker_processed = k - k_start
                worker_rate = worker_processed / elapsed if elapsed > 0 else 0
                print(f"[W{worker_id}] k={k:,}, tested={local_tested:,}, skipped={local_skipped:,}, found={len(local_found)}, rate={worker_rate:.0f} k/s, elapsed={elapsed:.0f}s", flush=True)
                last_print = now
        
        k += 1
    
    # Final progress update
    progress_dict[worker_id] = (k, local_tested, local_skipped, len(local_found))
    print(f"[W{worker_id}] DONE at k={k:,}, tested={local_tested:,}, skipped={local_skipped:,}, found={len(local_found)}", flush=True)
    return (k, local_tested, local_skipped, local_found)

def main():
    global RULES
    
    print("=" * 70)
    print("  Smart Sieve for C303 = M(1237) / P70")
    print("=" * 70)
    print()
    print(f"C303 = (2^1237 - 1) / P70")
    print(f"C303 digits: {len(str(C303))}")
    print(f"P70 digits: {len(str(P70))}")
    print()
    
    # Parameters
    K_START_DEFAULT = 15_000_000  # 15 million
    K_END = 100_000_000_000  # 100 billion
    NUM_WORKERS = 8
    CHECKPOINT_EVERY_SEC = 60  # save checkpoint every 60s
    
    # Load checkpoint
    start_k = K_START_DEFAULT
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE) as f:
                cp = json.load(f)
            saved_k = cp.get('last_k_processed', 0)
            if saved_k > start_k:
                start_k = saved_k + 1
                print(f"Checkpoint loaded: resuming from k = {start_k:,}")
            else:
                print(f"Checkpoint exists but k={saved_k} < start, beginning fresh")
        except Exception as e:
            print(f"Checkpoint load failed: {e}")
    
    print(f"Range: k from {start_k:,} to {K_END:,}")
    print(f"Workers: {NUM_WORKERS}")
    print(f"Checkpoint every: {CHECKPOINT_EVERY_SEC}s")
    print()
    
    # Generate sieve rules
    print("Generating sieve rules for primes up to 1000...")
    RULES = generate_sieve_rules(bound=1000)
    print(f"Generated {len(RULES)} rules")
    
    # Theoretical skip rate
    skip_fraction = 1.0
    for r, _ in RULES:
        skip_fraction *= (1 - 1/r)
    print(f"Theoretical pass rate: {skip_fraction*100:.2f}%")
    print(f"Theoretical skip rate: {(1-skip_fraction)*100:.2f}%")
    print()
    
    # Setup multiprocessing
    manager = mp.Manager()
    progress_dict = manager.dict()
    stop_event = manager.Event()
    
    # Divide work
    total_k = K_END - start_k
    chunk_size = total_k // NUM_WORKERS
    
    # Initialize progress dict
    for i in range(NUM_WORKERS):
        progress_dict[i] = (start_k, 0, 0, 0)
    
    # Build worker args
    worker_args = []
    for i in range(NUM_WORKERS):
        worker_k_start = start_k + i * chunk_size
        worker_k_end = K_END if i == NUM_WORKERS - 1 else worker_k_start + chunk_size
        worker_args.append((i, worker_k_start, worker_k_end, progress_dict, stop_event, time.time()))
        print(f"  Worker {i}: k = [{worker_k_start:,}, {worker_k_end:,})")
    
    print()
    print("Workers starting...")
    print("=" * 70)
    
    # Start workers using spawn (safer than fork for this setup)
    ctx = mp.get_context('fork')  # fork is faster on Linux
    workers = []
    for args in worker_args:
        p = ctx.Process(target=check_k_range, args=(args,))
        p.start()
        workers.append(p)
    
    # Monitor
    last_checkpoint_time = time.time()
    t_start = time.time()
    
    try:
        while any(p.is_alive() for p in workers):
            time.sleep(5)
            
            # Aggregate progress
            total_tested = 0
            total_skipped = 0
            total_found = 0
            max_k = 0
            for i in range(NUM_WORKERS):
                if i in progress_dict:
                    k_val, tested, skipped, found = progress_dict[i]
                    total_tested += tested
                    total_skipped += skipped
                    total_found += found
                    if k_val > max_k:
                        max_k = k_val
            
            elapsed = time.time() - t_start
            total_processed = total_tested + total_skipped
            rate = total_processed / elapsed if elapsed > 0 else 0
            
            print(f"[{time.strftime('%H:%M:%S')}] elapsed={elapsed:.0f}s, processed={total_processed:,}, tested={total_tested:,}, skipped={total_skipped:,}, found={total_found}, rate={rate:.0f} k/s, max_k={max_k:,}")
            
            # Save checkpoint
            if time.time() - last_checkpoint_time > CHECKPOINT_EVERY_SEC:
                with open(CHECKPOINT_FILE, 'w') as f:
                    json.dump({
                        'last_k_processed': max_k,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'total_tested': total_tested,
                        'total_skipped': total_skipped,
                        'elapsed_seconds': elapsed,
                    }, f, indent=2)
                last_checkpoint_time = time.time()
    
    except KeyboardInterrupt:
        print("\nInterrupted by user. Stopping workers...")
        stop_event.set()
        for p in workers:
            p.join(timeout=10)
        # Save final state
        max_k = max((progress_dict.get(i, (0,))[0] for i in range(NUM_WORKERS)), default=0)
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({
                'last_k_processed': max_k,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'interrupted': True,
            }, f, indent=2)
        print(f"Final checkpoint saved: k = {max_k:,}")
        return
    
    # Wait for completion
    for p in workers:
        p.join()
    
    print()
    print("=" * 70)
    print("All workers finished")
    print("=" * 70)
    
    # Final stats
    total_tested = sum(progress_dict.get(i, (0, 0, 0, 0))[1] for i in range(NUM_WORKERS))
    total_skipped = sum(progress_dict.get(i, (0, 0, 0, 0))[2] for i in range(NUM_WORKERS))
    total_found = sum(progress_dict.get(i, (0, 0, 0, 0))[3] for i in range(NUM_WORKERS))
    elapsed = time.time() - t_start
    
    print(f"Total elapsed: {elapsed:.0f}s ({elapsed/3600:.2f} hours)")
    print(f"Total tested: {total_tested:,}")
    print(f"Total skipped: {total_skipped:,}")
    print(f"Total processed: {total_tested + total_skipped:,}")
    print(f"Total factors found: {total_found}")
    print()
    
    if total_found > 0:
        print("!!! FACTOR FOUND !!! Check results.txt")
        if RESULTS_FILE.exists():
            with open(RESULTS_FILE) as f:
                print(f.read())
    else:
        print("No factor found in this range.")
        max_k = max((progress_dict.get(i, (0,))[0] for i in range(NUM_WORKERS)), default=0)
        print(f"Last k checked: {max_k:,}")
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({
                'last_k_processed': max_k,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_tested': total_tested,
                'total_skipped': total_skipped,
                'final': True,
                'no_factor_found': True,
            }, f, indent=2)

if __name__ == '__main__':
    main()
