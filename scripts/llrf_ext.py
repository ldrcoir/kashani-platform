#!/usr/bin/env python3
"""
Extended LLRF: run Lucas-Lehmer sequence PAST step p-2, up to step 2*p or beyond.

INSIGHT:
  For composite M(p) = q1 * q2, the LL sequence mod q1 and mod q2 have DIFFERENT
  cycle lengths in F_{q^2} (or F_q depending on whether 3 is QR).
  
  Standard LL stops at step p-2 (primality test threshold).
  But the FACTORING structure exists at ALL steps, not just p-2.
  
  If the cycle length in F_{q1^2} is L1 and in F_{q2^2} is L2,
  and L1 < L < L2 for some L, then at step L:
    s_L ≡ s_0 ≡ 4 (mod q1) but s_L ≢ 4 (mod q2)
  So gcd(s_L - 4, N) = q1.
  
  Pollard's rho does this with Floyd's cycle detection — but expects ~sqrt(q) iterations.
  For q ~ 100 digits, that's infeasible.
  
  BUT: the LL iteration has SPECIFIC STRUCTURE. The element a = 2+sqrt(3) has
  order dividing q^2-1 (or q-1) — so cycle length is at most q+1 or so. For random q,
  cycle length could be small if there's algebraic structure.
  
  Specifically, the order of a = 2+sqrt(3) mod q divides:
    q-1 if (3/q) = +1 (sqrt(3) in F_q)
    q+1 if (3/q) = -1 (sqrt(3) in F_{q^2})
  
  So cycle length is at most q+1 (for inert case).
  And it's at least a divisor of q+1.
  
  If 2-adic valuation of q+1 is small (e.g., q+1 = 2 * odd), then cycle length
  in 2-power steps is small. Specifically, s_n ≡ 4 mod q at step n means
  a^(2^n) ≡ a (mod q), i.e., 2^n ≡ 1 (mod ord_q(a)).
  
  So s_n returns to s_0 = 4 at step n where 2^n ≡ 1 (mod ord_q(a)).
  The smallest such n is the multiplicative order of 2 modulo ord_q(a).
  
  For P-1, ord_q(2) = p (since q | M(p)). So 2 has order p mod q.
  If ord_q(a) = m, we need 2^n ≡ 1 mod m. The smallest n is ord_m(2).
  
  Hmm complex. Let me just run LLRF extended and check empirically.
"""

import sys
import time
from pathlib import Path

import gmpy2
from gmpy2 import mpz, gcd, is_prime

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
LOG_FILE = BASE / 'logs/llrf_ext.log'
LOG_FILE.parent.mkdir(exist_ok=True)


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')


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


def llrf_extended(p, N, max_steps, log_lines=None, check_interval=100):
    """Run LL sequence for many steps, checking gcd at each step.
    Also check against initial values 4, 14, 194 for cycle detection.
    """
    s = mpz(4)
    initial_values = [mpz(4), mpz(14), mpz(194), mpz(37634)]
    
    for n in range(1, max_steps + 1):
        s = (s * s - 2) % N
        
        # Main check: gcd(s, N)
        g = gcd(s, N)
        if 1 < g < N:
            if log_lines is not None:
                log_lines.append(f'  Step {n}: gcd(s, N) = {g} (FACTOR!)')
            return int(g), n
        # gcd(s - 2, N): catches s ≡ 2 mod q (a^(2^n) = 1)
        g = gcd(s - 2, N)
        if 1 < g < N:
            if log_lines is not None:
                log_lines.append(f'  Step {n}: gcd(s - 2, N) = {g} (FACTOR!)')
            return int(g), n
        # gcd(s + 2, N): catches s ≡ -2 mod q
        g = gcd(s + 2, N)
        if 1 < g < N:
            if log_lines is not None:
                log_lines.append(f'  Step {n}: gcd(s + 2, N) = {g} (FACTOR!)')
            return int(g), n
        
        # Cycle detection: gcd(s - s_0, N), gcd(s - s_1, N), etc.
        for init_val in initial_values:
            g = gcd(s - init_val, N)
            if 1 < g < N:
                if log_lines is not None:
                    log_lines.append(f'  Step {n}: gcd(s - {init_val}, N) = {g} (cycle FACTOR!)')
                return int(g), n
        
        if n % check_interval == 0 and log_lines is not None:
            log_lines.append(f'  Step {n}/{max_steps}: no factor')
    
    return None, max_steps


