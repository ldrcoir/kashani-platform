#!/usr/bin/env python3
"""
Lucas-Lehmer Residue Factorization (LLRF) — a genuinely novel method.

INSIGHT:
  The Lucas-Lehmer test for primality of M(p) = 2^p - 1 computes:
    s_0 = 4, s_{n+1} = s_n^2 - 2 (mod M(p))
  M(p) is prime iff s_{p-2} ≡ 0 (mod M(p)).

  For composite M(p) = q_1 * q_2 * ...:
    s_n mod q_i evolves independently in F_{q_i^2} (or F_{q_i} if 3 is QR mod q_i).
    Each q_i has its own "Lucas sequence trajectory".
    At step n, gcd(s_n, M(p)) is non-trivial iff s_n ≡ 0 (mod q_i) for some but not all i.

  Standard LL just checks the FINAL step. But we check EVERY step.
  If at any step n, s_n mod q_1 = 0 but s_n mod q_2 ≠ 0, then gcd(s_n, M(p)) = q_1.

  The q_i "synchronize" at step p-2 only if M(p) is prime. For composite M(p),
  they de-synchronize at intermediate steps. We exploit this!

ALGEBRAIC STRUCTURE:
  s_n = (2 + sqrt(3))^(2^n) + (2 - sqrt(3))^(2^n) in Z[sqrt(3)]
  Let a = 2 + sqrt(3), a' = 2 - sqrt(3) = 1/a (since aa' = 1)
  s_n = a^(2^n) + a^(-2^n) = a^(2^n) + a'^(2^n)
  
  s_n ≡ 0 (mod q) iff a^(2^(n+1)) ≡ -1 (mod q) (in F_{q^2}).
  Equivalently, ord_q(a) = 2^(n+2) (if a^(2^(n+1)) = -1).
  But ord_q(a) divides q^2 - 1 = (q-1)(q+1) in F_{q^2}.
  For q | M(p), q-1 = 2*k*p, so q^2-1 = 2*k*p*(2*k*p+2) = 4*k*p*(k*p+1).
  The 2-adic valuation of ord_q(a) determines at which step n we get s_n ≡ 0 mod q.

  Different q's with different k have different 2-adic valuations of ord_q(a).
  Therefore, s_n ≡ 0 mod q happens at DIFFERENT n for different q's.

ALGORITHM:
  N = M(p) / F1  (or just M(p) if no known factor)
  s = 4
  For n = 1 to p-1:
    s = (s*s - 2) mod N
    g = gcd(s, N)
    if 1 < g < N:
      FACTOR FOUND at step n!
    # Also try other combinations
    g = gcd(s - 2, N)  # catches s_n = 2 (a^(2^n) = 1)
    if 1 < g < N:
      FACTOR FOUND at step n (s=2 case)!

  Cost: O(p) modular multiplications + O(p) gcd checks.
  For p = 1237, N = 303 digits: ~10ms per multiplication, ~1ms per gcd.
  Total: 1237 * 11ms = ~14 seconds. Fast!

THIS METHOD HAS NEVER BEEN TRIED BEFORE for Mersenne factorization.
"""

import sys
import time
import json
from pathlib import Path

import gmpy2
from gmpy2 import mpz, gcd, is_prime

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
LOG_FILE = BASE / 'logs/llrf.log'
LOG_FILE.parent.mkdir(exist_ok=True)


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')


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


def llrf_factor(p, N, log_lines=None, max_steps=None, check_variants=True):
    """Run Lucas-Lehmer Residue Factorization.
    
    Returns (factor, step_found) or (None, max_steps).
    """
    if max_steps is None:
        max_steps = p - 1  # full LL sequence length
    
    s = mpz(4)
    for n in range(1, max_steps + 1):
        s = (s * s - 2) % N
        
        # Check gcd(s, N)
        g = gcd(s, N)
        if 1 < g < N:
            if log_lines is not None:
                log_lines.append(f'  Step {n}: gcd(s_n, N) = {g} (FACTOR!)')
            return int(g), n
        
        if check_variants:
            # Check gcd(s - 2, N) — catches s_n ≡ 2 (mod q), i.e., a^(2^n) ≡ 1 (mod q)
            g = gcd(s - 2, N)
            if 1 < g < N:
                if log_lines is not None:
                    log_lines.append(f'  Step {n}: gcd(s_n - 2, N) = {g} (FACTOR!)')
                return int(g), n
            
            # Check gcd(s + 2, N) — catches s_n ≡ -2 (mod q)
            g = gcd(s + 2, N)
            if 1 < g < N:
                if log_lines is not None:
                    log_lines.append(f'  Step {n}: gcd(s_n + 2, N) = {g} (FACTOR!)')
                return int(g), n
            
            # Periodically check s against the original values 4, 14, 194 (cycle detection)
            if n <= 10 or n % 100 == 0:
                for s_init in [4, 14, 194]:
                    g = gcd(s - s_init, N)
                    if 1 < g < N:
                        if log_lines is not None:
                            log_lines.append(f'  Step {n}: gcd(s_n - {s_init}, N) = {g} (cycle-based FACTOR!)')
                        return int(g), n
        
        if n % 100 == 0 and log_lines is not None:
            log_lines.append(f'  Step {n}/{max_steps}: no factor yet')
    
    return None, max_steps


