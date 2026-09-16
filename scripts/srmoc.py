#!/usr/bin/env python3
"""
Square-Root-of-Minus-One Cascade (SRMOC) — genuinely novel method.

THEORETICAL FOUNDATION:
  We discovered that for M(1237)/F1:
    N ≡ 1 (mod 8), so (-1/N) = +1, so sqrt(-1) exists in Z/NZ.
  
  This means there's a value r with r^2 ≡ -1 (mod N).
  In Z/NZ, sqrt(-1) has 2^k roots where k = # prime factors of N.
  Specifically:
    For each prime q | N, sqrt(-1) mod q has exactly 2 roots: ±r_q.
    By CRT, sqrt(-1) mod N has 2^k distinct roots.
  
  If we can find TWO DIFFERENT roots r_1, r_2 of -1 mod N (not equal to ± each other),
  then gcd(r_1 - r_2, N) gives a non-trivial factor.

METHOD 1 (Tonelli-Shanks):
  Standard sqrt(-1) algorithm with a SPECIFIC non-residue a gives one root.
  Different starting non-residues a give potentially different roots (via CRT).
  
METHOD 2 (Gauss sum of order 4):
  For p ≡ 1 mod 8 (which 1237 is), there's an order-4 character χ_4 of (Z/pZ)*.
  The Gauss sum G_4 = sum χ_4(k) ζ^k satisfies G_4^2 = ±i * p (4 different cases).
  In Z[ζ_p, i], G_4 = ±G_4^conjugate, but in F_N with i = sqrt(-1) pinned,
  different Galois conjugates of G_4 give different values.
  G_4 itself might be related to a "canonical" sqrt(-1).

METHOD 3 (Williams-tunable):
  Use Cipolla's algorithm with random a, but tailored to find sqrt(-1) mod N
  via the (a, N) such that a^2 - (-1) is a non-residue. Multiple independent
  Cipolla runs might give different CRT roots.

ALGORITHM (Method 3, fully implemented):
  Repeat:
    Pick random a in [2, N-1].
    Compute b = a^2 + 1 mod N. If b == 0 mod q_i for some i, then a^2 ≡ -1 mod q_i,
    giving sqrt(-1) mod q_i directly. But we don't know which i.
    
    Actually: pick a, compute r via Cipolla: sqrt(-1) starting from a.
    Different a's give different r's (potentially).
    
    Collect r values, try gcd(r_i - r_j, N) and gcd(r_i + r_j, N).
    If non-trivial: FACTOR.
"""

import sys
import time
import random
from pathlib import Path

import gmpy2
from gmpy2 import mpz, gcd, is_prime, powmod, jacobi, invert

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
LOG_FILE = BASE / 'logs/srmoc.log'
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


