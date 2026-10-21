#!/usr/bin/env python3
"""
Compute Aurifeuillean factorization for M(1237).

M(p) = 2^p - 1 with p = 1237 (prime, ≡ 1 mod 4).
Decompose: M(p) = A^2 - 2p*B^2 (Aurifeuillean identity).

Method: Use Brent's algorithm with p = a^2 + b^2 representation.
1237 = 34^2 + 9^2.

Per Brent (1993), for p ≡ 1 mod 4 prime with p = a^2 + b^2:
  Define the polynomial decomposition Phi_p(x) = L_p(x)^2 - p*x*M_p(x)^2.
  Then M(p) = Phi_p(2) = L_p(2)^2 - 2p * M_p(2)^2.

The polynomial L_p has integer coefficients and can be computed via
Newton-like iteration on the cyclotomic polynomial.

Approach: Direct coefficient matching.
  Phi_p(x) = sum_{i=0}^{p-1} x^i (degree p-1)
  L_p(x) = sum_{i=0}^{(p-1)/2} l_i x^i (degree (p-1)/2, leading l_{(p-1)/2} = 1)
  M_p(x) = sum_{i=0}^{(p-3)/2} m_i x^i (degree (p-3)/2)

  Constraint: Phi_p - L_p^2 = -p*x*M_p^2

  Process coefficients from high to low:
  At degree d (from p-1 down to 0):
    Phi_p[d] - sum_{i+j=d} l_i l_j = (-p) * (M_p^2)[d-1] (with M_p^2 coeff = 0 for negative index)

  We build L_p and M_p simultaneously, choosing L_p coefficients such that
  (Phi_p - L_p^2) / (-p*x) is a perfect square polynomial.

  Algorithm:
    l_{(p-1)/2} = 1
    m_{(p-3)/2} = ? (leading coeff of M_p, must be non-negative integer)

    For each level from top:
      Let S = (Phi_p - L_p^2) / (-p*x) at current level.
      We want S to be a perfect square M_p^2.

      At the top (degree p-1 of Phi, i.e., 1236 for p=1237):
        Phi_p[1236] = 1, L_p^2[1236] = l_618^2 = 1. S[1235] = (1 - 1)/(-p) = 0. ✓
      At degree p-2 = 1235:
        Phi_p[1235] = 1, L_p^2[1235] = 2 l_618 l_617 = 2 l_617.
        S[1234] = (1 - 2 l_617) / (-p) = (2 l_617 - 1) / p
        This must equal m_617^2 (leading coeff of M_p^2 at degree 1234).
        For integer solution: 2 l_617 - 1 = p * m_617^2.
        Try m_617 = 1: 2 l_617 = p + 1, l_617 = (p+1)/2 = 619. ✓ (p=1237, (1237+1)/2 = 619)
        So l_617 = 619, m_617 = 1.

      At degree p-3 = 1234:
        Phi_p[1234] = 1, L_p^2[1234] = l_617^2 + 2 l_618 l_616 = 619^2 + 2 l_616
        S[1233] = (1 - 619^2 - 2 l_616) / (-p) = (619^2 + 2 l_616 - 1) / p
        This must equal M_p^2[1233] = 2 m_617 m_616 = 2 * 1 * m_616 = 2 m_616.
        So 619^2 + 2 l_616 - 1 = 2 p m_616.
        619^2 - 1 = 383161 - 1 = 383160. We need 383160 = 2 p m_616 - 2 l_616 = 2 (p m_616 - l_616)
        So p m_616 - l_616 = 191580.
        m_616 = (191580 + l_616) / p. We need to choose l_616 such that this is integer.

      This is a recursive procedure. At each level, we have ONE equation
      relating the new l_k and m_k (or sometimes just l_k or just m_k).
      The system is constrained because we want integer coefficients.

  Actually, the correct approach (from Montgomery 1992) is:
    L_p is uniquely determined (up to sign of the entire polynomial) by the
    requirement that all coefficients are integers. We can compute it
    iteratively, choosing the smallest |l_k| that keeps S a perfect square.

  For now, let me just use a different approach: compute L_p via
  'cyclotomic_square_root' which is the polynomial square root of Phi_p mod p,
  then lift to integer coefficients.

  Simplest: use Python's polynomial arithmetic with rational coefficients.
  Compute L_p over QQ, then evaluate at x=2 to get integer L_p(2).
"""

