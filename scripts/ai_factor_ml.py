#!/usr/bin/env python3
"""
Train a simple neural network (or gradient boosting) to predict 
"promising k values" for Mersenne factor search.

Approach:
1. Dataset: for each (p, k) where k = (q-1)/(2p) for a known factor q of M(p),
   label as positive.
2. Generate negative samples: random k values for the same p (these likely don't 
   yield a factor).
3. Features: k mod small primes, log10(k), is_prime, smoothness, etc.
4. Train a binary classifier.
5. For p=1237, generate many k candidates, score them, test top N.

Use sklearn's Gradient Boosting / Random Forest.
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
from collections import Counter

# Check if sklearn is available
try:
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("sklearn not available, trying to install...")
    import subprocess
    result = subprocess.run(['pip', 'install', '--quiet', '--break-system-packages', 'scikit-learn', 'numpy'], capture_output=True, text=True)
    print(result.stdout[-200:])
    print(result.stderr[-200:])
    try:
        from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report, accuracy_score
        import numpy as np
        SKLEARN_AVAILABLE = True
    except ImportError:
        print("Could not install sklearn. Falling back to manual classifier.")

print(f"sklearn available: {SKLEARN_AVAILABLE}")
print()

# Load data
FACTORS_FILE = Path('/home/z/my-project/download/A136030_factors_1_to_8000.txt')
lines = FACTORS_FILE.read_text().splitlines()

data = []
for line in lines:
    if line.startswith('#'):
        continue
    parts = line.split('\t')
    if len(parts) < 2:
        continue
    p_str, q_str = parts[0], parts[1].strip()
    p = int(p_str)
    if q_str in ('0', '-1'):
        continue
    q_val = int(q_str)
    if not is_prime(p):
        continue
    if powmod(2, p, q_val) != 1:
        continue
    if (q_val - 1) % (2 * p) != 0:
        continue
    k = (q_val - 1) // (2 * p)
    data.append((p, q_val, k))

print(f"Loaded {len(data)} positive (p, q, k) samples")
print()

def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

small_primes = small_primes_up_to(50)

def extract_features(p, k):
    """Extract features from (p, k) pair."""
    feats = []
    # k modular features
    for sp in small_primes:
        feats.append(k % sp)
    # p modular features  
    for sp in small_primes:
        feats.append(p % sp)
    # log values
    feats.append(math.log10(k + 1))  # avoid log(0)
    feats.append(math.log10(p + 1))
    feats.append(len(str(k)))
    feats.append(len(str(p)))
    # Structural features
    feats.append(1 if is_prime(k) else 0)
    feats.append(1 if k > 0 and int(math.isqrt(k))**2 == k else 0)
    feats.append(1 if k > 0 and (k & (k - 1)) == 0 else 0)  # power of 2
    # Smoothness
    k_temp = k
    num_factors = 0
    for sp in small_primes:
        while k_temp % sp == 0:
            num_factors += 1
            k_temp //= sp
    feats.append(num_factors)
    feats.append(1 if k_temp == 1 else 0)  # smooth
    feats.append(k_temp if k_temp < 10**10 else 10**10)  # remaining
    # Combined
    feats.append(1 if k % p == 0 else 0)
    feats.append(1 if k % 1237 == 0 else 0)
    return feats

# Generate training data
print("=" * 70)
print("  ساخت داده‌های آموزش")
print("=" * 70)
print()

random.seed(42)

# Positive samples
positives = []
for p, q, k in data:
    feats = extract_features(p, k)
    positives.append((feats, 1))
print(f"  Positive samples: {len(positives)}")

# Generate negatives: for each positive (p, k), generate 5 random k values 
# that don't yield a factor (we use random k values as proxies)
negatives = []
p_set = list(set(p for p, _, _ in data))
for p, q, k in data:
    # Generate 5 negative k's of similar magnitude
    for _ in range(5):
        k_rand = random.randint(1, max(10, k * 100))
        # Verify this k doesn't yield a factor (q = 2*p*k_rand + 1 might still work for SOME p, but unlikely for our specific p)
        # Just use it as negative — the model learns "common features of positives"
        feats = extract_features(p, k_rand)
        negatives.append((feats, 0))
print(f"  Negative samples: {len(negatives)}")

# Combine
all_samples = positives + negatives
random.shuffle(all_samples)
X = np.array([s[0] for s in all_samples])
y = np.array([s[1] for s in all_samples])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"  Train: {len(X_train)}, Test: {len(X_test)}")
print()

# Train classifier
print("=" * 70)
print("  آموزش مدل")
print("=" * 70)
print()

t0 = time.time()
print("Training Gradient Boosting Classifier...")
clf = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)
clf.fit(X_train, y_train)
t1 = time.time()
print(f"  Trained in {t1-t0:.1f}s")

# Evaluate
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"  Test accuracy: {acc:.4f}")
print()

# Print feature importance (top 10)
feature_names = (
    [f'k_mod_{p}' for p in small_primes] +
    [f'p_mod_{p}' for p in small_primes] +
    ['log10_k', 'log10_p', 'digits_k', 'digits_p',
     'is_prime_k', 'is_square', 'is_pow2',
     'num_factors', 'is_smooth', 'remaining',
     'k_mult_p', 'k_mult_1237']
)
importances = clf.feature_importances_
top_idx = np.argsort(importances)[::-1][:15]
print("Top 15 feature importances:")
for i in top_idx:
    if i < len(feature_names):
        print(f"  {feature_names[i]}: {importances[i]:.4f}")
print()

# ============================================================
# Apply model to p=1237: generate many k candidates, score, test top
# ============================================================
print("=" * 70)
print("  اعمال مدل روی p=1237: امتیازدهی به k های امیدبخش")
print("=" * 70)
print()

# Generate a large pool of k candidates
candidates = []
# Smooth k * 1237^j
for s in range(1, 1000):
    for j in [0, 1]:
        k = s * (1237 ** j)
        candidates.append(k)
# Powers of 2 * small
for j in range(20):
    for s in [1, 3, 5, 7, 9, 15, 21, 25, 27, 45, 63, 75, 99]:
        k = (1 << j) * s
        candidates.append(k)
# Random k values up to 10^10
random.seed(123)
for _ in range(10000):
    k = random.randint(1, 10**10)
    candidates.append(k)

# Score each candidate
P_target = 1237
scores = []
for k in candidates:
    feats = extract_features(P_target, k)
    score = clf.predict_proba([feats])[0][1]  # probability of being a "factor-yielding" k
    scores.append((k, score))

# Sort by score descending
scores.sort(key=lambda x: -x[1])

print(f"Top 20 k candidates with highest score:")
for k, score in scores[:20]:
    print(f"  k = {k} (log10 = {math.log10(k+1):.2f}), score = {score:.4f}")
print()

# ============================================================
# Test top N candidates: see if 2474*k + 1 | F2
# ============================================================
print("=" * 70)
print("  آزمایش top 10000 kandidate: آیا 2474*k+1 | F2؟")
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
for k, score in scores[:10000]:
    if k <= 0:
        continue
    q = 2474 * k + 1
    tested += 1
    if q % 3 == 0 or q % 5 == 0 or q % 7 == 0 or q % 11 == 0 or q % 13 == 0:
        continue
    if not is_prime(q):
        continue
    prime_count += 1
    if N % q == 0:
        factor_found = q
        print(f"  >>> FACTOR FOUND at k = {k} (score {score:.4f}): q = {q}")
        cof = N // q
        print(f"  cofactor: " + str(cof)[:60] + "...")
        break

elapsed = time.time() - t0
print(f"\nنتیجه: {tested} kandidate آزمایش، {prime_count} عدد prime q، factor {'found!' if factor_found else 'not found'}")
print(f"Elapsed: {elapsed:.1f}s")
print()

# Save analysis
analysis = {
    "samples_count": len(data),
    "positives": len(positives),
    "negatives": len(negatives),
    "test_accuracy": float(acc),
    "candidates_tested": tested,
    "candidates_prime_q": prime_count,
    "factor_found": factor_found,
    "top_20_k_candidates": [(k, float(s)) for k, s in scores[:20]],
}

with open('/home/z/my-project/download/ai_factor_ml_result.json', 'w') as f:
    json.dump(analysis, f, indent=2)
print("Analysis saved")
