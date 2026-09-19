#!/usr/bin/env python3
"""
Aggressive P-1 on N = M(1237)/F1 with B1=1e10 and multiple bases.
P-1 finds factor q when q-1 is B1-smooth.
For Mersenne factors q: q-1 = 2*p*k, so q-1 is smooth iff k is smooth.
Try bases 2, 3, 5, 7, 11 to catch any q where (a/q) = +1 for that specific a.

Also try with B2 (stage 2) for higher hit rate.
"""

import sys; sys.set_int_max_str_digits(1000000)
import gmpy2; from gmpy2 import mpz, gcd, is_prime, powmod
import time
from pathlib import Path

BASE = Path('/home/z/my-project')
LOG = BASE / 'logs/pm1_M1237_deep.log'

M = mpz(2)**1237 - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
N = M // F1

def log(msg):
    t = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{t}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f: f.write(line + '\n')

def update_factors(factor):
    FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
    lines = FACTORS_FILE.read_text().splitlines(keepends=True)
    out = []
    for line in lines:
        if line.startswith('#'): out.append(line); continue
        parts = line.split('\t')
        if len(parts) >= 2 and parts[0] == '1237':
            cur = parts[1].strip()
            if cur == '-1' or int(factor) < int(cur): out.append(f'1237\t{factor}\n')
            else: out.append(line)
        else: out.append(line)
    FACTORS_FILE.write_text(''.join(out))

# Stage 1: compute a^E mod N where E = prod p^k for p^k <= B1
# Stage 2: compute a^(E * p) for each prime p in (B1, B2]; gcd(a^(E*p) - 1, N) might find factor

def small_primes_up_to(limit):
    """Sieve of Eratosthenes."""
    if limit < 2: return []
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

log(f'P-1 deep on N = M(1237)/F1, {len(str(N))} digits')

B1 = 10**9  # 1e9
B2 = 10**10  # 1e10 (stage 2)

log(f'Stage 1: B1 = {B1}')
log(f'Sieving primes up to {B1}...')
t0 = time.time()
primes = small_primes_up_to(B1)
t1 = time.time()
log(f'Sieve done: {len(primes)} primes, time = {t1-t0:.1f}s')

