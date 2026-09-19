#!/usr/bin/env python3
"""
KEY INSIGHT: val = a^((N-1)/2474) is computed. We expected val^2474 = 1 mod N.
But val^2474 ≠ 1 mod N for a=5.

This means: for SOME qi | N, val^2474 ≡ 1 mod qi (since a^(qi-1) ≡ 1 mod qi by Fermat, 
and (qi-1) | (N-1) means a^(N-1) ≡ 1 mod qi, so val^2474 = a^(N-1) ≡ 1 mod qi).
BUT: for other qi', val^2474 ≢ 1 mod qi'.

Wait, that's not right. Let me think again.

Actually: val^2474 = a^((N-1)/2474 * 2474) = a^(N-1).
By Fermat, a^(qi-1) ≡ 1 mod qi (if gcd(a, qi) = 1).
Since qi | N, (qi - 1) | phi(N) but not necessarily (N - 1).
But N = product of qi, so (N-1) mod (qi-1) is not necessarily 0.

Hmm! So a^(N-1) mod qi = a^((N-1) mod (qi-1)) mod qi, which is NOT necessarily 1.

So val^2474 = a^(N-1) is NOT necessarily 1 mod qi for each qi.

If val^2474 ≡ 1 mod qi but ≢ 1 mod qj, then gcd(val^2474 - 1, N) gives a factor!

Let me test this directly.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod, invert, jacobi
import math
import time
from pathlib import Path

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1
N = int(F2)

LOG = Path('/home/z/my-project/download/fermat_method.log')
LOG.write_text('')
def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')

log(f'=== روش Fermat: استفاده از a^(N-1) ≢ 1 mod N ===')
log(f'')
log(f'استدلال:')
log(f'  val = a^((N-1)/2474)')
log(f'  val^2474 = a^(N-1)')
log(f'  برای هر qi | N: a^(qi-1) ≡ 1 mod qi (Fermat)')
log(f'  ولی (N-1) mod (qi-1) ممکن است ≠ 0 باشد')
log(f'  پس a^(N-1) mod qi ممکن است ≠ 1 باشد')
log(f'  اگر برای برخی qi: a^(N-1) ≡ 1 mod qi')
log(f'  و برای برخی qj: a^(N-1) ≢ 1 mod qj')
log(f'  آن‌گاه gcd(a^(N-1) - 1, N) فاکتور می‌دهد!')
log(f'')

# Compute a^(N-1) - 1 mod N and take gcd for various a
factor_found = None
for a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]:
    val_N = int(powmod(a, N - 1, N))
    g = gcd(val_N - 1, N)
    if 1 < g < N:
        log(f'  a={a}: gcd(a^(N-1) - 1, N) = {g}')
        log(f'  >>> FACTOR FOUND!')
        log(f'  is_prime: {is_prime(g)}')
        cof = N // g
        log(f'  cofactor: ' + str(cof)[:60] + '... (' + str(len(str(cof))) + ' digits)')
        log(f'  is_prime(cofactor): {is_prime(cof)}')
        if int(M) % g == 0:
            log(f'  ✓ REAL FACTOR of M(1237)!')
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
                    if cur == '-1' or g < int(cur):
                        out.append(f'1237\t{g}\n')
                    else:
                        out.append(line)
                else:
                    out.append(line)
            FACTORS_FILE.write_text(''.join(out))
            log(f'  Table updated!')
        factor_found = g
        break
    elif g == N:
        # All qi have a^(N-1) ≡ 1 mod qi. Trivial — a is "Fermat-pseudoprime base" for all qi.
        # Try gcd(a^(N-1)/d - 1, N) for various d
        for d in [2, 3, 4, 6, 7, 8, 12, 14, 16, 21, 24, 28, 42, 48, 56, 112, 168, 336]:
            if (N-1) % d != 0:
                continue
            val_d = int(powmod(a, (N-1) // d, N))
            g_d = gcd(val_d - 1, N)
            if 1 < g_d < N:
                log(f'  a={a}, d={d}: gcd(a^(N-1)/d - 1, N) = {g_d}')
                log(f'  >>> FACTOR FOUND!')
                log(f'  is_prime: {is_prime(g_d)}')
                cof = N // g_d
                log(f'  cofactor: ' + str(cof)[:60] + '...')
                if int(M) % g_d == 0:
                    log(f'  ✓ REAL FACTOR!')
                    factor_found = g_d
                    break
            g_d_plus = gcd(val_d + 1, N)
            if 1 < g_d_plus < N:
                log(f'  a={a}, d={d}: gcd(a^(N-1)/d + 1, N) = {g_d_plus}')
                log(f'  >>> FACTOR FOUND!')
                log(f'  is_prime: {is_prime(g_d_plus)}')
                cof = N // g_d_plus
                log(f'  cofactor: ' + str(cof)[:60] + '...')
                if int(M) % g_d_plus == 0:
                    log(f'  ✓ REAL FACTOR!')
                    factor_found = g_d_plus
                    break
        if factor_found:
            break

if not factor_found:
    log(f'  هیچ فاکتور از این روش پیدا نشد')
    log(f'  (یعنی برای همه‌ی a، a^(N-1) ≡ 1 mod همه‌ی qi، که N را pseudoprime می‌کند)')
log(f'')
log(f'=== پایان ===')
