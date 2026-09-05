#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full factorization of Mersenne numbers M(p) = 2^p - 1
for the first 191 entries of A136030 (which are all known).
"""

import sys
from sympy import primerange, factorint
from gmpy2 import is_prime as gmpy_is_prime

MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607,
    1279, 2203, 2281, 3217, 4253, 4423
}

# Read A136030 file
seq = {}
with open('/home/z/my-project/download/A136030_1_to_8000.txt') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) == 2:
            seq[int(parts[0])] = int(parts[1])

# Get primes (skipping Mersenne prime exponents)
all_primes = list(primerange(2, 100000))
candidate_primes = [p for p in all_primes if p not in MERSENNE_PRIME_EXPONENTS]
target_primes = candidate_primes[:8000]

print("=" * 70)
print("تجزیه کامل اعداد مرسن M(p) = 2^p - 1 برای 191 ورودی اول A136030")
print("=" * 70)
print()

# For each of first 191 entries, factorize M(p)
output_lines = []
for idx in range(1, 192):
    p = target_primes[idx-1]
    smallest = seq[idx]
    
    if smallest == -1:
        line = "[{}] M({}) = عامل پیدا نشد".format(idx, p)
    else:
        M = (1 << p) - 1
        # Use sympy to factorize
        # For small p, this is fast
        # For large p (>200), might be slow but we only need first 191
        try:
            factors = factorint(M, limit=10**15)
            if factors:
                factor_str = " * ".join("{}^{}".format(f, e) if e > 1 else str(f) 
                                         for f, e in sorted(factors.items()))
                remaining = M
                for f, e in factors.items():
                    remaining //= f**e
                if remaining > 1:
                    if remaining < 10**30:
                        # Try to factorize remaining more
                        factors2 = factorint(remaining, limit=10**10)
                        if factors2 and len(factors2) > 0:
                            factor_str += " * " + " * ".join("{}^{}".format(f, e) if e > 1 else str(f) 
                                                              for f, e in sorted(factors2.items()))
                            for f, e in factors2.items():
                                remaining //= f**e
                    if remaining > 1:
                        if gmpy_is_prime(remaining):
                            factor_str += " * {} (prime)".format(remaining)
                        else:
                            factor_str += " * C{} (composite)".format(len(str(remaining)))
                line = "[{}] M({}) = {} = {}".format(idx, p, M, factor_str)
            else:
                line = "[{}] M({}) = {} (no small factors)".format(idx, p, M)
        except Exception as e:
            line = "[{}] M({}) = error: {}".format(idx, p, e)
    
    print(line)
    output_lines.append(line)
    sys.stdout.flush()

# Save to file
with open('/home/z/my-project/download/A136030_first_191_factorizations.txt', 'w', encoding='utf-8') as f:
    f.write("تجزیه کامل اعداد مرسن M(p) = 2^p - 1\n")
    f.write("برای 191 ورودی اول دنباله A136030\n")
    f.write("=" * 60 + "\n\n")
    for line in output_lines:
        f.write(line + "\n")

print()
print("=" * 70)
print("ذخیره شد در: /home/z/my-project/download/A136030_first_191_factorizations.txt")
print("=" * 70)
