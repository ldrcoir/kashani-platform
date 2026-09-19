#!/usr/bin/env python3
"""
Improved version: 
- Start from 80-digit primes (as user requested)
- Sum log10, target = log10(F2)
- Use a smarter strategy: pick 3 random 80-digit primes such that sum < target,
  then fill the gap with smaller primes (63-64 digits, then refine).
- Use a "second chance" approach: if the first 3 leave a gap, also try to
  find a 4th prime (64-digit) whose log10 is just below the gap.
- Then refine with small primes.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, next_prime
import math
import time
import random
from pathlib import Path

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

LOG_FILE = Path('/home/z/my-project/download/prime80_log_v2.txt')
LOG_FILE.write_text('')
def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

log(f'=== تقریب log10(F2) با اعداد اول ۸۰ رقمی ===')
log(f'هدف: log10(F2) = {target:.10f}')
log(f'تعداد ارقام F2: {len(str(F2))}')
log(f'')

def random_prime_with_digits(d):
    low = 10**(d-1)
    high = 10**d - 1
    while True:
        n = random.randint(low, high)
        if n % 2 == 0:
            n += 1
        p = int(next_prime(mpz(n)))
        if p <= high:
            return p

# ============================================================
# Smart strategy: Pick 3 80-digit primes such that their sum_log < target.
# Then fill the gap (~63-64 in log10) with a carefully chosen 64-digit prime.
# Then refine with small primes.
# ============================================================

random.seed(42)  # reproducible

log(f'=== مرحله ۱: انتخاب ۳ عدد اول ۸۰ رقمی (مجموع باید کمتر از هدف باشد) ===')
selected = []
sum_log = 0.0

while len(selected) < 3:
    p = random_prime_with_digits(80)
    lp = math.log10(p)
    # Accept if sum after adding is still less than target with room for more primes
    # (need room for at least 1 more prime with log10 ~63)
    if sum_log + lp < target - 60:  # leave at least 60 in log10 for the 4th prime
        selected.append((p, lp))
        sum_log += lp
        log(f'  [{len(selected)}] p = {str(p)[:30]}...{str(p)[-15:]}')
        log(f'      log10 = {lp:.10f}, جمع = {sum_log:.10f}, باقی‌مانده = {target - sum_log:.10f}')

log(f'')
gap = target - sum_log
gap_digits = int(gap) + 1
log(f'فاصله باقی‌مانده: {gap:.10f}')
log(f'نیاز به عدد اول ~{gap_digits} رقمی')
log(f'')

# ============================================================
# مرحله ۲: پیدا کردن عدد اول با log10 ≈ gap (با حداقل خطا)
# Try multiple random primes, pick the one with log10 closest to (but <=) gap
# ============================================================
log(f'=== مرحله ۲: پیدا کردن عدد اول {gap_digits}-رقمی با log10 ≤ gap ===')

best_p = None
best_lp = 0
best_diff = float('inf')  # gap - lp (positive = under, negative = over)
attempts = 1000

# We want to AVOID overshoot: only accept primes with lp <= gap
log(f'تلاش با {attempts} عدد اول تصادفی...')
overshoot_count = 0
for attempt in range(attempts):
    p = random_prime_with_digits(gap_digits)
    lp = math.log10(p)
    if lp > gap:
        overshoot_count += 1
        # Skip overshoots (we want sum <= target)
        if attempt < 5:
            log(f'  تلاش {attempt+1}: log10 = {lp:.10f} > gap {gap:.10f} (overshoot، رد شد)')
        continue
    diff = gap - lp  # positive (under)
    if diff < best_diff:
        best_diff = diff
        best_p = p
        best_lp = lp
    if attempt < 5 or attempt == attempts - 1:
        log(f'  تلاش {attempt+1}: log10 = {lp:.10f}, diff = {diff:.10f}')

log(f'')
log(f'از {attempts} تلاش: {overshoot_count} overshoot, {attempts - overshoot_count} acceptable')
log(f'بهترین عدد اول {gap_digits}-رقمی:')
log(f'  p = {best_p}')
log(f'  log10(p) = {best_lp:.10f}')
log(f'  diff (gap - log10) = {best_diff:.10f}')
log(f'')

# Add this prime
selected.append((best_p, best_lp))
sum_log += best_lp
log(f'جمع بعد از اضافه کردن: {sum_log:.10f}, باقی‌مانده: {target - sum_log:.10f}')
log(f'')

# ============================================================
# مرحله ۳: تنظیم دقیق با اعداد اول کوچک‌تر
# ============================================================
log(f'=== مرحله ۳: تنظیم دقیق با اعداد اول کوچک ===')
remaining = target - sum_log
log(f'فاصله باقی‌مانده: {remaining:.10f}')
log(f'')

def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

# Try larger pool of small primes (up to 100000) for finer precision
small_primes = small_primes_up_to(100000)
small_primes_no2 = [p for p in small_primes if p != 2]
log(f'اعداد اول کوچک (تا 100000، بدون ۲): {len(small_primes_no2)}')

# Greedy descending
small_selected = []
cur_remaining = remaining
for p in sorted(small_primes_no2, reverse=True):
    lp = math.log10(p)
    if lp <= cur_remaining + 1e-12:
        small_selected.append(p)
        cur_remaining -= lp

log(f'  اعداد کوچک انتخاب‌شده: {len(small_selected)} عدد')
log(f'  اولین‌های کوچک: {small_selected[:10]}...')
log(f'  جمع log10 اینها = {sum(math.log10(p) for p in small_selected):.10f}')
log(f'  فاصله نهایی = {cur_remaining:.10e}')
log(f'')

# Refinement: swap small primes to reduce error further
def refine_small(target_remaining, selected_small, all_small_primes, log10_small, iterations=50000):
    cur_sum = sum(math.log10(p) for p in selected_small)
    cur_error = target_remaining - cur_sum  # error after small primes
    selected_set = set(selected_small)
    
    sorted_pairs = sorted(zip(log10_small, all_small_primes))
    sorted_logs = [lp for lp, _ in sorted_pairs]
    import bisect
    
    for it in range(iterations):
        if abs(cur_error) < 1e-12:
            break
        
        best_improvement = 1e-15
        best_op = None
        
        # Try add (only if cur_error > 0)
        if cur_error > 0:
            for p, lp in zip(all_small_primes, log10_small):
                if p in selected_set: continue
                if lp <= cur_error + 1e-15:
                    new_error = cur_error - lp
                    improvement = abs(cur_error) - abs(new_error)
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_op = ('add', p, lp)
        
        # Try swap
        for p1 in list(selected_set):
            lp1 = math.log10(p1)
            want = lp1 + cur_error
            idx = bisect.bisect_left(sorted_logs, want)
            for di in [-1, 0, 1]:
                ii = idx + di
                if 0 <= ii < len(sorted_pairs):
                    lp2, p2 = sorted_pairs[ii]
                    if p2 in selected_set or p2 == p1:
                        continue
                    delta = lp2 - lp1
                    new_error = cur_error - delta
                    improvement = abs(cur_error) - abs(new_error)
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_op = ('swap', p1, p2, lp1, lp2)
        
        # Try remove (if cur_error < 0)
        if cur_error < 0:
            for p1 in list(selected_set):
                lp1 = math.log10(p1)
                if lp1 <= -cur_error + 1e-15:
                    new_error = cur_error + lp1
                    improvement = abs(cur_error) - abs(new_error)
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_op = ('remove', p1, lp1)
        
        if best_op is None:
            break
        op = best_op[0]
        if op == 'add':
            _, p, lp = best_op
            selected_set.add(p)
            cur_error -= lp
        elif op == 'swap':
            _, p1, p2, lp1, lp2 = best_op
            selected_set.remove(p1)
            selected_set.add(p2)
            cur_error -= (lp2 - lp1)
        elif op == 'remove':
            _, p1, lp1 = best_op
            selected_set.remove(p1)
            cur_error += lp1
    
    return sorted(selected_set), sum(math.log10(p) for p in selected_set)

log(f'اعمال تنظیم دقیق (50k تکرار)...')
refined_small, refined_sum = refine_small(remaining, small_selected, small_primes_no2, [math.log10(p) for p in small_primes_no2], 50000)
log(f'  بعد از تنظیم: {len(refined_small)} عدد کوچک, جمع = {refined_sum:.10f}')
log(f'')

primes_final = [p for p, _ in selected] + refined_small
final_sum = sum_log + refined_sum
log(f'=== نتیجه‌ی نهایی ===')
log(f'جمع کل log10 = {final_sum:.10f}')
log(f'هدف = {target:.10f}')
log(f'خطای نهایی = {target - final_sum:.10e}')
log(f'')

log(f'اعداد اول استفاده‌شده:')
for i, p in enumerate(primes_final):
    lp = math.log10(p)
    if len(str(p)) > 30:
        log(f'  [{i+1}] {len(str(p))}-digit prime: {str(p)[:20]}...{str(p)[-10:]}, log10 = {lp:.10f}')
    else:
        log(f'  [{i+1}] p = {p} ({len(str(p))} digits, log10 = {lp:.10f})')
log(f'')

log(f'گروه‌بندی:')
log(f'  80-digit primes: {sum(1 for p in primes_final if 80 <= len(str(p)) <= 81)}')
log(f'  64-66 digit primes: {sum(1 for p in primes_final if 64 <= len(str(p)) <= 66)}')
log(f'  small primes (< 100000): {sum(1 for p in primes_final if p < 100000)}')
log(f'  total: {len(primes_final)}')
log(f'')

# Compute product
product = mpz(1)
for p in primes_final:
    product *= mpz(p)
log(f'محصول ∏ pᵢ: {str(product)[:60]}... ({len(str(product))} digits)')
log(f'log10(∏ pᵢ) = {math.log10(int(product)):.10f}')
log(f'نسبت ∏ pᵢ / F2 ≈ {10**(math.log10(int(product)) - log10_F2):.6e}')
log(f'')

# Divisibility
if F2 % product == 0:
    q = F2 // product
    log(f'  ✓ F2 = ∏ pᵢ × q, q = {q}')
    log(f'  is_prime(q): {is_prime(q)}')
else:
    rem = F2 % product
    log(f'  ✗ F2 بر ∏ pᵢ بخش‌پذیر نیست (remainder = {str(rem)[:50]}...)')

# Update the JSON file for the webpage to show this new result
import json
results = {
    "metadata": {
        "p": 1237,
        "F1_digits": len(str(F1)),
        "F2_digits": len(str(F2)),
        "F1_first_50": str(F1)[:50],
        "F1_last_20": str(F1)[-20:],
        "F2_first_50": str(F2)[:50],
        "F2_last_20": str(F2)[-20:],
        "log10_F1": float(mpmath.log10(int(F1))),
        "log10_F2": log10_F2,
        "diff": log10_F2 - float(mpmath.log10(int(F1))),
        "target": log10_F2,
        "computed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    },
    "strategies": [
        {
            "name": "Strategy A: Greedy Ascending (primes up to 100000)",
            "description": "Use primes 2, 3, 5, 7, ... in increasing order; add each if it doesn't overshoot",
            "prime_count": 0,
            "sum": 0,
            "error": 0,
            "primes": [],
            "log10_values": [],
            "cumulative_sum": [],
        },
        {
            "name": f"Strategy B: 3×80-digit primes + 1×{gap_digits}-digit prime + small refinement (NEW)",
            "description": f"Start from 80-digit primes, sum log10 to approach log10(F2)={log10_F2:.4f}, then refine with small primes",
            "prime_count": len(primes_final),
            "sum": final_sum,
            "error": target - final_sum,
            "primes": primes_final,
            "log10_values": [math.log10(p) for p in primes_final],
            "cumulative_sum": [],
        },
    ]
}
# Compute cumulative sums for the chart
cum = 0
for p in primes_final:
    cum += math.log10(p)
    results["strategies"][1]["cumulative_sum"].append(cum)

# Best strategy is the new one (B)
results["best_strategy_index"] = 1

# Save
with open('/home/z/my-project/public/log10_data.json', 'w') as f:
    json.dump(results, f, indent=2)
with open('/home/z/my-project/download/log10_factorization_results.json', 'w') as f:
    json.dump(results, f, indent=2)
log(f'')
log(f'فایل JSON به‌روزرسانی شد برای صفحه‌ی وب.')
