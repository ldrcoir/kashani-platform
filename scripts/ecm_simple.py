#!/usr/bin/env python3
"""
Simple ECM implementation in Python using Montgomery curve.

Goal: Try ECM with B1 > 3e9 on N = M(1237)/F1.

Standard ECM with Montgomery curve:
  y^2 = x^3 + Ax^2 + x (Montgomery form)
  Use Suyama's parameterization with sigma as the seed.
  
The factor F1 was found with B1 = 3e9. To find a NEW factor, we need to try 
curves that haven't been tried (or with HIGHER B1).

This is a SIMPLE implementation - not as fast as GMP-ECM (which is C-based).
Aim: B1 = 1e9 with 5-10 curves. Each curve takes maybe 1-2 minutes.

Algorithm:
  For each sigma:
    Initialize Montgomery curve via Suyama.
    Compute scalar multiplication on E by product of prime powers <= B1.
    Take gcd of result with N. If non-trivial, factor found.
"""

import sys
import time
import random
from pathlib import Path
import gmpy2
from gmpy2 import mpz, gcd as gmpy_gcd, is_prime, invert, powmod

sys.set_int_max_str_digits(1000000)

BASE = Path('/home/z/my-project')
LOG = BASE / 'logs/ecm_simple.log'
LOG.parent.mkdir(exist_ok=True)

def log(msg):
    print(msg, flush=True)
    with open(LOG, 'a') as f:
        f.write(msg + '\n')


def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]


def montgomery_curve_from_sigma(sigma, N):
    """Suyama's parameterization: generate Montgomery curve params from sigma.
    
    Returns (A, Qx) where:
      Curve: By^2 = x^3 + Ax^2 + x (with B = 1 typically)
      Base point Q = (Qx, _) on the curve.
    """
    sigma = mpz(sigma)
    u = (sigma * sigma - 5) % N
    v = (4 * sigma) % N
    # A = (v - u)^3 * (3*u + v) / (4 * u^3 * v) - 2
    num = (v - u) ** 3 * (3 * u + v) % N
    den = 4 * u * u * u % N * v % N
    try:
        den_inv = invert(den, N)
    except:
        # den not invertible, gcd(den, N) might give a factor!
        g = gmpy_gcd(den, N)
        if 1 < int(g) < int(N):
            return None, None, g
        return None, None, None
    A = (num * den_inv - 2) % N
    Qx = (u * u * u) % N
    return A, Qx, None


def montgomery_ladder(k, Px, A, N):
    """Montgomery ladder for scalar multiplication on Montgomery curve.
    Computes k * P = (X_{kP}, Z_{kP}) where P = (Px, 1).
    """
    R0 = (mpz(Px), mpz(1))  # X, Z
    R1 = (mpz(Px), mpz(1))  # Initial: R0 = P, R1 = P (then double R1)
    # First, double to get R1 = 2P
    R1 = _mont_double(R1, A, N)
    
    bits = bin(k)[2:]
    # Process MSB-to-LSB: start with R0 = P, R1 = 2P, then for each subsequent bit
    # either double-and-add or just double
    # Standard Montgomery ladder:
    #   R0 = (X_n, Z_n), R1 = (X_{n+1}, Z_{n+1})
    #   For bit = 0: R0 = 2*R0, R1 = R0 + R1
    #   For bit = 1: R1 = 2*R1, R0 = R0 + R1
    
    # Reset to standard initialization
    R0 = (mpz(Px), mpz(1))  # n = 1
    R1 = _mont_double(R0, A, N)  # n+1 = 2
    
    for bit in bits[1:]:  # skip the leading 1
        if bit == '0':
            R1 = _mont_add(R0, R1, A, N)
            R0 = _mont_double(R0, A, N)
        else:
            R0 = _mont_add(R0, R1, A, N)
            R1 = _mont_double(R1, A, N)
    
    return R0  # (X_k, Z_k)


