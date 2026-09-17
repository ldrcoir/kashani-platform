#!/usr/bin/env python3
"""
Creative approach: Pell + Aurifeuillean + Rabin factoring of C303.

For p = 1237, M(p) = A^2 - 2p*B^2 (Aurifeuillean identity).
F1 = a1^2 - 2p*b1^2 (Pell-like representation of F1, since (2p/F1) = +1).
N = M(p)/F1 = A'^2 - 2p*B'^2 where (A', B') = (A + B√2p)/(a1 + b1√2p).
R = A' * B'^(-1) mod N is sqrt(2p) mod N (a specific root).
R' = another sqrt of 2p mod N (from Tonelli-Shanks or other method).
If R ≠ ±R' (mod N), then gcd(R - R', N) gives a non-trivial factor of N!

Step 1: Solve Pell x^2 - 2p*y^2 = F1 via continued fraction of sqrt(2p).
        For F1 = 70 digits, need ~350 convergents.
Step 2: Solve Pell x^2 - 2p*y^2 = M(1237). 
        For M(1237) = 373 digits, need ~1800 convergents.
        BUT: standard CF doesn't necessarily find this specific norm.
        Actually, if (2p/M(1237)) = +1 (which is +1 since Aurifeuillean), 
        the equation has a solution. Use Lagrange-Matthews-Mollin algorithm.
        OR: use the structure M(1237) = 2^1237 - 1 to find a specific solution.
        
Alternative for Step 2: COMPUTE Aurifeuillean (A, B) directly via Hensel lifting
or via Brent's algorithm. Then verify A^2 - 2p*B^2 = M(1237).
"""

import sys
import time
from pathlib import Path
from math import isqrt, gcd
import gmpy2
from gmpy2 import mpz, isqrt as gmp_isqrt, is_prime, gcd as gmpy_gcd, powmod, invert, jacobi

# Allow large integer string conversion
sys.set_int_max_str_digits(1000000)

BASE = Path('/home/z/my-project')
LOG = BASE / 'logs/pell_rabin.log'
LOG.parent.mkdir(exist_ok=True)


def log(msg):
    print(msg, flush=True)
    with open(LOG, 'a') as f:
        f.write(msg + '\n')


def continued_fraction_sqrt_D(D, max_convergents=5000):
    """Compute continued fraction expansion of sqrt(D).
    Yields (p_k, q_k) for convergents, where p_k^2 - D*q_k^2 = a_k (the partial quotients).
    
    Uses the standard algorithm:
    m_0 = 0, d_0 = 1, a_0 = floor(sqrt(D))
    m_{n+1} = d_n * a_n - m_n
    d_{n+1} = (D - m_{n+1}^2) / d_n
    a_{n+1} = floor((sqrt(D) + m_{n+1}) / d_{n+1})
    Convergents: p_{-1} = 1, p_0 = a_0; q_{-1} = 0, q_0 = 1
    p_{n+1} = a_{n+1} * p_n + p_{n-1}
    q_{n+1} = a_{n+1} * q_n + q_{n-1}
    """
    a0 = isqrt(D)
    if a0 * a0 == D:
        return  # D is perfect square
    
    m, d, a = 0, 1, a0
    p_prev, p_curr = 1, a0
    q_prev, q_curr = 0, 1
    
    # First convergent
    yield (p_curr, q_curr)
    
    for n in range(max_convergents):
        m = d * a - m
        d = (D - m * m) // d
        a = (isqrt(D) + m) // d
        p_prev, p_curr = p_curr, a * p_curr + p_prev
        q_prev, q_curr = q_curr, a * q_curr + q_prev
        yield (p_curr, q_curr)


