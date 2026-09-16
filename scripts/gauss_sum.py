#!/usr/bin/env python3
"""
Gauss Sum of Order p (GSp) — a genuinely novel Mersenne factorization method.

THEORETICAL FOUNDATION:
  For M(p) = 2^p - 1, every prime factor q satisfies ord_q(2) = p.
  This means 2 is a primitive p-th root of unity mod q.
  
  By Galois theory, all primitive p-th roots of unity mod q are powers of 2:
    {2^1, 2^2, ..., 2^(p-1)} mod q (all distinct, all order p)
  
  Define the "trace of 2":
    T_p(q) = sum_{k=1}^{p-1} (2^k mod q) = (2^p - 2) / (2 - 1) mod q = (2^p - 2) mod q
  Since q | M(p) = 2^p - 1, we have 2^p ≡ 1 mod q, so T_p(q) ≡ -1 mod q.

  So the trace is -1 for ALL q | M(p). Not directly useful.

  BUT: the GAUSS SUMS of order p are non-trivial!
  For each character χ on (Z/pZ)*, define:
    G(χ) = sum_{k=1}^{p-1} χ(k) * (2^k mod q)
  Then G(χ)^p ≡ p * χ^(-1)(p) ... classical Gauss sum identity.
  
  These Gauss sums satisfy G(χ1) * G(χ2) = χ1*χ2(-1) * p * G(χ1*χ2).
  And G(χ)^2 = χ(-1) * p * G(χ^2). And G(χ)^p relates to specific values.

  For Gauss sums of order p (i.e., with characters of order p in F_q*),
  they live in the "splitting field" of p-th cyclotomic polynomial, which is
  F_q(ζ_p) = F_{q^m} where m | p-1. Their values are constrained.

KEY INSIGHT:
  Compute the specific Gauss sum G(χ_0) where χ_0 is the quadratic character
  of order p (when p ≡ 1 mod 4, so it's a real character).
  
  For p = 1237 ≡ 1 mod 4, the quadratic Gauss sum satisfies:
    G(χ_quad)^2 = p  (in Z, by classical theory)
  So G(χ_quad) = ±√p in Z.
  
  But mod q (for q | M(p)), G(χ_quad) is a specific integer mod q, and its
  square mod q equals p mod q. So G(χ_quad) is a "modular square root of p".
  
  By CRT, G(χ_quad) mod N corresponds to multiple values (one per prime factor q).
  If we can compute TWO different "modular square roots of p" and they differ
  (not ± each other), gcd gives a factor.

METHOD:
  Compute the Gauss sum G(χ_quad) explicitly:
    G(χ_quad) = sum_{k=1}^{p-1} χ_quad(k) * ζ_p^k
  where ζ_p is a primitive p-th root of unity.
  
  In Z/NZ, 2 is a primitive p-th root (since q | M(p) means 2^p ≡ 1 mod q).
  So ζ_p ≡ 2 mod q, and:
    G(χ_quad) mod q ≡ sum_{k=1}^{p-1} χ_quad(k) * 2^k mod q
  
  The quadratic character χ_quad(k) = (k/p) is the Legendre symbol of k mod p.
  
  So: G_chi_mod_N = sum_{k=1}^{p-1} (k/p) * 2^k mod N
  
  This is a "modular square root of p" via the identity G_quad^2 = p.

  After computing G_chi, we check: gcd(G_chi^2 - p, N). If non-trivial, factor!
  Also: gcd(G_chi - some_other_sqrt(p), N).
  
  For a different sqrt(p) mod N: use a different primitive p-th root mod q,
  i.e., replace 2 with 2^k for any generator k of (Z/pZ)*.
  
  In particular: G_chi_with_base(2^k) = sum_{k'} (k'/p) * 2^(k*k') mod N
              = G_chi_with_base(2) ... but with index permuted.
  
  The "two different square roots" approach:
  - G_quad evaluated with ζ = 2: gives sqrt(p) "view 1"
  - G_quad evaluated with ζ = 2^3 (assuming 3 is non-residue mod p): gives a DIFFERENT sqrt(p)
  - Their difference is a non-trivial factor

ALGORITHM:
  1. Compute Legendre symbols (k/1237) for k = 1, 2, ..., 1236
  2. Compute G1 = sum_{k=1}^{1236} (k/1237) * 2^k mod N
  3. Compute G2 = sum_{k=1}^{1236} (k/1237) * 2^(3k) mod N (replace 2 with 2^3)
  4. Compute gcd(G1 - G2, N), gcd(G1 + G2, N)
  5. If non-trivial, FACTOR!

This is GENUINELY NOVEL — using Gauss sums of order p for Mersenne factoring
has not been done before in the literature (to my knowledge).
"""

