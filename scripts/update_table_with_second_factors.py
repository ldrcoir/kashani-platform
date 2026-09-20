#!/usr/bin/env python3
"""
Update A136030_factors_1_to_8000.txt with the second factors found by log-method.
For composite F2 cases where we found a second factor, record it as the 
second smallest factor (only if smaller than existing entry).
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, next_prime, powmod
import math
import time
from pathlib import Path

# Load known factorizations
FACTORS_FILE = Path('/home/z/my-project/download/A136030_factors_1_to_8000.txt')
lines = FACTORS_FILE.read_text().splitlines()

def log_method_factor(F2, p_index, time_budget=1.5):
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

# Build list of (p, F1) pairs
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

print(f"Loaded {len(mersenne_data)} Mersenne numbers with known F1")

# Process all and find NEW second factors
new_factors = []
total = len(mersenne_data)
processed = 0
total_found = 0
total_failed = 0

t_start = time.time()
for p, F1 in mersenne_data:
    processed += 1
    M = (1 << p) - 1
    if M % F1 != 0: continue
    F2 = M // F1
    
    # Skip if F2 is prime (already complete)
    if is_prime(F2):
        continue
    
    # Apply log method
    second_factor = log_method_factor(F2, p, time_budget=1.0)
    
    if second_factor:
        # Verify: second_factor | F2 and second_factor > F1 (since F1 is smallest)
        if F2 % second_factor == 0 and second_factor > F1:
            # Also check if it's smaller than existing entry in table
            # The table only stores SMALLEST factor, so we can't store second factor
            # But we can verify F1 is still the smallest
            if second_factor > F1:
                # F1 is still smallest (correct), second_factor is the next factor
                new_factors.append({
                    'p': p,
                    'F1': F1,
                    'second_factor': second_factor,
                    'F2_remaining': F2 // second_factor,
                    'F2_remaining_is_prime': is_prime(F2 // second_factor),
                })
                total_found += 1
    else:
        total_failed += 1
    
    if processed % 100 == 0:
        elapsed = time.time() - t_start
        print(f"  progress: {processed}/{total}, found: {total_found}, failed: {total_failed}, elapsed: {elapsed:.1f}s")
    
    # Time budget total: ~100s
    if time.time() - t_start > 90:
        print(f"  Time budget exceeded, stopping at p = {p}")
        break

print()
print(f"Total processed: {processed}")
print(f"Total second factors found: {total_found}")
print(f"Total failed (F2 composite, no factor found): {total_failed}")
print()

# Save results
import json
with open('/home/z/my-project/download/second_factors_found.json', 'w') as f:
    json.dump(new_factors, f, indent=2, default=str)

# Print sample
print("=" * 70)
print(f"نمونه‌ای از عامل‌های دوم پیدا‌شده ({len(new_factors)} total):")
print("=" * 70)
print(f"  {'p':>5} {'F1':>15} {'F2 digits':>10} {'عامل دوم':>20} {'عامل digits':>12} {'F2/عامل prime?':>15}")

for r in new_factors[:30]:
    p = r['p']
    F1 = r['F1']
    sf = r['second_factor']
    f2_remaining = r['F2_remaining']
    f2_rem_prime = '✓' if r['F2_remaining_is_prime'] else '✗'
    F2_digits = len(str(int((1<<p) - 1) // F1))
    print(f"  {p:>5} {str(F1)[:15]:>15} {F2_digits:>10} {str(sf)[:20]:>20} {len(str(sf)):>12} {f2_rem_prime:>15}")
print()

# Count cases where log-method found factor and the rest is PRIME (full factorization achieved)
full_factorizations = sum(1 for r in new_factors if r['F2_remaining_is_prime'])
print(f"  مواردی که F2 = عامل دوم × عدد اول (تجزیه‌ی کامل!): {full_factorizations}")
