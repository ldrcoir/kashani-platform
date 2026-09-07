#!/usr/bin/env python3
"""
High-speed trial division for smallest prime factor of M(p) = 2^p - 1.
Uses gmpy2 (much faster than sympy) and runs in parallel across CPU cores.

Strategy:
  - For each missing prime p in A136030_factors_1_to_8000.txt, search
    candidate factors q = 2*k*p + 1 with q ≡ ±1 (mod 8).
  - Each worker handles a chunk of k values for a single prime.
  - Use gmpy2.is_prime for primality testing and pow(2, p, q) == 1 for divisibility.

Targets:
  - The smallest missing primes > 1500 (Cunningham's table only goes to 1499).
  - Search k in [k_start, k_start + chunk_size) per worker.

Time budget: ~5 minutes per prime, in parallel.
"""

import sys
import time
import json
import argparse
import multiprocessing as mp
from pathlib import Path

import gmpy2
from gmpy2 import mpz, is_prime

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
LOG_FILE = BASE / 'download/trial_division_fast_log.txt'

# Hard caps
DEFAULT_BUDGET_PER_PRIME = 240  # 4 minutes per prime
DEFAULT_K_CHUNK = 50_000_000     # each worker tests up to 50M k values per round
DEFAULT_MAX_PRIMES = 8


def search_chunk(args):
    """Search k in [k_start, k_end) for a factor of M(p).
    Returns (p, factor_or_None, k_tested)."""
    p, k_start, k_end = args
    tested = 0
    p_mpz = mpz(p)
    for k in range(k_start, k_end):
        tested += 1
        q = 2 * k * p + 1
        # q ≡ ±1 (mod 8)
        if (q & 7) not in (1, 7):
            continue
        if not is_prime(q):
            continue
        # q divides M(p)?
        if pow(2, p, q) == 1:
            return (p, q, tested)
    return (p, None, tested)


def get_missing_primes(path, min_n=1500, max_n=8000, limit=None):
    """Get list of primes p > min_n that are marked -1 in factors table."""
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
    """Update entry p in factors table with the newly found factor."""
    lines = path.read_text(encoding='utf-8').splitlines()
    out = []
    for line in lines:
        if line.startswith('#') or not line:
            out.append(line)
            continue
        parts = line.split('\t')
        if len(parts) == 2 and parts[0] == str(p):
            out.append(f'{p}\t{factor}')
        else:
            out.append(line)
    path.write_text('\n'.join(out) + '\n', encoding='utf-8')


def append_to_complete(path, p, factor):
    """Append newly found factor to complete factorizations file."""
    with open(path, 'a', encoding='utf-8') as f:
        f.write(f'[PART ] M({p}) = {factor}  (smallest known factor; cofactor untested)\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--budget', type=int, default=DEFAULT_BUDGET_PER_PRIME,
                        help='Time budget per prime (seconds)')
    parser.add_argument('--max-primes', type=int, default=DEFAULT_MAX_PRIMES,
                        help='Max number of primes to attempt')
    parser.add_argument('--min-n', type=int, default=1500,
                        help='Minimum n to consider')
    parser.add_argument('--max-n', type=int, default=8000,
                        help='Maximum n to consider')
    parser.add_argument('--workers', type=int, default=2,
                        help='Number of parallel workers')
    parser.add_argument('--specific', type=int, nargs='*', default=None,
                        help='Specific primes p to try (overrides scan)')
    args = parser.parse_args()

    COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'

    if args.specific:
        targets = sorted(args.specific)
    else:
        targets = get_missing_primes(FACTORS_FILE, args.min_n, args.max_n, args.max_primes)

    log_lines = []
    log_handle = open(LOG_FILE, 'w', encoding='utf-8')
    def log(msg):
        print(msg, file=sys.stderr)
        log_handle.write(msg + '\n')
        log_handle.flush()

    log(f'Fast trial division log - {time.strftime("%Y-%m-%d %H:%M:%S")}')
    log('=' * 60)
    log(f'Budget per prime: {args.budget}s')
    log(f'Parallel workers: {args.workers}')
    log(f'Targets ({len(targets)}): {targets}')
    log('')

    total_found = 0
    for i, p in enumerate(targets, 1):
        log(f'[{i}/{len(targets)}] M({p}) - searching k from 1 ...')
        t_start = time.time()
        deadline = t_start + args.budget
        k_cursor = 1
        round_idx = 0
        factor_found = None
        # Use a pool of workers, each handling a non-overlapping k-range.
        with mp.Pool(args.workers) as pool:
            while time.time() < deadline and factor_found is None:
                # Build worker args
                worker_args = []
                for w in range(args.workers):
                    k_start = k_cursor + w * DEFAULT_K_CHUNK
                    k_end = k_start + DEFAULT_K_CHUNK
                    if time.time() >= deadline:
                        break
                    # Truncate last chunk to deadline
                    worker_args.append((p, k_start, k_end))
                if not worker_args:
                    break
                round_idx += 1
                log(f'  round {round_idx}: k ranges {worker_args[0][1]}..{worker_args[-1][2]} '
                    f'(elapsed {time.time()-t_start:.0f}s)')
                # Async map; we want to abort early if any worker finds a factor
                results = pool.map(search_chunk, worker_args)
                for rp, factor, tested in results:
                    if factor is not None:
                        factor_found = factor
                        log(f'  *** FACTOR FOUND: {factor} ***')
                        break
                k_cursor += args.workers * DEFAULT_K_CHUNK

        elapsed = time.time() - t_start
        if factor_found is not None:
            log(f'  >>> Updated M({p}) -> {factor_found}  (elapsed {elapsed:.1f}s)')
            update_factor(FACTORS_FILE, p, factor_found)
            append_to_complete(COMPLETE_FILE, p, factor_found)
            total_found += 1
        else:
            log(f'  no factor found in {elapsed:.1f}s, k_max ~ {k_cursor:,}')

    log('')
    log(f'Summary: {total_found}/{len(targets)} primes factored')
    log_handle.close()


if __name__ == '__main__':
    main()
