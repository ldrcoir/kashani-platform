#!/usr/bin/env python3
"""
Direct computation of M(1237) = A^2 - 2p*B^2 using Brent's algorithm.

For p ≡ 1 mod 4 with p = a^2 + b^2 (Brent's decomposition):
  Define L_p(x), M_p(x) such that Phi_p(x) = L_p(x)^2 - p*x*M_p(x)^2.
  Then M(p) = L_p(2)^2 - 2p*M_p(2)^2 = A^2 - 2p*B^2 with A = L_p(2), B = M_p(2).

Algorithm (Brent 1993, "On Aurifeuillian Factorizations", or Granville-Pleasants):
  Compute L_p(x) using a SPECIFIC formula involving p = a^2 + b^2.
  For p ≡ 1 mod 4, p = a^2 + b^2 with a odd, b even:
    L_p(x) and M_p(x) are computed via a recurrence involving binomial coefficients
    and the choice of (a, b).

For p = 5: a = 1, b = 2 (1 odd, 2 even). L_5 = x^2 + 3x + 1, M_5 = x + 1.
For p = 13: a = 3, b = 2 (3 odd, 2 even). L_13 = ?
For p = 1237: 1237 = 34^2 + 9^2. 34 even, 9 odd. So a = 9, b = 34.

Direct computation via Newton's iteration in Z[x] using p-adic lifting:
  Initialize L mod p, M mod p (computed from (x-1)^{half} mod p and sqrt).
  Lift to mod p^K for sufficient K via Hensel lifting, updating BOTH L and M.

For p = 13 (test):
  L mod 13 = (x - 1)^6 mod 13 = (computed via binomial):
    binom(6,0) = 1, binom(6,1) = 6, binom(6,2) = 15, binom(6,3) = 20, binom(6,4) = 15, binom(6,5) = 6, binom(6,6) = 1.
    With signs (-1)^(6-j): 1, -6, 15, -20, 15, -6, 1.
    Mod 13: 1, 7, 2, 6, 2, 7, 1.
    So L mod 13 = x^6 + 7x^5 + 2x^4 + 6x^3 + 2x^2 + 7x + 1.
  L(2) mod 13 = 64 + 7*32 + 2*16 + 6*8 + 2*4 + 7*2 + 1 = 64 + 224 + 32 + 48 + 8 + 14 + 1 = 391.
  391 mod 13 = 391 - 30*13 = 391 - 390 = 1. ✓ (expected: A mod p = 1)
  
  A = 285 (computed earlier). 285 mod 13 = 285 - 21*13 = 285 - 273 = 12 = -1 mod 13. Hmm.
  Wait, A mod p should be 1 according to my computation, but A = 285 gives 12 mod 13.
  Maybe A = -285? Then A mod 13 = -12 = 1 mod 13. ✓
  Or maybe my formula gives L mod p = -(x-1)^{half}, not +(x-1)^{half}.

Let me check the sign. The Aurifeuillean decomposition has L_p^2 = Phi_p + p*x*M_p^2.
Modulo p: L_p^2 ≡ Phi_p. The two square roots of Phi_p mod p are ±(x-1)^{half}.
So both signs work for the mod-p reduction. We need to choose the right sign to get
the correct integer L.

For p = 5: A = 11. 11 mod 5 = 1 = (x-1)^2 evaluated at x=2: (2-1)^2 = 1. ✓
For p = 13: A = 285, but 285 mod 13 = 12 = -1. So we need L mod 13 = -1 mod 13 = 12.
(x-1)^6 at x=2: (2-1)^6 = 1. So +1 not -1.
So the correct L mod 13 is -(x-1)^6 mod 13 = -1 mod 13 = 12. ✓

So the sign matters! For some p, L = +(x-1)^{half} mod p; for others, L = -(x-1)^{half} mod p.

For p = 5: L mod 5 = +(x-1)^2 = +1 mod 5. ✓ (matches A = 11 mod 5 = 1)
For p = 13: L mod 13 = -(x-1)^6 = -1 mod 13 = 12. ✓ (matches A = 285 mod 13 = 12, or A = -285)

The sign is determined by some quadratic residue / character condition related to (a, b) 
in p = a^2 + b^2.

For our case p = 1237 = 34^2 + 9^2 (a=9 odd, b=34 even), the sign is yet to be determined.
Let me try both signs and see which one gives an integer A, B.

Also, more importantly, let me try to use Newton's iteration more carefully,
correctly handling both L and M.
"""

