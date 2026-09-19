#!/usr/bin/env python3
"""
User's request:
1. Remove log(2) from the sum (i.e., exclude p=2 from the primes list)
2. Target the sum to approach log10(F2) directly (not log10(F2/F1))
   i.e., target = log10(F2) ≈ 302.97
3. Then perform division: F2 / product_of_primes
4. Check if mathematically sound

Mathematical analysis:
- We want Σ log10(p_i) ≈ log10(F2)
- This means ∏ p_i ≈ F2
- Equivalently: F2 / ∏ p_i ≈ 1
- If exactly: F2 = ∏ p_i, then F2 is divided into primes (full factorization!)
- But F2 is 303 digits, so we need many primes (or large primes)
- The product of all primes up to X has log10 ≈ X/ln(10) ≈ 0.4343 * X
- For target = 302.97: X ≈ 302.97 / 0.4343 ≈ 697.6
- So we need primes up to ~700 to get sum ≈ 303
- But this gives an APPROXIMATION, not exact factorization
- F2's actual prime factors are huge (each > 10^70 likely)
- So small primes (up to 700) won't exactly divide F2

But the user wants to:
- Take the product of these small primes (which is close to F2 in log10)
- Compute F2 / product and see what happens
- The result will be F2 / product ≈ some number close to 1
- This is NOT a factorization of F2 — it's a ratio

Still, let's do it and show the result.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, invert, powmod, jacobi, isqrt
import math
import json
import time
from pathlib import Path

# Setup
P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1

# High-precision log10
try:
    import mpmath
    mpmath.mp.dps = 80
    log10_F1 = float(mpmath.log10(int(F1)))
    log10_F2 = float(mpmath.log10(int(F2)))
except ImportError:
    log10_F1 = math.log10(int(F1))
    log10_F2 = math.log10(int(F2))

print("=" * 70)
print("  بررسی درخواست: حذف log(2) و هدف‌گذاری روی log10(F2)")
print("=" * 70)
print()
print(f"F1 = {F1} ({len(str(F1))} digits, prime: {is_prime(F1)})")
print(f"F2 = M(1237)/F1 ({len(str(F2))} digits, prime: {is_prime(F2)})")
print(f"log10(F1) = {log10_F1:.10f}")
print(f"log10(F2) = {log10_F2:.10f}")
print()

# ============================================================
# Mathematical analysis (BEFORE running the algorithm)
# ============================================================
print("=" * 70)
print("  تحلیل ریاضی پیش از اجرا")
print("=" * 70)
print()
print("هدف: Σ log10(pᵢ) ≈ log10(F2)")
print("یعنی: ∏ pᵢ ≈ F2")
print("یعنی: F2 / ∏ pᵢ ≈ 1")
print()
print("نکته مهم:")
print("- F2 یک عدد ۳۰۳ رقمی مرکب است.")
print("- اگر ∏ pᵢ = F2 دقیقاً، آن‌گاه F2 به عوامل اول کوچک تجزیه شده است.")
print("- ولی عوامل اول واقعی F2 بسیار بزرگ هستند (احتمالاً > 10^70).")
print("- پس هیچ جمعی از log10 اعداد اول کوچک (مثلاً تا 1000) دقیقاً برابر log10(F2) نخواهد بود.")
print("- بهترین حالت: تقریب با خطای بسیار کوچک (مثلاً 10^-6).")
print("- در این حالت: F2 / ∏ pᵢ ≈ 1.000... یا 0.999...")
print("- این تقسیم یک عدد first rational (نزدیک به 1) می‌دهد، نه یک فاکتور اول F2.")
print()
print("نتیجه‌ی ریاضی: این روش عوامل اول F2 را پیدا نمی‌کند.")
print("اما می‌توانیم تقسیم را انجام دهیم و نتیجه را ببینیم.")
print()

# ============================================================
# Algorithm: greedy ascending, exclude 2, target log10(F2)
# ============================================================
print("=" * 70)
print("  اجرا: حریصانه کوچک→بزرگ، بدون ۲، هدف log10(F2)")
print("=" * 70)
print()

def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

PRIME_LIMIT = 100000
all_primes = small_primes_up_to(PRIME_LIMIT)
# EXCLUDE p=2
primes_no2 = [p for p in all_primes if p != 2]
log10_primes_no2 = [math.log10(p) for p in primes_no2]
print(f"Generated {len(primes_no2)} primes up to {PRIME_LIMIT} (excluding 2)")

target = log10_F2
print(f"Target = log10(F2) = {target:.10f}")
print()

# Greedy ascending (no 2)
def greedy_asc(target, primes, log10_primes):
    sum_log = 0.0
    selected = []
    for p, lp in zip(primes, log10_primes):
        if sum_log + lp <= target + 1e-12:
            sum_log += lp
            selected.append(p)
    return sum_log, selected

t0 = time.time()
sum_greedy, sel_greedy = greedy_asc(target, primes_no2, log10_primes_no2)
t1 = time.time()
print(f"Greedy ascending (no 2): {len(sel_greedy)} primes, sum = {sum_greedy:.10f}")
print(f"  Target: {target:.10f}")
print(f"  Error: {target - sum_greedy:.10f}")
print(f"  Time: {t1-t0:.3f}s")
print()

# Now refine
def refine_heavy(target, selected_primes, all_primes, log10_primes, iterations=200000):
    current_sum = sum(math.log10(p) for p in selected_primes)
    selected_set = set(selected_primes)
    sorted_with_log = sorted([(lp, p) for p, lp in zip(all_primes, log10_primes)])
    sorted_logs = [lp for lp, _ in sorted_with_log]
    import bisect
    
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

print("Refining (200k iterations)...")
t0 = time.time()
sum_refined, sel_refined = refine_heavy(target, sel_greedy, primes_no2, log10_primes_no2, iterations=200000)
t1 = time.time()
print(f"Refined: {len(sel_refined)} primes, sum = {sum_refined:.10f}")
print(f"  Target: {target:.10f}")
print(f"  Error: {target - sum_refined:.10e}")
print(f"  Time: {t1-t0:.3f}s")
print()

# ============================================================
# THE DIVISION: F2 / product
# ============================================================
print("=" * 70)
print("  تقسیم: F2 ÷ ∏ pᵢ")
print("=" * 70)
print()

product = mpz(1)
for p in sel_refined:
    product *= mpz(p)

print(f"تعداد اعداد اول انتخاب‌شده: {len(sel_refined)}")
print(f"∫ pᵢ = {str(product)[:60]}... ({len(str(product))} digits)")
print(f"log10(∏ pᵢ) = {math.log10(int(product)):.10f}")
print(f"log10(F2)   = {log10_F2:.10f}")
print(f"diff (log10) = {log10_F2 - math.log10(int(product)):.10e}")
print()

# Integer division
print("تقسیم صحیح:")
quotient = F2 // product
remainder = F2 % product
print(f"  F2 ÷ ∏ pᵢ = {quotient}")
print(f"  F2 mod ∏ pᵢ = {remainder}")
print(f"  quotient digits: {len(str(quotient))}")
print(f"  remainder digits: {len(str(remainder))}")
print()

# Is the quotient prime?
if quotient > 1:
    print(f"  is_prime(quotient): {is_prime(quotient)}")
    
# Is remainder 0?
if remainder == 0:
    print(f"  ✓ F2 = ∏ pᵢ × quotient")
    print(f"  اگر quotient اول باشد، تجزیه‌ی کامل F2 داریم!")
else:
    print(f"  ✗ F2 بر ∏ pᵢ بخش‌پذیر نیست (remainder ≠ 0)")
    
    # Compute the ratio F2 / product as a real number
    log10_ratio = log10_F2 - math.log10(int(product))
    print(f"  F2 / ∏ pᵢ ≈ 10^({log10_ratio:.6f}) ≈ {10**log10_ratio:.6f}")
    print()

# ============================================================
# Check: does any prime q (large) make (product * q) | F2?
# Equivalently: q | (F2 / product) ... but this is fractional.
# Try: does quotient divide F2? quotient = F2 // product.
# F2 = quotient * product + remainder
# If q | quotient and q | F2 - remainder, then q | F2 (if also q | remainder... not quite)
# 
# The real test: take gcd(quotient, F2) — if quotient has a factor in common with F2,
# that's a factor of F2 we missed!
# ============================================================
print("=" * 70)
print("  بررسی: آیا quotient با F2 مقسوم‌علیه مشترک دارد؟")
print("=" * 70)
print()
g_q_F2 = gcd(quotient, F2)
print(f"gcd(quotient, F2) = {g_q_F2}")
print(f"  digits: {len(str(g_q_F2))}")
print(f"  is 1? {g_q_F2 == 1}")
print(f"  is F2? {g_q_F2 == F2}")
if g_q_F2 > 1 and g_q_F2 < F2:
    print(f"  ✓ عامل F2 پیدا شد! = {g_q_F2}")
    print(f"  is_prime: {is_prime(g_q_F2)}")
else:
    print(f"  ✗ quotient و F2 coprime هستند (هیچ فاکتور مشترکی ندارند)")
    
print()
print("=" * 70)
print("  تحلیل نهایی")
print("=" * 70)
print()
print("""
از نظر ریاضی:
- روش «تقریب log10» فقط یک تقریب عددی است.
- عوامل اول واقعی F2 اعداد بزرگ (احتمالاً > 10^70) هستند.
- انتخاب اعداد اول کوچک (تا 100000) فقط log10(F2) را تقریب می‌زند،
  ولی این اعداد اول به‌طور واقعی F2 را تشکیل نمی‌دهند.
- وقتی F2 ÷ ∏ pᵢ را حساب می‌کنیم:
  * اگر remainder = 0: یعنی ∏ pᵢ دقیقاً F2 را تقسیم می‌کند (ولی این بعید است)
  * اگر remainder ≠ 0: quotient یک عدد بزرگ می‌شود که با F2 coprime است
- به طور خلاصه: این روش عوامل اول F2 را پیدا نمی‌کند.

پیشنهاد: برای پیدا کردن عوامل اول واقعی F2 باید از روش‌های 
تخصصی تجزیه (SNFS, ECM با B1 > 10^10) استفاده کرد.
""")
