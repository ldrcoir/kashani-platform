#!/usr/bin/env python3
"""
Mersenne-Invariant Discriminant Method (MIDM) — yet another novel approach.

KEY INSIGHT:
  For N = M(p)/F1 (Mersenne composite cofactor), we have:
    - ord_q(2) = p for each q | N.
    - 2 generates a cyclic subgroup of order p in F_q*.
    - The complement has size (q-1)/p = 2k.
  
  Now, since q_i - 1 = 2 k_i p, we can write k_i = (q_i - 1) / (2p).
  The value k_i is unique to each q_i.
  
  Consider elements a = 2^j for j = 0, 1, ..., p-1. These are p-th roots of unity.
  In Z/NZ, a = 2^j is a single value (well-defined since 2^p ≡ 1 mod N).
  So the p-th roots of unity in Z/NZ are {2^0, 2^1, ..., 2^(p-1)}.
  
  But via CRT, 2^j mod q_1 and 2^j mod q_2 are different residues (in general).
  The CRT-lifted value 2^j mod N is a unique number, but it represents
  (2^j mod q_1, 2^j mod q_2) — TWO different residues.
  
NEW IDEA: Use MODULAR SUMS of p-th roots of unity.
  For each q_i, the sum S_j = sum_{j=0}^{p-1} (2^j)^k = sum (2^k)^j 
  equals (2^(kp) - 1) / (2^k - 1) mod q_i.
  
  For k = 0: S_0 = p (sum of 1's).
  For k != 0 mod p: S_k = 0 mod q_i (since 2^(kp) = 1 mod q_i, but 2^k != 1 mod q_i,
                  so (2^(kp) - 1) / (2^k - 1) = 0/0... wait, that's undefined).
  
  Actually, sum_{j=0}^{p-1} z^j = (z^p - 1)/(z - 1). For z = 2^k with k not divisible by p:
  z^p = 2^(kp) = (2^p)^k = 1^k = 1 mod q_i. So z^p - 1 = 0 mod q_i.
  But z != 1 mod q_i (since ord_q_i(2) = p and k not div by p).
  So sum = 0 mod q_i.
  
  For k = 0: sum = p mod q_i.
  
  So the sum is either 0 or p mod each q_i. Not discriminating.
  
NEW IDEA 2: Use power sums of p-th roots.
  sum (2^j)^k for k=1, ..., p-1. These are "Newton power sums" of the p-th roots of unity.
  Newton's identities relate these to elementary symmetric polynomials.
  For p-th roots of unity, the elementary symmetric polynomials are all 0 (except the product = 1).
  So power sums are 0 for k = 1, ..., p-1.
  Again not discriminating.
  
NEW IDEA 3: Try the SUM over a non-trivial subset.
  Consider the QUADRATIC RESIDUES mod p (where p ≡ 1 mod 4):
  S = sum_{j in QR mod p} 2^j mod N.
  By Gauss sum theory: S^2 ≡ p mod q_i (or -p mod q_i, depending on QR/NR choice).
  
  Wait — this is exactly the GAUSS SUM method I tried earlier!
  And we found that S values from different "views" (different ζ = 2^k) were just ± each other
  (since Galois action on quadratic character only has sign change).
  
  So Gauss sum approach is exhausted.
  
NEW IDEA 4: Try cubic or quartic Gauss sums.
  p = 1237. p - 1 = 1236 = 4 * 3 * 103.
  Characters of order 3 and 4 exist on (Z/pZ)*.
  
  For a quartic (order-4) character χ_4 of (Z/pZ)*:
    G_4(ζ) = sum χ_4(j) ζ^j
  G_4^4 = something related to p^2 and Jacobi sums.
  G_4 has FOUR distinct Galois conjugates (related by i = sqrt(-1)).
  But we don't have sqrt(-1) mod N (we discovered this).
  
  So quartic Gauss sums don't factor N for our case.
  
  For a cubic (order-3) character χ_3 of (Z/pZ)*:
    G_3(ζ) = sum χ_3(j) ζ^j
  G_3^3 = something. Has 3 conjugates.
  
  For p ≡ 1 mod 3: p - 1 divisible by 3. 1237 - 1 = 1236 = 4 * 3 * 103, so yes divisible by 3.
  
  Let me compute cubic Gauss sums and see if they distinguish the factors.

NEW IDEA 5: Use MULTIPLICATIVE COMBINATIONS instead of single values.
  Compute many r_a = a^((N-1)/p) mod N for various a.
  Then try gcd(r_a1 * r_a2 * r_a3 ... - r_b1 * r_b2 * ... , N) for various subsets.
  Statistically, this might hit a non-trivial gcd.
  
  But this is essentially "random search", which we know is unlikely to work.

NEW IDEA 6 (NOVEL, NO LITERATURE): Use PRODUCTS of Mersenne-related elements.
  For each prime q | N, define ω_q = 2 mod q (a primitive p-th root of unity).
  The order of ω_q in F_q is p. The COFACTOR group has order 2k.
  
  Find elements x ∈ F_q* with x = ω_q^a * c^b where c is a generator of the cofactor.
  These x's have order lcm(ord(ω_q^a), ord(c^b)).
  Different q_i might have different cofactor structure, so different c.
  
  We can't directly access ω_q^a * c^b without knowing q.
  
  But we CAN compute (2^a) * (g^b) mod N for any g we choose.
  If g has order 2k_i mod q_i (e.g., g = 3 with appropriate choice), then 
  (2^a) * (g^b) mod q_i = ω_q_i^a * (g^b mod q_i).
  
  In particular, for b = (q-1)/2k_i = p... hmm we don't know q or k_i.

NEW IDEA 7 (NOVEL): Use PRODUCTS of powers of 2 to extract cofactor info.
  Specifically: 2^a / 2^b mod N = 2^(a-b) mod N.
  The p-th root of unity set is closed under this.
  
  But 2^a * 3^b mod N is a "mixed" element, which might have interesting behavior.
  
  Try: 2^a * 3^b mod N for various a, b. Check gcd((2^a * 3^b)^p - 1, N).
  (2^a * 3^b)^p = 2^(ap) * 3^(bp) mod N.
  mod q_i: 2^(ap) = 1 (since ord = p), so (2^a * 3^b)^p = 3^(bp) mod q_i.
  
  If we choose b such that 3^(bp) mod q_i differs across q_i, we might get a factor.
  3^(bp) mod q_i has order (q_i - 1) / gcd(q_i - 1, bp) = 2k_i p / gcd(2k_i p, bp).
  For this to be 1 mod q_1 but not q_2: gcd(2k_1 p, bp) | ord_q_1(3).
  Complex.
"""

