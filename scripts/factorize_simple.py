#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple factorization: just show smallest factor and quotient."""
import sys
from sympy import primerange
from gmpy2 import is_prime as gmpy_is_prime, mpz

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
for idx in range(1, 192):
    p = target_primes[idx-1]
    smallest = seq[idx]
    M = (1 << p) - 1
    
    if smallest == -1 or smallest == 0:
        line = "[{}] M({}) = {} - عامل پیدا نشد".format(idx, p, M)
    elif smallest == 1:
        line = "[{}] M({}) = 1".format(idx, p)
    else:
        # Divide M by smallest
        quotient = M // smallest
        remainder = M % smallest
        if remainder != 0:
            line = "[{}] M({}) - ERROR: smallest not a factor".format(idx, p)
        else:
            # Check if quotient is prime
            if gmpy_is_prime(quotient):
                line = "[{}] M({}) = {} * {} (هر دو اول)".format(idx, p, smallest, quotient)
            else:
                # Try to factor quotient with small primes
                q = quotient
                factors = [smallest]
                # Try trial division up to 10^7
                d = smallest + 1
                while d * d <= q and d < 10**7:
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
                # Build factor string
                factor_str = " * ".join(str(f) for f in factors)
                line = "[{}] M({}) = {} = {}".format(idx, p, M, factor_str)
    
    print(line, flush=True)
    output_lines.append(line)

with open('/home/z/my-project/download/A136030_first_191_factorizations.txt', 'w', encoding='utf-8') as f:
    f.write("تجزیه کامل اعداد مرسن M(p) = 2^p - 1\n")
    f.write("برای 191 ورودی اول دنباله A136030\n")
    f.write("=" * 60 + "\n\n")
    for line in output_lines:
        f.write(line + "\n")
print("\nذخیره شد!")
