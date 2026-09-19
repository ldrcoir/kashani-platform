#!/usr/bin/env python3
"""
BREAKTHROUGH: 1237 | (N-1) and 2474 | (N-1).

This means (Z/NZ)* has a cyclic subgroup of order 2474 = 2 * 1237.

Reasoning:
- 2474 = 2 * 1237, and 1237 is prime.
- The subgroup of order 2474 has elements of order 1, 2, 1237, 2474.
- Element of order 2: -1 (the unique element with x^2 = 1, x ≠ 1).
- Element of order 1237: 2 (we know this!).
- Element of order 2474: g such that g^1237 = -1.

KEY INSIGHT: If we find g with g^1237 = -1 mod N, then:
- For each prime qi | N, g^1237 mod qi is some specific value.
- If g^1237 ≡ -1 mod qi (for ALL qi), then gcd(g^1237 + 1, N) = N (trivial).
- If g^1237 ≡ -1 mod some qi and ≢ -1 mod other qj, then gcd(g^1237 + 1, N) gives 
  product of qi's where g^1237 ≡ -1.

How to find g with g^1237 = -1 mod N?
- Pick random g. Compute g^1237 mod N.
- The result is some value. If = -1 (mod N), we found g.
- Probability: number of elements with g^1237 = -1 / phi(N).
- Number of elements with g^1237 = -1: depends on structure.
- For each qi: number of elements g with g^1237 = -1 mod qi is:
  - if 2474 | (qi - 1) (TRUE for all our qi), then number is 1236 (out of qi-1).
  - So number mod N = 1236^k.
- Probability = 1236^k / phi(N). Still very small.

Smarter approach: 
- Since 2474 | (N - 1), we can compute a^((N-1)/2474) which gives an element of 
  order dividing 2474 (so order ∈ {1, 2, 1237, 2474}).
- If order is 2474, we have g with g^1237 = -1.

Try this for various a!
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

LOG = Path('/home/z/my-project/download/order_2474_method.log')
LOG.write_text('')
def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')

log(f'=== روش جدید: استفاده از order 2474 در (Z/NZ)* ===')
log(f'')
log(f'کشف: (N-1) mod 2474 = {(N-1) % 2474} (= 0!)')
log(f'پس 2474 | (N-1)، یعنی (Z/NZ)* دارای زیرگروه cyclic از مرتبه‌ی 2474 است')
log(f'2474 = 2 × 1237 (1237 prime)')
log(f'عناصر این زیرگروه order ∈ {{1, 2, 1237, 2474}} دارند')
log(f'')

# Verify
log(f'بررسی: (N-1) / 2474 = ?')
exp = (N - 1) // 2474
log(f'  (N-1) / 2474 = {str(exp)[:60]}... ({len(str(exp))} digits)')
log(f'')

# For each a, compute a^((N-1)/2474) mod N.
# This gives an element with order dividing 2474.
# Check what order it has.

log(f'بررسی a^((N-1)/2474) برای اعداد اول کوچک:')
factor_found = None
for a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127]:
    val = int(powmod(a, exp, N))
    
    # Order dividing 2474 means val^2474 = 1.
    # What's the actual order? 
    # val^1 = val (could be 1 if order 1)
    # val^2 = ?
    # val^1237 = ? (could be -1 if order 2474)
    # val^2474 = ? (should be 1)
    
    # Check various
    val_1 = val
    val_2 = int(powmod(val, 2, N))
    val_1237 = int(powmod(val, 1237, N))
    val_2474 = int(powmod(val, 2474, N))
    
    log(f'  a={a}: val = a^((N-1)/2474), val^1 (first 20)={str(val_1)[:20]}, val^2 first={str(val_2)[:20]}, val^1237 first={str(val_1237)[:20]}, val^2474 first={str(val_2474)[:20]}')
    
    # Compute gcd of differences with N
    for label, v in [('val-1', val_1 - 1), ('val+1', val_1 + 1),
                     ('val^2-1', val_2 - 1), ('val^2+1', val_2 + 1),
                     ('val^1237-1', val_1237 - 1), ('val^1237+1', val_1237 + 1),
                     ('val^2474-1', val_2474 - 1), ('val^2474+1', val_2474 + 1)]:
        g = gcd(abs(v) % N, N)
        if 1 < g < N:
            log(f'    >>> FACTOR from {label}: {g}')
            log(f'    is_prime: {is_prime(g)}')
            cof = N // g
            log(f'    cofactor: ' + str(cof)[:60] + '... (' + str(len(str(cof))) + ' digits)')
            if int(M) % g == 0:
                log(f'    ✓ REAL FACTOR of M(1237)!')
                factor_found = g
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
                log(f'    Table updated!')
                sys.exit(0)
            break
    if factor_found:
        break

if not factor_found:
    log(f'  هیچ فاکتور پیدا نشد')
log(f'')

# ============================================================
# روش ۲: یافتن g با g^1237 ≡ -1 mod N از طریق BSGS یا ساخت هوشمند
# ============================================================
log(f'=== روش ۲: یافتن g با g^1237 ≡ -1 (یعنی order = 2474) ===')
log(f'')

# Idea: a^((N-1)/2474) gives an element of order dividing 2474.
# If order = 2474, then a^((N-1)/2) = a^((N-1)/2474 * 1237) = val^1237.
# We computed val^1237 above — let's see if it's -1 for any a.

# Actually, val^1237 = a^((N-1)/2) which is the Euler criterion!
# (a/N) = a^((N-1)/2) mod N = ±1.

# So val^1237 = (a/N) mod N.
# For a with (a/N) = -1, val^1237 ≡ -1 mod N. So val has order 2474!
# For a with (a/N) = +1, val^1237 ≡ +1 mod N. So val has order 1 or 1237.

# So: for a with (a/N) = -1, val = a^((N-1)/2474) has order 2474.
# For such val, val^1237 ≡ -1 mod N.

# But we want to extract a FACTOR, not just find val.
# val^1237 ≡ -1 mod N means val^1237 + 1 ≡ 0 mod N (trivial if N | (val^1237 + 1)).

# But val^1237 ≡ -1 mod N requires val^1237 + 1 ≡ 0 mod ALL qi. So gcd = N. Trivial.

# What if we use val^(1237/2)? But 1237 is prime, no half.

# Better: val has order 2474. Compute val^2 — order divides 1237. So val^2 in <2>!
# Find j with 2^j ≡ val^2 mod N (BSGS in <2>).
# Then val ≡ ± 2^(j/2) mod ... but j might not be even.

# Hmm, complex. Let me think differently.

# val^1237 ≡ -1 mod N.
# val^1237 ≡ -1 mod qi for all qi.
# val has order 2474 mod each qi.
# 
# Now: val^2 has order 1237 mod each qi. val^2 is in <2 mod qi> for each qi.
# So val^2 is in <2> mod N.
# val^2 = 2^j for some j in [0, 1236].

# Let's find j via BSGS:
log(f'برای a با (a/N) = -1 (مثل 5، 19، 23، ...):')
log(f'  val = a^((N-1)/2474)')
log(f'  val^1237 = -1 (یعنی val has order 2474)')
log(f'  val^2 in <2>, so val^2 = 2^j for some j')
log(f'  پیدا کردن j با BSGS:')
log(f'')

# Build BSGS table for <2> of order 1237
m_bsgs = int(math.isqrt(1237)) + 1
table = {}
val_bsgs = 1
for j in range(m_bsgs):
    table[val_bsgs] = j
    val_bsgs = (val_bsgs * 2) % N
inv_2m = int(invert(powmod(2, m_bsgs, N), N))

def find_discrete_log(target, N, m, table, inv_2m):
    gamma = target
    for k in range(m + 1):
        if gamma in table:
            return (k * m + table[gamma]) % 1237
        gamma = (gamma * inv_2m) % N
    return None

# For each a with (a/N) = -1:
for a in [5, 19, 23, 37, 41, 43, 47, 89, 101, 103, 107, 109, 113, 127, 137, 139]:
    if jacobi(a, N) != -1:
        continue
    val = int(powmod(a, exp, N))
    val_squared = (val * val) % N
    # Find j with 2^j ≡ val_squared mod N
    j = find_discrete_log(val_squared, N, m_bsgs, table, inv_2m)
    log(f'  a={a}: val^2 = 2^j with j = {j}')
    if j is not None:
        # val^2 = 2^j. So val ≡ ± 2^(j/2) mod N? Only if j even.
        # Actually: val^2 = 2^j, so (val * 2^(-j/2))^2 = 1 mod N
        # If j even: 2^(-j/2) makes sense.
        if j % 2 == 0:
            # val = ± 2^(j/2) mod N
            # Compute 2^(j/2) mod N
            half_j = j // 2
            two_half_j = int(powmod(2, half_j, N))
            # val ≡ ± two_half_j mod N
            # Check both:
            if val == two_half_j:
                log(f'    val = +2^{half_j}')
            elif val == N - two_half_j:
                log(f'    val = -2^{half_j}')
            else:
                # val ≢ ± 2^(j/2) mod N! 
                # But (val - 2^(j/2))(val + 2^(j/2)) ≡ 0 mod N
                # If val ≢ ± 2^(j/2) mod N, then one of (val - 2^(j/2)) or (val + 2^(j/2))
                # is divisible by some qi but not all → factor!
                log(f'    val ≢ ± 2^{half_j}! این به ما فاکتور می‌دهد!')
                g1 = gcd(val - two_half_j, N)
                g2 = gcd(val + two_half_j, N)
                log(f'    gcd(val - 2^{half_j}, N) = {g1}')
                log(f'    gcd(val + 2^{half_j}, N) = {g2}')
                if 1 < g1 < N:
                    log(f'    >>> FACTOR: {g1}')
                    log(f'    is_prime: {is_prime(g1)}')
                    cof = N // g1
                    log(f'    cofactor: ' + str(cof)[:60] + '...')
                    if int(M) % g1 == 0:
                        log(f'    ✓ REAL FACTOR!')
                        sys.exit(0)
                if 1 < g2 < N:
                    log(f'    >>> FACTOR: {g2}')
                    log(f'    is_prime: {is_prime(g2)}')
                    cof = N // g2
                    log(f'    cofactor: ' + str(cof)[:60] + '...')
                    if int(M) % g2 == 0:
                        log(f'    ✓ REAL FACTOR!')
                        sys.exit(0)
        else:
            # j is odd. val^2 = 2^j but j odd. 
            # We can't take 2^(j/2). But maybe:
            # val^2 = 2^j = 2 * 2^(j-1) = 2 * (2^((j-1)/2))^2
            # So val^2 / (2^((j-1)/2))^2 = 2 mod N
            # (val / 2^((j-1)/2))^2 = 2 mod N
            # This means val / 2^((j-1)/2) is a square root of 2!
            # We know sqrt(2) = 2^619 mod N (since 2 has order 1237, sqrt(2) = 2^((1237+1)/2) = 2^619).
            # Actually wait: 2^619 squared = 2^1238 = 2 * 2^1237 = 2 * 1 = 2 mod N. Yes.
            # So sqrt(2) = ± 2^619 mod N.
            # Then: val / 2^((j-1)/2) ≡ ± 2^619 mod N
            # val ≡ ± 2^619 * 2^((j-1)/2) = ± 2^(619 + (j-1)/2) mod N
            # 
            # If val matches one of these → consistent, no factor.
            # If val matches neither → factor!
            
            half_j_minus_1 = (j - 1) // 2
            exponent_target = (619 + half_j_minus_1) % 1237
            expected_pos = int(powmod(2, exponent_target, N))
            expected_neg = N - expected_pos
            if val == expected_pos:
                log(f'    val = +2^{exponent_target} (consistent, no factor)')
            elif val == expected_neg:
                log(f'    val = -2^{exponent_target} (consistent, no factor)')
            else:
                log(f'    val inconsistent! Finding factor:')
                g1 = gcd(val - expected_pos, N)
                g2 = gcd(val + expected_pos, N)
                log(f'    gcd(val - 2^{exponent_target}, N) = {g1}')
                log(f'    gcd(val + 2^{exponent_target}, N) = {g2}')
                if 1 < g1 < N:
                    log(f'    >>> FACTOR: {g1}')
                    log(f'    is_prime: {is_prime(g1)}')
                    cof = N // g1
                    log(f'    cofactor: ' + str(cof)[:60] + '...')
                    if int(M) % g1 == 0:
                        log(f'    ✓ REAL FACTOR!')
                        sys.exit(0)
                if 1 < g2 < N:
                    log(f'    >>> FACTOR: {g2}')
                    log(f'    is_prime: {is_prime(g2)}')
                    cof = N // g2
                    log(f'    cofactor: ' + str(cof)[:60] + '...')
                    if int(M) % g2 == 0:
                        log(f'    ✓ REAL FACTOR!')
                        sys.exit(0)

log(f'')
log(f'=== پایان ===')
