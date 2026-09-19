#!/usr/bin/env python3
"""
CREATIVE APPROACH: Mersenne-Embedded ECM

Reasoning:
1. N = F2 = M(1237)/F1, so 2^1237 ≡ 1 mod N. The element 2 in (Z/NZ)* has order 1237 (prime).
2. <2> is a cyclic subgroup of order 1237 in (Z/NZ)*.
3. We can use 2 as a "structural seed" for factoring.

Key Insight - A NEW factoring approach via subgroup structure:

For each prime p | N, the Chinese Remainder Theorem gives:
   (Z/NZ)* ≅ (Z/F1_part)* × (Z/p)* × ...
   <2> mod N corresponds to <2 mod F1_part> × <2 mod p> × ...
   
If we can find an element g ∈ (Z/NZ)* such that:
   - g ≡ 1 mod F1_part  (i.e., g ≡ 1 mod N/p_remaining or specific factor)
   - g ≠ 1 mod p for some other prime p | N
Then gcd(g - 1, N) gives a non-trivial factor.

The element 2 has order 1237 mod N (since F2 = N divides M(1237) but M doesn't divide 
anything smaller like M(1)=1 or M(k) for k < 1237 — well, actually 2^1 = 2 ≠ 1 mod N, 
so order is exactly 1237).

This means: <2> mod N is cyclic of order 1237.

For N = p1 * p2 * ... * pk (prime factorization):
   2 mod N corresponds to (2 mod p1, 2 mod p2, ..., 2 mod pk) via CRT
   2 has order 1237 mod each pi (since ord_pi(2) | 1237 = prime, and ord_pi(2) != 1).
   So <2> mod N has order lcm(1237, ..., 1237) = 1237. Consistent.

Now: in <2> mod N, all elements are of the form 2^k for k ∈ [0, 1236].
If we pick two distinct elements 2^a and 2^b with a, b ∈ [0, 1236]:
   2^a ≡ 2^b mod some prime pi  iff  a ≡ b mod 1237  (impossible if a ≠ b in [0, 1236])
So distinct elements of <2> are distinct mod each prime factor.

So <2> doesn't immediately give a factor. We need to LEAVE the cyclic group.

NEW IDEA: Use <2> as a starting point, then move to a larger group via:
   - Multiplication by other elements
   - Polynomial operations: take 2^k, compute polynomial in 2^k, see if gcd with N
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

LOG = Path('/home/z/my-project/download/mersenne_embedded.log')
LOG.write_text('')
def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')

log(f'=== روش ابداعی: Mersenne-Embedded Factoring ===')
log(f'N = F2, {len(str(N))} digits')
log(f'')
log(f'استدلال:')
log(f'  1. N | M(1237) → 2^1237 ≡ 1 mod N')
log(f'  2. 1237 prime → ord_N(2) ∈ {{1, 1237}}')
log(f'  3. 2 ≠ 1 mod N → ord_N(2) = 1237')
log(f'  4. <2> cyclic subgroup of (Z/NZ)* of order 1237')
log(f'  5. CRT: (Z/NZ)* ≅ (Z/p1)* × (Z/p2)* × ... (for pi | N)')
log(f'  6. 2 in CRT has order 1237 mod each pi (pi | F2 means ord_pi(2) | 1237 = prime, ≠ 1)')
log(f'')

# Verify ord_N(2) = 1237
log(f'بررسی: ord_N(2) = ?')
log(f'  2^1237 mod N = {powmod(2, 1237, N)} (should be 1)')
# Check smaller divisors of 1237: 1237 is prime, so only divisor is 1
# 2^1 = 2 ≠ 1 mod N (since N > 1)
log(f'  2^1 mod N = {powmod(2, 1, N)} ≠ 1')
log(f'  → ord_N(2) = 1237 confirmed')
log(f'')

# ============================================================
# METHOD A: Use <2> as generator, build polynomial
# ============================================================
log(f'=== روش A: چندجمله‌ای در 2 mod N ===')
log(f'ایده: محاسبه‌ی polynomial f(2) با f دارای خاصیت ساختاری')
log(f'')

# Idea: if we have a polynomial f(x) such that f(2^k) ≡ 0 mod p_i for some i,
# but f(2^k) ≢ 0 mod other prime factors, then gcd(f(2^k), N) gives a factor.

# What polynomials have roots in <2>?
# Since <2> has order 1237 (prime), and the elements are 2^k for k ∈ [0, 1236],
# the minimal polynomial of 2 over Z/NZ... well, that's complex.

# Simpler idea: cyclotomic polynomials.
# Phi_1237(x) = (x^1237 - 1) / (x - 1) = x^1236 + x^1235 + ... + x + 1
# This is a polynomial whose roots are primitive 1237-th roots of unity.

# In Z/NZ: 2 is a primitive 1237-th root (since ord_N(2) = 1237 exactly).
# So Phi_1237(2) ≡ 0 mod N? No: 2^1237 ≡ 1, so (2^1237 - 1)/(2 - 1) = 2^1236 + ... + 1.
# But 2^1237 - 1 = M(1237) ≡ 0 mod N (since N | M(1237)).
# So 2^1237 - 1 ≡ 0 mod N, and (2^1237 - 1)/(2-1) = M(1237)/1 = M(1237) ≡ 0 mod N too.
# Trivial.

# Better: use Phi_p(2) for OTHER primes p, not just 1237.
# Phi_3(2) = 2^2 + 2 + 1 = 7
# Phi_5(2) = 2^4 + 2^3 + 2^2 + 2 + 1 = 31
# Phi_7(2) = 2^6 + 2^5 + ... + 1 = 127
# These are Mersenne numbers M(p) for prime p!
# M(p) = Phi_p(2).

# M(3) = 7, M(5) = 31, M(7) = 127, M(11) = 23 * 89, M(13) = 8191, ...
# We need to find a prime p such that gcd(M(p), F2) gives a non-trivial factor.
# But M(p) for small p is small. For p = 1237, M(p) is huge.

# IDEA: compute gcd(M(p), F2) for various primes p.
# M(p) | F2 only if p | 1237 (since ord_q(2) = p means p | ord_q(2) | 1237, so p = 1237).
# So M(p) | F2 only for p = 1237. Trivial.

# But: gcd(M(p), F2) might be > 1 if F2 has a prime factor q with ord_q(2) | p.
# ord_q(2) = 1237 (for q | F2). So ord_q(2) | p means 1237 | p, i.e., p = 1237.
# So no luck.

# Different: try M(k) for k = 1237 * something. Then ord_q(2) = 1237 | k means M(k) is divisible by q.
# M(k) for k > 1237: large.

# IDEA: try small primes p, compute M(p), then gcd with F2.
# This will likely give gcd = 1 unless F2 shares a factor with M(p) for small p.
# F2 = M(1237)/F1. F2 doesn't divide M(p) for p < 1237 (since F2 has order-1237 elements).
# So gcd(M(p), F2) = 1 for p < 1237. Boring.

# DIFFERENT IDEA: compute M(p) mod F2 for various p, take gcd(M(p), F2).
# M(p) mod F2: 2^p - 1 mod F2. For p = 1237, this is 0. For other p, it's some nonzero value.

# What's interesting: for p = 1237 * k (multiples of 1237), 2^(1237k) ≡ 1^k = 1 mod F2.
# So 2^(1237k) - 1 ≡ 0 mod F2. Trivial.

# What about p such that gcd(p, 1237) = 1?
# Then ord_q(2) = 1237 doesn't divide p, so 2^p ≢ 1 mod q.
# So 2^p - 1 ≢ 0 mod q for any q | F2. So gcd(2^p - 1, F2) = 1. Trivial.

log(f'تحلیل: استفاده از چندجمله‌ای‌های ساده در 2 به نتیجه نمی‌رسد')
log(f'  چون 2^k - 1 ≡ 0 mod q (q | F2) فقط وقتی 1237 | k')
log(f'')

# ============================================================
# METHOD B: Use powers of 2 and Jacobi symbol differences
# ============================================================
log(f'=== روش B: تفاوت Jacobi ===')
log(f'ایده: اگر q1, q2 فاکتورهای F2 باشند، ممکن است (a/q1) ≠ (a/q2) برای a = 2^k + ...')
log(f'')

# For q | M(1237): 2 has order 1237 mod q.
# (2/q) = 2^((q-1)/2) mod q.
# q ≡ 1 mod 2474 (so q ≡ 1 mod 4), thus (2/q) = +1 (since (2/q) = (-1)^((q^2-1)/8), 
#   and for q ≡ ±1 mod 8, (2/q) = +1; for q ≡ ±3 mod 8, (2/q) = -1)
# q ≡ 1 mod 4 and q ≡ 1 mod 2474, so q ≡ 1 mod 2474 = 2 * 1237
# q mod 8 can be 1, 3, 5, 7.

# We previously found (1237/N) = +1 and (2/N) = +1 (in earlier sessions).
# Since N = q1 * q2 * ... * qk, (a/N) = product of (a/qi).
# If all qi have (a/qi) = +1, then (a/N) = +1.
# If some have +1 and some -1, (a/N) = (-1)^(# of -1).

# We previously found (1237/N) = +1. This means even number of qi have (1237/qi) = -1.
# (Could be 0, 2, 4, ...)

# Check (a/N) for various a to gather info about qi
log(f'بررسی (a/N) برای a های مختلف:')
jacobi_data = []
for a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 1237, -1, -2, -1237, -2474, 2474]:
    j = jacobi(a % N, N)
    jacobi_data.append((a, j))
    log(f'  ({a}/N) = {j}')
log(f'')

# Find a where (a/N) = -1 — means odd number of qi have (a/qi) = -1
log(f'مقادیر a با (a/N) = -1 (نشان‌دهنده‌ی تفاوت بین qi):')
for a, j in jacobi_data:
    if j == -1:
        log(f'  a = {a}: (a/N) = -1')
log(f'')

# ============================================================
# METHOD C: Use 2 as a "twist" parameter in elliptic curve
# ============================================================
log(f'=== روش C: منحنی بیضوی با torsion point از <2> ===')
log(f'ایده: منحنی E: y^2 = x^3 - x با torsion Z/2Z. نقاط torsion آن y=0, x∈{{0,±1}}.')
log(f'اما استفاده از 2^k به‌عنوان x-coordinate ممکن است نقاط ساختاری تولید کند.')
log(f'')

# Try: for x = 2^k mod N, compute y^2 = x^3 - x mod N
# If y^2 is a perfect square mod N for some k, we have a point.
# Check gcd(y, N) — might give a factor.

# Even simpler: just check (x^3 - x / N) Jacobi symbol
log(f'بررسی (x^3 - x / N) برای x = 2^k, k = 1..1236:')
t0 = time.time()
interesting_ks = []
for k in range(1, 1237):
    x = int(powmod(2, k, N))
    # Compute x^3 - x mod N
    val = (x * x * x - x) % N
    j = jacobi(val, N)
    if j == -1:
        # Means (val/qi) = -1 for odd # of qi
        interesting_ks.append((k, val, j))
        if len(interesting_ks) < 5:
            log(f'  k={k}: (2^(3k) - 2^k / N) = {j}')
elapsed = time.time() - t0
log(f'  total k with Jacobi = -1: {len(interesting_ks)} (elapsed {elapsed:.2f}s)')
log(f'')

# ============================================================
# METHOD D: BSGS in (Z/NZ)* for finding elements with specific orders
# ============================================================
log(f'=== روش D: BSGS برای پیدا کردن عنصر با ord کوچک‌تر از 1237 ===')
log(f'ایده: اگر عنصر g با ord(g) = d | 1237 (یعنی d=1 یا d=1237) پیدا کنیم')
log(f'  اگه d=1، آن‌گاه g ≡ 1 mod همه‌ی qi. ولی اگر g ≡ 1 mod همه‌ی qi به جز یکی، فاکتور می‌دهد.')
log(f'  چون 1237 prime است، فقط d=1 یا d=1237 ممکن است.')
log(f'')

# In (Z/NZ)*, the elements of order dividing 1237 form a subgroup of order 1237 (= <2>).
# All elements of order 1 are just {1}. All elements of order 1237 are <2> \ {1} (1236 elements).

# These 1237 elements (including 1) are exactly <2>. They are all ≡ to (some 2^k) mod each qi.

# Now: take any element g ∈ (Z/NZ)*. Compute g^(1237). 
# g^1237 ≡ 1 mod qi iff ord_qi(g) | 1237.
# If for some qi, ord_qi(g) | 1237, and for another qi', ord_qi'(g) doesn't divide 1237:
#   then g^1237 - 1 ≡ 0 mod qi but ≢ 0 mod qi' → gcd gives factor!

# So: pick random g, compute g^1237 mod N, take gcd(g^1237 - 1, N).
# If factor found, great. If g^1237 ≡ 1 mod N (trivial), try another g.
# If g^1237 ≢ 1 mod N at all (no qi has ord dividing 1237), then gcd = 1.

log(f'آزمایش: برای g های مختلف، gcd(g^1237 - 1, N):')
random.seed(1234)
for trial in range(30):
    g = random.randint(2, N - 1)
    val = powmod(g, 1237, N)
    g_result = gcd(int(val) - 1, N)
    if 1 < g_result < N:
        log(f'  >>> FACTOR FOUND at trial {trial+1}: g = {g}, factor = {g_result}')
        log(f'  is_prime: {is_prime(g_result)}')
        cof = N // g_result
        log(f'  cofactor: {cof}')
        sys.exit(0)
    elif g_result == N:
        # trivial — g^1237 ≡ 1 mod N, meaning ord_qi(g) | 1237 for all qi
        # Since 1237 prime, ord_qi(g) ∈ {1, 1237}.
        # If all qi have ord_qi(g) = 1237, then g^1237 ≡ 1 mod all qi → trivial.
        pass
log(f'  هیچ فاکتور از ۳۰ آزمایش پیدا نشد')
log(f'')

# Now: choose g specifically — like a small prime, or a value with structure
log(f'آزمایش با g های خاص:')
special_gs = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
for g in special_gs:
    val = powmod(g, 1237, N)
    g_result = gcd(int(val) - 1, N)
    if 1 < g_result < N:
        log(f'  >>> FACTOR FOUND: g = {g}, factor = {g_result}')
        sys.exit(0)
log(f'  هیچ فاکتور از اعداد اول کوچک پیدا نشد')
log(f'')

# ============================================================
# METHOD E: Use 2 in a structured way — compute 2^k mod N for k = 1..1236, 
#   look at differences 2^k - 1 mod N for gcd
# ============================================================
log(f'=== روش E: gcd(2^k - 1, N) برای k = 1..1236 ===')
log(f'ایده: 2^k - 1 ≡ 0 mod q (q | F2) iff ord_q(2) | k iff 1237 | k')
log(f'  برای k < 1237, 1237 ∤ k, پس 2^k - 1 ≢ 0 mod q')
log(f'  یعنی gcd(2^k - 1, F2) = 1 برای همه‌ی k < 1237. تکرار کار قبلی.')
log(f'')

# ============================================================
# METHOD F: Use Mersenne "exponent" — compute 2^(1237^k) mod N
# ============================================================
log(f'=== روش F: 2^(1237^k) mod N برای k = 1..10 ===')
log(f'ایده: اگر q | F2 با ord_q(2) = 1237، آن‌گاه 2^(1237^k) ≡ 1 mod q')
log(f'  این به ما gcd = 1 یا gcd = N (trivial) می‌دهد، فاکتور جدید نه.')
log(f'')

# Compute 2^(1237^k) mod N for k = 1..10
val = mpz(2)
for k in range(1, 11):
    val = powmod(val, 1237, N)
    log(f'  2^(1237^{k}) mod N: first 30 digits = {str(int(val))[:30]}...')
    # gcd
    g = gcd(int(val) - 1, N)
    log(f'    gcd(2^(1237^{k}) - 1, N) = {g}')
    if 1 < g < N:
        log(f'  >>> FACTOR: {g}')
        sys.exit(0)
log(f'')

# ============================================================
# METHOD G: Use 2 * 3 mod N and compute 2^k * 3^j — diagonal element
# ============================================================
log(f'=== روش G: ضرب 2 و 3 به‌عنوان diagonal generator ===')
log(f'ایده: 2 با ord=1237 و 3 با ord بزرگ. گاوس <2, 3> در (Z/NZ)*')
log(f'اگر 3 ord ≠ 1237 داشته باشد، می‌توانیم structure استفاده کنیم.')
log(f'')

# Compute ord_N(3) — if it's not 1237, we have something useful
# But ord_N(3) divides (N-1) which is unknown.
# We can compute 3^1237 mod N and see if it's 1.
log(f'بررسی: 3^1237 mod N = {powmod(3, 1237, N)}')
log(f'  اگر 1 باشد: ord_N(3) | 1237، یعنی ord_N(3) = 1 یا 1237')
log(f'  اگر ≠1 باشد: ord_N(3) ∤ 1237، پس یک عنصر با ساختار متفاوت')
log(f'')

# Now: compute 2^a * 3^b mod N for various (a, b), see if any gives gcd > 1
log(f'بررسی 2^a * 3^b - 1 mod N برای a, b ∈ [0, 1236]:')
t0 = time.time()
powers_of_2 = [int(powmod(2, k, N)) for k in range(1237)]
powers_of_3 = [int(powmod(3, k, N)) for k in range(1237)]  # limited
# Now check 2^a * 3^b - 1 for various b values
# Sample: b ∈ {1, 2, 3, 5, 7, 10, 50, 100, 500, 1236}
b_values = [1, 2, 3, 5, 7, 10, 50, 100, 500, 1236]
found = False
for b in b_values:
    val_3b = int(powmod(3, b, N))
    # Compute 2^a * 3^b mod N for a = 0..1236
    # Then gcd(2^a * 3^b - 1, N)
    # Incremental: start with val = 3^b, then multiply by 2 each step
    cur = val_3b
    for a in range(1237):
        g = gcd(int(cur) - 1, N)
        if 1 < g < N:
            log(f'  >>> FACTOR FOUND at a={a}, b={b}: {g}')
            log(f'  is_prime: {is_prime(g)}')
            cof = N // g
            log(f'  cofactor: {cof}')
            sys.exit(0)
        cur = (cur * 2) % N
    elapsed = time.time() - t0
    log(f'  b={b}: completed all 1237 a values (elapsed {elapsed:.1f}s)')

log(f'  هیچ فاکتور پیدا نشد')
log(f'')

# ============================================================
# METHOD H: Use 2 as a "Mersenne-friendly" base in Pollard rho
# ============================================================
log(f'=== روش H: Pollard rho با تابع f(x) = x^2 + 2 (Mersenne-friendly) ===')
log(f'ایده: چون 2 به‌طور طبیعی در <2> قرار دارد، استفاده از آن در Pollard rho')
log(f'  ممکن است cycles کوتاه‌تر در یکی از qi بدهد و فاکتور به‌دست آید.')
log(f'')

def pollard_rho_custom(n, start, c, max_iter=10**6):
    """Pollard's rho with custom function f(x) = x^2 + c."""
    x = start % n
    y = start % n
    d = 1
    count = 0
    while d == 1 and count < max_iter:
        x = (x*x + c) % n
        y = (y*y + c) % n
        y = (y*y + c) % n
        d = gcd(abs(x - y), n)
        count += 1
        if count % 100000 == 0:
            log(f'    iter {count}: d = {d}')
    return d if d != n else None

# Try several (start, c) combinations related to 2 and 1237
configs = [(2, 1), (2, 2), (2, 7), (2^1237 % N, 1), (2^619, 1), (2^619, 2), (2^619, 7), (1237, 1), (1237, 2)]
for start_val, c in configs:
    log(f'  Pollard rho با start = {str(start_val)[:30]}, c = {c}')
    t0 = time.time()
    d = pollard_rho_custom(N, int(start_val), c, max_iter=300000)
    elapsed = time.time() - t0
    if d and 1 < d < N:
        log(f'  >>> FACTOR FOUND: {d} (elapsed {elapsed:.1f}s)')
        if int(M) % d == 0:
            log(f'  ✓ REAL FACTOR of M(1237)!')
        sys.exit(0)
    else:
        log(f'  ✗ no factor (elapsed {elapsed:.1f}s)')

log(f'')
log(f'=== پایان روش‌های ابداعی ===')
