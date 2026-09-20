#!/usr/bin/env python3
"""
Faster version: Apply log method to many Mersenne numbers.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, next_prime, powmod
import math
import time
import json
from pathlib import Path

print("روش لگاریتمی برای عامل دوم اعداد Mersenne")
print("=" * 70)
print()

# Load known factorizations
FACTORS_FILE = Path('/home/z/my-project/download/A136030_factors_1_to_8000.txt')
lines = FACTORS_FILE.read_text().splitlines()

# Build list of (p, F1) pairs
mersenne_data = []
for line in lines:
    if line.startswith('#'):
        continue
    parts = line.split('\t')
    if len(parts) < 2:
        continue
    p_str, q_str = parts[0], parts[1].strip()
    if q_str in ('0', '-1'):
        continue
    p = int(p_str)
    q_val = int(q_str)
    if not is_prime(p):
        continue
    if powmod(2, p, q_val) != 1:
        continue
    mersenne_data.append((p, q_val))

print(f"Loaded {len(mersenne_data)} Mersenne numbers with known first factor")
print()

# Log method: try q = 2p*k + 1 for k = 1, 2, ...
def log_method_factor(F2, p_index, time_budget=2.0, k_max=10**7):
    """Find a factor q of F2 where q = 2p*k + 1."""
    t0 = time.time()
    two_p = 2 * p_index
    
    for k in range(1, k_max + 1):
        q = two_p * k + 1
        # Quick composite filter
        if q % 3 == 0 or q % 5 == 0 or q % 7 == 0 or q % 11 == 0 or q % 13 == 0:
            continue
        if not is_prime(q):
            continue
        if F2 % q == 0:
            return q
        if time.time() - t0 > time_budget:
            return None
    return None

# Process all Mersenne numbers
results = []
total = len(mersenne_data)
processed = 0
t_start = time.time()

for p, F1 in mersenne_data:
    processed += 1
    if processed > 300:  # limit for demo
        break
    
    M = (1 << p) - 1
    if M % F1 != 0:
        continue
    F2 = M // F1
    f2_digits = len(str(F2))
    
    # Skip if F2 is too large for trial division (> ~200 digits)
    if f2_digits > 200:
        # Just check if F2 is prime
        f2_prime = is_prime(F2)
        results.append({
            'p': p,
            'F1': F1,
            'F1_digits': len(str(F1)),
            'F2_digits': f2_digits,
            'F2_is_prime': f2_prime,
            'second_factor': F2 if f2_prime else None,
            'method': 'F2 prime (no need for log method)' if f2_prime else 'F2 too large for log method',
        })
        continue
    
    f2_prime = is_prime(F2)
    
    if f2_prime:
        results.append({
            'p': p,
            'F1': F1,
            'F1_digits': len(str(F1)),
            'F2_digits': f2_digits,
            'F2_is_prime': True,
            'second_factor': F2,
            'method': 'direct (F2 prime)',
        })
    else:
        # Apply log method
        t0 = time.time()
        second_factor = log_method_factor(F2, p, time_budget=2.0)
        elapsed = time.time() - t0
        
        if second_factor:
            results.append({
                'p': p,
                'F1': F1,
                'F1_digits': len(str(F1)),
                'F2_digits': f2_digits,
                'F2_is_prime': False,
                'second_factor': second_factor,
                'method': f'log-method (found in {elapsed:.2f}s)',
            })
        else:
            results.append({
                'p': p,
                'F1': F1,
                'F1_digits': len(str(F1)),
                'F2_digits': f2_digits,
                'F2_is_prime': False,
                'second_factor': None,
                'method': f'log-method (not found in {elapsed:.2f}s)',
            })
    
    # Print progress every 20
    if processed % 20 == 0:
        elapsed = time.time() - t_start
        print(f"  progress: {processed}/{total}, elapsed {elapsed:.1f}s")

print()
print("=" * 70)
print("  نتایج نمونه")
print("=" * 70)
print()

# Stats
total_done = len(results)
found_via_log = sum(1 for r in results if not r['F2_is_prime'] and r['second_factor'])
f2_prime_count = sum(1 for r in results if r['F2_is_prime'])
not_found = sum(1 for r in results if not r['F2_is_prime'] and not r['second_factor'])

print(f"آمار:")
print(f"  کل پردازش‌شده: {total_done}")
print(f"  F2 اول (تجزیه کامل با F1): {f2_prime_count}")
print(f"  عامل دوم با log-method پیدا شد: {found_via_log}")
print(f"  عامل دوم پیدا نشد: {not_found}")
print()

# Show first 20 results
print("۲۰ مورد نخست:")
print(f"  {'p':>5} {'F1 dig':>7} {'F2 dig':>7} {'F2 prime':>9} {'عامل دوم':>20} {'روش':>30}")
for r in results[:20]:
    p = r['p']
    f1d = r['F1_digits']
    f2d = r['F2_digits']
    f2p = '✓' if r['F2_is_prime'] else '✗'
    sf = str(r['second_factor'])[:17] + '...' if r['second_factor'] and len(str(r['second_factor'])) > 20 else str(r['second_factor']) if r['second_factor'] else 'پیدا نشد'
    method = r['method'][:30]
    print(f"  {p:>5} {f1d:>7} {f2d:>7} {f2p:>9} {sf:>20} {method:>30}")
print()

# Success stories
print("=" * 70)
print("  موفقیت‌های log-method (F2 مرکب، عامل پیدا شد):")
print("=" * 70)
success_count = 0
for r in results:
    if not r['F2_is_prime'] and r['second_factor'] and success_count < 30:
        print(f"  p = {r['p']}: F1 = {r['F1']} ({r['F1_digits']} digits), F2 = ... ({r['F2_digits']} digits)")
        print(f"    عامل دوم = {r['second_factor']} ({len(str(r['second_factor']))} digits, prime: {is_prime(r['second_factor'])})")
        print(f"    روش: {r['method']}")
        print()
        success_count += 1

print(f"جمعاً {success_count} مورد نمایش داده شد")
print()

# Save results
with open('/home/z/my-project/download/log_method_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
print("نتایج ذخیره شد: /home/z/my-project/download/log_method_results.json")