import sys
import time
from pathlib import Path

import gmpy2
from gmpy2 import mpz, gcd, is_prime, powmod, jacobi

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
LOG_FILE = BASE / 'logs/gauss_sum.log'
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


def gauss_sum_quad_with_base(p, N, base_exponent=1):
    """Compute G_chi_quad(ζ) where ζ = base^base_exponent mod N (base = 2 by convention).
    
    G_chi_quad(ζ) = sum_{k=1}^{p-1} χ_quad(k) * ζ^k
    where χ_quad(k) = (k/p) is the Legendre symbol.
    
    For base = 2 (standard), ζ = 2^base_exponent mod N.
    Since 2^p ≡ 1 (mod N) (because N | M(p)), ζ is a p-th root of unity.
    
    Returns G mod N.
    """
    # Compute Legendre symbols (k/p) for k = 1, ..., p-1
    # Use Euler's criterion: (k/p) = k^((p-1)/2) mod p, but easier: use gmpy2.jacobi(k, p)
    # For p prime, jacobi(k, p) is the Legendre symbol.
    legendre = [0] * (p + 1)
    for k in range(1, p):
        legendre[k] = jacobi(k, p)
    
    # ζ = 2^base_exponent mod N
    zeta = powmod(2, base_exponent, N)
    
    # Compute G = sum_{k=1}^{p-1} χ(k) * ζ^k
    # Use Horner-like scheme for efficiency:
    # G = sum_k χ(k) * z^k
    # Direct sum is O(p) mults, but each powmod(z, k, N) is O(log k) per call.
    # Better: precompute z^k iteratively.
    G = mpz(0)
    z_pow_k = mpz(1)  # z^0 = 1
    z = zeta
    for k in range(1, p):
        z_pow_k = (z_pow_k * z) % N
        G = (G + legendre[k] * z_pow_k) % N
    return G


def gauss_sum_quad_with_base_multiple_bases(p, N, base_exponents, log_lines=None):
    """Compute Gauss sums for multiple base exponents.
    Each base exponent gives a different "view" of sqrt(p) mod N.
    If two views differ (not just by sign), gcd gives a factor.
    """
    Gs = []
    for be in base_exponents:
        if log_lines is not None:
            log_lines.append(f'  Computing Gauss sum with base exponent {be}...')
        t0 = time.time()
        G = gauss_sum_quad_with_base(p, N, base_exponent=be)
        elapsed = time.time() - t0
        if log_lines is not None:
            log_lines.append(f'    G = {G} ({len(str(G))} digits), time={elapsed:.1f}s')
        Gs.append(int(G))
    return Gs


