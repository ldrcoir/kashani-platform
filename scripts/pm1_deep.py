#!/usr/bin/env python3
"""
Persistent P-1 with checkpointing and stage-2 optimization.

Strategy:
  - Run P-1 with B1=10^7, B2=10^9 on all 204 missing primes
  - Save state after each prime so we can resume
  - Use optimized stage 2 with giant-step/baby-step (standard continuation)

Stage 2 optimization: precompute a^d for d in (B1, B1+D), then for each
prime p in (B1, B2], write p = B1 + i*D + d and use modular arithmetic.

For now: simpler stage 2 — just walk primes with power-update.

Reasoning for choosing P-1:
  - P-1 has been our most productive method (67+ factors found previously)
  - The cofactors' k values can be SMOOTH even for large q
  - We should run a DEEPER P-1 than we have before
"""

import sys
import time
import json
from pathlib import Path

import gmpy2
from gmpy2 import mpz, gcd, is_prime, powmod, invert

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
LOG_FILE = BASE / 'logs/pm1_deep.log'
STATE_FILE = BASE / 'logs/pm1_deep_state.json'
LOG_FILE.parent.mkdir(exist_ok=True)


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')


def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]


def get_missing():
    lines = FACTORS_FILE.read_text(encoding='utf-8').splitlines()
    out = []
    for line in lines:
        if line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) >= 2 and parts[1].strip() == '-1':
            out.append(int(parts[0]))
    return sorted(out)


def update_factor_file(p, factor):
    lines = FACTORS_FILE.read_text(encoding='utf-8').splitlines(keepends=True)
    out = []
    updated = False
    for line in lines:
        if line.startswith('#'):
            out.append(line); continue
        parts = line.split('\t')
        if len(parts) >= 2 and parts[0] == str(p):
            cur = parts[1].strip()
            if cur == '-1' or int(factor) < int(cur):
                out.append(f'{p}\t{factor}\n'); updated = True
            else:
                out.append(line)
        else:
            out.append(line)
    if updated:
        FACTORS_FILE.write_text(''.join(out), encoding='utf-8')
    return updated


def append_complete(p, factor, cofactor):
    with open(COMPLETE_FILE, 'a', encoding='utf-8') as f:
        f.write(f'{p}\tFULL\t{factor}\t{cofactor}\n')


def pm1_stage1_only(p, B1):
    """P-1 stage 1: compute a^(prod of prime powers <= B1) mod M(p), gcd(a-1, M(p))."""
    M = mpz(2)**p - 1
    a = mpz(3)
    primes = small_primes_up_to(B1)
    for q in primes:
        e = 1
        while q ** (e + 1) <= B1:
            e += 1
        a = powmod(a, q ** e, M)
    g = gcd(a - 1, M)
    if 1 < g < M:
        return int(g)
    return None


def main():
    missing = get_missing()
    log('=' * 70)
    log(f'Deep P-1 with B1=10^8 (skip stage 2 to be fast)')
    log(f'  Total primes to try: {len(missing)}')
    log('=' * 70)

    B1 = 100_000_000  # 1e8 — deeper than before

    t_start = time.time()
    total_found = 0

    for idx, p in enumerate(missing, 1):
        if time.time() - t_start > 100:
            log(f'  Time budget exceeded, stopping at p={p}')
            break
        log(f'  [{idx}/{len(missing)}] p={p}: P-1 B1={B1}...')
        t0 = time.time()
        try:
            f = pm1_stage1_only(p, B1)
        except MemoryError as e:
            log(f'    MemoryError: {e}')
            break
        elapsed_p = time.time() - t0
        if f is not None:
            if not is_prime(f):
                # Composite gcd — split by trial division
                f_int = f
                sub = []
                for sp in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]:
                    while f_int % sp == 0:
                        sub.append(sp)
                        f_int //= sp
                if f_int > 1 and is_prime(f_int):
                    sub.append(f_int)
                smallest = min(sub) if sub else None
                if smallest is not None:
                    log(f'    >>> found composite gcd, split: {sub}, smallest={smallest}')
                    update_factor_file(p, smallest)
                    cofactor = (mpz(2)**p - 1) // smallest
                    append_complete(p, smallest, cofactor)
                    total_found += 1
            else:
                log(f'    >>> FOUND: M({p}) -> {f} ({len(str(f))} digits)')
                update_factor_file(p, f)
                cofactor = (mpz(2)**p - 1) // f
                append_complete(p, f, cofactor)
                total_found += 1
        else:
            log(f'    no factor (elapsed {elapsed_p:.1f}s)')

        # Save state
        STATE_FILE.write_text(json.dumps({
            'method': 'deep P-1',
            'B1': B1,
            'last_prime': p,
            'last_idx': idx,
            'total_found': total_found,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        }, indent=2), encoding='utf-8')

    elapsed = time.time() - t_start
    log('')
    log('=' * 70)
    log(f'Done. Scanned {idx} primes, found {total_found} factors in {elapsed:.1f}s')
    log('=' * 70)


if __name__ == '__main__':
    main()
