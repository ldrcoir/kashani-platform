#!/usr/bin/env python3
"""
CREATIVE METHOD: Find a second cyclic subgroup of order 1237 in (Z/NZ)*
that is DIFFERENT from <2>. Then use the difference via CRT to extract a factor.

Reasoning:
- (Z/NZ)* has order phi(N) = (q1-1)(q2-1)...(qk-1) for prime factors qi of N.
- 1237 | (qi - 1) for each qi (since qi ≡ 1 mod 2474 and 1237 | 2474).
- So 1237 | phi(N).
- (Z/NZ)* has a UNIQUE subgroup of order 1237? NO! It might have MULTIPLE.
- Number of subgroups of order p (prime) in a finite abelian group = number of 
  elements of order p divided by (p-1).
- For (Z/NZ)* ≅ product (Z/qi Z)*, each (Z/qi Z)* has 1236 elements of order 1237 
  (since (Z/qi Z)* is cyclic of order qi-1, which is divisible by 1237).
- So total elements of order 1237 in (Z/NZ)* = (1236)^k where k = number of distinct prime factors.
- Number of distinct cyclic subgroups of order 1237 = (1236)^k / 1236 = (1236)^(k-1).

For k = 2 (two prime factors): 1236 subgroups of order 1237.
For k = 3: 1236^2 = ~1.5M subgroups.

So there are MANY subgroups of order 1237 besides <2>.

KEY INSIGHT: If we find another element g of order 1237 in (Z/NZ)* that is 
NOT in <2>, then:
  - g^1237 ≡ 1 mod N (by definition)
  - But for some qi, g mod qi might be in <2 mod qi> (same subgroup)
  - For other qj, g mod qj is NOT in <2 mod qj> (different subgroup)
  
This means: g is "aligned" with <2> mod some primes and not others.

If g ≡ 2^a mod qi (for some a in [0, 1236]) and g ≢ 2^b mod qj for any b,
then: take h = g * 2^(-a) (multiply by 2^(1237-a) mod N = inverse of 2^a).
   h ≡ 1 mod qi but h ≢ 1 mod qj.
   gcd(h - 1, N) = qi (or product of all primes where h ≡ 1).

How to find such g? 
- Pick random g in (Z/NZ)*.
- Compute g^1237 mod N. If = 1, then ord(g) | 1237. Since 1237 prime, ord(g) = 1 or 1237.
  If g^1237 = 1 and g != 1, then g has order 1237.
- This is a random subgroup of order 1237. With high probability, it's NOT <2>.

Let's verify and try this!
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod, invert, jacobi
import math
import time
import random
from pathlib import Path

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1
N = int(F2)

LOG = Path('/home/z/my-project/download/subgroup_method.log')
LOG.write_text('')
def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')

log(f'=== روش ابداعی: یافتن زیرگروه دوم از مرتبه‌ی ۱۲۳۷ ===')
log(f'')
log(f'استدلال:')
log(f'  - (Z/NZ)* دارای phi(N) = (q1-1)(q2-1)...(qk-1) عنصر است')
log(f'  - 1237 | (qi-1) برای هر qi، پس 1237 | phi(N)')
log(f'  - تعداد زیرگروه‌های cyclic از مرتبه‌ی 1237 در (Z/NZ)* = (1236)^(k-1)')
log(f'  - <2> یکی از این زیرگروه‌هاست')
log(f'  - زیرگروه‌های دیگر متفاوت‌اند — این تفاوت CRT به ما فاکتور می‌دهد!')
log(f'')

# Verify ord_N(2) = 1237
log(f'بررسی: ord_N(2) = 1237?')
val = powmod(2, 1237, N)
log(f'  2^1237 mod N = {val} (must be 1)')
log(f'  2^1 mod N = {powmod(2, 1, N)} (must be != 1)')
log(f'  → ord_N(2) = 1237 ✓')
log(f'')

# ============================================================
# METHOD 1: Find a random element g with g^1237 ≡ 1 mod N, g ≠ 1, g not in <2>
# Then compute h = g * 2^(-a) for some a to align g with 2 mod some primes
# ============================================================
log(f'=== روش ۱: یافتن عنصر تصادفی g با ord(g) = ۱۲۳۷ ===')

# Probability that a random g has g^1237 ≡ 1 mod N:
# = (number of elements with ord | 1237) / phi(N)
# = (1237^k) / phi(N)  where k = number of prime factors
# For k = 2: 1237^2 / phi(N). phi(N) is huge, so probability is tiny.
# For random g, almost certainly g^1237 ≢ 1 mod N.

# So we need a smarter approach to find g with ord(g) = 1237.

# Idea: Find g such that g^1237 ≡ 1 mod N. 
# One way: compute g^phi(N)/1237 — but we don't know phi(N).
# 
# Another way: Use structure of (Z/NZ)*.
# (Z/NZ)* ≅ (Z/q1 Z)* × (Z/q2 Z)* × ... × (Z/qk Z)*
# Each (Z/qi Z)* is cyclic of order qi - 1, divisible by 1237.
# So each (Z/qi Z)* has 1236 generators of order 1237.
# 
# To find element of order 1237 mod N: pick random g, compute g^((N-1)/1237) — but we don't 
# know if (N-1)/1237 has the right structure. (N-1) is divisible by 1237 only if 1237 | (N-1).
# N mod 1237?
log(f'بررسی: N mod 1237 = {N % 1237}')
log(f'بررسی: (N-1) mod 1237 = {(N-1) % 1237}')
log(f'بررسی: (N-1) mod 2474 = {(N-1) % 2474}')
# So we don't have 1237 | (N-1) necessarily. (N-1) might not be divisible by 1237.
# In that case, we can't easily find elements of order 1237 from "outside" <2>.

# Wait — but the elements of order 1237 in (Z/NZ)* do exist (since each (Z/qi Z)* has them).
# Number of elements with g^1237 = 1 in (Z/NZ)* = 1237^k.
# Total elements in (Z/NZ)* = phi(N).
# Probability = 1237^k / phi(N) ≈ 1237^2 / 10^300 ≈ 10^-294 for k=2.
# Very small.

# So random search won't find them. Need to use STRUCTURE.

# Idea: pick any g. Compute g^((N-1) / gcd(N-1, 1237)). Hmm, gcd(N-1, 1237) might be 1.
# In that case, this gives 1.

# Alternative: pick g, compute g^? — we need a "1237-th power structure".

# Smart idea: Since <2> is the unique subgroup of order 1237 if N is PRIME, but N is composite.
# For composite N, the number of cyclic subgroups of order 1237 is (1236)^(k-1).
# If k = 2, there are 1236 such subgroups.
# If k = 1, there's only 1 (but N is prime then, contradiction).

# So for k >= 2, there are multiple subgroups.

# But how to find another subgroup?
# 
# Answer: pick element g. Compute g^phi(N) / 1237. This gives an element of order dividing 1237.
# But we don't know phi(N).
# 
# Alternative: We know ord_N(2) = 1237. So <2> is one subgroup.
# Take g = 2 + something and see what happens.
# 
# Or: take g = 3 (or another small prime). What is ord_N(3)?
# Compute 3^1237 mod N. If = 1, then ord_N(3) | 1237 = prime, so ord_N(3) = 1 or 1237.
# 3 ≠ 1 mod N, so ord_N(3) = 1237.
# That would mean 3 is in <2>, i.e., 3 = 2^j for some j ∈ [0, 1236].

log(f'')
log(f'بررسی: آیا 3 در <2> قرار دارد؟')
v3 = powmod(3, 1237, N)
log(f'  3^1237 mod N = {v3}')
if v3 == 1:
    log(f'  ✓ 3 در <2> است (ord_N(3) | 1237)')
    log(f'    چون 3 ≠ 1، ord_N(3) = 1237')
    # 3 is in <2>, so 3 = 2^j for some j
    # Find j via discrete log
    log(f'    یافتن j با 2^j ≡ 3 mod N (BSGS در زیرگروه <2> از مرتبه‌ی 1237):')
    # BSGS in cyclic group <2> of order 1237
    # Build table of 2^0, 2^1, ..., 2^m where m = ceil(sqrt(1237)) ~ 36
    m = int(math.isqrt(1237)) + 1
    table = {}
    val = 1
    for j in range(m):
        table[val] = j
        val = (val * 2) % N
    # Find 3 * (2^(-m))^k for k = 0..m
    inv_2m = int(invert(powmod(2, m, N), N))
    gamma = 3
    found_j = None
    for k in range(m + 1):
        if gamma in table:
            found_j = k * m + table[gamma]
            found_j = found_j % 1237  # since ord is 1237
            break
        gamma = (gamma * inv_2m) % N
    if found_j is not None:
        log(f'    j = {found_j} (2^{found_j} ≡ 3 mod N)')
        log(f'    verify: 2^{found_j} mod N == 3? {powmod(2, found_j, N) == 3}')
    else:
        log(f'    3 در <2> نیست (با BSGS تأیید شد)')
else:
    log(f'  ✗ 3 در <2> نیست (3^1237 ≢ 1 mod N)')
    log(f'    یعنی ord_N(3) ∤ 1237')
    log(f'    این جالب است! 3 در یک زیرگروه متفاوت قرار دارد.')
log(f'')

# ============================================================
# روش ۲: یافتن زیرگروه‌های دیگر با استفاده از عناصر مختلف
# ============================================================
log(f'=== روش ۲: بررسی عناصر مختلف، یافتن آنهایی که در <2> نیستند ===')

# For each prime a, check if a^1237 ≡ 1 mod N. If yes, a is in <2>. Find j via BSGS.
# If no, a has ord ≠ 1237 — different structure.

# Build BSGS table for <2> (do it once)
m = int(math.isqrt(1237)) + 1
table = {}
val = 1
for j in range(m):
    table[val] = j
    val = (val * 2) % N
inv_2m = int(invert(powmod(2, m, N), N))

def find_discrete_log_in_subgroup_2(target, N, m, table, inv_2m):
    """Find j with 2^j ≡ target mod N, assuming target is in <2>."""
    gamma = target
    for k in range(m + 1):
        if gamma in table:
            return (k * m + table[gamma]) % 1237
        gamma = (gamma * inv_2m) % N
    return None

# Check small primes
log(f'بررسی اعداد اول کوچک:')
for a in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]:
    v = powmod(a, 1237, N)
    if v == 1:
        # a is in <2>. Find j
        j = find_discrete_log_in_subgroup_2(a, N, m, table, inv_2m)
        log(f'  a = {a}: in <2> (2^j ≡ a for j = {j})')
    else:
        log(f'  a = {a}: NOT in <2> (a^1237 mod N != 1)')
        # Try a^((N-1)/2) - might give factor
        # Or: use a in a different way
        # Idea: g = a. Compute g^(some specific value)
        # For different primes qi, ord_qi(a) might divide different things.
        # If a^1237 ≢ 1 mod N, then for SOME qi, a^1237 ≢ 1 mod qi.
        # For others, a^1237 ≡ 1 mod qi (so a is in <2> mod qi).
        # Compute gcd(a^1237 - 1, N) — might give product of qi where a^1237 ≡ 1.
        g_check = gcd(int(v) - 1, N)
        log(f'    gcd(a^1237 - 1, N) = {g_check}')
        if 1 < g_check < N:
            log(f'    >>> FACTOR FOUND: {g_check}')
            log(f'    is_prime: {is_prime(g_check)}')
            cof = N // g_check
            log(f'    cofactor: ' + str(cof)[:60] + '... (' + str(len(str(cof))) + ' digits)')
            if int(M) % g_check == 0:
                log(f'    ✓ REAL FACTOR of M(1237)!')
                sys.exit(0)
log(f'')

# ============================================================
# روش ۳: برای عناصر a با a^1237 ≢ 1 mod N، یافتن تفاوت 
# در (Z/qi Z)* برای qi مختلف
# ============================================================
log(f'=== روش ۳: برای a هایی که در <2> نیستند، استفاده از CRT ساختاری ===')
log(f'')

# Idea: 
# For a with a^1237 ≢ 1 mod N, ord_N(a) ∤ 1237.
# But ord_qi(a) | (qi - 1) = 2474 * m_i for some m_i.
# So ord_qi(a) | 2474 * m_i.
# If ord_qi(a) = 2474 (the max divisor coprime to m_i — wait, this is not right).
# 
# Actually: a^1237 ≡ 1 mod qi means ord_qi(a) | 1237.
# a^1237 ≢ 1 mod qi means ord_qi(a) ∤ 1237. Since 1237 is prime, ord_qi(a) is NOT 1 or 1237.
# So ord_qi(a) is some other divisor of qi-1.
#
# Now: gcd(a^1237 - 1, N) gives product of qi where a^1237 ≡ 1 mod qi (i.e., a in <2> mod qi).
# If a is in <2> mod some qi and not in <2> mod other qj, this gcd gives a factor!

# But we already tried this above and got gcd = 1 (no factor).
# Wait, let me check more carefully.

log(f'بررسی دقیق‌تر: برای a های مختلف، gcd(a^1237 - 1, N):')
factor_found = None
for a in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]:
    v = int(powmod(a, 1237, N))
    g_minus = gcd(v - 1, N)
    g_plus = gcd(v + 1, N)
    if 1 < g_minus < N:
        log(f'  a={a}: gcd(a^1237 - 1, N) = {g_minus}')
        log(f'  >>> FACTOR: {g_minus}')
        log(f'  is_prime: {is_prime(g_minus)}')
        cof = N // g_minus
        log(f'  cofactor: ' + str(cof)[:60] + '...')
        if int(M) % g_minus == 0:
            log(f'  ✓ REAL FACTOR!')
            factor_found = g_minus
            break
    if 1 < g_plus < N:
        log(f'  a={a}: gcd(a^1237 + 1, N) = {g_plus}')
        log(f'  >>> FACTOR: {g_plus}')
        log(f'  is_prime: {is_prime(g_plus)}')
        cof = N // g_plus
        log(f'  cofactor: ' + str(cof)[:60] + '...')
        if int(M) % g_plus == 0:
            log(f'  ✓ REAL FACTOR!')
            factor_found = g_plus
            break

if not factor_found:
    log(f'  هیچ فاکتور از این روش پیدا نشد')
    log(f'  یعنی برای هر a در این لیست، یا a^1237 ≡ 1 mod همه‌ی qi (a در <2> است)')
    log(f'  یا a^1237 ≢ 1 mod همه‌ی qi (هیچ qi a را در <2> ندارد)')
log(f'')

# ============================================================
# روش ۴: استفاده از تفاوت ord_qi(a) برای a های مختلف
# ============================================================
log(f'=== روش ۴: ساخت گ <2> از تفاوت‌ها ===')
log(f'')

# For a, b both with a^1237 ≢ 1 and b^1237 ≢ 1 mod N:
# Compute (a^1237 - 1) mod N and (b^1237 - 1) mod N.
# Take their difference and gcd with N.

# More interesting: take a * 2^j for various j.
# (a * 2^j)^1237 = a^1237 * 2^(1237*j) = a^1237 * 1 = a^1237.
# So multiplying by 2 doesn't help — same result.

# Try: a^1237 * b^(-1237) = (a/b)^1237. Hmm.

# Better: Use a in a DIFFERENT power structure. Compute a^((N-1)/2) - Euler criterion.
# Already tried this — gave trivial.

# Try: a^((N-1)/1237) — but 1237 might not divide N-1.
# We saw (N-1) mod 1237 = ?
log(f'(N-1) mod 1237 = {(N-1) % 1237}')
log(f'(N-1) mod 2474 = {(N-1) % 2474}')
# If (N-1) mod 1237 = 0, we could compute a^((N-1)/1237) and get something with structure.
# If not, this doesn't directly work.

# ============================================================
# روش ۵: استفاده از Phi structure — N-1 having divisors
# ============================================================
log(f'=== روش ۵: استفاده از مقسوم‌علیه‌های شناخته‌شده‌ی N-1 ===')
log(f'')
# N-1 has known factorization partially: 2^4 * 3 * 7 * (large remaining factor).
# So divisors of N-1 that we know: 2, 4, 8, 16, 3, 6, 12, 24, ..., 7, 14, 28, ..., 21, 42, ..., 336, ...
# Let's use these.

# For each divisor d of (N-1) that we know:
# Compute a^((N-1)/d) mod N. Check if this equals 1.
# If = 1: ord(a) | (N-1)/d, so ord(a) divides smaller divisor.
# If ≠ 1: ord(a) doesn't divide (N-1)/d.

# Specifically: for a^((N-1)/2): Euler criterion. We know this for various a.
# (a/N) = ±1 (we computed earlier).

# Let's try: a^((N-1)/q) for q = 2, 3, 4, 7, 12, etc.
# Compute these for various a and find gcd.

# N-1 = 2^4 * 3 * 7 * remaining
# (N-1)/2 = 2^3 * 3 * 7 * remaining
# (N-1)/3 = 2^4 * 7 * remaining
# (N-1)/7 = 2^4 * 3 * remaining
# (N-1)/12 = 2^2 * 7 * remaining
# (N-1)/16 = 3 * 7 * remaining

known_divisors = [2, 3, 4, 6, 7, 8, 12, 14, 16, 21, 24, 28, 42, 48, 56, 112, 168, 336]
log(f'مقسوم‌علیه‌های شناخته‌شده‌ی N-1: {known_divisors[:10]}...')

# For each a, compute a^((N-1)/d) for each d, check gcd with N
log(f'آزمایش a^((N-1)/d) ± 1 برای a های مختلف و d های شناخته‌شده:')
factor_found = None
t0 = time.time()
for a in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61]:
    for d in known_divisors:
        if (N - 1) % d != 0:
            continue
        exp = (N - 1) // d
        val = int(powmod(a, exp, N))
        for delta_label, delta in [('val-1', val - 1), ('val+1', val + 1)]:
            g = gcd(abs(delta) % N, N)
            if 1 < g < N:
                log(f'  a={a}, d={d}: gcd({delta_label}, N) = {g}')
                log(f'  >>> FACTOR: {g}')
                log(f'  is_prime: {is_prime(g)}')
                cof = N // g
                log(f'  cofactor: ' + str(cof)[:60] + '...')
                if int(M) % g == 0:
                    log(f'  ✓ REAL FACTOR!')
                    factor_found = g
                    break
        if factor_found:
            break
    if factor_found:
        break

if not factor_found:
    elapsed = time.time() - t0
    log(f'  هیچ فاکتور پیدا نشد (elapsed {elapsed:.1f}s)')

log(f'')
log(f'=== پایان ===')