# Try multiple bases
for base_a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
    log(f'')
    log(f'=== Base a = {base_a}, B1 = {B1} ===')
    t0 = time.time()
    
    # Compute a^E mod N incrementally
    val = mpz(base_a)
    for i, p in enumerate(primes):
        # e_p = floor(log(B1) / log(p)) = largest k with p^k <= B1
        pe = p
        while pe * p <= B1:
            pe *= p
        val = powmod(val, pe, N)
        # Check gcd periodically
        if (i + 1) % 5_000_000 == 0:
            g = gcd(val - 1, N)
            if 1 < int(g) < int(N):
                log(f'  Stage 1 intermediate: pi={i+1}, prime={p}, FOUND factor {g} ({len(str(g))} digits)')
                if int(M) % int(g) == 0:
                    log(f'  REAL FACTOR! is_prime: {is_prime(int(g))}')
                    update_factors(int(g))
                    sys.exit(0)
            elapsed = time.time() - t0
            log(f'  Progress: pi={i+1}, prime={p}, elapsed={elapsed:.1f}s')
    
    g = gcd(val - 1, N)
    log(f'  Stage 1 done: gcd = {g} (trivial={g==1 or g==N})')
    if 1 < int(g) < int(N):
        log(f'  Stage 1 FACTOR: {g} ({len(str(g))} digits)')
        if int(M) % int(g) == 0:
            log(f'  REAL FACTOR! is_prime: {is_prime(int(g))}')
            cof = int(N) // int(g)
            log(f'  cofactor: {cof} ({len(str(cof))} digits), is_prime: {is_prime(cof)}')
            update_factors(int(g))
            sys.exit(0)
    
    t2 = time.time()
    log(f'  Stage 1 time: {t2-t0:.1f}s')
    
    # Stage 2: continue with primes in (B1, B2]
    log(f'  Stage 2: primes in ({B1}, {B2}]')
    # We need to compute a^(E*p) for each prime p in (B1, B2]
    # Standard stage 2: precompute a^E, then a^(E*p) = (a^E)^p
    # But it's cheaper: precompute (a^E)^2, then for each prime p, multiply by appropriate power.
    # Simple approach (slower): for each prime p in (B1, B2], compute (val)^p mod N, then gcd.
    # Even simpler: store val (which is a^E mod N), then for each prime p, multiply val by val^((p-1)/...) etc.
    
    # Standard "improved stage 2": 
    # Let g_a = a^E mod N (we have this as 'val')
    # For each prime p in (B1, B2]: gcd(g_a^p - 1, N)
    # But g_a^p = (g_a)^p. Computing g_a^p for each prime is O(log p) per prime.
    # Better: use "standard continuation": g_a^2, g_a^3, ... by multiplying.
    # Or "baby-step giant-step" for stage 2.
    
    # Simple version: precompute powers g_a^k for k = 1, 2, ..., D (giant step)
    # Then for each prime p in (B1, B2], p = k*D + r, g_a^p = g_a^(k*D) * g_a^r
    # Precompute g_a^r for r = 0, 1, ..., D-1 (baby steps)
    # Precompute g_a^D (giant step)
    # Then g_a^p = (g_a^D)^k * g_a^r
    
    # For B2 = 1e10, D = sqrt(B2) = 1e5
    # Precompute g_a^r for r = 0..D-1: 1e5 powmods. Feasible.
    # Precompute (g_a^D)^k for k = 0..D-1: 1e5 powmods.
    # Then for each prime p in (B1, B2]: lookup.
    
    D = int(gmpy2.isqrt(B2)) + 1
    log(f'  Stage 2 D = {D}')
    
    # Baby steps: g_a^r for r = 0, 1, ..., D-1
    baby = [mpz(1)]
    cur = mpz(1)
    for r in range(1, D):
        cur = (cur * val) % N
        baby.append(cur)
    
    # Giant step base: g_a^D
    g_D = powmod(val, D, N)
    
    # For each prime p in (B1, B2]: find k, r with p = k*D + r
    # Then g_a^p = (g_D)^k * baby[r]
    # Compute product of (g_a^p - 1) for all primes p in (B1, B2], then gcd with N
    
    # Generate primes in (B1, B2] using segmented sieve
    log(f'  Generating primes in ({B1}, {B2}]...')
    t_seg_start = time.time()
    
    # Segmented sieve
    sqrt_B2 = int(B2**0.5) + 1
    small_primes = small_primes_up_to(sqrt_B2)
    
    segment_size = 10**7  # 10M
    accum_product = mpz(1)
    
    for seg_start in range(B1 + 1, B2 + 1, segment_size):
        seg_end = min(seg_start + segment_size - 1, B2)
        sieve = bytearray([1]) * (seg_end - seg_start + 1)
        for p in small_primes:
            # First multiple of p >= seg_start
            start = max(p*p, ((seg_start + p - 1) // p) * p)
            for j in range(start, seg_end + 1, p):
                sieve[j - seg_start] = 0
        # Collect primes
        for i, is_p in enumerate(sieve):
            if is_p:
                p = seg_start + i
                if p <= B2:
                    # Compute g_a^p = (g_D)^k * baby[r] where p = k*D + r
                    k = p // D
                    r = p - k * D
                    # g_a^p = (g_D)^k * baby[r]
                    giant_k = powmod(g_D, k, N)
                    gap = (giant_k * baby[r]) % N
                    accum_product = (accum_product * (gap - 1)) % N
        
        # Check gcd periodically
        g = gcd(accum_product, N)
        if 1 < int(g) < int(N):
            log(f'  Stage 2: FOUND factor {g} ({len(str(g))} digits) at segment starting {seg_start}')
            if int(M) % int(g) == 0:
                log(f'  REAL FACTOR! is_prime: {is_prime(int(g))}')
                update_factors(int(g))
                sys.exit(0)
        
        elapsed = time.time() - t_seg_start
        log(f'  Segment {seg_start}-{seg_end}: elapsed {elapsed:.1f}s')
        # Stop after first few segments for time budget
        if time.time() - t0 > 600:  # 10 min budget per base
            log(f'  Time budget exceeded for base {base_a}')
            break
    
    t3 = time.time()
    log(f'  Stage 2 time: {t3-t2:.1f}s, total for base {base_a}: {t3-t0:.1f}s')

log(f'')
log(f'P-1 deep complete. No factor found.')
