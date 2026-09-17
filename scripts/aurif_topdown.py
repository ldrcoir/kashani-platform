#!/usr/bin/env python3
"""
Compute M mod p directly (coefficient by coefficient, top-down).

For p = 13, M = poly of degree 5 (length 6), M^2 = poly of degree 10 (length 11).
M[5] = ±sqrt(M^2[10]) mod p.
M[4] = (M^2[9] - 2*M[5]*0) / (2*M[5])  [since M^2[9] = 2*M[5]*M[4] + lower-order terms, but lower order terms don't contribute at degree 9]
  Actually: M^2[9] = sum_{i+j=9} M[i]*M[j]. For M of degree 5, i+j=9 means (i,j) ∈ {(4,5),(5,4)}. So M^2[9] = 2*M[4]*M[5].
M[3] = (M^2[8] - M[4]^2) / (2*M[5])  [M^2[8] = 2*M[3]*M[5] + M[4]^2]
M[2] = (M^2[7] - 2*M[3]*M[4]) / (2*M[5])
M[1] = (M^2[6] - 2*M[2]*M[4] - M[3]^2) / (2*M[5])
M[0] = (M^2[5] - 2*M[1]*M[4] - 2*M[2]*M[3]) / (2*M[5])

Verify: M^2[4] should equal 2*M[0]*M[4] + 2*M[1]*M[3] + M[2]^2.
"""

import gmpy2
from gmpy2 import mpz
import time


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


def poly_sqrt_topdown(M_sq, mod_int, half):
    """Compute M = sqrt(M_sq) mod mod_int, where M has degree half-1, M_sq has degree 2*half-2.
    Tries both signs of leading coefficient.
    Returns list of M coefficients or None.
    """
    # M[half-1] = ±sqrt(M_sq[2*half-2]) mod mod_int
    leading_M_sq = M_sq[2 * half - 2]
    # Find sqrt
    sqrt_leads = []
    for s in range(mod_int):
        if (s * s) % mod_int == leading_M_sq:
            sqrt_leads.append(s)
            if len(sqrt_leads) >= 2:
                break
    
    for sqrt_lead in sqrt_leads:
        M = [0] * half
        M[half - 1] = sqrt_lead
        inv_2_lead = pow(2 * sqrt_lead, -1, mod_int)
        ok = True
        # Compute M[half-2] down to M[0]
        for d in range(2 * half - 3, -1, -1):  # d = degree of M_sq we're trying to match
            new_idx = d - (half - 1)  # M[new_idx] is the unknown
            if new_idx < 0 or new_idx > half - 1:
                continue
            # M^2[d] = sum_{i+j=d} M[i]*M[j]
            # The unknown is M[new_idx] paired with M[half-1] (the leading coeff).
            # Other terms: M[i]*M[j] where i+j=d, i,j ≤ half-1, and (i,j) ≠ (new_idx, half-1) and ≠ (half-1, new_idx).
            # If new_idx ≠ half-1: sum = 2*M[new_idx]*M[half-1] + (other terms with known M[i]).
            # If new_idx = half-1: d = 2*half-2, and sum = M[half-1]^2 = leading_M_sq (already known, no unknown).
            # So we only handle new_idx < half-1.
            
            if new_idx == half - 1:
                # Already determined
                continue
            
            sum_known = 0
            for i in range(half):
                j = d - i
                if j < 0 or j >= half:
                    continue
                if i == new_idx and j == half - 1:
                    continue
                if i == half - 1 and j == new_idx:
                    continue
                sum_known = (sum_known + M[i] * M[j]) % mod_int
            # 2 * M[new_idx] * M[half-1] + sum_known = M_sq[d]
            # M[new_idx] = (M_sq[d] - sum_known) * inv_2_lead mod mod_int
            M[new_idx] = ((M_sq[d] - sum_known) * inv_2_lead) % mod_int
        
        # Verify
        M_check = poly_mult_mod_int(M, M, mod_int, 2 * half - 2)
        if M_check == M_sq[:2 * half - 1]:
            return M
    return None


