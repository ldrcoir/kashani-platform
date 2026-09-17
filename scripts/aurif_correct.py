#!/usr/bin/env python3
"""
CORRECTED Aurifeuillean A, B computation for M(1237).

Algorithm (Brent 1993, correct version):
  For p ≡ 1 mod 4, write p = a^2 + b^2 with a odd, b even.
  M(p) = A^2 - 2p*B^2 where:
    A = L_p(2), B = M_p(2)
    L_p(x), M_p(x) are polynomials with integer coefficients,
    Phi_p(x) = L_p(x)^2 - p*x*M_p(x)^2
  
  Compute (A, B) via direct construction.
  
ALGORITHM (correct Hensel lifting):
  Init: L = (x-1)^((p-1)/2) mod p, M = sqrt((L^2 - Phi)/p*x) mod p
  Iterate: Lift L from mod p^k to mod p^(k+1), then update M.
  
The key fix from previous attempt: M update needs proper handling.
Specifically: We compute (L^2 - Phi) mod p^(k+2) to get M^2 mod p^(k+1), 
then sqrt to get M mod p^(k+1).
"""

import sys
import time
from pathlib import Path
from math import isqrt
import gmpy2
from gmpy2 import mpz, is_prime, gcd as gmpy_gcd, powmod, invert, jacobi

sys.set_int_max_str_digits(1000000)

BASE = Path('/home/z/my-project')
LOG = BASE / 'logs/aurif_correct.log'
LOG.parent.mkdir(exist_ok=True)


def log(msg):
    print(msg, flush=True)
    with open(LOG, 'a') as f:
        f.write(msg + '\n')


def poly_mult_mod_int(a, b, mod_int, max_deg):
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


def poly_sqrt_high_first(P, mod_int, max_deg, sqrt_lead):
    """Compute sqrt(P) mod (mod_int, x^{max_deg+1}), high-degree-first.
    P has degree 2*max_deg. sqrt has degree max_deg. sqrt[max_deg] = sqrt_lead.
    """
    if max_deg < 0:
        return []
    
    sqrt_poly = [0] * (max_deg + 1)
    sqrt_poly[max_deg] = sqrt_lead
    
    # Use top-down approach:
    # For d from 2*max_deg down to 0:
    #   Let new_idx = d - max_deg (the new coefficient to determine, in [0, max_deg])
    #   The equation: sum_{i+j=d, i,j in [0, max_deg]} sqrt[i]*sqrt[j] = P[d] mod mod_int
    #   For (i, j) = (new_idx, max_deg): contributes 2*sqrt[new_idx]*sqrt[max_deg] if i != j, else sqrt[new_idx]^2 (only when new_idx == max_deg).
    #   Solve for sqrt[new_idx].
    
    inv_2_lead = pow(2 * sqrt_lead, -1, mod_int) if sqrt_lead != 0 else None
    
    for d in range(2 * max_deg, -1, -1):
        new_idx = d - max_deg
        if new_idx < 0 or new_idx > max_deg:
            continue
        if new_idx == max_deg:
            # Already determined: sqrt[max_deg]^2 = P[2*max_deg] (already verified)
            continue
        
        # Compute sum_known (excluding the term with new_idx)
        sum_known = 0
        for j in range(max_deg + 1):
            i = d - j
            if i < 0 or i > max_deg or j > max_deg:
                continue
            if i == new_idx and j == max_deg:
                continue
            if i == max_deg and j == new_idx:
                continue  # same term, double-counted in the (i==new_idx, j==max_deg) skip
            sum_known = (sum_known + sqrt_poly[i] * sqrt_poly[j]) % mod_int
        
        # Equation: 2 * sqrt[new_idx] * sqrt[max_deg] + sum_known = P[d] mod mod_int
        sqrt_poly[new_idx] = ((P[d] - sum_known) * inv_2_lead) % mod_int
    
    return sqrt_poly


