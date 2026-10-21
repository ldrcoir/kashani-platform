#!/usr/bin/env python3
"""
Try Tonelli-Shanks for sqrt(2474) mod N (composite).
On composite N, TS may leak a factor during intermediate steps.
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

print(f"N = F2 (303 digits, prime: {is_prime(N)})")
print(f"N mod 4 = {int(N) % 4}, N mod 8 = {int(N) % 8}")

# v_2(N-1)
N_int = int(N)
Nm1 = N_int - 1
v2 = 0
temp = Nm1
while temp % 2 == 0:
    v2 += 1
    temp //= 2
Q_ts = Nm1 >> v2
print(f"v_2(N-1) = {v2}, Q = (N-1)/2^{v2} (odd part)")
print()

# Find a quadratic non-residue z
z = None
for zz in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]:
    j = jacobi(zz, N_int)
    if j == -1:
        z = zz
        break
    if j == 0:
        g = gcd(zz, N_int)
        if 1 < int(g) < N_int:
            print(f"FACTOR from Jacobi(zz,N): {g}")
            sys.exit(0)
print(f"Non-residue z = {z}")
print()

def check_factor(label, value):
    """Check if value gives a non-trivial factor of M(1237)."""
    g = gcd(abs(int(value)), N_int)
    if 1 < int(g) < N_int:
        if int(M) % int(g) == 0:
            print(f"  >>> {label}: REAL FACTOR! {g} ({len(str(g))} digits)")
            print(f"  is_prime: {is_prime(int(g))}")
            cof = N_int // int(g)
            print(f"  cofactor: {str(cof)[:60]}... ({len(str(cof))} digits)")
            print(f"  is_prime(cofactor): {is_prime(cof)}")
            return int(g)
        else:
            print(f"  {label}: gcd {g} not factor of M (spurious)")
    return None

# Try TS for several values where (a/N) = +1
# Specifically: a = 2, 2474 (both have (a/N) = +1)
for a_val in [2, 2474]:
    print(f"--- TS for a = {a_val}, (a/N) = {jacobi(a_val, N_int)} ---")
    
    a = a_val
    M_ts = v2
    c_ts = powmod(z, Q_ts, N)  # z^Q
    t_ts = powmod(a, Q_ts, N)  # a^Q
    R_ts = powmod(a, (Q_ts + 1) // 2, N)  # a^((Q+1)/2)
    
    print(f"  Initial: t = a^Q mod N (verify Jacobi: t = -1 mod N iff a is NQR? Actually t = (a/N) mod N ideally, but composite)")
    
    sqrt_a = None
    for iteration in range(200):
        if t_ts == 0:
            print(f"  iter {iteration}: t = 0, no sqrt")
            check_factor("t=0", t_ts)
            break
        if t_ts == 1:
            print(f"  iter {iteration}: t = 1, R is the sqrt")
            sqrt_a = int(R_ts)
            break
        # Find least i in [1, M_ts-1] with t^(2^i) = 1
        i_ts = None
        temp_t = t_ts
        for ii in range(1, M_ts + 1):
            temp_t = (temp_t * temp_t) % N
            if temp_t == 0:
                check_factor(f"t^(2^{ii})", temp_t)
                break
            if temp_t == 1:
                i_ts = ii
                break
        if i_ts is None:
            print(f"  iter {iteration}: didn't find i (M_ts={M_ts}), composite failure")
            # Try gcd of various intermediate values
            check_factor("R_ts-1", int(R_ts) - 1)
            check_factor("R_ts+1", int(R_ts) + 1)
            check_factor("c_ts-1", int(c_ts) - 1)
            check_factor("c_ts+1", int(c_ts) + 1)
            check_factor("t_ts-1", int(t_ts) - 1)
            check_factor("t_ts+1", int(t_ts) + 1)
            break
        
        # Compute b = c^(2^(M-i-1)) mod N
        b_ts = powmod(c_ts, 1 << (M_ts - i_ts - 1), N)
        # Update
        M_ts = i_ts
        c_ts = (b_ts * b_ts) % N
        t_ts = (t_ts * c_ts) % N
        R_ts = (R_ts * b_ts) % N
    
    if sqrt_a is not None:
        # Verify
        is_sqrt = powmod(sqrt_a, 2, N) == a
        print(f"  sqrt({a}) = {str(sqrt_a)[:50]}...")
        print(f"  Verify: sqrt^2 mod N == {a}? {is_sqrt}")
        if is_sqrt:
            # Also compute via simple method
            # For a = 2: sqrt(2) = 2^619 mod N
            if a == 2:
                simple = int(powmod(2, 619, N))
                print(f"  Simple sqrt(2) = 2^619 mod N = {str(simple)[:50]}...")
                print(f"  Same as TS? {sqrt_a == simple}")
                print(f"  Negation? {sqrt_a == N_int - simple}")
                if sqrt_a != simple and sqrt_a != N_int - simple:
                    g = gcd(abs(sqrt_a - simple), N_int)
                    if 1 < int(g) < N_int:
                        print(f"  >>> FACTOR from sqrt(2) mismatch: {g}")
                        if int(M) % int(g) == 0:
                            print(f"  >>> REAL FACTOR! {g}")
            elif a == 2474:
                # We have one sqrt: sqrt(2) * sqrt(1237)... but sqrt(1237) doesn't exist!
                # Wait, sqrt(2474) DOES exist. So TS gives us a value.
                # But we don't have an algebraic formula. Hmm.
                # Try: 2474 = 2*1237. If 2^k ≡ 1237 mod N for some k:
                # Then sqrt(2474) = sqrt(2 * 2^k) = sqrt(2^(k+1)) = 2^((k+1)/2) if k+1 even
                # We could compute 2^j for j = 0..p-1 and check 2^j == 1237 mod N
                print(f"  Searching for j with 2^j ≡ 1237 mod N (small p={P}):")
                # We can also check 2^j == 1237 mod each candidate factor.
                # Actually, let's just compute baby-step giant-step in the cyclic group <2> of order p.
                # <2> has order p. We need 2^j == 1237 mod N for some j ∈ [0, p-1].
                # BSGS: store 2^0, 2^1, ..., 2^(m-1) for m = ceil(sqrt(p))
                # Then for k = 0, 1, ..., m-1, check if 1237 * (2^(-m))^k is in the table.
                m_bsgs = int(gmpy2.isqrt(P)) + 1
                print(f"  BSGS m = {m_bsgs}")
                # Precompute table
                table = {}
                pow2 = 1
                for j in range(m_bsgs):
                    table[int(pow2)] = j
                    pow2 = (pow2 * 2) % N_int
                # giant step: 2^(-m) mod N
                inv_2m = int(invert(powmod(2, m_bsgs, N), N))
                gamma = 1237
                found_j = None
                for k in range(m_bsgs + 1):
                    if gamma in table:
                        found_j = k * m_bsgs + table[gamma]
                        # Reduce mod p
                        found_j = found_j % P
                        break
                    gamma = (gamma * inv_2m) % N_int
                if found_j is not None:
                    print(f"  >>> Found j = {found_j} with 2^j ≡ 1237 mod N")
                    # Verify
                    chk = int(powmod(2, found_j, N))
                    print(f"  Verify: 2^{found_j} mod N == 1237? {chk == 1237}")
                    # Now sqrt(2474) = sqrt(2 * 2^j) = 2^((j+1)/2) if j+1 is even
                    if (found_j + 1) % 2 == 0:
                        k = (found_j + 1) // 2
                        sqrt_2474_alg = int(powmod(2, k, N))
                        print(f"  Algebraic sqrt(2474) = 2^{k} mod N = {str(sqrt_2474_alg)[:50]}...")
                        print(f"  Verify: (sqrt)^2 mod N == 2474? {powmod(sqrt_2474_alg, 2, N) == 2474}")
                        print(f"  Same as TS? {sqrt_a == sqrt_2474_alg}")
                        print(f"  Negation? {sqrt_a == N_int - sqrt_2474_alg}")
                        if sqrt_a != sqrt_2474_alg and sqrt_a != N_int - sqrt_2474_alg:
                            g = gcd(abs(sqrt_a - sqrt_2474_alg), N_int)
                            if 1 < int(g) < N_int and int(M) % int(g) == 0:
                                print(f"  >>> REAL FACTOR! {g}")
                                sys.exit(0)
                    else:
                        print(f"  j+1 = {found_j+1} is odd, can't take sqrt as 2^((j+1)/2)")
                else:
                    print(f"  1237 NOT in <2> mod N (not a p-th root of unity)")
                    # This is actually interesting info
    print()

# Also try: compute sqrt(2474) algebraically via a different decomposition
# 2474 = 2 * 1237 = 2 * 1237
# But we don't have sqrt(1237) mod N. Hmm.
# What if we use 2474 = something else?
# 2474 = 2 * 1237. sqrt(2474) = sqrt(2)*sqrt(1237). But sqrt(1237) doesn't exist.
# 
# 2474 = 7^2 * 50 + 24? Hmm.
# 2474 = 2 * 1237. Let's see... 1237 = 34^2 + 9^2. So 1237 ≡ 1 mod 4. ✓
# 2474 = 2 * (34^2 + 9^2) = (34 + 9)^2 + (34 - 9)^2 = 43^2 + 25^2 = 1849 + 625 = 2474 ✓
# So 2474 = 43^2 + 25^2 = 2474. We have sum of two squares.
# 
# Sum of two squares factorization: (43 + 25i)(43 - 25i) in Gaussian integers
# In Z[i]/NZ[i]: 2474 = (43+25i)(43-25i)
# 
# In Z[i] mod N: we need a sqrt of -1 mod N. Then 2474 = (43 + 25*sqrt(-1))(43 - 25*sqrt(-1)).
# 
# If (-1/N) = +1, sqrt(-1) exists. Let's check:
print(f"(-1/N) = {jacobi(-1 % N_int, N_int)}")
# Wait, Jacobi(-1, N) for odd N: (-1/N) = (-1)^((N-1)/2) = +1 if N ≡ 1 mod 4, -1 if N ≡ 3 mod 4
print(f"N mod 4 = {N_int % 4}")
print(f"Expected (-1/N) = {1 if N_int % 4 == 1 else -1}")
print()

# N mod 4 = 1 → sqrt(-1) mod N exists (in principle).
# Compute sqrt(-1) mod N: i.e., x with x^2 ≡ -1 mod N.
# For prime p ≡ 1 mod 4: use TS or known formula.
# For composite N: similar TS approach, may leak factor.

print("Trying TS for a = -1 mod N (i.e., sqrt(-1)):")
a_neg1 = (-1) % N_int  # = N - 1
# (a/N) = (-1/N) should be +1
print(f"  (a/N) = {jacobi(a_neg1, N_int)}")

M_ts = v2
c_ts = powmod(z, Q_ts, N)
t_ts = powmod(a_neg1, Q_ts, N)
R_ts = powmod(a_neg1, (Q_ts + 1) // 2, N)

sqrt_neg1 = None
for iteration in range(200):
    if t_ts == 0:
        print(f"  iter {iteration}: t = 0")
        check_factor("t=0", t_ts)
        break
    if t_ts == 1:
        sqrt_neg1 = int(R_ts)
        print(f"  iter {iteration}: sqrt(-1) found")
        break
    i_ts = None
    temp_t = t_ts
    for ii in range(1, M_ts + 1):
        temp_t = (temp_t * temp_t) % N
        if temp_t == 0:
            check_factor(f"t^(2^{ii})", temp_t)
            break
        if temp_t == 1:
            i_ts = ii
            break
    if i_ts is None:
        print(f"  iter {iteration}: TS failed (composite)")
        check_factor("R_ts-1", int(R_ts) - 1)
        check_factor("R_ts+1", int(R_ts) + 1)
        check_factor("t_ts-1", int(t_ts) - 1)
        check_factor("t_ts+1", int(t_ts) + 1)
        break
    b_ts = powmod(c_ts, 1 << (M_ts - i_ts - 1), N)
    M_ts = i_ts
    c_ts = (b_ts * b_ts) % N
    t_ts = (t_ts * c_ts) % N
    R_ts = (R_ts * b_ts) % N

if sqrt_neg1 is not None:
    print(f"  sqrt(-1) = {str(sqrt_neg1)[:50]}...")
    print(f"  Verify: sqrt(-1)^2 mod N == -1? {powmod(sqrt_neg1, 2, N) == a_neg1}")
    if powmod(sqrt_neg1, 2, N) == a_neg1:
        # Now use: 2474 = 43^2 + 25^2 = (43 + 25*sqrt(-1))(43 - 25*sqrt(-1)) mod N
        sqrt_2474_gauss1 = (43 + 25 * sqrt_neg1) % N_int
        sqrt_2474_gauss2 = (43 - 25 * sqrt_neg1) % N_int
        # Actually these are Gaussian "integers" whose product is 2474, not sqrt of 2474!
        # Hmm. (43+25i)(43-25i) = 2474 in Z[i].
        # In Z[i]/NZ[i], this gives 2474 ≡ 0... wait no, 2474 ≠ 0 mod N (since N is huge).
        # I'm confused. Let me think again.
        # 
        # 2474 = 43^2 + 25^2. So 2474 ≡ 43^2 + 25^2 mod N. 
        # If we have a "sqrt(-1)" mod N (call it i), then 2474 ≡ (43 + 25i)(43 - 25i) mod N.
        # This is a factorization of 2474 mod N into two "Gaussian" factors.
        # 
        # But we want sqrt(2474), not factorization of 2474.
        # 
        # Actually, the relation (43+25i)(43-25i) = 2474 in Z[i] means that 43+25i is a "divisor" of 2474 in Z[i].
        # In Z[i]/(N), 43+25i is a unit-times-divisor of 2474.
        # 
        # Hmm, this isn't directly useful for sqrt(2474).
        # 
        # What IS useful: if N = q1*q2, then in Z[i]/(N) ≅ Z[i]/(q1) × Z[i]/(q2).
        # If 2474 splits differently in Z[i]/(q1) vs Z[i]/(q2), gcd gives factor.
        # 
        # 2474 = 2 * 1237. In Z[i]: 2 = -i*(1+i)^2 (since 2 = (1+i)(1-i) and (1-i) = -i*(1+i)).
        # 1237 ≡ 1 mod 4, so 1237 splits in Z[i]: 1237 = (34+9i)(34-9i).
        # So 2474 = 2 * 1237 = (-i)*(1+i)^2 * (34+9i)(34-9i) in Z[i].
        # 
        # In Z[i]/(q): 2474 mod q = the norm N(43+25i) = 43^2+25^2 = 2474, but 43+25i is NOT 
        # the same as 2474 — it's a Gaussian "factor" of 2474.
        # 
        # Hmm this is getting complex. Let me just try another approach.
        pass
print()

print("=" * 70)
print("If no factor found, need to try ECM or other advanced methods.")
print("=" * 70)
