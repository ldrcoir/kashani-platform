#!/usr/bin/env python3
"""
Compute Aurifeuillean A, B for M(1237) using direct coefficient matching,
then use them to factor via Rabin's attack with multiple sqrt(2p) mod N.

ALGORITHM:
  1. Compute polynomial L_p(x), M_p(x) over QQ such that 
     Phi_p(x) = L_p(x)^2 - p*x*M_p(x)^2 (Aurifeuillean identity).
     Use the recurrence: l_d = 1, and at each step:
       2 l_d l_{d-1} - p m_{d-1}^2 = 1 (coefficient of x^{2d-1} in Phi_p, L^2)
       ... etc.
     Solve quadratic Diophantine equation at each step.
  2. Evaluate L_p(2) and M_p(2) to get A, B with M(p) = A^2 - 2p B^2.
  3. Compute R1 = A * B^{-1} mod N (a sqrt of 2p mod N).
  4. Find ANOTHER sqrt(2p) mod N (e.g., via different Aurifeuillean form, or Cipolla).
  5. If R1 ≠ ± R2 mod N: gcd(R1 - R2, N) gives factor.
"""

import sys
import time
from pathlib import Path

import gmpy2
from gmpy2 import mpz, gcd, is_prime, powmod, invert, jacobi

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
LOG_FILE = BASE / 'logs/aurif_direct.log'
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


def compute_aurif_coefficients(p):
    """Compute L_p(x), M_p(x) such that Phi_p(x) = L_p^2 - p*x*M_p^2.
    
    Returns two lists: L coefficients (l_0, l_1, ..., l_d) and M coefficients (m_0, ..., m_{d-1})
    where d = (p-1)/2.
    
    Algorithm:
      l_d = 1 (leading coefficient of L_p)
      For each k = 1 to d (top-down):
        At step k, we determine l_{d-k} and m_{d-k} (or just one of them).
        Constraint: coefficient of x^{2d-k} in L^2 - p*x*M^2 equals Phi_p[2d-k] = 1.
        
        Let:
          Sum_L = sum_{i+j=2d-k, i,j ≤ d} l_i * l_j (using already-determined higher coeffs)
          Sum_M = sum_{i+j=2d-k-1, i,j ≤ d-1} m_i * m_j (using already-determined higher coeffs)
          (Note: when both l_new and m_new contribute to the sums, we extract them explicitly.)
        
        Coefficient of x^{2d-k} in L^2 - p*x*M^2:
          For L^2: sum_{i+j = 2d-k} l_i * l_j = 2*l_d * l_{d-k} + (sum of known terms)
                                            = 2 * l_{d-k} + known
          For p*x*M^2: M^2's coefficient at x^{2d-k-1} = sum_{i+j = 2d-k-1} m_i * m_j.
            If 2d-k-1 = 2(d-1), i.e., k = 1: m_{d-1}^2 (just leading).
            Otherwise: 2 * m_{d-1} * m_{d-k+1} + (sum of known terms), where m_{d-k+1} is the NEW 
              coefficient (for k >= 2, m_{d-k+1} is being determined at step k-1).
            Hmm wait. Let me re-index.
            
        Better: Let's index L = [l_d, l_{d-1}, ..., l_0] (top down) and M = [m_{d-1}, ..., m_0].
        At step k = 1, ..., d, we determine l_{d-k} (and m_{d-k} if it exists).
        
        Actually let's just keep all unknowns and solve them step by step.
        Step k determines l_{d-k} and (for k >= 2) m_{d-k+1}? Hmm.
        
        Let me think differently. At step k = 1, the new l is l_{d-1} and the new m is m_{d-1}.
        Two unknowns, one equation: 2*l_{d-1} - p*m_{d-1}^2 = 1 - 0 = 1.
        
        At step k = 2, the new l is l_{d-2}, and we already know m_{d-1}. New m is m_{d-2}.
        Equation: 2*l_d*l_{d-2} + l_{d-1}^2 - p*(2*m_{d-1}*m_{d-2}) = Phi[2d-2]
                 2*l_{d-2} + l_{d-1}^2 - p*2*m_{d-1}*m_{d-2} = 1
        Two unknowns (l_{d-2}, m_{d-2}). 
        
        Hmm, always 2 unknowns. We need another constraint.
        
        The constraint is that the quotient (L^2 - Phi_p) / (p*x) is a perfect square.
        This is a global constraint, not step-by-step.
        
        ACTUAL ALGORITHM (from Brent):
          Use Newton's iteration to find L as a polynomial:
            L = sqrt(Phi_p mod p * x^k) — treating Phi_p as living in some ring where x is nilpotent.
          Specifically, compute L mod (p, x^{d+1}) (work modulo p for the polynomial coefficients).
          Then the relation L^2 ≡ Phi_p mod (p, x^{d+1}) holds (since p*x*M^2 ≡ 0 mod p).
          By Newton: L_new = (L + Phi_p / L) / 2, iterating until convergence.
          
        Let me just compute L mod p as a polynomial, then lift to Z.
    """
    pass  # Will compute via Newton's iteration modularly.