def compute_aurif_AB(p, target_K, log_func):
    """Compute A, B with M(p) = A^2 - 2p*B^2 via Hensel lifting.
    Returns (A, B) as integers or (None, None) on failure.
    """
    half = (p - 1) // 2
    
    # Initialize L mod p: L = (x-1)^half mod p (polynomial of degree half)
    L = [0] * (half + 1)
    binom = 1
    sign = (-1) ** half
    L[0] = (sign * binom) % p
    for j in range(1, half + 1):
        binom = (binom * (half - j + 1) * pow(j, -1, p)) % p
        sign = -sign
        L[j] = (sign * binom) % p
    
    # Try both signs of L
    for L_sign_name, L_init in [('+', L), ('-', [(-l) % p for l in L])]:
        log_func(f"  Trying L sign = {L_sign_name}")
        
        # Compute initial M mod p from L mod p:
        # L^2 - Phi = p*x*M^2 mod p^2, so M^2 mod p = ((L^2 - Phi)/p)/x mod p
        p2 = p * p
        L_curr = list(L_init)
        L_sq_p2 = poly_mult_mod_int(L_curr, L_curr, p2, 2 * half)
        R_p2 = [(L_sq_p2[i] - 1) % p2 for i in range(2 * half + 1)]
        if any(r % p != 0 for r in R_p2):
            log_func(f"    R not div by p")
            continue
        R_div_p = [r // p for r in R_p2]
        if R_div_p[0] % p != 0:
            log_func(f"    R/p[0] not 0 mod p")
            continue
        M_sq_p = [R_div_p[i+1] % p for i in range(2 * half - 1)]  # length 2*half - 1
        
        # Take polynomial sqrt of M_sq_p mod p
        leading_M_sq = M_sq_p[2 * half - 2]
        sqrt_leads = []
        for s in range(p):
            if (s * s) % p == leading_M_sq:
                sqrt_leads.append(s)
                if len(sqrt_leads) >= 2:
                    break
        
        if not sqrt_leads:
            log_func(f"    No sqrt of leading M^2 coeff mod p")
            continue
        
        for sqrt_lead in sqrt_leads:
            M = poly_sqrt_high_first(M_sq_p, p, half - 1, sqrt_lead)
            # Verify
            M_check = poly_mult_mod_int(M, M, p, 2 * (half - 1))
            if M_check != M_sq_p:
                continue
            log_func(f"    M mod p verified, leading = {M[half-1]}, constant = {M[0]}")
            
            # Hensel lifting
            mod = p
            L_cur = list(L_curr)
            M_cur = list(M)
            hensel_ok = True
            inv2 = pow(2, -1, p)
            
            t_hensel_start = time.time()
            
            for k in range(target_K - 1):
                new_mod = mod * p
                
                # Lift L: L_new = L + mod * delta_L
                # Equation: 2 * delta_L * L ≡ (Phi - L^2 + p*x*M^2) / mod mod p
                L_sq = poly_mult_mod_int(L_cur, L_cur, new_mod, 2 * half)
                M_sq = poly_mult_mod_int(M_cur, M_cur, new_mod, 2 * half - 1)
                x_M_sq = [0] + M_sq
                p_x_M_sq = [(p * c) % new_mod for c in x_M_sq]
                while len(p_x_M_sq) < 2 * half + 1:
                    p_x_M_sq.append(0)
                
                R = [((1 - L_sq[i] + p_x_M_sq[i]) % new_mod) for i in range(2 * half + 1)]
                
                # Check R divisible by mod
                for i, r in enumerate(R):
                    if r % mod != 0:
                        log_func(f"    Hensel L fails at k={k}, i={i}: r={r}, mod={mod}")
                        hensel_ok = False
                        break
                if not hensel_ok:
                    break
                
                R_div = [r // mod for r in R]
                # Top-down solve for delta_L (degree ≤ half)
                delta_L = [0] * (half + 1)
                # Use formula: 2 * delta_L * L = R_div mod (p, x^{2*half+1})
                # delta_L has degree ≤ half, so we need delta_L[half], delta_L[half-1], ..., delta_L[0]
                # Coefficient at degree d of 2*delta_L*L: 2 * sum_{i+j=d} delta_L[i] * L[j]
                # Solve top-down: for d from 2*half down to 0:
                #   new_idx = d - half (in [0, half])
                #   The unknown term is delta_L[new_idx] paired with L[half].
                #   Equation: 2 * delta_L[new_idx] * L[half] + sum_of_known = R_div[d] mod p
                #   (when new_idx != half, i.e., d != 2*half)
                #   When d == 2*half (new_idx == half): delta_L[half] is unknown, paired with L[half]
                #     2 * delta_L[half] * L[half] = R_div[2*half] mod p
                #     delta_L[half] = R_div[2*half] / (2 * L[half]) mod p
                
                # L[half] should be 1 (since L = (x-1)^half is monic, leading coeff 1)
                # But for sign "-", L[half] = -1 mod p. Let's verify.
                # Actually we already set L = list(L_init), and L_init for "+" has L[half] = 1,
                # and for "-" has L[half] = -1 mod p = p - 1.
                L_lead = L_cur[half] % p
                inv_2_L_lead = pow(2 * L_lead, -1, p)
                
                for d in range(2 * half, -1, -1):
                    new_idx = d - half
                    if new_idx < 0 or new_idx > half:
                        continue
                    # Compute sum_known (terms not involving delta_L[new_idx])
                    sum_known = 0
                    for j in range(0, half + 1):
                        i = d - j
                        if i < 0 or i > half or j > half:
                            continue
                        if i == new_idx and j == half:
                            continue
                        if i > new_idx:
                            sum_known = (sum_known + delta_L[i] * L_cur[j]) % p
                    delta_L[new_idx] = ((R_div[d] - 2 * sum_known) * inv_2_L_lead) % p
                
                # Update L
                L_cur = [(L_cur[i] + mod * delta_L[i]) % new_mod for i in range(half + 1)]
                
                # Lift M: M_new = M + mod * delta_M
                # Compute (L_new)^2 mod (new_mod * p) = p^(k+2)
                mod2 = new_mod * p
                L_new_sq = poly_mult_mod_int(L_cur, L_cur, mod2, 2 * half)
                diff = [(L_new_sq[i] - 1) % mod2 for i in range(2 * half + 1)]
                # Should be divisible by p
                for i, val in enumerate(diff):
                    if val % p != 0:
                        log_func(f"    M update: diff not div by p at i={i}")
                        hensel_ok = False
                        break
                if not hensel_ok:
                    break
                
                diff_div_p = [val // p for val in diff]
                if diff_div_p[0] % new_mod != 0:
                    log_func(f"    M update: diff_div_p[0] not 0 mod new_mod")
                    hensel_ok = False
                    break
                M_new_sq = [diff_div_p[i+1] % new_mod for i in range(2 * half - 1)]
                
                # Lift M: M_new = M_cur + mod * delta_M, with 2*M_cur*delta_M = (M_new_sq - M_cur^2)/mod mod p
                M_sq_cur_mod_new = poly_mult_mod_int(M_cur, M_cur, new_mod, 2 * half - 1)
                diff_M_sq = [((M_new_sq[i] - (M_sq_cur_mod_new[i] if i < len(M_sq_cur_mod_new) else 0)) % new_mod) for i in range(2 * half - 1)]
                for i, val in enumerate(diff_M_sq):
                    if val % mod != 0:
                        log_func(f"    M delta fails at i={i}")
                        hensel_ok = False
                        break
                if not hensel_ok:
                    break
                diff_M_div = [val // mod for val in diff_M_sq]
                
                c = M_cur[half - 1] % p
                if c == 0:
                    log_func(f"    M_cur leading 0")
                    hensel_ok = False
                    break
                inv_2c = pow(2 * c, -1, p)
                delta_M = [0] * half
                for d in range(2 * half - 2, -1, -1):
                    new_idx = d - (half - 1)
                    if new_idx < 0 or new_idx > half - 1:
                        continue
                    sum_known = 0
                    for j in range(half):
                        i = d - j
                        if i < 0 or i > half - 1 or j > half - 1:
                            continue
                        if i == new_idx and j == half - 1:
                            continue
                        if i > new_idx:
                            sum_known = (sum_known + (M_cur[j] * delta_M[i])) % p
                    delta_M[new_idx] = ((diff_M_div[d] - 2 * sum_known) * inv_2c) % p
                
                M_cur = [(M_cur[i] + mod * delta_M[i]) % new_mod for i in range(half)]
                
                mod = new_mod
                if (k + 1) % 10 == 0:
                    elapsed_h = time.time() - t_hensel_start
                    log_func(f"    Step {k+1}/{target_K-1}, mod has {len(str(mod))} digits, time {elapsed_h:.1f}s")
            
            if not hensel_ok:
                log_func(f"    Hensel failed for sign {L_sign_name}, sqrt_lead {sqrt_lead}")
                continue
            
            log_func(f"    Hensel complete!")
            
            # Evaluate L(2) mod p^K
            A_mod = 0
            pow2 = 1
            for i in range(half + 1):
                A_mod = (A_mod + L_cur[i] * pow2) % mod
                pow2 = (pow2 * 2) % mod
            
            M_p_int = (1 << p) - 1
            for A_try in [A_mod, A_mod - mod]:
                diff = A_try * A_try - M_p_int
                if diff > 0 and diff % (2 * p) == 0:
                    B_sq = diff // (2 * p)
                    B = gmpy2.isqrt(mpz(B_sq))
                    if B * B == mpz(B_sq):
                        log_func(f"    >>> A = {A_try}")
                        log_func(f"    >>> B = {B}")
                        log_func(f"    Verify: A^2 - 2p B^2 = M(p)? {A_try**2 - 2*p*int(B)**2 == M_p_int}")
                        return A_try, int(B)
            
            log_func(f"    No integer A, B for this combination")
    
    return None, None


# Test with p=13 first
print("Test p = 13:")
def log_test(msg):
    print(msg)
A, B = compute_aurif_AB(13, target_K=20, log_func=log_test)
print(f"A = {A}, B = {B}")
if A is not None:
    print(f"Verify: {A}^2 - 26*{B}^2 = {A**2 - 26*B**2}, M(13) = {2**13 - 1}")