def main():
    p = 1237
    F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
    M = mpz(2)**p - 1
    N = M // F1
    
    log('=' * 70)
    log('Extended LLRF — running LL sequence past step p-2')
    log(f'  Target: M({p})/F1, {len(str(N))} digits')
    log(f'  Max steps: 4*p = {4*p}')
    log('=' * 70)
    
    if is_prime(N):
        log('N is already prime — done')
        return
    
    log_lines = []
    t0 = time.time()
    # Run up to 4*p steps (much longer than standard p-2)
    factor, step = llrf_extended(p, N, max_steps=4*p, log_lines=log_lines, check_interval=200)
    elapsed = time.time() - t0
    
    for line in log_lines[-30:]:
        log(line)
    log(f'  Total time: {elapsed:.1f}s, scanned {step} steps')
    
    if factor is not None:
        log(f'  >>> FACTOR FOUND at step {step}: {factor} ({len(str(factor))} digits)')
        if not is_prime(factor):
            f_int = factor
            sub = []
            for sp in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]:
                while f_int % sp == 0:
                    sub.append(sp)
                    f_int //= sp
            if f_int > 1 and is_prime(f_int):
                sub.append(f_int)
            log(f'  Composite, sub-factors: {sub}')
            smallest = min(sub) if sub else None
            if smallest is not None and smallest < int(F1):
                log(f'  Updating factors file with {smallest}')
                update_factor_file(p, smallest)
                cofactor = M // smallest
                append_complete(p, smallest, cofactor)
        else:
            if factor < int(F1):
                log(f'  Updating factors file with {factor}')
                update_factor_file(p, factor)
                cofactor = M // factor
                append_complete(p, factor, cofactor)
    else:
        log(f'  No factor found in {step} extended LL steps')
    
    # Also try on missing primes with extended LLRF
    log('')
    log('=' * 70)
    log(f'Extended LLRF on all 204 missing primes')
    log('=' * 70)
    
    missing = get_missing()
    total_found = 0
    t_start = time.time()
    
    for idx, mp in enumerate(missing, 1):
        if time.time() - t_start > 95:
            log(f'  Time budget exceeded at p={mp}')
            break
        log(f'  [{idx}/{len(missing)}] p={mp}: extended LLRF up to 4*p={4*mp}')
        t0 = time.time()
        Mp = mpz(2)**mp - 1
        log_lines_p = []
        # Run up to 2*p steps (faster)
        factor, step = llrf_extended(mp, Mp, max_steps=2*mp, log_lines=log_lines_p, check_interval=500)
        elapsed_p = time.time() - t0
        for line in log_lines_p[-5:]:
            log(line)
        log(f'    time: {elapsed_p:.2f}s, {step} steps')
        if factor is not None:
            log(f'  >>> p={mp}: FACTOR: {factor} ({len(str(factor))} digits)')
            if not is_prime(factor):
                f_int = factor
                sub = []
                for sp in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]:
                    while f_int % sp == 0:
                        sub.append(sp)
                        f_int //= sp
                if f_int > 1 and is_prime(f_int):
                    sub.append(f_int)
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
    
    elapsed_total = time.time() - t_start
    log('')
    log('=' * 70)
    log(f'Extended LLRF complete. Total {total_found} factor(s) in {elapsed_total:.1f}s')
    log('=' * 70)


if __name__ == '__main__':
    main()