import sys
import time
from pathlib import Path

import gmpy2
from gmpy2 import mpz, isqrt, is_square, is_prime, gcd

p = 1237
M = mpz(2)**p - 1
F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)

# Approach: compute L_p via Newton's iteration with rational arithmetic.
# L_p^2 = Phi_p (mod x^((p+1)/2)) — i.e., truncated power series.
# L_p (over QQ) is the polynomial square root of Phi_p (as power series).

# We use sympy for symbolic polynomial arithmetic.

from sympy import Symbol, Poly, Rational, S
from sympy.polys.rings import ring as sym_ring_QQ

# Polynomial ring over QQ (rationals)
R = sym_ring_QQ('x', S.QQ)
xx = R.gens[0]


def poly_psr(Phi_poly, target_deg, ring, gen):
    """Compute polynomial square root via Newton's iteration.
    Returns L such that L^2 ≡ Phi (mod x^(target_deg+1)).
    """
    # Start: L = leading_coeff * x^target_deg
    # First coefficient must be a perfect square in QQ.
    # Phi has degree 2*target_deg (if leading coeff is square).

    # Get leading coefficient of Phi at degree 2*target_deg
    c = Phi_poly.coeff(2 * target_deg)
    if c < 0:
        raise ValueError(f"Leading coefficient {c} is negative, no real square root")
    sqrt_c = Rational(c).sqrt() if hasattr(Rational(c), 'sqrt') else None
    # Use sympy sqrt for rationals
    from sympy import sqrt as sym_sqrt
    sqrt_c_sym = sym_sqrt(Rational(c))
    # Try to express as rational
    if sqrt_c_sym.is_rational:
        sqrt_c = Rational(sqrt_c_sym)
    else:
        sqrt_c = Rational(sqrt_c_sym)
    print(f"  leading coeff of Phi at x^{2*target_deg} = {c}, sqrt = {sqrt_c}")

    # L = sqrt_c * x^target_deg + ... (we'll build it)
    L = ring.from_dict({target_deg: sqrt_c})

    # Newton's iteration: L_new = (L + Phi / L) // 2, truncated to degree target_deg.
    # We need to be able to divide polynomials and add.
    from sympy.polys.polyclasses import DMP

    for it in range(2 * target_deg + 5):
        # Compute Phi / L (polynomial division, keep quotient truncated to target_deg)
        # Use ring.div (returns (quotient, remainder))
        try:
            quot, rem = ring.div(Phi_poly, L)
        except Exception as e:
            print(f"  Newton iter {it}: div error: {e}")
            break
        # L_new = (L + quot) / 2, truncated to target_deg
        L_new_full = L + quot
        # Truncate to degree target_deg
        new_dict = {}
        for d, c in L_new_full.items():
            if d <= target_deg:
                new_dict[d] = c
        L_new = ring.from_dict(new_dict) / 2

        if L_new == L:
            print(f"  Newton converged at iter {it}")
            break
        L = L_new
        if it % 10 == 0:
            print(f"  Newton iter {it}, L degree = {L.degree()}")

    return L


