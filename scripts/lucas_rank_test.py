#!/usr/bin/env python3
"""
FINAL CREATIVE ATTEMPT: Using the structure we discovered.

Key insight from previous tests:
- gcd(V_k(1,-1) - 2, N) = 1 for k = 1237, 2474, 4948, 9896 (small multiples of 1237)
- gcd(V_k(1,-1) - 2, N) = N for k = 2^20, 2^30, 2^40 (powers of 2)

This means: for the prime factors qi of N:
- ord_qi(V_1 in Lucas sequence) does NOT divide 1237 (otherwise V_1237 ≡ 2 mod qi, giving gcd = N).
- ord_qi(V_1) DOES divide 2^40 (since V_{2^40} ≡ 2 mod N means mod each qi too).

Wait, if gcd = N for k = 2^40, that means V_{2^40} ≡ 2 mod N, which means V_{2^40} ≡ 2 mod each qi.
The Lucas sequence V_k starts at V_0 = 2, V_1 = P, V_2 = P^2 - 2Q, etc.
V_k = 2 iff (k is multiple of the rank of apparition) OR (k = 0).

If V_{2^40} ≡ 2 mod qi, then the rank of apparition (smallest k > 0 with V_k = 2) divides 2^40.
So rank is a power of 2, ≤ 2^40.

But for k = 1237 (which is prime), V_{1237} ≢ 2 mod qi (since gcd = 1, not N).
This means rank does NOT divide 1237. Combined with rank | 2^40, we get rank = 2^j for some j ≤ 40.

Wait, this might tell us something about qi!

Actually let me check: for the Lucas sequence V_k(P, Q), V_k = 2 happens when k is a multiple of the "rank of apparition" α(P, Q). If α | k, then V_k = 2 mod N (or mod any factor).

Since V_{2^40} = 2 mod N, we have α | 2^40, so α is a power of 2.

The fact that V_{1237} ≠ 2 mod N (gcd = 1, but actually let me double-check what 1 means here):
Actually gcd(V_1237 - 2, N) = 1 means V_1237 ≢ 2 mod any qi. So α ∤ 1237.

OK so α is a power of 2 between 2^1 and 2^40.

If we find the EXACT α, we can extract info:
- V_α ≡ 2 mod qi for each qi
- V_{α/2} ≢ 2 mod qi (if α > 1)
- V_{α/2} mod qi is something else

Actually, V_{2^j} = V_{2^(j-1)}^2 - 2*Q^(2^(j-1)). With Q = -1: V_{2^j} = V_{2^(j-1)}^2 - 2*(-1)^(2^(j-1)).
For j ≥ 2, 2^(j-1) is even, so Q^(2^(j-1)) = 1, so V_{2^j} = V_{2^(j-1)}^2 - 2.

So V_{2^j} = V_{2^(j-1)}^2 - 2 for j ≥ 2.
V_1 = P = 1
V_2 = 1 - 2*(-1) = 3 (using V_2 = P*V_1 - Q*V_0 = 1*1 - (-1)*2 = 1 + 2 = 3)
V_4 = 3^2 - 2 = 7
V_8 = 7^2 - 2 = 47
V_16 = 47^2 - 2 = 2207
V_32 = 2207^2 - 2 = 4870847
...

These are LUCAS NUMBERS! L_n = V_n(1, -1). Specifically L_2 = 3, L_4 = 7, L_8 = 47, L_16 = 2207, ...
These are L_{2^j} = 2 cosh(2^j * arccosh(1/2)) but also iterates of x^2 - 2.

So for each qi | F2, we have L_{2^j} mod qi = 2 for some j ≤ 40 (since V_{2^40} ≡ 2 mod qi).

Actually, V_k = 2 happens iff α | k. So α | 2^40, meaning α = 2^j for some j.

If α = 1, then V_1 = 2, but V_1 = P = 1 ≠ 2. So α > 1.
If α = 2, then V_2 ≡ 2 mod qi, i.e., 3 ≡ 2 mod qi, i.e., qi | 1. Impossible.
If α = 4, then V_4 ≡ 2 mod qi, i.e., 7 ≡ 2 mod qi, i.e., qi | 5. So qi = 5.
If α = 8, then V_8 ≡ 2 mod qi, i.e., 47 ≡ 2 mod qi, i.e., qi | 45 = 9*5. So qi ∈ {3, 5}.
If α = 16, then V_16 ≡ 2 mod qi, i.e., 2207 ≡ 2 mod qi, i.e., qi | 2205 = 5 * 441 = 5 * 9 * 49. So qi ∈ {3, 5, 7}.
If α = 32, then V_32 ≡ 2 mod qi, i.e., 4870847 ≡ 2 mod qi, i.e., qi | 4870845 = ?
  4870845 / 3 = 1623615; /5 = 974169; /3 = 324723 / 3 = 108241; 108241 = 108241. Is 108241 prime? sqrt(108241) ~ 329. 
  Try: 108241 / 7 = 15463 (check: 7 * 15463 = 108241). 15463: /7=2209; 2209 = 47^2. So 108241 = 7 * 7 * 47^2 = 7^2 * 47^2.
  So 4870845 = 5 * 3^3 * 7^2 * 47^2 = 5 * 27 * 49 * 2209.
  Primes dividing 4870845: {3, 5, 7, 47}.
  
Generally, V_{2^j} - 2 = (L_{2^j} - 2). The set of primes dividing V_{2^j} - 2 gives candidates for qi.

But we know qi | N = F2, and qi > 10^9. So none of {3, 5, 7, 47, ...} are factors.

If α = 2^j for some j ≤ 40, and qi | V_{2^j} - 2 but qi is large (>10^9), then qi divides the (j-th) iterate of x^2 - 2 starting from 3, minus 2.

Hmm, but we said V_{2^40} ≡ 2 mod N (so V_{2^40} - 2 ≡ 0 mod N, i.e., N | (V_{2^40} - 2)).
That's actually gcd = N (trivial). 

Wait wait — let me re-check the earlier output:
'k=1048576: gcd(V_k - 2, N) = 93234...737 (= N)'
Yes, gcd = N. So V_{2^20} ≡ 2 mod N. So 2^20 is a multiple of α (rank of apparition).

For V_{2^20} ≡ 2 mod qi for all qi | N: this means α(qi) | 2^20 for each qi.
So α(qi) is a power of 2, dividing 2^20 = 2^20, so α(qi) = 2^j for j ≤ 20.

So qi | V_{2^j} - 2 for some j ≤ 20.

Now: V_{2^j} - 2 has known factorization: 
  V_2 - 2 = 3 - 2 = 1 (trivial)
  V_4 - 2 = 7 - 2 = 5
  V_8 - 2 = 47 - 2 = 45 = 3^2 * 5
  V_16 - 2 = 2207 - 2 = 2205 = 3^2 * 5 * 7^2
  V_32 - 2 = 4870847 - 2 = 4870845 = 3^3 * 5 * 7^2 * 47^2
  ...

The primes dividing these are: 3, 5, 7, 47, 2207, 4870847, ...

NONE of these are > 10^9. So if α(qi) ≤ 2^20, then qi must divide some V_{2^j} - 2 with j ≤ 20, but the prime factors of these are small.

This means: the primes qi | F2 do NOT have α(qi) ≤ 2^20. So gcd(V_{2^20} - 2, N) shouldn't be N.

But we observed gcd(V_{2^20} - 2, N) = N! This contradicts!

Unless... my Lucas sequence formula is wrong somewhere. Let me check.

Actually wait — maybe gcd = N because N | V_{2^20} - 2 for a different reason. Let me re-verify with computation.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod
import math
import time

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1
N = int(F2)

def lucas_v_mod_correct(k, P_param, Q_param, N):
    """Compute V_k(P, Q) mod N using correct fast doubling formulas.
    
    V_0 = 2, V_1 = P
    V_2n = V_n^2 - 2*Q^n
    V_2n+1 = V_n * V_{n+1} - P * Q^n
    
    Need to track (V_n, V_{n+1}, Q^n).
    """
    if k == 0: return 2 % N
    if k == 1: return P_param % N
    
    bits = bin(k)[2:]
    # Start at (V_0, V_1, Q^0) = (2, P, 1)
    a, b, qn = mpz(2), mpz(P_param) % N, mpz(1)
    
    for bit in bits:
        # First: doubling (V_n, V_{n+1}, Q^n) -> (V_2n, V_2n+1, Q^2n)
        # V_2n = a^2 - 2*qn
        # V_2n+1 = a*b - P*qn
        # Q^2n = qn^2
        c = (a*a - 2*qn) % N  # V_2n
        d = (a*b - P_param*qn) % N  # V_2n+1
        new_qn = (qn*qn) % N  # Q^2n
        
        if bit == '0':
            a, b, qn = c, d, new_qn
        else:
            # Advance by 1: (V_2n, V_2n+1, Q^2n) -> (V_2n+1, V_2n+2, Q^(2n+1))
            # V_2n+2 = ? Use V_2n+2 = V_{n+1}^2 - 2*Q^(n+1) but we have (V_2n, V_2n+1, Q^2n).
            # Alternative: V_{2n+2} = V_{2n+1} * V_1 - Q * V_{2n} = d * P - Q * c
            # Or: V_{2n+2} = P * V_{2n+1} - Q * V_{2n} = P_param * d - Q_param * c
            e = (P_param * d - Q_param * c) % N
            new_qn_adv = (new_qn * Q_param) % N  # Q^(2n+1) = Q^2n * Q
            a, b, qn = d, e, new_qn_adv
    
    return int(a)

# Verify: V_2(1, -1) should be 3.
print(f"V_2(1, -1) = {lucas_v_mod_correct(2, 1, -1, 10**9)}")  # should be 3
print(f"V_4(1, -1) = {lucas_v_mod_correct(4, 1, -1, 10**9)}")  # should be 7
print(f"V_8(1, -1) = {lucas_v_mod_correct(8, 1, -1, 10**9)}")  # should be 47
print(f"V_16(1, -1) = {lucas_v_mod_correct(16, 1, -1, 10**9)}")  # should be 2207
print(f"V_32(1, -1) = {lucas_v_mod_correct(32, 1, -1, 10**9)}")  # should be 4870847
print()

# OK, the formula seems right. Now compute V_k mod N for various k to find pattern
print(f"N = F2, {len(str(N))} digits")
print()
print("Computing V_k(1, -1) mod N for k = 2^j (j = 1..30):")
for j in range(1, 31):
    k = 1 << j
    t0 = time.time()
    v = lucas_v_mod_correct(k, 1, -1, N)
    elapsed = time.time() - t0
    g = gcd(v - 2, N)
    print(f"  k=2^{j}={k}: V_k mod N (first 30 digits)={str(v)[:30]}, gcd(V_k - 2, N) = {g} (digits: {len(str(g)) if g > 0 else 0}) (elapsed {elapsed:.4f}s)")
    if 1 < g < N:
        print(f"  >>> FACTOR FOUND: {g}")
        print(f"  is_prime: {is_prime(g)}")
        cof = N // g
        print(f"  cofactor: " + str(cof)[:60] + "...")
        if int(M) % g == 0:
            print(f"  ✓ REAL FACTOR of M(1237)!")
        sys.exit(0)

# Now: try smaller j to see exact threshold
print()
print("For each j, factor V_{2^j} - 2 and check if any factor divides N:")
# V_{2^j} - 2 for j = 2, 3, 4, 5, ...
# We know:
# V_2 - 2 = 1
# V_4 - 2 = 5
# V_8 - 2 = 45 = 3^2 * 5
# V_16 - 2 = 2205 = 3^2 * 5 * 7^2
# V_32 - 2 = 4870845 = 3^3 * 5 * 7^2 * 47^2
# V_64 - 2 = 23725150497407 = ?
# V_128 - 2 = ?

# Compute iterates
val = 3  # V_2 = 3
for j in range(2, 30):
    val_minus_2 = val - 2
    # Find prime factorization of val_minus_2
    print(f"  V_{1 << j} - 2 = {val_minus_2}")
    # Trial-divide by small primes
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]
    factorization = []
    remaining = val_minus_2
    for p in small_primes:
        while remaining % p == 0:
            factorization.append(p)
            remaining //= p
    if remaining > 1:
        factorization.append(f"remaining={remaining}")
    print(f"    factorization (small primes): {factorization}")
    # Check if any small prime divides N
    for p in factorization:
        if isinstance(p, int) and N % p == 0:
            print(f"  >>> {p} divides N! FACTOR: {p}")
            sys.exit(0)
    # Iterate: V_{2^(j+1)} = V_{2^j}^2 - 2 (since Q = -1, Q^(2^j) = (-1)^(2^j) = 1 for j >= 1)
    val = val * val - 2
    if val > 10**100:
        # too big, switch to mod N
        break

# Now compute V_{2^j} mod N for j up to where V_k ≡ 2 mod N
print()
print("Computing V_{2^j}(1, -1) mod N for j = 1..50 to find smallest j with V ≡ 2 mod N:")
v = 3  # V_2 = 3 mod N (no need to mod since 3 < N)
v_history = [(2, 3)]
for j in range(2, 51):
    # V_{2^j} = V_{2^(j-1)}^2 - 2 (since Q^(2^(j-1)) = 1 for j >= 2)
    # Wait: Q = -1, so Q^(2^(j-1)) = (-1)^(2^(j-1)).
    # For j = 2: Q^2 = 1, V_4 = V_2^2 - 2*1 = 9 - 2 = 7 ✓
    # For j = 3: Q^4 = 1, V_8 = V_4^2 - 2*1 = 49 - 2 = 47 ✓
    # So for j >= 2, V_{2^j} = V_{2^(j-1)}^2 - 2 (mod N)
    v = (v * v - 2) % N
    g = gcd(v - 2, N)
    print(f"  j={j} (k=2^{j}): V mod N (first 20)={str(v)[:20]}, gcd(V-2, N)={'N (trivial)' if g == N else '1' if g == 1 else g} (digits: {len(str(g)) if g > 1 else 0})")
    v_history.append((j, v))
    if 1 < g < N:
        print(f"  >>> FACTOR: {g}")
        sys.exit(0)
    if g == N:
        # V_k ≡ 2 mod N for this k = 2^j. So 2^j is a multiple of alpha for all qi.
        print(f"  Found smallest j with V_k ≡ 2 mod N: j = {j}")
        break
