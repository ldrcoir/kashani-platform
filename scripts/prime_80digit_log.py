#!/usr/bin/env python3
"""
Start from 80-digit primes, sum log10 until reaching log10(F2) ≈ 302.97.

Strategy:
- Generate random 80-digit primes (use gmpy2's next_prime).
- For each prime, add log10(p) to the running sum.
- Continue until sum is close to log10(F2).
- Log each step.

Number of primes needed: 302.97 / 80 ≈ 3.79, so about 4 primes (since each is ~80 in log10).
But we want exact sum close to target. So:
1. Pick 3 random 80-digit primes → sum_log ≈ 240. Need ~63 more in log10.
2. Then pick a prime with log10 ≈ 63, i.e., a 63-digit prime.
3. Or: pick 4 primes and adjust.

Actually with 80-digit primes, we need ~3-4 of them.
Plan: 
  - Generate random 80-digit primes until we have a set of 3 with sum_log just below target.
  - Then add a smaller prime (smaller digit count) to fine-tune.

Better plan: 
  - Pick primes with log10 ≈ 80, but with small variation, so we can reach the target exactly.
  - 80-digit primes have log10 in [80, 81).
  - 3 such primes: sum_log in [240, 243). 
  - Need: 302.97 - 240 = 62.97 → need a 63-digit prime (log10 ≈ 63).
  - 302.97 - 243 = 59.97 → need a 60-digit prime.
  - So: 3 primes of 80-digit + 1 prime of ~60-digit = 4 primes total.

But user says "start from 80-digit primes". Let me:
  - Pick several 80-digit primes (say 3)
  - Then continue with progressively smaller primes to fill the gap
  - All logged.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, next_prime, gcd, powmod, log10
import math
import time
import random
from pathlib import Path

# Setup
P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1

try:
    import mpmath
    mpmath.mp.dps = 80
    log10_F2 = float(mpmath.log10(int(F2)))
except ImportError:
    log10_F2 = math.log10(int(F2))

target = log10_F2
print(f"Target = log10(F2) = {target:.10f}")
print(f"F2 has {len(str(F2))} digits")
print()

# ============================================================
# Logging
# ============================================================
LOG_FILE = Path('/home/z/my-project/download/prime80_log.txt')
LOG_FILE.write_text('')
def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

log(f'=== تولید اعداد اول 80 رقمی و جمع log10 ===')
log(f'هدف: log10(F2) = {target:.10f}')
log(f'تعداد ارقام F2: {len(str(F2))}')
log(f'')

# ============================================================
# Generate random 80-digit primes
# ============================================================
def random_prime_with_digits(d):
    """Generate a random prime with exactly d digits."""
    low = 10**(d-1)
    high = 10**d - 1
    while True:
        # Random number in [low, high]
        n = random.randint(low, high)
        # Make odd
        if n % 2 == 0:
            n += 1
        # Find next prime >= n
        p = int(next_prime(mpz(n)))
        if p <= high:
            return p

# Phase 1: Generate 3 random 80-digit primes
log(f'=== مرحله ۱: تولید ۳ عدد اول ۸۰ رقمی ===')
primes_80 = []
sum_log = 0.0
for i in range(3):
    t0 = time.time()
    p = random_prime_with_digits(80)
    t1 = time.time()
    lp = math.log10(p)
    primes_80.append(p)
    sum_log += lp
    log(f'  [{i+1}] عدد اول ۸۰ رقمی: p = {str(p)[:40]}...{str(p)[-20:]}')
    log(f'      log10(p) = {lp:.10f}')
    log(f'      جمع تجمعی = {sum_log:.10f}')
    log(f'      فاصله تا هدف = {target - sum_log:.10f}')
    log(f'      زمان: {t1-t0:.3f}s')
    log(f'')

# Now we need (target - sum_log) more in log10. This should be ~60-65 (since 3*80=240, target=303, gap=63).
gap = target - sum_log
log(f'فاصله باقی‌مانده تا هدف: {gap:.10f}')
gap_digits = int(gap) + 1  # number of digits needed
log(f'یعنی به یک عدد اول ~{gap_digits} رقمی نیاز داریم.')
log(f'')

# Phase 2: Generate a prime with log10 ≈ gap
# We want log10(p) = gap as closely as possible.
# Start with a random prime with gap_digits, then try multiple to get close.
log(f'=== مرحله ۲: پیدا کردن عدد اول با log10 ≈ {gap:.6f} ===')

# Try multiple primes and pick the one that gets us closest
best_p = None
best_diff = float('inf')
best_lp = 0
attempts = 100
log(f'تلاش با {attempts} عدد اول تصادفی {gap_digits} رقمی...')

for attempt in range(attempts):
    p = random_prime_with_digits(gap_digits)
    lp = math.log10(p)
    diff = abs((sum_log + lp) - target)
    if diff < best_diff:
        best_diff = diff
        best_p = p
        best_lp = lp
    if attempt < 5 or attempt == attempts - 1:
        log(f'  تلاش {attempt+1}: p = {str(p)[:30]}... log10 = {lp:.10f}, خطای تجمعی = {abs((sum_log + lp) - target):.10f}')

log(f'')
log(f'بهترین عدد اول {gap_digits} رقمی پیدا شده:')
log(f'  p = {best_p}')
log(f'  log10(p) = {best_lp:.10f}')
log(f'  جمع تجمعی بعد از اضافه کردن = {sum_log + best_lp:.10f}')
log(f'  خطا = {target - (sum_log + best_lp):.10f}')
log(f'')

# Add this prime
primes_all = primes_80 + [best_p]
sum_log_total = sum_log + best_lp
log(f'  ✓ اضافه شد')
log(f'')

# ============================================================
# Phase 3: Fine-tune with smaller primes (refine)
# ============================================================
log(f'=== مرحله ۳: تنظیم دقیق با اعداد اول کوچک‌تر ===')
remaining = target - sum_log_total
log(f'فاصله باقی‌مانده: {remaining:.10f} (log10)')
log(f'')

# Generate small primes (greedy ascending from 2 — but user said no 2, so start from 3)
def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

small_primes = small_primes_up_to(1000)
small_primes_no2 = [p for p in small_primes if p != 2]
log(f'اعداد اول کوچک (تا 1000، بدون ۲): {len(small_primes_no2)}')

# Greedy descending: pick largest prime whose log10 fits remaining
small_selected = []
cur_remaining = remaining
for p in sorted(small_primes_no2, reverse=True):
    lp = math.log10(p)
    if lp <= cur_remaining + 1e-12:
        small_selected.append(p)
        cur_remaining -= lp

log(f'  اعداد کوچک انتخاب‌شده: {small_selected}')
log(f'  جمع log10 اینها = {sum(math.log10(p) for p in small_selected):.10f}')
log(f'  فاصله نهایی = {cur_remaining:.10f}')
log(f'')

primes_final = primes_all + small_selected
final_sum = sum_log_total + sum(math.log10(p) for p in small_selected)
log(f'  جمع کل log10 = {final_sum:.10f}')
log(f'  هدف = {target:.10f}')
log(f'  خطای نهایی = {target - final_sum:.10e}')
log(f'')

# ============================================================
# Summary
# ============================================================
log(f'=== خلاصه ===')
log(f'')
log(f'اعداد اول استفاده‌شده (به ترتیب اضافه شدن):')
for i, p in enumerate(primes_final):
    lp = math.log10(p)
    log(f'  [{i+1}] p = {p} ({len(str(p))} digits, log10 = {lp:.10f})')
log(f'')
log(f'جمع کل log10 = {final_sum:.10f}')
log(f'هدف (log10(F2)) = {target:.10f}')
log(f'خطا = {target - final_sum:.10e}')
log(f'')
log(f'تعداد اعداد اول: {len(primes_final)}')
log(f'  - 80-digit primes: {len(primes_80)}')
log(f'  - {gap_digits}-digit prime: 1')
log(f'  - small primes: {len(small_selected)}')

# Compute product and check
product = mpz(1)
for p in primes_final:
    product *= mpz(p)
log(f'')
log(f'محصول ∏ pᵢ = {str(product)[:60]}... ({len(str(product))} digits)')
log(f'log10(∏ pᵢ) = {math.log10(int(product)):.10f}')
log(f'نسبت ∏ pᵢ / F2 ≈ {10**(math.log10(int(product)) - log10_F2):.6e}')

# Test: does product divide F2?
if F2 % product == 0:
    quotient = F2 // product
    log(f'  ✓ F2 = ∏ pᵢ × {quotient}')
    log(f'  is_prime(quotient): {is_prime(quotient)}')
else:
    rem = F2 % product
    log(f'  ✗ F2 بر ∏ pᵢ بخش‌پذیر نیست (remainder = {str(rem)[:50]}...)')

print()
print(f'لاگ کامل: {LOG_FILE}')
print(f'تعداد خط: {len(LOG_FILE.read_text().splitlines())}')