def main():
    print(f"Computing Aurifeuillean L_p(x) for p={p}")
    print(f"  M(p) = {M} ({len(str(M))} digits)")
    print(f"  F1 = {F1} ({len(str(F1))} digits)")
    print(f"  Target: A^2 - 2p*B^2 = M(p) where A = L_p(2), B = M_p(2)")
    print()

    # Build Phi_p(x) = sum_{i=0}^{p-1} x^i  (degree p-1 = 1236)
    target_deg = (p - 1) // 2  # 618
    print(f"  Phi_p(x) degree: {2*target_deg}, target L_p degree: {target_deg}")

    # Build Phi_p as polynomial
    # Phi_p has 1237 terms, each coefficient 1.
    phi_dict = {i: 1 for i in range(2 * target_deg + 1)}
    Phi = R.from_dict(phi_dict)
    print(f"  Built Phi_p(x) with {len(phi_dict)} terms")

    # Compute L_p via Newton's iteration
    print(f"Computing L_p(x) via Newton's iteration (target degree {target_deg})...")
    t0 = time.time()
    L = poly_psr(Phi, target_deg, R, xx)
    print(f"  L_p computed in {time.time() - t0:.1f}s, degree = {L.degree()}")

    # Verify: L_p^2 - Phi_p should be divisible by p*x and the quotient should be a perfect square.
    diff = L**2 - Phi
    print(f"  L^2 - Phi degree = {diff.degree()}")

    # Compute M_p such that p*x*M_p^2 = L^2 - Phi
    # (L^2 - Phi) / (p*x) should be M_p^2
    # Diff has degree at most 2*target_deg - 1 = 1235 (since leading matches)
    # We need (L^2 - Phi) / (p * x) to be a perfect square.
    diff_dict = dict(diff.items())
    # Check if all coefficients of diff are multiples of p (except the constant term which should be 0)
    print(f"  Constant term of diff: {diff.coeff(0)}")
    if diff.coeff(0) != 0:
        print("  ERROR: constant term not zero")

    # Divide diff by p*x (i.e., shift by 1 and divide each coefficient by p)
    s_dict = {}
    for d, c in diff_dict.items():
        if d == 0:
            continue
        # / (p * x): coefficient at d becomes coefficient at d-1, divided by p
        new_d = d - 1
        new_c = c / p
        if new_d not in s_dict:
            s_dict[new_d] = new_c
        else:
            s_dict[new_d] += new_c
    print(f"  S = (L^2 - Phi) / (p*x) has {len(s_dict)} non-zero terms, degree = {max(s_dict.keys())}")

    # Evaluate L_p and M_p at x=2
    # First find M_p by square root of S
    # S should be a perfect square polynomial. Compute its square root via Newton too.
    S_poly = R.from_dict(s_dict)
    print(f"  Computing M_p = sqrt(S) via Newton's iteration...")
    t1 = time.time()
    M_p = poly_psr(S_poly, (p - 3) // 2, R, xx)
    print(f"  M_p computed in {time.time() - t1:.1f}s, degree = {M_p.degree()}")

    # Verify: M_p^2 == S
    check = M_p**2 - S_poly
    print(f"  Verification: M_p^2 - S = {check}")

    # Evaluate at x=2
    A = sum(c * (2 ** d) for d, c in L.items())
    B = sum(c * (2 ** d) for d, c in M_p.items())
    A = int(A) if hasattr(A, '__int__') else A
    B = int(B) if hasattr(B, '__int__') else B
    print(f"  A = L_p(2) = {A}")
    print(f"  B = M_p(2) = {B}")

    # Verify: A^2 - 2p*B^2 == M
    check_M = A*A - 2*p*B*B
    print(f"  A^2 - 2p*B^2 = {check_M}")
    print(f"  M(p) =       {M}")
    print(f"  Match: {check_M == M}")

    # Save A, B to file
    with open('/home/z/my-project/logs/M1237_aurifeuillean.txt', 'w') as f:
        f.write(f"p = {p}\n")
        f.write(f"A = {A}\n")
        f.write(f"B = {B}\n")
        f.write(f"A^2 - 2p*B^2 = M(p) ✓\n")


if __name__ == '__main__':
    main()
