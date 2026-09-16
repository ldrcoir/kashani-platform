#!/usr/bin/env python3
"""
Aurifeuillean A, B computation via Hensel lifting (corrected version).
Then use for Rabin-style factorization of M(1237)/F1.

Algorithm:
1. Compute (A, B) with M(p) = A^2 - 2p B^2 (Aurifeuillean).
2. Compute (a_1, b_1) with F1 = a_1^2 - 2p b_1^2 (Cornacchia).
3. Compute (A', B') with N = A'^2 - 2p B'^2 via (A + B sqrt(2p))/(a_1 + b_1 sqrt(2p)).
4. Compute R = A' * B'^{-1} mod N (sqrt of 2p mod N).
5. Find another sqrt of 2p mod N via Cipolla/Tonelli-Shanks.
6. gcd(R_1 - R_2, N) and gcd(R_1 + R_2, N) for factor.
"""

import sys
import time
import random
from pathlib import Path

import gmpy2
from gmpy2 import mpz, gcd, is_prime, powmod, invert, jacobi, isqrt

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
LOG_FILE = BASE / 'logs/aurif_full.log'
LOG_FILE.parent.mkdir(exist_ok=True)


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    with open(LOG_FILE, 'a') as f:
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


def poly_sqrt_high_first(P, mod_int, max_deg, sqrt_lead):
    """Compute sqrt(P) as polynomial mod (mod_int, x^{max_deg+1}),
    using high-degree-first approach. P has degree 2*max_deg, sqrt has degree max_deg.
    sqrt_lead is the leading coefficient of the sqrt.
    """
    if max_deg < 0:
        return []
    sqrt_poly = [0] * (max_deg + 1)
    sqrt_poly[max_deg] = sqrt_lead
    # Newton's iteration in 1/x variable (high-degree-first)
    # Reverse P and sqrt_poly: P_rev[i] = P[2*max_deg - i], sqrt_rev[i] = sqrt[max_deg - i].
    # sqrt_rev has constant = sqrt_lead, P_rev has constant = P[2*max_deg].
    # Compute sqrt_rev via Newton: y_{n+1} = (y_n + P_rev / y_n) / 2.
    # 1/y_n via Newton: B_{n+1} = B_n * (2 - y_n * B_n).
    sqrt_rev = [sqrt_lead] + [0] * max_deg
    P_rev = [P[2 * max_deg - i] if (2 * max_deg - i) < len(P) else 0 for i in range(2 * max_deg + 1)]
    
    inv2 = pow(2, -1, mod_int)
    for iteration in range(2 * max_deg + 5):
        # Compute 1/sqrt_rev mod (mod_int, x^{max_deg+1})
        B = poly_inv_newton(sqrt_rev, mod_int, max_deg)
        # Compute P_rev / sqrt_rev = P_rev * B mod (mod_int, x^{max_deg+1})
        P_over = poly_mult_mod_int(P_rev, B, mod_int, max_deg)
        # sqrt_rev_new = (sqrt_rev + P_over) / 2
        sqrt_rev_new = [((sqrt_rev[i] + (P_over[i] if i < len(P_over) else 0)) * inv2) % mod_int for i in range(max_deg + 1)]
        if sqrt_rev_new == sqrt_rev:
            break
        sqrt_rev = sqrt_rev_new
    # Reverse to get sqrt
    sqrt_poly = sqrt_rev[::-1]
    return sqrt_poly