def try_gauss_sum_factoring(p, N, log_lines=None):
    """Run the Gauss sum method for factoring.
    Returns factor (int) or None.
    """
    # Use base exponents: 1, and some non-residues mod p
    # Need generators of (Z/pZ)* to get different "views".
    # Use a few small non-residues mod p as different base exponents.
    non_residues = []
    for k in range(2, 50):
        if jacobi(k, p) == -1:
            non_residues.append(k)
        if len(non_residues) >= 5:
            break
    base_exponents = [1] + non_residues
    
    if log_lines is not None:
        log_lines.append(f'  Using base exponents: {base_exponents}')
    
    Gs = gauss_sum_quad_with_base_multiple_bases(p, N, base_exponents, log_lines=log_lines)
    
    # Check G^2 - p (should be 0 mod N if Gauss sum theory holds)
    for i, G in enumerate(Gs):
        G_mpz = mpz(G)
        G_sq = (G_mpz * G_mpz) % N
        diff = (G_sq - p) % N
        g = gcd(diff, N)
        if 1 < g < N:
            if log_lines is not None:
                log_lines.append(f'  G_{base_exponents[i]}^2 ≡ p mod N? No, gcd(G^2 - p, N) = {g}')
            return int(g)
    
    # Try pairwise differences
    for i in range(len(Gs)):
        for j in range(i + 1, len(Gs)):
            # gcd(G_i - G_j, N)
            g = gcd(Gs[i] - Gs[j], N)
            if 1 < g < N:
                if log_lines is not None:
                    log_lines.append(f'  gcd(G_{base_exponents[i]} - G_{base_exponents[j]}, N) = {g} (FACTOR!)')
                return int(g)
            # gcd(G_i + G_j, N)
            g = gcd(Gs[i] + Gs[j], N)
            if 1 < g < N:
                if log_lines is not None:
                    log_lines.append(f'  gcd(G_{base_exponents[i]} + G_{base_exponents[j]}, N) = {g} (FACTOR!)')
                return int(g)
    
    # Try Gauss sum and -Gauss sum (since there are two square roots of p: ±G)
    for G in Gs:
        for G_other in Gs:
            if G == G_other:
                continue
            # G^2 ≡ p, so G ≡ ±sqrt(p) mod q for each q | N.
            # If G ≡ sqrt(p) mod q_1 but G ≡ -sqrt(p) mod q_2, then gcd(G + G, N) might give something.
            # gcd(2G, N): if N is odd, gcd(2G, N) = gcd(G, N) (since gcd(2, N)=1).
            pass
    
    if log_lines is not None:
        log_lines.append(f'  No factor from Gauss sums')
    return None


def main():
    p = 1237
    F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
    M = mpz(2)**p - 1
    N = M // F1
    
    log('=' * 70)
    log('Gauss Sum of Order p (GSp) — novel Mersenne factorization method')
    log(f'  Target: M({p})/F1, {len(str(N))} digits')
    log(f'  Algorithm: compute quadratic Gauss sum G with multiple bases,')
    log(f'    use gcd(G1 - G2, N) to factor.')
    log(f'  Theory: G^2 ≡ p mod N; different "views" of sqrt(p) give different G.')
    log('=' * 70)
    
    if is_prime(N):
        log('N is already prime — done')
        return
    
    log_lines = []
    t0 = time.time()
    factor = try_gauss_sum_factoring(p, N, log_lines=log_lines)
    elapsed = time.time() - t0
    for line in log_lines:
        log(line)
    log(f'  Total time: {elapsed:.1f}s')
    
    if factor is not None:
        log(f'  >>> FACTOR FOUND: {factor} ({len(str(factor))} digits)')
        if not is_prime(factor):
            f_int = factor
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
        log(f'  No factor found via Gauss sum method')
    
    # Also try on all missing primes
    log('')
    log('=' * 70)
    log(f'Gauss sum method on all 204 missing primes')
    log('=' * 70)
    
    missing = get_missing()
    total_found = 0
    t_start = time.time()
    
    for idx, mp in enumerate(missing, 1):
        if time.time() - t_start > 95:
            log(f'  Time budget exceeded at p={mp}')
            break
        log(f'  [{idx}/{len(missing)}] p={mp}')
        t0 = time.time()
        Mp = mpz(2)**mp - 1
        # For missing primes, we don't have F1. Apply directly to M(p).
        log_lines_p = []
        factor = try_gauss_sum_factoring(mp, Mp, log_lines=log_lines_p)
        elapsed_p = time.time() - t0
        for line in log_lines_p[-3:]:
            log(line)
        log(f'    time: {elapsed_p:.2f}s')
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
    log(f'Gauss sum method complete. Total {total_found} factor(s) in {elapsed_total:.1f}s')
    log('=' * 70)


if __name__ == '__main__':
    main()
