#!/usr/bin/env python3
"""
Square-Root-of-Minus-Two Cascade (SRM2C) — based on algebraic discovery.

DISCOVERY (from analysis):
  N = M(1237)/F1 has factors q with:
    q ≡ 3 mod 8 (most likely, based on (-1/N)=+1, (2/N)=+1, sqrt(-1) and sqrt(2) don't exist)
    q is non-residue mod 1237
  
  For such q: (-2/q) = (-1/q)(2/q) = (-1)(-1) = +1, so sqrt(-2) mod q exists.
  By CRT, sqrt(-2) mod N has 2^k roots where k = # prime factors.
  
  Finding multiple roots r_1, r_2 with r_1 ≠ ± r_2 (mod N) → gcd gives factor.

ALGORITHM:
  Find sqrt(-2) mod N via:
    1. Tonelli-Shanks-style: a^((N-1)/4) gives ±sqrt(-2) when (-2/N) = +1 and 
       the appropriate a is chosen.
       Actually, if (-2/N) = +1, then r = a^((N-1)/4) for some a gives r^2 ≡ -2 mod N.
       But the existence of sqrt(-2) mod N for COMPOSITE N requires ALL prime factors
       to have (-2/q) = +1.
       
       Wait, that's the same issue as sqrt(-1). Let me re-think.
       
       If our hypothesis is that N = q1 * q2 with both q_i ≡ 3 mod 8, then:
         For each q_i: (-1/q_i) = -1, (2/q_i) = -1, so (-2/q_i) = (-1)(-1) = +1.
         So sqrt(-2) exists mod each q_i.
         By CRT, sqrt(-2) mod N exists and has 4 roots (2 per factor).
         
       So in this case, sqrt(-2) DOES exist mod N!
       
       Let's verify by trying r = a^((N-1)/4) for various a.
       For N ≡ 1 mod 4 and (-2/N) = +1: r = a^((N-1)/4) gives ±sqrt(-2) for prime N.
       For composite N: r = a^((N-1)/4) gives some value; we check r^2 mod N.
"""

import sys
import time
import random
from pathlib import Path

import gmpy2
from gmpy2 import mpz, gcd, is_prime, powmod, jacobi

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
LOG_FILE = BASE / 'logs/srm2c.log'
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


