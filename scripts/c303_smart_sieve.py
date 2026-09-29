#!/usr/bin/env python3
"""
Smart sieve for finding smallest prime factor of C303 = M(1237)/P70.

Strategy:
- Each prime factor q of C303 must satisfy q = 2*1237*k + 1 for some k >= 1
- Use modular sieve: for each small prime r (≠ 2, 1237), if q = 2*1237*k + 1 ≡ 0 (mod r),
  then k ≡ -(2*1237)^(-1) (mod r). Skip such k values.
- For each remaining candidate q, check primality, then check if q | C303 via:
  pow(2, 1237, q) == 1  (fast — uses the Mersenne structure)
- Multi-threaded with checkpointing.

Speed comparison:
- pow(2, 1237, q) is much faster than C303 % q == 0 (especially for large q)
- Wait, actually: pow(2, 1237, q) requires raising 2 to power 1237 mod q (~11 squarings)
- C303 % q requires division of a 303-digit number by q
- For q ~ 10^15 (k ~ 10^12), C303 % q takes time proportional to log(C303) * log(q) = 303 * 50 = ~15000 digit operations
- pow(2, 1237, q) takes ~11 squarings of numbers up to q^2 = ~30 digits = ~330 digit operations
- So pow(2, 1237, q) is about 50x faster than C303 % q == 0

But: pow(2, 1237, q) == 1 is necessary but NOT sufficient for q | C303:
- pow(2, 1237, q) == 1 means q | M(1237)
- q | M(1237) means q is a factor of M(1237)
- But M(1237) = P70 * C303, so q could be a factor of P70 OR C303
- Since P70 is prime and small (70-digit), we can verify q != P70 first
- For q < P70: q != P70 trivially
- So: if q < P70 and pow(2, 1237, q) == 1, then q is a NEW factor of M(1237)
  → q | C303 (since q != P70)
- For q == P70: skip (it's the known factor)
- For q > P70: rare case, but possible if C303 has factor q > P70. Use direct C303 % q == 0.

For our search (k from 15M to 100B), q = 2*1237*k + 1 ranges from ~3.7e10 to ~2.5e14,
all much less than P70 (~10^69). So we can use pow(2, 1237, q) == 1.

But wait: pow(2, 1237, q) == 1 only checks q | M(1237), not q | C303.
If q | M(1237) and q != P70 and q < P70, then q | C303 (since C303 = M(1237)/P70).
For q > P70: would need separate check.

Actually a cleaner check: C303 % q == 0 directly, but using pow(2, 1237, q) == 1 first 
as a fast filter (most random q won't satisfy this).

Let's use this two-stage approach:
1. Filter: pow(2, 1237, q) == 1 (fast, ~50x faster)
2. Verify: q < P70 → q | C303 (since q != P70)
3. If q >= P70: check C303 % q == 0 directly (slow but rare)

For our search range (k up to 10^11), q = 2*1237*10^11 + 1 ≈ 2.5×10^14, way less than P70 (~10^69).
So we can use pow(2, 1237, q) == 1 alone!
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
TWO_P = 2 * P  # 2474
M = mpz(2)**P - 1
P70 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
C303 = M // P70

# Files
BASE_DIR = Path('/home/z/my-project/download')
CHECKPOINT_FILE = BASE_DIR / 'c303_sieve_checkpoint.json'
RESULTS_FILE = BASE_DIR / 'c303_sieve_results.txt'
PROGRESS_FILE = BASE_DIR / 'c303_sieve_progress.txt'

def generate_sieve_rules(bound=1000):
    """Generate sieve rules for small primes r (≠ 2, 1237) up to bound."""
    # Sieve of Eratosthenes
    sieve = bytearray([1]) * (bound + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(bound**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    primes = [i for i in range(2, bound + 1) if sieve[i]]
    
    # For each prime r != 2 and != 1237:
    # If q = 2474*k + 1 ≡ 0 mod r → k ≡ -(2474)^(-1) mod r → skip k ≡ this residue mod r
    rules = []
    for r in primes:
        if r == 2 or r == 1237: continue
        inv_2474 = pow(TWO_P, -1, r)
        blocked_residue = (-inv_2474) % r
        rules.append((r, blocked_residue))
    return rules

def k_passes_sieve(k, rules):
    """Returns True if k is NOT eliminated by sieve rules (i.e., passes)."""
    for r, blocked in rules:
        if k % r == blocked:
            return False
    return True

def check_k(k_start, k_end, rules, worker_id, progress_dict, stop_event):
    """Worker: check all k in [k_start, k_end) using sieve rules."""
    local_count = 0
    local_skipped = 0
    local_tested = 0
    last_print = time.time()
    
    # Pre-compute: for each rule (r, blocked), the first k in our range that violates.
    # Then iterate, skipping values.
    
    # Simple approach: iterate k from k_start to k_end, check sieve.
    # For performance, we can use CRT-based skipping but that's complex.
    # Let's first try simple iteration with fast sieve check.
    
    for k in range(k_start, k_end):
        if stop_event.is_set():
            break
        
        # Fast sieve check
        passes = True
        for r, blocked in rules:
            if k % r == blocked:
                passes = False
                break
        
        if not passes:
            local_skipped += 1
            continue
        
        local_tested += 1
        
        # Compute q = 2474*k + 1
        q = TWO_P * k + 1
        
        # Check primality (fast)
        if not is_prime(q):
            continue
        
        # Now: q is prime. Check if q | M(1237) via pow(2, 1237, q) == 1
        # This is fast since q is small
        if powmod(2, P, q) == 1:
            # q | M(1237). Since q < P70 (because q ≈ 2474*k ≤ 2474*10^11 ≈ 2.5*10^14, and P70 ≈ 10^69),
            # q != P70, so q | C303.
            # But verify with C303 % q == 0 just to be safe
            if C303 % q == 0:
                # FACTOR FOUND!
                # Write to results file
                with open(RESULTS_FILE, 'a') as f:
                    f.write(f"FACTOR FOUND!\n")
                    f.write(f"k = {k}\n")
                    f.write(f"q = {q}\n")
                    f.write(f"q digits: {len(str(q))}\n")
                    f.write(f"is_prime: True\n")
                    cofactor = C303 // q
                    f.write(f"cofactor digits: {len(str(cofactor))}\n")
                    f.write(f"is_prime(cofactor): {is_prime(cofactor)}\n")
                    f.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"---\n")
                
                # Signal other workers to stop
                stop_event.set()
                
                print(f"\n!!! FACTOR FOUND by worker {worker_id} !!!")
                print(f"k = {k}")
                print(f"q = {q}")
                print(f"q digits: {len(str(q))}")
                print(f"cofactor = {str(cofactor)[:60]}... ({len(str(cofactor))} digits)")
                print(f"is_prime(cofactor): {is_prime(cofactor)}")
                return
        
        local_count += 1
        
        # Update progress every 100,000 k
        if (k - k_start) % 100_000 == 0 and k > k_start:
            progress_dict[worker_id] = (k, local_tested, local_skipped, local_count)
            now = time.time()
            if now - last_print > 10:
                elapsed = now - last_print
                print(f"[W{worker_id}] k={k:>15,}, tested={local_tested:,}, skipped={local_skipped:,}, found={local_count} (last 10s: {(k - k_start) - 0} k processed)")
                last_print = now
    
    # Final progress update
    progress_dict[worker_id] = (k_end, local_tested, local_skipped, local_count)
    print(f"[W{worker_id}] DONE: k reached {k_end:,}, tested={local_tested:,}, skipped={local_skipped:,}, found={local_count}")

def main():
    print("=" * 70)
    print("  Smart Sieve for C303 = M(1237) / P70")
    print("=" * 70)
    print()
    print(f"C303 = (2^1237 - 1) / P70")
    print(f"C303 digits: {len(str(C303))}")
    print(f"P70 digits: {len(str(P70))}")
    print()
    
    # Parameters
    K_START = 15_000_000  # 15 million
    K_END = 100_000_000_000  # 100 billion
    NUM_WORKERS = 8
    CHECKPOINT_EVERY = 1_000_000  # every 1M k
    
    # Load checkpoint if exists
    start_k = K_START
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE) as f:
                cp = json.load(f)
            start_k = cp.get('last_k_processed', K_START)
            print(f"Checkpoint loaded: starting from k = {start_k:,}")
            # Move past checkpoint
            start_k += 1
        except Exception as e:
            print(f"Checkpoint load failed: {e}")
    
    print(f"Range: k from {start_k:,} to {K_END:,}")
    print(f"Workers: {NUM_WORKERS}")
    print(f"Checkpoint every: {CHECKPOINT_EVERY:,} k")
    print()
    
    # Generate sieve rules
    print("Generating sieve rules for primes up to 1000...")
    rules = generate_sieve_rules(bound=1000)
    print(f"Generated {len(rules)} rules (one per small prime r)")
    print()
    
    # Show: with these rules, what fraction of k do we skip?
    # Rough estimate: product over r of (1 - 1/r) ≈ 1/log(1000) ≈ 0.14
    # So ~86% of k are skipped
    # Exact computation:
    skip_fraction = 1.0
    for r, _ in rules:
        skip_fraction *= (1 - 1/r)
    print(f"Theoretical pass rate: {skip_fraction*100:.2f}%")
    print(f"Theoretical skip rate: {(1-skip_fraction)*100:.2f}%")
    print()
    
    # Setup multiprocessing
    manager = mp.Manager()
    progress_dict = manager.dict()
    stop_event = manager.Event()
    
    # Initialize progress dict
    for i in range(NUM_WORKERS):
        progress_dict[i] = (start_k, 0, 0, 0)
    
    # Divide work
    total_k = K_END - start_k
    chunk_size = total_k // NUM_WORKERS
    
    print(f"Each worker handles ~{chunk_size:,} k values")
    print()
    
    # Start workers
    workers = []
    for i in range(NUM_WORKERS):
        worker_k_start = start_k + i * chunk_size
        worker_k_end = K_END if i == NUM_WORKERS - 1 else worker_k_start + chunk_size
        p = mp.Process(target=check_k, args=(worker_k_start, worker_k_end, rules, i, progress_dict, stop_event))
        p.start()
        workers.append(p)
        print(f"  Worker {i}: k = [{worker_k_start:,}, {worker_k_end:,})")
    
    print()
    print("Workers started. Monitoring progress...")
    print("=" * 70)
    
    # Monitor
    last_checkpoint_time = time.time()
    t_start = time.time()
    
    try:
        while any(p.is_alive() for p in workers):
            time.sleep(10)
            
            # Aggregate progress
            total_tested = sum(progress_dict.get(i, (0, 0, 0, 0))[1] for i in range(NUM_WORKERS))
            total_skipped = sum(progress_dict.get(i, (0, 0, 0, 0))[2] for i in range(NUM_WORKERS))
            total_processed = sum(progress_dict.get(i, (0, 0, 0, 0))[0] - start_k - i * (total_k // NUM_WORKERS) 
                                 for i in range(NUM_WORKERS))
            
            elapsed = time.time() - t_start
            rate = total_processed / elapsed if elapsed > 0 else 0
            
            print(f"\n[{time.strftime('%H:%M:%S')}] Elapsed: {elapsed:.0f}s, Processed: {total_processed:,} k, Rate: {rate:.0f} k/s")
            print(f"  Tested: {total_tested:,}, Skipped: {total_skipped:,}, Found: 0")
            print(f"  ETA to {K_END:,}: {(K_END - start_k - total_processed) / rate if rate > 0 else 'inf':.0f}s" if rate > 0 else "")
            
            # Checkpoint every minute
            if time.time() - last_checkpoint_time > 60:
                # Find max k processed
                max_k = max(progress_dict.get(i, (0, 0, 0, 0))[0] for i in range(NUM_WORKERS))
                with open(CHECKPOINT_FILE, 'w') as f:
                    json.dump({
                        'last_k_processed': max_k,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'total_tested': total_tested,
                        'total_skipped': total_skipped,
                    }, f, indent=2)
                last_checkpoint_time = time.time()
                print(f"  Checkpoint saved: k = {max_k:,}")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user. Saving checkpoint...")
        stop_event.set()
        for p in workers:
            p.join(timeout=5)
        max_k = max(progress_dict.get(i, (0, 0, 0, 0))[0] for i in range(NUM_WORKERS))
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({
                'last_k_processed': max_k,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }, f, indent=2)
        print(f"Checkpoint saved: k = {max_k:,}")
        return
    
    # Wait for all to finish
    for p in workers:
        p.join()
    
    print()
    print("=" * 70)
    print("All workers finished")
    print("=" * 70)
    
    # Final stats
    total_tested = sum(progress_dict.get(i, (0, 0, 0, 0))[1] for i in range(NUM_WORKERS))
    total_skipped = sum(progress_dict.get(i, (0, 0, 0, 0))[2] for i in range(NUM_WORKERS))
    elapsed = time.time() - t_start
    
    print(f"Total elapsed: {elapsed:.0f}s ({elapsed/3600:.2f} hours)")
    print(f"Total tested: {total_tested:,}")
    print(f"Total skipped: {total_skipped:,}")
    print(f"Total processed: {total_tested + total_skipped:,}")
    print()
    
    if not stop_event.is_set():
        print("No factor found in this range.")
        print(f"Last k checked: {max(progress_dict.get(i, (0, 0, 0, 0))[0] for i in range(NUM_WORKERS)):,}")
        # Save final checkpoint
        max_k = max(progress_dict.get(i, (0, 0, 0, 0))[0] for i in range(NUM_WORKERS))
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({
                'last_k_processed': max_k,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_tested': total_tested,
                'total_skipped': total_skipped,
                'final': True,
            }, f, indent=2)
        print(f"Final checkpoint saved.")
    else:
        print("Factor was found! Check results.txt")
        with open(RESULTS_FILE) as f:
            print(f.read())

if __name__ == '__main__':
    main()
