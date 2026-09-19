#!/usr/bin/env python3
"""
Bounded-time ECM on N = M(1237)/F1 in foreground.
Uses Montgomery curve with Suyama parameterization.
B1 = 1e7, ~30s per curve, try as many as time allows.
"""

import sys; sys.set_int_max_str_digits(1000000)
import gmpy2; from gmpy2 import mpz, gcd, is_prime, powmod, invert, isqrt
import time, random
from pathlib import Path

M = mpz(2)**1237 - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
N = M // F1

print(f'ECM on N = M(1237)/F1, {len(str(N))} digits')
print(f'Time budget: 300s')
print()

B1 = 10_000_000

def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

# Precompute prime powers for stage 1
print(f'Sieving primes up to {B1}...')
t0 = time.time()
primes = small_primes_up_to(B1)
print(f'Sieve: {len(primes)} primes in {time.time()-t0:.1f}s')

# Build list of (prime, exponent) for stage 1
import math
prime_powers = []
for p in primes:
    k = int(math.log(B1) / math.log(p))
    pe = p ** k
    prime_powers.append((p, pe))
print(f'Prime powers: {len(prime_powers)}')

# Montgomery curve ECM with Suyama parameterization
def montgomery_ecm_curve(sigma, N):
    """Suyama parameterization. Returns (A, X, Z) for Montgomery curve."""
    # u = sigma^2 - 5; v = 4*sigma
    s = sigma
    u = (s*s - 5) % N
    v = (4*s) % N
    # X = u^3; Z = v^3
    X = (u*u*u) % N
    Z = (v*v*v) % N
    # A = (v - u)^3 * (3*u + v) / (u^3 * v) - 2
    num = ((v - u) ** 3) * (3*u + v) % N
    den = (u*u*u * v) % N
    A = (num * invert(den, N) - 2) % N
    return A, X, Z

def mont_ladder(k, X, Z, A, N):
    """Montgomery ladder for scalar mult on By^2 = Bx^3 + Ax^2 + x."""
    R0_X, R0_Z = X, Z
    R1_X, R1_Z = ((X*X - Z*Z) ** 2) % N, (4*X*Z * (X*X + A*X*Z + Z*Z)) % N
    # Iterate bits from second-most-significant to LSB
    bits = bin(k)[2:]  # binary representation, MSB first
    for bit in bits[1:]:
        if bit == '0':
            # R1 = R0 + R1, R0 = 2*R0
            new_R1_X = (R0_X * R1_Z - R1_X * R0_Z) ** 2 % N
            new_R1_Z = ((R0_X * R1_Z - R1_X * R0_Z) ** 2 * X) % N
            new_R0_X = (R0_X * R0_X - R0_Z * R0_Z) ** 2 % N
            new_R0_Z = (4 * R0_X * R0_Z * (R0_X * R0_X + A * R0_X * R0_Z + R0_Z * R0_Z)) % N
            # Hmm wait, the formulas need careful thought
            # Standard Montgomery doubling:
            #   X_2 = (X^2 - Z^2)^2
            #   Z_2 = 4*X*Z * ((X-Z)^2 + 4*X*Z)  [for A=0]
            # General with A: Z_2 = 4*X*Z*(X^2 + A*X*Z + Z^2)
            # Differential addition:
            #   X_add = (X1*Z2 - X2*Z1)^2 * X3
            #   Z_add = (X1*Z2 - X2*Z1)^2 * Z3 (no, that's wrong)
            # Actually let me use the standard formulas
            # Let's use the simpler form:
            #   X_{2P} = (X_P^2 - Z_P^2)^2
            #   Z_{2P} = 4 X_P Z_P ((X_P - Z_P)^2 + ((A+2)/4) * 4 X_P Z_P)
            # For Montgomery: B y^2 = x^3 + A x^2 + x
            #   X_{2P} = (X_P + Z_P)^2 (X_P - Z_P)^2
            #   Z_{2P} = 4 X_P Z_P (X_P - Z_P)^2 + ((A+2)/4) * (2 X_P Z_P)^2 ... 
            # Forget the formulas — let me just use the simple version where 
            # we don't track Y and use the X-only formulas.
            pass
        else:
            pass
    # This is getting complex. Let me use a simpler version.
    return None