def compute_aurif_AB(p, target_K, log_func):
    """Compute A, B with M(p) = A^2 - 2p B^2 via Hensel lifting with proper M updates."""
    half = (p - 1) // 2
    
    # Initialize L mod p (try both signs)
    L_pos = [0] * (half + 1)
    binom = 1
    sign = (-1) ** half
    L_pos[0] = (sign * binom) % p
    for j in range(1, half + 1):
        binom = (binom * (half - j + 1) * pow(j, -1, p)) % p
        sign = -sign
        L_pos[j] = (sign * binom) % p
    
    for L_sign_name, L_init in [('+', L_pos), ('-', [(-l) % p for l in L_pos])]:
        log_func(f"  Trying L sign = {L_sign_name}")
        
        # Compute M mod p
        p2 = p * p
        L = list(L_init)
        L_sq_p2 = poly_mult_mod_int(L, L, p2, 2 * half)
        R_p2 = [(L_sq_p2[i] - 1) % p2 for i in range(2 * half + 1)]
        if any(r % p != 0 for r in R_p2):
            log_func(f"    R not div by p for sign {L_sign_name}")
            continue
        R_div_p = [r // p for r in R_p2]
        if R_div_p[0] % p != 0:
            log_func(f"    R/p[0] = {R_div_p[0]} not 0 mod p for sign {L_sign_name}")
            continue
        M_sq_p = [R_div_p[i+1] % p for i in range(2 * half - 1)]
        
        # Use top-down sqrt
        M = poly_sqrt_topdown(M_sq_p, p, half)
        if M is None:
            log_func(f"    Top-down sqrt of M^2 mod p failed")
            continue
        log_func(f"    M mod p computed, leading = {M[half-1]}, constant = {M[0]}")
        
        # Verify M^2 mod p
        M_check = poly_mult_mod_int(M, M, p, 2 * (half - 1))
        if M_check != M_sq_p:
            log_func(f"    M mod p verification failed (top-down)")
            continue
        log_func(f"    M mod p verified!")
        
        # Hensel lifting
        mod = p
        L_cur = list(L)
        M_cur = list(M)
        hensel_ok = True
        inv2 = pow(2, -1, p)
        
        for k in range(target_K - 1):
            new_mod = mod * p
            
            # Lift L
            L_sq = poly_mult_mod_int(L_cur, L_cur, new_mod, 2 * half)
            M_sq = poly_mult_mod_int(M_cur, M_cur, new_mod, 2 * half - 1)
            x_M_sq = [0] + M_sq
            p_x_M_sq = [(p * c) % new_mod for c in x_M_sq]
            while len(p_x_M_sq) < 2 * half + 1:
                p_x_M_sq.append(0)
            
            R = [((1 - L_sq[i] + p_x_M_sq[i]) % new_mod) for i in range(2 * half + 1)]
            for i, r in enumerate(R):
                if r % mod != 0:
                    log_func(f"    Hensel L fails at k={k}, i={i}")
                    hensel_ok = False
                    break
            if not hensel_ok:
                break
            
            R_div = [r // mod for r in R]
            # Top-down solve for delta_L (degree ≤ half)
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
                        sum_known = (sum_known + delta_L[i] * L_cur[j]) % p
                delta_L[new_idx] = ((R_div[d] - 2 * sum_known) * inv2) % p
            
            L_cur = [(L_cur[i] + mod * delta_L[i]) % new_mod for i in range(half + 1)]
            
            # Lift M
            mod2 = new_mod * p
            L_new_sq = poly_mult_mod_int(L_cur, L_cur, mod2, 2 * half)
            diff = [(L_new_sq[i] - 1) % mod2 for i in range(2 * half + 1)]
            for i, val in enumerate(diff):
                if val % p != 0:
                    log_func(f"    M update fails at i={i}: diff={val}")
                    hensel_ok = False
                    break
            if not hensel_ok:
                break
            diff_div_p = [val // p for val in diff]
            if diff_div_p[0] % new_mod != 0:
                log_func(f"    M update: diff_div_p[0] = {diff_div_p[0]} not 0 mod new_mod")
                hensel_ok = False
                break
            M_new_sq = [diff_div_p[i+1] % new_mod for i in range(2 * half - 1)]
            
            # Lift M: M_new = M_cur + mod * delta_M, where 2 * M_cur * delta_M ≡ (M_new_sq - M_cur^2) / mod mod p
            M_sq_cur_mod_new = poly_mult_mod_int(M_cur, M_cur, new_mod, 2 * half - 1)
            diff_M_sq = [((M_new_sq[i] - (M_sq_cur_mod_new[i] if i < len(M_sq_cur_mod_new) else 0)) % new_mod) for i in range(2 * half - 1)]
            for i, val in enumerate(diff_M_sq):
                if val % mod != 0:
                    log_func(f"    M delta fails at i={i}: val={val}")
                    hensel_ok = False
                    break
            if not hensel_ok:
                break
            diff_M_div = [val // mod for val in diff_M_sq]
            
            c = M_cur[half - 1] % p
            if c == 0:
                log_func(f"    M_cur leading coeff 0 mod p")
                hensel_ok = False
                break
            inv2c = pow(2 * c, -1, p)
            # Top-down solve for delta_M (degree ≤ half-1)
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
                delta_M[new_idx] = ((diff_M_div[d] - 2 * sum_known) * inv2c) % p
            
            M_cur = [(M_cur[i] + mod * delta_M[i]) % new_mod for i in range(half)]
            
            mod = new_mod
            if (k + 1) % 10 == 0:
                log_func(f"    Step {k+1}/{target_K-1}, mod has {len(str(mod))} digits")
        
        if not hensel_ok:
            log_func(f"    Hensel failed for sign {L_sign_name}")
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
A, B = compute_aurif_AB(13, target_K=15, log_func=log_test)
print(f"A = {A}, B = {B}")
if A is not None:
    print(f"Verify: {A}^2 - 26*{B}^2 = {A**2 - 26*B**2}, M(13) = {2**13 - 1}")
