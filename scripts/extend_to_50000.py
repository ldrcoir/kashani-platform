#!/usr/bin/env python3
"""
Extend A136030 factors table from n=8000 to n=50000.

Strategy:
1. Read existing table (n=1 to 8000)
2. For each n in 8001..50000:
   - If n is a known Mersenne prime exponent: value = 0
   - If n == 1: value = 1
   - If n is prime: trial divide (k up to 100K) + quick P-1 (B1=1M); if not found, -1
   - If n is composite: look up smallest prime factor p of n; value = value of M(p)
3. Save periodically (every 1000 entries)
4. Final write

All paths under /home/z/my-project/.
"""

import sys
import time
import json
import math
import argparse
from pathlib import Path

import gmpy2
from gmpy2 import mpz, is_prime, powmod, gcd

BASE = Path('/home/z/my-project')
EXISTING_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
# Try to load from the 50000 file if it exists (for resume), else use 8000 file
NEW_FILE = BASE / 'download/A136030_factors_1_to_50000.txt'
LOG_FILE = BASE / 'download/extend_to_50000_log.txt'

# Known Mersenne prime exponents up to 50000
# Source: https://www.mersenne.org/primes/ (public list)
MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607,
    1279, 2203, 2281, 3217, 4253, 4423, 9689, 9941, 11213,
    19937, 21701, 23209, 44497
}

# Small primes for P-1
SMALL_PRIMES_1M = None  # cached

def get_small_primes_up_to(limit):
    """Sieve of Eratosthenes."""
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]


def trial_divide(p, max_k=100000):
    """Trial divide M(p) with candidates q = 2*k*p+1, q ≡ ±1 (mod 8).
    Returns factor or None."""
    for k in range(1, max_k + 1):
        q = 2 * k * p + 1
        if (q & 7) not in (1, 7):
            continue
        if not is_prime(q):
            continue
        if powmod(2, p, q) == 1:
            return q
    return None


def pm1_quick(p, B1=1_000_000):
    """Quick P-1 (Stage 1 only) on M(p) with bound B1.
    Returns a prime factor or None."""
    global SMALL_PRIMES_1M
    if SMALL_PRIMES_1M is None:
        SMALL_PRIMES_1M = get_small_primes_up_to(B1)
    M = mpz(2)**p - 1
    a = mpz(3)
    for q in SMALL_PRIMES_1M:
        e = max(1, int(math.log(B1) / math.log(q)))
        a = powmod(a, q**e, M)
    g = gcd(a - 1, M)
    if 1 < g < M:
        # Extract smallest prime factor if composite
        f = int(g)
        if is_prime(f):
            return f
        # Trial divide for small primes
        for pr in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]:
            while f % pr == 0:
                if is_prime(pr):
                    return pr
                f //= pr
        if f > 1 and is_prime(f):
            return f
        # Try with different base
        return None
    return None


def smallest_prime_factor(n):
    """Find smallest prime factor of n."""
    if n < 2:
        return None
    if n % 2 == 0:
        return 2
    for p in range(3, int(n**0.5) + 1, 2):
        if n % p == 0:
            return p
    return n  # n is prime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, default=8001, help='Start n')
    parser.add_argument('--end', type=int, default=50000, help='End n (inclusive)')
    parser.add_argument('--resume', action='store_true', help='Resume from NEW_FILE if it exists')
    args = parser.parse_args()

    print('Reading existing factors file ...', file=sys.stderr)
    existing = {}
    source_file = NEW_FILE if (args.resume and NEW_FILE.exists()) else EXISTING_FILE
    print(f'  Source: {source_file.name}', file=sys.stderr)
    with open(source_file) as f:
        for line in f:
            if '\t' in line and not line.startswith('#'):
                parts = line.strip().split('\t')
                n, v = int(parts[0]), parts[1]
                existing[n] = v
    print(f'  {len(existing)} entries read.', file=sys.stderr)

    # Open log file (append mode for resume)
    log_handle = open(LOG_FILE, 'a', encoding='utf-8')
    def log(msg):
        print(msg, file=sys.stderr)
        log_handle.write(msg + '\n')
        log_handle.flush()

    log(f'\n--- Resume log - {time.strftime("%Y-%m-%d %H:%M:%S")} ---')
    log(f'Range: n={args.start} to n={args.end}')
    log(f'Loaded {len(existing)} existing entries from {source_file.name}')

    # Results dict
    results = dict(existing)
    
    # Stats
    new_found = 0
    new_missing = 0
    new_mersenne = 0
    new_composite = 0
    t_start = time.time()

    log(f'Processing n from {args.start} to {args.end} ...')
    sys.stderr.flush()
    
    for n in range(args.start, args.end + 1):
        # Skip if already in existing
        if n in results:
            continue
        
        # Mersenne prime exponent?
        if n in MERSENNE_PRIME_EXPONENTS:
            results[n] = '0'
            new_mersenne += 1
            continue
        
        # Is n prime?
        if not is_prime(n):
            # Composite: use smallest prime factor's value
            sp = smallest_prime_factor(n)
            if sp is not None and sp in results:
                sp_val = results[sp]
                if sp_val == '0':
                    # M(sp) is a Mersenne prime, so the smallest prime factor
                    # of M(n) is M(sp) itself = 2^sp - 1
                    results[n] = str((1 << sp) - 1)
                else:
                    results[n] = sp_val
                new_composite += 1
            else:
                # sp not in results yet (shouldn't happen since sp < n)
                results[n] = '-1'
            continue
        
        # n is prime, not Mersenne prime
        # Step 1: trial division with k up to 1M (fast with gmpy2, ~0.3s per prime)
        factor = trial_divide(n, max_k=1_000_000)
        if factor is not None:
            results[n] = str(factor)
            new_found += 1
        elif n <= 10000:
            # Step 2: quick P-1 with B1=100K (only for small primes where M(p) is manageable)
            factor = pm1_quick(n, B1=100_000)
            if factor is not None:
                results[n] = str(factor)
                new_found += 1
            else:
                results[n] = '-1'
                new_missing += 1
        else:
            # For large primes, P-1 is too slow (M(p) is huge). Just mark as -1.
            results[n] = '-1'
            new_missing += 1
        
        # Periodic progress and save
        if n % 100 == 0:
            elapsed = time.time() - t_start
            rate = (n - args.start + 1) / elapsed if elapsed > 0 else 0
            eta = (args.end - n) / rate if rate > 0 else 0
            log(f'  n={n}, found={new_found}, missing={new_missing}, '
                f'mersenne={new_mersenne}, composite={new_composite}, '
                f'elapsed={elapsed:.0f}s, rate={rate:.1f}/s, eta={eta:.0f}s')
            # Save current state
            write_table(NEW_FILE, results)
    
    # Final write
    write_table(NEW_FILE, results)
    
    log('')
    log('Chunk done!')
    log(f'Total entries in table: {len(results)}')
    log(f'New found: {new_found}')
    log(f'New missing: {new_missing}')
    log(f'New Mersenne primes: {new_mersenne}')
    log(f'New composite (derived): {new_composite}')
    log(f'Total elapsed: {time.time() - t_start:.0f}s')
    log_handle.close()


def write_table(path, results):
    """Write the factors table."""
    lines = [
        '# Series A136030: Smallest prime factor of Mersenne number M(n) = 2^n - 1',
        '# n from 1 to 50000',
        '# Value: 1 if n=1; 0 if M(n) is a Mersenne prime; else smallest prime factor; -1 if not found',
        '# Format: n<TAB>value',
    ]
    for n in sorted(results.keys()):
        lines.append(f'{n}\t{results[n]}')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
