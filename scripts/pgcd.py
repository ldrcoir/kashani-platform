#!/usr/bin/env python3
"""
Polynomial GCD Factorization (PGCD) - genuinely novel approach.

CONCEPTUAL INSIGHT:
  Phi_p(x) = (x^p - 1)/(x - 1) = product over k=1..p-1 of (x - 2^k mod N)
  (since 2^p ≡ 1 mod N and the roots of Phi_p in F_N are the p-th roots of unity,
   which are {2^k mod q_i for k=0..p-1} for each q_i | N, but viewed via CRT).
  
  Wait, more carefully: Phi_p(x) mod N has degree p-1 = 1236.
  In Z/NZ, Phi_p(2) = 0 (since 2^p ≡ 1 mod N and 2 ≠ 1).
  So (x - 2) divides Phi_p(x) mod N? Only if Phi_p has only one root at x = 2.
  But Phi_p(x) ≡ 0 mod q_i when x = 2^k for k=1..p-1 (p-1 distinct roots mod q_i).
  And Phi_p(x) ≡ 0 mod N (as a polynomial)? No, Phi_p(x) is a polynomial with 
  coefficients; saying "Phi_p(x) ≡ 0 mod N as a polynomial" means all coeffs are 0 mod N,
  which is NOT true. Phi_p(x) has coeff 1 at all positions.
  
  So Phi_p(x) mod N is a degree-(p-1) polynomial with all coeff = 1.
  We want to find gcd(Phi_p(x), Q(x)) in (Z/NZ)[x] for some cleverly chosen Q.

KEY INSIGHT:
  In Z/q_i Z [x], Phi_p(x) factors as ∏_{k=0}^{p-1} (x - 2^k) (since 2^k mod q_i 
  for k=0..p-1 are p distinct p-th roots of unity).
  
  For Q(x) = x^2 - a, gcd(Phi_p, Q) mod q_i depends on (a/q_i):
    - If (a/q_i) = +1: Q has roots ±sqrt(a) in F_q_i. If any of these equals 2^k mod q_i 
      for some k, then gcd(Phi_p, Q) has those roots. So gcd = (x - r1)(x - r2) (or 
      (x - r)^2 if doubled root).
      Wait, we need sqrt(a) to be a power of 2 mod q_i. Since {2^k} are all p-th 
      roots of unity, we need sqrt(a) to be a p-th root of unity, i.e., (sqrt(a))^p = 1, 
      i.e., a^p = sqrt(a)^{2p} = (sqrt(a)^p)^2 = 1, i.e., a^p ≡ 1 mod q_i.
      So we need a^p ≡ 1 mod q_i for the gcd to be nontrivial.
      
      Specifically, if a^p ≡ 1 mod q_i AND sqrt(a) ≡ 2^k mod q_i for some k in [1, p-1]:
      Then gcd(Phi_p, Q) mod q_i = (x - 2^k)(x - 2^{(p-k) mod p}) (since -2^k = 2^k * (-1),
      and -1 = ? mod q_i... actually -1 is in F_q_i, but is -1 a power of 2 mod q_i?
      Not necessarily. -1 is a p-th root of unity iff (-1)^p = 1 iff p even (no, p=1237 is odd).
      So -1 is NOT a p-th root of unity (since p is odd and -1 has order 2, which doesn't divide p=1237).
      So -1 ∉ {2^k mod q_i : k = 0..p-1}.
      
      Therefore -2^k mod q_i is NOT in the set of p-th roots of unity. 
      Hmm, so (x - 2^k)(x - (-2^k)) mod q_i = (x - 2^k)(x + 2^k) = x^2 - 2^{2k} = x^2 - a
      where a = 2^{2k}.
      
      So a = 2^{2k} for some k, and sqrt(a) = 2^k (positive root). The other root is -2^k, 
      which is NOT a p-th root of unity.
      
      Therefore, for Q(x) = x^2 - a with a = 2^{2k} (k=1..p-1, k != p/2 since p odd),
      the gcd(Phi_p, Q) mod q_i = (x - 2^k) (only one root in Phi_p, since -2^k is not a root).
      
      Specifically: gcd(Phi_p(x), x^2 - 2^{2k}) mod q_i = (x - 2^k) mod q_i 
      (since x^2 - 2^{2k} = (x - 2^k)(x + 2^k), and only x = 2^k is a root of Phi_p).
  
  So:
    For each k = 1..p-1:
      Q_k(x) = x^2 - 2^{2k mod p} mod N (computable since 2^p ≡ 1 mod N)
      G_k(x) = gcd(Phi_p(x), Q_k(x)) mod N
      
      In mod q_i: G_k(x) = (x - 2^k mod q_i) for ALL q_i (the k-th root is the same).
      So G_k(x) = (x - 2^k mod N) mod N? Yes! By CRT, since the polynomial is x - 2^k 
      in each F_q_i, and 2^k mod N is well-defined.
      
      So G_k(x) = (x - 2^k mod N) - trivial!
  
  Hmm, that's not useful. Let me think again.

ALTERNATIVE: Use Q(x) that has a root which is a p-th root of unity mod q_1 but NOT mod q_2.

  This happens when (D/q_1) ≠ (D/q_2) for D = a, and additionally sqrt(a) is a power of 2 mod q_i 
  where (a/q_i) = +1.

  But sqrt(a) being a power of 2 mod q_i requires a^p ≡ 1 mod q_i, which is a strong condition.
  
  Let me think of a specific case: a = 2.
    sqrt(2) is a power of 2 mod q_i iff sqrt(2) = 2^k mod q_i for some k, iff 2 = 2^{2k} mod q_i,
    iff 2^{2k-1} ≡ 1 mod q_i, iff ord_q_i(2) | (2k-1), iff 1237 | (2k-1).
    For p = 1237 (odd), 2k-1 ≡ 0 mod 1237 means 2k ≡ 1 mod 1237, so k = (1+1237)/2 = 619 mod 1237.
    So k = 619 works (and k = 619 + 1237 = 1856, etc., within [0, p-1]).
    So sqrt(2) ≡ 2^619 mod q_i (if (2/q_i) = +1).
    
  Hmm interesting. So for Q(x) = x^2 - 2:
    In F_q_i with (2/q_i) = +1: roots are ±2^619, of which +2^619 is a p-th root of unity 
    (since 2^619 has order dividing p=1237), but -2^619 is NOT a p-th root of unity 
    (since p is odd, -1 has order 2 which doesn't divide 1237).
    So gcd(Phi_p, x^2 - 2) mod q_i = (x - 2^619) mod q_i.
    
    In F_q_i with (2/q_i) = -1: x^2 - 2 has no roots, so gcd = 1.
  
  So gcd(Phi_p(x), x^2 - 2) mod N (via CRT):
    In F_q_i with (2/q_i) = +1: x - 2^619 (degree 1)
    In F_q_j with (2/q_j) = -1: 1 (degree 0)
  
  The CRT result is: in mod q_i (with (2/q_i)=+1), it's x - 2^619 mod q_i. 
  In mod q_j (with (2/q_j)=-1), it's 1 mod q_j.
  
  The polynomial is g(x) = (x - 2^619 mod N) in mod q_i but g(x) = 1 in mod q_j.
  CRT: g(x) mod N = ?
  
  Hmm. The polynomial is determined by its values mod each prime factor.
  In F_q_i [x]: g(x) = x - 2^619 mod q_i.
  In F_q_j [x]: g(x) = 1.
  
  CRT for the polynomial coefficients:
    constant term: (a_0 mod q_i = -2^619 mod q_i, a_0 mod q_j = 1)
    linear term: (a_1 mod q_i = 1, a_1 mod q_j = 0)
  
  So g(x) = c_1 * x + c_0 in Z/NZ [x], where:
    c_1 ≡ 1 mod q_i and c_1 ≡ 0 mod q_j (via CRT)
    c_0 ≡ -2^619 mod q_i and c_0 ≡ 1 mod q_j (via CRT)
  
  Now: 
    gcd(c_1, N) = q_i (since c_1 ≡ 0 mod q_j and ≡ 1 mod q_i, gcd gives q_j... wait)
    Actually c_1 ≡ 1 mod q_i, c_1 ≡ 0 mod q_j. So gcd(c_1, N) = q_j (the prime for which c_1 ≡ 0).
  
  YES! So if we compute gcd(c_1, N), we get q_j (a non-trivial factor)!

ALGORITHM:
  1. Compute Phi_p(x) mod N (degree p-1 = 1236, all coefficients 1).
  2. Compute gcd(Phi_p(x), x^2 - 2) mod N. Result is a polynomial of degree <= 1.
  3. The coefficient of x in this gcd, gcd with N, gives a non-trivial factor!

This is GENUINELY NOVEL — using polynomial GCD with x^2 - a (specifically a=2) to factor N 
via the CRT structure of Phi_p(x).

WHY THIS SHOULD WORK:
  We know sqrt(2) mod N doesn't exist (some (2/q_i) = -1).
  But (2/N) = +1 (overall Jacobi).
  So N has both (2/q_i)=+1 and (2/q_j)=-1 factors.
  The polynomial GCD extracts this asymmetry via CRT!
  
  Polynomial GCD over Z/NZ can be computed using Euclidean algorithm.
  
KEY IMPLEMENTATION DETAIL:
  Polynomial GCD over Z/NZ can fail if leading coefficient is not invertible mod N.
  But if it's NOT invertible, gcd(leading_coeff, N) gives a factor directly!
  
  So even partial computation can yield a factor.

Let me implement this.
"""

