#!/usr/bin/env python3
"""
FRESH APPROACH — start from scratch, no preconceptions.

Question: We have N = F2 = M(1237)/F1, and we want to factor N.

What is UNIQUE about Mersenne numbers vs other composites?
- 2^1237 ≡ 1 mod N
- This is a "syntactic" property — the binary expansion of N is special

NEW IDEA — think about this from a completely different angle:

For a prime p, M(p) = 2^p - 1. The factorization of M(p) is special because:
- All prime factors q of M(p) satisfy q ≡ 1 mod 2p
- This is the "Mersenne factor structure"

But: M(1237) = F1 * F2 = F1 * (q1 * q2 * ... * qk) for unknown q1, q2, ..., qk.

Now: what if I focus on the F1 we already know?
F1 is a 70-digit prime, and F1 ≡ 1 mod 2474.

F1 - 1 = 2 * 1237 * (large number k_F1)
k_F1 ≈ 10^66 (we computed earlier)

Idea: F1 and F2's factors come from the same "Mersenne structure". Maybe F1 and 
each qi of F2 share some algebraic relationship we can exploit?

Let me think... 

ANOTHER ANGLE: 2^1237 - 1 = F1 * F2. So 2 ≡ 1 (mod gcd(F1, 2-1=1)) — trivial.
But: 2^1237 = 1 + F1*F2. So 2^1237 ≡ 1 mod F1 AND mod F2 (well, mod each qi of F2).

What if I compute (2^j mod F1) for j = 1..1236, and compare to (2^j mod F2)?
If for some j, (2^j mod F1) has some special structure that aligns with F2's structure...

Hmm, this is just <2 mod F1> = cyclic of order 1237, and <2 mod F2> = cyclic of order 1237 (or sub-order if F2 has multiple prime factors with different ord).

Actually: ord_qi(2) for qi | F2:
- 2^1237 ≡ 1 mod qi (since qi | F2 | M(1237))
- ord_qi(2) | 1237 = prime
- ord_qi(2) ≠ 1 (else qi | 1)
- So ord_qi(2) = 1237 for each qi | F2.

So <2 mod qi> has order 1237 for each qi.
<2 mod F2> has order LCM of these = 1237 (since 1237 is prime and all are 1237).

So <2 mod F2> = cyclic of order 1237.
Similarly <2 mod F1> = cyclic of order 1237 (since ord_F1(2) = 1237, as we verified).

By CRT: <2 mod N = F1*F2> = <2 mod F1> × <2 mod F2> as groups, but both have order 1237.

Wait, the product has order lcm(1237, 1237) = 1237, not 1237^2 = 1530169.

So <2 mod N> is cyclic of order 1237, NOT the full product!

This means: there's an isomorphism <2 mod N> ≅ <2 mod F1> ≅ <2 mod F2> (all cyclic of order 1237).

The element 2 mod N corresponds to (2 mod F1, 2 mod F2) via CRT.
For each j, 2^j mod N corresponds to (2^j mod F1, 2^j mod F2).

Since all three groups are cyclic of order 1237 and 2 is a generator in each,
the map j → 2^j is a bijection from Z/1237 to each group.

So the map <2 mod N> → <2 mod F1> × <2 mod F2> is a DIAGONAL embedding:
  2^j mod N ↔ (2^j mod F1, 2^j mod F2)

This is consistent (not a "split" subgroup).

Hmm. So <2 mod N> is just the diagonal, not the full product.

NOW THE KEY INSIGHT:
The product group (Z/F1 Z)* × (Z/F2 Z)* has order phi(F1)*phi(F2) = (F1-1)*(F2-1).
The diagonal <2> has order 1237.
There's MUCH MORE in the product group than the diagonal.

If we can find an element in (Z/N Z)* = (Z/F1 Z)* × (Z/F2 Z)* that is in the 
"off-diagonal" (e.g., (1, g) for g ≠ 1 in (Z/F2 Z)*), we'd factor N.

But how to find such "off-diagonal" elements without knowing F1, F2 factorization?

NEW IDEA: 
We KNOW F1 explicitly. So we can compute things mod F1 explicitly.
For example: 2^j mod F1 — we know this for any j.
What if we want an element g ∈ (Z/N Z)* such that g ≡ 1 mod F1 but g ≢ 1 mod F2?

g ≡ 1 mod F1 means g = 1 + F1*t for some t.
g ≢ 1 mod F2 means (1 + F1*t) ≢ 1 mod F2, i.e., F1*t ≢ 0 mod F2, i.e., t ≢ 0 mod (F2/gcd(F1,F2)).
Since gcd(F1, F2) = 1 (both prime, different), we need t ≢ 0 mod F2.

So we want t such that 1 + F1*t ≡ 1 mod F1 (trivially true) but ≢ 1 mod F2.

Equivalently: F1*t ≢ 0 mod F2, i.e., t ≢ 0 mod F2.

For ANY t in [1, F2-1] coprime to F2, we have g = 1 + F1*t that is:
- ≡ 1 mod F1 (good)
- ≢ 1 mod F2 (good)
- So gcd(g - 1, N) = gcd(F1*t, N) = F1 * gcd(t, N) (since gcd(F1, F2)=1)
  - if t coprime to N: gcd = F1 (TRIVIAL! gives us F1 back, which we already know)

So this doesn't help directly.

REFINEMENT:
We want g such that g ≡ 1 mod qi for SOME qi | F2, but g ≢ 1 mod qj for OTHER qj.

Equiv: g^? ≡ 1 mod (product of subset of qi's) but not others.

For this, we need to find g with structure that varies across qi's.

METHOD: Use modular structure that's different mod each qi.

Specifically: take g = 2^j * (something with structure depending on qi).

Actually, the simplest such "something": a random element h in (Z/N Z)*.
For each qi: h mod qi is random in (Z/qi Z)*.
h^((qi-1)/2) mod qi = ±1 (Legendre symbol).
For different qi, the sign might differ.

So gcd(h^((N-1)/2) - 1, N) might give a factor if the Legendre symbols differ.

But (N-1)/2 is the same for all qi via Fermat (since N is pseudoprime).

Hmm, but if N is pseudoprime base h, then h^((N-1)/2) ≡ ±1 mod N (Euler).
If = 1 mod all qi: gcd = N trivial.
If = -1 mod all qi: gcd = 1 (since (h^(...)+1) ≡ 0 mod N means all qi have h^... = -1).
If +1 mod some, -1 mod others: gcd(h^((N-1)/2) - 1, N) gives the "+1" subset → factor!

We computed Jacobi symbols earlier and found some a with (a/N) = -1.
(a/N) = -1 means odd number of qi have (a/qi) = -1.
So a^((N-1)/2) = product of (a/qi) across qi.
- = -1 if odd number of qi have (a/qi) = -1.
- = 1 if even number.

For a with (a/N) = -1: a^((N-1)/2) ≡ -1 mod N (since = product = -1).
So gcd(a^((N-1)/2) - 1, N) = gcd(-2, N) = 1 (since N is odd). TRIVIAL.

For a with (a/N) = +1: a^((N-1)/2) ≡ +1 mod N.
So gcd(a^((N-1)/2) - 1, N) = N. TRIVIAL.

Hmm, no luck.

But wait: a^((N-1)/2) = (a/q1)*(a/q2)*...*(a/qk) mod N.
For (a/N) = +1: product = +1.
For (a/N) = -1: product = -1.

We're taking a^((N-1)/2), which equals (a/N) by Euler criterion (since N is pseudoprime).

So this only gives us ±1, not a "partial" factorization.

NEW IDEA: Use (N-1)/4 or other fractions of (N-1).
N - 1 = 2^4 * 3 * 7 * remaining.
(N-1)/2 = 2^3 * 3 * 7 * remaining.

If a^((N-1)/2) = +1 mod N (Euler +1), then ord(a) | (N-1)/2.
What about a^((N-1)/4)? 
For each qi: a^((N-1)/4) mod qi = a^(((qi-1) * (N-1)/(qi-1))/4) — depends on (qi-1) divisibility by 4.

If 4 | (qi-1) (which it does since qi ≡ 1 mod 2474 = 1 mod 2, and qi odd → qi ≡ 1 mod 4 if (qi-1)/2 even).
qi ≡ 1 mod 2474. 2474 = 2*1237. So qi - 1 = 2 * 1237 * m. 
qi - 1 mod 4 = (2*1237*m) mod 4 = 2 * (1237*m mod 2).
1237 is odd, so 1237*m mod 2 = m mod 2.
So qi - 1 mod 4 = 2 * (m mod 2).
If m even: qi - 1 ≡ 0 mod 4 → qi ≡ 1 mod 4.
If m odd: qi - 1 ≡ 2 mod 4 → qi ≡ 3 mod 4.

So qi can be 1 or 3 mod 4, depending on parity of m = (qi-1)/2474.

If different qi have different m parity, then a^((N-1)/4) might give different signs.

Let me try!
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

LOG = Path('/home/z/my-project/download/fractional_euler.log')
LOG.write_text('')
def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')

log(f'=== روش جدید: Fractional Euler — استفاده از (N-1)/4 ===')
log(f'')
log(f'استدلال:')
log(f'  N - 1 = 2^4 * 3 * 7 * remaining = 2474 * k_total (where 2474 | (N-1))')
log(f'  برای هر qi | N: qi - 1 = 2474 * m_i')
log(f'  m_i parity (even/odd) → qi ≡ 1 or 3 mod 4')
log(f'  اگر qi های مختلف m_i parity متفاوت دارند، می‌توانیم از این استفاده کنیم')
log(f'')

# Compute (N-1) factorization we know
N_minus_1 = N - 1
log(f'N - 1 = {str(N_minus_1)[:30]}...')
log(f'(N-1) mod 4 = {N_minus_1 % 4}')
log(f'(N-1) mod 8 = {N_minus_1 % 8}')
log(f'(N-1) mod 16 = {N_minus_1 % 16}')

# v_2(N-1)
v2 = 0
temp = N_minus_1
while temp % 2 == 0:
    v2 += 1
    temp //= 2
log(f'v_2(N-1) = {v2}, (N-1) = 2^{v2} * {str(temp)[:30]}...')
log(f'')

# Try: for each a, compute a^((N-1)/2^j) for j = 1, 2, ..., v2+1
# Check gcd with N

factor_found = None
for a in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]:
    for j in range(1, v2 + 2):
        if (N_minus_1) % (1 << j) != 0:
            continue
        exp = N_minus_1 >> j  # (N-1) / 2^j
        val = int(powmod(a, exp, N))
        g_minus = gcd(val - 1, N)
        g_plus = gcd(val + 1, N)
        if 1 < g_minus < N:
            log(f'  a={a}, j={j}: gcd(a^((N-1)/2^{j}) - 1, N) = {g_minus}')
            log(f'  >>> FACTOR FOUND: {g_minus}')
            log(f'  is_prime: {is_prime(g_minus)}')
            cof = N // g_minus
            log(f'  cofactor: ' + str(cof)[:60] + '... (' + str(len(str(cof))) + ' digits)')
            log(f'  is_prime(cofactor): {is_prime(cof)}')
            if int(M) % g_minus == 0:
                log(f'  ✓ REAL FACTOR of M(1237)!')
            factor_found = g_minus
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
                    if cur == '-1' or g_minus < int(cur):
                        out.append(f'1237\t{g_minus}\n')
                    else:
                        out.append(line)
                else:
                    out.append(line)
            FACTORS_FILE.write_text(''.join(out))
            log(f'  Table updated!')
            break
        if 1 < g_plus < N:
            log(f'  a={a}, j={j}: gcd(a^((N-1)/2^{j}) + 1, N) = {g_plus}')
            log(f'  >>> FACTOR FOUND: {g_plus}')
            log(f'  is_prime: {is_prime(g_plus)}')
            cof = N // g_plus
            log(f'  cofactor: ' + str(cof)[:60] + '... (' + str(len(str(cof))) + ' digits)')
            log(f'  is_prime(cofactor): {is_prime(cof)}')
            if int(M) % g_plus == 0:
                log(f'  ✓ REAL FACTOR!')
            factor_found = g_plus
            break
    if factor_found:
        break

if not factor_found:
    log(f'  ✗ هیچ فاکتور از روش Fractional Euler پیدا نشد')
    log(f'  (یعنی برای همه‌ی a و همه‌ی 2^j، a^((N-1)/2^j) ≡ ±1 mod همه‌ی qi به‌طور یکنواخت)')
log(f'')

# ============================================================
# روش ۲: استثمار تنوع در 2474 | (qi - 1)
# (N-1)/2474 = sum of (qi - 1)/2474 * (product of other qj - 1)/2474 (approximately)
# اگر m_i = (qi-1)/2474 دارای parity متفاوت باشد، a^((N-1)/2474 * 1237) = a^((N-1)/2)
# ممکن است sign‌های متفاوت بدهد
# ============================================================
log(f'=== روش ۲: gcd(a^((N-1)/2474 ± 1) ===')
log(f'برای هر a: val = a^((N-1)/2474). بررسی gcd(val ± 1, N):')
log(f'')

factor_found = None
exp_2474 = N_minus_1 // 2474
for a in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]:
    val = int(powmod(a, exp_2474, N))
    g_minus = gcd(val - 1, N)
    g_plus = gcd(val + 1, N)
    if 1 < g_minus < N:
        log(f'  a={a}: gcd(val - 1, N) = {g_minus}')
        log(f'  >>> FACTOR: {g_minus}')
        log(f'  is_prime: {is_prime(g_minus)}')
        cof = N // g_minus
        log(f'  cofactor: ' + str(cof)[:60] + '...')
        if int(M) % g_minus == 0:
            log(f'  ✓ REAL FACTOR!')
        factor_found = g_minus
        break
    if 1 < g_plus < N:
        log(f'  a={a}: gcd(val + 1, N) = {g_plus}')
        log(f'  >>> FACTOR: {g_plus}')
        log(f'  is_prime: {is_prime(g_plus)}')
        cof = N // g_plus
        log(f'  cofactor: ' + str(cof)[:60] + '...')
        if int(M) % g_plus == 0:
            log(f'  ✓ REAL FACTOR!')
        factor_found = g_plus
        break

if not factor_found:
    log(f'  ✗ هیچ فاکتور پیدا نشد')
log(f'')

# ============================================================
# روش ۳: BSGS-style با exponent ساختاری
# اگر بدانیم val^k = 1 mod qi ولی val^k ≠ 1 mod qj، gcd(val^k - 1, N) فاکتور می‌دهد.
# ولی نمی‌دانیم k. آزمایش k های مختلف.
# ============================================================
log(f'=== روش ۳: آزمایش k های ساختاری برای gcd(val^k - 1, N) ===')
log(f'')

# Use val = a^((N-1)/2474) and try various k
factor_found = None
a = 5  # use one with (a/N) = -1
val = int(powmod(a, exp_2474, N))
log(f'  استفاده از a = 5, val = a^((N-1)/2474)')
log(f'  val (first 30 digits): {str(val)[:30]}')
log(f'')

# Try k's related to structure
k_candidates = []
for j in range(1, 50):
    k_candidates.append(1 << j)  # powers of 2
for j in range(50):
    k_candidates.append(1237 * j + 1)
for j in range(50):
    k_candidates.append(2474 * j + 1)
for j in range(50):
    k_candidates.append(j * 1237)
for j in range(50):
    k_candidates.append(j * 2474)
# Add small primes
for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]:
    for mult in [1, 2, 3, 1237, 2474]:
        k_candidates.append(p * mult)
# Some special values
k_candidates.extend([1237, 2474, 4948, 9896, 2*1237, 3*1237, 5*1237, 7*1237, 11*1237, 13*1237])

for k in k_candidates:
    val_k = int(powmod(val, k, N))
    g_minus = gcd(val_k - 1, N)
    g_plus = gcd(val_k + 1, N)
    if 1 < g_minus < N:
        log(f'  k={k}: gcd(val^k - 1, N) = {g_minus}')
        log(f'  >>> FACTOR: {g_minus}')
        factor_found = g_minus
        break
    if 1 < g_plus < N:
        log(f'  k={k}: gcd(val^k + 1, N) = {g_plus}')
        log(f'  >>> FACTOR: {g_plus}')
        factor_found = g_plus
        break

if not factor_found:
    log(f'  ✗ هیچ فاکتور از k های ساختاری پیدا نشد')
log(f'')

log(f'=== پایان ===')
