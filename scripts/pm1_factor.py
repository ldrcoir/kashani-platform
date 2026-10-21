#!/usr/bin/env python3
"""
P-1 factoring for smallest prime factor of M(p) = 2^p - 1.

P-1 is especially effective for Mersenne numbers because:
  If q is a prime factor of M(p), then q = 2*k*p + 1 for some k.
  So q - 1 = 2*k*p, which is highly smooth if k is smooth.

Algorithm:
  1. Compute M = 2^p - 1
  2. Pick base a = 3
  3. Compute E = product of prime powers q^e <= B1 (i.e., log(B1)/log(q) for each prime q)
  4. Compute g = gcd(pow(a, E, M) - 1, M)
  5. If 1 < g < M, found a non-trivial factor

Stage 2 (optional, more powerful):
  For each prime q in (B1, B2], compute pow(a, q*E, M) incrementally and gcd.
  This catches factors where q-1 has exactly one large prime factor.

Targets: the smallest missing primes p > 1500 in A136030_factors_1_to_8000.txt.
"""

import sys
import time
import json
import argparse
from pathlib import Path

import gmpy2
from gmpy2 import mpz, gcd, is_prime, powmod

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
LOG_FILE = BASE / 'download/pm1_log.txt'


def small_primes_up_to(limit):
    """Sieve of Eratosthenes up to limit. Returns list of primes."""
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]


def pm1_factor(p, B1, B2=None, log_lines=None, base=3):
    """P-1 factoring on M(p) = 2^p - 1.
    Stage 1 bound B1. Optional Stage 2 bound B2.
    Returns a factor (int) or None."""
    M = mpz(2)**p - 1
    a = mpz(base)
    # Stage 1: compute E = product of prime powers q^e <= B1
    primes = small_primes_up_to(B1)
    if log_lines is not None:
        log_lines.append(f'  Stage 1: {len(primes)} primes up to B1={B1}')
    # For each prime q, multiply a by q^e where q^e <= B1
    # i.e., exponent = floor(log(B1)/log(q))
    import math
    for q in primes:
        e = max(1, int(math.log(B1) / math.log(q)))
        a = powmod(a, q**e, M)
    # Stage 1 gcd
    g = gcd(a - 1, M)
    if 1 < g < M:
        if log_lines is not None:
            log_lines.append(f'  Stage 1 found factor: {g}')
        return int(g)
    if g == M:
        # Bad base or huge factor; try different base
        if log_lines is not None:
            log_lines.append(f'  Stage 1 gcd = M (try different base)')
        return None

    # Stage 2: for primes q in (B1, B2], check if a^q reveals a factor.
    # We use the standard "powering with prev" approach: precompute a^d for d up to
    # a small delta, then walk through primes.
    if B2 is None or B2 <= B1:
        return None
    if log_lines is not None:
        log_lines.append(f'  Stage 2: primes in ({B1}, {B2}]')
    # Get primes in (B1, B2]
    primes2 = small_primes_up_to(B2)
    primes2 = [q for q in primes2 if q > B1]
    if not primes2:
        return None
    # Compute a^E once (already done - a is currently a^E mod M)
    # For each prime q in stage 2, we want a^(E*q) = (a^E)^q
    # Precompute powers of a^E for small differences between consecutive primes
    # (standard stage-2 optimization)
    # For simplicity, just iterate one prime at a time
    aE = a  # this is a^E mod M
    # Precompute aE^d for d = 2, 4, 6, ..., max_gap (since prime gaps are even after 2)
    # Use baby-step/giant-step style
    # Simpler: just compute aE^q for each q directly. Slower but correct.
    last_q = None
    aE_to_last = None
    found = None
    # Get all prime gaps up front
    diffs = []
    last = None
    for q in primes2:
        if last is None:
            diffs.append(q)
        else:
            diffs.append(q - last)
        last = q
    # Precompute aE^d for d in unique diffs (these are small even numbers, except first)
    # Actually the first diff is the prime itself, which is huge. So we need aE^(first prime)
    # Standard stage-2: instead of computing a^E once, we compute a^(E * first_prime)
    # Then increment by a^(E * gap) for subsequent primes
    # The first prime is the smallest prime > B1
    first_q = primes2[0]
    aE_q = powmod(aE, first_q, M)  # a^(E * first_q)
    # Compute gcd
    g = gcd(aE_q - 1, M)
    if 1 < g < M:
        if log_lines is not None:
            log_lines.append(f'  Stage 2 found factor at q={first_q}: {g}')
        return int(g)
    # Now walk: next_q = first_q + gap
    # We need a^(E * next_q) = a^(E * first_q) * a^(E * gap)
    # Precompute a^(E * d) for d in unique gaps
    unique_gaps = sorted(set(diffs[1:]))  # skip first which is first_q
    if log_lines is not None:
        log_lines.append(f'  Stage 2: {len(unique_gaps)} unique gaps')
    aE_gaps = {}
    for d in unique_gaps:
        aE_gaps[d] = powmod(aE, d, M)
    # Walk
    current = aE_q
    last_q_val = first_q
    for q in primes2[1:]:
        d = q - last_q_val
        current = (current * aE_gaps[d]) % M
        g = gcd(current - 1, M)
        if 1 < g < M:
            if log_lines is not None:
                log_lines.append(f'  Stage 2 found factor at q={q}: {g}')
            return int(g)
        last_q_val = q
    return None


