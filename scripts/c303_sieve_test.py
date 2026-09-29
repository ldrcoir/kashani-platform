#!/usr/bin/env python3
"""Quick test of the sieve logic on a small range."""

import sys
sys.set_int_max_str_digits(1000000)
import gmpy2
from gmpy2 import mpz, is_prime, powmod
import time

P = 1237
TWO_P = 2474
M = mpz(2)**P - 1
P70 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
C303 = M // P70

# Generate sieve rules
def generate_sieve_rules(bound=1000):
    sieve = bytearray([1]) * (bound + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(bound**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    primes = [i for i in range(2, bound + 1) if sieve[i]]
    
    rules = []
    for r in primes:
        if r == 2 or r == 1237: continue
        inv_2474 = pow(TWO_P, -1, r)
        blocked_residue = (-inv_2474) % r
        rules.append((r, blocked_residue))
    return rules

rules = generate_sieve_rules(bound=1000)
print(f"Generated {len(rules)} sieve rules")

# Test on a small range: k from 1 to 10 million (we know no factor exists there from previous work)
# Should run in a few seconds

t_start = time.time()
tested = 0
skipped = 0
last_log = t_start

K_START = 1
K_END = 5_000_000

for k in range(K_START, K_END):
    # Fast sieve check
    passes = True
    for r, blocked in rules:
        if k % r == blocked:
            passes = False
            break
    
    if not passes:
        skipped += 1
        continue
    
    tested += 1
    q = TWO_P * k + 1
    
    if not is_prime(q):
        continue
    
    # Check if q | M(1237) (fast)
    if powmod(2, P, q) == 1:
        # q | M(1237). Verify q | C303
        if C303 % q == 0:
            print(f"\n!!! FACTOR FOUND at k={k}: q = {q}")
            sys.exit(0)
        else:
            print(f"\nNote: q = {q} satisfies pow(2,1237,q)=1 but does NOT divide C303 (q | P70? {P70 % q == 0})")
    
    if k % 100_000 == 0 and k > 0:
        elapsed = time.time() - t_start
        rate = k / elapsed
        print(f"  k={k:,}, tested={tested:,}, skipped={skipped:,}, rate={rate:.0f} k/s, elapsed={elapsed:.1f}s")

elapsed = time.time() - t_start
print(f"\nDone: k=[{K_START}, {K_END}), tested={tested:,}, skipped={skipped:,}, elapsed={elapsed:.1f}s")
print(f"Pass rate: {tested/(tested+skipped)*100:.2f}%")
print(f"Effective rate: {K_END/elapsed:.0f} k/s (with sieve)")
print(f"Without sieve, would need: {K_END} primality tests in {elapsed:.1f}s = {K_END/elapsed:.0f} q/s")