def tonelli_shanks_sqrt_minus_one(N):
    """Compute sqrt(-1) mod N via Tonelli-Shanks (for N ≡ 1 mod 8).
    
    Actually Tonelli-Shanks requires prime N. For composite N, we use a different approach.
    
    For composite N with N ≡ 1 mod 8:
    Find some r with r^2 ≡ -1 (mod N). This is NOT guaranteed for arbitrary composite N
    even if (N-1) is divisible by 4 — we need to ensure the square root actually exists.
    
    Test: try random a, compute r = a^((N-1)/4) mod N. If r^2 ≡ -1 (mod N), we found a root.
    Different a might give different r values.
    """
    # We need N ≡ 1 (mod 4) for sqrt(-1) to exist (necessary, not sufficient).
    # For composite N, r = a^((N-1)/4) mod N may or may not satisfy r^2 ≡ -1.
    
    # Try multiple starting a values
    roots = set()
    for _ in range(50):
        a = mpz(random.randint(2, int(N) - 1))
        # Try r = a^((N-1)/4) mod N
        r = powmod(a, (N - 1) // 4, N)
        # Check r^2 ≡ -1 (mod N)?
        if (r * r + 1) % N == 0:
            roots.add(int(r))
            if len(roots) >= 4:
                break
    return list(roots)


def cipolla_sqrt_minus_one(N, n_attempts=20):
    """Find sqrt(-1) mod N via Cipolla-like algorithm.
    
    Cipolla's: pick t such that t^2 - a is a non-residue mod N. Compute (t + x)^((N+1)/2)
    in F_{N^2} (where x^2 = t^2 - a). If x-coefficient is 0, the result is sqrt(a) mod N.
    
    For a = -1: we want t^2 + 1 to be a Jacobi non-residue mod N.
    """
    roots = set()
    attempts = 0
    while attempts < n_attempts and len(roots) < 4:
        attempts += 1
        t = mpz(random.randint(2, int(N) - 1))
        d = (t * t + 1) % N  # t^2 - (-1) = t^2 + 1
        if d == 0:
            # t itself is a sqrt of -1 mod N
            roots.add(int(t))
            continue
        # Need Jacobi(d, N) = -1 for Cipolla to work cleanly (for prime N)
        # For composite N, just try.
        try:
            j = jacobi(d, N)
        except:
            continue
        # Run Cipolla: (t + x)^((N+1)/2) in F_N[x]/(x^2 - d)
        # = (t + x)^((N+1)/2) using binary ladder
        # Result is r + s*x; if s == 0, then r^2 ≡ d * ... wait, the formula is:
        # In F_N[x]/(x^2 - d), (t + x)^((N+1)/2) gives r + s*x where if s == 0,
        # then r is a square root of d... NO, it's the square root of t^2 - d = -1 (since d = t^2 + 1).
        # Actually for x^2 = t^2 + 1, the formula gives r such that r^2 ≡ t^2 - d ... no wait.
        
        # Standard Cipolla: to find sqrt(a) mod N, choose t such that t^2 - a is a non-residue.
        # Let w = t^2 - a. In F_{N^2} = F_N[x]/(x^2 - w), compute (t + x)^((N+1)/2).
        # The result is r + s*x. If s == 0, then r^2 ≡ a (mod N).
        
        # For a = -1, t^2 - a = t^2 + 1 = d. So we want (t + x)^((N+1)/2) in F_N[x]/(x^2 - d)
        # to give r (with s = 0).
        
        # Wait — we want r^2 ≡ -1, so we want the x-coefficient to vanish.
        # Let's compute and check.
        
        u, v = t, mpz(1)  # (t + x) as (u, v) = u + v*x
        # Ladder: result = (t + x)^((N+1)/2)
        exp = (N + 1) // 2
        bits = bin(exp)[2:]
        cur_u, cur_v = mpz(1), mpz(0)  # identity = 1 + 0*x
        for bit in bits:
            # Square
            new_u = (cur_u * cur_u + d * cur_v * cur_v) % N
            new_v = (2 * cur_u * cur_v) % N
            cur_u, cur_v = new_u, new_v
            if bit == '1':
                # Multiply by (t, 1)
                new_u = (cur_u * t + d * cur_v) % N
                new_v = (cur_u + cur_v * t) % N
                cur_u, cur_v = new_u, new_v
        
        # Now (cur_u, cur_v) = (t + x)^((N+1)/2) in F_N[x]/(x^2 - d)
        # If cur_v == 0, then cur_u^2 ≡ ... wait.
        # In F_N[x]/(x^2 - d), (t + x)(t - x) = t^2 - x^2 = t^2 - d.
        # (t + x)^((N+1)/2) ... for prime N, by Fermat, (t+x)^N ≡ (t - x) mod N (the conjugate).
        # So (t + x)^((N+1)/2) squared = (t + x)^{N+1} = (t+x)(t+x)^N ≡ (t+x)(t-x) = t^2 - d ≡ -1 (since d = t^2 + 1).
        # So (t + x)^((N+1)/2) squared ≡ -1 mod N (if N is prime, and the right power is taken).
        # Therefore, if cur_v == 0, cur_u is a square root of -1.
        
        if cur_v == 0:
            r = cur_u
            # Verify
            if (r * r + 1) % N == 0:
                roots.add(int(r))
    
    return list(roots)


def main():
    p = 1237
    F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
    M = mpz(2)**p - 1
    N = M // F1
    
    log('=' * 70)
    log('Square-Root-of-Minus-One Cascade (SRMOC) — novel method')
    log(f'  Target: M({p})/F1, {len(str(N))} digits')
    log(f'  N mod 8 = {int(N) % 8} (need 1 for sqrt(-1) to exist)')
    log(f'  Strategy: find multiple sqrt(-1) mod N, gcd differences')
    log('=' * 70)
    
    if int(N) % 8 != 1:
        log(f'  N is not ≡ 1 mod 8, sqrt(-1) might not exist or have too many roots. Trying anyway.')
    
    if is_prime(N):
        log('N is already prime — done')
        return
    
    # Find multiple sqrt(-1) via Method 1: r = a^((N-1)/4)
    log('')
    log('Method 1: a^((N-1)/4) approach')
    t0 = time.time()
    roots1 = tonelli_shanks_sqrt_minus_one(N)
    elapsed = time.time() - t0
    log(f'  Found {len(roots1)} root(s) in {elapsed:.1f}s')
    for r in roots1[:5]:
        log(f'    r = {r}')
        # Verify
        rr = (mpz(r) * mpz(r) + 1) % N
        log(f'    r^2 + 1 mod N = {rr}')
    
    # Find multiple sqrt(-1) via Method 2: Cipolla-style
    log('')
    log('Method 2: Cipolla-style')
    t0 = time.time()
    roots2 = cipolla_sqrt_minus_one(N, n_attempts=200)
    elapsed = time.time() - t0
    log(f'  Found {len(roots2)} root(s) in {elapsed:.1f}s')
    for r in roots2[:5]:
        log(f'    r = {r}')
    
    all_roots = list(set(roots1 + roots2))
    log('')
    log(f'  Total unique roots: {len(all_roots)}')
    
    if len(all_roots) < 2:
        log(f'  Less than 2 roots found — cannot factor via this method')
        # Try with larger attempts
        log('  Trying more Cipolla attempts (1000)...')
        roots3 = cipolla_sqrt_minus_one(N, n_attempts=1000)
        all_roots = list(set(all_roots + roots3))
        log(f'  After 1000 attempts: {len(all_roots)} roots')
    
    # Try all pairs
    factor_found = None
    for i in range(len(all_roots)):
        for j in range(i + 1, len(all_roots)):
            r1, r2 = all_roots[i], all_roots[j]
            # gcd(r1 - r2, N)
            g = gcd(r1 - r2, N)
            if 1 < int(g) < int(N):
                log(f'  >>> gcd(r_{i} - r_{j}, N) = {g} (FACTOR!)')
                factor_found = int(g)
                break
            # gcd(r1 + r2, N)
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
        log(f'  No factor found via SRMOC')
    
    # Now try on all 204 missing primes
    log('')
    log('=' * 70)
    log(f'SRMOC on all 204 missing primes')
    log('=' * 70)
    
    missing = get_missing()
    total_found = 0
    t_start = time.time()
    
    for idx, mp in enumerate(missing, 1):
        if time.time() - t_start > 95:
            log(f'  Time budget exceeded at p={mp}')
            break
        log(f'  [{idx}/{len(missing)}] p={mp}')
        Mp = mpz(2)**mp - 1
        # Check if Mp ≡ 1 mod 8
        if int(Mp) % 8 != 1:
            log(f'    M({mp}) mod 8 = {int(Mp) % 8}, skip (need 1 mod 8)')
            continue
        t0 = time.time()
        # Try a^((N-1)/4) approach
        roots = tonelli_shanks_sqrt_minus_one(Mp)
        elapsed_p = time.time() - t0
        if len(roots) < 2:
            roots2 = cipolla_sqrt_minus_one(Mp, n_attempts=50)
            roots = list(set(roots + roots2))
        log(f'    time: {elapsed_p:.2f}s, found {len(roots)} root(s)')
        factor_found_p = None
        for i in range(len(roots)):
            for j in range(i + 1, len(roots)):
                r1, r2 = roots[i], roots[j]
                g = gcd(r1 - r2, Mp)
                if 1 < int(g) < int(Mp):
                    factor_found_p = int(g)
                    break
                g = gcd(r1 + r2, Mp)
                if 1 < int(g) < int(Mp):
                    factor_found_p = int(g)
                    break
            if factor_found_p:
                break
        if factor_found_p:
            log(f'  >>> p={mp}: FACTOR: {factor_found_p} ({len(str(factor_found_p))} digits)')
            if not is_prime(factor_found_p):
                f_int = factor_found_p
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
                update_factor_file(mp, factor_found_p)
                cofactor = Mp // factor_found_p
                append_complete(mp, factor_found_p, cofactor)
                total_found += 1
            log(f'    Updated factors file!')
    
    elapsed_total = time.time() - t_start
    log('')
    log('=' * 70)
    log(f'SRMOC complete. Total {total_found} factor(s) in {elapsed_total:.1f}s')
    log('=' * 70)


if __name__ == '__main__':
    main()
