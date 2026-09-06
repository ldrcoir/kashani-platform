#!/usr/bin/env python3
"""
Trial-division search for smallest prime factor of M(p) = 2^p - 1 for the
smallest 'missing' primes p in A136030 (those still marked -1).

Trial-division approach (specialized for Mersenne numbers):
  Any prime factor q of M(p) satisfies q = 2*k*p + 1 for some integer k >= 1
  and q ≡ ±1 (mod 8).
  We iterate k = 1, 2, 3, ..., and for each candidate q:
    1. Quick composite filter (small-prime sieve up to ~10000)
    2. Full primality test (sympy.isprime)
    3. Check pow(2, p, q) == 1  (q divides M(p))

If a factor is found, we record it and stop (we want the smallest).

We process the smallest missing primes > 1500 first (those not covered by
the Cunningham 2- table, which only goes up to n=1499).

Time budget: ~3 minutes per prime. Re-runnable; results accumulate.
"""

import sys
import time
import json
from pathlib import Path
from sympy import isprime

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
NEW_FACTORS_LOG = BASE / 'download/trial_division_log.txt'

# Per-prime time budget (seconds)
BUDGET_PER_PRIME = 60
# Max k to test per prime (hard cap, regardless of time)
MAX_K = 50_000_000
# How many primes to attempt
MAX_PRIMES = 3
# Small primes for quick composite filter
SMALL_PRIMES = [p for p in range(2, 1000) if isprime(p)]


def small_primes_sieve_factor(n, primes):
    """Return True if n has a small prime factor in `primes` (and is thus composite)."""
    for p in primes:
        if p * p > n:
            break
        if n % p == 0:
            return True
    return False


def read_factors_table(path):
    rows = []
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
            rows.append((n, v))
    return rows


def write_factors_table(path, rows):
    lines = [
        '# Series A136030: Smallest prime factor of Mersenne number M(n) = 2^n - 1',
        '# n from 1 to 8000',
        '# Value: 1 if n=1; 0 if M(n) is a Mersenne prime; else smallest prime factor; -1 if not found',
        '# Format: n<TAB>value',
    ]
    for n, v in rows:
        lines.append(f'{n}\t{v}')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def trial_divide_mersenne(p, budget_seconds, max_k, log_lines):
    """Search for smallest prime factor of M(p) of form 2*k*p+1.
    Returns the factor (int) or None."""
    t0 = time.time()
    found = None
    k_tested = 0
    last_progress = t0
    for k in range(1, max_k + 1):
        k_tested = k
        # Periodic time check
        if k % 100000 == 0:
            now = time.time()
            if now - t0 > budget_seconds:
                log_lines.append(f'    time budget exhausted at k={k}')
                break
            if now - last_progress > 15:
                log_lines.append(f'    progress: k={k}, elapsed={now-t0:.0f}s')
                last_progress = now
        q = 2 * k * p + 1
        # q must be ≡ ±1 (mod 8)
        r = q & 7
        if r != 1 and r != 7:
            continue
        # Quick composite filter
        if small_primes_sieve_factor(q, SMALL_PRIMES):
            continue
        # Full primality
        if not isprime(q):
            continue
        # Does q divide M(p)?
        if pow(2, p, q) == 1:
            found = q
            log_lines.append(f'    *** FOUND at k={k}: q={q} ***')
            break
    elapsed = time.time() - t0
    log_lines.append(f'    finished: k_tested={k_tested}, elapsed={elapsed:.1f}s')
    return found


def main():
    print('Reading factors table ...', file=sys.stderr)
    rows = read_factors_table(FACTORS_FILE)
    missing = [n for n, v in rows if v == -1]
    # Filter to primes > 1500 (Cunningham's range already covered)
    missing_primes = [n for n in missing if n > 1500 and isprime(n)]
    missing_primes.sort()
    print(f'  Missing primes > 1500: {len(missing_primes)}', file=sys.stderr)
    print(f'  First 10: {missing_primes[:10]}', file=sys.stderr)

    targets = missing_primes[:MAX_PRIMES]
    log_lines = [f'Trial division log - {time.strftime("%Y-%m-%d %H:%M:%S")}',
                 '=' * 60,
                 f'Time budget per prime: {BUDGET_PER_PRIME}s',
                 f'Max k per prime: {MAX_K}',
                 f'Targets: {targets}',
                 '']

    new_findings = []
    # Open log file at start so we can flush incrementally
    log_handle = open(NEW_FACTORS_LOG, 'w', encoding='utf-8')
    def log(msg):
        print(msg, file=sys.stderr)
        log_handle.write(msg + '\n')
        log_handle.flush()

    log(f'Trial division log - {time.strftime("%Y-%m-%d %H:%M:%S")}')
    log('=' * 60)
    log(f'Time budget per prime: {BUDGET_PER_PRIME}s')
    log(f'Max k per prime: {MAX_K}')
    log(f'Targets: {targets}')
    log('')

    for i, p in enumerate(targets, 1):
        log(f'[{i}/{len(targets)}] M({p}):')
        log(f'  searching k in [1, {MAX_K}], budget {BUDGET_PER_PRIME}s')
        prime_log = []
        factor = trial_divide_mersenne(p, BUDGET_PER_PRIME, MAX_K, prime_log)
        for line in prime_log:
            log(f'  {line}')
        if factor is not None:
            new_findings.append((p, factor))
            # Update rows
            for j, (n, v) in enumerate(rows):
                if n == p and v == -1:
                    rows[j] = (n, factor)
                    break
            log(f'  >>> Updated factors table: M({p}) -> {factor}')

    log('')
    log('Summary:')
    log(f'  Targets tried: {len(targets)}')
    log(f'  Factors found: {len(new_findings)}')
    for p, q in new_findings:
        log(f'    M({p}) -> {q}')
    log_handle.close()
    print(f'\nLog: {NEW_FACTORS_LOG}', file=sys.stderr)
    print(f'New factors: {len(new_findings)}', file=sys.stderr)

    if new_findings:
        write_factors_table(FACTORS_FILE, rows)
        print(f'Updated factors table.', file=sys.stderr)
        # Also append to complete factorizations file
        with open(COMPLETE_FILE, 'a', encoding='utf-8') as f:
            for p, q in new_findings:
                f.write(f'[PART ] M({p}) = {q}  (smallest known factor; cofactor untested)\n')
        print(f'Appended to complete factorizations file.', file=sys.stderr)


if __name__ == '__main__':
    main()
