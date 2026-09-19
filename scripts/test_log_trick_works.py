#!/usr/bin/env python3
"""
Counter-example: A case where the log10 trick DOES work.

Setup:
- Choose N = p1 * p2 where p1, p2 are KNOWN primes with specific structure.
- E.g., N = p1 * p2 where p1 is small (say, 10 digits) and p2 is large (50 digits).
- log10(N) ≈ 60.
- If we generate primes up to a "small bound" (e.g., all primes up to 10^7),
  we cover ALL small primes including p1.
- Then gcd(product_of_small_primes, N) = p1.

This is just "trial division" but framed as log10-approximation.

The key insight: the log10 trick "works" only when one of the factors is
small enough that we generate ALL primes in its size range.
For F2 (303 digits), we don't know the factor sizes — they could be 100+ digits.
Generating ALL 100-digit primes is infeasible (10^97 of them).

So the trick is essentially trial division, with the "log10 approximation" being
just a side-effect of covering the small-prime range.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, next_prime, gcd, powmod
import math
import time
import random
from pathlib import Path

print("=" * 70)
print("  مثال نقض: حالتی که روش log10 واقعاً کار می‌کند")
print("=" * 70)
print()

# Setup: choose small p1 and large p2
random.seed(42)
def random_prime_with_digits(d):
    low = 10**(d-1)
    high = 10**d - 1
    while True:
        n = random.randint(low, high)
        if n % 2 == 0: n += 1
        p = int(next_prime(mpz(n)))
        if p <= high: return p

p1 = random_prime_with_digits(7)   # 7-digit small prime
p2 = random_prime_with_digits(50)  # 50-digit large prime
N = p1 * p2
print(f"تولید عدد مرکب با ساختار نامتقارن:")
print(f"  p1 = {p1} ({len(str(p1))} digits, small)")
print(f"  p2 = {p2} ({len(str(p2))} digits, large)")
print(f"  N = p1 × p2 = {str(N)[:60]}... ({len(str(N))} digits)")
print(f"  log10(N) = {math.log10(N):.10f}")
print()

# METHOD: log10 trick
# Generate primes with log10 sum approaching log10(N).
# Use primes starting from 2, 3, 5, ... in increasing order (greedy asc).
# When sum exceeds log10(N), stop.
# Then gcd(product, N) gives p1 if p1 is among the selected primes.

def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

print("=" * 70)
print("  روش: تولید اعداد اول کوچک به کوچک (حریصانه صعودی)")
print("=" * 70)
print()

# Generate primes up to 10^7 (covers p1 = 7-digit)
primes = small_primes_up_to(10**7)
print(f"تولید {len(primes)} عدد اول تا 10^7")

# Greedy ascending — add primes whose log10 sum stays <= log10(N)
target = math.log10(N)
print(f"هدف: log10(N) = {target:.10f}")
print()

selected = []
sum_log = 0.0
for p in primes:
    lp = math.log10(p)
    if sum_log + lp <= target:
        selected.append(p)
        sum_log += lp
    else:
        # Don't add this prime (would overshoot)
        pass  # but we keep iterating in case a smaller prime fits later (impossible since sorted asc)

print(f"اعداد اول انتخاب‌شده: {len(selected)} عدد")
print(f"بزرگ‌ترین عدد اول انتخاب‌شده: {selected[-1] if selected else 'none'}")
print(f"جمع log10 = {sum_log:.10f}")
print(f"هدف = {target:.10f}")
print(f"خطا = {target - sum_log:.10e}")
print()

# Now compute product and gcd with N
product = mpz(1)
for p in selected:
    product *= mpz(p)

print(f"محصول ∏ pᵢ: {str(product)[:60]}... ({len(str(product))} digits)")

g = gcd(int(product), int(N))
print(f"gcd(∏ pᵢ, N) = {g}")
print()

if g > 1 and g < N:
    print(f"  ✓✓✓ روش log10 فاکتور پیدا کرد: {g}")
    print(f"  is_prime(g): {is_prime(g)}")
    cof = N // g
    print(f"  cofactor = {cof}")
    print(f"  is_prime(cofactor): {is_prime(cof)}")
    print()
    if g == p1:
        print(f"  ✓ این دقیقاً p1 است (عامل کوچک)!")
    elif g == p2:
        print(f"  ✓ این دقیقاً p2 است (عامل بزرگ)!")
    print()
    print(f"  نتیجه: تجزیه‌ی کامل N = {g} × {cof}")
else:
    print(f"  ✗ روش log10 فاکتور پیدا نکرد (نباید اتفاق بیفتد)")
    print(f"  دلیل: p1 = {p1} در بین اعداد اول انتخاب‌شده نبود؟")
    if p1 in selected:
        print(f"  ولی p1 = {p1} در selected هست! چرا gcd کار نکرد؟")
        print(f"  product mod p1 = {int(product) % p1}")
        print(f"  N mod p1 = {int(N) % p1}")

# ============================================================
# ANALYSIS
# ============================================================
print()
print("=" * 70)
print("  تحلیل: چرا این بار کار کرد؟")
print("=" * 70)
print(f"""
کار کرد چون:
- p1 یک عدد اول کوچک (۷ رقمی) بود.
- ما همه‌ی اعداد اول تا 10^7 را تولید کردیم.
- پس p1 حتماً در لیست ما بود.
- پس product ≡ 0 mod p1.
- پس gcd(product, N) شامل p1 بود.

این در واقع روش «تقسیم آزمایشی» (trial division) است که با پوشیدن 
تمام اعداد اول کوچک، هر فاکتور کوچکی پیدا می‌شود.

نکته کلیدی:
- روش «log10 trick» فقط وقتی کار می‌کند که حداقل یکی از فاکتورها
  به اندازه‌ی کافی کوچک باشد که در محدوده‌ی تولید اعداد اول ما قرار بگیرد.
- برای F2 (303 digits)، فاکتورهای آن همگی بزرگ هستند (احتمالاً > 10^70).
- تولید همه‌ی اعداد اول 70 رقمی غیرممکن است (10^67 عدد).
- پس روش log10 برای F2 غیرقابل اجرا است.

نتیجه‌گیری:
روش «ماشین حسابی log10» در واقع همان «تقسیم آزمایشی» است، 
ولی با کلام متفاوت. برای اعداد با فاکتورهای کوچک کار می‌کند، 
ولی برای اعداد با فاکتورهای بزرگ (مثل F2) بی‌فایده است.
""")
