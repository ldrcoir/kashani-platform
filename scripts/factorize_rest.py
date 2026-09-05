#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Factorize entries 145-191."""
import sys
from sympy import primerange
from gmpy2 import is_prime as gmpy_is_prime

MERSENNE_PRIME_EXPONENTS = {2,3,5,7,13,17,19,31,61,89,107,127,521,607,1279,2203,2281,3217,4253,4423}

seq = {}
with open('/home/z/my-project/download/A136030_1_to_8000.txt') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) == 2:
            seq[int(parts[0])] = int(parts[1])

all_primes = list(primerange(2, 100000))
candidate_primes = [p for p in all_primes if p not in MERSENNE_PRIME_EXPONENTS]
target_primes = candidate_primes[:8000]

output_lines = []
for idx in range(145, 192):
    p = target_primes[idx-1]
    smallest = seq[idx]
    M = (1 << p) - 1
    
    if smallest <= 0:
        line = "[{}] M({}) = {} - عامل پیدا نشد".format(idx, p, M)
    else:
        quotient = M // smallest
        if gmpy_is_prime(quotient):
            line = "[{}] M({}) = {} * {} (هر دو اول)".format(idx, p, smallest, quotient)
        else:
            # Just show smallest and remaining
            q = quotient
            factors = [smallest]
            d = smallest + 1
            limit = 10**7
            while d * d <= q and d < limit:
                if q % d == 0:
                    factors.append(d)
                    q //= d
                    while q % d == 0:
                        factors.append(d)
                        q //= d
                d += 2 if d > 2 else 1
            if q > 1:
                if gmpy_is_prime(q):
                    factors.append(q)
                else:
                    factors.append("C{}".format(len(str(q))))
            factor_str = " * ".join(str(f) for f in factors)
            line = "[{}] M({}) = {} = {}".format(idx, p, M, factor_str)
    
    print(line, flush=True)
    output_lines.append(line)

# Append to existing file
with open('/home/z/my-project/download/A136030_first_191_factorizations.txt', 'a', encoding='utf-8') as f:
    for line in output_lines:
        f.write(line + "\n")
print("\nذخیره شد!")