def compute_L_mod_p(p, target_deg, modulus):
    """Compute L_p(x) modulo a small prime modulus, using Newton's iteration.
    
    Phi_p(x) = sum_{i=0}^{p-1} x^i, viewed modulo 'modulus' (a small prime).
    L(x) such that L^2 ≡ Phi_p(x) mod (modulus, x^{target_deg+1}).
    
    Newton: L_new = (L + Phi_p / L) / 2, truncated to degree target_deg.
    """
    from sympy import nextprime
    
    # We need modulus to be such that the leading coeff of Phi_p (= 1) has a square root mod modulus.
    # 1 is its own square root, so any modulus works for the leading coefficient.
    
    # Polynomial arithmetic modulo 'modulus' and x^{target_deg+1}.
    # We represent polynomials as lists of coefficients (length target_deg+1).
    
    # Phi_p(x) mod modulus and x^{target_deg+1}: just [1, 1, 1, ..., 1] truncated.
    Phi = [1] * (target_deg + 1)  # length target_deg + 1
    # Actually Phi_p has degree p-1, which is 2*target_deg. We only need up to target_deg.
    # Phi coefficients are all 1.
    
    # Initialize L = x^target_deg (leading term)
    L = [0] * (target_deg + 1)
    L[target_deg] = 1
    
    # Newton iteration: L_new = (L + Phi / L) / 2 mod (modulus, x^{target_deg+1})
    # Need polynomial division mod modulus.
    
    inv2 = pow(2, -1, modulus)  # inverse of 2 mod modulus
    
    for it in range(target_deg * 2 + 5):
        # Compute Phi / L mod modulus, truncated to degree target_deg
        # Polynomial long division
        quot = [0] * (target_deg + 1)
        rem = Phi[:]  # copy
        # We want quot such that Phi - quot * L is divisible by x^{target_deg+1} in some sense,
        # but since L is degree target_deg, we can compute quotient of degree up to target_deg.
        # Use a simpler approach: shift-based division.
        # Actually, we want quot = Phi / L mod x^{target_deg+1}.
        # For power series division: if L[0] is invertible, then 1/L as power series.
        # But L[0] might be 0.
        # 
        # Let's just use sympy for this, or implement properly.
        
        # Simpler: use the Newton iteration for the inverse, then multiply.
        # 1/L as power series: B such that L * B = 1 mod x^{target_deg+1}.
        # But this requires L[0] ≠ 0.
        
        # If L[0] == 0, we need to handle differently.
        # In our case L[target_deg] = 1, L[0] = ? (unknown).
        
        # Alternative: use the formal power series arithmetic where we treat L as having
        # leading coefficient 1 (so it's "monic" with respect to x^{target_deg}).
        # Then division by L is well-defined.
        
        # Actually, easier: compute L via "inversion by Newton" using reverse polynomials.
        # Let L_rev(x) = x^target_deg * L(1/x). Then L_rev has nonzero constant term (= L[target_deg] = 1).
        # Compute 1/L_rev via Newton's iteration, then reverse to get 1/L.
        
        # Reverse L
        L_rev = L[::-1]
        # Compute B = 1/L_rev mod x^{target_deg+1} via Newton:
        # B_new = B * (2 - L_rev * B) mod x^{target_deg+1}
        B = [inv2] if L_rev[0] == 1 else [pow(L_rev[0], -1, modulus)]
        # extend to length target_deg+1
        while len(B) < target_deg + 1:
            B.append(0)
        for _ in range(target_deg + 5):
            # B_new = B * (2 - L_rev * B) mod x^{target_deg+1}
            # First compute L_rev * B
            conv = poly_mult_mod(L_rev, B, modulus, target_deg + 1)
            # 2 - conv
            two_minus = [(-c) % modulus for c in conv]
            two_minus[0] = (2 - conv[0]) % modulus  # actually first term is 2 - conv[0]
            # Actually 2 - conv means: subtract conv from the constant polynomial 2.
            # As a list: [2, 0, 0, ...] - conv.
            two_minus = [(2 if i == 0 else 0) - conv[i] for i in range(target_deg + 1)]
            two_minus = [c % modulus for c in two_minus]
            # B_new = B * two_minus mod x^{target_deg+1}
            B_new = poly_mult_mod(B, two_minus, modulus, target_deg + 1)
            if B_new == B:
                break
            B = B_new
        
        # Now B = 1/L_rev mod x^{target_deg+1}, so 1/L = reverse(B).
        inv_L_rev = B
        # 1/L = x^{target_deg} * (1/L_rev)(1/x)
        # As a list, 1/L is reverse of B.
        inv_L = inv_L_rev[::-1]
        # Wait, 1/L = ? Let's think.
        # L(x) = sum_{i=0}^{target_deg} L[i] x^i
        # L_rev(x) = sum_{i=0}^{target_deg} L[target_deg - i] x^i = x^{target_deg} L(1/x)
        # 1/L(x) = x^{-target_deg} / L_rev(1/x) = x^{-target_deg} * B(1/x)
        # = x^{-target_deg} * sum B[i] (1/x)^i = sum B[i] x^{-target_deg-i}
        # This is a Laurent series, not a polynomial.
        
        # OK this approach is getting tangled. Let me use sympy for polynomial arithmetic.
        return None  # signal to use sympy approach
    
    return L


