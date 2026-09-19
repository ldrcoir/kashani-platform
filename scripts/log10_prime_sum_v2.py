#!/usr/bin/env python3
"""
Final high-precision computation: use primes up to 100000 and combine
greedy + refine + extended DP to minimize error.
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz
import math
import json
import time
from pathlib import Path

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

diff = log10_F2 - log10_F1
target = diff
print(f"log10(F1) = {log10_F1!r}")
print(f"log10(F2) = {log10_F2!r}")
print(f"Target (diff) = {target!r}")

# Generate primes
def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

PRIME_LIMIT = 100000
primes = small_primes_up_to(PRIME_LIMIT)
log10_primes = [math.log10(p) for p in primes]
print(f"Generated {len(primes)} primes up to {PRIME_LIMIT}")
print()

# ============================================================
# Strategy A: Greedy ascending (use 2, 3, 5, 7, ... in order)
# ============================================================
def greedy_asc(target, primes, log10_primes):
    sum_log = 0.0
    selected = []
    for p, lp in zip(primes, log10_primes):
        if sum_log + lp <= target + 1e-12:  # tiny tolerance for floating
            sum_log += lp
            selected.append(p)
    return sum_log, selected

t0 = time.time()
sumA, selA = greedy_asc(target, primes, log10_primes)
t1 = time.time()
print(f"Strategy A (greedy asc, {len(primes)} primes): {len(selA)} primes, sum={sumA:.10f}, error={target-sumA:.10f}, time={t1-t0:.3f}s")

# ============================================================
# Strategy B: Greedy ascending then refinement (heavy)
# ============================================================
def refine_heavy(target, selected_primes, all_primes, log10_primes, iterations=100000, log_every=10000):
    current_sum = sum(math.log10(p) for p in selected_primes)
    selected_set = set(selected_primes)
    
    for it in range(iterations):
        error = target - current_sum
        if abs(error) < 1e-12:
            break
        
        best_improvement = 1e-15
        best_op = None
        
        # If error > 0, try to ADD a prime
        if error > 0:
            # Find prime not selected with log10 ≈ error (largest that fits)
            # Use binary search for speed
            for p, lp in zip(all_primes, log10_primes):
                if p in selected_set:
                    continue
                if lp <= error + 1e-15:
                    improvement = lp - max(0, error - lp)  # we want to minimize |error - lp|
                    # Actually new error = error - lp. improvement = |error| - |error - lp|
                    new_error = error - lp
                    improvement = abs(error) - abs(new_error)
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_op = ('add', p, lp)
        
        # Try swap: remove p1, add p2 where log10(p2) - log10(p1) ≈ error
        # This is O(N^2). For 10000 primes, 1e8 ops — too slow.
        # Smarter: for each selected p1, find p2 (not selected) with log10(p2) ≈ log10(p1) + error
        # Binary search on sorted log10_primes
        sorted_with_log = sorted([(lp, p) for p, lp in zip(all_primes, log10_primes)])
        sorted_logs = [lp for lp, _ in sorted_with_log]
        for p1 in list(selected_set):
            lp1 = math.log10(p1)
            # want log10(p2) ≈ lp1 + error
            want = lp1 + error
            # Binary search for closest log10 in sorted_logs
            import bisect
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
        
        # If error < 0, try to REMOVE a prime (smallest lp that overshoots)
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
        
        if (it + 1) % log_every == 0:
            print(f"  iter {it+1}: sum={current_sum:.10f}, error={target-current_sum:.10f}")
    
    return current_sum, sorted(selected_set)

t0 = time.time()
sumB, selB = refine_heavy(target, selA, primes, log10_primes, iterations=200000)
t1 = time.time()
print(f"Strategy B (greedy asc + heavy refine): {len(selB)} primes, sum={sumB:.10f}, error={target-sumB:.10f}, time={t1-t0:.3f}s")

# ============================================================
# Strategy C: Greedy descending
# ============================================================
def greedy_desc_smart(target, primes, log10_primes):
    """Greedy: sort by log10 desc, pick first that fits, repeat."""
    sum_log = 0.0
    selected = []
    pairs = sorted(zip(primes, log10_primes), key=lambda x: -x[1])
    # Use binary search to find largest prime that fits
    changed = True
    while changed:
        changed = False
        for p, lp in pairs:
            if sum_log + lp <= target + 1e-12:
                sum_log += lp
                selected.append(p)
                changed = True
                break
    return sum_log, selected

t0 = time.time()
sumC, selC = greedy_desc_smart(target, primes, log10_primes)
t1 = time.time()
print(f"Strategy C (greedy desc, duplicates allowed if not in selected): {len(selC)} primes, sum={sumC:.10f}, error={target-sumC:.10f}, time={t1-t0:.3f}s")

# ============================================================
# Strategy D: All primes up to 100000 — find unique primes sum closest
# ============================================================
# Use greedy asc + refine + extended search with all primes up to 100000
# This is the "best" attempt.

t0 = time.time()
sumD, selD = refine_heavy(target, selA, primes, log10_primes, iterations=500000)
t1 = time.time()
print(f"Strategy D (final, 500k iterations): {len(selD)} primes, sum={sumD:.10f}, error={target-sumD:.10f}, time={t1-t0:.3f}s")

# Verify: also compute as product
product = 1
for p in selD:
    product *= p
log10_product = math.log10(product)
print(f"Verification: product of {len(selD)} primes = {str(product)[:50]}... ({len(str(product))} digits)")
print(f"log10(product) = {log10_product:.10f}")
print(f"diff = log10(F2)-log10(F1) = {target:.10f}")
print(f"product / F2 ratio: {10**(log10_product - log10_F2):.6e}")
print(f"F1 * product vs F2: log10(F1*product) = {log10_F1 + log10_product:.10f}, log10(F2) = {log10_F2:.10f}")
print(f"Difference (in log10): {(log10_F1 + log10_product) - log10_F2:.10f}")

# Save final results
results = {
    "metadata": {
        "p": 1237,
        "F1_digits": len(str(F1)),
        "F2_digits": len(str(F2)),
        "F1_first_50": str(F1)[:50],
        "F1_last_20": str(F1)[-20:],
        "F2_first_50": str(F2)[:50],
        "F2_last_20": str(F2)[-20:],
        "log10_F1": log10_F1,
        "log10_F2": log10_F2,
        "diff": diff,
        "target": target,
        "computed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    },
    "strategies": [
        {
            "name": "Strategy A: Greedy Ascending (primes up to 100000)",
            "description": "Use primes 2, 3, 5, 7, ... in increasing order; add each if it doesn't overshoot",
            "prime_count": len(selA),
            "sum": sumA,
            "error": target - sumA,
            "primes": selA,
        },
        {
            "name": "Strategy B: Greedy Asc + Heavy Refinement (200k iter)",
            "description": "Start with greedy ascending, then perform 200000 swap/add/remove operations to minimize error",
            "prime_count": len(selB),
            "sum": sumB,
            "error": target - sumB,
            "primes": selB,
        },
        {
            "name": "Strategy C: Greedy Descending",
            "description": "Always pick the largest prime whose log10 still fits",
            "prime_count": len(selC),
            "sum": sumC,
            "error": target - sumC,
            "primes": selC,
        },
        {
            "name": "Strategy D: Best (500k iterations refinement)",
            "description": "Greedy ascending with 500000 refinement iterations — our best result",
            "prime_count": len(selD),
            "sum": sumD,
            "error": target - sumD,
            "primes": selD,
        },
    ]
}

# Add log10 values for each
for s in results["strategies"]:
    s["log10_values"] = [math.log10(p) for p in s["primes"]]
    # Compute cumulative sum
    cum = 0
    s["cumulative_sum"] = []
    for p in s["primes"]:
        cum += math.log10(p)
        s["cumulative_sum"].append(cum)

best_strategy = min(results["strategies"], key=lambda s: abs(s["error"]))
results["best_strategy_index"] = results["strategies"].index(best_strategy)
print(f"\nBest strategy: {best_strategy['name']}")
print(f"  Error: {best_strategy['error']:.10e}")

out_path = Path('/home/z/my-project/download/log10_factorization_results.json')
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {out_path}")

# Also save the product verification
verify = {
    "F1": str(F1),
    "F2_first_50": str(F2)[:50],
    "F2_last_50": str(F2)[-50:],
    "F2_digits": len(str(F2)),
    "best_primes": best_strategy["primes"],
    "best_sum_log10": best_strategy["sum"],
    "best_error": best_strategy["error"],
    "product_of_primes_first_50": str(product)[:50],
    "product_of_primes_last_50": str(product)[-50:],
    "product_digits": len(str(product)),
    "F1_times_product_digits": len(str(F1 * product)),
    "log10_F1_plus_log10_product": log10_F1 + log10_product,
    "log10_F2": log10_F2,
}
with open('/home/z/my-project/download/log10_verification.json', 'w') as f:
    json.dump(verify, f, indent=2)
print(f"Verification saved to /home/z/my-project/download/log10_verification.json")