def find_sqrt_minus_two(N, n_attempts=200):
    """Try to find sqrt(-2) mod N.
    
    Use the identity: if (-2/N) = +1 and N is prime, then r = a^((N-1)/4) gives
    r^2 ≡ -2 mod N for some a (specifically, when a is a "witness" of the right type).
    
    For composite N with (-2/N) = +1: r^2 might be -1, 2, or -2, or something else.
    If r^2 ≡ -2 mod N, we found a root.
    
    Also try r = a^((N-1)/2) — should be ±1 (Euler's criterion).
    Also try more aggressive: r = a^((N-1)/2) * b^((N-1)/4) etc.
    """
    roots = set()
    attempts = 0
    while attempts < n_attempts and len(roots) < 8:
        attempts += 1
        a = mpz(random.randint(2, int(N) - 1))
        # Try a^((N-1)/4)
        r = powmod(a, (N - 1) // 4, N)
        if (r * r + 2) % N == 0:
            roots.add(int(r))
        # Try a^((N-1)/2) * 2^((N-1)/4)
        # Or other combinations
        r2 = powmod(a, (N - 1) // 2, N)
        # r2 should be ±1
        if r2 == 1 or r2 == N - 1:
            # r * r2 might give a different root
            r_combined = (r * r2) % N
            if (r_combined * r_combined + 2) % N == 0:
                roots.add(int(r_combined))
    return list(roots)


def cipolla_sqrt(N, a_val, n_attempts=50):
    """Find sqrt(a_val) mod N via Cipolla's algorithm (general a_val)."""
    roots = set()
    attempts = 0
    while attempts < n_attempts and len(roots) < 8:
        attempts += 1
        t = mpz(random.randint(2, int(N) - 1))
        d = (t * t - a_val) % N  # t^2 - a_val
        if d == 0:
            # t is a sqrt directly
            if (t * t - a_val) % N == 0:
                roots.add(int(t))
            continue
        try:
            j = jacobi(d, N)
        except:
            continue
        # Cipolla: (t + x)^((N+1)/2) in F_N[x]/(x^2 - d)
        # = r + s*x; if s == 0, r is sqrt(a_val).
        u, v = t, mpz(1)
        exp = (N + 1) // 2
        bits = bin(exp)[2:]
        cur_u, cur_v = mpz(1), mpz(0)
        for bit in bits:
            new_u = (cur_u * cur_u + d * cur_v * cur_v) % N
            new_v = (2 * cur_u * cur_v) % N
            cur_u, cur_v = new_u, new_v
            if bit == '1':
                new_u = (cur_u * t + d * cur_v) % N
                new_v = (cur_u + cur_v * t) % N
                cur_u, cur_v = new_u, new_v
        if cur_v == 0:
            r = cur_u
            if (r * r - a_val) % N == 0:
                roots.add(int(r))
    return list(roots)


def main():
    p = 1237
    F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
    M = mpz(2)**p - 1
    N = M // F1
    
    log('=' * 70)
    log('Square-Root-of-Minus-Two Cascade (SRM2C) — based on algebraic discovery')
    log(f'  Target: M({p})/F1, {len(str(N))} digits')
    log(f'  Discovery: factors likely q ≡ 3 mod 8, so (-2/q) = +1, sqrt(-2) exists')
    log('=' * 70)
    
    # Verify (-2/N)
    log(f'(-2/N) = {jacobi(-2, N)}')
    log(f'(2/N) = {jacobi(2, N)}')
    log(f'(-1/N) = {jacobi(-1, N)}')
    log(f'(5/N) = {jacobi(5, N)}  [was -1, suggests (5/q_i) structure]')
    
    if is_prime(N):
        log('N is already prime — done')
        return
    
    # Find sqrt(-2) via a^((N-1)/4)
    log('')
    log('Method 1: a^((N-1)/4) approach')
    t0 = time.time()
    roots1 = find_sqrt_minus_two(N, n_attempts=500)
    elapsed = time.time() - t0
    log(f'  Found {len(roots1)} root(s) of -2 mod N in {elapsed:.1f}s')
    for r in roots1[:8]:
        log(f'    r = {r} ({len(str(r))} digits)')
        log(f'    r^2 + 2 mod N = {(mpz(r)*mpz(r)+2) % N}')
    
    # Method 2: Cipolla
    log('')
    log('Method 2: Cipolla for sqrt(-2)')
    t0 = time.time()
    roots2 = cipolla_sqrt(N, -2, n_attempts=200)
    elapsed = time.time() - t0
    log(f'  Found {len(roots2)} root(s) in {elapsed:.1f}s')
    for r in roots2[:8]:
        log(f'    r = {r}')
    
    all_roots = list(set(roots1 + roots2))
    log('')
    log(f'  Total unique sqrt(-2) roots: {len(all_roots)}')
    
    if len(all_roots) >= 2:
        log('  Trying pairwise gcd...')
        factor_found = None
        for i in range(len(all_roots)):
            for j in range(i + 1, len(all_roots)):
                r1, r2 = all_roots[i], all_roots[j]
                g = gcd(r1 - r2, N)
                if 1 < int(g) < int(N):
                    log(f'  >>> gcd(r_{i} - r_{j}, N) = {g} (FACTOR!)')
                    factor_found = int(g)
                    break
                g = gcd(r1 + r2, N)
                if 1 < int(g) < int(N):
                    log(f'  >>> gcd(r_{i} + r_{j}, N) = {g} (FACTOR!)')
                    factor_found = int(g)
                    break
            if factor_found:
                break
        
        if factor_found:
            log(f'  FACTOR FOUND: {factor_found} ({len(str(factor_found))} digits)')
            if not is_prime(factor_found):
                f_int = factor_found
                sub = []
                for sp in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]:
                    while f_int % sp == 0:
                        sub.append(sp)
                        f_int //= sp
                if f_int > 1 and is_prime(f_int):
                    sub.append(f_int)
                log(f'  Composite, sub: {sub}')
                smallest = min(sub) if sub else None
                if smallest is not None and smallest < int(F1):
                    update_factor_file(p, smallest)
                    cofactor = M // smallest
                    append_complete(p, smallest, cofactor)
                    log(f'  Updated factors file with {smallest}')
            else:
                if factor_found < int(F1):
                    update_factor_file(p, factor_found)
                    cofactor = M // factor_found
                    append_complete(p, factor_found, cofactor)
                    log(f'  Updated factors file with {factor_found}')
        else:
            log('  No factor found from pairwise gcd of sqrt(-2) roots')
    else:
        log('  Less than 2 roots — cannot factor via this method')


if __name__ == '__main__':
    main()