import sys
import time
from pathlib import Path

import gmpy2
from gmpy2 import mpz, gcd, is_prime, powmod

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
LOG_FILE = BASE / 'logs/midm.log'
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
    log('Mersenne-Invariant Discriminant Method (MIDM)')
    log(f'  Target: M({p})/F1, {len(str(N))} digits')
    log(f'  Try: (2^a * 3^b)^p mod N for various a, b; check gcd.')
    log('=' * 70)
    
    if is_prime(N):
        log('N is already prime — done')
        return
    
    # (2^a * 3^b)^p mod N = 2^(ap) * 3^(bp) mod N = 1 * 3^(bp) mod N (since 2^p = 1)
    # So we're essentially computing 3^(bp) mod N for various b.
    # Then check gcd(3^(bp) - 1, N) and gcd(3^(bp) + 1, N).
    
    # If 3 has order 2k_i * p in F_{q_i}* (e.g., if 3 is a primitive root mod q_i):
    #   3^(bp) mod q_i = 3^(bp mod (q_i - 1)) mod q_i = 3^(bp mod 2k_i p) mod q_i.
    #   For 3^(bp) ≡ 1 mod q_i: bp divisible by 2k_i p, i.e., b divisible by 2k_i.
    #   For 3^(bp) ≡ 1 mod q_j: b divisible by 2k_j.
    #   If 2k_i and 2k_j are different, choosing b = lcm or specific value gives a factor.
    
    # Different b values give different "tests" of the cofactor structure.
    # Try b = 1, 2, 3, ..., 10000 and check gcd(3^(bp) - 1, N).
    
    log('Trying b = 1, 2, ..., 1000:')
    t0 = time.time()
    found = False
    # Precompute 3^p mod N, then iterate powers
    base_p = powmod(3, p, N)
    cur = base_p  # 3^(1*p) mod N
    for b in range(1, 1001):
        # Check gcd(cur - 1, N) and gcd(cur + 1, N)
        g1 = gcd(cur - 1, N)
        if 1 < int(g1) < int(N):
            log(f'  >>> b={b}: gcd(3^(bp) - 1, N) = {g1} (FACTOR!)')
            log(f'      FACTOR FOUND: {g1} ({len(str(g1))} digits)')
            if int(g1) < int(F1):
                update_factor_file(p, int(g1))
            found = True
            break
        g2 = gcd(cur + 1, N)
        if 1 < int(g2) < int(N):
            log(f'  >>> b={b}: gcd(3^(bp) + 1, N) = {g2} (FACTOR!)')
            log(f'      FACTOR FOUND: {g2} ({len(str(g2))} digits)')
            if int(g2) < int(F1):
                update_factor_file(p, int(g2))
            found = True
            break
        cur = (cur * base_p) % N
    
    elapsed = time.time() - t0
    log(f'  Done b=1..1000 in {elapsed:.1f}s')
    
    if found:
        return
    
    # Try other bases
    log('')
    log('Trying with base 5 instead of 3:')
    base_p = powmod(5, p, N)
    cur = base_p
    for b in range(1, 1001):
        g1 = gcd(cur - 1, N)
        if 1 < int(g1) < int(N):
            log(f'  >>> b={b}: gcd(5^(bp) - 1, N) = {g1} (FACTOR!)')
            if int(g1) < int(F1):
                update_factor_file(p, int(g1))
            return
        g2 = gcd(cur + 1, N)
        if 1 < int(g2) < int(N):
            log(f'  >>> b={b}: gcd(5^(bp) + 1, N) = {g2} (FACTOR!)')
            if int(g2) < int(F1):
                update_factor_file(p, int(g2))
            return
        cur = (cur * base_p) % N
    log('  No factor with base 5')
    
    # Try with base 7
    log('Trying with base 7:')
    base_p = powmod(7, p, N)
    cur = base_p
    for b in range(1, 1001):
        g1 = gcd(cur - 1, N)
        if 1 < int(g1) < int(N):
            log(f'  >>> b={b}: gcd(7^(bp) - 1, N) = {g1} (FACTOR!)')
            if int(g1) < int(F1):
                update_factor_file(p, int(g1))
            return
        g2 = gcd(cur + 1, N)
        if 1 < int(g2) < int(N):
            log(f'  >>> b={b}: gcd(7^(bp) + 1, N) = {g2} (FACTOR!)')
            if int(g2) < int(F1):
                update_factor_file(p, int(g2))
            return
        cur = (cur * base_p) % N
    log('  No factor with base 7')
    
    # Try with bases up to 100, but smaller b range
    log('Trying bases 11, 13, ..., 97 with b up to 200:')
    for base in [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]:
        base_p = powmod(base, p, N)
        cur = base_p
        for b in range(1, 201):
            g1 = gcd(cur - 1, N)
            if 1 < int(g1) < int(N):
                log(f'  >>> base={base}, b={b}: gcd = {g1} (FACTOR!)')
                if int(g1) < int(F1):
                    update_factor_file(p, int(g1))
                return
            g2 = gcd(cur + 1, N)
            if 1 < int(g2) < int(N):
                log(f'  >>> base={base}, b={b}: gcd = {g2} (FACTOR!)')
                if int(g2) < int(F1):
                    update_factor_file(p, int(g2))
                return
            cur = (cur * base_p) % N
    log('  No factor found with bases up to 97')
    
    # P-1 style: also try a^(b * 2p), a^(b * 4p), etc.
    log('')
    log('Trying powers of 2*p:')
    for base in [3, 5, 7]:
        base_2p = powmod(base, 2 * p, N)
        cur = base_2p
        for b in range(1, 2001):
            g1 = gcd(cur - 1, N)
            if 1 < int(g1) < int(N):
                log(f'  >>> base={base}, b={b}: gcd(3^(2b*p) - 1, N) = {g1} (FACTOR!)')
                if int(g1) < int(F1):
                    update_factor_file(p, int(g1))
                return
            g2 = gcd(cur + 1, N)
            if 1 < int(g2) < int(N):
                log(f'  >>> base={base}, b={b}: gcd = {g2} (FACTOR!)')
                if int(g2) < int(F1):
                    update_factor_file(p, int(g2))
                return
            cur = (cur * base_2p) % N
    log('  No factor with 2*p multiplier')
    
    log('No factor found via MIDM')


if __name__ == '__main__':
    main()