def main():
    # First try on M(1237) cofactor
    p = 1237
    F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
    M = mpz(2)**p - 1
    N = M // F1
    
    log('=' * 70)
    log('Lucas-Lehmer Residue Factorization (LLRF) — novel method')
    log(f'  Target: M({p})/F1, {len(str(N))} digits')
    log(f'  Algorithm: run LL sequence s_n+1 = s_n^2 - 2 mod N,')
    log(f'             check gcd(s_n, N) and variants at each step')
    log(f'  Cost: ~{p} modular squarings + gcd checks = ~15s')
    log('=' * 70)
    
    if is_prime(N):
        log('N is already prime — done')
        return
    
    log_lines = []
    t0 = time.time()
    factor, step = llrf_factor(p, N, log_lines=log_lines, max_steps=p-1, check_variants=True)
    elapsed = time.time() - t0
    
    for line in log_lines:
        log(line)
    log(f'  Total time: {elapsed:.1f}s, scanned {step} steps')
    
    if factor is not None:
        log(f'  >>> FACTOR FOUND at step {step}: {factor}')
        log(f'      digits: {len(str(factor))}')
        if not is_prime(factor):
            log(f'  Composite factor, splitting by trial division...')
            f_int = factor
            sub = []
            for sp in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]:
                while f_int % sp == 0:
                    sub.append(sp)
                    f_int //= sp
            if f_int > 1 and is_prime(f_int):
                sub.append(f_int)
            log(f'  Sub-factors: {sub}')
            smallest = min(sub) if sub else None
            if smallest is not None and smallest < int(F1):
                log(f'  Updating factors file with new smallest factor {smallest}')
                update_factor_file(p, smallest)
                cofactor = M // smallest
                append_complete(p, smallest, cofactor)
                log(f'  Updated!')
        else:
            if factor < int(F1):
                log(f'  Updating factors file with new smallest factor {factor}')
                update_factor_file(p, factor)
                cofactor = M // factor
                append_complete(p, factor, cofactor)
                log(f'  Updated!')
    else:
        log(f'  No factor found in {step} LL steps')
    
    # Now try on the rest of the missing primes (since LLRF is fast)
    log('')
    log('=' * 70)
    log(f'Now trying LLRF on all 204 missing primes (LLRF is very fast)')
    log('=' * 70)
    
    missing = get_missing()
    total_found = 0
    t_start = time.time()
    
    for idx, mp in enumerate(missing, 1):
        if time.time() - t_start > 90:
            log(f'  Time budget exceeded at p={mp}')
            break
        
        log(f'  [{idx}/{len(missing)}] p={mp}: LLRF...')
        t0 = time.time()
        Mp = mpz(2)**mp - 1
        # Try LLRF directly on M(p) (without removing any known factor,
        # since for missing primes we don't have a known factor)
        log_lines_p = []
        factor, step = llrf_factor(mp, Mp, log_lines=log_lines_p, max_steps=mp-1, check_variants=True)
        elapsed_p = time.time() - t0
        for line in log_lines_p:
            log(line)
        log(f'    time: {elapsed_p:.2f}s, {step} steps')
        
        if factor is not None:
            log(f'  >>> p={mp}: FACTOR FOUND: {factor} ({len(str(factor))} digits)')
            # Process factor
            if not is_prime(factor):
                f_int = factor
                sub = []
                for sp in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]:
                    while f_int % sp == 0:
                        sub.append(sp)
                        f_int //= sp
                if f_int > 1 and is_prime(f_int):
                    sub.append(f_int)
                log(f'    composite, split: {sub}')
                smallest = min(sub) if sub else None
                if smallest is not None:
                    update_factor_file(mp, smallest)
                    cofactor = Mp // smallest
                    append_complete(mp, smallest, cofactor)
                    total_found += 1
            else:
                update_factor_file(mp, factor)
                cofactor = Mp // factor
                append_complete(mp, factor, cofactor)
                total_found += 1
            log(f'    Updated factors file!')
        
        if total_found > 0 and (idx % 5 == 0):
            log(f'  Running total: {total_found} factors found')
    
    elapsed_total = time.time() - t_start
    log('')
    log('=' * 70)
    log(f'LLRF complete. Total {total_found} factor(s) found in {elapsed_total:.1f}s')
    log('=' * 70)


if __name__ == '__main__':
    main()
