#!/usr/bin/env python3
"""
Phase 1: Test divisibility of F2 by each of the 128 small primes (one by one).
Phase 2: When all fail, iterate primes of form 2*1237*k+1 = 2474k+1
         (which is necessary for any prime factor of M(1237)).
         Try larger and larger k values.
Phase 3: Log everything to a file.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod
import math
import json
import time
from pathlib import Path

# Setup
P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1

# Load best primes (without 2, with target = log10(F2))
# Re-do the selection
def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

PRIME_LIMIT = 100000
all_primes = small_primes_up_to(PRIME_LIMIT)
primes_no2 = [p for p in all_primes if p != 2]
log10_primes_no2 = [math.log10(p) for p in primes_no2]

try:
    import mpmath
    mpmath.mp.dps = 80
    log10_F2 = float(mpmath.log10(int(F2)))
except ImportError:
    log10_F2 = math.log10(int(F2))

target = log10_F2

# Greedy ascending (no 2)
sum_greedy = 0.0
sel_greedy = []
for p, lp in zip(primes_no2, log10_primes_no2):
    if sum_greedy + lp <= target + 1e-12:
        sum_greedy += lp
        sel_greedy.append(p)

# Refine
import bisect
sorted_with_log = sorted([(lp, p) for p, lp in zip(primes_no2, log10_primes_no2)])
sorted_logs = [lp for lp, _ in sorted_with_log]

def refine_heavy(target, selected_primes, all_primes, log10_primes, iterations=200000):
    current_sum = sum(math.log10(p) for p in selected_primes)
    selected_set = set(selected_primes)
    
    for it in range(iterations):
        error = target - current_sum
        if abs(error) < 1e-12:
            break
        best_improvement = 1e-15
        best_op = None
        if error > 0:
            for p, lp in zip(all_primes, log10_primes):
                if p in selected_set:
                    continue
                if lp <= error + 1e-15:
                    new_error = error - lp
                    improvement = abs(error) - abs(new_error)
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_op = ('add', p, lp)
        for p1 in list(selected_set):
            lp1 = math.log10(p1)
            want = lp1 + error
            idx = bisect.bisect_left(sorted_logs, want)
            for di in [-1, 0, 1]:
                ii = idx + di
                if 0 <= ii < len(sorted_with_log):
                    lp2, p2 = sorted_with_log[ii]
                    if p2 in selected_set or p2 == p1:
                        continue
                    delta = lp2 - lp1
                    new_error = error - delta
                    improvement = abs(error) - abs(new_error)
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_op = ('swap', p1, p2, lp1, lp2)
        if error < 0:
            for p1 in list(selected_set):
                lp1 = math.log10(p1)
                if lp1 <= -error + 1e-15:
                    new_error = error + lp1
                    improvement = abs(error) - abs(new_error)
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_op = ('remove', p1, lp1)
        if best_op is None:
            break
        op = best_op[0]
        if op == 'add':
            _, p, lp = best_op
            selected_set.add(p)
            current_sum += lp
        elif op == 'swap':
            _, p1, p2, lp1, lp2 = best_op
            selected_set.remove(p1)
            selected_set.add(p2)
            current_sum += lp2 - lp1
        elif op == 'remove':
            _, p1, lp1 = best_op
            selected_set.remove(p1)
            current_sum -= lp1
    return current_sum, sorted(selected_set)

sum_refined, sel_refined = refine_heavy(target, sel_greedy, primes_no2, log10_primes_no2, iterations=200000)
selected_primes = sel_refined
print(f"Selected {len(selected_primes)} primes (target=log10(F2), no 2)")
print(f"Sum = {sum_refined:.10f}, target = {target:.10f}, error = {target - sum_refined:.6e}")
print()

# ============================================================
# Logging setup
# ============================================================
LOG_FILE = Path('/home/z/my-project/download/divisibility_log.txt')
LOG_FILE.write_text('')  # clear
def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

log(f'=== آزمایش بخش‌پذیری F2 ===')
log(f'F2 = M(1237)/F1, {len(str(F2))} digits')
log(f'تعداد اعداد اول انتخاب‌شده: {len(selected_primes)}')
log(f'')

# ============================================================
# Phase 1: Test each selected prime one by one
# ============================================================
log(f'=== مرحله ۱: آزمایش اعداد اول انتخاب‌شده (دانه‌دانه) ===')
log(f'')
factors_found_phase1 = []
for i, p in enumerate(selected_primes):
    r = int(F2 % p)
    found = (r == 0)
    if found:
        factors_found_phase1.append(p)
        log(f'  [{i+1:3d}/{len(selected_primes)}] p = {p:>6d}  >>> F2 mod p = {r}  ✓ بخش‌پذیر است!!!')
    else:
        # only log every 25th to keep log compact
        if (i+1) % 25 == 0 or i < 5 or i == len(selected_primes)-1:
            log(f'  [{i+1:3d}/{len(selected_primes)}] p = {p:>6d}  →  F2 mod p = {r}')

log(f'')
log(f'نتیجه‌ی مرحله ۱: {len(factors_found_phase1)} فاکتور پیدا شد')
if factors_found_phase1:
    log(f'  فاکتورها: {factors_found_phase1}')
else:
    log(f'  ✗ هیچ‌کدام از این {len(selected_primes)} عدد اول کوچک، F2 را تقسیم نمی‌کند.')
log(f'')

# ============================================================
# Phase 2: Iterate primes of form 2474k + 1 (necessary for q | M(1237))
# ============================================================
log(f'=== مرحله ۲: تکرار با اعداد اول بزرگ‌تر از فرم q = 2474k + 1 ===')
log(f'نکته: هر عامل اول q از M(1237) باید در فرم q ≡ 1 (mod 2474) باشد،')
log(f'      چون ord_q(2) = 1237 باید بر (q-1) بخش‌پذیر باشد.')
log(f'')

# Verify: F1 should be of form 2474k+1
k_F1 = (int(F1) - 1) // 2474
rem_F1 = (int(F1) - 1) % 2474
log(f'بررسی: F1 - 1 = 2474 × {k_F1} + {rem_F1}')
log(f'  پس F1 = 2474 × {k_F1} + 1 (k_F1 = {k_F1}, ~10^{int(math.log10(k_F1))} = ~10^66)')
log(f'  یعنی F1 خودش یک عدد از این فرم است (k = ~10^66)')
log(f'  اما رسیدن به k = 10^66 با تکرار متوالی غیرممکن است.')
log(f'')

# Iterate k = 1, 2, 3, ...
log(f'شروع تکرار از k = 1 تا 10^7 (یا تا زمان‌برآمد بودجه)...')
log(f'')

TIME_BUDGET = 90  # seconds
t_start = time.time()
k = 0
tested_count = 0
prime_count = 0
factors_found_phase2 = []
last_log_time = t_start

while time.time() - t_start < TIME_BUDGET:
    k += 1
    q = 2474 * k + 1
    tested_count += 1
    
    # Quick composite check: skip if q is obviously composite
    # (Use a few small prime divisibility tests first)
    if q % 3 == 0 or q % 5 == 0 or q % 7 == 0 or q % 11 == 0 or q % 13 == 0:
        continue
    if q % 17 == 0 or q % 19 == 0 or q % 23 == 0 or q % 29 == 0 or q % 31 == 0:
        continue
    
    # Full primality test
    if not is_prime(q):
        continue
    prime_count += 1
    
    # Test divisibility of F2 by q
    if F2 % q == 0:
        factors_found_phase2.append((k, q))
        log(f'  >>> k = {k}, q = {q}  ✓✓✓ فاکتور پیدا شد!')
        log(f'      is_prime(q): True')
        log(f'      F2 = q × {F2 // q}')
        # This is a real factor!
    
    # Log progress periodically
    if time.time() - last_log_time > 10:
        elapsed = time.time() - t_start
        log(f'  پیش‌رفت: k = {k}, tested = {tested_count}, primes = {prime_count}, elapsed = {elapsed:.1f}s, factors = {len(factors_found_phase2)}')
        last_log_time = time.time()

elapsed = time.time() - t_start
log(f'')
log(f'پایان مرحله ۲:')
log(f'  k از 1 تا {k}')
log(f'  اعداد آزمایش‌شده: {tested_count}')
log(f'  اعداد اول در این فرم: {prime_count}')
log(f'  فاکتورهای پیدا شده: {len(factors_found_phase2)}')
if factors_found_phase2:
    log(f'  فاکتورها: {factors_found_phase2}')
else:
    log(f'  ✗ هیچ فاکتوری در k ≤ {k} پیدا نشد.')
log(f'')

# ============================================================
# Phase 3: Try larger primes more efficiently using the structure
# Since F1 is 70 digits with k_F1 ~ 10^66, we can't reach there by sequential iteration.
# Instead, let's try a few large k values of "nice" forms (e.g., powers of 10, special forms)
# and just check if they happen to divide F2.
# ============================================================
log(f'=== مرحله ۳: تست چند k بزرگ خاص (با ساختار معنادار) ===')
log(f'')
special_ks = [
    ('10^3', 10**3),
    ('10^4', 10**4),
    ('10^5', 10**5),
    ('10^6', 10**6),
    ('10^7', 10**7),
    ('10^8', 10**8),
    ('10^9', 10**9),
    ('10^10', 10**10),
    ('2^20', 2**20),
    ('2^30', 2**30),
    ('2^40', 2**40),
    ('F1-k (the F1 itself)', k_F1),  # this is F1's k, should give F1 itself
]

for label, k_val in special_ks:
    q = 2474 * k_val + 1
    q_digits = len(str(q))
    is_p = is_prime(q)
    log(f'  k = {label}: q = 2474×k+1 ({q_digits} digits), is_prime = {is_p}')
    if is_p:
        if F2 % q == 0:
            log(f'    >>> ✓✓✓ فاکتور پیدا شد! q = {q}')
            factors_found_phase2.append((label, q))
        else:
            log(f'    → F2 mod q ≠ 0')
    log(f'')

# ============================================================
# Summary
# ============================================================
log(f'=== خلاصه نهایی ===')
log(f'مرحله ۱ (اعداد اول کوچک انتخاب‌شده): {len(factors_found_phase1)} فاکتور')
log(f'مرحله ۲ (k = 1 تا {k}): {len(factors_found_phase2)} فاکتور')
log(f'مرحله ۳ (k های خاص): {len(factors_found_phase2) - len([f for f in factors_found_phase2 if isinstance(f[0], int)])} فاکتور')
log(f'')
total_factors = len(factors_found_phase1) + len(factors_found_phase2)
log(f'مجموع فاکتورهای پیدا شده: {total_factors}')
log(f'')
if total_factors == 0:
    log(f'نتیجه‌گیری ریاضی:')
    log(f'  عوامل اول واقعی F2 همگی بزرگ‌تر از 10^{int(math.log10(k))} + 1 هستند.')
    log(f'  برای پیدا کردن آن‌ها باید از روش‌های پیشرفته (SNFS, ECM با B1 > 10^10) استفاده کرد.')
    log(f'  روش «تقریب log10» فقط یک تقریب عددی است و فاکتورهای واقعی را پیدا نمی‌کند.')

print()
print(f'لاگ کامل ذخیره شد در: {LOG_FILE}')
print(f'تعداد خطوط لاگ: {len(LOG_FILE.read_text().splitlines())}')