import sys
import time
from pathlib import Path
import gmpy2
from gmpy2 import mpz, gcd as gmpy_gcd, is_prime, powmod, invert

sys.set_int_max_str_digits(1000000)

BASE = Path('/home/z/my-project')
LOG = BASE / 'logs/pgcd.log'
LOG.parent.mkdir(exist_ok=True)


def log(msg):
    print(msg, flush=True)
    with open(LOG, 'a') as f:
        f.write(msg + '\n')


def poly_mod_reduce(p_poly, q_poly, N):
    """Compute p_poly mod q_poly in (Z/NZ)[x].
    Returns (remainder, factor_or_None). If a leading coefficient is not invertible
    mod N, the gcd of that leading coeff with N gives a factor.
    """
    p_poly = list(p_poly)  # copy
    while len(p_poly) >= len(q_poly):
        # Leading coeff of p
        lead_p = p_poly[-1] % N
        if lead_p == 0:
            p_poly.pop()
            continue
        # Leading coeff of q
        lead_q = q_poly[-1] % N
        # Compute inverse of lead_q mod N
        g = gmpy_gcd(lead_q, N)
        if 1 < int(g) < int(N):
            # Found a factor!
            return None, int(g)
        if g == N:
            # lead_q = 0 mod N, can't reduce
            return None, None
        # inv_lead_q = invert(lead_q, N)
        try:
            inv_lead_q = invert(lead_q, N)
        except:
            # lead_q not invertible
            g = gmpy_gcd(lead_q, N)
            return None, int(g) if 1 < int(g) < int(N) else None
        # ratio = lead_p * inv_lead_q mod N
        ratio = (lead_p * inv_lead_q) % N
        # Subtract ratio * q_poly * x^(deg_p - deg_q) from p_poly
        shift = len(p_poly) - len(q_poly)
        for i, c in enumerate(q_poly):
            p_poly[shift + i] = (p_poly[shift + i] - ratio * c) % N
        # Remove trailing zeros (highest degree)
        while p_poly and p_poly[-1] % N == 0:
            p_poly.pop()
    return p_poly, None


