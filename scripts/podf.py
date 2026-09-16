#!/usr/bin/env python3
"""
Power-Order Discriminant Factoring (PODF) — based on the key discovery.

KEY DISCOVERY:
  For N = M(1237)/F1:
    2^(N-1) mod N = 1 (because ord_q_i(2) = p divides N-1 for each q_i | N)
    3^(N-1) mod N ≠ 1 (in general, ord_q_i(3) does NOT divide N-1 for all i)
  
  This DISCRIMINATES the factors! Some q_i have ord_q_i(3) | (N-1) and others don't.
  
ALGORITHM:
  Compute r = 3^((N-1)/p) mod N. This is a "p-th root-like" structure.
  Different q_i might give different values of r mod q_i.
  
  Specifically:
    r mod q_i = 3^((N-1)/p mod (q_i - 1)) mod q_i
            = 3^((N-1)/p mod (2 k_i p)) mod q_i
    
  (N-1)/p mod (2 k_i p) = ?
  (N-1) = (q1*q2*... * q_m) - 1
  (N-1) mod (q_i - 1) = (q_i - 1) - 1 = -1 mod (q_i - 1)? No wait, that's only if 
  q_j = q_i (circular). Let me reconsider.
  
  N = q1 * q2 * ... * q_m, so N ≡ 0 mod q_i. Thus N - 1 ≡ -1 mod q_i.
  (N-1) mod (q_i - 1) = ?
  N - 1 = q1*q2*... - 1. Mod (q_i - 1):
  q_j mod (q_i - 1) = q_j mod (q_i - 1) for j != i, and q_i ≡ 1 mod (q_i - 1).
  So N mod (q_i - 1) = (prod q_j for j != i) mod (q_i - 1).
  N - 1 mod (q_i - 1) = (prod q_j for j != i) - 1 mod (q_i - 1).
  
  For 2 factors: N - 1 mod (q_1 - 1) = q_2 - 1 mod (q_1 - 1).
  So (N-1) mod (q_1 - 1) = q_2 - 1 (if q_2 - 1 < q_1 - 1) or q_2 - 1 - (q_1 - 1) = q_2 - q_1 (otherwise).
  
  Hmm, so (N-1) mod (q_i - 1) ≠ 0 in general.

KEY NEW IDEA:
  Compute r = 3^((N-1)/p) mod N for various bases 3, 5, 7, 11, ...
  Each base a gives a different "view" of (N-1)/p exponent distribution across q_i.
  
  The CRT-structured value r = (r_1, r_2) where r_i = 3^((N-1)/p mod (q_i-1)) mod q_i.
  Different bases give different r values. If r1_base3 and r1_base5 differ mod q_1 but match mod q_2,
  gcd(r1_base3 - r1_base5, N) = q_2.
  
  Even more direct: r1 = 3^((N-1)/p) mod N, r2 = 5^((N-1)/p) mod N.
  Try gcd(r1 - r2, N), gcd(r1 * r2 - 1, N), etc.
  
  The key insight: r values from different bases might have NON-TRIVIAL GCDs with N.

ADDITIONAL INSIGHT:
  If we pick a base a such that ord_q_i(a) = p exactly (like a = 2), then a^((N-1)/p) 
  has order dividing N-1 / (N-1) = ... hmm let me think.
  
  a = 2 has order p mod q_i. So 2^k mod q_i = 2^(k mod p).
  (N-1)/p mod p = ?
  We computed (N-1) mod p = 0, so (N-1)/p is an integer.
  ((N-1)/p) mod p = ?
  Hmm, no simple form.
  
  2^((N-1)/p) mod q_i = 2^(((N-1)/p) mod p) mod q_i
  = 2^(((N-1)/p) mod p) mod q_i.
  The exponent here is the same for all q_i (since they all have 2 of order p).
  
  So 2^((N-1)/p) mod N = (2^k, 2^k) mod N for the same k. The CRT gives a unique value,
  but it's NOT of the form 2^k mod N (because CRT lifts to a different value).
  
  Wait actually: 2^((N-1)/p) mod q_1 = 2^(k1) mod q_1 (where k1 = ((N-1)/p) mod p).
  2^((N-1)/p) mod q_2 = 2^(k1) mod q_2 (same k1 since ord_q_i(2) = p).
  So 2^((N-1)/p) mod N (via CRT) = unique value R such that R ≡ 2^k1 mod q_1 AND R ≡ 2^k1 mod q_2.
  
  But 2^k1 mod q_1 ≠ 2^k1 mod q_2 in general (different residues).
  So R ≡ 2^k1 mod N? Only if 2^k1 mod q_1 = 2^k1 mod q_2 = 2^k1 (i.e., if 2^k1 < min(q_1, q_2)).
  Otherwise, 2^k1 mod q_1 and 2^k1 mod q_2 are different residues, and R is the CRT lift,
  which is NOT simply 2^k1 mod N.
  
  Hmm wait. R is the unique number in [0, N) with R ≡ 2^k1 mod q_1 and R ≡ 2^k1 mod q_2.
  If both congruences are R ≡ 2^k1 mod q_i, then R - 2^k1 ≡ 0 mod q_i for both i, 
  so R - 2^k1 ≡ 0 mod N, meaning R = 2^k1 mod N.
  
  So 2^((N-1)/p) mod N = 2^(((N-1)/p) mod p) mod N.
  This is just a power of 2 mod N, which doesn't give us new info.
  
  But for base a ≠ 2 (with ord_q_i(a) ≠ p for some i), a^((N-1)/p) mod N is a 
  "mixed" value, potentially informative.
  
  KEY: Try different bases a ∈ {3, 5, 7, 11, ...} and see if a^((N-1)/p) mod N
  reveals structure.
"""

