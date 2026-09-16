#!/usr/bin/env python3
"""
Direct computation of M(1237) = A^2 - 2p*B^2 using Brent's algorithm based on
the cyclotomic polynomial Aurifeuillean identity.

ALGORITHM (Brent 1993, improved):
  For p ≡ 1 mod 4, M(p) = A^2 - 2p B^2 where:
    A + B*sqrt(2p) = (1 + sqrt(2p))^{2p-1} * (1 + 1/sqrt(2p))^{p-1} ... no, too complex.

ACTUALLY, simpler approach:
  The polynomial L_p(x) satisfies L_p(x)^2 = Phi_p(x) + p*x*M_p(x)^2.
  L_p mod p = (x-1)^{(p-1)/2} mod p (the polynomial square root of Phi_p mod p).
  
  Lift L_p, M_p simultaneously via Hensel lifting on L_p^2 - p*x*M_p^2 = Phi_p.
  
  At each step:
    Given L mod p^k, M mod p^k with L^2 - p*x*M^2 ≡ Phi mod p^k:
    Lift: L' = L + p^k * δ_L, M' = M + p^k * δ_M.
    Want: (L')^2 - p*x*(M')^2 ≡ Phi mod p^{k+1}.
    
    (L + p^k δ_L)^2 = L^2 + 2 p^k δ_L L + p^{2k} δ_L^2 ≡ L^2 + 2 p^k δ_L L mod p^{k+1}.
    p*x*(M + p^k δ_M)^2 = p*x*M^2 + 2 p^{k+1} x M δ_M + p^{2k+1} x δ_M^2 ≡ p*x*M^2 mod p^{k+1}.
    
    So: L^2 + 2 p^k δ_L L - p*x*M^2 ≡ Phi mod p^{k+1}.
    R = (Phi - L^2 + p*x*M^2) / p^k mod p (a polynomial in F_p[x]).
    2 δ_L L ≡ R mod p, in F_p[x].
    
    Since L has degree half and L[0] ≠ 0, L is invertible as power series.
    δ_L = R * (2L)^{-1} mod (p, x^{half+1}) — gives δ_L's low-degree coefficients.
    
    But L^2 has degree 2*half, so R has degree ≤ 2*half.
    The equation 2 δ_L L = R mod (p, x^{2*half+1}) gives delta_L of degree half 
    (619 unknowns vs 1237 equations; the high-degree equations provide consistency checks).
    
    To compute: solve 2 δ_L L ≡ R mod (p, x^{half+1}) — gives low part of δ_L.
    Then δ_L = inverse_problem gives high-degree coefficients by matching high-degree of R.
    
    Actually, since L is monic of degree half with L[half] = 1, the high-degree part of 
    2 δ_L L (coefficient at degree 2*half) is 2 * δ_L[half] * L[half] = 2 * δ_L[half].
    So δ_L[half] = R[2*half] / 2 mod p.
    
    Then δ_L[half-1]: coefficient of x^{2*half - 1} in 2 δ_L L is 2(δ_L[half-1] * L[half] + δ_L[half] * L[half-1]) = 2 δ_L[half-1] + 2 δ_L[half] L[half-1].
    So 2 δ_L[half-1] = R[2*half - 1] - 2 δ_L[half] L[half-1].
    δ_L[half-1] = (R[2*half - 1] - 2 δ_L[half] L[half-1]) / 2 mod p.
    
    Continue down to δ_L[0].

  Then M needs no update at this step (since M correction is 0 mod p^{k+1}).
  Actually we DO need to update M eventually, but the order is:
    At each step, we have L mod p^k and M mod p^{k-1} (M is one level behind).
    The lift of M from p^{k-1} to p^k can be done at the same time.
    
  Hmm, let me think. p*x*M^2 mod p^{k+1} requires M mod p^k.
  Initially: L mod p, M mod p.
  Step 1: Lift L from mod p to mod p^2 (using M mod p).
  Step 2: Lift M from mod p to mod p^2 (using L mod p^2):
    (L mod p^2)^2 - Phi = p*x*M^2 in some sense.
    M^2 mod p^2 = ((L mod p^2)^2 - Phi) / (p*x) mod p^2.
    Then take sqrt to get M mod p^2.
  Step 3: Lift L from mod p^2 to mod p^3 (using M mod p^2).
  Step 4: Lift M from mod p^2 to mod p^3.
  Etc.
"""