def solve_pell_equation(D, N, max_convergents=100000):
    """Solve x^2 - D*y^2 = N using continued fraction method.
    
    Returns (x, y) with x^2 - D*y^2 = N or x^2 - D*y^2 = -N (any representation).
    For positive N: search for convergent with norm = N or -N.
    """
    log(f"  Solving x^2 - {D}*y^2 = {N} (N has {len(str(N))} digits)")
    log(f"  Searching convergents of sqrt({D})...")
    
    t0 = time.time()
    found = None
    for k, (p, q) in enumerate(continued_fraction_sqrt_D(D, max_convergents)):
        norm = p * p - D * q * q
        if norm == N:
            found = (p, q, +1)
            break
        if norm == -N:
            found = (p, q, -1)
            break
        if k % 1000 == 0 and k > 0:
            elapsed = time.time() - t0
            log(f"    k={k}, p has {len(str(p))} digits, elapsed {elapsed:.1f}s")
    
    if found:
        log(f"  Found at k={k}: ({found[0]}, {found[1]}), norm = {found[2] * N}")
        return found
    log(f"  No solution found in {max_convergents} convergents")
    return None


def main():
    p = 1237
    D = 2 * p  # = 2474
    M_p = mpz(2)**p - 1
    F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
    N = M_p // F1
    
    log('=' * 70)
    log('Pell + Aurifeuillean + Rabin factoring of C303')
    log(f'  p = {p}, D = 2p = {D}')
    log(f'  F1 = {F1} ({len(str(F1))} digits)')
    log(f'  N = M(p)/F1 ({len(str(N))} digits)')
    log('=' * 70)
    
    # Verify (2p/F1) = +1 (necessary for Pell solution to exist)
    j_f1 = jacobi(D, int(F1))
    log(f'  (2p/F1) = {j_f1} (need +1 for Pell solution)')
    if j_f1 != 1:
        log('  (2p/F1) != 1, no Pell solution. Abort.')
        return
    
    # Step 1: Solve x^2 - 2p*y^2 = F1
    log('')
    log('Step 1: Solve Pell-like x^2 - 2p*y^2 = F1')
    t0 = time.time()
    result_F1 = solve_pell_equation(D, int(F1), max_convergents=200000)
    elapsed = time.time() - t0
    log(f'  Time: {elapsed:.1f}s')
    
    if result_F1 is None:
        log('  Could not find Pell solution for F1')
        return
    a1, b1, sign_F1 = result_F1
    log(f'  Solution: a1 = {a1}, b1 = {b1}')
    log(f'  Verify: a1^2 - {D}*b1^2 = {a1*a1 - D*b1*b1} (should equal {sign_F1 * int(F1)})')
    
    if sign_F1 == -1:
        log('  Got norm = -F1. Need to multiply by fundamental unit of norm -1 if exists,')
        log('  or by fundamental unit squared (norm 1). Skipping for now - try sign +1.')
        # Try to convert -F1 solution to +F1 solution by multiplying by fundamental unit
        # For now, just continue and accept the -F1 representation
    
    # Step 2: Find Aurifeuillean (A, B) for M(1237) = A^2 - 2p*B^2
    # Method 1: Try Pell x^2 - 2p*y^2 = M(1237)
    log('')
    log('Step 2: Find Aurifeuillean (A, B) for M(p) = A^2 - 2p*B^2')
    log('  Method 1: Solve Pell x^2 - 2p*y^2 = M(p)')
    t0 = time.time()
    # M(p) is 373 digits. Need about 373/log10(φ) ≈ 1785 convergents.
    # But convergents only reach norms in a specific range. To hit a specific norm like M(p),
    # we may need MANY more convergents.
    # For Pell-like equations, the standard approach is to find the smallest solution,
    # not just any convergent. For huge N, this is hard.
    # We'll try a few thousand convergents.
    result_M = solve_pell_equation(D, int(M_p), max_convergents=5000)
    elapsed = time.time() - t0
    log(f'  Time: {elapsed:.1f}s')
    
    if result_M is None:
        log('  Standard CF did not yield M(p) directly. Try infrastructure approach.')
        log('  Or use Aurifeuillean Hensel lifting (different algorithm).')
        return
    A, B, sign_M = result_M
    log(f'  Solution: A = {A}, B = {B}')
    log(f'  Verify: A^2 - {D}*B^2 = {A*A - D*B*B} (should equal {sign_M * int(M_p)})')
    
    if sign_M == -1:
        log('  Got norm = -M(p). Convert to +M(p) by multiplying by unit of norm -1.')
        # Try to find unit of norm -1 first
        # The fundamental solution of Pell u^2 - D v^2 = 1 or -1
        # We found one for M(p), need to check if there's also a -1 solution
        # If u^2 - D v^2 = -1 exists, multiplying our -M(p) solution by it gives +M(p).
        # If only u^2 - D v^2 = 1 exists (no -1 solution), then we can't flip -M(p) to +M(p) easily.
        log('  Skipping sign flip for now.')
    
    # Step 3: Compute (A', B') = (A + B√2p) / (a1 + b1√2p)
    log('')
    log('Step 3: Compute (A_prime, B_prime) for N = M(p)/F1')
    # (A + B√D) / (a1 + b1√D) = (A + B√D)(a1 - b1√D) / (a1^2 - D b1^2) = (A a1 - D B b1 + (B a1 - A b1) √D) / F1
    # So A' = (A * a1 - D * B * b1) / F1
    #    B' = (B * a1 - A * b1) / F1
    # Note: signs depend on signs of (A, B) and (a1, b1).
    # Need to find the right sign combination that gives integer (A', B').
    
    A_mpz = mpz(A)
    B_mpz = mpz(B)
    a1_mpz = mpz(a1)
    b1_mpz = mpz(b1)
    F1_mpz = mpz(F1)
    
    # Try sign combinations
    for sign_a1 in [1, -1]:
        for sign_b1 in [1, -1]:
            for sign_A in [1, -1]:
                for sign_B in [1, -1]:
                    A_num = sign_A * A_mpz * (sign_a1 * a1_mpz) - D * (sign_B * B_mpz) * (sign_b1 * b1_mpz)
                    B_num = (sign_B * B_mpz) * (sign_a1 * a1_mpz) - (sign_A * A_mpz) * (sign_b1 * b1_mpz)
                    if A_num % F1_mpz == 0 and B_num % F1_mpz == 0:
                        A_prime = int(A_num // F1_mpz)
                        B_prime = int(B_num // F1_mpz)
                        # Verify
                        verify = A_prime * A_prime - D * B_prime * B_prime
                        if verify == int(N):
                            log(f'  Found valid (A_prime, B_prime)!')
                            log(f'  A_prime has {len(str(A_prime))} digits')
                            log(f'  B_prime has {len(str(B_prime))} digits')
                            log(f'  Verify: A_prime^2 - 2p B_prime^2 = N ✓')
                            
                            # Step 4: Compute R = A_prime * B_prime^-1 mod N (sqrt of 2p mod N)
                            log('')
                            log('Step 4: Compute R = A_prime * B_prime^-1 mod N (sqrt of 2p mod N)')
                            B_prime_mpz = mpz(abs(B_prime))
                            N_mpz = mpz(N)
                            g = gmpy_gcd(B_prime_mpz, N_mpz)
                            log(f'  gcd(B_prime, N) = {g}')
                            if 1 < int(g) < int(N):
                                log(f'  >>> FACTOR FOUND: gcd(B_prime, N) = {g}')
                                log(f'      Factor has {len(str(g))} digits')
                                # Update factor file
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
                            
                            try:
                                B_inv = invert(B_prime_mpz, N_mpz)
                            except:
                                log('  B_prime not invertible mod N')
                                continue
                            
                            R = (mpz(A_prime) * B_inv) % N_mpz
                            log(f'  R has {len(str(R))} digits')
                            # Verify R^2 ≡ 2p mod N
                            R_sq = (R * R) % N_mpz
                            expected = mpz(2 * p) % N_mpz
                            log(f'  Verify: R^2 mod N == 2p mod N? {R_sq == expected}')
                            if R_sq != expected:
                                continue
                            
                            # Step 5: Find ANOTHER sqrt of 2p mod N via Tonelli-Shanks (modified for composite)
                            # For composite N with (2p/N) = +1, sqrt exists but Tonelli-Shanks may not work directly.
                            # Use Cipolla-style algorithm with random t.
                            log('')
                            log('Step 5: Find another sqrt(2p) mod N')
                            other_roots = []
                            import random
                            random.seed(42)
                            
                            for trial in range(50):
                                # Cipolla: find t such that t^2 - 2p is a Jacobi non-residue mod N
                                for _ in range(50):
                                    t = mpz(random.randint(2, int(N) - 1))
                                    d = (t * t - 2 * p) % N_mpz
                                    if d == 0:
                                        continue
                                    try:
                                        j = jacobi(int(d), int(N))
                                    except:
                                        continue
                                    if j == -1:
                                        break
                                else:
                                    continue
                                
                                # Cipolla ladder: (t + x)^((N+1)/2) in F_N[x]/(x^2 - d)
                                u, v = t, mpz(1)
                                exp = (N_mpz + 1) // 2
                                bits = bin(int(exp))[2:]
                                cur_u, cur_v = mpz(1), mpz(0)
                                for bit in bits:
                                    new_u = (cur_u * cur_u + d * cur_v * cur_v) % N_mpz
                                    new_v = (2 * cur_u * cur_v) % N_mpz
                                    cur_u, cur_v = new_u, new_v
                                    if bit == '1':
                                        new_u = (cur_u * t + d * cur_v) % N_mpz
                                        new_v = (cur_u + cur_v * t) % N_mpz
                                        cur_u, cur_v = new_u, new_v
                                
                                if cur_v == 0:
                                    r_cipolla = cur_u
                                    if (r_cipolla * r_cipolla - 2 * p) % N_mpz == 0:
                                        other_roots.append(int(r_cipolla))
                                        if len(other_roots) >= 5:
                                            break
                            
                            log(f'  Found {len(other_roots)} Cipolla roots')
                            
                            # Step 6: Try gcd(R ± Cipolla_root, N)
                            log('')
                            log('Step 6: Try gcd(R ± other_root, N)')
                            factor_found = None
                            for i, r_other in enumerate(other_roots):
                                g = gmpy_gcd(int(R) - r_other, int(N))
                                if 1 < int(g) < int(N):
                                    log(f'  >>> FACTOR FOUND: gcd(R - R_{i}, N) = {g}')
                                    log(f'      Factor has {len(str(g))} digits')
                                    factor_found = int(g)
                                    break
                                g = gmpy_gcd(int(R) + r_other, int(N))
                                if 1 < int(g) < int(N):
                                    log(f'  >>> FACTOR FOUND: gcd(R + R_{i}, N) = {g}')
                                    log(f'      Factor has {len(str(g))} digits')
                                    factor_found = int(g)
                                    break
                            
                            if factor_found:
                                # Update factor file
                                lines = (BASE / 'download/A136030_factors_1_to_8000.txt').read_text().splitlines(keepends=True)
                                out = []
                                for line in lines:
                                    if line.startswith('#'):
                                        out.append(line); continue
                                    parts = line.split('\t')
                                    if len(parts) >= 2 and parts[0] == str(p):
                                        cur = parts[1].strip()
                                        if cur == '-1' or factor_found < int(cur):
                                            out.append(f'{p}\t{factor_found}\n')
                                        else:
                                            out.append(line)
                                    else:
                                        out.append(line)
                                (BASE / 'download/A136030_factors_1_to_8000.txt').write_text(''.join(out))
                                log('  Updated factors table!')
                                return
                            
                            log('  No non-trivial gcd found')
                            return
    
    log('  Could not find valid sign combination for (A_prime, B_prime)')
    log('  This means our Pell solutions may have wrong sign, or different relation.')


if __name__ == '__main__':
    main()
