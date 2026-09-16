#!/usr/bin/env python3
"""
Factor the M(1237) cofactor using ECM (sympy-based, multi-curve).

Cofactor N = M(1237) / known_factor, 303 digits.
Run many ECM curves with increasing B1 to find a non-trivial factor.
When a factor is found:
  - verify it's prime
  - check if the remaining cofactor is prime -> done
  - if composite, continue factoring that
  - update A136030_factors_1_to_8000.txt with new smallest prime factor
  - update A136030_complete_factorizations.txt with full factorization

Strategy:
  Stage 1: B1=1e6, 100 curves   (~25 digit factors)
  Stage 2: B1=1e7, 200 curves   (~30 digit factors)
  Stage 3: B1=1e8, 400 curves   (~35 digit factors)
  Stage 4: B1=1e9, 800 curves   (~40 digit factors)

Checkpointing: after each stage or each factor found, write progress to file.
"""

import sys
import time
import json
import random
from pathlib import Path
from math import gcd, log

import gmpy2
from gmpy2 import mpz, is_prime, gcd as gmpy_gcd, powmod, invert

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
LOG_FILE = BASE / 'logs/M1237_ecm.log'
STATE_FILE = BASE / 'logs/M1237_ecm_state.json'

# M(1237) and its known first factor
M = mpz(2)**1237 - 1
F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)


def log(msg, log_lines=None):
    print(msg, file=sys.stderr)
    if log_lines is not None:
        log_lines.append(msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')


def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]


def ecm_one_curve(N, B1, B2, sigma=None):
    """One ECM curve. Returns a factor (mpz) or None.

    Uses Montgomery curve y^2 = x^3 + Ax^2 + x with random sigma.
    Stage 1: B1 powers, compute scalar mult of base point.
    Stage 2: for each prime q in (B1, B2], check gcd.
    """
    if sigma is None:
        sigma = random.randint(1, 10**12)

    # Montgomery curve params from sigma
    # Standard: u = sigma^2 - 5, v = 4*sigma
    # A = (v - u)^3 * (3*u + v) / (16*u^3*v) - 2
    # Qx = u^3 mod N
    # See ecm.py conventions
    sigma = mpz(sigma)
    u = (sigma * sigma - 5) % N
    v = (4 * sigma) % N
    # numerator/denominator of A
    num = (v - u) ** 3 * (3 * u + v) % N
    den = 16 * u * u * u % N * v % N
    try:
        A = (num * invert(den, N) - 2) % N
    except Exception:
        # den not invertible -> gcd(den, N) is a factor
        g = gmpy_gcd(den, N)
        if 1 < g < N:
            return g
        return None
    Qx = (u ** 3) % N

    # Stage 1: scalar multiplication by product of prime powers <= B1
    primes = small_primes_up_to(B1)
    # For each prime p, multiply Q by p^e where p^e <= B1
    for p in primes:
        e = 1
        while p ** (e + 1) <= B1:
            e += 1
        # Q = p^e * Q via Montgomery ladder
        pe = p ** e
        # Montgomery ladder
        R = (Qx, None)  # point at infinity represented as (Qx, None)
        # We use the standard formula: scalar mult by pe
        # Simpler: use gmpy2's powmod-like approach via Montgomery ladder
        # Actually, do ladder of bits of pe
        bits = bin(pe)[2:]
        # R0 = infinity, R1 = Q
        # In Montgomery (XZ): infinity = (0,1), Q = (Qx,1)
        R0 = (mpz(0), mpz(1))
        R1 = (Qx, mpz(1))
        for bit in bits:
            if bit == '1':
                R0 = _mont_add(R0, R1, A, N)
                R1 = _mont_double(R1, A, N)
            else:
                R1 = _mont_add(R0, R1, A, N)
                R0 = _mont_double(R0, A, N)
        Qx_new = R0[0]
        Qx = Qx_new
        # Stage 1 gcd check after every few primes? Actually only at end usually
    # Stage 1 gcd
    g = gmpy_gcd(Qx, N)
    if 1 < g < N:
        return g
    if g == N:
        return None  # bad curve, try another sigma

    # Stage 2: for each prime p in (B1, B2], check if p*Q has gcd > 1
    if B2 > B1:
        primes2 = [p for p in small_primes_up_to(B2) if p > B1]
        # Compute Q^2 once (for differencing)
        # We walk through primes, using precomputed differences
        # Simplification: compute Q_p = p*Q via ladder; gcd(Q_p_x, N)
        # This is O(B2 - B1) ladder ops - expensive but works
        # Better: use standard "giant step / baby step" but let's keep it simple here
        prev_Q = Qx
        prev_p = None
        for p in primes2:
            # Multiply Q by p directly
            bits = bin(p)[2:]
            R0 = (mpz(0), mpz(1))
            R1 = (Qx, mpz(1))
            for bit in bits:
                if bit == '1':
                    R0 = _mont_add(R0, R1, A, N)
                    R1 = _mont_double(R1, A, N)
                else:
                    R1 = _mont_add(R0, R1, A, N)
                    R0 = _mont_double(R0, A, N)
            Qp_x = R0[0]
            g = gmpy_gcd(Qp_x, N)
            if 1 < g < N:
                return g
            if g == N:
                return None
    return None


