#!/usr/bin/env python3
"""
DEEP INVESTIGATION: val^2 is NOT in <2>!

This means (Z/NZ)* has MULTIPLE distinct cyclic subgroups of order 1237.
This is a real structural fact we can use!

Reasoning:
- val = a^((N-1)/2474) for a with (a/N) = -1.
- val has order 2474 in (Z/NZ)* (we verified val^2474 = 1 and val^1237 ≡ -1).
- val^2 has order 1237.
- val^2 is in some cyclic subgroup of order 1237.
- We checked: val^2 is NOT in <2> (BSGS found j = None).

This means: val^2 is in a DIFFERENT subgroup of order 1237.

Now: by CRT, val^2 mod qi for each qi | N is in <2 mod qi> (since (Z/qi Z)* is cyclic 
of order qi-1 = 2474*m_i, and <2 mod qi> is the unique subgroup of order 1237).
Wait, that's a CONTRADICTION! 

In a CYCLIC group, there's only ONE subgroup of any given order. So if (Z/qi Z)* is cyclic 
of order qi-1 = 2474*m_i, then it has a UNIQUE subgroup of order 1237, which is <2 mod qi>.

So val^2 mod qi IS in <2 mod qi> for each qi.
Therefore val^2 mod N is in the image of <2> under CRT, which is <2 mod N>.

So val^2 ∈ <2 mod N>. But BSGS found j = None, meaning val^2 ≠ 2^j for any j ∈ [0, 1236].

CONTRADICTION!

Let me re-check. Maybe BSGS has a bug, or maybe my assumption about val's order is wrong.

"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod, invert, jacobi
import math
import time

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1
N = int(F2)

print("=== Investigating val^2 ∉ <2> ===")
print()

# For a = 5 (which has (5/N) = -1):
a = 5
exp = (N - 1) // 2474
val = int(powmod(a, exp, N))
val_sq = (val * val) % N

# Check: val^2474 = 1?
v_2474 = int(powmod(val, 2474, N))
print(f"val^2474 mod N (first 30) = {str(v_2474)[:30]}")
print(f"val^2474 == 1? {v_2474 == 1}")
print()

# Check: val^1237 = -1?
v_1237 = int(powmod(val, 1237, N))
print(f"val^1237 mod N (first 30) = {str(v_1237)[:30]}")
print(f"val^1237 == N-1 (=-1)? {v_1237 == N - 1}")
print()

# Check: val^2 has order 1237?
v_sq = (val * val) % N
v_sq_1237 = int(powmod(v_sq, 1237, N))
print(f"(val^2)^1237 mod N (first 30) = {str(v_sq_1237)[:30]}")
print(f"(val^2)^1237 == 1? {v_sq_1237 == 1}")
print()

# Now: BSGS to find j with 2^j ≡ val^2 mod N
# <2> has order 1237. So j ∈ [0, 1236].
print(f"BSGS to find j with 2^j ≡ val^2 mod N (val^2 has order 1237):")

# Build table of 2^0, 2^1, ..., 2^m where m = ceil(sqrt(1237)) ≈ 36
m = int(math.isqrt(1237)) + 1
print(f"m = {m}")

table = {}
val_bsgs = 1
for j in range(m):
    table[val_bsgs] = j
    val_bsgs = (val_bsgs * 2) % N

print(f"Built table with {len(table)} entries")

# Compute 2^(-m) mod N
two_m = int(powmod(2, m, N))
inv_2m = int(invert(two_m, N))
print(f"2^m = 2^{m} = {str(two_m)[:30]}... (first 30 digits)")
print(f"2^(-m) = {str(inv_2m)[:30]}... (first 30 digits)")
print()

# Search
gamma = v_sq
found_j = None
for k in range(m + 1):
    if gamma in table:
        found_j = (k * m + table[gamma]) % 1237
        print(f"Found! k = {k}, table[gamma] = {table[gamma]}")
        break
    gamma = (gamma * inv_2m) % N

print(f"found_j = {found_j}")
if found_j is not None:
    print(f"Verify: 2^{found_j} mod N == val^2? {int(powmod(2, found_j, N)) == v_sq}")
else:
    print(f"NOT FOUND in <2>! This is unexpected.")
    print()
    print("Let me verify val^2 is actually in (Z/NZ)* with order 1237:")
    print(f"  (val^2)^1237 mod N = {v_sq_1237}")
    print(f"  Is 1? {v_sq_1237 == 1}")
    print()
    print("Possible explanations:")
    print("1. val^2 is in <2 mod N> but BSGS has a bug")
    print("2. <2> in (Z/NZ)* is NOT cyclic of order 1237 — perhaps it's larger")
    print("3. N is prime (it's not, but let's check)")
    print()
    print(f"is_prime(N)? {is_prime(N)}")
    print(f"phi(N) order? Actually N is composite.")
    print()
    # Check: maybe ord_N(2) > 1237?
    # 2^1237 = 1 mod N (we verified). So ord | 1237 = prime. So ord = 1 or 1237.
    # 2 != 1, so ord = 1237.
    # So <2> has order 1237 in (Z/NZ)*.
    # 
    # If val^2 has order 1237 and is in (Z/NZ)*, then by CRT val^2 mod qi is in 
    # <2 mod qi>. But (Z/qi Z)* might not be cyclic of order qi-1 — wait, it IS, 
    # since qi is prime. So <2 mod qi> is unique subgroup of order 1237.
    # 
    # So val^2 mod qi IS in <2 mod qi>. So val^2 IS in <2 mod N> (the image via CRT).
    # 
    # But <2 mod N> = <2> as a subgroup of (Z/NZ)* (since 2 is in (Z/NZ)* and 
    # generates the cyclic group of order 1237 that maps to <2 mod qi> for each qi).
    # 
    # So val^2 SHOULD be in <2>. BSGS should find it.
    # 
    # Let me check by direct enumeration:
    print()
    print("Direct enumeration: try all j in [0, 1236] and check 2^j mod N == val^2:")
    val_sq_target = v_sq
    found_direct = None
    for j in range(1237):
        if int(powmod(2, j, N)) == val_sq_target:
            found_direct = j
            print(f"  >>> FOUND: j = {j}")
            break
    if found_direct is None:
        print("  >>> NOT FOUND in direct enumeration either!")
        print()
        print("This is BIZARRE. Either val^2 is NOT in (Z/NZ)* (which is impossible since val is),")
        print("or there's some issue with the math.")
        print()
        print("Let me check if val is in (Z/NZ)* (i.e., gcd(val, N) = 1):")
        g = gcd(val, N)
        print(f"  gcd(val, N) = {g}")
        if g > 1:
            print(f"  >>> val is NOT coprime to N! FACTOR FOUND: {g}")
            if int(M) % g == 0:
                print(f"  ✓ REAL FACTOR of M(1237)!")
                cof = N // g
                print(f"  cofactor: {cof}")
