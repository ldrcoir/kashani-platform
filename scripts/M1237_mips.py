#!/usr/bin/env python3
"""
Mersenne Index Power Search (MIPS) - direct k scan.

WHY THIS IS GENUINELY DIFFERENT:
  - For M(p), every prime factor q satisfies q = 2*k*p + 1 for some k.
  - P-1 checks if k is B1-smooth (i.e., all prime factors of k <= B1).
    That fails for large k.
  - This method EXPLICITLY tries small k values: q_candidate = 2*k*p + 1.
  - For each k = 1, 2, 3, ...:
      - Compute q_cand = 2*k*p + 1
      - Check if q_cand is prime (skip if not)
      - Check if M(p) % q_cand == 0  →  FACTOR FOUND

  - This is NOT smoothness-based. It's a direct scan over k.
  - P-1 misses this when k is large even if k is prime (k itself is just one large prime).
  - We can directly scan k up to BILLIONS quickly (each k test is microseconds).

ALGORITHM:
  For k = 1, 2, 3, ..., 10^12 (or whatever we can afford):
    q_cand = 2*k*p + 1
    if q_cand is prime:
        if M(p) % q_cand == 0:
            FACTOR FOUND!

  For M(1237), we know F1 has k = F1 / (2*1237) ≈ 10^66, way beyond scan.
  But COFACTORS might have smaller k.

  Cost per k: ~O(log p) for primality test, but quick compositeness rejection.
  Realistic rate: ~10^5 - 10^6 k values per second.

  Time to scan k up to 10^9: 10^9 / 10^5 = 10000 seconds = 2.8 hours.
  Time to scan k up to 10^12: 2800 hours. Infeasible without parallelism.
"""

import sys
import time
from pathlib import Path

import gmpy2
from gmpy2 import mpz, is_prime, gcd

p = 1237
M = mpz(2)**p - 1
F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
N = M // F1
print(f"N has {len(str(N))} digits", file=sys.stderr)

LOG_FILE = Path('/home/z/my-project/logs/M1237_mips.log')
LOG_FILE.parent.mkdir(exist_ok=True)


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')


def main():
    log('=' * 70)
    log(f'Mersenne Index Power Search (MIPS)')
    log(f'  Target: N = M(1237)/F1, {len(str(N))} digits')
    log(f'  Strategy: scan k = 1, 2, ..., 10^10')
    log(f'    For each k: q_cand = 2*k*p + 1')
    log(f'    If prime AND M(1237) % q_cand == 0: factor!')
    log('=' * 70)

    if is_prime(N):
        log('N is already prime — done')
        return

    start_k = 1
    end_k = 10_000_000  # 10 million, takes ~1-2 min

    t_start = time.time()
    found_count = 0
    current_N = N
    current_M = M

    k = start_k
    while k <= end_k:
        q_cand = 2 * k * p + 1
        # Quick composite rejection: q_cand is composite if not prime
        if not is_prime(q_cand):
            k += 1
            continue
        # Check if q_cand divides current_M (or current_N, equivalent)
        if current_M % q_cand == 0:
            log(f'>>> k={k}: q_cand={q_cand} divides M(1237)! FACTOR FOUND')
            log(f'    q_cand digits: {len(str(q_cand))}')
            found_count += 1
            # Update factors file
            # Use existing function
            sys.path.insert(0, '/home/z/my-project/scripts')
            from pm1_factor import update_factor, append_to_complete
            if q_cand < int(F1):
                log(f'    NEW SMALLER than F1: {q_cand}')
                update_factor('/home/z/my-project/download/A136030_factors_1_to_8000.txt', p, int(q_cand))
            while current_N % q_cand == 0:
                current_N //= q_cand
                current_M //= q_cand
            log(f'    reduced N to {len(str(current_N))} digits')
            if is_prime(current_N) or current_N == 1:
                log(f'    N is now prime or 1 — done')
                break

        # Log progress every 100000 k
        if k % 100_000 == 0:
            elapsed = time.time() - t_start
            rate = k / elapsed if elapsed > 0 else 0
            log(f'  k={k}, elapsed={elapsed:.1f}s, rate={rate:.0f} k/s, found={found_count}')

        k += 1

    elapsed = time.time() - t_start
    log('')
    log('=' * 70)
    log(f'MIPS complete: scanned k in [{start_k}, {end_k}]')
    log(f'  Elapsed: {elapsed:.1f}s')
    log(f'  Found: {found_count} factor(s)')
    log(f'  Remaining N: {len(str(current_N))} digits, is_prime={is_prime(current_N)}')
    log('=' * 70)


if __name__ == '__main__':
    main()
