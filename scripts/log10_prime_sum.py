#!/usr/bin/env python3
"""
Compute log10(F1), log10(F2), their difference, and find primes whose
log10 sum approximates the difference with minimum error.

Multiple strategies:
1. Greedy small→large (use 2, 3, 5, ... primes until sum exceeds target)
2. Greedy large→small (use largest prime whose log10 fits)
3. Dynamic programming for exact subset sum
4. Random/multi-pass refinement
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, isqrt
import math
import json
import time
from pathlib import Path

# Setup
P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1

print(f"F1 = {F1}")
print(f"F1 digits: {len(str(F1))}")
print(f"F2 digits: {len(str(F2))}")
print()

# Compute log10 with high precision using mpmath-like approach
# Python's math.log10 on int gives ~15 significant digits — enough for visualization.
log10_F1 = math.log10(int(F1))
log10_F2 = math.log10(int(F2))
diff = log10_F2 - log10_F1

print(f"log10(F1) = {log10_F1!r}")
print(f"log10(F2) = {log10_F2!r}")
print(f"diff = log10(F2) - log10(F1) = {diff!r}")
print()

# Better precision using decimal log:
# log10(F) = log10(2) * log2(F)
# Or: use log10(int) with more digits via mpmath if available
try:
    import mpmath
    mpmath.mp.dps = 50  # 50 decimal places
    log10_F1_hp = float(mpmath.log10(int(F1)))
    log10_F2_hp = float(mpmath.log10(int(F2)))
    diff_hp = log10_F2_hp - log10_F1_hp
    print(f"High-precision:")
    print(f"  log10(F1) = {log10_F1_hp!r}")
    print(f"  log10(F2) = {log10_F2_hp!r}")
    print(f"  diff      = {diff_hp!r}")
    print()
    log10_F1 = log10_F1_hp
    log10_F2 = log10_F2_hp
    diff = diff_hp
except ImportError:
    print("mpmath not available, using math.log10 (15-digit precision)")

# ============================================================
# Generate primes up to some bound
# ============================================================
def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

# We want primes whose log10 sum to ~233.31
# Largest single prime: 10^233.31 (too big to enumerate!)
# So we use primes up to some reasonable bound, e.g., 10^7 or so
# Actually since we want sum of log10(p) to equal ~233.31:
#   If we use first N primes: sum_{p <= X} log10(p) ≈ X/ln(10) ≈ X * 0.4343
#   We want sum ≈ 233.31 → X ≈ 233.31 / 0.4343 ≈ 537
# So primes up to 537 (or 1000) should be enough.

PRIME_LIMIT = 1000
primes = small_primes_up_to(PRIME_LIMIT)
log10_primes = [math.log10(p) for p in primes]

print(f"Generated {len(primes)} primes up to {PRIME_LIMIT}")
print(f"Sum of all log10(primes up to {PRIME_LIMIT}) = {sum(log10_primes):.6f}")
print()

target = diff
print(f"Target: {target:.10f}")
print()

# ============================================================
# Strategy 1: Greedy small→large (use primes in order 2, 3, 5, 7, ...)
#   Add each prime if it doesn't overshoot
# ============================================================
print("=" * 70)
print("Strategy 1: Greedy small→large (use primes in increasing order)")
print("=" * 70)

def greedy_asc(target, primes, log10_primes):
    sum_log = 0.0
    selected = []
    for p, lp in zip(primes, log10_primes):
        if sum_log + lp <= target:
            sum_log += lp
            selected.append((p, lp))
    return sum_log, selected

t0 = time.time()
sum1, sel1 = greedy_asc(target, primes, log10_primes)
t1 = time.time()
print(f"Time: {t1-t0:.4f}s")
print(f"Selected {len(sel1)} primes")
print(f"Sum = {sum1:.10f}")
print(f"Target = {target:.10f}")
print(f"Error = {target - sum1:.10f}")
print(f"First 10 selected: {sel1[:10]}")
print(f"Last 10 selected: {sel1[-10:]}")
print()

# ============================================================
# Strategy 2: Greedy large→small (use largest prime that fits)
# ============================================================
print("=" * 70)
print("Strategy 2: Greedy large→small")
print("=" * 70)

def greedy_desc(target, primes, log10_primes):
    sum_log = 0.0
    selected = []
    remaining = target
    # Sort primes by log10 descending
    pairs = sorted(zip(primes, log10_primes), key=lambda x: -x[1])
    # Repeatedly pick largest that fits
    changed = True
    while changed:
        changed = False
        for p, lp in pairs:
            if sum_log + lp <= target:
                sum_log += lp
                selected.append((p, lp))
                changed = True
                break  # restart to always pick largest
    return sum_log, selected

t0 = time.time()
sum2, sel2 = greedy_desc(target, primes, log10_primes)
t1 = time.time()
print(f"Time: {t1-t0:.4f}s")
print(f"Selected {len(sel2)} primes")
print(f"Sum = {sum2:.10f}")
print(f"Error = {target - sum2:.10f}")
print(f"First 10 selected: {sel2[:10]}")
print()

# ============================================================
# Strategy 3: Dynamic Programming for exact subset sum (with tolerance)
#   For each prime, decide include/exclude. State = current sum.
#   Use quantized sums (e.g., to 0.001 precision) for tractability.
# ============================================================
print("=" * 70)
print("Strategy 3: DP with quantized precision")
print("=" * 70)

def dp_subset(target, primes, log10_primes, precision=0.001):
    """DP for subset sum approximating target.
    Quantize sums to multiples of `precision` for state space reduction."""
    scale = int(1.0 / precision)
    target_q = int(round(target * scale))
    # dp[s] = list of primes achieving quantized sum s (just one example)
    # We want the largest quantized sum <= target_q
    dp = {0: []}  # sum -> list of primes
    for p, lp in zip(primes, log10_primes):
        lp_q = int(round(lp * scale))
        if lp_q == 0:  # too small for precision
            continue
        new_dp = {}
        for s, primes_list in dp.items():
            # Option 1: skip this prime
            if s not in new_dp or len(primes_list) < len(new_dp[s]):
                new_dp[s] = primes_list
            # Option 2: include this prime (if doesn't overshoot)
            new_s = s + lp_q
            if new_s <= target_q:
                if new_s not in new_dp or len(primes_list) + 1 < len(new_dp[new_s]):
                    new_dp[new_s] = primes_list + [p]
        # Merge dp and new_dp (keep best for each s)
        for s, primes_list in new_dp.items():
            if s not in dp or len(primes_list) < len(dp[s]):
                dp[s] = primes_list
    
    # Find best s <= target_q
    best_s = max(s for s in dp if s <= target_q)
    best_primes = dp[best_s]
    # Recompute actual sum
    actual_sum = sum(math.log10(p) for p in best_primes)
    return actual_sum, best_primes

t0 = time.time()
sum3, sel3 = dp_subset(target, primes, log10_primes, precision=0.001)
t1 = time.time()
print(f"Time: {t1-t0:.4f}s")
print(f"Selected {len(sel3)} primes")
print(f"Sum = {sum3:.10f}")
print(f"Error = {target - sum3:.10f}")
print(f"Selected primes: {sel3}")
print()

# ============================================================
# Strategy 4: Greedy with replacement — try replacing pairs of selected
#   primes with single larger primes (or vice versa) to reduce error
# ============================================================
print("=" * 70)
print("Strategy 4: Greedy asc + local refinement")
print("=" * 70)

def refine(target, selected_primes, all_primes, log10_primes, iterations=1000):
    """Local refinement: try swap, add, remove operations."""
    current_sum = sum(math.log10(p) for p in selected_primes)
    selected_set = set(selected_primes)
    
    for it in range(iterations):
        error = target - current_sum
        if abs(error) < 1e-10:
            break
        # Try adding a prime that reduces error
        best_improvement = 0
        best_op = None
        # ADD: find prime not selected, with log10 close to error
        if error > 0:
            for p, lp in zip(all_primes, log10_primes):
                if p not in selected_set and lp <= error:
                    improvement = lp  # adding reduces error by lp
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_op = ('add', p, lp)
        # SWAP: remove p1 (selected), add p2 (not selected) where log10(p2) - log10(p1) ≈ error
        for p1 in list(selected_set):
            lp1 = math.log10(p1)
            for p2, lp2 in zip(all_primes, log10_primes):
                if p2 in selected_set: continue
                delta = lp2 - lp1
                if abs(error - delta) < abs(error) and abs(error - delta) < abs(error):
                    improvement = abs(error) - abs(error - delta)
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_op = ('swap', p1, p2, lp1, lp2)
        # REMOVE: remove a prime to reduce overshoot (if error < 0)
        if error < 0:
            for p1 in list(selected_set):
                lp1 = math.log10(p1)
                if lp1 <= -error:
                    improvement = -(-error - lp1) if lp1 <= -error else 0
                    # actually improvement = lp1 (removing reduces sum by lp1, error decreases by lp1)
                    # new error = error + lp1; if lp1 <= -error, new error >= 0
                    # improvement = |error| - |new error| = -error - |error + lp1|
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

t0 = time.time()
sum4, sel4 = refine(target, list(p for p, _ in sel1), primes, log10_primes, iterations=5000)
t1 = time.time()
print(f"Time: {t1-t0:.4f}s")
print(f"Selected {len(sel4)} primes")
print(f"Sum = {sum4:.10f}")
print(f"Error = {target - sum4:.10f}")
print(f"Selected primes: {sel4}")
print()

# ============================================================
# Strategy 5: Generate primes up to higher bound for finer granularity
# ============================================================
print("=" * 70)
print("Strategy 5: Extended primes + greedy asc + refine")
print("=" * 70)

EXT_PRIME_LIMIT = 10000
ext_primes = small_primes_up_to(EXT_PRIME_LIMIT)
ext_log10_primes = [math.log10(p) for p in ext_primes]
print(f"Extended primes: {len(ext_primes)} primes up to {EXT_PRIME_LIMIT}")

t0 = time.time()
sum5_asc, sel5_asc_pairs = greedy_asc(target, ext_primes, ext_log10_primes)
sel5_asc = [p for p, _ in sel5_asc_pairs]
sum5, sel5 = refine(target, sel5_asc, ext_primes, ext_log10_primes, iterations=10000)
t1 = time.time()
print(f"Time: {t1-t0:.4f}s")
print(f"Selected {len(sel5)} primes")
print(f"Sum = {sum5:.10f}")
print(f"Error = {target - sum5:.10f}")
print(f"Selected primes (first 30): {sel5[:30]}")
print(f"Selected primes (last 10): {sel5[-10:]}")
print()

# ============================================================
# Save results as JSON
# ============================================================
results = {
    "metadata": {
        "p": 1237,
        "F1_digits": len(str(F1)),
        "F2_digits": len(str(F2)),
        "F1_first_30": str(F1)[:30],
        "F1_last_30": str(F1)[-30:],
        "F2_first_30": str(F2)[:30],
        "F2_last_30": str(F2)[-30:],
        "log10_F1": log10_F1,
        "log10_F2": log10_F2,
        "diff": diff,
        "target": target,
        "computed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    },
    "strategies": [
        {
            "name": "Greedy ascending (first 168 primes)",
            "description": "Use primes in increasing order, add each if it doesn't overshoot",
            "prime_count": len(sel1),
            "sum": sum1,
            "error": target - sum1,
            "primes": [p for p, _ in sel1],
            "log10_values": [lp for _, lp in sel1],
        },
        {
            "name": "Greedy descending",
            "description": "Always pick the largest prime whose log10 still fits",
            "prime_count": len(sel2),
            "sum": sum2,
            "error": target - sum2,
            "primes": [p for p, _ in sel2],
            "log10_values": [lp for _, lp in sel2],
        },
        {
            "name": "Dynamic Programming (quantized)",
            "description": "DP for subset sum with quantized precision (0.001)",
            "prime_count": len(sel3),
            "sum": sum3,
            "error": target - sum3,
            "primes": sel3,
            "log10_values": [math.log10(p) for p in sel3],
        },
        {
            "name": "Greedy asc + local refinement",
            "description": "Start with greedy ascending, then swap/add/remove to reduce error",
            "prime_count": len(sel4),
            "sum": sum4,
            "error": target - sum4,
            "primes": sel4,
            "log10_values": [math.log10(p) for p in sel4],
        },
        {
            "name": "Extended primes + greedy + refine (best)",
            "description": "Use primes up to 10000, greedy asc, then heavy refinement",
            "prime_count": len(sel5),
            "sum": sum5,
            "error": target - sum5,
            "primes": sel5,
            "log10_values": [math.log10(p) for p in sel5],
        },
    ]
}

# Find best
best_strategy = min(results["strategies"], key=lambda s: abs(s["error"]))
results["best_strategy_index"] = results["strategies"].index(best_strategy)
print(f"\nBest strategy: {best_strategy['name']}")
print(f"  Error: {best_strategy['error']:.10f}")
print(f"  Primes: {best_strategy['prime_count']}")

# Save JSON
out_path = Path('/home/z/my-project/download/log10_factorization_results.json')
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {out_path}")
