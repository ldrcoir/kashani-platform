#!/usr/bin/env python3
"""
Extended log-method: increase time budget for failed cases.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, next_prime, powmod
import math
import time
import json
from pathlib import Path

print("روش لگاریتمی گسترش‌یافته — بودجه‌ی زمانی بیشتر")
print("=" * 70)

# Load known factorizations
FACTORS_FILE = Path('/home/z/my-project/download/A136030_factors_1_to_8000.txt')
lines = FACTORS_FILE.read_text().splitlines()

mersenne_data = []
for line in lines:
    if line.startswith('#'): continue
    parts = line.split('\t')
    if len(parts) < 2: continue
    p_str, q_str = parts[0], parts[1].strip()
    if q_str in ('0', '-1'): continue
    p = int(p_str)
    q_val = int(q_str)
    if not is_prime(p): continue
    if powmod(2, p, q_val) != 1: continue
    mersenne_data.append((p, q_val))

print(f"Loaded {len(mersenne_data)} Mersenne numbers")

# Try with 5 second budget on the previously-failed cases
def log_method_factor(F2, p_index, time_budget=5.0):
    t0 = time.time()
    two_p = 2 * p_index
    
    for k in range(1, 10**8 + 1):
        q = two_p * k + 1
        if q % 3 == 0 or q % 5 == 0 or q % 7 == 0 or q % 11 == 0 or q % 13 == 0:
            continue
        if not is_prime(q): continue
        if F2 % q == 0:
            return q
        if time.time() - t0 > time_budget:
            return None
    return None

# Run on a wider range with longer time budget
results = []
total_time_start = time.time()
target_count = 50  # how many to process

# Sort by F2 size (smallest first)
mersenne_data_with_F2 = []
for p, F1 in mersenne_data:
    M = (1 << p) - 1
    if M % F1 != 0: continue
    F2 = M // F1
    if is_prime(F2): continue  # skip if F2 is prime
    mersenne_data_with_F2.append((p, F1, F2))

print(f"Mersenne numbers with composite F2: {len(mersenne_data_with_F2)}")
print()

# Try the first 50 (smallest p first)
mersenne_data_with_F2.sort(key=lambda x: x[0])
print(f"Testing first {target_count} (smallest p)...")
print()

for p, F1, F2 in mersenne_data_with_F2[:target_count]:
    t0 = time.time()
    second_factor = log_method_factor(F2, p, time_budget=2.0)
    elapsed = time.time() - t0
    
    f2_digits = len(str(F2))
    if second_factor:
        print(f"  p={p:>4}: F2 ({f2_digits} digits) → عامل: {second_factor} ({len(str(second_factor))} digits) (elapsed {elapsed:.2f}s)")
        results.append({
            'p': p, 'F1': F1, 'F1_digits': len(str(F1)), 
            'F2_digits': f2_digits, 'second_factor': second_factor,
            'time': elapsed
        })
    else:
        print(f"  p={p:>4}: F2 ({f2_digits} digits) → ✗ not found (elapsed {elapsed:.2f}s)")

print()
print("=" * 70)
print("خلاصه")
print("=" * 70)
print()
found = len(results)
not_found = target_count - found
print(f"تعداد پردازش‌شده: {target_count}")
print(f"عامل دوم پیدا شد: {found}")
print(f"پیدا نشد: {not_found}")
print(f"نرخ موفقیت: {found/target_count*100:.1f}%")
print()

if results:
    print("موفقیت‌ها:")
    for r in results:
        print(f"  p = {r['p']}: عامل دوم = {r['second_factor']} ({len(str(r['second_factor']))} digits, time: {r['time']:.2f}s)")

# Save
with open('/home/z/my-project/download/log_method_extended.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