def get_missing_primes(path, min_n=1500, max_n=8000, limit=None):
    missing = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) != 2:
                continue
            try:
                n = int(parts[0]); v = int(parts[1])
            except ValueError:
                continue
            if v == -1 and min_n <= n <= max_n:
                if is_prime(n):
                    missing.append(n)
    missing.sort()
    if limit:
        missing = missing[:limit]
    return missing


def update_factor(path, p, factor):
    """Update entry p in factors table with the newly found factor.
    Only update if existing value is -1 OR new factor is smaller and prime.
    Never overwrite a smaller existing prime factor with a larger composite."""
    lines = path.read_text(encoding='utf-8').splitlines()
    out = []
    updated = False
    for line in lines:
        if line.startswith('#') or not line:
            out.append(line)
            continue
        parts = line.split('\t')
        if len(parts) == 2 and parts[0] == str(p):
            existing = parts[1]
            if existing == '-1':
                out.append(f'{p}\t{factor}')
                updated = True
            else:
                try:
                    existing_val = int(existing)
                    if factor < existing_val and is_prime(factor):
                        out.append(f'{p}\t{factor}')
                        updated = True
                    else:
                        out.append(line)  # keep existing smaller factor
                except ValueError:
                    out.append(line)
        else:
            out.append(line)
    if updated:
        path.write_text('\n'.join(out) + '\n', encoding='utf-8')
    return updated


def append_to_complete(path, p, factor):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(f'[PART ] M({p}) = {factor}  (smallest known factor; P-1 found)\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--b1', type=int, default=1_000_000,
                        help='Stage 1 bound B1')
    parser.add_argument('--b2', type=int, default=100_000_000,
                        help='Stage 2 bound B2 (0 to disable)')
    parser.add_argument('--max-primes', type=int, default=10)
    parser.add_argument('--min-n', type=int, default=1500)
    parser.add_argument('--max-n', type=int, default=8000)
    parser.add_argument('--specific', type=int, nargs='*', default=None)
    args = parser.parse_args()

    if args.specific:
        # Filter to only those that are actually -1 in the file
        all_missing = set(get_missing_primes(FACTORS_FILE, 0, 100000))
        targets = sorted(set(args.specific) & all_missing)
        if len(targets) < len(args.specific):
            skipped = set(args.specific) - all_missing
            print(f'Note: skipping {len(skipped)} primes that are not -1: {sorted(skipped)[:10]}', file=sys.stderr)
    else:
        targets = get_missing_primes(FACTORS_FILE, args.min_n, args.max_n,
                                     args.max_primes)

    log_handle = open(LOG_FILE, 'w', encoding='utf-8')
    def log(msg):
        print(msg, file=sys.stderr)
        log_handle.write(msg + '\n')
        log_handle.flush()

    log(f'P-1 factoring log - {time.strftime("%Y-%m-%d %H:%M:%S")}')
    log('=' * 60)
    log(f'B1={args.b1}, B2={args.b2 if args.b2 > 0 else "disabled"}')
    log(f'Targets ({len(targets)}): {targets}')
    log('')

    total_found = 0
    for i, p in enumerate(targets, 1):
        log(f'[{i}/{len(targets)}] M({p}) ...')
        prime_log = []
        t_start = time.time()
        # If B2 is 0, disable stage 2
        b2 = args.b2 if args.b2 > 0 else None
        # Try multiple bases to avoid the rare case where gcd == M
        factor = None
        for base in [3, 5, 7, 11, 13, 17]:
            factor = pm1_factor(p, args.b1, b2, prime_log, base=base)
            if factor is not None:
                # P-1 gcd can return a composite product of multiple factors.
                # Try to extract the smallest prime factor of the gcd.
                if not is_prime(factor):
                    prime_log.append(f'  gcd is composite ({factor}); factoring')
                    # Trial-divide the composite to find a smaller prime factor
                    f = factor
                    smallest_prime = None
                    for pr in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
                        while f % pr == 0:
                            smallest_prime = pr if smallest_prime is None or pr < smallest_prime else smallest_prime
                            f //= pr
                    # If remaining is > 1 and prime, that's a candidate too
                    if f > 1 and is_prime(f):
                        smallest_prime = f if smallest_prime is None or f < smallest_prime else smallest_prime
                    if smallest_prime is not None:
                        prime_log.append(f'  extracted smallest prime factor: {smallest_prime}')
                        factor = smallest_prime
                    else:
                        prime_log.append(f'  could not extract prime factor; skipping')
                        factor = None
                        continue
                break
            # If gcd was M, retry with different base; otherwise no point retrying
            if any('gcd = M' in line for line in prime_log):
                prime_log.append(f'  retrying with base {base+2}')
                continue
            else:
                break
        elapsed = time.time() - t_start
        for line in prime_log:
            log(f'  {line}')
        log(f'  elapsed: {elapsed:.1f}s')
        if factor is not None:
            log(f'  >>> FOUND: M({p}) -> {factor}')
            update_factor(FACTORS_FILE, p, factor)
            append_to_complete(COMPLETE_FILE, p, factor)
            total_found += 1
        else:
            log(f'  no factor found')

    log('')
    log(f'Summary: {total_found}/{len(targets)} primes factored')
    log_handle.close()


if __name__ == '__main__':
    main()
