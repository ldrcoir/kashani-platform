#!/usr/bin/env python3
"""
CREATIVE ALGORITHM FROM SCRATCH — no Euler, no Riemann, no advanced tools.

Setup:
- We know M = 2^1237 - 1 = F1 * F2 (we have F1, want to find factors of F2)
- We know 2^1237 = M + 1 (trivial)

Algorithm idea (from scratch):

1. The "binary long division" of 2^j by F1 gives a quotient S_j = floor(2^j / F1).
2. S_j satisfies a recurrence: S_{j+1} = 2*S_j + c_j (where c_j is the carry bit).
3. But there's also a "mod M" reduction. When 2*V_j ≥ M, we have S_{j+1} = 2*S_j + c_j - F2.

The KEY observation:
- If we use a base OTHER than 2, say F1 itself, then F1 has some order mod each prime q | F2.
- If ord_q(F1) is small for SOME q (but not all), gcd(F1^k - 1, M) gives a factor.

This is just P-1 with base F1 — but F1 is uniquely related to the structure of M(1237).
Specifically: F1 is the LARGEST known factor of M(1237), and it's an "atypical" small factor.

ACTUALLY, a more interesting idea: since F1 ≡ 0 mod F1, computing F1^k mod M gives 0 mod F1.
So F1^k - 1 ≡ -1 mod F1, and gcd(F1^k - 1, M) = gcd(F1^k - 1, F2).

So: F1 is "automatically coprime" to M (in the sense that F1^k - 1 has no factor of F1).
This is a free advantage! We can compute F1^k mod M freely, and gcd gives us factors of F2 directly.

Let me try this — P-1 with base F1, and various exponents.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod, invert
import math
import time
from pathlib import Path

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1
N = int(F2)

LOG = Path('/home/z/my-project/download/from_scratch.log')
LOG.write_text('')
def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')

log(f'=== روش اختراعی از صفر ===')
log(f'')
log(f'استدلال:')
log(f'  M = F1 * F2 (می‌دانم F1، نمی‌دانم F2)')
log(f'  2^1237 = M + 1 (یعنی 2^1237 ≡ 1 mod M)')
log(f'  ایده: از F1 به‌عنوان base در P-1 استفاده کن')
log(f'  چون F1 ≡ 0 mod F1، پس F1^k - 1 ≡ -1 mod F1')
log(f'  پس gcd(F1^k - 1, M) = gcd(F1^k - 1, F2) به‌طور خودکار!')
log(f'')

# ============================================================
# روش ۱: P-1 با base = F1، exponents ساختاری
# ============================================================
log(f'=== روش ۱: P-1 با base = F1 ===')
log(f'')

# Try: F1^k mod M for various k, take gcd(F1^k - 1, M)
# Since F1 ≡ 0 mod F1, gcd(F1^k - 1, F1) = gcd(-1, F1) = 1
# So gcd(F1^k - 1, M) = gcd(F1^k - 1, F2)

# First, let's compute F1^2 mod M and see what we get
val_F1_sq = powmod(F1, 2, M)
log(f'F1^2 mod M (first 60 digits): {str(val_F1_sq)[:60]}')
g = gcd(int(val_F1_sq) - 1, int(M))
log(f'gcd(F1^2 - 1, M) = {g}')
if 1 < g < int(M):
    log(f'>>> FACTOR! {g}')
log(f'')

# Try various k
log(f'آزمایش k های ساختاری:')
exponents_to_try = []
# Powers of 2
for j in range(0, 30):
    exponents_to_try.append((f'2^{j}', 1 << j))
# Multiples of 1237
for j in range(1, 30):
    exponents_to_try.append((f'1237*{j}', 1237 * j))
# Multiples of 2474
for j in range(1, 30):
    exponents_to_try.append((f'2474*{j}', 2474 * j))
# Primorial-style: products of small primes
for limit in [10, 100, 1000, 10000, 100000]:
    primorial = 1
    p = 2
    while p <= limit:
        primorial *= p
        p = int(gmpy2.next_prime(gmpy2.mpz(p)))
    exponents_to_try.append((f'primorial({limit})', primorial))
# Some specific large numbers
exponents_to_try.append(('1237^2', 1237**2))
exponents_to_try.append(('1237^3', 1237**3))
exponents_to_try.append(('F1 mod 1237', int(F1 % 1237)))
exponents_to_try.append(('F1 - 1', int(F1 - 1)))
exponents_to_try.append(('(F1-1)/2474', int((F1 - 1) // 2474)))

factor_found = None
t0 = time.time()
for label, k in exponents_to_try:
    if k <= 0: continue
    val = powmod(F1, k, M)
    val_minus_1 = (int(val) - 1) % int(M)
    g = gcd(val_minus_1, int(M))
    if 1 < g < int(M):
        log(f'  k={label}: FACTOR FOUND! {g}')
        log(f'  is_prime: {is_prime(g)}')
        cof = int(M) // g
        log(f'  cofactor: {str(cof)[:60]}... ({len(str(cof))} digits)')
        log(f'  is_prime(cofactor): {is_prime(cof)}')
        if int(M) % g == 0:
            log(f'  ✓ REAL FACTOR of M(1237)!')
        factor_found = g
        break
    elif g == int(M):
        # F1^k ≡ 1 mod M, means F1^k ≡ 1 mod both F1 and F2
        # F1^k ≡ 1 mod F1 means 0 ≡ 1 mod F1, impossible
        # So this shouldn't happen unless there's an error
        log(f'  k={label}: gcd = M (unexpected)')
    elif g == 1:
        pass  # no factor
    if time.time() - t0 > 30:
        log(f'  زمان بیش از 30s، توقف')
        break

elapsed = time.time() - t0
if not factor_found:
    log(f'  ✗ هیچ فاکتور در این exponents پیدا نشد (elapsed {elapsed:.1f}s)')
log(f'')

# ============================================================
# روش ۲: استفاده از Fibonacci / Lucas با base = F1
# ============================================================
log(f'=== روش ۲: Lucas sequence با P = F1 ===')
log(f'')

# Lucas sequence V_k(P, 1) where P = F1
# V_0 = 2, V_1 = P, V_{k+1} = P*V_k - V_{k-1}
# Fast doubling: V_{2k} = V_k^2 - 2, V_{2k+1} = V_k * V_{k+1} - P

def lucas_v_f1(k, N):
    """Compute V_k(F1, 1) mod N using fast doubling."""
    if k == 0: return 2 % N
    if k == 1: return int(F1) % N
    bits = bin(k)[2:]
    a, b = mpz(2), mpz(int(F1) % N)  # V_0, V_1
    for bit in bits[1:]:
        # V_{2n} = V_n^2 - 2 (since Q=1)
        # V_{2n+1} = V_n * V_{n+1} - P
        c = (a*a - 2) % N  # V_2n
        d = (a*b - int(F1)) % N  # V_2n+1
        if bit == '0':
            a, b = c, d
        else:
            e = (b*b - 2) % N  # V_2n+2
            a, b = d, e
    return int(a)

# Try V_k(F1, 1) mod M for various k
log(f'محاسبه‌ی V_k(F1, 1) mod M برای k های ساختاری:')
for k_label, k in [('1237', 1237), ('2474', 2474), ('4948', 4948), ('1237^2', 1237**2), 
                    ('2^20', 1<<20), ('2^30', 1<<30), ('2^40', 1<<40),
                    ('10^6', 10**6), ('10^7', 10**7)]:
    t0 = time.time()
    v = lucas_v_f1(k, int(M))
    elapsed = time.time() - t0
    # gcd(V_k - 2, M) — V_k = 2 means rank of apparition divides k
    g = gcd(v - 2, int(M))
    log(f'  k={k_label}: V_k mod M (first 30) = {str(v)[:30]}, gcd(V_k - 2, M) = {g} (elapsed {elapsed:.3f}s)')
    if 1 < g < int(M):
        log(f'  >>> FACTOR! {g}')
        factor_found = g
        break

log(f'')

# ============================================================
# روش ۳: استفاده از F1 به‌عنوان "anchor" برای ساخت element با order مختلف
# ============================================================
log(f'=== روش ۳: ساخت element با base = (F1 + a) برای a های کوچک ===')
log(f'')

# (F1 + a) mod M = F1 + a (since F1 < M)
# Compute (F1 + a)^k mod M for various a, k

factor_found = None
for a in [1, 2, 3, 5, 7, 11, 13, -1, -2, -3, -5, -7]:
    base = (int(F1) + a) % int(M)
    if base == 0: continue
    log(f'  base = F1 + {a} = {str(base)[:30]}...')
    for k_label, k in [('2474', 2474), ('1237^2', 1237**2), ('10^6', 10**6), ('10^7', 10**7)]:
        val = powmod(base, k, int(M))
        for delta in [-1, 1]:
            g = gcd((int(val) + delta) % int(M), int(M))
            if 1 < g < int(M):
                log(f'    k={k_label}, delta={delta}: FACTOR {g}')
                factor_found = g
                break
        if factor_found: break
    if factor_found: break

if not factor_found:
    log(f'  ✗ هیچ فاکتور در این روش‌ها')
log(f'')

# ============================================================
# روش ۴: استفاده از F1 به‌عنوان "ماتریس تبدیل"
# ============================================================
log(f'=== روش ۴: تبدیل F1 به‌عنوان ماتریس 2x2 ===')
log(f'')

# Consider the 2x2 matrix A = [[F1, 1], [1, 0]] mod M.
# A^k has determinant (-1)^k and trace V_k(F1, -1) (Lucas-like).
# If A^k ≡ I mod some q | F2 but not others, we get a factor.

# Compute A^k for various k, take gcd of "off-diagonal" with M.

def mat_mult(A, B, N):
    """Multiply two 2x2 matrices mod N."""
    return [
        [(A[0][0]*B[0][0] + A[0][1]*B[1][0]) % N, (A[0][0]*B[0][1] + A[0][1]*B[1][1]) % N],
        [(A[1][0]*B[0][0] + A[1][1]*B[1][0]) % N, (A[1][0]*B[0][1] + A[1][1]*B[1][1]) % N],
    ]

def mat_pow(A, k, N):
    """Compute A^k mod N by fast exponentiation."""
    result = [[1, 0], [0, 1]]  # identity
    base = [row[:] for row in A]
    while k > 0:
        if k & 1:
            result = mat_mult(result, base, N)
        base = mat_mult(base, base, N)
        k >>= 1
    return result

A = [[int(F1), 1], [1, 0]]
log(f'  A = [[F1, 1], [1, 0]]')

for k_label, k in [('2474', 2474), ('1237^2', 1237**2), ('10^6', 10**6), ('10^7', 10**7), ('10^8', 10**8)]:
    t0 = time.time()
    A_k = mat_pow(A, k, int(M))
    elapsed = time.time() - t0
    # Check if A_k is close to identity mod some factor
    # A_k = I + something. gcd(something, M) might give factor.
    # off-diagonal elements
    g01 = gcd(A_k[0][1], int(M))
    g10 = gcd(A_k[1][0], int(M))
    # diagonal differences
    g00 = gcd(A_k[0][0] - 1, int(M))
    g11 = gcd(A_k[1][1] - 1, int(M))
    log(f'  k={k_label}: gcd(off-diag) = {g01}, {g10}; gcd(diag-1) = {g00}, {g11} (elapsed {elapsed:.3f}s)')
    for g in [g01, g10, g00, g11]:
        if 1 < g < int(M):
            log(f'    >>> FACTOR! {g}')
            log(f'    is_prime: {is_prime(g)}')
            cof = int(M) // g
            log(f'    cofactor: {str(cof)[:60]}...')
            factor_found = g
            break
    if factor_found: break

if not factor_found:
    log(f'  ✗ هیچ فاکتور')
log(f'')

# ============================================================
# روش ۵: استفاده از "разност" F1 و F2 به‌صورت ضمنی
# ============================================================
log(f'=== روش ۵: محاسبه‌ی (F1 + 1)^k mod M ===')
log(f'  اگر (F1+1) بر q | F2 بخش‌پذیر باشد، می‌توانیم استفاده کنیم')
log(f'')

# (F1 + 1) might be related to F2 in some way
F1_plus_1 = int(F1) + 1
log(f'  F1 + 1 = {F1_plus_1}')
log(f'  is_prime(F1 + 1)? {is_prime(F1_plus_1)}')
log(f'  F1 + 1 = 2^{int(math.log2(F1_plus_1))} (تقریباً)')
log(f'  F1 + 1 in binary: {bin(F1_plus_1)[:60]}...')

# Check small factors of F1 + 1
F1p1_temp = F1_plus_1
factors_F1p1 = []
for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]:
    while F1p1_temp % p == 0:
        factors_F1p1.append(p)
        F1p1_temp //= p
log(f'  عوامل کوچک F1+1: {factors_F1p1}')
log(f'  باقی‌مانده: {F1p1_temp} ({len(str(F1p1_temp))} digits, is_prime: {is_prime(F1p1_temp)})')
log(f'')

# Now: maybe (F1+1) has a special structure that we can use
# Specifically, (F1+1) = 2 * something, and "something" might be related to F2
# Let's check gcd((F1+1)/2 - some_value, M)
# Or: gcd(F1+1 mod F2, M) — but we don't know F2

# Try: gcd((F1+1)^k - 1, M) for various k
for k in [1237, 2474, 4948, 1237**2, 10**6, 10**7, 10**8]:
    val = powmod(F1_plus_1, k, int(M))
    g = gcd(int(val) - 1, int(M))
    if 1 < g < int(M):
        log(f'  k={k}: FACTOR! {g}')
        factor_found = g
        break
    elif g == int(M):
        log(f'  k={k}: trivial gcd = M')
    else:
        log(f'  k={k}: no factor (gcd = 1)')

log(f'')
log(f'=== پایان روش‌های اختراعی ===')