import gmpy2
from gmpy2 import mpz
import time

# Let's first verify the Hensel approach for p = 5, then apply to p = 1237.
# I'll write a general function.

def compute_aurif_AB(p, target_K=None):
    """Compute A, B such that M(p) = A^2 - 2p*B^2 using Hensel lifting.
    
    Returns (A, B) as integers, or None if failed.
    """
    half = (p - 1) // 2
    
    if target_K is None:
        # Need p^K > 2 * |A|. A ≈ 2^half (since L is monic of degree half).
        # 2 * A ≈ 2^(half+1). So need p^K > 2^(half+1).
        # log2(p^K) = K * log2(p) > half + 1.
        target_K = (half + 100) // max(1, int(gmpy2.log2(p))) + 5
    
    # Initialize L mod p: try +(x-1)^half first.
    L_pos = [0] * (half + 1)
    binom = 1
    sign = (-1) ** half
    L_pos[0] = (sign * binom) % p
    for j in range(1, half + 1):
        binom = (binom * (half - j + 1) * pow(j, -1, p)) % p
        sign = -sign
        L_pos[j] = (sign * binom) % p
    
    # Negative version
    L_neg = [(-l) % p for l in L_pos]
    
    # Try both signs
    for L_sign_name, L_init in [('+', L_pos), ('-', L_neg)]:
        print(f"  Trying L mod p = {L_sign_name}(x-1)^half mod p")
        L = list(L_init)
        
        # Compute M mod p (independent of sign of L, since M^2 = (L^2 - Phi)/(p*x) = same for ±L)
        # Wait, M^2 mod p depends on L mod p^2, not L mod p. But L mod p^2 depends on the sign.
        # Let me compute M mod p for each sign separately.
        
        # Compute L^2 mod p^2 (using L mod p as integer)
        p2 = p * p
        L_sq_p2 = poly_mult_mod_int(L, L, p2, 2 * half)
        # R = (L^2 - Phi) mod p^2
        R_p2 = [(L_sq_p2[i] - 1) % p2 for i in range(2 * half + 1)]
        # Check R divisible by p
        if any(r % p != 0 for r in R_p2):
            print(f"    R not divisible by p for sign {L_sign_name}, skip")
            continue
        R_div_p = [r // p for r in R_p2]
        # M^2 mod p = R_div_p / x mod p (shift)
        # R_div_p[0] should be 0
        if R_div_p[0] != 0:
            print(f"    R_div_p[0] = {R_div_p[0]} (should be 0), skip")
            continue
        # M^2 mod p: degree half - 1, length half
        # Actually, M^2 has degree 2*(half-1) = 2*half - 2, length 2*half - 1.
        # R_div_p has length 2*half + 1. After shifting (dividing by x), we get 2*half entries.
        # M^2[i] = R_div_p[i+1] mod p for i in 0, ..., 2*half - 2 (length 2*half - 1).
        M_sq_p = [R_div_p[i+1] % p for i in range(2 * half - 1)]
        
        # Take polynomial sqrt of M_sq_p mod p, starting from high-degree-first.
        # M[half-1] = sqrt(M_sq_p[2*half - 2]) mod p.
        leading_M_sq = M_sq_p[2 * half - 2]
        sqrt_lead = None
        for s in range(p):
            if (s * s) % p == leading_M_sq:
                sqrt_lead = s
                break
        if sqrt_lead is None:
            print(f"    No sqrt of leading M^2 coeff mod p, skip")
            continue
        
        # Newton iteration for polynomial sqrt (high-degree-first via reverse)
        # Reverse M and M_sq
        M_rev = [0] * half
        M_rev[0] = sqrt_lead  # corresponds to highest degree
        M_sq_rev = M_sq_p[::-1]  # length 2*half - 1, M_sq_rev[0] = leading coeff
        
        inv2 = pow(2, -1, p)
        converged = False
        for iteration in range(30):
            # 1/M_rev mod (p, x^half)
            B = poly_inv_newton(M_rev, p, half - 1)
            # M_sq_rev / M_rev = M_sq_rev * B mod (p, x^half)
            P_over = poly_mult_mod_int(M_sq_rev, B, p, half - 1)
            # M_rev_new = (M_rev + P_over) / 2 mod (p, x^half)
            M_rev_new = [((M_rev[i] + (P_over[i] if i < len(P_over) else 0)) * inv2) % p for i in range(half)]
            if M_rev_new == M_rev:
                converged = True
                break
            M_rev = M_rev_new
        
        if not converged:
            print(f"    Newton for M sqrt didn't converge")
            continue
        
        M = M_rev[::-1]
        # Verify
        M_check = poly_mult_mod_int(M, M, p, 2 * (half - 1))
        if M_check != M_sq_p:
            print(f"    M mod p verification failed")
            continue
        print(f"    M mod p verified, leading = {M[half-1]}")
        
        # Hensel lifting (with both L and M updates)
        mod = p
        hensel_ok = True
        for k in range(target_K - 1):
            new_mod = mod * p
            
            # Lift L: L_new = L + mod * delta_L
            # Equation: 2 * delta_L * L ≡ (Phi - L^2 + p*x*M^2) / mod mod p
            
            # Compute L^2 mod new_mod (using current L mod mod)
            L_sq = poly_mult_mod_int(L, L, new_mod, 2 * half)
            # Compute p * x * M^2 mod new_mod (using current M mod mod)
            M_sq = poly_mult_mod_int(M, M, new_mod, 2 * half - 1)
            x_M_sq = [0] + M_sq
            p_x_M_sq = [(p * c) % new_mod for c in x_M_sq]
            while len(p_x_M_sq) < 2 * half + 1:
                p_x_M_sq.append(0)
            
            # R = (Phi - L^2 + p*x*M^2) mod new_mod
            R = [((1 - L_sq[i] + p_x_M_sq[i]) % new_mod) for i in range(2 * half + 1)]
            
            # Check R divisible by mod
            for i, r in enumerate(R):
                if r % mod != 0:
                    print(f"    Hensel fails at k={k}, i={i}: R not divisible by mod")
                    hensel_ok = False
                    break
            if not hensel_ok:
                break
            
            R_div_mod = [r // mod for r in R]
            
            # Solve 2 * delta_L * L ≡ R_div_mod mod (p, x^{2*half+1}) for delta_L of degree ≤ half.
            delta_L = [0] * (half + 1)
            for d in range(2 * half, -1, -1):
                new_idx = d - half
                if new_idx < 0 or new_idx > half:
                    continue
                sum_known = 0
                for j in range(0, half + 1):
                    i = d - j
                    if i < 0 or i > half or j > half:
                        continue
                    if i == new_idx and j == half:
                        continue
                    if i > new_idx:
                        sum_known = (sum_known + delta_L[i] * L[j]) % p
                delta_L[new_idx] = ((R_div_mod[d] - 2 * sum_known) * inv2) % p
            
            # Update L
            L = [(L[i] + mod * delta_L[i]) % new_mod for i in range(half + 1)]
            
            # Now update M: lift from mod to new_mod.
            # Compute L_new^2 mod new_mod^2 = (new_mod)^2 (or use new_mod for efficiency?)
            # Actually, we want M_new = M + mod * delta_M, and need:
            #   (L_new)^2 - p * x * (M_new)^2 ≡ Phi mod new_mod (already satisfied by L_new, since we set it so with M mod mod).
            # Wait, but we want M_new mod new_mod, not just M mod mod.
            # The equation (L_new)^2 - p*x*(M_new)^2 = Phi in Z[x] means M_new is uniquely determined.
            # (L_new)^2 - Phi = p*x*M_new^2 in Z[x], so M_new^2 = ((L_new)^2 - Phi) / (p*x).
            
            # Compute (L_new)^2 mod (new_mod * p) = mod * p^2 = p^{k+2}
            mod2 = new_mod * p  # for k = current step, this is p^{k+2}
            L_new_sq = poly_mult_mod_int(L, L, mod2, 2 * half)
            # Compute (L_new)^2 - Phi mod mod2
            diff_L2_Phi = [(L_new_sq[i] - 1) % mod2 for i in range(2 * half + 1)]
            # This should be p * x * M_new^2 in Z[x], so divisible by p*x.
            # diff / p mod (new_mod * p / p) = mod2 / p = new_mod. Hmm let me think.
            # Actually we want M_new^2 mod new_mod (not mod2).
            # M_new^2 = (L_new^2 - Phi) / (p * x).
            # M_new^2 mod new_mod = ((L_new^2 - Phi) / (p*x)) mod new_mod.
            # Compute (L_new^2 - Phi) mod (p * x * new_mod)? This is getting tangled.
            
            # Simpler: just use (L_new)^2 mod (new_mod * p) to extract M_new mod new_mod.
            # (L_new)^2 - Phi should be divisible by p (in integer coefficients), giving M_new^2 * p * x.
            # We want M_new^2 mod new_mod, so divide (L_new)^2 - Phi by p*x and take mod new_mod.
            
            # Check: is (L_new)^2 - Phi divisible by p?
            for i, val in enumerate(diff_L2_Phi):
                if val % p != 0:
                    print(f"    M update: (L^2 - Phi) not divisible by p at i={i}: {val}")
                    hensel_ok = False
                    break
            if not hensel_ok:
                break
            
            # Divide by p
            M_new_sq_over_p = [val // p for val in diff_L2_Phi]
            # This should be x * M_new^2 (i.e., constant term 0).
            # Hmm wait, in Z[x], (L_new)^2 - Phi = p*x*M_new^2 exactly.
            # So (L_new)^2 - Phi mod (p * x * new_mod) = p * x * (M_new mod new_mod)^2 (approximately).
            # Divide by p: x * M_new^2 in Z[x], mod (new_mod * x)? Not exactly.
            
            # Let me just compute M_new^2 mod new_mod by shifting and mod:
            # (L_new^2 - Phi) / p mod new_mod = x * M_new^2 mod new_mod.
            # So M_new^2[i] = (M_new_sq_over_p[i+1]) mod new_mod for i = 0, ..., 2*half - 2.
            
            # Check M_new_sq_over_p[0] = 0 (since constant term of x*M^2 is 0)
            if M_new_sq_over_p[0] != 0:
                # Might be nonzero mod new_mod if M_new is updated; check mod new_mod.
                if M_new_sq_over_p[0] % new_mod != 0:
                    print(f"    M update: M_new_sq_over_p[0] = {M_new_sq_over_p[0]} not 0 mod new_mod, skip")
                    # Actually maybe this means M_new^2 has a nonzero constant term mod new_mod, which shouldn't happen.
                    # Let me check if the constant term is 0 mod new_mod.
                    if M_new_sq_over_p[0] % new_mod != 0:
                        hensel_ok = False
                        break
            
            # M_new^2 mod new_mod (taking the shifted and mod)
            M_new_sq_mod = [M_new_sq_over_p[i+1] % new_mod for i in range(2 * half - 1)]
            
            # Take sqrt to get M_new mod new_mod
            # First, the leading coeff M_new[half-1] should match the existing M[half-1] lifted to mod new_mod
            # (since M = M_new + mod * delta_M, M[half-1] mod mod is known, but M_new[half-1] mod new_mod requires lifting).
            
            # Take sqrt mod new_mod (more complex than mod p, but follows similar approach)
            # For Hensel sqrt, we need the existing M mod mod as initial guess and lift.
            # M_new = M + mod * delta_M (for some delta_M).
            # M_new^2 = M^2 + 2*mod*M*delta_M + mod^2 * delta_M^2 ≡ M^2 + 2*mod*M*delta_M mod new_mod.
            # Want M_new^2 ≡ M_new_sq_mod mod new_mod.
            # So 2*mod*M*delta_M ≡ M_new_sq_mod - M^2 mod new_mod.
            # (M_new_sq_mod - M^2) / mod ≡ 2*M*delta_M mod p.
            
            M_sq_mod = poly_mult_mod_int(M, M, new_mod, 2 * half - 1)
            # Compute M_new_sq_mod - M_sq_mod (both mod new_mod)
            diff_M_sq = [((M_new_sq_mod[i] - (M_sq_mod[i] if i < len(M_sq_mod) else 0)) % new_mod) for i in range(2 * half - 1)]
            # This should be divisible by mod
            for i, val in enumerate(diff_M_sq):
                if val % mod != 0:
                    print(f"    M update: diff_M_sq not div by mod at i={i}: {val}")
                    hensel_ok = False
                    break
            if not hensel_ok:
                break
            
            diff_div = [val // mod for val in diff_M_sq]
            # Solve 2 * M * delta_M ≡ diff_div mod (p, x^{2*half-1}) for delta_M of degree ≤ half-1.
            # M has leading coeff M[half-1] (let's call it c). Coefficient at degree 2*half-2 of 2*M*delta_M is 2*c*delta_M[half-1].
            # So delta_M[half-1] = diff_div[2*half-2] / (2*c) mod p.
            
            c = M[half - 1] % p
            if c == 0:
                print(f"    Leading coeff M[half-1] mod p = 0, can't update M")
                hensel_ok = False
                break
            
            delta_M = [0] * half
            inv2c = pow(2 * c, -1, p)
            for d in range(2 * half - 2, -1, -1):
                new_idx = d - (half - 1)
                if new_idx < 0 or new_idx > half - 1:
                    continue
                # 2 * sum_{i+j=d, i in [0,half-1], j in [0,half-1]} M[j] * delta_M[i] = diff_div[d]
                # Solve for delta_M[new_idx] (= delta_M[d - (half-1)] = delta_M[i] where j = half-1, i = d - (half-1)).
                # The unknown delta_M[new_idx] is paired with M[half-1] = c.
                sum_known = 0
                for j in range(half):
                    i = d - j
                    if i < 0 or i > half - 1 or j > half - 1:
                        continue
                    if i == new_idx and j == half - 1:
                        continue
                    if i > new_idx:
                        sum_known = (sum_known + (M[j] * delta_M[i])) % p
                delta_M[new_idx] = ((diff_div[d] - 2 * sum_known) * inv2c) % p
            
            # Update M
            M = [(M[i] + mod * delta_M[i]) % new_mod for i in range(half)]
            
            mod = new_mod
            if (k + 1) % 5 == 0:
                print(f"    Step {k+1}/{target_K-1}, mod has {len(str(mod))} digits")
        
        if not hensel_ok:
            print(f"    Hensel lifting failed for sign {L_sign_name}")
            continue
        
        print(f"    Hensel complete for sign {L_sign_name}")
        
        # Evaluate L(2) mod p^K
        A_mod = 0
        pow2 = 1
        for i in range(half + 1):
            A_mod = (A_mod + L[i] * pow2) % mod
            pow2 = (pow2 * 2) % mod
        
        # A should be in [-p^K/2, p^K/2). Try A_mod and A_mod - mod.
        M_p_int = (1 << p) - 1
        for A_try in [A_mod, A_mod - mod]:
            diff = A_try * A_try - M_p_int
            if diff > 0 and diff % (2 * p) == 0:
                B_sq = diff // (2 * p)
                B = gmpy2.isqrt(mpz(B_sq))
                if B * B == mpz(B_sq):
                    print(f"    >>> A = {A_try}, B = {B}")
                    print(f"    Verify: A^2 - 2p B^2 = M(p)? {A_try**2 - 2*p*int(B)**2 == M_p_int}")
                    return A_try, int(B)
        
        print(f"    No integer A, B for sign {L_sign_name} (A_mod = {A_mod}, digits = {len(str(A_mod))})")
    
    return None, None


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


def poly_inv_newton(a, mod_int, max_deg):
    """Compute 1/a as power series mod mod_int, truncated to max_deg."""
    if max_deg < 0:
        return []
    inv_a0 = pow(a[0], -1, mod_int)
    B = [inv_a0] + [0] * max_deg
    for _ in range(max_deg + 5):
        aB = poly_mult_mod_int(a, B, mod_int, max_deg)
        two_minus = [(-x) % mod_int for x in aB]
        two_minus[0] = (2 - aB[0]) % mod_int
        B_new = poly_mult_mod_int(B, two_minus, mod_int, max_deg)
        if B_new == B:
            break
        B = B_new
    return B


# Test with p = 5 first
print("Test p = 5:")
A, B = compute_aurif_AB(5, target_K=10)
print(f"A = {A}, B = {B}")
if A is not None:
    print(f"Verify: {A}^2 - 10*{B}^2 = {A**2 - 10*B**2}, M(5) = {2**5 - 1}")
print()

print("Test p = 13:")
A, B = compute_aurif_AB(13, target_K=15)
print(f"A = {A}, B = {B}")
if A is not None:
    print(f"Verify: {A}^2 - 26*{B}^2 = {A**2 - 26*B**2}, M(13) = {2**13 - 1}")