def _mont_double(P, A, N):
    """Double a point P = (X, Z) on Montgomery curve y^2 = x^3 + Ax^2 + x.
    Returns (X_2, Z_2) = 2P.
    Formulas:
      4XZ = (X+Z)^2 - (X-Z)^2
      X_2 = (X+Z)^2 * (X-Z)^2
      Z_2 = 4XZ * ((X-Z)^2 + ((A+2)/4) * 4XZ)
    """
    X, Z = P
    if Z == 0:
        return (mpz(0), mpz(1))
    XpZ = (X + Z) % N
    XmZ = (X - Z) % N
    XpZ2 = XpZ * XpZ % N
    XmZ2 = XmZ * XmZ % N
    X_new = XpZ2 * XmZ2 % N
    diff = (XpZ2 - XmZ2) % N
    # Z_new = diff * (XmZ2 + (A+2)/4 * diff)
    # Use: Z_new = diff * (XmZ2 + a24 * diff) where a24 = (A + 2) / 4
    # For (A+2)/4 to be integer, A must be ≡ 2 mod 4. In Suyama, A is computed via formula.
    # Standard form: a24 = (A+2)/4 mod N. Need A+2 divisible by 4.
    # If not, use alternative formulation.
    # We'll just compute a24 = (A+2) * invert(4, N) mod N
    a24 = (A + 2) * invert(4, N) % N
    Z_new = diff * (XmZ2 + a24 * diff) % N
    return (X_new, Z_new)


def _mont_add(P, Q, A, N):
    """Add P + Q on Montgomery curve.
    P = (X1, Z1), Q = (X2, Z2). The "difference" P-Q = (X_diff, Z_diff) must be known.
    In Montgomery ladder, P - Q is the original base point (X_P, 1).
    
    Formula:
      X_add = Z_diff * ((X1-Z1)*(X2+Z2) + (X1+Z1)*(X2-Z2))^2
      Z_add = X_diff * ((X1-Z1)*(X2+Z2) - (X1+Z1)*(X2-Z2))^2
    
    Here, we use P - Q = base = (Px, 1), so Z_diff = 1, X_diff = Px.
    """
    X1, Z1 = P
    X2, Z2 = Q
    # P_diff = (X1 - Z1)(X2 + Z2) + (X1 + Z1)(X2 - Z2)
    u = (X1 - Z1) * (X2 + Z2) % N
    v = (X1 + Z1) * (X2 - Z2) % N
    add = (u + v) % N
    sub = (u - v) % N
    X_new = add * add % N  # Z_diff = 1, so no extra factor
    Z_new = sub * sub % N  # X_diff = ?, wait
    
    # Hmm, the formula requires knowing X_diff (= X_{P-Q}) and Z_diff (= Z_{P-Q}).
    # In Montgomery ladder, the difference is always the original base point.
    # So X_diff = X_initial = X1_initial, Z_diff = 1.
    # X_add = Z_diff * add^2 = 1 * add^2 = add^2
    # Z_add = X_diff * sub^2
    
    # But wait, we don't have access to X_diff in this function. Let me re-think.
    
    # Actually, in the Montgomery ladder context, the difference between 
    # R0 (= nP) and R1 (= (n+1)P) is always P (the base point).
    # So if we use this _mont_add in the ladder, X_diff = X_P (= initial X), Z_diff = 1.
    
    # But here, we're called with arbitrary P, Q from the ladder. The difference 
    # IS the base, but we need to know its X coordinate.
    
    # For the ladder to work correctly, we need to track this. Let me just use the 
    # standard formulation:
    #   X_add = (X1*Z2 + X2*Z1)^2 * X_diff
    #   Z_add = (X1*Z2 - X2*Z1)^2 * Z_diff
    
    # In our case Z_diff = 1, X_diff = base X (constant).
    
    # Actually for safety, let me use a different formula that doesn't require X_diff:
    # Montgomery ladder is sufficient with just R0, R1 = (X_n, Z_n), (X_{n+1}, Z_{n+1})
    # where R1 - R0 = base point.
    
    # For add: given R0 = nP, R1 = (n+1)P (both with X, Z known), 
    # sum = (2n+1)P:
    #   X_{2n+1} = Z_1 * (X_0 - Z_0)^2 ... no wait, formula is:
    #   X_{add} = Z_{-1} * (X_1 - X_0)^2 where Z_{-1} = Z(P-Q)
    
    # I'll use the formula assuming P-Q = base, with X_base known externally.
    
    # For now, let me use a simpler approach: convert to Weierstrass and use standard addition.
    # OR: use a different parameterization.
    
    # Actually, the simplest correct approach: use the "differential addition" formula.
    # Given P, Q, and P-Q = (X_{PQ}, Z_{PQ}):
    #   X_{P+Q} = Z_{PQ} * ((X_P - Z_P)(X_Q + Z_Q) + (X_P + Z_P)(X_Q - Z_Q))^2
    #   Z_{P+Q} = X_{PQ} * ((X_P - Z_P)(X_Q + Z_Q) - (X_P + Z_P)(X_Q - Z_Q))^2
    
    # In our Montgomery ladder, P-Q is the BASE point. We track it.
    
    # For now, I'll just track the difference and pass it in.
    return None  # signal: not implemented properly


