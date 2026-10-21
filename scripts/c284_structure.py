#!/usr/bin/env python3
"""C284 structural analysis."""
import sys
sys.set_int_max_str_digits(1000000)
import gmpy2
from gmpy2 import mpz, is_prime, isqrt, iroot, gcd, powmod, jacobi

C = mpz(53392955842462906502525256206896237530607657681405452248628829538140335056019091833139309039691476989536595672486245741799613486059460767317912672601233477410458189253022780891585730123223883909898404934891596729489833819787859139386557550548823481244976333432522178629028656984007087)

print(f"C284 = {C}")
print(f"Decimal digits: {len(str(C))}")
print(f"Bit length: {C.bit_length()}")
print(f"C mod 4 = {C % 4}")
print(f"C mod 8 = {C % 8}")
print(f"C mod 12 = {C % 12}")
print(f"C mod 1229 = {C % 1229}")
print(f"C mod 2458 = {C % 2458}")

# Check perfect power
print("\n=== Perfect power check ===")
for k in range(2, 30):
    root, exact = iroot(C, k)
    if exact:
        print(f"  C = ({root})^{k}")
        print(f"  Is root prime? {is_prime(root)}")
        break
else:
    print(f"  C is NOT a perfect power (checked up to k=29)")

# Verify C | 2^1229 - 1
print("\n=== Mersenne structure ===")
N = powmod(2, 1229, C)
print(f"  2^1229 mod C = {N}")
print(f"  (2^1229 - 1) mod C = {(N - 1) % C}")
print(f"  => C divides 2^1229 - 1: {(N - 1) % C == 0}")

# Verify known factors divide
print("\n=== Known factor verification ===")
known_factors = [
    ("36871", mpz(36871)),
    ("46703", mpz(46703)),
    ("P23 = 10543179280661916121033", mpz(10543179280661916121033)),
    ("P55 = 9536289355314392579996071515160583098298616686033085857", mpz(9536289355314392579996071515160583098298616686033085857)),
]
product = mpz(1)
for name, f in known_factors:
    print(f"  {name}: divides C? {C % f == 0}; is prime? {is_prime(f)}")
    product *= f

print(f"\nProduct of known factors: {product}")
print(f"C / product = {C // product}")
print(f"C mod product = {C % product}")
print(f"Co-factor: {(C // product)} ({len(str(C // product))} digits)")
print(f"Co-factor is prime? {is_prime(C // product)}")

# Check (1229 / q) for hypothetical q
# Check small primes p: what is ord_p(2)?
print("\n=== Order of 2 mod small primes ===")
small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
for p in small_primes:
    order = 1
    val = mpz(2)
    while val % p != 1:
        val = (val * 2) % p
        order += 1
        if order > 100:
            break
    print(f"  ord_{p}(2) = {order}, p mod 4 = {p % 4}, p mod 1229 = {p % 1229}")

# Verify form q = 2458k + 1 for known factors
print("\n=== q-1 = 2458*k analysis for known factors ===")
for name, f in known_factors:
    k = (f - 1) // 2458
    print(f"  {name} = 2458*{k} + 1; (f-1)/2458 = {k}; exact? {(f-1) % 2458 == 0}")

# Quadratic residue analysis
print("\n=== Quadratic residue analysis ===")
# If C ≡ 3 mod 4, then for prime q | C: (q / C-q-complement-pair-pattern)
# Actually, since C ≡ 3 mod 4, the primes q | C must be (1 mod 4, 3 mod 4) pairs
# (i.e., odd number of primes ≡ 3 mod 4)
# Let's verify: each prime factor q_i must have q_i mod 4 such that product = 3 mod 4
# C mod 4 = 3, so product of (q_i mod 4) ≡ 3 mod 4
# Since each q_i ≡ 1 or 3 mod 4, and the product is 3 mod 4, there must be an odd number of q_i ≡ 3 mod 4
print(f"  C mod 4 = {C % 4}")
print(f"  Number of prime factors ≡ 3 mod 4 must be odd (1, 3, 5, ...)")

# Is C ≡ 1 mod 8?
print(f"  C mod 8 = {C % 8}")
# If C ≡ 3 mod 8, then prime factors split as: an odd number ≡ 3 or 5 mod 8, with sum of residues = 3 mod 8

# Pollard p-1 / p+1 hint: what is C mod 1229?
print(f"\n  C mod 1229 = {C % 1229}")
print(f"  C-1 mod 1229 = {(C-1) % 1229}")
print(f"  C+1 mod 1229 = {(C+1) % 1229}")

# Fermat's Little Theorem check on potential small factors
print("\n=== Small factor trial up to 10^7 ===")
# Trial divide C by primes p = 2458k+1 up to 10^7
small_factors_found = []
import math
k_max = 10**7 // 2458
print(f"  Checking k in [1, {k_max}]...")
for k in range(1, k_max + 1):
    q = 2458 * k + 1
    # Quick primality check via gmpy2
    if gmpy2.is_prime(q):
        if C % q == 0:
            small_factors_found.append((k, q))
            print(f"  !!! Found small factor: q = {q} (k = {k})")
            break  # don't search more
if not small_factors_found:
    print(f"  No small factor found up to k={k_max} (~q up to 10^7)")

# Trial divide up to 10^8 if time permits — should be fast since we only check primes of form 2458k+1
print(f"\n=== Extended trial up to 10^8 ===")
k_max_2 = 10**8 // 2458
print(f"  Checking k in [1, {k_max_2}]...")
found = False
for k in range(k_max + 1, k_max_2 + 1):
    q = 2458 * k + 1
    if gmpy2.is_prime(q):
        if C % q == 0:
            print(f"  !!! Found small factor: q = {q} (k = {k})")
            found = True
            break
if not found:
    print(f"  No small factor found up to k={k_max_2} (~q up to 10^8)")