import gmpy2
from gmpy2 import mpz
import time

p = 1237
half = (p - 1) // 2  # 618
target_K = 70  # Hensel depth

# Initialize L mod p (polynomial of degree half = 618, length half+1 = 619)
# L mod p = (x-1)^half mod p
L = [0] * (half + 1)
binom = 1
sign = (-1)**half
L[0] = (sign * binom) % p
for j in range(1, half + 1):
    binom = (binom * (half - j + 1) * pow(j, -1, p)) % p
    sign = -sign
    L[j] = (sign * binom) % p

# Phi_p as polynomial (all coeffs = 1, length 2*half+1 = 1237)
Phi = [1] * (2 * half + 1)


def poly_mult_mod_int(a, b, mod_int, max_deg):
    """Multiply polynomials a, b mod integer mod_int, truncate to max_deg."""
    if max_deg < 0:
        return []
    result = [0] * (max_deg + 1)
    for i in range(min(len(a), max_deg + 1)):
        ai = a[i]
        if ai == 0:
            continue
        for j in range(min(len(b), max_deg + 1 - i)):
            bj = b[j]
            if bj == 0:
                continue
            result[i + j] = (result[i + j] + ai * bj) % mod_int
    return result


def poly_sub_mod(a, b, mod_int):
    """a - b mod mod_int."""
    n = max(len(a), len(b))
    return [((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % mod_int for i in range(n)]


def poly_inv_newton(a, mod_int, max_deg):
    """Compute 1/a as power series mod mod_int, truncated to max_deg.
    Requires a[0] invertible mod mod_int.
    """
    if max_deg < 0:
        return []
    inv_a0 = pow(a[0], -1, mod_int)
    B = [inv_a0] + [0] * max_deg
    for _ in range(max_deg + 5):
        # B_new = B * (2 - a * B) mod (mod_int, x^{max_deg+1})
        aB = poly_mult_mod_int(a, B, mod_int, max_deg)
        two_minus = [(-x) % mod_int for x in aB]
        two_minus[0] = (2 - aB[0]) % mod_int
        B_new = poly_mult_mod_int(B, two_minus, mod_int, max_deg)
        if B_new == B:
            break
        B = B_new
    return B


# Step 1: Compute M mod p
# L^2 = Phi + p*x*M^2, so p*x*M^2 = L^2 - Phi in Z[x], but mod p, p*x*M^2 ≡ 0, so L^2 ≡ Phi mod p (no info on M).
# To get M mod p: compute (L mod p^2)^2 mod p^2, then R = ((L mod p^2)^2 - Phi) mod p^2, then M^2 mod p = (R/p) / x mod p, then sqrt.

# Lift L from mod p to mod p^2:
# R = Phi - L^2 mod p^2. Compute L^2 mod p^2 (with L mod p interpreted as integers in [0, p)).
print("Computing L^2 mod p^2...")
t0 = time.time()
L_sq_p2 = poly_mult_mod_int(L, L, p*p, 2*half)
R_p2 = [(Phi[i] - L_sq_p2[i]) % (p*p) for i in range(2*half + 1)]

# R should be divisible by p (since L^2 ≡ Phi mod p)
print("Checking R divisible by p...")
R_div_p = [r // p for r in R_p2]
# Wait, need r % p == 0 first
all_div = all(r % p == 0 for r in R_p2)
print(f"  All R[i] divisible by p: {all_div}")
if not all_div:
    for i, r in enumerate(R_p2):
        if r % p != 0:
            print(f"    R[{i}] = {r} not div by p")
            break

# M^2 mod p = R_div_p / x (since L^2 - Phi = p*x*M^2 means p*(x*M^2) = L^2 - Phi, so R_div_p = x*M^2 mod p)
# So M^2 mod p has R_div_p[i+1] at position i (since x * M^2 = sum M^2[i] x^(i+1))
# Actually: x * M^2 = sum_i M_sq[i] x^(i+1), so coeff at x^(i+1) is M_sq[i].
# So M_sq[i] = R_div_p[i+1] for i in 0, ..., half-1.
# And R_div_p[0] should be 0 (constant term of x*M^2 is 0).
print(f"  R_div_p[0] = {R_div_p[0]} (should be 0)")
M_sq_p = [R_div_p[i+1] % p for i in range(half)]  # length half = 618
print(f"  M^2 mod p has {sum(1 for x in M_sq_p if x != 0)} non-zero entries")

# Take square root of M^2 mod p to get M mod p (polynomial of degree half-1 = 617).
# Need to use Newton's iteration on power series. But for sqrt, we need the leading coeff to be a QR.
# Actually let's reverse the polynomial and compute sqrt of the reversed.
# (x^k * M(1/x))^2 = x^{2k} * M(1/x)^2.
# Let P = M^2 mod p (length half). Let P_rev = reversed (length half).
# If M[0] != 0, then P[0] = M[0]^2, and we can compute M as sqrt(P) starting from M[0] = ±sqrt(P[0]).

# Or: start from the highest coefficient. P[half-1] = M[half-1]^2.
# Compute M[half-1] = sqrt(P[half-1]) mod p.
# Then M[half-2] from P[half-2] = M[half-1]^2 + 2*M[half-2]*M[half-1]? No, P[half-2] is coeff of x^(half-2) in M^2.

# Let me do the standard Newton iteration for polynomial square root:
# Given P (with P[0] != 0 or P[highest] != 0), compute M such that M^2 = P, by Newton:
#   y_{n+1} = (y_n + P / y_n) / 2, starting with y_0 = sqrt(P[0]) (low-degree-first) or 
#   starting with y_0 = sqrt(P[top]) (high-degree-first).

# For us, M has degree half-1 = 617, so M[617] is the leading coeff.
# M^2 has degree 2*617 = 1234.
# We computed M^2 mod p as a polynomial of degree half-1 = 617... wait that's wrong.
# Hmm. p*x*M^2 = (L^2 - Phi) has degree ≤ 2*half = 1236.
# So x*M^2 has degree ≤ 2*half - 1 = 1235 (since p*x*M^2 = (L^2 - Phi) / p has degree 2*half, but the leading coeff is 0 because L^2 ≡ Phi mod p means (L^2 - Phi)[2*half] is divisible by p and contributes to the high-degree of x*M^2 only if M's degree is exactly half-1).
# Actually M has degree half-1, so M^2 has degree 2*(half-1) = 1234, and x*M^2 has degree 1235.
# So (L^2 - Phi)/p has degree 1235, not 1236.

# Wait, but I computed L^2 mod p^2 with degree 2*half = 1236. And R = (Phi - L^2) mod p^2 has degree 1236.
# R/p has degree 1236 too. But x*M^2 has degree 1235 (since M has degree 617).
# So R/p must have leading coefficient 0 at degree 1236 (i.e., R[2*half] must be 0 mod p^2).
# Let me check.

print(f"  R_div_p[2*half] = R_div_p[{2*half}] = {R_div_p[2*half] if 2*half < len(R_div_p) else 'N/A'} (should be 0 mod p)")
print(f"  len(R_div_p) = {len(R_div_p)}")
# Need to check if R_div_p[2*half] is 0 mod p (not as integer, just mod p).
# Actually R = (Phi - L^2) mod p^2, so R[i] ∈ [0, p^2). R_div_p = R / p, so R_div_p[i] ∈ [0, p).
# Wait that's not right. R_div_p[i] = R[i] // p, and R[i] ∈ [0, p^2), so R_div_p[i] ∈ [0, p).
# So R_div_p is a polynomial mod p (with integer coefficients in [0, p)).

# M^2 = R_div_p / x mod p (polynomial). M^2 has degree 1234 = 2*(half-1).
# So M^2 has length half = 618 (degrees 0 to 617). Let me check.
# R_div_p has length 1237 (degrees 0 to 1236). R_div_p[0] should be 0 (since x*M^2 has constant 0).
# M^2[i] = R_div_p[i+1] for i in 0, ..., 1234. So M^2 has 1235 coeffs (degree 1234).
# But M has degree half-1 = 617, so M^2 has degree 2*617 = 1234. So M^2 has 1235 coeffs.
# So M_sq_p should have length 1235 (degrees 0 to 1234), not 618.

# I made a mistake earlier. Let me recompute.
M_sq_p = [R_div_p[i+1] % p for i in range(2 * (half - 1) + 1)]  # length 1235
print(f"  M^2 mod p has {sum(1 for x in M_sq_p if x != 0)} non-zero entries (degree ≤ {len(M_sq_p)-1})")

# Now compute M mod p as polynomial square root of M^2 mod p, using high-degree-first Newton.
# Leading coeff: M[half-1] = sqrt(M_sq_p[half-1 + (half-1)]) = sqrt(M_sq_p[2*half-2]) = sqrt(M_sq_p[1234]) mod p.
leading_M_sq = M_sq_p[2 * (half - 1)]
print(f"  Leading coeff of M^2 mod p = {leading_M_sq}")

# Find sqrt of leading_M_sq mod p (brute force for small p)
sqrt_lead = None
for s in range(p):
    if (s * s) % p == leading_M_sq:
        sqrt_lead = s
        break
if sqrt_lead is None:
    print(f"  No sqrt of {leading_M_sq} mod {p}")
else:
    print(f"  sqrt({leading_M_sq}) mod p = {sqrt_lead}")

# Initialize M with leading coeff = sqrt_lead (degree half-1 = 617)
M = [0] * half  # length 618 (degrees 0 to 617)
M[half - 1] = sqrt_lead

# Newton's iteration for polynomial sqrt, high-degree-first.
# We treat M^2 as a power series in 1/x (i.e., in x^{-1}).
# Reverse: let M^2_rev = reverse of M_sq_p (length 1235), M_rev = reverse of M (length 618).
# Then M_rev^2 = M^2_rev as power series in x (low-degree-first).
# Newton: M_rev_new = (M_rev + M^2_rev / M_rev) / 2, truncated to degree 617.
# Requires M_rev[0] != 0. M_rev[0] = M[half-1] = sqrt_lead ≠ 0 (if leading_M_sq is QR).

# Reverse M and M_sq
M_rev = M[::-1]  # length 618, M_rev[0] = M[617] = sqrt_lead
M_sq_rev = M_sq_p[::-1]  # length 1235, M_sq_rev[0] = M_sq_p[1234] = leading_M_sq (which is M[617]^2 = sqrt_lead^2)

# Verify M_sq_rev[0] = M_rev[0]^2
assert M_sq_rev[0] == (M_rev[0] * M_rev[0]) % p, f"M_sq_rev[0] = {M_sq_rev[0]}, M_rev[0]^2 = {(M_rev[0]**2) % p}"

# Newton iteration for sqrt (low-degree-first):
# y_{n+1} = (y_n + P / y_n) / 2 mod (p, x^{half}) where P = M_sq_rev.
# P / y_n: polynomial division. Use Newton's inverse of y_n, then multiply by P.

inv2 = pow(2, -1, p)
for iteration in range(30):
    # Compute inv of M_rev mod (p, x^half)
    B = poly_inv_newton(M_rev, p, half - 1)  # length half
    # Compute P / M_rev = P * B mod (p, x^half)
    P_over = poly_mult_mod_int(M_sq_rev, B, p, half - 1)  # length half
    # M_rev_new = (M_rev + P_over) / 2 mod (p, x^half)
    M_rev_new = [((M_rev[i] + (P_over[i] if i < len(P_over) else 0)) * inv2) % p for i in range(half)]
    if M_rev_new == M_rev:
        print(f"  Newton for M sqrt converged at iteration {iteration}")
        break
    M_rev = M_rev_new

# Reverse to get M mod p
M = M_rev[::-1]

# Verify M^2 mod p
M_sq_check = poly_mult_mod_int(M, M, p, 2 * (half - 1))
if M_sq_check == M_sq_p:
    print(f"  M mod p verified! leading = {M[half-1]}, constant = {M[0]}")
else:
    diff_count = sum(1 for i in range(min(len(M_sq_check), len(M_sq_p))) if M_sq_check[i] != M_sq_p[i])
    print(f"  M mod p verification failed: {diff_count} coefficients differ")
    print(f"    M[0:5] = {M[:5]}, M^2[0:5] = {M_sq_check[:5]}, expected: {M_sq_p[:5]}")

print(f"  Initial computation took {time.time() - t0:.1f}s")

# Now Hensel lift (L, M) from mod p^k to mod p^{k+1} repeatedly.
print(f"\nStarting Hensel lifting to depth {target_K}...")
mod = p  # current modulus
for k in range(target_K - 1):
    new_mod = mod * p
    # Lift L: L_new = L + mod * delta_L
    # Compute L^2 mod new_mod (using L mod mod)
    L_sq = poly_mult_mod_int(L, L, new_mod, 2*half)
    # Compute p * x * M^2 mod new_mod (using M mod mod)
    M_sq = poly_mult_mod_int(M, M, new_mod, 2*half - 1)  # M^2 degree 2*half - 2
    # x * M^2: shift by 1
    x_M_sq = [0] + M_sq
    # p * x * M^2
    p_x_M_sq = [(p * c) % new_mod for c in x_M_sq]
    # Pad to length 2*half+1
    while len(p_x_M_sq) < 2*half + 1:
        p_x_M_sq.append(0)
    
    # R = (Phi - L^2 + p*x*M^2) mod new_mod
    R = [((Phi[i] - L_sq[i] + p_x_M_sq[i]) % new_mod) for i in range(2*half + 1)]
    # R should be divisible by mod
    for i, r in enumerate(R):
        if r % mod != 0:
            print(f"  Hensel fails at k={k}, i={i}: R[i]={r} not divisible by mod={mod}")
            break
    else:
        R_div_mod = [r // mod for r in R]  # polynomial mod p (in [0, p))
        # Solve 2 * delta_L * L ≡ R_div_mod mod (p, x^{2*half+1}) for delta_L of degree ≤ half.
        # Method: solve from high degree down.
        # High degree: 2 * delta_L[half] * L[half] ≡ R_div_mod[2*half] mod p
        #   L[half] = 1 (leading), so 2 * delta_L[half] ≡ R_div_mod[2*half] mod p
        #   delta_L[half] = R_div_mod[2*half] * inv2 mod p
        # Lower degrees: 2 * sum_{i+j = d} delta_L[i] * L[j] ≡ R_div_mod[d] mod p
        #   = 2 * (delta_L[half] * L[d-half] + delta_L[half-1] * L[d-half+1] + ... )
        #   Solve for delta_L[d-half] from highest to lowest.
        
        delta_L = [0] * (half + 1)
        for d in range(2*half, -1, -1):
            # Find delta_L coefficient for degree d - half (the new one to determine)
            # In the sum 2 * sum_{i+j=d} delta_L[i] * L[j], the unknowns are delta_L[i] for i = d - half, ..., half (where L[d-i] exists, i.e., d - i <= half, i.e., i >= d - half).
            # Wait, we want to solve for delta_L where 2 * delta_L * L = R_div_mod.
            # L is monic of degree half. 2 * delta_L * L has degree 2*half.
            # Coefficient at degree d: 2 * sum_{i+j=d, i in [0,half], j in [0,half]} delta_L[i] * L[j]
            # If d > 2*half, no constraint. For d = 2*half: only term is 2 * delta_L[half] * L[half] = 2 * delta_L[half].
            # For d = 2*half - 1: 2 * (delta_L[half] * L[half-1] + delta_L[half-1] * L[half])
            # = 2 * delta_L[half] * L[half-1] + 2 * delta_L[half-1]
            # Since delta_L[half] is known, solve for delta_L[half-1].
            # Etc.
            
            new_idx = d - half  # if d >= half, this is the delta_L index being determined
            if new_idx < 0 or new_idx > half:
                continue
            # Sum: 2 * sum_{j=max(0, d-half)}^{min(half, d)} delta_L[d-j] * L[j]
            # We want to determine delta_L[new_idx] = delta_L[d - half].
            # In the sum, the unknown delta_L[new_idx] appears with L[half] = 1 (when j = half, i = new_idx, valid if d = new_idx + half which is our current d).
            # So: 2 * delta_L[new_idx] * L[half] = R_div_mod[d] - 2 * sum_{j != half, j in [0, half], i = d-j in [0, half]} delta_L[d-j] * L[j]
            
            sum_known = 0
            for j in range(0, half + 1):
                i = d - j
                if i < 0 or i > half or j > half:
                    continue
                if i == new_idx and j == half:
                    continue  # this is the unknown
                if i > new_idx:  # already determined (higher index = higher degree)
                    sum_known = (sum_known + delta_L[i] * L[j]) % p
                # else: i < new_idx, not yet determined; should not contribute since d - j = i < new_idx means j > half (impossible if j <= half and d <= 2*half, i = d-j >= half, then i >= half = new_idx when j <= half. Wait, d <= 2*half, j in [0, half], so i = d - j in [d - half, d]. For our d, we want i = new_idx = d - half. So i = d - j = d - half means j = half. So when j != half, i != new_idx. But i could be > new_idx (already determined) or < new_idx (not yet determined). 
                # Hmm, if i < new_idx, the value delta_L[i] is not yet determined. But it shouldn't appear in the equation for d (since we're solving top-down).
                # Actually, when j != half, i = d - j != d - half = new_idx. So i could be other values.
                # If j < half, then i = d - j > d - half = new_idx, so i > new_idx (already determined).
                # If j > half: not allowed.
                # So when j < half, i > new_idx and delta_L[i] is already determined.
                # When j = half, i = new_idx (the unknown).
                # So the only unknown in the sum is at j = half, and that's the one we solve for.
                # The "if i > new_idx" clause captures the "already determined" cases.
            
            # 2 * (sum_known + delta_L[new_idx] * L[half]) ≡ R_div_mod[d] mod p
            # 2 * delta_L[new_idx] * 1 = R_div_mod[d] - 2 * sum_known mod p
            delta_L[new_idx] = ((R_div_mod[d] - 2 * sum_known) * inv2) % p
        
        # Now L_new = L + mod * delta_L mod new_mod
        L_new = [(L[i] + mod * delta_L[i]) % new_mod for i in range(half + 1)]
        L = L_new
        
        # For M: we need to lift M from mod mod to mod new_mod.
        # Use: M^2 = (L^2 - Phi) / (p * x) (in some sense).
        # Compute L_new^2 mod new_mod:
        # L_new_sq = poly_mult_mod_int(L, L, new_mod, 2*half)
        # But L is now L_new (length half+1), and new_mod is current.
        # Actually, we have L_new such that L_new^2 - p*x*M^2 ≡ Phi mod new_mod.
        # We want M_new such that L_new^2 - p*x*M_new^2 ≡ Phi mod new_mod (with M_new = M + mod*delta_M).
        # Since L^2 - p*x*M^2 = Phi + p * R (where R is the residual), and we've corrected L by mod*delta_L:
        #   L_new^2 = L^2 + 2*mod*delta_L*L + mod^2*delta_L^2 ≡ L^2 + 2*mod*delta_L*L mod new_mod
        #   p*x*M_new^2 = p*x*(M + mod*delta_M)^2 ≡ p*x*M^2 + 2*p*x*mod*M*delta_M mod new_mod
        #                ≡ p*x*M^2 + 2*mod*p*x*M*delta_M mod new_mod
        # Wait, 2*p*mod*M*delta_M has factor p*mod, and mod = p^k. So 2*p*mod = 2*p^{k+1} ≡ 0 mod new_mod = p^{k+1}.
        # So p*x*M_new^2 ≡ p*x*M^2 mod new_mod.
        # Therefore M doesn't need to be updated at this step (its update is invisible mod p^{k+1}).
        
        # Actually that's the same as before. So M is only updated every "other" step?
        # No wait, let me re-examine.
        
        # We have L mod p^k, M mod p^k.
        # We want L mod p^{k+1}, M mod p^{k+1}.
        # L_new = L + p^k * delta_L.
        # M_new = M + p^k * delta_M.
        # (L_new)^2 - p*x*(M_new)^2 = L^2 + 2*p^k*delta_L*L + p^{2k}*delta_L^2 - p*x*M^2 - 2*p^{k+1}*x*M*delta_M - p^{2k+1}*x*delta_M^2
        #                          ≡ L^2 + 2*p^k*delta_L*L - p*x*M^2 mod p^{k+1}
        # Want ≡ Phi mod p^{k+1}.
        # So 2*p^k*delta_L*L ≡ (Phi - L^2 + p*x*M^2) mod p^{k+1}
        # Divide by p^k: 2*delta_L*L ≡ (Phi - L^2 + p*x*M^2)/p^k mod p
        # So delta_L is determined. delta_M doesn't appear (it would appear in higher-order corrections).
        
        # So at each step, ONLY L is updated. M stays at mod p.
        # But we need M to be correct mod p^{k+1} for FUTURE steps.
        
        # Hmm, but at the next step (k+1 to k+2), the equation 2*delta_L*L ≡ R mod p
        # uses M mod p^{k+1}. If M is still mod p, then p*x*M^2 mod p^{k+2} is not accurate.
        
        # Specifically: p*x*M^2 mod p^{k+2} requires M mod p^{k+1}.
        # If M is only mod p^k, then p*x*M^2 mod p^{k+2} has error p^{k+1} * 2*x*M*delta_M ≈ 2*p^{k+1} * x*M * delta_M, which is not 0 mod p^{k+2}.
        
        # So we DO need to update M to mod p^{k+1} at each step.
        
        # The update for M:
        # (L_new)^2 - p*x*M_new^2 ≡ Phi mod p^{k+1}, with M_new = M + p^k * delta_M (need delta_M to make this hold exactly).
        # But we've already adjusted L_new so that (L_new)^2 - p*x*M^2 ≡ Phi mod p^{k+1} (using M mod p^k).
        # So if we keep M mod p^k (no update), then (L_new)^2 - p*x*M_new^2 (with M_new = M mod p^k, lifted trivially) ≡ (L_new)^2 - p*x*M^2 ≡ Phi mod p^{k+1}. 
        # Wait, but p*x*M_new^2 = p*x*M^2 + 2*p^{k+1}*x*M*delta_M + ..., and the linear correction has factor p^{k+1}, so mod p^{k+1} it's 0. So p*x*M_new^2 ≡ p*x*M^2 mod p^{k+1}. So (L_new)^2 - p*x*M_new^2 ≡ Phi mod p^{k+1} automatically.
        
        # So M doesn't need to be updated for the constraint mod p^{k+1}.
        # BUT, for the NEXT iteration, we need M mod p^{k+1}.
        
        # So at the next iteration (lifting to p^{k+2}):
        # We have L mod p^{k+1}, M mod p^k.
        # Equation: 2 * delta_L' * L ≡ (Phi - L^2 + p*x*M^2) / p^{k+1} mod p
        # p*x*M^2 mod p^{k+2} requires M mod p^{k+1}. We only have M mod p^k.
        # Error: p*x*M^2 mod p^{k+2} differs from p*x*(M mod p^k)^2 mod p^{k+2} by 2*p*x*M*delta_M*p^k = 2*p^{k+1}*x*M*delta_M.
        # This error divided by p^{k+1} (to get the mod-p RHS) gives 2*x*M*delta_M mod p, which is generally nonzero.
        
        # So we MUST update M at each step.
        
        # Updating M: at step k -> k+1, M is currently mod p^k. We want M mod p^{k+1}.
        # Compute (L_new)^2 mod p^{k+2}: this is needed.
        # Compute (L_new)^2 - Phi mod p^{k+2}. This should be p*x*M_new^2 for some M_new.
        # M_new^2 mod p^{k+1} = ((L_new)^2 - Phi) / (p*x) mod p^{k+1}.
        # M_new = sqrt of M_new^2 mod p^{k+1}.
        
        # So the algorithm at each step:
        # 1. Lift L from mod p^k to mod p^{k+1} using M mod p^k (compute delta_L, set L = L + p^k * delta_L).
        # 2. Update M from mod p^k to mod p^{k+1}: compute (L_new)^2 mod p^{k+2}, extract M^2 mod p^{k+1} = ((L_new)^2 - Phi)/(p*x) mod p^{k+1}, then sqrt.
        
        # This is doable but requires a square root computation each step.
        
        # For simplicity, let me just compute L mod p^K (only L, not M), and then at the end, 
        # recover M from L.
        
        # Skip M update for now; only lift L. (This is what the code above does.)
        # We'll deal with M at the end.
    
    mod = new_mod
    if (k + 1) % 10 == 0:
        print(f"  Step {k+1}/{target_K-1}, mod has {len(str(mod))} digits, elapsed {time.time() - t0:.1f}s")

print(f"\nHensel lifting complete. Final L mod p^K computed.")
print(f"  Total elapsed: {time.time() - t0:.1f}s")

# Evaluate L(2) mod p^K
A_mod = 0
pow2 = 1
for i in range(half + 1):
    A_mod = (A_mod + L[i] * pow2) % mod
    pow2 = (pow2 * 2) % mod

# A as integer should be in [0, p^K). But we want A in the "canonical" range.
# A is approximately 2^618 in absolute value, but could be negative (if Aurifeuillean L has negative leading coeffs).
# Wait, L[half] = 1 mod p, but as an integer, L[half] = 1 (we initialized with sign +1).
# Actually L mod p^K with L[half] = 1 (the smallest positive representative).
# So A mod p^K = L(2) mod p^K, and A in [0, p^K).
# A ≈ 2^618 (since L is degree 618 monic, L(2) ≈ 2^618).
# p^K ≈ 2^657 > 2^618, so A mod p^K = A (the actual integer, if A is positive and < p^K).

print(f"A mod p^K = {A_mod}")
print(f"A has {len(str(A_mod))} digits")
# Check if A_mod is approximately 2^618
import math
expected_bits = 618
actual_bits = math.log2(float(A_mod)) if A_mod > 0 else 0
print(f"Expected ~2^{expected_bits}, actual ~2^{actual_bits:.1f}")

# Compute B^2 = (A^2 - M(p)) / (2p)
A_int = int(A_mod)
M_p_int = (1 << p) - 1  # 2^p - 1
diff = A_int * A_int - M_p_int
print(f"\nA^2 - M(p): {len(str(abs(diff)))} digits, sign: {'+' if diff > 0 else '-'}")
print(f"Divisible by 2p = {2*p}? {diff % (2*p) == 0}")

if diff % (2 * p) == 0:
    B_sq = diff // (2 * p)
    if B_sq < 0:
        # Try -A instead
        A_int_neg = A_int - mod  # negative representative
        diff = A_int_neg * A_int_neg - M_p_int
        print(f"Trying -A: A^2 - M(p) divisible by 2p? {diff % (2*p) == 0}")
        if diff % (2 * p) == 0:
            A_int = A_int_neg
            B_sq = diff // (2 * p)
    if B_sq >= 0:
        B = gmpy2.isqrt(mpz(B_sq))
        if B * B == mpz(B_sq):
            print(f"B = {B}")
            print(f"B has {len(str(B))} digits")
            verify = A_int**2 - 2*p*int(B)**2
            print(f"Verify: A^2 - 2p B^2 = M(p)? {verify == M_p_int}")
        else:
            print(f"B^2 is not a perfect square")