def poly_mult_mod(a, b, modulus, max_deg):
    """Multiply polynomials a and b mod modulus, truncate to degree max_deg-1."""
    result = [0] * max_deg
    for i in range(min(len(a), max_deg)):
        if a[i] == 0:
            continue
        for j in range(min(len(b), max_deg - i)):
            if b[j] == 0:
                continue
            result[i + j] = (result[i + j] + a[i] * b[j]) % modulus
    return result


def compute_aurif_via_sympy(p, log):
    """Compute L_p, M_p via sympy's polynomial ring over QQ."""
    from sympy import QQ, Rational
    from sympy.polys.rings import ring as sym_ring
    
    log(f"Building polynomial ring over QQ for p={p}...")
    R, x = sym_ring('x', QQ)
    
    target_deg = (p - 1) // 2  # 618
    log(f"  target_deg = {target_deg}")
    
    # Phi_p(x) = sum_{i=0}^{p-1} x^i = sum_{i=0}^{2*target_deg} x^i
    log(f"Building Phi_p...")
    Phi = sum(x**i for i in range(2 * target_deg + 1))
    log(f"  Phi_p built")
    
    # Newton's iteration: L_new = (L + Phi / L) / 2
    # Initialize L = x^target_deg (leading term only)
    L = x**target_deg
    log(f"Starting Newton's iteration (this may take a few minutes)...")
    
    for it in range(2 * target_deg + 5):
        # Polynomial division: Phi / L (mod x^{target_deg+1} as power series)
        # sympy has quo_rem method
        q = Phi.quo(L)  # polynomial quotient
        # Truncate q to degree target_deg
        # q is a PolyRing element, can iterate over monomials
        new_dict = {}
        for monom, coeff in q.items():
            d = list(monom)[0]
            if d <= target_deg:
                new_dict[monom] = coeff
        q_trunc = R.from_dict(new_dict)
        L_new = (L + q_trunc) / 2
        # Check convergence
        if L_new == L:
            log(f"  Converged at iter {it}")
            break
        L = L_new
        if it % 50 == 0:
            log(f"  iter {it}, L degree = {L.degree() if hasattr(L, 'degree') else '?'}")
    
    log(f"  Final L has degree: see below")
    
    # Now compute M_p such that L^2 - Phi = p*x*M^2
    # diff = L^2 - Phi
    diff = L**2 - Phi
    log(f"  L^2 - Phi has degree: {diff.degree() if hasattr(diff, 'degree') else '?'}")
    
    # Divide diff by p*x
    # diff = p * x * M^2, so M^2 = diff / (p * x)
    # diff has constant term 0 (since L^2 - Phi_p has degree < p, and L^2 and Phi_p have same leading coeff)
    # Actually L^2 might not have the same constant term as Phi_p (= 1), so diff has nonzero constant term.
    
    # Let me just evaluate L at x=2 to get A, and compute B = sqrt((A^2 - M) / (2*p))
    # ... or B = (L_p(2) - some adjustment).
    
    # Actually, simpler: Phi_p(2) = M(p) = 2^p - 1.
    # L_p(2) = A, M_p(2) = B, and A^2 - 2p B^2 = M(p).
    
    # Evaluate L at x=2:
    A = sum(coeff * 2**d for monom, coeff in L.items() for d in [list(monom)[0]])
    log(f"  A = L_p(2) = {A}")
    log(f"  A has {len(str(A))} digits")
    
    # Compute B = sqrt((A^2 - M(p)) / (2*p))
    A_int = int(A)
    M_int = 2**p - 1
    diff_num = A_int**2 - M_int
    if diff_num != 2 * p * (diff_num // (2 * p)):
        log(f"  ERROR: A^2 - M(p) is not divisible by 2p")
        return None, None
    
    B_sq = diff_num // (2 * p)
    B = gmpy2.isqrt(mpz(B_sq))
    if B * B != mpz(B_sq):
        log(f"  ERROR: B^2 is not a perfect square")
        return None, None
    
    log(f"  B = {B}")
    log(f"  B has {len(str(B))} digits")
    
    # Verify
    check = A_int**2 - 2 * p * int(B)**2
    log(f"  Verify: A^2 - 2p B^2 = M(p)? {check == M_int}")
    
    return A_int, int(B)


def main():
    p = 1237
    F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
    M = mpz(2)**p - 1
    N = M // F1
    
    log('=' * 70)
    log('Aurifeuillean Direct Computation for M(1237)')
    log(f'  Goal: find A, B with M(p) = A^2 - 2p B^2, then R = A*B^-1 mod N is sqrt(2p) mod N')
    log('=' * 70)
    
    if is_prime(N):
        log('N is already prime — done')
        return
    
    # Compute A, B via sympy
    t0 = time.time()
    try:
        A, B = compute_aurif_via_sympy(p, log)
    except Exception as e:
        log(f'  Error: {e}')
        import traceback
        log(traceback.format_exc())
        return
    elapsed = time.time() - t0
    
    if A is None:
        log('  Failed to compute A, B')
        return
    
    log(f'  Total time: {elapsed:.1f}s')
    
    # Now R = A * B^{-1} mod N is sqrt(2p) mod N
    B_mpz = mpz(B)
    A_mpz = mpz(A)
    
    # Check gcd(B, N) first
    g = gcd(B_mpz, N)
    if 1 < int(g) < int(N):
        log(f'  >>> gcd(B, N) = {g} (FACTOR!)')
        log(f'      FACTOR FOUND!')
        if int(g) < int(F1):
            update_factor_file(p, int(g))
        return
    
    try:
        B_inv = invert(B_mpz, N)
    except Exception as e:
        log(f'  B is not invertible mod N: {e}')
        return
    
    R = (A_mpz * B_inv) % N
    log(f'  R = A * B^-1 mod N = {R}')
    log(f'  R has {len(str(R))} digits')
    
    # Verify R^2 ≡ 2p mod N
    R_sq = (R * R) % N
    log(f'  R^2 mod N = {R_sq}')
    log(f'  2p mod N = {(2 * p) % N}')
    log(f'  Match: {R_sq == (2 * p) % N}')
    
    if R_sq != (2 * p) % N:
        log(f'  R is NOT a sqrt(2p) mod N. Something is wrong.')
        return
    
    # Now find another sqrt(2p) mod N (different CRT lift).
    # Try Cipolla with random non-residues.
    log('')
    log('Finding another sqrt(2p) mod N via Cipolla with random non-residues...')
    
    other_roots = []
    import random
    for _ in range(20):
        # Cipolla for sqrt(2p) mod N: pick t such that t^2 - 2p is a Jacobi non-residue
        for _ in range(50):
            t = mpz(random.randint(2, int(N) - 1))
            d = (t * t - 2 * p) % N
            try:
                j = jacobi(d, N)
            except:
                continue
            if j == -1:
                break
        else:
            continue
        
        # Cipolla ladder: (t + x)^((N+1)/2) in F_N[x]/(x^2 - d)
        # Wait, Cipolla requires prime modulus. For composite N, this might not work directly.
        # But let's try anyway.
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
            r_cipolla = cur_u
            # Verify
            if (r_cipolla * r_cipolla - 2 * p) % N == 0:
                other_roots.append(int(r_cipolla))
                log(f'  Cipolla found root: {r_cipolla} ({len(str(r_cipolla))} digits)')
    
    # Now compare R (from Aurifeuillean) with each Cipolla root
    log('')
    log('Comparing Aurifeuillean R with Cipolla roots:')
    for i, r_other in enumerate(other_roots):
        log(f'  Cipolla root {i}: {r_other}')
        g = gcd(R - r_other, N)
        log(f'    gcd(R - root, N) = {g}')
        if 1 < int(g) < int(N):
            log(f'  >>> FACTOR FOUND: {g} ({len(str(g))} digits)')
            if int(g) < int(F1):
                update_factor_file(p, int(g))
            return
        g = gcd(R + r_other, N)
        log(f'    gcd(R + root, N) = {g}')
        if 1 < int(g) < int(N):
            log(f'  >>> FACTOR FOUND: {g} ({len(str(g))} digits)')
            if int(g) < int(F1):
                update_factor_file(p, int(g))
            return
    
    if not other_roots:
        log('  No Cipolla roots found (composite modulus limitation)')
    
    # Also try pairwise gcd of Cipolla roots with each other
    log('')
    log('Pairwise gcd among Cipolla roots:')
    for i in range(len(other_roots)):
        for j in range(i + 1, len(other_roots)):
            r1, r2 = other_roots[i], other_roots[j]
            g = gcd(r1 - r2, N)
            if 1 < int(g) < int(N):
                log(f'  >>> gcd(root_{i} - root_{j}, N) = {g} (FACTOR!)')
                if int(g) < int(F1):
                    update_factor_file(p, int(g))
                return
            g = gcd(r1 + r2, N)
            if 1 < int(g) < int(N):
                log(f'  >>> gcd(root_{i} + root_{j}, N) = {g} (FACTOR!)')
                if int(g) < int(F1):
                    update_factor_file(p, int(g))
                return
    
    log('')
    log('No factor found via Aurifeuillean + Cipolla combination')


if __name__ == '__main__':
    main()
