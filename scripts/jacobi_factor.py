#!/usr/bin/env python3
"""
DEEP ANALYSIS based on the Jacobi discovery:
- (5/N) = -1, (19/N) = -1, (23/N) = -1, (37/N) = -1, (41/N) = -1, (43/N) = -1, (47/N) = -1, (89/N) = -1
- (2/N) = +1, (3/N) = +1, etc.

For N = q1 * q2 * ... * qk (prime factorization), (a/N) = product (a/qi).
(a/N) = -1 means odd number of qi have (a/qi) = -1.

This is HUGELY informative! 

Key reasoning:
- For q | F2 (so q ≡ 1 mod 2474), (2/q) = +1 (since 2 is a quadratic residue mod q when q ≡ ±1 mod 8, 
  and q ≡ 1 mod 2474 = 1 mod 2, and the cases q ≡ 1 mod 8 or q ≡ 7 mod 8 give (2/q) = +1).

- The 8 primes with (a/N) = -1 (5, 19, 23, 37, 41, 43, 47, 89) each give us info: 
  for SOME qi, (a/qi) = -1, for OTHERS, (a/qi) = +1.

- For different a values, the partition of qi into "has (a/qi)=+1" vs "has (a/qi)=-1" differs.
- If we can find a value a* where the partitions are inconsistent (e.g., 
  (5/q1) = +1, (19/q1) = -1, but (5/q2) = -1, (19/q2) = +1), then:
  gcd(5^((N-1)/2) + 5^(...) - 1, N) might give a factor (Chinese Remainder difference).

Actually, a cleaner approach: Tonelli-Shanks sqrt computation can fail/succeed differently 
for different primes qi. We already tried this and got "TS failed on composite N" — 
but we didn't extract the factor from the failure!

Let me redo this with the right approach: 
- For (a/N) = -1, try to compute sqrt(a) mod N using TS.
- TS on composite N where the order of t = a^Q differs between primes qi will fail 
  partway through. The failure point gives gcd > 1!

Wait, we tried this before. Let me check what happened. Let me try again more carefully.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod, invert, jacobi, isqrt
import math
import time
import random
from pathlib import Path

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1
N = int(F2)

LOG = Path('/home/z/my-project/download/jacobi_factor.log')
LOG.write_text('')
def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')

log(f'=== استخراج فاکتور از تفاوت Jacobi ===')
log(f'N = F2, {len(str(N))} digits')
log(f'')

# Step 1: For each a with (a/N) = -1, try TS and look for factor extraction points.
# v_2(N-1):
Nm1 = N - 1
v2 = 0
temp = Nm1
while temp % 2 == 0:
    v2 += 1
    temp //= 2
Q_ts = Nm1 >> v2
log(f'v_2(N-1) = {v2}, Q = (N-1)/2^{v2}')
log(f'')

# For each a with (a/N) = -1, try TS
# Note: (a/N) = -1 means there is NO sqrt of a mod N. But TS will fail at some step.
# When it fails, it gives a non-trivial gcd.

# But (a/N) = -1 means a is not a QR mod N, so no sqrt exists. TS will detect this.
# The standard TS procedure computes t = a^Q. If t = 1, sqrt = a^((Q+1)/2).
# If t = -1 (= N-1), no sqrt (since N-1 mod each qi might be -1 for one but not the other).
# Wait — if (a/N) = -1, then a^((N-1)/2) ≡ -1 mod N. So a^((N-1)/2) + 1 ≡ 0 mod N. Trivial.

# But: a^((N-1)/2) = a^(Q * 2^v) = (a^Q)^(2^v).
# After v2 squarings of a^Q, we get -1 mod N.
# At SOME intermediate squaring i, the value becomes -1 mod some qi but +1 mod others.
# That's where gcd gives a factor!

# Algorithm: 
#   t = a^Q mod N
#   for i in 0..v2-1:
#     t = t^2 mod N  (now t = a^(Q*2^(i+1)))
#     if t == 1: succeeded, sqrt exists from here
#     if t == -1 (N-1): failed (no sqrt)
#     else: at boundary, compute gcd(t - 1, N) and gcd(t + 1, N) for factor

log(f'تلاش: برای هر a با (a/N) = -1، محاسبه‌ی t = a^Q و چک کردن gcd در هر مرحله')

problematic_as = [5, 19, 23, 37, 41, 43, 47, 89, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]
# Add more primes that have (a/N) = -1
all_test_as = []
for a in range(2, 1000):
    if is_prime(a):
        if jacobi(a, N) == -1:
            all_test_as.append(a)
log(f'تعداد اعداد اول با (a/N) = -1 در [2, 1000): {len(all_test_as)}')
log(f'نمونه‌ها: {all_test_as[:20]}')
log(f'')

factor_found = None
for a in all_test_as[:50]:  # test first 50
    # Compute t = a^Q mod N
    t = int(powmod(a, Q_ts, N))
    
    if t == 1:
        # a is "QR mod all qi" with ord(a^Q) = 1 mod all qi — but (a/N) = -1 contradicts
        # Unless (a/N) computed via Euler differs from product. Let's check.
        # (a/N) = a^((N-1)/2) mod N (Euler)
        # Compute that
        euler = int(powmod(a, Nm1 // 2, N))
        if euler != N - 1:
            log(f'  a={a}: t=1, Euler = {euler} ≠ -1, inconsistency')
            g = gcd(euler + 1, N)
            if 1 < g < N:
                log(f'    >>> FACTOR from Euler: {g}')
                factor_found = g
                break
        continue
    
    # Now we have t = a^Q. Try squaring chain.
    cur = t
    found_at = None
    for i in range(v2 + 1):
        if cur == 1:
            # succeeded — sqrt exists with this a
            break
        if cur == N - 1:
            # all qi gave -1 at this point — no factor here
            break
        # Check gcd
        g1 = gcd(cur - 1, N)
        g2 = gcd(cur + 1, N)
        if 1 < g1 < N:
            log(f'  a={a}: at i={i}, gcd(t-1, N) = {g1}')
            found_at = ('t-1', g1, i)
            break
        if 1 < g2 < N:
            log(f'  a={a}: at i={i}, gcd(t+1, N) = {g2}')
            found_at = ('t+1', g2, i)
            break
        cur = (cur * cur) % N
    
    if found_at:
        kind, factor, i = found_at
        log(f'  >>> FACTOR FOUND with a={a}: {factor} (at squaring step {i})')
        log(f'  is_prime(factor): {is_prime(factor)}')
        cof = N // factor
        log(f'  cofactor: ' + str(cof)[:60] + '... (' + str(len(str(cof))) + ' digits')
        log(f'  is_prime(cofactor): {is_prime(cof)}')
        if int(M) % factor == 0:
            log(f'  ✓ REAL FACTOR of M(1237)!')
        factor_found = factor
        break

if not factor_found:
    log(f'  هیچ فاکتور از TS-failures پیدا نشد')
log(f'')

# ============================================================
# Better approach: use Tonelli-Shanks with PROPER factor extraction
# ============================================================
log(f'=== روش پیشرفته: TS با factor extraction ===')

# Standard Tonelli-Shanks for finding sqrt of a mod N (composite).
# When TS fails because composite, intermediate values give factors.

# Pseudocode:
# Input: a, N (with (a/N) = +1 ideally)
# Output: sqrt of a mod N, OR a non-trivial factor of N if TS fails

def tonelli_shanks_composite(a, N, v2, Q):
    """TS for sqrt of a mod N (composite). Returns (sqrt, factor) where one is None."""
    # Initialize
    M_ts = v2
    # Find a non-residue z (i.e., (z/N) = -1)
    z = None
    for zz in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if jacobi(zz, N) == -1:
            z = zz
            break
    if z is None:
        return None, None
    c_ts = int(powmod(z, Q, N))
    t_ts = int(powmod(a, Q, N))
    R_ts = int(powmod(a, (Q + 1) // 2, N))
    
    # Track all intermediate values for factor extraction
    for iteration in range(200):
        if t_ts == 0:
            return 0, None  # sqrt is 0 (trivial)
        if t_ts == 1:
            return R_ts, None  # success
        
        # Find least i with t^(2^i) = 1
        i_ts = None
        temp = t_ts
        for ii in range(1, M_ts + 1):
            temp = (temp * temp) % N
            # Check gcd at each step
            g = gcd(temp - 1, N)
            if 1 < g < N:
                return None, g  # factor found!
            g = gcd(temp + 1, N)
            if 1 < g < N:
                return None, g
            if temp == 1:
                i_ts = ii
                break
            if temp == 0:
                g = gcd(t_ts, N)
                if 1 < g < N:
                    return None, g
                break
        
        if i_ts is None:
            # TS failed at composite level — try gcd of various intermediates
            for val in [R_ts - 1, R_ts + 1, c_ts - 1, c_ts + 1, t_ts - 1, t_ts + 1]:
                g = gcd(abs(val) % N, N)
                if 1 < g < N:
                    return None, g
            return None, None
        
        b_ts = int(powmod(c_ts, 1 << (M_ts - i_ts - 1), N))
        M_ts = i_ts
        c_ts = (b_ts * b_ts) % N
        t_ts = (t_ts * c_ts) % N
        R_ts = (R_ts * b_ts) % N
    
    return None, None

# Try with several a values that have (a/N) = +1 (so sqrt should exist)
log(f'برای a های با (a/N) = +1، TS را امتحان می‌کنیم:')
for a in [2, 3, 7, 11, 13, 17, 29, 31, 53, 59, 61, 67, 71, 73, 79, 83, 97]:
    j = jacobi(a, N)
    if j != 1:
        continue
    sqrt_a, factor = tonelli_shanks_composite(a, N, v2, Q_ts)
    if factor:
        log(f'  a={a}: ✓✓✓ FACTOR FOUND: {factor}')
        log(f'  is_prime: {is_prime(factor)}')
        cof = N // factor
        log(f'  cofactor: ' + str(cof)[:60] + '... (' + str(len(str(cof))) + ' digits')
        if int(M) % factor == 0:
            log(f'  ✓ REAL FACTOR of M(1237)!')
            sys.exit(0)
    elif sqrt_a is not None:
        log(f'  a={a}: sqrt = {str(sqrt_a)[:30]}... (TS succeeded, no factor)')
    else:
        log(f'  a={a}: TS inconclusive')
log(f'')

# Try with a values that have (a/N) = -1 (these should FAIL TS in interesting way)
log(f'برای a های با (a/N) = -1، TS احتمالاً شکست می‌خورد و فاکتور می‌دهد:')
for a in [5, 19, 23, 37, 41, 43, 47, 89, 101, 103, 107]:
    sqrt_a, factor = tonelli_shanks_composite(a, N, v2, Q_ts)
    if factor:
        log(f'  a={a}: ✓✓✓ FACTOR FOUND: {factor}')
        log(f'  is_prime: {is_prime(factor)}')
        cof = N // factor
        log(f'  cofactor: ' + str(cof)[:60] + '... (' + str(len(str(cof))) + ' digits')
        if int(M) % factor == 0:
            log(f'  ✓ REAL FACTOR of M(1237)!')
            sys.exit(0)
    elif sqrt_a is not None:
        log(f'  a={a}: sqrt = {str(sqrt_a)[:30]}... (TS succeeded, no factor)')
    else:
        log(f'  a={a}: TS inconclusive')

log(f'')
log(f'=== پایان ===')
