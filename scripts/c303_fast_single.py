#!/usr/bin/env python3
"""
Single-threaded fast sieve for C303.

Use next_prime to jump directly between primes — skips most primality tests.
For each prime q in the right range, check:
1. q ≡ 1 (mod 2474)
2. pow(2, 1237, q) == 1
3. q | C303
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, powmod, next_prime
import time
import json
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

# Parameters
K_START_DEFAULT = 15_000_000
K_END = 100_000_000_000  # 100 billion

def main():
    print("=" * 70)
    print("  Fast Single-threaded Sieve for C303 (using next_prime)")
    print("=" * 70)
    print()
    print(f"C303 = (2^1237 - 1) / P70")
    print(f"C303 digits: {len(str(C303))}")
    print(f"P70 digits: {len(str(P70))}")
    print()
    
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
                print(f"Starting fresh from k = {start_k:,}")
        except Exception as e:
            print(f"Checkpoint load failed: {e}")
    else:
        print(f"Starting fresh from k = {start_k:,}")
    
    q_start = TWO_P * start_k + 1
    q_end = TWO_P * K_END + 1
    
    print(f"q range: [{q_start}, {q_end})")
    print(f"q digits: {len(str(q_start))} to {len(str(q_end))}")
    print()
    
    # Iterate from prime to prime
    q = gmpy2.next_prime(q_start - 1)
    q = int(q)
    
    count_primes = 0
    count_mod_2474 = 0
    count_pow = 0
    last_checkpoint_time = time.time()
    t_start = time.time()
    last_k_logged = start_k
    
    print(f"Starting from q = {q}")
    print()
    
    try:
        while q < q_end:
            count_primes += 1
            
            # Check q ≡ 1 mod 2474 (very fast)
            if (q - 1) % TWO_P == 0:
                k = (q - 1) // TWO_P
                count_mod_2474 += 1
                
                # Check pow(2, 1237, q) == 1
                if powmod(2, P, q) == 1:
                    count_pow += 1
                    # Verify q | C303
                    if C303 % q == 0:
                        # FACTOR FOUND!
                        cofactor = int(C303) // q
                        with open(RESULTS_FILE, 'a') as f:
                            f.write(f"=== FACTOR FOUND ===\n")
                            f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write(f"k = {k}\n")
                            f.write(f"q = {q}\n")
                            f.write(f"q digits: {len(str(q))}\n")
                            f.write(f"cofactor digits: {len(str(cofactor))}\n")
                            f.write(f"is_prime(cofactor): {is_prime(cofactor)}\n")
                            f.write(f"===\n")
                        
                        print(f"\n!!! FACTOR FOUND !!!")
                        print(f"k = {k}")
                        print(f"q = {q}")
                        print(f"q digits: {len(str(q))}")
                        print(f"cofactor = {str(cofactor)[:60]}... ({len(str(cofactor))} digits)")
                        print(f"is_prime(cofactor): {is_prime(cofactor)}")
                        return
            
            # Progress update
            if count_primes % 100_000 == 0:
                elapsed = time.time() - t_start
                rate = count_primes / elapsed if elapsed > 0 else 0
                # Estimate k from q
                current_k = (q - 1) // TWO_P
                # How many k "passed" (whether good residue or not)
                k_progress = current_k - start_k
                print(f"[{time.strftime('%H:%M:%S')}] elapsed={elapsed:.0f}s, primes_checked={count_primes:,}, q={q:,} (k={current_k:,}), rate={rate:.0f} primes/s, k_progress={k_progress:,}")
                
                # Save checkpoint
                if time.time() - last_checkpoint_time > 30:
                    with open(CHECKPOINT_FILE, 'w') as f:
                        json.dump({
                            'last_k_processed': current_k,
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'primes_checked': count_primes,
                            'mod_2474_count': count_mod_2474,
                            'pow_count': count_pow,
                            'elapsed_seconds': elapsed,
                        }, f, indent=2)
                    last_checkpoint_time = time.time()
            
            # Jump to next prime
            q = int(gmpy2.next_prime(q))
    
    except KeyboardInterrupt:
        print("\nInterrupted. Saving checkpoint...")
        current_k = (q - 1) // TWO_P
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({'last_k_processed': current_k, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'interrupted': True}, f, indent=2)
        print(f"Checkpoint saved: k = {current_k:,}")
        return
    
    # Done — no factor found
    elapsed = time.time() - t_start
    print()
    print("=" * 70)
    print("Done — no factor found")
    print("=" * 70)
    print(f"Elapsed: {elapsed:.0f}s ({elapsed/3600:.2f} hours)")
    print(f"Primes checked: {count_primes:,}")
    print(f"Primes ≡ 1 mod 2474: {count_mod_2474:,}")
    print(f"Primes with pow(2,1237,q)==1: {count_pow}")
    
    current_k = (q - 1) // TWO_P
    print(f"Last k: {current_k:,}")
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({'last_k_processed': current_k, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'final': True, 'no_factor_found': True}, f, indent=2)

if __name__ == '__main__':
    main()
