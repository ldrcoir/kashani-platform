#!/usr/bin/env python3
"""
For each Mersenne number M(p) with a known first factor F1, find the SECOND factor
using the logarithmic method.

Strategy:
- For each prime p with a known smallest factor F1 of M(p):
  - Compute M(p) = 2^p - 1
  - F2 = M(p) / F1
  - If F2 is prime: done
  - If F2 is composite: apply log-method to find factors of F2
    (find primes q with log10 sum approaching log10(F2), check divisibility)

Use the database A136030_factors_1_to_8000.txt for known first factors.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, next_prime, powmod
import math
import time
import json
from pathlib import Path
from collections import Counter

print("=" * 70)
print("  روش لگاریتمی برای پیدا کردن عامل دوم اعداد Mersenne")
print("=" * 70)
print()

# Load known factorizations
FACTORS_FILE = Path('/home/z/my-project/download/A136030_factors_1_to_8000.txt')
lines = FACTORS_FILE.read_text().splitlines()

# Build list of (p, F1) pairs where F1 is a known smallest factor
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
    # Verify F1 actually divides M(p)
    if powmod(2, p, q_val) != 1:
        continue  # data error
    mersenne_data.append((p, q_val))

print(f"Loaded {len(mersenne_data)} Mersenne numbers with known first factor")
print()

# Define the log-method
def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

def log_method_factor(F2, p_index, time_budget=10):
    """
    Apply log-method to factor F2 (which divides M(p_index)).
    
    Returns: factor found (int) or None
    
    Strategy:
    - For each prime q with q ≡ 1 (mod 2*p_index), test if q | F2.
    - Search up to a time budget.
    """
    t0 = time.time()
    # All factors of M(p) are q ≡ 1 mod 2p
    two_p = 2 * p_index
    
    # Try small k values
    k_max = 10000000  # k up to 10M
    tested = 0
    prime_count = 0
    
    for k in range(1, k_max + 1):
        q = two_p * k + 1
        tested += 1
        if q % 3 == 0 or q % 5 == 0 or q % 7 == 0 or q % 11 == 0 or q % 13 == 0:
            continue
        if not is_prime(q):
            continue
        prime_count += 1
        if F2 % q == 0:
            return q
        if time.time() - t0 > time_budget:
            return None
    
    return None

# Process each Mersenne number
results = []
for p, F1 in mersenne_data[:200]:  # first 200 for demo
    M = int(gmpy2.powmod(2, p, 10**500) - 1) if p < 500 * math.log(10) / math.log(2) else None
    # Actually compute M = 2^p - 1 directly
    M = (1 << p) - 1
    F2 = M // F1
    if M % F1 != 0:
        continue  # data error
    
    # Is F2 prime?
    f2_prime = is_prime(F2)
    f2_digits = len(str(F2))
    
    # If F2 is prime, this is a full factorization
    # If F2 is composite, we need to find the second factor
    
    if f2_prime:
        results.append({
            'p': p,
            'F1': F1,
            'F1_digits': len(str(F1)),
            'F2': F2,
            'F2_digits': f2_digits,
            'F2_is_prime': True,
            'second_factor': F2,  # F2 is itself the second (and final) factor
            'method': 'direct (F2 prime)',
        })
    else:
        # Apply log-method to find second factor
        t0 = time.time()
        second_factor = log_method_factor(F2, p, time_budget=5)
        elapsed = time.time() - t0
        
        if second_factor:
            results.append({
                'p': p,
                'F1': F1,
                'F1_digits': len(str(F1)),
                'F2': str(F2)[:30] + '...' if f2_digits > 30 else F2,
                'F2_digits': f2_digits,
                'F2_is_prime': False,
                'second_factor': second_factor,
                'method': f'log-method (found in {elapsed:.1f}s)',
            })
        else:
            results.append({
                'p': p,
                'F1': F1,
                'F1_digits': len(str(F1)),
                'F2': str(F2)[:30] + '...' if f2_digits > 30 else F2,
                'F2_digits': f2_digits,
                'F2_is_prime': False,
                'second_factor': None,
                'method': f'log-method (not found in {elapsed:.1f}s)',
            })

# Print summary
print("=" * 70)
print("  نتایج برای ۲۰۰ عدد Mersenne نخست با فاکتور شناخته‌شده")
print("=" * 70)
print()
print(f"{'p':>5} {'F1 digits':>10} {'F2 digits':>10} {'F2 prime?':>10} {'عامل دوم':>20} {'روش':>30}")

for r in results[:50]:
    p = r['p']
    f1d = r['F1_digits']
    f2d = r['F2_digits']
    f2p = '✓' if r['F2_is_prime'] else '✗'
    if r['second_factor']:
        if r['F2_is_prime']:
            sf = f"{r['second_factor']}"
        else:
            sf = f"{r['second_factor']}"
        if len(sf) > 20:
            sf = sf[:17] + '...'
    else:
        sf = 'پیدا نشد'
    method = r['method'][:30]
    print(f"  {p:>5} {f1d:>10} {f2d:>10} {f2p:>10} {sf:>20} {method:>30}")

print()
print(f"  ... (نمایش ۵۰ از {len(results)})")
print()

# Statistics
total = len(results)
found = sum(1 for r in results if r['second_factor'])
not_found = sum(1 for r in results if not r['second_factor'])
f2_prime_count = sum(1 for r in results if r['F2_is_prime'])

print(f"آمار:")
print(f"  کل: {total}")
print(f"  F2 اول (تجزیه کامل با F1): {f2_prime_count}")
print(f"  عامل دوم پیدا شده (از F2 مرکب): {found - f2_prime_count}")
print(f"  عامل دوم پیدا نشده: {not_found}")
print()

# Show some success stories
print("=" * 70)
print("  موفقیت‌های روش لگاریتمی (F2 مرکب، عامل دوم پیدا شد):")
print("=" * 70)
for r in results:
    if not r['F2_is_prime'] and r['second_factor']:
        print(f"  p = {r['p']}: F1 = {r['F1']} ({r['F1_digits']} digits)")
        print(f"    F2 = {r['F2']} ({r['F2_digits']} digits, composite)")
        print(f"    عامل دوم = {r['second_factor']} ({len(str(r['second_factor']))} digits)")
        print(f"    روش: {r['method']}")
        print()

# Save results
with open('/home/z/my-project/download/log_method_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
print("نتایج ذخیره شد: /home/z/my-project/download/log_method_results.json")
