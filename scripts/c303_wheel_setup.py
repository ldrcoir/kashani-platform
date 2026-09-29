#!/usr/bin/env python3
"""
Smart sieve v3 — use a "wheel" based on the product of small primes.

Strategy:
- The "blocked" residues for each prime r partition the k space.
- We use a "wheel" with the LCM of small primes (modular sieve).
- For each small prime r, we know k ≡ blocked (mod r) is bad.
- The remaining k values (those not blocked by any r) are tested.

For bound=100, LCM(3..97) is huge, but we can use mod L = LCM(small primes).
For example, with primes {3, 5, 7}, L = 105.
Compute the "good residues" mod 105 = residues k such that k is not ≡ blocked (mod r) for any r.
Then iterate only over k ≡ good_residue (mod 105).

This way, we skip the sieve check entirely during iteration!
"""

import sys
sys.set_int_max_str_digits(1000000)
import gmpy2
from gmpy2 import mpz, is_prime, powmod
import time
import json
import multiprocessing as mp
from pathlib import Path

P = 1237
TWO_P = 2474
M = mpz(2)**P - 1
P70 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
C303 = M // P70

# Choose small primes for the wheel
# Wheel primes: 3, 5, 7, 11, 13 — product = 15015
# Or larger: 3, 5, 7, 11, 13, 17, 19 — product = 4849845
# Or 3, 5, 7, 11, 13, 17, 19, 23 — product = 111546435 (8 primes)

WHEEL_PRIMES = [3, 5, 7, 11, 13, 17, 19]  # 7 primes, product = 4849845
WHEEL_MOD = 1
for p in WHEEL_PRIMES:
    WHEEL_MOD *= p

print(f"Wheel primes: {WHEEL_PRIMES}")
print(f"Wheel modulus: {WHEEL_MOD}")

# For each wheel prime, find blocked residue (where q = 2474*k + 1 ≡ 0 mod r)
wheel_blocked = {}
for r in WHEEL_PRIMES:
    inv_2474 = pow(TWO_P, -1, r)
    blocked = (-inv_2474) % r
    wheel_blocked[r] = blocked

print(f"Blocked residues per wheel prime: {wheel_blocked}")

# Compute "good residues" mod WHEEL_MOD
# A residue k0 mod WHEEL_MOD is good iff for each r, k0 mod r != blocked[r]
# This is the CRT complement of the union of bad residues

print(f"Computing good residues mod {WHEEL_MOD}...")
t0 = time.time()

# Method: iterate k from 0 to WHEEL_MOD-1, check if good
good_residues = []
for k0 in range(WHEEL_MOD):
    is_good = True
    for r in WHEEL_PRIMES:
        if k0 % r == wheel_blocked[r]:
            is_good = False
            break
    if is_good:
        good_residues.append(k0)

t1 = time.time()
print(f"Computed {len(good_residues)} good residues in {t1-t0:.1f}s")
print(f"Pass rate (good / total): {len(good_residues)/WHEEL_MOD*100:.2f}%")

# Save good residues (so we don't recompute)
import pickle
with open('/home/z/my-project/download/good_residues.pkl', 'wb') as f:
    pickle.dump(good_residues, f)
print(f"Saved to good_residues.pkl")

# Now: for additional primes > WHEEL_PRIMES[-1], we use traditional sieve rules
def gen_extra_rules(bound):
    sieve = bytearray([1]) * (bound + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(bound**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    primes = [i for i in range(2, bound + 1) if sieve[i]]
    rules = []
    for r in primes:
        if r == 2 or r == 1237: continue
        if r in WHEEL_PRIMES: continue  # already in wheel
        inv_2474 = pow(TWO_P, -1, r)
        blocked = (-inv_2474) % r
        rules.append((r, blocked))
    return rules

EXTRA_RULES = gen_extra_rules(bound=1000)
print(f"Extra sieve rules (bound=1000): {len(EXTRA_RULES)}")

# Combined pass rate
total_pass = len(good_residues) / WHEEL_MOD
for r, _ in EXTRA_RULES:
    total_pass *= (1 - 1/r)
print(f"Combined pass rate (wheel + extra): {total_pass*100:.2f}%")