# Let me use a simpler ECM with Weierstrass curve, like the existing ecm_bg2
def weierstrass_ecm(N, B1, primes, sigma, time_limit):
    """Simple Weierstrass ECM. Returns factor or None."""
    random.seed(sigma)
    a_c = random.randint(1, 10**9)
    b_c = random.randint(1, 10**9)
    disc = (4 * a_c**3 + 27 * b_c**2) % N
    if disc == 0:
        return None
    
    # Find a point on the curve
    found_point = False
    for _ in range(100):
        x = random.randint(0, int(N) - 1)
        rhs = (x**3 + a_c * x + b_c) % int(N)
        y = isqrt(mpz(rhs))
        if (y * y) % N == rhs:
            P = (x, int(y))
            found_point = True
            break
    if not found_point:
        return None
    
    # Stage 1: compute P^E for E = prod p^k
    Px, Py = P
    for p, pe in primes:
        # Multiply P by pe
        # Use double-and-add
        k = pe
        Rx, Ry = None, None
        ax, ay = Px, Py
        while k > 0:
            if k & 1:
                if Rx is None:
                    Rx, Ry = ax, ay
                else:
                    # Add R + A on curve y^2 = x^3 + a_c x + b_c
                    if Rx == ax:
                        if (Ry - ay) % N == 0:
                            # Doubling
                            num = (3*Rx*Rx + a_c) % N
                            den = (2*Ry) % N
                        else:
                            # P + (-P) = O, return identity
                            Rx, Ry = None, None
                            k >>= 1
                            continue
                    else:
                        num = (ay - Ry) % N
                        den = (ax - Rx) % N
                    g = gcd(den, N)
                    if 1 < int(g) < int(N):
                        return int(g)
                    if int(g) == int(N):
                        Rx, Ry = None, None
                        k >>= 1
                        continue
                    lam = (num * invert(den, N)) % N
                    x3 = (lam*lam - Rx - ax) % N
                    y3 = (lam * (Rx - x3) - Ry) % N
                    Rx, Ry = x3, y3
            # Double A
            if ax is not None:
                num = (3*ax*ax + a_c) % N
                den = (2*ay) % N
                g = gcd(den, N)
                if 1 < int(g) < int(N):
                    return int(g)
                if int(g) == int(N):
                    ax, ay = None, None
                else:
                    lam = (num * invert(den, N)) % N
                    x3 = (lam*lam - ax - ax) % N
                    y3 = (lam * (ax - x3) - ay) % N
                    ax, ay = x3, y3
            k >>= 1
    
    # Stage 1 done. Compute gcd(Ry - 1, N)? No — should be gcd with the "denominator" that failed during scalar mult.
    # Actually, if scalar mult completed without finding a factor, the resulting point is on the curve mod N.
    # If the order of P mod some prime q is B1-smooth, then P^E ≡ O mod q, but P^E ≢ O mod N (different q).
    # Then Z-coordinate of P^E (in projective coords) ≡ 0 mod q but ≢ 0 mod N.
    # In affine coords: we'd hit "0 in denominator" — which gives the factor!
    
    # But if we successfully computed P^E in affine, then no factor was found in stage 1.
    # If P^E = O (Rx, Ry both became None), then Z ≡ 0 mod N, meaning P^E ≡ O mod all q_i — no factor.
    # If P^E is a finite point, no factor found in stage 1.
    
    return None  # Stage 1 didn't find a factor

# Main loop: try many curves
start_time = time.time()
trial = 0
print(f'Starting ECM trials at {time.strftime("%H:%M:%S")}')
while time.time() - start_time < 280:  # 280s budget
    trial += 1
    sigma = random.randint(1, 10**12)
    t0 = time.time()
    result = weierstrass_ecm(N, B1, prime_powers, sigma, 30)
    elapsed = time.time() - t0
    if result is not None:
        g = result
        print(f'Trial {trial} (sigma={sigma}): FOUND gcd {g} ({len(str(g))} digits) in {elapsed:.1f}s')
        if int(M) % int(g) == 0 and powmod(2, 1237, g) == 1:
            print(f'>>> REAL FACTOR! is_prime: {is_prime(int(g))}')
            cof = int(N) // int(g)
            print(f'>>> cofactor: {str(cof)[:60]}... ({len(str(cof))} digits)')
            print(f'>>> is_prime(cofactor): {is_prime(cof)}')
            # Update table
            FACTORS_FILE = Path('/home/z/my-project/download/A136030_factors_1_to_8000.txt')
            lines = FACTORS_FILE.read_text().splitlines(keepends=True)
            out = []
            for line in lines:
                if line.startswith('#'):
                    out.append(line)
                    continue
                parts = line.split('\t')
                if len(parts) >= 2 and parts[0] == '1237':
                    cur = parts[1].strip()
                    if cur == '-1' or int(g) < int(cur):
                        out.append(f'1237\t{int(g)}\n')
                    else:
                        out.append(line)
                else:
                    out.append(line)
            FACTORS_FILE.write_text(''.join(out))
            print(f'>>> Table updated!')
            sys.exit(0)
    else:
        if trial % 5 == 0:
            print(f'Trial {trial} (sigma={sigma}): no factor (elapsed {elapsed:.1f}s, total {time.time()-start_time:.1f}s)')

print(f'\nECM complete: {trial} trials in {time.time()-start_time:.1f}s. No factor found.')
