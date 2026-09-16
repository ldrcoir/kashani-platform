#!/usr/bin/env python3
"""
Residue Diffusion Factoring (RDF) — a genuinely novel method.

DISCOVERY (from earlier analysis):
  For N = M(1237)/F1:
    a^((N-1)/2) mod N is never ±1.
    a^(N-1) mod N is never 1.
  This means N has very specific algebraic structure.

NOVEL IDEA:
  For N = q1 * q2 (assumed), a^(N-1) mod N = (a^(N-1) mod q1, a^(N-1) mod q2) via CRT.
  a^(N-1) mod q1 = a^((N-1) mod (q1-1)) mod q1.
  Let e1 = (N-1) mod (q1-1) and e2 = (N-1) mod (q2-1).
  By Fermat: e1 < q1-1, e2 < q2-1.
  
  For random a, a^e1 mod q1 and a^e2 mod q2 are essentially random values in F_q1*, F_q2*.
  
  The CRT value r_a is a "random" element of Z/NZ (specifically, in the 
  image of the map a -> a^(N-1) mod N).
  
  If we collect MANY r_a values, we can try to extract structure:
    - Pairwise gcd: gcd(r_a - r_b, N) — if r_a ≡ r_b mod q1 but not mod q2, this gives q1.
    - Cross-combination: gcd(r_a * r_b - 1, N), gcd(r_a * r_b + 1, N), etc.

ALGORITHM:
  Generate many r_a values for random a.
  Try pairwise gcd differences (and other combinations).
  If any non-trivial gcd: factor found!
  
COST:
  Each r_a computation: O(log N) modular mults ~ 1ms.
  1000 values: ~1 sec.
  Pairwise gcd: 1000 * 1000 = 10^6 operations, but gcd is fast.

REALISTIC EXPECTATION:
  Probability of finding factor via pairwise gcd is low (similar to random).
  But we can try a structured approach: hash r_a values to buckets by some
  property, and look for collisions within buckets.
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
LOG_FILE = BASE / 'logs/rdf.log'
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


def main():
    p = 1237
    F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
    M = mpz(2)**p - 1
    N = M // F1
    
    log('=' * 70)
    log('Residue Diffusion Factoring (RDF)')
    log(f'  Target: M({p})/F1, {len(str(N))} digits')
    log(f'  Algorithm: collect many r_a = a^(N-1) mod N for random a,')
    log(f'    try pairwise gcd to find factor.')
    log('=' * 70)
    
    if is_prime(N):
        log('N is already prime — done')
        return
    
    # Phase 1: collect many r_a values
    t0 = time.time()
    n_witnesses = 200
    log(f'Collecting {n_witnesses} witness values r_a = a^(N-1) mod N...')
    r_values = []
    for _ in range(n_witnesses):
        a = mpz(random.randint(2, int(N) - 1))
        # Make sure gcd(a, N) = 1
        if gcd(a, N) > 1 and gcd(a, N) < N:
            log(f'  Direct factor: gcd(a, N) = {gcd(a, N)}')
            return
        r = powmod(a, N - 1, N)
        r_values.append(r)
    elapsed = time.time() - t0
    log(f'  Collected {len(r_values)} values in {elapsed:.1f}s')
    
    # Phase 2: try pairwise gcd(r_a - r_b, N) and gcd(r_a + r_b, N)
    log('Trying pairwise gcd differences...')
    t0 = time.time()
    factor_found = None
    for i in range(len(r_values)):
        for j in range(i + 1, len(r_values)):
            r1, r2 = r_values[i], r_values[j]
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
    elapsed = time.time() - t0
    log(f'  Pairwise done in {elapsed:.1f}s')
    
    if factor_found:
        log(f'  FACTOR FOUND: {factor_found}')
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
        else:
            if factor_found < int(F1):
                update_factor_file(p, factor_found)
        return
    
    # Phase 3: try gcd(r_a * r_b - 1, N) — "multiplicative" difference
    log('Trying multiplicative combinations gcd(r_a * r_b - 1, N)...')
    t0 = time.time()
    factor_found = None
    for i in range(len(r_values)):
        for j in range(i + 1, min(i + 50, len(r_values))):  # Limit to nearby pairs for speed
            r1, r2 = r_values[i], r_values[j]
            g = gcd(r1 * r2 - 1, N)
            if 1 < int(g) < int(N):
                log(f'  >>> gcd(r_{i} * r_{j} - 1, N) = {g} (FACTOR!)')
                factor_found = int(g)
                break
            g = gcd(r1 * r2 + 1, N)
            if 1 < int(g) < int(N):
                log(f'  >>> gcd(r_{i} * r_{j} + 1, N) = {g} (FACTOR!)')
                factor_found = int(g)
                break
        if factor_found:
            break
    elapsed = time.time() - t0
    log(f'  Multiplicative done in {elapsed:.1f}s')
    
    if factor_found:
        log(f'  FACTOR FOUND: {factor_found}')
        return
    
    # Phase 4: hash-based collision detection
    # Hash each r_a to a small bucket, look for collisions
    log('Hash-based collision detection...')
    log('  Hash = (r mod small_prime), check for collisions in same bucket.')
    
    for hash_mod in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]:
        buckets = {}
        for i, r in enumerate(r_values):
            key = int(r) % hash_mod
            if key in buckets:
                # Collision! Try gcd with previous r in same bucket
                for j in buckets[key]:
                    g = gcd(r - r_values[j], N)
                    if 1 < int(g) < int(N):
                        log(f'  >>> Collision in bucket mod {hash_mod}: gcd = {g}')
                        log(f'      FACTOR FOUND: {g}')
                        if int(g) < int(F1):
                            update_factor_file(p, int(g))
                        return
                buckets[key].append(i)
            else:
                buckets[key] = [i]
    log('  No collision-based factor found')
    
    # Phase 5: use different exponents
    log('Trying with different exponent: a^((N-1)/2) mod N:')
    r_half = []
    for _ in range(200):
        a = mpz(random.randint(2, int(N) - 1))
        r = powmod(a, (N - 1) // 2, N)
        r_half.append(r)
    
    log('Pairwise gcd on r_half:')
    for i in range(len(r_half)):
        for j in range(i + 1, len(r_half)):
            r1, r2 = r_half[i], r_half[j]
            g = gcd(r1 - r2, N)
            if 1 < int(g) < int(N):
                log(f'  >>> gcd(r_half_{i} - r_half_{j}, N) = {g}')
                log(f'      FACTOR FOUND: {g}')
                if int(g) < int(F1):
                    update_factor_file(p, int(g))
                return
            g = gcd(r1 + r2, N)
            if 1 < int(g) < int(N):
                log(f'  >>> gcd(r_half_{i} + r_half_{j}, N) = {g}')
                if int(g) < int(F1):
                    update_factor_file(p, int(g))
                return
    
    log('No factor found via RDF')


if __name__ == '__main__':
    main()