def poly_gcd(a, b, N):
    """Compute gcd(a, b) in (Z/NZ)[x] using Euclidean algorithm.
    Returns (gcd_poly, factor_or_None).
    If during computation we find a non-invertible leading coefficient,
    gcd(leading_coeff, N) gives a non-trivial factor of N.
    """
    a = list(a)
    b = list(b)
    
    # Ensure leading coefficients are non-zero
    while a and a[-1] % N == 0:
        a.pop()
    while b and b[-1] % N == 0:
        b.pop()
    
    if not a:
        return b, None
    if not b:
        return a, None
    
    iteration = 0
    while b:
        iteration += 1
        if iteration > 10000:
            log(f'  Too many iterations, aborting')
            return None, None
        rem, factor = poly_mod_reduce(a, b, N)
        if factor is not None:
            return None, factor
        if rem is None:
            # Something weird
            return None, None
        a = b
        b = rem
        if iteration % 100 == 0:
            log(f'  iter {iteration}: deg(a)={len(a)-1 if a else -1}, deg(b)={len(b)-1 if b else -1}')
    
    return a, None


def main():
    p = 1237
    M_p = mpz(2)**p - 1
    F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
    N = M_p // F1
    
    log('=' * 70)
    log('Polynomial GCD Factorization (PGCD)')
    log(f'  Target: N = M({p})/F1, {len(str(N))} digits')
    log(f'  Algorithm: compute gcd(Phi_p(x), x^2 - 2) mod N')
    log(f'  If asymmetric (2/q_i) signs, gcd gives a factor!')
    log('=' * 70)
    
    # Verify (2/N) = +1 but sqrt(2) doesn't exist
    from gmpy2 import jacobi
    log(f'(2/N) = {jacobi(2, int(N))} (should be +1)')
    
    # Phi_p(x) = 1 + x + x^2 + ... + x^(p-1) (degree p-1 = 1236)
    # All coefficients are 1
    Phi_p = [mpz(1)] * p  # length p = 1237
    
    # Q(x) = x^2 - 2
    Q = [-mpz(2), mpz(0), mpz(1)]  # -2 + 0*x + 1*x^2
    
    log('')
    log('Computing gcd(Phi_p, x^2 - 2) mod N...')
    log('  Phi_p has degree 1236, Q has degree 2')
    log('  Expected: a polynomial of degree 0 or 1, or a factor found via non-invertible leading coeff')
    
    t0 = time.time()
    result, factor = poly_gcd(Phi_p, Q, N)
    elapsed = time.time() - t0
    
    if factor is not None:
        log(f'  >>> FACTOR FOUND via non-invertible leading coeff!')
        log(f'      Factor = {factor}')
        log(f'      Digits: {len(str(factor))}')
        cofactor = int(N) // factor
        log(f'      Cofactor: {cofactor} ({len(str(cofactor))} digits)')
        log(f'      is_prime(factor): {is_prime(factor)}')
        log(f'      is_prime(cofactor): {is_prime(cofactor)}')
        
        # Update factors table
        lines = (BASE / 'download/A136030_factors_1_to_8000.txt').read_text().splitlines(keepends=True)
        out = []
        for line in lines:
            if line.startswith('#'):
                out.append(line); continue
            parts = line.split('\t')
            if len(parts) >= 2 and parts[0] == str(p):
                cur = parts[1].strip()
                if cur == '-1' or factor < int(cur):
                    out.append(f'{p}\t{factor}\n')
                else:
                    out.append(line)
            else:
                out.append(line)
        (BASE / 'download/A136030_factors_1_to_8000.txt').write_text(''.join(out))
        log('  Updated factors table!')
        return
    
    if result is None:
        log('  GCD computation failed')
        return
    
    log(f'  GCD computed in {elapsed:.1f}s')
    log(f'  Result has degree {len(result)-1 if result else -1}')
    log(f'  Coefficients: {result}')
    
    if len(result) <= 2:
        # Try gcd of each coefficient with N
        for i, c in enumerate(result):
            g = gmpy_gcd(c, N)
            if 1 < int(g) < int(N):
                log(f'  >>> FACTOR FOUND: gcd(coeff[{i}], N) = {g}')
                log(f'      Factor has {len(str(g))} digits')
                cofactor = int(N) // int(g)
                log(f'      Cofactor: {cofactor}')
                
                # Update factors table
                lines = (BASE / 'download/A136030_factors_1_to_8000.txt').read_text().splitlines(keepends=True)
                out = []
                for line in lines:
                    if line.startswith('#'):
                        out.append(line); continue
                    parts = line.split('\t')
                    if len(parts) >= 2 and parts[0] == str(p):
                        cur = parts[1].strip()
                        if cur == '-1' or int(g) < int(cur):
                            out.append(f'{p}\t{int(g)}\n')
                        else:
                            out.append(line)
                    else:
                        out.append(line)
                (BASE / 'download/A136030_factors_1_to_8000.txt').write_text(''.join(out))
                log('  Updated factors table!')
                return
    else:
        log(f'  GCD has degree {len(result)-1}, larger than expected (degree 1 or 0)')
        log(f'  This means our analysis was wrong, or there are multiple factor structures.')


if __name__ == '__main__':
    main()
