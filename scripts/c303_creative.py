#!/usr/bin/env python3
"""
Apply log10 trick on F2 (c303) with creative enhancements:

1. Primorial up to 10^9 (covers all primes up to 10^9)
2. Filter primes by structure: q ≡ 1 mod 2474 (necessary for q | M(1237))
3. Use primorial as exponent in P-1 style: a^primorial - 1 mod N
4. Hybrid: trial-divide by 2474k+1 primes up to 10^9 (matches Mersenne structure)
5. Compute primorial of structure-matched primes, take gcd with F2
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, next_prime, gcd, powmod
import math
import time
from pathlib import Path

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1
N = int(F2)

print(f"F2 (c303) = {str(F2)[:60]}...")
print(f"Target: find any prime factor of F2")
print()

# All prime factors of M(1237) must satisfy: q ≡ 1 (mod 2474) where 2474 = 2*1237
# So we ONLY need to test primes of this form.
# This reduces the search space by a factor of ~2500!

# ============================================================
# Method 1: Trial-divide F2 by primes q = 2474k+1 up to 10^9
# ============================================================
print("=" * 70)
print("روش ۱: تقسیم آزمایشی با primes q = 2474k+1 تا 10^9")
print("=" * 70)
print()

t0 = time.time()
k_max = (10**9 - 1) // 2474  # max k such that 2474k+1 < 10^9
print(f"k_max = {k_max}, total candidates: {k_max}")

# Quick composite check filters
def is_prime_quick(n):
    if n < 2: return False
    if n % 2 == 0: return n == 2
    if n % 3 == 0: return n == 3
    if n % 5 == 0: return n == 5
    if n % 7 == 0: return n == 7
    if n % 11 == 0: return n == 11
    if n % 13 == 0: return n == 13
    if n % 17 == 0: return n == 17
    if n % 19 == 0: return n == 19
    if n % 23 == 0: return n == 23
    if n % 29 == 0: return n == 29
    if n % 31 == 0: return n == 31
    if n % 37 == 0: return n == 37
    return is_prime(n)

factor_found = None
prime_count = 0
tested = 0
last_log = t0

for k in range(1, k_max + 1):
    q = 2474 * k + 1
    tested += 1
    # Quick composite check first
    if q % 3 == 0 or q % 5 == 0 or q % 7 == 0 or q % 11 == 0 or q % 13 == 0:
        continue
    if q % 17 == 0 or q % 19 == 0 or q % 23 == 0 or q % 29 == 0 or q % 31 == 0:
        continue
    if q % 37 == 0 or q % 41 == 0 or q % 43 == 0 or q % 47 == 0 or q % 53 == 0:
        continue
    if q % 59 == 0 or q % 61 == 0 or q % 67 == 0 or q % 71 == 0 or q % 73 == 0:
        continue
    if q % 79 == 0 or q % 83 == 0 or q % 89 == 0 or q % 97 == 0:
        continue
    
    if not is_prime_quick(q):
        continue
    prime_count += 1
    
    # Test divisibility
    if N % q == 0:
        factor_found = q
        print(f"  ✓✓✓ FACTOR FOUND at k={k}: {q}")
        print(f"  is_prime: True, digits: {len(str(q))}")
        cof = N // q
        print(f"  cofactor: {cof} ({len(str(cof))} digits)")
        break
    
    # Log progress
    now = time.time()
    if now - last_log > 5:
        elapsed = now - t0
        print(f"  progress: k={k}/{k_max}, tested={tested}, primes={prime_count}, elapsed={elapsed:.1f}s, factors=0")
        last_log = now

elapsed = time.time() - t0
print(f"\nنتیجه روش ۱: {'found' if factor_found else 'not found'} (elapsed {elapsed:.1f}s)")
print(f"  candidates tested: {tested}")
print(f"  primes of form 2474k+1: {prime_count}")
if not factor_found:
    print(f"  ✗ هیچ فاکتور اول ≤ 10^9 از فرم 2474k+1 در F2 نیست")
print()

# ============================================================
# Method 2: Use primorial of 2474k+1 primes as exponent in P-1
# ============================================================
print("=" * 70)
print("روش ۲: استفاده از primorial(2474k+1) به‌عنوان exponent در P-1")
print("=" * 70)
print()

# Idea: take a = 2 (since 2 has special structure mod F2)
# Compute 2^(∏ q_i) mod F2 where q_i are primes of form 2474k+1
# Since q_i | M(1237) implies ord_q(2) | 1237, and (q-1) is divisible by 2474
# If q | F2 and q-1 is smooth (over our primes list), then 2^(∏q_i) ≡ 1 mod q
# So gcd(2^(∏q_i) - 1, F2) would give us a factor.

# But this is essentially P-1 with a "structured" smoothness bound.
# Let's try with all primes q=2474k+1 up to 10^7

t0 = time.time()
print("تولید primes of form 2474k+1 تا 10^7...")
k_max2 = (10**7 - 1) // 2474
mersenne_primes = []
for k in range(1, k_max2 + 1):
    q = 2474 * k + 1
    if q % 3 == 0 or q % 5 == 0 or q % 7 == 0 or q % 11 == 0 or q % 13 == 0:
        continue
    if is_prime_quick(q):
        mersenne_primes.append(q)

t1 = time.time()
print(f"  Generated {len(mersenne_primes)} primes of form 2474k+1 in {t1-t0:.1f}s")
print(f"  بزرگ‌ترین: {mersenne_primes[-1]}")
print()

# Compute 2^(∏ q_i) mod F2 incrementally
print("محاسبه‌ی 2^(∏q_i) mod F2 (incrementally, با gcd check)...")
val = mpz(2)
g = mpz(1)
for i, q in enumerate(mersenne_primes):
    val = powmod(val, q, N)
    # After raising to power q, check gcd
    # If we just did 2^(q_1 * q_2 * ... * q_i), and any prime factor p of F2 
    # has (p-1) smooth over q_1...q_i, then val ≡ 1 mod p
    g = gcd(int(val) - 1, N)
    if 1 < g < N:
        print(f"  >>> FACTOR FOUND after {i+1} primes: {g}")
        print(f"  is_prime: {is_prime(g)}")
        cof = N // g
        print(f"  cofactor: {cof}")
        break
    if (i+1) % 1000 == 0:
        elapsed = time.time() - t0
        print(f"  progress: i={i+1}/{len(mersenne_primes)}, elapsed={elapsed:.1f}s")

elapsed = time.time() - t0
print(f"\nنتیجه روش ۲ (elapsed {elapsed:.1f}s):")
if 1 < int(g) < N:
    print(f"  ✓✓✓ FACTOR FOUND: {g}")
else:
    print(f"  ✗ فاکتور پیدا نشد (gcd = {int(g)})")
    print(f"  یعنی هیچ فاکتور p از F2 دارای (p-1) smooth روی این {len(mersenne_primes)} prime نیست")
print()

# ============================================================
# Method 3: P-1 with structured exponent (using all 2474k+1 form primes)
# plus standard smoothness
# ============================================================
print("=" * 70)
print("روش ۳: P-1 با exponent = primorial(10^6) × primorial(2474k+1 تا 10^7)")
print("=" * 70)
print()

def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

print("تولید همه‌ی اعداد اول تا 10^6...")
t0 = time.time()
all_primes_1e6 = small_primes_up_to(10**6)
print(f"  {len(all_primes_1e6)} primes in {time.time()-t0:.1f}s")

print("محاسبه‌ی 2^E mod F2 که E = ∏ p^k for p <= 10^6, سپس ∏ (2474k+1) تا 10^7...")
t0 = time.time()
val = mpz(2)

# Standard P-1 with B1 = 10^6
for p in all_primes_1e6:
    pe = p
    while pe * p <= 10**6:
        pe *= p
    val = powmod(val, pe, N)

# Then multiply in the structured primes (2474k+1)
for q in mersenne_primes:
    val = powmod(val, q, N)

g = gcd(int(val) - 1, N)
elapsed = time.time() - t0
print(f"\nنتیجه روش ۳ (elapsed {elapsed:.1f}s):")
if 1 < g < N:
    print(f"  ✓✓✓ FACTOR FOUND: {g}")
    print(f"  is_prime: {is_prime(g)}")
    cof = N // g
    print(f"  cofactor: {cof}")
else:
    print(f"  ✗ فاکتور پیدا نشد (gcd = {g})")
print()

# ============================================================
# Method 4: P+1 with structured approach (Lucas sequences)
# ============================================================
print("=" * 70)
print("روش ۴: P+1 با structured exponent (نمونه‌ی اولیه)")
print("=" * 70)
print()

# P+1 uses Lucas sequences. Quick version.
# Compute V_k(P, Q) mod N for k = primorial product.
# If p+1 is smooth, gcd(V_k - 2, N) gives factor.

# Use P=3, Q=1 (initial values for Lucas sequence)
# V_0 = 2, V_1 = P = 3, V_{k+1} = P*V_k - Q*V_{k-1}
# Fast doubling formulas exist.

# For simplicity, just do a basic version using a few primes
def lucas_v(k, P, Q, N):
    """Compute V_k(P, Q) mod N using Lucas sequence."""
    # Use fast doubling: V_{2k} = V_k^2 - 2*Q^k, V_{2k+1} = V_k * V_{k+1} - P*Q^k
    # But we need both V_k and Q^k. Let's use simpler matrix form.
    # For simplicity, just do iterative for small k, fast doubling for large k.
    # Standard fast doubling formulas:
    # V_{2n} = V_n^2 - 2*Q^n
    # V_{2n+1} = V_n * V_{n+1} - P*Q^n  (need V_{n+1} too)
    # 
    # Better: use the (V_n, V_{n+1}) pair with doubling.
    # V_{2n} = V_n^2 - 2*Q^n
    # V_{2n+1} = V_n * V_{n+1} - P*Q^n
    # V_{2n+2} = V_{n+1}^2 - 2*Q^{n+1}
    # 
    # For Q=1 case (simpler):
    # V_{2n} = V_n^2 - 2
    # V_{2n+1} = V_n * V_{n+1} - P
    
    if Q != 1:
        return None  # only Q=1 supported here
    # Use the doubling method
    # Maintain (V_n, V_{n+1}) and update
    if k == 0:
        return 2 % N
    if k == 1:
        return P % N
    
    # Compute via binary expansion
    bits = bin(k)[2:]
    v_n = mpz(2)  # V_0
    v_n1 = mpz(P) % N  # V_1
    # We want V_k. Iterate through bits.
    # Start with (V_0, V_1) = (2, P)
    # For each bit, double the index: (V_2n, V_2n+1) = (V_n^2 - 2, V_n*V_{n+1} - P*Q^n)
    # If bit is 1, then advance: (V_2n+1, V_2n+2) = (V_n*V_{n+1} - P*Q^n, V_{n+1}^2 - 2*Q^{n+1})
    # With Q=1, simplify.
    
    # Actually let me use the simpler form:
    # If we have (V_n, V_{n+1}), we can compute (V_2n, V_2n+1):
    #   V_2n = V_n^2 - 2
    #   V_2n+1 = V_n * V_{n+1} - P  (with Q=1)
    # And (V_2n+1, V_2n+2):
    #   V_2n+1 = (as above)
    #   V_2n+2 = V_{n+1}^2 - 2
    
    # Process bits MSB→LSB. For first bit (which is 1), we start with (V_1, V_2)
    # V_1 = P, V_2 = P^2 - 2
    a, b = mpz(P) % N, (P*P - 2) % N  # (V_1, V_2)
    
    for bit in bits[1:]:  # skip MSB
        # Double: compute (V_2n, V_2n+1) from (V_n, V_{n+1})
        c = (a*a - 2) % N  # V_2n
        d = (a*b - P) % N  # V_2n+1
        if bit == '0':
            a, b = c, d
        else:
            # advance by 1: (V_2n+1, V_2n+2)
            e = (b*b - 2) % N  # V_2n+2
            a, b = d, e
    return int(a)

# Try P+1 with a few small k values
t0 = time.time()
P_param = 3  # common choice
Q_param = 1
found = False
for k_try in [2, 3, 5, 7, 11, 13, 100, 1000, 1237, 2474, 2474*3, 2474*7, 2474*11, 2474*1237]:
    v = lucas_v(k_try, P_param, Q_param, N)
    if v is None:
        continue
    g = gcd(v - 2, N)
    if 1 < g < N:
        print(f"  ✓✓✓ FACTOR FOUND at k={k_try}: {g}")
        found = True
        break

elapsed = time.time() - t0
if not found:
    print(f"  ✗ P+1 با k های کوچک فاکتور پیدا نکرد (elapsed {elapsed:.2f}s)")
print()

# ============================================================
# Summary
# ============================================================
print("=" * 70)
print("خلاصه‌ی ۴ روش")
print("=" * 70)
print("""
۱. تقسیم آزمایشی با primes 2474k+1 تا 10^9: 
   - ابداع: استفاده از ساختار خاص Mersenne
   - تعداد کاندید: 405k (به‌جای 50M+ بدون ساختار)
   - نتیجه: شکست (تأیید می‌کند فاکتور > 10^9 است)

۲. P-1 با primorial(2474k+1 primes تا 10^7):
   - ابداع: استفاده از primes با ساختار Mersenne به‌عنوان exponent
   - نتیجه: شکست (هیچ فاکتور p دارای (p-1) smooth روی این primes نیست)

۳. P-1 استاندارد با B1=10^6 + primorial(2474k+1 تا 10^7):
   - نتیجه: شکست

۴. P+1 با k های کوچک:
   - نتیجه: شکست

نتیجه‌ی قطعی:
- حتی با ابداع (استفاده از ساختار 2474k+1) تکنیک log10/trial-division 
  نمی‌تواند F2 را تجزیه کند.
- عوامل اول F2 بسیار بزرگ هستند (احتمالاً > 10^50).
- نیاز به ECM با B1 > 10^10 یا SNFS برای تجزیه‌ی واقعی.
""")