def compute_aurif_AB(p, target_K=None, log_func=None):
    """Compute A, B such that M(p) = A^2 - 2p*B^2 via Hensel lifting."""
    def log_local(msg):
        if log_func:
            log_func(msg)
    
    half = (p - 1) // 2
    
    if target_K is None:
        # Need p^K > 2 * |A| ≈ 2 * 2^half = 2^(half+1)
        # log2(p^K) = K * log2(p) > half + 1
        target_K = max(20, int((half + 100) / max(1, float(gmpy2.log2(p)))) + 5)
    log_local(f"  target_K = {target_K}")
    
    # Initialize L mod p: try BOTH +(x-1)^half and -(x-1)^half
    L_pos = [0] * (half + 1)
    binom = 1
    sign = (-1) ** half
    L_pos[0] = (sign * binom) % p
    for j in range(1, half + 1):
        binom = (binom * (half - j + 1) * pow(j, -1, p)) % p
        sign = -sign
        L_pos[j] = (sign * binom) % p
    
    for L_sign_name, L_init in [('+', L_pos), ('-', [(-l) % p for l in L_pos])]:
        log_local(f"  Trying L sign = {L_sign_name}")
        
        # Compute M mod p from L mod p:
        # L^2 mod p^2, then R = (L^2 - Phi)/p, then M^2 = R/x mod p.
        p2 = p * p
        L = list(L_init)
        L_sq_p2 = poly_mult_mod_int(L, L, p2, 2 * half)
        R_p2 = [(L_sq_p2[i] - 1) % p2 for i in range(2 * half + 1)]
        if any(r % p != 0 for r in R_p2):
            log_local(f"    R not div by p for sign {L_sign_name}")
            continue
        R_div_p = [r // p for r in R_p2]
        if R_div_p[0] != 0:
            log_local(f"    R/p[0] = {R_div_p[0]} != 0 for sign {L_sign_name}")
            continue
        M_sq_p = [R_div_p[i+1] % p for i in range(2 * half - 1)]  # length 2*half - 1
        
        # Take polynomial sqrt of M_sq_p mod p.
        # Leading coeff: M[half-1] = ±sqrt(M_sq_p[2*half - 2]) mod p.
        # Try BOTH signs.
        leading_M_sq = M_sq_p[2 * half - 2]
        sqrt_leads = []
        for s in range(p):
            if (s * s) % p == leading_M_sq:
                sqrt_leads.append(s)
                if len(sqrt_leads) >= 2:
                    break
        
        for sqrt_lead in sqrt_leads:
            log_local(f"    Trying M leading coeff = {sqrt_lead}")
            M = poly_sqrt_high_first(M_sq_p, p, half - 1, sqrt_lead)
            # Verify
            M_check = poly_mult_mod_int(M, M, p, 2 * (half - 1))
            if M_check != M_sq_p:
                log_local(f"    M mod p verification failed for sqrt_lead = {sqrt_lead}")
                continue
            log_local(f"    M mod p verified, leading = {M[half-1]}, constant = {M[0]}")
            
            # Hensel lifting with both L and M updates
            mod = p
            L_cur = list(L)
            M_cur = list(M)
            hensel_ok = True
            inv2 = pow(2, -1, p)
            
            for k in range(target_K - 1):
                new_mod = mod * p
                
                # Lift L: L_new = L + mod * delta_L
                L_sq = poly_mult_mod_int(L_cur, L_cur, new_mod, 2 * half)
                M_sq = poly_mult_mod_int(M_cur, M_cur, new_mod, 2 * half - 1)
                x_M_sq = [0] + M_sq
                p_x_M_sq = [(p * c) % new_mod for c in x_M_sq]
                while len(p_x_M_sq) < 2 * half + 1:
                    p_x_M_sq.append(0)
                
                R = [((1 - L_sq[i] + p_x_M_sq[i]) % new_mod) for i in range(2 * half + 1)]
                
                for i, r in enumerate(R):
                    if r % mod != 0:
                        log_local(f"    Hensel L fails at k={k}, i={i}")
                        hensel_ok = False
                        break
                if not hensel_ok:
                    break
                
                R_div = [r // mod for r in R]
                # Solve 2 * delta_L * L_cur ≡ R_div mod p, delta_L of degree ≤ half.
                # Top-down: delta_L[half] = R_div[2*half] / (2 * L_cur[half]) mod p
                # Then continue down.
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
                
                # Lift M: M_new = M + mod * delta_M
                # Equation: (L_new)^2 - p * x * (M_new)^2 ≡ Phi mod new_mod
                # We've satisfied this with L_new (using M_cur mod mod).
                # For M_new: compute (L_new)^2 - Phi = p * x * M_new^2 in Z[x].
                # Take M_new^2 = ((L_new)^2 - Phi)/(p*x) mod new_mod.
                # Then sqrt to get M_new mod new_mod.
                
                # Compute (L_new)^2 mod (new_mod * p) to extract M_new mod new_mod.
                mod2 = new_mod * p  # = p^{k+2}
                L_new_sq = poly_mult_mod_int(L_cur, L_cur, mod2, 2 * half)
                diff = [(L_new_sq[i] - 1) % mod2 for i in range(2 * half + 1)]
                # Should be divisible by p
                for i, val in enumerate(diff):
                    if val % p != 0:
                        log_local(f"    M update fails at i={i}: diff={val}")
                        hensel_ok = False
                        break
                if not hensel_ok:
                    break
                diff_div_p = [val // p for val in diff]
                # diff_div_p = x * M_new^2 in Z[x] mod (mod2/p) = mod new_mod * p / p = mod new_mod? 
                # Hmm: diff_div_p is x * M_new^2 in Z[x], mod (mod2/p) = new_mod.
                # Wait, mod2 = new_mod * p, so mod2 / p = new_mod.
                # So diff_div_p is x * M_new^2 mod new_mod. Constant term should be 0.
                if diff_div_p[0] % new_mod != 0:
                    log_local(f"    M update: diff_div_p[0] = {diff_div_p[0]} not 0 mod new_mod")
                    hensel_ok = False
                    break
                # Take shift (divide by x): M_new^2[i] = diff_div_p[i+1] mod new_mod for i = 0, ..., 2*half-2
                M_new_sq = [diff_div_p[i+1] % new_mod for i in range(2 * half - 1)]
                
                # Take sqrt mod new_mod: M_new = M_cur + mod * delta_M.
                # Use the relation: M_new^2 ≡ M_new_sq mod new_mod.
                # M_cur^2 ≡ M_sq (current) mod mod (we have this from previous step).
                # Lift: solve 2 * M_cur * delta_M ≡ (M_new_sq - M_cur^2)/mod mod p for delta_M (degree ≤ half-1).
                M_sq_cur_mod_new = poly_mult_mod_int(M_cur, M_cur, new_mod, 2 * half - 1)
                diff_M_sq = [((M_new_sq[i] - (M_sq_cur_mod_new[i] if i < len(M_sq_cur_mod_new) else 0)) % new_mod) for i in range(2 * half - 1)]
                # diff_M_sq should be divisible by mod
                for i, val in enumerate(diff_M_sq):
                    if val % mod != 0:
                        log_local(f"    M delta fails at i={i}: val={val}")
                        hensel_ok = False
                        break
                if not hensel_ok:
                    break
                diff_M_div = [val // mod for val in diff_M_sq]
                
                # Solve 2 * M_cur * delta_M ≡ diff_M_div mod p (top-down)
                c = M_cur[half - 1] % p
                if c == 0:
                    log_local(f"    M_cur leading coeff 0 mod p, can't update M")
                    hensel_ok = False
                    break
                inv2c = pow(2 * c, -1, p)
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
                    log_local(f"    Step {k+1}/{target_K-1}, mod has {len(str(mod))} digits")
            
            if not hensel_ok:
                log_local(f"    Hensel failed for sign {L_sign_name}, sqrt_lead {sqrt_lead}")
                continue
            
            log_local(f"    Hensel complete!")
            
            # Evaluate L(2) mod p^K
            A_mod = 0
            pow2 = 1
            for i in range(half + 1):
                A_mod = (A_mod + L_cur[i] * pow2) % mod
                pow2 = (pow2 * 2) % mod
            
            # Try A_mod and A_mod - mod (for negative A)
            M_p_int = (1 << p) - 1
            for A_try in [A_mod, A_mod - mod]:
                diff = A_try * A_try - M_p_int
                if diff > 0 and diff % (2 * p) == 0:
                    B_sq = diff // (2 * p)
                    B = isqrt(mpz(B_sq))
                    if B * B == mpz(B_sq):
                        log_local(f"    >>> A = {A_try}")
                        log_local(f"    >>> B = {B}")
                        log_local(f"    Verify: A^2 - 2p B^2 = M(p)? {A_try**2 - 2*p*int(B)**2 == M_p_int}")
                        return A_try, int(B)
            
            log_local(f"    No integer A, B for this combination")
    
    return None, None


def cornacchia(D, p):
    """Find x, y such that x^2 + D*y^2 = p (prime), where (−D/p) = 1.
    Returns (x, y) or None.
    Modified for x^2 - D*y^2 = p (Pell-like).
    """
    # For x^2 - D*y^2 = p, we need x^2 ≡ p mod D, then (x^2 - p)/D should be a perfect square y^2.
    # Find x_0 = sqrt(p) mod D (using Tonelli-Shanks or similar).
    if jacobi(p % D, D) != 1:
        return None  # No solution
    # Find sqrt(p mod D) mod D
    # For D = 2p (our case), this is special.
    # Actually for x^2 - 2*p*y^2 = F1 (prime, with (2p/F1) = 1):
    # Find x_0 with x_0^2 ≡ F1 mod (2p), then y_0 = sqrt((x_0^2 - F1)/(2p)) if integer.
    # Or via continued fraction of sqrt(2p).
    # For simplicity, use brute force for small D.
    pass


def cornacchia_pell(D, N):
    """Find (x, y) with x^2 - D y^2 = N (N prime, (D/N) = 1).
    Uses continued fraction of sqrt(D).
    """
    # Compute continued fraction of sqrt(D)
    # Find x_0, y_0 by brute force using the relation x^2 ≡ N mod D.
    # Then iterate via continued fraction.
    # For our case D = 2*1237 = 2474, N = F1 (70 digits).
    # Brute force is infeasible.
    # Use Tonelli-Shanks to find sqrt(N) mod D, then verify.
    
    # Find r with r^2 ≡ N mod D
    D_int = int(D)
    N_int = int(N)
    # Use sympy or gmpy2 for sqrt mod D
    # For composite D = 2p, this is a multi-step process.
    # sqrt(N) mod 2: N is odd, so N mod 2 = 1, sqrt(1) mod 2 = 1.
    # sqrt(N) mod p (=1237): use Tonelli-Shanks since p is prime.
    # Then CRT.
    
    # Tonelli-Shanks for sqrt(N) mod p
    p = 1237  # hardcoded for our use case
    if jacobi(N_int, p) != 1:
        return None
    # Find r_p with r_p^2 ≡ N mod p
    # Use Tonelli-Shanks
    # N mod p
    N_mod_p = N_int % p
    # Find sqrt
    # For p = 1237, p - 1 = 1236 = 4 * 3 * 103. p ≡ 1 mod 4.
    # Use Tonelli-Shanks
    Q = p - 1
    S = 0
    while Q % 2 == 0:
        Q //= 2
        S += 1
    # Find a non-residue z
    z = 2
    while jacobi(z, p) != -1:
        z += 1
    M = S
    c = pow(z, Q, p)
    t = pow(N_mod_p, Q, p)
    R = pow(N_mod_p, (Q + 1) // 2, p)
    while True:
        if t == 0:
            return None
        if t == 1:
            r_p = R
            break
        # Find least i such that t^(2^i) = 1
        i = 1
        temp = (t * t) % p
        while temp != 1:
            temp = (temp * temp) % p
            i += 1
            if i >= M:
                return None
        b = pow(c, 1 << (M - i - 1), p)
        M = i
        c = (b * b) % p
        t = (t * c) % p
        R = (R * b) % p
    
    # Now r_p^2 ≡ N mod p, and 1^2 ≡ N mod 2 (since N is odd).
    # CRT: r such that r ≡ r_p mod p and r ≡ 1 mod 2.
    # Since p = 1237 is odd, use CRT.
    r = (r_p * 2 * pow(2, -1, p) + 1 * p * pow(p, -1, 2)) % (2 * p)
    # Verify r^2 ≡ N mod 2p
    if (r * r - N_int) % (2 * p) != 0:
        return None
    
    # Now use Cornacchia-style: find x with x ≡ r mod 2p, x in [0, 2p) initially, 
    # then iterate using continued fraction of sqrt(2p).
    # For Pell-like x^2 - 2p y^2 = N, the algorithm is more complex than for x^2 + 2p y^2 = N.
    # 
    # For indefinite forms, use infrastructure of Pell equation:
    # 1. Find fundamental solution (u, v) to u^2 - 2p v^2 = 1 via CF of sqrt(2p).
    # 2. Find ONE solution (x_0, y_0) to x^2 - 2p y^2 = N via CF of sqrt(2p) (looking for convergents p_k/q_k with p_k^2 - 2p q_k^2 = ±N).
    # 3. Multiply by units to get all solutions.
    
    # For our case, N = F1 is 70 digits, so y_0 ~ sqrt(N/(2p)) ~ sqrt(F1/2474) ~ 10^33.
    # The CF of sqrt(2p) needs to be computed to depth ~ log(y_0)/log(sqrt(2p)) ~ 70/sqrt(2474) ~ 1.4 ... 
    # Hmm, but for each convergent we check the norm.
    # Actually for the FUNDAMENTAL solution (x_0, y_0), y_0 can be much smaller than the full solution.
    
    # Let me just try direct brute force search over small y.
    # y from 0 to 10^6, check if N + 2p*y^2 is a perfect square.
    # This is too slow for large y_0.
    
    # Use the continued fraction method.
    # Compute CF of sqrt(2p) = sqrt(2474).
    import math
    sqrt_D = math.isqrt(2 * p)
    if sqrt_D * sqrt_D == 2 * p:
        return None  # Perfect square, no Pell
    # CF of sqrt(D)
    # m_0 = 0, d_0 = 1, a_0 = floor(sqrt(D))
    # m_{n+1} = d_n * a_n - m_n
    # d_{n+1} = (D - m_{n+1}^2) / d_n
    # a_{n+1} = floor((sqrt(D) + m_{n+1}) / d_{n+1})
    # Convergents: p_n = a_n p_{n-1} + p_{n-2}, q_n = a_n q_{n-1} + q_{n-2}
    # with p_{-1} = 1, p_{-2} = 0, q_{-1} = 0, q_{-2} = 1.
    
    D_val = 2 * p
    m, d, a = 0, 1, math.isqrt(D_val)
    p_prev, p_curr = 1, a
    q_prev, q_curr = 0, 1
    
    # Check convergent 0: (a, 1) with norm a^2 - D = a^2 - 2p.
    norm = p_curr * p_curr - D_val * q_curr * q_curr
    if norm == N_int:
        return (p_curr, q_curr)
    if norm == -N_int:
        # We have x^2 - D y^2 = -N. Multiply by fundamental solution of Pell.
        # Need to find fundamental (u, v) with u^2 - D v^2 = 1.
        # Then (x + y sqrt(D)) * (u + v sqrt(D)) = (xu + D yv) + (xv + yu) sqrt(D)
        # gives a new (x', y') with x'^2 - D y'^2 = -N (since (x + y sqrt(D))(x - y sqrt(D)) = -N
        # and multiplying by unit changes the norm by 1^2 = 1).
        # Hmm wait: norm((x + y sqrt(D)) * (u + v sqrt(D))) = norm(x + y sqrt(D)) * norm(u + v sqrt(D)) = -N * 1 = -N.
        # So this gives another solution to -N, not N.
        # We need to multiply by a unit of norm -1, or square the unit.
        # Squaring: (u + v sqrt(D))^2 has norm 1. Still doesn't flip -N to N.
        # 
        # For Pell, the unit (u, v) has norm 1 (assuming no solution of norm -1 exists).
        # If a solution of norm -1 exists, the fundamental unit has norm -1, and squaring gives norm 1.
        # 
        # For our problem, we want to find (x, y) with norm +N (not -N).
        # If we find (x_0, y_0) with norm -N, then (x_0 + y_0 sqrt(D)) * (u + v sqrt(D)) where (u, v) 
        # has norm -1 (if exists) gives norm N.
        # Otherwise, we need to find a different initial solution.
        pass
    
    # Continue CF
    max_iter = 10000
    for n in range(1, max_iter):
        m = d * a - m
        d = (D_val - m * m) // d
        a = (math.isqrt(D_val) + m) // d
        p_prev, p_curr = p_curr, a * p_curr + p_prev
        q_prev, q_curr = q_curr, a * q_curr + q_prev
        
        norm = p_curr * p_curr - D_val * q_curr * q_curr
        if abs(norm) == N_int:
            if norm == N_int:
                return (p_curr, q_curr)
            # If norm = -N, try multiplying by fundamental unit
            # For now, skip
        # Check if we've found the fundamental unit (norm = 1)
        if norm == 1 and (p_curr, q_curr) != (1, 0):
            # Fundamental unit found
            fundamental_unit = (p_curr, q_curr)
    
    return None


def main():
    p = 1237
    F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
    M = mpz(2)**p - 1
    N = M // F1
    
    log('=' * 70)
    log('Full Aurifeuillean-based factorization attempt')
    log(f'  Target: M({p})/F1, {len(str(N))} digits')
    log('=' * 70)
    
    # Step 1: Compute (A, B) for M(p) via Hensel lifting
    log('Step 1: Compute (A, B) for M(p) via Hensel lifting')
    t0 = time.time()
    A, B = compute_aurif_AB(p, log_func=log)
    elapsed = time.time() - t0
    log(f'  Total time: {elapsed:.1f}s')
    
    if A is None:
        log('  Failed to compute (A, B)')
        return
    
    log(f'  A has {len(str(abs(A)))} digits')
    log(f'  B has {len(str(abs(B)))} digits')
    
    # Step 2: Compute (a_1, b_1) for F1 via Cornacchia-Pell
    log('')
    log('Step 2: Compute (a_1, b_1) for F1 via Cornacchia-Pell')
    t0 = time.time()
    result = cornacchia_pell(2 * p, int(F1))
    elapsed = time.time() - t0
    log(f'  Time: {elapsed:.1f}s')
    if result is None:
        log('  Failed to find (a_1, b_1)')
        return
    a_1, b_1 = result
    log(f'  a_1 = {a_1}')
    log(f'  b_1 = {b_1}')
    log(f'  Verify: a_1^2 - 2p b_1^2 = F1? {a_1**2 - 2*p*b_1**2 == int(F1)}')
    
    # Step 3: Compute (A', B') for N = M(p)/F1
    log('')
    log('Step 3: Compute (A_prime, B_prime) for N via (A + B sqrt(2p))/(a_1 + b_1 sqrt(2p))')
    # A' = (A * a_1 - 2p * B * b_1) / F1
    # B' = (B * a_1 - A * b_1) / F1
    A_prime_num = A * a_1 - 2 * p * B * b_1
    B_prime_num = B * a_1 - A * b_1
    if A_prime_num % int(F1) != 0 or B_prime_num % int(F1) != 0:
        log('  Division not exact, wrong sign somewhere')
        # Try with b_1 negative
        b_1_neg = -b_1
        A_prime_num = A * a_1 - 2 * p * B * b_1_neg
        B_prime_num = B * a_1 - A * b_1_neg
        if A_prime_num % int(F1) != 0 or B_prime_num % int(F1) != 0:
            log('  Still not exact, abort')
            return
    A_prime = A_prime_num // int(F1)
    B_prime = B_prime_num // int(F1)
    log(f'  A_prime has {len(str(abs(A_prime)))} digits')
    log(f'  B_prime has {len(str(abs(B_prime)))} digits')
    log(f'  Verify: A_prime^2 - 2p B_prime^2 = N? {A_prime**2 - 2*p*B_prime**2 == int(N)}')
    
    if A_prime**2 - 2 * p * B_prime**2 != int(N):
        log('  Verification failed!')
        return
    
    # Step 4: Compute R1 = A' * B'^{-1} mod N (sqrt of 2p mod N)
    log('')
    log('Step 4: Compute R1 = A_prime * B_prime^-1 mod N')
    B_prime_mpz = mpz(B_prime)
    A_prime_mpz = mpz(A_prime)
    # Check gcd(B_prime, N)
    g = gcd(B_prime_mpz, N)
    if 1 < int(g) < int(N):
        log(f'  >>> FACTOR from gcd(B_prime, N) = {g}')
        # Update factor file
        lines = FACTORS_FILE.read_text(encoding='utf-8').splitlines(keepends=True)
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
        FACTORS_FILE.write_text(''.join(out), encoding='utf-8')
        return
    
    if g == 0:
        log('  B_prime = 0, can\'t invert')
        return
    
    try:
        B_prime_inv = invert(abs(B_prime_mpz), N)
    except Exception as e:
        log(f'  B_prime not invertible mod N: {e}')
        return
    
    R1 = (A_prime_mpz * B_prime_inv) % N
    log(f'  R1 = A_prime * B_prime^-1 mod N (computed)')
    # Verify
    R1_sq = (R1 * R1) % N
    expected = (2 * p) % N
    log(f'  R1^2 mod N == 2p mod N? {R1_sq == expected}')
    if R1_sq != expected:
        log('  R1 is not a sqrt of 2p mod N, something wrong')
        return
    
    # Step 5: Find another sqrt of 2p mod N via Cipolla
    log('')
    log('Step 5: Find another sqrt(2p) mod N via Cipolla')
    other_roots = []
    for _ in range(50):
        t = mpz(random.randint(2, int(N) - 1))
        d = (t * t - 2 * p) % N
        if d == 0:
            continue
        try:
            j = jacobi(d, N)
        except:
            continue
        # Cipolla ladder
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
            if (r_cipolla * r_cipolla - 2 * p) % N == 0:
                other_roots.append(int(r_cipolla))
                if len(other_roots) >= 5:
                    break
    
    log(f'  Found {len(other_roots)} Cipolla roots')
    
    # Step 6: Compute gcd(R1 - R_cipolla, N) for each Cipolla root
    log('')
    log('Step 6: Try gcd(R1 ± R_cipolla, N) for each Cipolla root')
    for i, r_other in enumerate(other_roots):
        g = gcd(int(R1) - r_other, int(N))
        if 1 < g < int(N):
            log(f'  >>> FACTOR FOUND: gcd(R1 - R_{i}, N) = {g}')
            log(f'      Factor has {len(str(g))} digits')
            # Update factors file
            lines = FACTORS_FILE.read_text(encoding='utf-8').splitlines(keepends=True)
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
            FACTORS_FILE.write_text(''.join(out), encoding='utf-8')
            return
        g = gcd(int(R1) + r_other, int(N))
        if 1 < g < int(N):
            log(f'  >>> FACTOR FOUND: gcd(R1 + R_{i}, N) = {g}')
            log(f'      Factor has {len(str(g))} digits')
            lines = FACTORS_FILE.read_text(encoding='utf-8').splitlines(keepends=True)
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
            FACTORS_FILE.write_text(''.join(out), encoding='utf-8')
            return
    
    # Also try pairwise gcd among Cipolla roots
    log('Pairwise gcd among Cipolla roots:')
    for i in range(len(other_roots)):
        for j in range(i + 1, len(other_roots)):
            g = gcd(other_roots[i] - other_roots[j], int(N))
            if 1 < g < int(N):
                log(f'  >>> FACTOR: gcd(R_{i} - R_{j}, N) = {g}')
                return
            g = gcd(other_roots[i] + other_roots[j], int(N))
            if 1 < g < int(N):
                log(f'  >>> FACTOR: gcd(R_{i} + R_{j}, N) = {g}')
                return
    
    log('')
    log('No factor found via Rabin-style attack')


if __name__ == '__main__':
    main()
