#!/usr/bin/env python3
"""
TRULY from scratch — forget all algorithms.

Setup:
- We have M = 2^1237 - 1, F1, F2 = M/F1.
- We want to factor F2.

Let's think purely arithmetically. The previous "creative" methods all returned
F1 because the rank of apparition structure aligned. Let's try things that
definitely don't have this property.

Idea: Use F1 + F2 = F1 + M/F1. This is a known quantity:
  F1 + F2 = F1 + M/F1 = (F1^2 + M) / F1
  
We can compute F1^2 + M mod anything. And we know F1, M, so F1^2 + M is known.

Better: Let's think about the "Euclidean rhythm" of M:
- gcd(M, F1) = F1
- gcd(M, 2^j) = gcd(2^1237 - 1, 2^j) = 1 if 0 < j < 1237, gcd = 2^1237 - 1 = M if j = 1237
- gcd(M, 2^j - 1) = 2^gcd(1237, j) - 1 = 2^1 - 1 = 1 if gcd(1237,j) = 1

So 2^j - 1 is coprime to M for j = 1, 2, ..., 1236 (since 1237 is prime).

What about gcd(M - F1, M)? = gcd(F1*(F2 - 1), M) = F1 * gcd(F2 - 1, F2) (if coprime F1, F2)
   = F1 * gcd(F2 - 1, F2) = F1 * 1 = F1 (if F2 is not divisible by anything F2-1 shares, which is true)
Hmm, F1 again.

What about gcd(F1 + F2 - 2, M)?
F1 + F2 - 2 = F1 + M/F1 - 2.
mod F1: F1 + F2 - 2 ≡ 0 + F2 - 2 ≡ F2 - 2 mod F1
mod F2: F1 + F2 - 2 ≡ F1 - 2 + 0 ≡ F1 - 2 mod F2

So gcd(F1 + F2 - 2, M) = gcd(F1 + F2 - 2, F1*F2). 
   = gcd(F2 - 2, F1) * gcd(F1 - 2, F2) (roughly, if coprime F1, F2)
We can compute F1 + F2 - 2 explicitly!
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod, invert, next_prime
import math
import time
from pathlib import Path

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1
N = int(F2)

LOG = Path('/home/z/my-project/download/scratch_v2.log')
LOG.write_text('')
def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')

log(f'=== پَک کردن کامل — از صفر ===')
log(f'')
log(f'داده‌های خام:')
log(f'  M = 2^1237 - 1 ({len(str(M))} digits)')
log(f'  F1 = {F1} ({len(str(F1))} digits, prime)')
log(f'  F2 = M / F1 ({len(str(F2))} digits, composite)')
log(f'')

# ============================================================
# روش ۱: محاسبه‌ی F1 + F2 - 2 (یک عدد کاملاً مشخص)
# ============================================================
log(f'=== روش ۱: F1 + F2 - 2 (یک عدد مشخص) ===')
log(f'')

F1_int = int(F1)
F2_int = int(F2)

val_1 = F1_int + F2_int - 2
log(f'F1 + F2 - 2 = {val_1}')
log(f'  ({len(str(val_1))} digits, is_prime: {is_prime(val_1)})')
log(f'  این عدد mod F1 = {(F2_int - 2) % F1_int}')
log(f'  این عدد mod F2 = {(F1_int - 2) % F2_int}')
log(f'')

# Compute gcd of various combinations with M
candidates = [
    ('F1 + F2 - 2', F1_int + F2_int - 2),
    ('F1 + F2 - 1', F1_int + F2_int - 1),
    ('F1 + F2', F1_int + F2_int),
    ('F1 + F2 + 1', F1_int + F2_int + 1),
    ('F1 + F2 + 2', F1_int + F2_int + 2),
    ('F1*2 - F2', 2*F1_int - F2_int),
    ('F2 - F1', F2_int - F1_int),
    ('F2 mod F1', F2_int % F1_int),
    ('F1 mod F2', F1_int % F2_int),  # = F1 since F1 < F2
    ('F1 ^ 2 - F2', F1_int**2 - F2_int),
    ('F1 ^ 2 + F2', F1_int**2 + F2_int),
    ('F2 ^ 2 mod M', pow(F2_int, 2, int(M))),
    ('F2 ^ 3 mod M', pow(F2_int, 3, int(M))),
    ('F2 / 2 (int)', F2_int // 2),
    ('F2 mod 3', F2_int % 3),
    ('F2 mod 5', F2_int % 5),
    ('F2 mod 7', F2_int % 7),
    ('F2 mod 11', F2_int % 11),
    ('F2 mod 13', F2_int % 13),
    ('F2 mod 1237', F2_int % 1237),
    ('F2 mod 2474', F2_int % 2474),
]

factor_found = None
for label, val in candidates:
    if val == 0:
        log(f'  {label} = 0, skip')
        continue
    g = gcd(abs(val), int(M))
    if 1 < g < int(M):
        log(f'  {label} = {val}')
        log(f'  gcd({label}, M) = {g}')
        log(f'  >>> FACTOR! is_prime: {is_prime(g)}')
        if int(M) % g == 0:
            cof = int(M) // g
            log(f'  cofactor: {str(cof)[:60]}... ({len(str(cof))} digits)')
            log(f'  is_prime(cofactor): {is_prime(cof)}')
        factor_found = g
        break
    elif g == int(M):
        log(f'  {label}: gcd = M (trivial)')
    elif g == 1:
        log(f'  {label}: gcd = 1 (no factor)')
    else:
        log(f'  {label}: gcd = {g}')

if not factor_found:
    log(f'  ✗ هیچ فاکتور از F1+F2-combinations')
log(f'')

# ============================================================
# روش ۲: استفاده از M در ماتریس با F1
# ============================================================
log(f'=== روش ۲: ماتریس [[F1, M], [1, 0]] به توان k ===')
log(f'')

# A = [[F1, M], [1, 0]] mod M.
# A = [[F1 mod M, M mod M], [1, 0]] = [[F1, 0], [1, 0]] mod M.
# So A is just [[F1, 0], [1, 0]] mod M, which is degenerate.

# Better: A = [[F1, 1], [1, 0]] but compute mod (M + small offset)?
# Or: use [[F1 + 1, 1], [1, 0]] — F1 + 1 has different structure

# Actually, let's try a fresh matrix approach: 
# M^T = [[0, -1], [1, F1 + F2]] (companion matrix of x^2 - (F1+F2)x + F1*F2 = 0)
# Wait, x^2 - (F1+F2)x + M = 0 has roots F1 and F2.

# Compute M^k mod (M - p) for prime p? Let's try mod (M - 2) and (M - 3) etc.
# But (M - 2) = M - 2 is just a number, not useful directly.

# Let's try: gcd of trace(M^k mod N) - (F1 + F2) with N
# Where N = F2. If M^k ≡ [[F1^k, 0], [0, F2^k]] mod N (the eigenvalues are F1, F2 mod N)
# Hmm, the eigenvalues of M^T = [[0, -M], [1, F1+F2]] are F1 and F2.
# Mod N = F2: F2 mod N = 0, F1 mod N = F1.
# So eigenvalues mod N are F1 and 0. 
# M^T mod N = [[0, -M mod N], [1, (F1+F2) mod N]] = [[0, -F1*F2 mod F2], [1, F1]] 
#          = [[0, 0], [1, F1]] (since F1*F2 ≡ 0 mod F2)
# (M^T)^k mod N: characteristic polynomial x^2 - (F1+F2)x + M.
# Mod F2: x^2 - F1*x + 0 (since F2 ≡ 0, M ≡ 0 mod F2)
# So x^2 = F1*x, x^k = F1^(k-1) * x for k >= 1.
# (M^T)^k mod F2 has trace = F1^k (the x-eigenvalue sum: 0 + F1^k = F1^k for k >= 1)

# So: trace((M^T)^k mod M) = F1^k + F2^k mod M, but we don't know F2.

# Wait: trace((M^T)^k mod M) should be computable directly from M and F1.
# Let's compute it.

def mat_pow_trace_mod(A, k, mod):
    """Compute trace of A^k mod `mod` using fast exponentiation."""
    # A is 2x2
    result = [[1, 0], [0, 1]]  # identity, trace = 2
    base = [row[:] for row in A]
    while k > 0:
        if k & 1:
            new = [
                [(result[0][0]*base[0][0] + result[0][1]*base[1][0]) % mod, 
                 (result[0][0]*base[0][1] + result[0][1]*base[1][1]) % mod],
                [(result[1][0]*base[0][0] + result[1][1]*base[1][0]) % mod, 
                 (result[1][0]*base[0][1] + result[1][1]*base[1][1]) % mod]
            ]
            result = new
        new = [
            [(base[0][0]*base[0][0] + base[0][1]*base[1][0]) % mod, 
             (base[0][0]*base[0][1] + base[0][1]*base[1][1]) % mod],
            [(base[1][0]*base[0][0] + base[1][1]*base[1][0]) % mod, 
             (base[1][0]*base[0][1] + base[1][1]*base[1][1]) % mod]
        ]
        base = new
        k >>= 1
    return (result[0][0] + result[1][1]) % mod

# M^T = [[0, -M], [1, F1+F2]] — but we don't know F2.
# Hmm, this won't work since F2 is unknown.

# Alternative: use F1 as an "anchor" with M
# Consider A = [[F1, M mod F1], [1, 0]] = [[F1, 0], [1, 0]] — degenerate.
# A = [[F1, 1], [1, 0]] — we did this before, returns F1.

# Try: A = [[F1, M], [1, 1]] (different structure)
A = [[F1_int, int(M)], [1, 1]]
log(f'  A = [[F1, M], [1, 1]]')
log(f'  A mod F1 = [[0, 0], [1, 1]] — degenerate')
log(f'  A mod F2 = [[F1, 0], [1, 1]] (since M ≡ 0 mod F2)')

for k_label, k in [('1237', 1237), ('2474', 2474), ('4948', 4948), ('1237^2', 1237**2), ('10^6', 10**6)]:
    t0 = time.time()
    trace_M = mat_pow_trace_mod(A, k, int(M))  # trace mod M
    trace_F2 = mat_pow_trace_mod(A, k, N)      # trace mod F2 (cheating? we know F2)
    elapsed = time.time() - t0
    log(f'  k={k_label}: trace(A^k mod M) (first 30) = {str(trace_M)[:30]} (elapsed {elapsed:.3f}s)')
    log(f'    gcd(trace_M - trace_F2, M) — اگر فاکتور باشد: ')
    # trace_F2 might be 0 (if A is degenerate mod F2) — let's see
    g = gcd(abs(trace_M - trace_F2), int(M))
    if 1 < g < int(M):
        log(f'    >>> FACTOR! {g}')
        factor_found = g
        break

if not factor_found:
    log(f'  ✗ ماتریس روش به نتیجه نرسید')
log(f'')

# ============================================================
# روش ۳: استفاده از (F1 * a) mod M برای a های ساختاری
# ============================================================
log(f'=== روش ۳: (F1 * a) mod M برای a های ساختاری ===')
log(f'')

# (F1 * a) mod M = F1 * a (if a small) or = F1 * a - M * floor(F1 * a / M)
# In any case, gcd(F1 * a, M) = F1 * gcd(a, F2) since F1 | M.
# So gcd(F1 * a, M) gives us F1 * gcd(a, F2).
# If gcd(a, F2) = 1: result = F1 (trivial, gives back F1)
# If gcd(a, F2) > 1: result = F1 * gcd(a, F2) — would give factor of F2!

# But we need a to be such that gcd(a, F2) > 1, i.e., a has a factor in common with F2.
# Since F2's smallest factor > 10^50 (estimated), a must be > 10^50 to have a chance.

# So this is essentially "trial division with big numbers" — not useful.

# But wait: what if we use a = F1 itself? Then F1 * F1 = F1^2.
# gcd(F1^2, M) = F1 (trivial).

# What about a = M - 1? a = 2^1237 - 2 = 2(2^1236 - 1) = 2 * M(1236).
# M(1236) = 2^1236 - 1. gcd(M(1236), M) — since 1236 < 1237 and 1237 prime, 
# gcd(M(1236), M(1237)) = M(gcd(1236, 1237)) = M(1) = 1 (since gcd = 1).

# Hmm, still trivial.

# Let me try: gcd(F2 mod p, M) for various small primes p
# (F2 mod p) is small (less than p), so gcd with M (huge) is just gcd(F2 mod p, M)
# If p | F2, then F2 mod p = 0, gcd = 0... no wait, gcd(0, M) = M.
# If p does not divide F2, F2 mod p = small non-zero, gcd with M = 1 (since M is much bigger).

# So this is just trial division by p, which we've done before.

# Idea: use TWO bases simultaneously
# Compute (F1 * F2)^j mod M = M^j mod M = 0. Trivial.
# Compute (F1 + F2)^j mod M. We have F1 + F2 = F1 + M/F1.

F1_plus_F2 = F1_int + F2_int
log(f'F1 + F2 = {F1_plus_F2}')
log(f'  ({len(str(F1_plus_F2))} digits, is_prime: {is_prime(F1_plus_F2)})')
log(f'')

# Compute (F1+F2)^k mod M for various k
# This is the key: (F1+F2) is a SPECIFIC number we can compute.
# Its powers mod M will hit some structure.

for k in [1, 2, 3, 5, 7, 11, 1237, 2474, 4948, 2*1237**2, 10**6]:
    val = powmod(F1_plus_F2, k, int(M))
    g_minus = gcd(int(val) - 1, int(M))
    g_plus = gcd(int(val) + 1, int(M))
    if 1 < g_minus < int(M):
        log(f'  k={k}: gcd((F1+F2)^k - 1, M) = {g_minus} → FACTOR!')
        factor_found = g_minus
        break
    if 1 < g_plus < int(M):
        log(f'  k={k}: gcd((F1+F2)^k + 1, M) = {g_plus} → FACTOR!')
        factor_found = g_plus
        break
    if g_minus == int(M):
        log(f'  k={k}: (F1+F2)^k ≡ 1 mod M (trivial)')
    elif g_plus == int(M):
        log(f'  k={k}: (F1+F2)^k ≡ -1 mod M (trivial)')
    else:
        log(f'  k={k}: gcd = 1 (no factor)')

if not factor_found:
    log(f'  ✗ هیچ فاکتور از (F1+F2)^k')
log(f'')

# ============================================================
# روش ۴: «رسم» رفتار F2 در فرم باینری
# ============================================================
log(f'=== روش ۴: تحلیل باینری F2 ===')
log(f'')

# F2 in binary
F2_bin = bin(F2_int)[2:]
log(f'F2 در باینری: {F2_bin[:80]}... ({len(F2_bin)} bits)')
log(f'تعداد بیت‌های ۱: {F2_bin.count("1")}')
log(f'تعداد بیت‌های ۰: {F2_bin.count("0")}')
log(f'نسبت ۱ به ۰: {F2_bin.count("1") / F2_bin.count("0"):.4f}')
log(f'')

# Patterns
# Check for repeating patterns
for length in [1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
    # Find most common pattern of this length
    patterns = {}
    for i in range(len(F2_bin) - length):
        p = F2_bin[i:i+length]
        patterns[p] = patterns.get(p, 0) + 1
    if patterns:
        most_common = max(patterns, key=patterns.get)
        least_common = min(patterns, key=patterns.get)
        log(f'  طول {length}: پرتکرارترین = "{most_common}" ({patterns[most_common]} بار), کم‌تکرارترین = "{least_common}" ({patterns[least_common]} بار)')

log(f'')

# ============================================================
# روش ۵: استفاده از «رابطه‌ی پنهان» F2 ≡ (M - 0) / F1
# ============================================================
log(f'=== روش ۵: رابطه‌ی پنهان M = F1 * F2 ===')
log(f'')

# Since M = F1 * F2, we have F2 = M / F1 = (M mod F1^j) / F1 mod F1^j for various j.
# This is just F2 directly — we already have F2.

# Try: F2 mod (F1 - k) for small k
for k in range(-20, 21):
    if k == 0: continue
    mod = F1_int + k
    if mod <= 0: continue
    rem = F2_int % mod
    log(f'  F2 mod (F1 + ({k:+d})) = F2 mod {mod} = {rem}')
    if rem == 0:
        log(f'    >>> {mod} divides F2! FACTOR!')
        factor_found = mod
        break

log(f'')

# Try: F2 mod (F1 ± prime)
small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
for p in small_primes:
    for sign in [1, -1]:
        mod_val = F1_int + sign * p
        if mod_val <= 0: continue
        rem = F2_int % mod_val
        if rem == 0 and mod_val > 1 and mod_val < F2_int:
            log(f'  >>> F2 mod (F1 {"+" if sign>0 else "-"} {p}) = F2 mod {mod_val} = 0 → FACTOR!')
            factor_found = mod_val
            break
    if factor_found: break

if not factor_found:
    log(f'  ✗ هیچ فاکتور از F2 mod (F1 ± p)')
log(f'')

log(f'=== پایان ===')
