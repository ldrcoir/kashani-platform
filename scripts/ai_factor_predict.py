#!/usr/bin/env python3
"""
Train an ML model to predict "promising k values" for Mersenne factor search.

Setup:
- For each known factor q of M(p) (where p is a Mersenne prime index), 
  k = (q - 1) / (2*p). 
- This k has structure: k = small factors * prime etc.
- ML task: predict which k values are most likely to yield factors.

We use existing data:
- A136030_factors_1_to_8000.txt: known smallest factors of M(p) for p in 1..8000.
- For each p with a known factor q, compute k = (q - 1) / (2*p) — this is the 
  "structure multiplier".
- Train a model on (p, k) pairs.

Then for F2 (p=1237), we don't know q. But we know q ≡ 1 mod 2474 = 2*p.
So k = (q - 1) / 2474 is unknown. We want to predict "promising" k values.

Approach:
- Features of k: 
  * k mod 2, mod 3, mod 5, mod 7, ...
  * k is prime?
  * k is smooth (small prime factorization)?
  * k has factor 1237?
  * k is a perfect square?
  * k = 2^j?
- Target: did this k yield a factor for some p?

For p = 1237, we don't have labeled data (no known factor of F2).
But we can train on ALL (p, k) pairs from known Mersenne factors and see 
which k features are most common.

This is a HEURISTIC approach — it won't find the exact factor of F2, 
but it can help us PRIORITIZE which k values to test.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod
import math
import time
import json
import random
from pathlib import Path
from collections import defaultdict, Counter

print("=" * 70)
print("  آموزش مدل ML برای پیش‌بینی k های امیدبخش برای فاکتورهای Mersenne")
print("=" * 70)
print()

# ============================================================
# Load data: A136030 factors
# ============================================================
FACTORS_FILE = Path('/home/z/my-project/download/A136030_factors_1_to_8000.txt')
lines = FACTORS_FILE.read_text().splitlines()

# Build (p, q, k) triples where k = (q-1)/(2p) and q is a known factor of M(p)
data = []
for line in lines:
    if line.startswith('#'):
        continue
    parts = line.split('\t')
    if len(parts) < 2:
        continue
    p_str, q_str = parts[0], parts[1].strip()
    p = int(p_str)
    q_val = int(q_str) if q_str not in ('0', '-1') else None
    if q_val is None or q_val == 0:
        continue
    if not is_prime(p):
        continue  # only Mersenne prime indices
    if q_val == 0:  # M(p) is Mersenne prime
        continue
    # Verify: q_val | M(p)?
    if powmod(2, p, q_val) != 1:
        continue  # data error
    # Compute k = (q_val - 1) / (2*p)
    if (q_val - 1) % (2 * p) != 0:
        continue
    k = (q_val - 1) // (2 * p)
    data.append((p, q_val, k))

print(f"Loaded {len(data)} (p, q, k) triples from known Mersenne factorizations")
print(f"Sample (first 10):")
for i, (p, q, k) in enumerate(data[:10]):
    print(f"  p={p}, q={q}, k={k}")
print()

# ============================================================
# Feature engineering for k values
# ============================================================
print("=" * 70)
print("  استخراج features از k ها")
print("=" * 70)
print()

def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

small_primes = small_primes_up_to(100)

def extract_features(k):
    """Extract features from k value."""
    if k == 0:
        return {'k': 0}
    
    features = {}
    features['k'] = k
    features['log10_k'] = math.log10(k) if k > 0 else -1
    features['digits_k'] = len(str(k))
    
    # Modular features
    for p in small_primes:
        features[f'k_mod_{p}'] = k % p
    
    # Structural features
    features['is_prime'] = 1 if is_prime(k) else 0
    features['is_perfect_square'] = 1 if int(math.isqrt(k))**2 == k else 0
    features['is_power_of_2'] = 1 if (k & (k - 1)) == 0 and k > 0 else 0
    features['is_fibonacci'] = 0  # set later
    
    # Smooth: k has small prime factor?
    k_temp = k
    small_factors = []
    for p in small_primes:
        while k_temp % p == 0:
            small_factors.append(p)
            k_temp //= p
    features['smallest_prime_factor'] = small_factors[0] if small_factors else k
    features['num_small_factors'] = len(small_factors)
    features['remaining_after_small'] = k_temp
    features['is_smooth'] = 1 if k_temp == 1 else 0
    
    # Is k a multiple of 1237?
    features['mult_1237'] = 1 if k % 1237 == 0 else 0
    # Is k a multiple of p (the Mersenne index)?
    # Already implicit since q - 1 = 2*p*k, so gcd(k, p) might be > 1 sometimes
    
    # Powers
    features['log2_k'] = math.log2(k) if k > 0 else -1
    features['log2_k_int'] = int(features['log2_k'])
    
    # Number of prime factors (rough)
    features['omega_k'] = len(small_factors) + (1 if k_temp > 1 else 0)
    
    return features

# Extract features for all k values
print("استخراج features برای تمام داده‌ها...")
t0 = time.time()
all_features = []
for p, q, k in data:
    feats = extract_features(k)
    feats['p'] = p
    feats['q'] = q
    all_features.append(feats)
t1 = time.time()
print(f"  استخراج features از {len(all_features)} نمونه در {t1-t0:.1f}s")
print()

# ============================================================
# Analyze features: what patterns emerge?
# ============================================================
print("=" * 70)
print("  تحلیل features: الگوهای رایج در k های موفق")
print("=" * 70)
print()

# 1. Distribution of k mod 2, k mod 3, k mod 5, ...
print("1. Distribution of k mod small primes:")
for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73]:
    mod_dist = Counter(feat[f'k_mod_{p}'] for feat in all_features)
    # Show top 3
    top = mod_dist.most_common(3)
    print(f"  k mod {p}: {top[:5]}")
print()

# 2. How often is k prime?
prime_count = sum(1 for feat in all_features if feat['is_prime'])
print(f"2. k اول است: {prime_count} / {len(all_features)} = {prime_count/len(all_features)*100:.1f}%")
print()

# 3. How often is k smooth?
smooth_count = sum(1 for feat in all_features if feat['is_smooth'])
print(f"3. k کاملاً smooth (all factors ≤ 100): {smooth_count} / {len(all_features)} = {smooth_count/len(all_features)*100:.1f}%")
print()

# 4. Distribution of smallest prime factor of k
print("4. Distribution of smallest prime factor of k:")
spf_dist = Counter(feat['smallest_prime_factor'] for feat in all_features)
print(f"  Top 10: {spf_dist.most_common(10)}")
print()

# 5. Distribution of log10(k)
print("5. Distribution of log10(k):")
log_buckets = Counter()
for feat in all_features:
    bucket = int(feat['log10_k'])
    log_buckets[bucket] += 1
for b in sorted(log_buckets.keys())[:20]:
    print(f"  log10(k) in [{b}, {b+1}): {log_buckets[b]} samples")
print()

# 6. Is k a multiple of 1237?
mult_1237 = sum(1 for feat in all_features if feat['mult_1237'])
print(f"6. k مضرب 1237 است: {mult_1237} / {len(all_features)}")
print()

# 7. Is k a power of 2?
pow2 = sum(1 for feat in all_features if feat['is_power_of_2'])
print(f"7. k توان ۲ است: {pow2} / {len(all_features)}")
print()

# ============================================================
# Apply to F2 (p=1237): generate k candidates based on observed patterns
# ============================================================
print("=" * 70)
print("  اعمال الگوها روی p=1237 برای تولید k های امیدبخش")
print("=" * 70)
print()

# Strategy: based on the analysis, generate k values that match common patterns:
# - k divisible by small primes (especially 2, 3, 5, 7)
# - k smooth
# - k with specific log10 (typically small)
# - k that are perfect squares, powers of 2, Fibonacci numbers, etc.

# Generate candidate k values
candidates = set()

# 1. All k of form: small_smooth_k * 1237^j for small j
print("1. تولید k = smooth × 1237^j (j=0,1,2):")
small_smooth = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 24, 25, 27, 28, 30, 32, 35, 36, 40, 42, 45, 48, 49, 50, 54, 56, 60, 63, 64, 70, 72, 75, 80, 81, 84, 90, 96, 98, 100]
for s in small_smooth:
    for j in [0, 1, 2]:
        k = s * (1237 ** j)
        candidates.add(k)
print(f"  اضافه شد: {len(candidates)} kandidate")
print()

# 2. k = power of 2 times small number
print("2. تولید k = 2^j * small برای j = 0..20:")
for j in range(21):
    for s in [1, 3, 5, 7, 9, 11, 13, 15, 21, 25, 27, 33, 35, 45, 49, 63, 75, 81, 99]:
        k = (1 << j) * s
        if k < 10**20:  # cap
            candidates.add(k)
print(f"  اضافه شد: {len(candidates)} kandidate")
print()

# 3. k from Fibonacci sequence
print("3. تولید k = Fibonacci numbers:")
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
for n in range(2, 200):
    k = fib(n)
    if k < 10**20:
        candidates.add(k)
print(f"  اضافه شد: {len(candidates)} kandidate")
print()

# 4. k = Mersenne M(j) = 2^j - 1
print("4. تولید k = M(j) = 2^j - 1 برای j = 1..64:")
for j in range(1, 65):
    k = (1 << j) - 1
    if k < 10**20:
        candidates.add(k)
print(f"  اضافه شد: {len(candidates)} kandidate")
print()

# 5. k = squares
print("5. تولید k = perfect squares تا 10^10:")
for s in range(1, 10**5 + 1):
    k = s * s
    if k < 10**20:
        candidates.add(k)
print(f"  اضافه شد: {len(candidates)} kandidate")
print()

# 6. k from observed patterns: take k values that actually worked for OTHER p, scale
print("6. k های که برای p های دیگر جواب داده، scaling به p=1237:")
for p_other, q_other, k_other in data:
    if p_other == 1237:
        continue
    # scale: keep structure but adapt
    # k = k_other * (1237 / p_other) is not integer usually
    # Instead: try k = k_other * j for small j
    for j in [1, 2, 3]:
        k = k_other * j
        if k < 10**15:
            candidates.add(k)
print(f"  اضافه شد: {len(candidates)} kandidate")
print()

# ============================================================
# Now: test each candidate k to see if 2474*k + 1 divides F2
# ============================================================
print("=" * 70)
print("  آزمایش k های امیدبخش: آیا 2474*k + 1 | F2؟")
print("=" * 70)
print()

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1
N = int(F2)

t0 = time.time()
tested = 0
prime_count = 0
factor_found = None
for k in sorted(candidates):
    if k <= 0:
        continue
    q = 2474 * k + 1
    tested += 1
    # Quick composite check
    if q % 3 == 0 or q % 5 == 0 or q % 7 == 0 or q % 11 == 0 or q % 13 == 0:
        continue
    if not is_prime(q):
        continue
    prime_count += 1
    if N % q == 0:
        factor_found = q
        print(f"  >>> FACTOR FOUND at k = {k}: q = {q}")
        print(f"  is_prime: True")
        cof = N // q
        print(f"  cofactor: " + str(cof)[:60] + "... (" + str(len(str(cof))) + " digits)")
        if int(M) % q == 0:
            print(f"  ✓ REAL FACTOR of M(1237)!")
            sys.exit(0)
        break
    if tested % 1000 == 0:
        elapsed = time.time() - t0
        print(f"  progress: tested={tested}, primes={prime_count}, elapsed={elapsed:.1f}s")

elapsed = time.time() - t0
print(f"\nنتیجه: {tested} k های امیدبخش آزمایش شد، {prime_count} عدد q=2474k+1 اول بودند")
if not factor_found:
    print(f"  ✗ هیچ فاکتور پیدا نشد (elapsed {elapsed:.1f}s)")
else:
    print(f"  ✓ فاکتور: {factor_found}")
print()

# ============================================================
# Save analysis
# ============================================================
analysis = {
    "samples_count": len(all_features),
    "p_1237_data_points": sum(1 for f in all_features if f['p'] == 1237),
    "feature_distributions": {
        "is_prime_pct": prime_count / max(len(all_features), 1) * 100,
        "is_smooth_pct": smooth_count / max(len(all_features), 1) * 100,
        "mult_1237_count": mult_1237,
        "power_of_2_count": pow2,
    },
    "candidates_generated": len(candidates),
    "candidates_tested": tested,
    "candidates_prime_q": prime_count,
    "factor_found": factor_found,
}

with open('/home/z/my-project/download/ai_factor_analysis.json', 'w') as f:
    json.dump(analysis, f, indent=2, default=str)
print("Analysis saved to /home/z/my-project/download/ai_factor_analysis.json")