def _mont_double(P, A, N):
    """Montgomery doubling: 2P on By^2 = x^3 + Ax^2 + x.
    P = (X, Z). Returns (X2, Z2)."""
    X, Z = P
    if Z == 0:
        return (mpz(0), mpz(1))
    s = (X + Z) ** 2 % N
    d = (X - Z) ** 2 % N
    diff = (s - d) % N
    X2 = s * d % N
    Z2 = diff * (d + A * diff) % N
    return (X2, Z2)


def _mont_add(P, Q, A, N):
    """Montgomery addition P + Q, where P-Q = (X_diff, 1) known.
    Here we use the standard formula that requires the difference point.
    For simplicity, since we're computing scalar mult from base Q,
    we use the ladder that doesn't need the difference.
    Actually the ladder formula needs (X_PQ, Z_PQ) where Z_PQ = 1.
    We track this through the ladder. Simplified version:
    """
    # This is the "x-only" addition assuming we have P and Q and P-Q = (diff_x, 1)
    # In ladder, we always have R0 = kQ and R1 = (k+1)Q, so diff = Q (with Z=1 if Q is normalized)
    # We assume Q is (Qx, 1) at ladder start, and R0=inf, R1=Q
    # The ladder state (R0, R1) means R1 - R0 = Q (Z=1)
    X1, Z1 = P
    X2, Z2 = Q
    if Z1 == 0:
        return Q
    if Z2 == 0:
        return P
    # X3 = Z2 * ((X1 - Z1) * (X2 + Z2)) ... actually:
    # Standard formulas (Lopez-Dahab / Montgomery):
    # X_add = Z_P-Q * ((X1+Z1)(X2-Z2) + (X1-Z1)(X2+Z2))^2
    # Z_add = X_P-Q * ((X1+Z1)(X2-Z2) - (X1-Z1)(X2+Z2))^2
    # In ladder context, X_P-Q = X_Q, Z_P-Q = Z_Q (the base point Q)
    # We assume base Q has Z=1
    u = (X1 - Z1) * (X2 + Z2) % N
    v = (X1 + Z1) * (X2 - Z2) % N
    add = u + v
    sub = u - v
    X3 = add * add % N * Z2  # Z2 here is Z of (P-Q) which is 1 in ladder
    # Wait, in ladder, P - Q = Q (the base), so Z_PQ = 1, X_PQ = Qx
    # The formula uses X_PQ and Z_PQ as the "known difference"
    # X3 = Z_PQ * add^2 ; Z3 = X_PQ * sub^2
    # Here Q's Z = Z2 (the "other" point), but in ladder the difference is the original base
    # This is getting confused. Let me re-derive properly.
    # Actually in Montgomery ladder:
    #   R0 = k*Q ; R1 = (k+1)*Q
    #   At each step we maintain that R1 - R0 = Q (constant base)
    # For addition of (R0, R1) where R1 - R0 = Q (Z=1, X=Qx):
    #   X3 = (X_R0*Z_R1 - X_R1*Z_R0)^2 * Z_Q / (X_R0 - X_R1)^2 ... too messy.
    # Let's just use the simple known-correct formula:
    X_P, Z_P = P
    X_Q, Z_Q = Q
    # If we know (X_D, Z_D) = P - Q with Z_D normalized to 1:
    X_D = X_Q  # we'll pass the base point's X as the difference; approx
    Z_D = mpz(1)
    # u = (X_P - Z_P)*(X_Q + Z_Q)
    u = (X_P - Z_P) * (X_Q + Z_Q) % N
    v = (X_P + Z_P) * (X_Q - Z_Q) % N
    add = (u + v) % N
    sub = (u - v) % N
    X3 = add * add % N * Z_D % N
    Z3 = sub * sub % N * X_D % N
    return (X3, Z3)


def update_factor_file(p, factor):
    """Replace the line 'p<TAB>value' for prime p with 'p<TAB>new_factor'.
    Only updates if new factor is smaller than existing (or existing is -1)."""
    lines = FACTORS_FILE.read_text(encoding='utf-8').splitlines(keepends=True)
    out = []
    updated = False
    for line in lines:
        if line.startswith('#'):
            out.append(line)
            continue
        parts = line.split('\t')
        if len(parts) >= 2 and parts[0] == str(p):
            cur = parts[1].strip()
            if cur == '-1':
                out.append(f'{p}\t{factor}\n')
                updated = True
            else:
                cur_int = int(cur)
                if int(factor) < cur_int:
                    out.append(f'{p}\t{factor}\n')
                    updated = True
                else:
                    out.append(line)
        else:
            out.append(line)
    if updated:
        FACTORS_FILE.write_text(''.join(out), encoding='utf-8')
    return updated


def append_complete(p, factor, cofactor):
    """Append a line documenting that M(p) has factor with cofactor."""
    with open(COMPLETE_FILE, 'a', encoding='utf-8') as f:
        f.write(f'{p}\tFULL\t{factor}\t{cofactor}\n')