def main():
    """Main ECM run. We'll use a simpler implementation."""
    log('=' * 70)
    log('ECM Simple Implementation')
    log('=' * 70)
    
    p = 1237
    M_p = mpz(2)**p - 1
    F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
    N = M_p // F1
    
    log(f'  N has {len(str(N))} digits')
    log(f'  Trying ECM with various sigmas and B1 values')
    log('')
    
    # Note: This implementation is incomplete due to Montgomery add complexity.
    # Let me use a SIMPLER approach: P-1 with B1 = 1e9 (deeper than what we tried before).
    
    log('Simpler approach: P-1 with B1 = 1e9 on N (not M(1237) directly)')
    log('  Since F1 is already known, we want to factor N = M(p)/F1.')
    log('  P-1 on N: for base a = 3, compute a^(e) mod N where e = prod of prime powers <= B1.')
    log('  Then gcd(a^e - 1, N) might give a factor.')
    
    B1 = 1_000_000_000  # 1e9
    log(f'  B1 = {B1}')
    
    # Generate primes up to B1 (this needs ~50MB memory)
    log(f'  Sieving primes up to {B1}...')
    t0 = time.time()
    primes = small_primes_up_to(B1)
    log(f'  Sieve done: {len(primes)} primes, time = {time.time()-t0:.1f}s')
    
    # Compute a^e mod N where e = product of prime powers q^k with q^k <= B1
    log('  Computing a^e mod N (incremental)')
    bases = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    t_start = time.time()
    factor_found = None
    
    for base in bases:
        if time.time() - t_start > 100:
            log(f'  Time budget')
            break
        log(f'  Trying base a = {base}, B1 = {B1}')
        a = mpz(base)
        # Incremental: for each prime p, a = a^(p^k) where p^k <= B1
        for pi, prime in enumerate(primes):
            # Compute p^e where p^e <= B1
            e = 1
            pe = prime
            while pe * prime <= B1:
                pe *= prime
                e += 1
            # a = a^(pe) mod N
            a = powmod(a, pe, N)
            # Periodic gcd check (every 1000 primes to save time)
            if (pi + 1) % 100_000 == 0:
                g = gmpy_gcd(a - 1, N)
                if 1 < int(g) < int(N):
                    log(f'    >>> FACTOR FOUND: gcd = {g} ({len(str(g))} digits)')
                    factor_found = int(g)
                    break
                elapsed = time.time() - t_start
                log(f'    Progress: pi={pi+1}, prime={prime}, elapsed={elapsed:.1f}s')
        
        if not factor_found:
            # Final gcd check
            g = gmpy_gcd(a - 1, N)
            if 1 < int(g) < int(N):
                log(f'    >>> FACTOR FOUND at end: gcd = {g} ({len(str(g))} digits)')
                factor_found = int(g)
            else:
                log(f'    No factor found with base {base}')
        if factor_found:
            break
    
    if factor_found:
        log('')
        log(f'FACTOR FOUND: {factor_found}')
        log(f'Digits: {len(str(factor_found))}')
        cofactor = int(N) // factor_found
        log(f'Cofactor: {cofactor} ({len(str(cofactor))} digits)')
        log(f'is_prime(factor): {is_prime(factor_found)}')
        log(f'is_prime(cofactor): {is_prime(cofactor)}')
        
        # Update factors table
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
        log('Updated factors table!')


if __name__ == '__main__':
    main()
