#!/usr/bin/env python3
"""
M(1237) factoring via Aurifeuillean identity + dual-sqrt approach.

Key idea:
- p = 1237, p ≡ 1 mod 4, so M(p) has Aurifeuillean factorization M(p) = A^2 - 2p*B^2.
- We already have F1 (70-digit prime Aurifeuillean factor).
- F2 = M(p)/F1 is 303-digit composite.
- Strategy: compute TWO different sqrt(2p) mod N (where N = F2). If they differ, gcd gives factor.

Sources of sqrt(2p) mod N:
  (1) Algebraic: sqrt(2) = 2^((p+1)/2)/2 = 2^619 mod N  [since 2^p ≡ 1 mod N]
                   sqrt(1237) mod N via polynomial GCD of Phi_p(x) and (x^2 - 1237)
                   sqrt(2p) = sqrt(2) * sqrt(1237) mod N
  (2) Tonelli-Shanks on composite N (mod 4 cases)
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, gcd, is_prime, isqrt, powmod, invert, jacobi
import time

print("=" * 70)
print("  M(1237) factoring via dual-sqrt(2p) approach")
print("=" * 70)

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
N = M // F1  # = F2, 303 digits

print(f"p = {P}, p mod 4 = {P % 4}")
print(f"F1 = {F1}  ({len(str(F1))} digits, prime: {is_prime(F1)})")
print(f"N = F2 = M(p)/F1  ({len(str(N))} digits, prime: {is_prime(N)})")
print()

# ============================================================
# Step 1: Check (1237/N) and (2/N) Jacobi symbols
# ============================================================
print("Step 1: Jacobi symbols")
print(f"  (2/N) = {jacobi(2, int(N))}")
print(f"  (1237/N) = {jacobi(1237, int(N))}")
print(f"  (2474/N) = (2*1237/N) = {jacobi(2474, int(N))}")
print()

# ============================================================
# Step 2: Compute sqrt(2) mod N = 2^619 mod N
# ============================================================
print("Step 2: sqrt(2) mod N = 2^619 mod N  (since 2^p ≡ 1 → 2^((p+1)/2) is a sqrt of 2)")
sqrt2 = powmod(2, 619, N)
print(f"  sqrt(2) = {str(sqrt2)[:50]}...")
print(f"  Verify: sqrt(2)^2 mod N == 2? {powmod(sqrt2, 2, N) == 2}")
print()

# ============================================================
# Step 3: Compute sqrt(1237) mod N via polynomial GCD
#         gcd(Phi_p(x), x^2 - 1237) over Z/NZ
#         If degree 1: sqrt(1237) exists and is unique (single value mod N)
#         If degree 0: doesn't exist (or GCD failed due to non-invertible leading coeff)
# ============================================================
print("Step 3: Compute sqrt(1237) mod N via polynomial GCD")
print("  Computing gcd(Phi_p(x), x^2 - 1237) over Z/NZ...")

t0 = time.time()

def poly_gcd_N(a_poly, b_poly, N_val):
    """Polynomial GCD over Z/N_val Z. Returns (gcd_poly, factor_found).
    If a non-trivial gcd with N_val is hit during inversion, returns (None, factor)."""
    a = [mpz(x) % N_val for x in a_poly]
    b = [mpz(x) % N_val for x in b_poly]
    # Strip leading zeros
    while a and a[-1] == 0: a.pop()
    while b and b[-1] == 0: b.pop()
    if not a: return (b, None)
    if not b: return (a, None)
    for step in range(1000000):
        if not b: return (a, None)
        while len(a) >= len(b):
            # Strip trailing zeros
            while a and a[-1] == 0: a.pop()
            if not a or len(a) < len(b): break
            lp = a[-1]
            lq = b[-1]
            # Try to invert lq mod N_val
            g = gcd(lq, N_val)
            if 1 < int(g) < int(N_val):
                return (None, int(g))  # factor found!
            if int(g) == int(N_val):
                # lq ≡ 0 mod N. Just pop and continue
                a.pop()
                continue
            # g == 1: invertible
            ratio = (lp * invert(lq, N_val)) % N_val
            shift = len(a) - len(b)
            for i in range(len(b)):
                a[shift + i] = (a[shift + i] - ratio * b[i]) % N_val
        a, b = b, a
    return (a, None)

# Phi_p(x) = 1 + x + x^2 + ... + x^(p-1) = (x^p - 1)/(x - 1)
Phi_p = [mpz(1)] * P  # 1237 coefficients, all = 1
# x^2 - 1237 mod N
neg_p = (-P) % int(N)
Q_poly = [mpz(neg_p), mpz(0), mpz(1)]

result, factor = poly_gcd_N(Phi_p, Q_poly, int(N))
t1 = time.time()
print(f"  Time: {t1 - t0:.1f}s")

if factor is not None:
    print(f"  >>> FACTOR FOUND during polynomial GCD: {factor}")
    if int(M) % factor == 0:
        print(f"  >>> REAL FACTOR of M(1237)! ({len(str(factor))} digits)")
        print(f"  is_prime: {is_prime(factor)}")
        cof = int(M) // factor
        print(f"  cofactor: {str(cof)[:60]}... ({len(str(cof))} digits)")
        print(f"  is_prime(cofactor): {is_prime(cof)}")
        sys.exit(0)
    else:
        print(f"  (not a factor of M(1237), spurious)")

if result is None:
    print(f"  GCD returned None unexpectedly")
    sys.exit(1)

# Strip zeros
while result and result[-1] == 0: result.pop()
deg = len(result) - 1 if result else -1
print(f"  gcd degree = {deg}")
print(f"  gcd = {result}")

if deg == 1:
    # x^2 ≡ 1237 mod N has a unique root mod each q_i, AND it's the same root!
    # gcd = c0 + c1*x → root = -c0/c1 mod N
    c0 = int(result[0]); c1 = int(result[1])
    if c1 == 0:
        print("  c1 = 0, can't invert")
    else:
        g = gcd(mpz(c1), N)
        if 1 < int(g) < int(N):
            print(f"  >>> FACTOR from c1: {g}")
            sys.exit(0)
        sqrt_1237 = (-c0 * int(invert(mpz(c1), N))) % int(N)
        print(f"  sqrt(1237) = {str(sqrt_1237)[:50]}...")
        print(f"  Verify: sqrt(1237)^2 mod N == 1237? {powmod(sqrt_1237, 2, N) == 1237}")
        
        # Now compute sqrt(2p) = sqrt(2) * sqrt(1237) mod N
        sqrt_2p_alg = (int(sqrt2) * sqrt_1237) % int(N)
        print(f"  sqrt(2p) [algebraic] = sqrt(2) * sqrt(1237) = {str(sqrt_2p_alg)[:50]}...")
        print(f"  Verify: (sqrt(2p))^2 mod N == 2474? {powmod(sqrt_2p_alg, 2, N) == 2474}")
        print()
        
        # Step 4: Compute ANOTHER sqrt(2p) mod N via Tonelli-Shanks on composite N
        print("Step 4: Compute alternative sqrt(2474) mod N via Tonelli-Shanks")
        print(f"  N mod 4 = {int(N) % 4}, N mod 8 = {int(N) % 8}")
        
        # Find v_2(N-1)
        Nm1 = int(N) - 1
        v2 = 0
        temp = Nm1
        while temp % 2 == 0:
            v2 += 1
            temp //= 2
        Q_ts = Nm1 >> v2  # odd part of N-1
        print(f"  v_2(N-1) = {v2}, Q = (N-1)/2^{v2} (odd)")
        
        # Find a quadratic non-residue z mod N
        z = None
        for zz in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113]:
            j = jacobi(zz, int(N))
            if j == -1:
                z = zz
                break
            if j == 0:
                # gcd(zz, N) > 1 — factor!
                g = gcd(zz, int(N))
                if 1 < int(g) < int(N):
                    print(f"  >>> FACTOR from Jacobi: {g}")
                    sys.exit(0)
        print(f"  Using non-residue z = {z}")
        if z is None:
            print("  No small non-residue found!")
            sys.exit(1)
        
        # Tonelli-Shanks on composite N
        # R^2 = a = 2474
        a = 2474
        M_ts = v2
        c_ts = powmod(z, Q_ts, N)  # z^Q
        t_ts = powmod(a, Q_ts, N)  # a^Q
        R_ts = powmod(a, (Q_ts + 1) // 2, N)  # a^((Q+1)/2)
        
        sqrt_2p_ts = None
        for iteration in range(100):
            if t_ts == 0:
                print(f"  TS iter {iteration}: t=0, R=0")
                break
            if t_ts == 1:
                print(f"  TS iter {iteration}: t=1, R is the sqrt")
                sqrt_2p_ts = int(R_ts)
                break
            # Find least i in [1, M_ts-1] with t^(2^i) = 1
            i_ts = None
            temp_t = t_ts
            for ii in range(1, M_ts + 1):
                temp_t = (temp_t * temp_t) % N
                if temp_t == 1:
                    i_ts = ii
                    break
                # Check if gcd gives a factor
                if temp_t == 0:
                    g = gcd(int(t_ts), int(N))
                    if 1 < int(g) < int(N):
                        print(f"  >>> FACTOR from TS intermediate t: {g}")
                        if int(M) % int(g) == 0:
                            print(f"  >>> REAL FACTOR! {g}")
                            sys.exit(0)
            if i_ts is None:
                print(f"  TS didn't find i, likely composite failure")
                # Check gcd of t_ts - 1
                g = gcd(int(t_ts) - 1, int(N))
                if 1 < int(g) < int(N):
                    print(f"  >>> FACTOR from t-1: {g}")
                    if int(M) % int(g) == 0:
                        print(f"  >>> REAL FACTOR! {g}")
                        sys.exit(0)
                break
            b_ts = powmod(c_ts, 1 << (M_ts - i_ts - 1), N)
            M_ts = i_ts
            c_ts = (b_ts * b_ts) % N
            t_ts = (t_ts * c_ts) % N
            R_ts = (R_ts * b_ts) % N
        
        if sqrt_2p_ts is not None:
            print(f"  sqrt(2p) [Tonelli-Shanks] = {str(sqrt_2p_ts)[:50]}...")
            print(f"  Verify: (sqrt)^2 mod N == 2474? {powmod(sqrt_2p_ts, 2, N) == 2474}")
            print()
            print(f"  Algebraic:  {str(sqrt_2p_alg)[:60]}")
            print(f"  T-Shanks:   {str(sqrt_2p_ts)[:60]}")
            print(f"  Equal?      {sqrt_2p_alg == sqrt_2p_ts}")
            print(f"  Negation?   {sqrt_2p_ts == int(N) - sqrt_2p_alg}")
            
            if sqrt_2p_alg != sqrt_2p_ts and sqrt_2p_ts != int(N) - sqrt_2p_alg:
                print(f"\n  >>> DIFFERENT square roots of 2p mod N!")
                g = gcd(abs(sqrt_2p_alg - sqrt_2p_ts), int(N))
                print(f"  gcd(R1 - R2, N) = {g}")
                if 1 < int(g) < int(N) and int(M) % int(g) == 0:
                    print(f"  >>> REAL FACTOR! {g} ({len(str(g))} digits)")
                    print(f"  is_prime: {is_prime(int(g))}")
                    cof = int(N) // int(g)
                    print(f"  cofactor: {str(cof)[:60]}... ({len(str(cof))} digits)")
                    print(f"  is_prime(cofactor): {is_prime(cof)}")
                    sys.exit(0)
                g = gcd(sqrt_2p_alg + sqrt_2p_ts, int(N))
                print(f"  gcd(R1 + R2, N) = {g}")
                if 1 < int(g) < int(N) and int(M) % int(g) == 0:
                    print(f"  >>> REAL FACTOR! {g}")
                    sys.exit(0)
            else:
                print(f"  Same or negation — no factor from this pair.")
                # Try also negating just one of sqrt(2), sqrt(1237):
                print()
                print("  Trying other combinations:")
                # -sqrt(2) * sqrt(1237)
                alt1 = (int(N) - int(sqrt2)) * sqrt_1237 % int(N)
                print(f"  alt1 = -sqrt(2)*sqrt(1237): verify sqrt(2p)? {powmod(alt1, 2, N) == 2474}")
                if powmod(alt1, 2, N) == 2474 and alt1 != sqrt_2p_ts and alt1 != int(N) - sqrt_2p_ts:
                    g = gcd(abs(alt1 - sqrt_2p_ts), int(N))
                    if 1 < int(g) < int(N) and int(M) % int(g) == 0:
                        print(f"  >>> FACTOR! {g}")
                        sys.exit(0)
                # sqrt(2) * -sqrt(1237)
                alt2 = int(sqrt2) * (int(N) - sqrt_1237) % int(N)
                print(f"  alt2 = sqrt(2)*(-sqrt(1237)): verify? {powmod(alt2, 2, N) == 2474}")
                if powmod(alt2, 2, N) == 2474 and alt2 != sqrt_2p_ts and alt2 != int(N) - sqrt_2p_ts:
                    g = gcd(abs(alt2 - sqrt_2p_ts), int(N))
                    if 1 < int(g) < int(N) and int(M) % int(g) == 0:
                        print(f"  >>> FACTOR! {g}")
                        sys.exit(0)
                # If all combos fail: N's prime factors all share same sqrt(2p) value.
                print("  All algebraic combos give same sqrt. Need different approach.")
        else:
            print(f"  Tonelli-Shanks did not produce a sqrt (failed on composite N).")
            # Check intermediate values for factors
            for label, val in [("R_ts", int(R_ts)), ("c_ts", int(c_ts)), ("t_ts", int(t_ts))]:
                for delta in [val - 1, val + 1]:
                    g = gcd(abs(delta), int(N))
                    if 1 < int(g) < int(N) and int(M) % int(g) == 0:
                        print(f"  >>> FACTOR from {label}±1: {g}")
                        sys.exit(0)

elif deg == 0:
    print(f"  gcd is constant ({result if result else 'empty'}). sqrt(1237) does NOT exist mod all of N.")
    print(f"  This means at least one prime q_i | N has (1237/q_i) = -1.")
    # Try gcd(Phi_p(x), x^2 - 1237) differently — maybe via Phi_p(sqrt(1237))?
    # Or use (2*1237 = 2474) directly
    print()
    print("  Trying gcd(Phi_p(x), x^2 - 2474) directly:")
    neg_a = (-2474) % int(N)
    Q_poly2 = [mpz(neg_a), mpz(0), mpz(1)]
    result2, factor2 = poly_gcd_N(Phi_p, Q_poly2, int(N))
    if factor2:
        print(f"  >>> FACTOR from direct 2474: {factor2}")
        if int(M) % int(factor2) == 0:
            print(f"  >>> REAL FACTOR! {factor2}")
            sys.exit(0)
    if result2:
        while result2 and result2[-1] == 0: result2.pop()
        deg2 = len(result2) - 1 if result2 else -1
        print(f"  gcd(Phi_p, x^2-2474) degree = {deg2}")
        if deg2 == 1:
            c0 = int(result2[0]); c1 = int(result2[1])
            sqrt_2474 = (-c0 * int(invert(mpz(c1), N))) % int(N)
            print(f"  sqrt(2474) = {str(sqrt_2474)[:50]}...")
            print(f"  Verify: (sqrt)^2 mod N == 2474? {powmod(sqrt_2474, 2, N) == 2474}")
            # Compare with Tonelli-Shanks for sqrt(2474)
            # ... (similar to above)
else:
    print(f"  gcd degree = {deg}, unexpected (composite factors differ in their sqrt(1237) mod)")
    # This is the GOOD case! Means sqrt(1237) differs mod different q_i.
    # gcd(Phi_p, x^2 - 1237) of degree 2 means x^2 - 1237 splits Phi_p into 2 components.
    # The gcd itself is a product of factors giving different sqrt(1237).
    # Actually: if deg = 2, gcd = x^2 - 1237 itself, meaning all roots of Phi_p satisfy x^2=1237.
    # Hmm that's a different case.
    # If gcd has degree 2: it's (x^2 - 1237) mod N, but mod each q_i it could be different linear factors
    # If N = q1*q2 with sqrt(1237) mod q1 ≠ sqrt(1237) mod q2:
    #   gcd over Z/N might still appear as degree 1 (since x - r1 mod q1 and x - r2 mod q2 → gcd doesn't simplify)
    # Hmm.
    print(f"  gcd coeffs: {result}")

print()
print("=" * 70)
print("  Approach did not yield a factor. Need to try other methods (ECM, etc.)")
print("=" * 70)