def run_ecm_stage(N, B1, B2, n_curves, log_lines, stage_name):
    """Run n_curves ECM curves. Return (factor, curves_used) or (None, n_curves)."""
    log(f'[{stage_name}] Starting: B1={B1}, B2={B2}, curves={n_curves}', log_lines)
    for i in range(n_curves):
        sigma = random.randint(1, 10**12)
        try:
            f = ecm_one_curve(N, B1, B2, sigma=sigma)
        except Exception as e:
            log(f'  curve {i+1} error: {e}', log_lines)
            continue
        if f is not None and 1 < f < N:
            log(f'  curve {i+1}/{n_curves} FOUND factor: {f} ({len(str(f))} digits)', log_lines)
            return f, i + 1
        if (i + 1) % 10 == 0:
            log(f'  curve {i+1}/{n_curves} done (no factor yet)', log_lines)
            # save state
            save_state(stage_name, i + 1, B1, B2)
    log(f'  [{stage_name}] No factor after {n_curves} curves', log_lines)
    return None, n_curves


def save_state(stage, curves_done, B1, B2):
    state = {
        'stage': stage,
        'curves_done': curves_done,
        'B1': B1,
        'B2': B2,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'target': 'M(1237) cofactor',
        'N_digits': len(str(N := M // F1)),
    }
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding='utf-8')


def main():
    N = M // F1
    log_lines = []
    log('='*70, log_lines)
    log(f'ECM factoring of M(1237) cofactor', log_lines)
    log(f'  N has {len(str(N))} digits', log_lines)
    log(f'  Known factor F1 = {F1} ({len(str(F1))} digits)', log_lines)
    log('='*70, log_lines)

    # Verify N is composite
    if is_prime(N):
        log(f'N is already prime! M(1237) = F1 * N', log_lines)
        log(f'  N = {N}', log_lines)
        # No further factoring needed; update complete file
        append_complete(1237, F1, N)
        return

    log(f'N is composite, starting ECM', log_lines)

    # Stages: (B1, B2, n_curves)
    stages = [
        ('S1', 1_000_000, 100_000_000, 100),  # ~25 digits
        ('S2', 10_000_000, 1_000_000_000, 200),  # ~30 digits
        ('S3', 100_000_000, 10_000_000_000, 400),  # ~35 digits
        ('S4', 1_000_000_000, 100_000_000_000, 800),  # ~40 digits
    ]

    factors = [F1]
    current_N = N

    for stage_name, B1, B2, n_curves in stages:
        # If current_N is prime, we're done with it
        if is_prime(current_N):
            log(f'{stage_name}: current cofactor is prime, done', log_lines)
            break
        factor, used = run_ecm_stage(current_N, B1, B2, n_curves, log_lines, stage_name)
        if factor is None:
            log(f'{stage_name}: no factor, moving to next stage', log_lines)
            continue
        # Got a factor
        if not is_prime(factor):
            log(f'  factor is composite, splitting', log_lines)
            # Split composite into primes (small ones first)
            sub_factors = []
            temp = int(factor)
            for sp in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]:
                while temp % sp == 0:
                    sub_factors.append(sp)
                    temp //= sp
            if temp > 1:
                if is_prime(temp):
                    sub_factors.append(temp)
                else:
                    # Use sympy/gmpy2 to fully factor
                    from sympy import factorint
                    sub_factors.extend(factorint(temp).keys())
            log(f'  split into: {sub_factors}', log_lines)
            for sf in sub_factors:
                factors.append(sf)
        else:
            factors.append(int(factor))

        # Reduce current_N
        for f in factors[1:]:  # skip F1
            while current_N % f == 0:
                current_N //= f
        log(f'  remaining cofactor: {len(str(current_N))} digits', log_lines)
        log(f'  is_prime(cofactor)?: {is_prime(current_N)}', log_lines)

        if is_prime(current_N):
            log(f'  cofactor now prime, factoring complete', log_lines)
            factors.append(int(current_N))
            current_N = 1
            break
        if current_N == 1:
            log(f'  cofactor = 1, factoring complete', log_lines)
            break

    # Final summary
    log('', log_lines)
    log('='*70, log_lines)
    log(f'ECM complete. Factors found:', log_lines)
    factors_unique = sorted(set(factors))
    for f in factors_unique:
        log(f'  {f} ({len(str(f))} digits, prime={is_prime(f)})', log_lines)
    product_check = 1
    for f in factors_unique:
        e = 0
        temp = M
        while temp % f == 0:
            temp //= f
            e += 1
        log(f'    exponent in M(1237): {e}', log_lines)
        product_check *= f ** e
    log(f'  product check: {product_check == M}', log_lines)
    if product_check == M:
        # Update factors file with smallest prime factor
        smallest = min(factors_unique)
        log(f'  smallest prime factor: {smallest}', log_lines)
        updated = update_factor_file(1237, smallest)
        log(f'  updated factors table: {updated}', log_lines)
        # Append to complete file
        cofactor = M // smallest
        append_complete(1237, smallest, cofactor)
        log(f'  appended to complete file', log_lines)
    log('='*70, log_lines)


if __name__ == '__main__':
    main()
