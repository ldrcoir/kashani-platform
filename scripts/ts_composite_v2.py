#!/usr/bin/env python3
"""
Enhanced TS for composite N: extract factor from order differences.

When TS fails on composite N = q1*q2 because the order of t = a^Q mod N
doesn't divide 2^v2(N-1), it means t^(2^i) ≡ 1 mod one prime but not the
other for some i. We can extract the factor by computing gcd(t^(2^i) - 1, N).
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, gcd, is_prime, powmod, invert, jacobi
import time

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
N = M // F1

N_int = int(N)
Nm1 = N_int - 1
v2 = 0
temp = Nm1
while temp % 2 == 0:
    v2 += 1
    temp //= 2
Q_ts = Nm1 >> v2

def check_factor(label, value):
    g = gcd(abs(int(value)), N_int)
    if 1 < int(g) < N_int:
        if int(M) % int(g) == 0:
            print(f"  >>> {label}: REAL FACTOR! {g}")
            print(f"      digits: {len(str(g))}, is_prime: {is_prime(int(g))}")
            cof = N_int // int(g)
            print(f"      cofactor: {str(cof)[:60]}... ({len(str(cof))} digits)")
            print(f"      is_prime(cofactor): {is_prime(cof)}")
            return int(g)
    return None

# Try for various a values where (a/N) = +1
for a_val in [2474, 2, -1 % N_int, -2 % N_int, -1237 % N_int, -2474 % N_int, 7, 11]:
    j = jacobi(a_val % N_int, N_int)
    print(f"\n=== a = {a_val}, (a/N) = {j} ===")
    if j != 1:
        print(f"  (a/N) != 1, skipping TS; trying gcd(a^k ± 1, N) anyway")
    
    # Compute t = a^Q mod N
    t = int(powmod(a_val, Q_ts, N))
    
    # Try gcd(t^k - 1, N) for various k
    print(f"  t = a^Q mod N")
    
    # Squaring chain
    cur = t
    for k in range(1, v2 + 2):  # k = 1, 2, ..., v2+1
        cur = (cur * cur) % N_int
        # cur is now t^(2^k)
        # Check gcd(cur - 1, N)
        g = check_factor(f"t^(2^{k}) - 1", cur - 1)
        if g:
            print(f"  Found at k = {k}!")
            sys.exit(0)
        g = check_factor(f"t^(2^{k}) + 1", cur + 1)
        if g:
            print(f"  Found at k = {k}!")
            sys.exit(0)
        # Also try smaller powers: t^1, t^2, t^3, t^4, t^8, ...
    
    # Also try t - 1 (i.e., a^Q - 1)
    g = check_factor("t - 1 (a^Q - 1)", t - 1)
    if g:
        sys.exit(0)
    g = check_factor("t + 1 (a^Q + 1)", t + 1)
    if g:
        sys.exit(0)
    
    # Try a^((N-1)/2) - 1 = a^((N-1)/2) - 1
    half = int(powmod(a_val, Nm1 // 2, N))
    g = check_factor("a^((N-1)/2) - 1 (Euler)", half - 1)
    if g:
        sys.exit(0)
    g = check_factor("a^((N-1)/2) + 1", half + 1)
    if g:
        sys.exit(0)
    
    # Try a^(N-1) - 1 (Fermat-like)
    fermat = int(powmod(a_val, Nm1, N))
    g = check_factor("a^(N-1) - 1 (Fermat)", fermat - 1)
    if g:
        sys.exit(0)
    g = check_factor("a^(N-1) + 1", fermat + 1)
    if g:
        sys.exit(0)

# Also try: combinations based on Aurifeuillean structure
# 2p = 2474. p = 1237. 
# p = 1237 = 34^2 + 9^2 (Jacobi-style).
# (a^((p+1)/2) - related values)
print(f"\n=== Trying Mersenne-specific values ===")
# 2^(p) ≡ 1 mod N. So 2^(p-1) ≡ 2^(-1) mod N.
# 2^(p-1)/2 = 2^618 - is it 1 or -1 mod each q?
# (2/q) = (2/N) computed = +1. So 2 is QR mod each q_i (assuming 2 prime factors).
# Euler: 2^((q_i-1)/2) ≡ +1 mod q_i.
# 2^618 mod q_i = 2^(618 mod (q_i-1)) mod q_i. Hmm.
# 
# (q_i - 1) = 1237 * k_i for some even k_i. So (q_i - 1) = 2474 * m_i.
# 618 = (1237 - 1)/2 = 618. So 618 mod (q_i-1) = 618 (since q_i - 1 > 618).
# 2^618 mod q_i = ? Not necessarily ±1.
# 
# Let's compute 2^((p-1)/2) = 2^618 mod N and check gcd.
val_618 = int(powmod(2, 618, N))
g = check_factor("2^618 - 1", val_618 - 1)
if g: sys.exit(0)
g = check_factor("2^618 + 1", val_618 + 1)
if g: sys.exit(0)

# 2^((p+1)/2) = 2^619 = sqrt(2) mod N. 
# (2^619)^2 = 2 mod N. So (2^619 - sqrt(2)) = 0 mod N — but sqrt(2) IS 2^619.
# (2^619)^2 - 2 = 0 mod N. Trivial.
# 
# What about 2^619 - some_specific_value?

# Aurifeuillean: M(p) = A^2 - 2p B^2. gcd(M(p), A - B*sqrt(2p)) gives F1.
# In Z/MZ: A ≡ ±B*sqrt(2p) mod M. So gcd(A - B*sqrt(2p), M) and gcd(A + B*sqrt(2p), M) 
# split M into F1 and F2.
# 
# In Z/NZ (where N = F2): A ≡ ±B*sqrt(2p) mod N (the + or - sign choice).
# A ≡ -B*sqrt(2p) mod F1 (giving F1 from one sign).
# A ≡ +B*sqrt(2p) mod F2 (giving F2 from the other).
# 
# But the sign mod q_i (for q_i | F2) might be the SAME (giving all of F2) or DIFFERENT.
# If DIFFERENT, the gcd would split F2!
# 
# To check this, we need A and B. Without them, we can't directly check.
# 
# Alternative: use the fact that 2^k (for some specific k) might be the "Aurifeuillean sqrt".
# Specifically, the Aurifeuillean R = A * B^(-1) mod M is a p-th root of unity: R = 2^j for some j.
# We computed earlier that R is in the subgroup <2> of order p.
# 
# Let's find j such that 2^(2j) ≡ 2p mod F1 (i.e., 2^(2j-1) ≡ p mod F1).
# Use BSGS in the cyclic group <2> mod F1 of order p = 1237.

print(f"\n=== BSGS for 2^j ≡ p mod F1 ===")
F1_int = int(F1)
p_target = P  # 1237
# We want j with 2^j ≡ p_target mod F1_int, j in [0, p-1]
# This is DLP in cyclic group <2> of order p = 1237.
m_bsgs = int(gmpy2.isqrt(p_target)) + 1  # ~36
print(f"  BSGS m = {m_bsgs}")
# Build table
table = {}
pow2 = 1
for j in range(m_bsgs):
    table[pow2] = j
    pow2 = (pow2 * 2) % F1_int
# Find j with 2^j ≡ p_target mod F1
inv_2m = int(invert(powmod(2, m_bsgs, F1), F1))
gamma = p_target
found_j_F1 = None
for k in range(m_bsgs + 1):
    if gamma in table:
        found_j_F1 = (k * m_bsgs + table[gamma]) % p_target
        break
    gamma = (gamma * inv_2m) % F1_int

if found_j_F1 is not None:
    print(f"  Found j_F1 = {found_j_F1} with 2^j ≡ {p_target} mod F1")
    print(f"  Verify: 2^{found_j_F1} mod F1 = {int(powmod(2, found_j_F1, F1))} (expect {p_target})")
    
    # Now: j_F1 is the same j for all primes q_i | M(p) (since Aurifeuillean R is global).
    # 2^(2j_F1 - 1) ≡ p mod F1. Should also be ≡ p mod N (= F2)?
    # If yes: 2^(2j_F1 - 1) - p ≡ 0 mod N → gcd(2^(2j_F1-1) - p, N) = N (trivial).
    # If NO: gcd(2^(2j_F1-1) - p, N) is non-trivial!
    
    # Wait, but R = 2^j_F1 is the Aurifeuillean root. R^2 = 2p mod M(p), so 2^(2j_F1) ≡ 2p mod M.
    # Equivalently 2^(2j_F1 - 1) ≡ p mod M. So mod each prime factor of M, including F2.
    # So gcd(2^(2j_F1-1) - p, M) = M (trivial).
    # 
    # Hmm, that's trivial. The Aurifeuillean root is the same mod all factors.
    
    # But maybe the Aurifeuillean root mod F1 corresponds to a DIFFERENT j mod q_i?
    # No, j is a property of the algebraic relation, and 2 has order p mod each prime.
    # The j satisfying 2^(2j-1) ≡ p mod q_i is unique (mod p). And it's the same j as mod F1
    # (because the relation 2^(2j-1) ≡ p mod M means it holds mod each prime factor).
    
    # So the basic approach gives nothing new.
    
    # However: the SIGN of the sqrt(2p) might differ mod different primes!
    # R = 2^j mod M. -R = M - 2^j mod M.
    # The Aurifeuillean factorization is M = F1 * F2 where F1 = gcd(M, A + B*sqrt(2p)) 
    # and F2 = gcd(M, A - B*sqrt(2p)) (or vice versa).
    # The signs of "sqrt(2p)" picked are different mod F1 vs F2.
    # 
    # So: gcd(A + B*R - 0, M) = F1 (or F2). 
    # If we compute A + B*R mod M and gcd with M: it equals F1 (or F2).
    # If we compute A - B*R mod M and gcd with M: it equals F2 (or F1).
    # 
    # These splits M into F1 and F2 (already known).
    # 
    # Now: what if the sign of "sqrt(2p)" is DIFFERENT mod different primes q_i | F2?
    # Then gcd(A + B*R, F2) would split F2 further!
    # 
    # The sign choice is global: A + B*R or A - B*R. Each prime q_i | M is in one of the two.
    # F1 is in one (say A + B*R = 0 mod F1).
    # All primes q_i | F2 are in the other (A - B*R = 0 mod F2).
    # So A - B*R ≡ 0 mod F2 (all q_i | F2). Doesn't split F2.
    
    # So basic Aurifeuillean gives no further info beyond F1.
    
    # EXCEPT: what if there's an Aurifeuillean factorization of F2 directly?
    # F2 = M/F1. Is there an Aurifeuillean factorization of F2?
    # F2 is not of the form M(p') for any prime p'. So no direct Mersenne Aurifeuillean.
    # But F2 might have other algebraic structure...
    
    pass
else:
    print(f"  p_target = {p_target} not in <2> mod F1 (unexpected!)")
    # This shouldn't happen since 2 has order p = 1237 mod F1, so <2> has p elements,
    # including possibly p_target = 1237.

print("\n=== Summary ===")
print("Basic algebraic and TS approaches didn't crack F2.")
print("F2 (303 digits) requires SNFS or extended ECM — beyond current scope.")