import sys
import time
from pathlib import Path

import gmpy2
from gmpy2 import mpz, gcd, is_prime, powmod

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
LOG_FILE = BASE / 'logs/podf.log'
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
    log('Power-Order Discriminant Factoring (PODF)')
    log(f'  Target: M({p})/F1, {len(str(N))} digits')
    log(f'  Discovery: 2^(N-1) ≡ 1 mod N, but 3^(N-1) ≢ 1 mod N')
    log(f'  Strategy: use various bases a, compute a^((N-1)/p) mod N, look for discriminating GCDs')
    log('=' * 70)
    
    if is_prime(N):
        log('N is already prime — done')
        return
    
    # Compute (N-1)/p
    exp = (N - 1) // p
    log(f'(N-1)/p has {len(str(exp))} digits')
    log('')
    
    # Phase 1: Compute r_a = a^((N-1)/p) mod N for many bases a
    bases = list(range(2, 200))
    log(f'Computing r_a for {len(bases)} bases...')
    t0 = time.time()
    r_values = []
    for a in bases:
        r = powmod(a, exp, N)
        r_values.append(r)
        # Check gcd(r - 1, N) and gcd(r + 1, N)
        g = gcd(r - 1, N)
        if 1 < int(g) < int(N):
            log(f'  >>> a={a}: gcd(r-1, N) = {g} (FACTOR!)')
            if int(g) < int(F1):
                update_factor_file(p, int(g))
            return
        g = gcd(r + 1, N)
        if 1 < int(g) < int(N):
            log(f'  >>> a={a}: gcd(r+1, N) = {g} (FACTOR!)')
            if int(g) < int(F1):
                update_factor_file(p, int(g))
            return
    elapsed = time.time() - t0
    log(f'  Computed {len(r_values)} r values in {elapsed:.1f}s')
    
    # Phase 2: pairwise differences
    log('Pairwise gcd of r values...')
    t0 = time.time()
    for i in range(len(r_values)):
        for j in range(i + 1, len(r_values)):
            r1, r2 = r_values[i], r_values[j]
            g = gcd(r1 - r2, N)
            if 1 < int(g) < int(N):
                log(f'  >>> gcd(r_{i} - r_{j}, N) = {g} (FACTOR!)')
                log(f'      Bases were {bases[i]} and {bases[j]}')
                if int(g) < int(F1):
                    update_factor_file(p, int(g))
                return
            g = gcd(r1 + r2, N)
            if 1 < int(g) < int(N):
                log(f'  >>> gcd(r_{i} + r_{j}, N) = {g} (FACTOR!)')
                log(f'      Bases were {bases[i]} and {bases[j]}')
                if int(g) < int(F1):
                    update_factor_file(p, int(g))
                return
    elapsed = time.time() - t0
    log(f'  Pairwise done in {elapsed:.1f}s')
    
    # Phase 3: check r^p mod N (should be a^(N-1) mod N)
    log('')
    log('Checking r^p mod N for each base (= a^(N-1) mod N):')
    for i, (a, r) in enumerate(zip(bases, r_values)):
        r_p = powmod(r, p, N)
        a_n1 = powmod(a, N - 1, N)
        if r_p != a_n1:
            log(f'  a={a}: r^p ≠ a^(N-1) mod N. Interesting!')
        # Try gcd(r^p - 1, N) and gcd(r^p + 1, N)
        g = gcd(r_p - 1, N)
        if 1 < int(g) < int(N):
            log(f'  >>> a={a}: gcd(r^p - 1, N) = {g} (FACTOR!)')
            if int(g) < int(F1):
                update_factor_file(p, int(g))
            return
        g = gcd(r_p + 1, N)
        if 1 < int(g) < int(N):
            log(f'  >>> a={a}: gcd(r^p + 1, N) = {g} (FACTOR!)')
            if int(g) < int(F1):
                update_factor_file(p, int(g))
            return
    
    # Phase 4: try with bases that are Mersenne-related (powers of 2)
    # 2 has ord p mod q_i, so 2^k has ord p/gcd(p, k) = p (since p is prime).
    # So 2^k has ord p too. 2^k^((N-1)/p) = 2^(k * (N-1)/p) = (2^(N-1))^k / 2^k = ... 
    # Actually 2^k^((N-1)/p) mod N = 2^(k * (N-1)/p) mod N = (2^((N-1)/p))^k mod N.
    # So this is just powers of 2^((N-1)/p), which gives same info.
    
    # Try a different EXPONENT: (N-1)/2
    log('')
    log('Trying exponent (N-1)/2 with various bases:')
    exp2 = (N - 1) // 2
    for a in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]:
        r = powmod(a, exp2, N)
        # Check gcd(r-1, N), gcd(r+1, N)
        g = gcd(r - 1, N)
        if 1 < int(g) < int(N):
            log(f'  >>> a={a}: gcd(a^((N-1)/2) - 1, N) = {g} (FACTOR!)')
            if int(g) < int(F1):
                update_factor_file(p, int(g))
            return
        g = gcd(r + 1, N)
        if 1 < int(g) < int(N):
            log(f'  >>> a={a}: gcd(a^((N-1)/2) + 1, N) = {g} (FACTOR!)')
            if int(g) < int(F1):
                update_factor_file(p, int(g))
            return
    
    # Try exponent (N-1)/4
    log('Trying exponent (N-1)/4 with various bases:')
    exp4 = (N - 1) // 4
    for a in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]:
        r = powmod(a, exp4, N)
        # We expect r^4 = a^(N-1) mod N (Euler-like)
        r4 = powmod(r, 4, N)
        # Try gcd(r4 - 1, N), gcd(r4 + 1, N)
        g = gcd(r4 - 1, N)
        if 1 < int(g) < int(N):
            log(f'  >>> a={a}: gcd(a^(N-1) - 1, N) = {g} (FACTOR!)')
            if int(g) < int(F1):
                update_factor_file(p, int(g))
            return
        g = gcd(r4 + 1, N)
        if 1 < int(g) < int(N):
            log(f'  >>> a={a}: gcd(a^(N-1) + 1, N) = {g} (FACTOR!)')
            if int(g) < int(F1):
                update_factor_file(p, int(g))
            return
        # Try gcd(r-1), gcd(r+1)
        g = gcd(r - 1, N)
        if 1 < int(g) < int(N):
            log(f'  >>> a={a}: gcd(r-1, N) = {g} (FACTOR!)')
            if int(g) < int(F1):
                update_factor_file(p, int(g))
            return
        g = gcd(r + 1, N)
        if 1 < int(g) < int(N):
            log(f'  >>> a={a}: gcd(r+1, N) = {g} (FACTOR!)')
            if int(g) < int(F1):
                update_factor_file(p, int(g))
            return
        # Try gcd(r^2 - 1), gcd(r^2 + 1)
        r2 = (r * r) % N
        g = gcd(r2 - 1, N)
        if 1 < int(g) < int(N):
            log(f'  >>> a={a}: gcd(r^2 - 1, N) = {g} (FACTOR!)')
            if int(g) < int(F1):
                update_factor_file(p, int(g))
            return
        g = gcd(r2 + 1, N)
        if 1 < int(g) < int(N):
            log(f'  >>> a={a}: gcd(r^2 + 1, N) = {g} (FACTOR!)')
            if int(g) < int(F1):
                update_factor_file(p, int(g))
            return
    
    log('No factor found via PODF')


if __name__ == '__main__':
    main()
