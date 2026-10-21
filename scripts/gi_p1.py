#!/usr/bin/env python3
"""
Gaussian Integer P-1 (GI-P1) — a genuinely novel method for factoring Mersenne cofactors.

NOVELTY:
  For M(p) = 2^p - 1, p prime. If p = a^2 + b^2 (Gaussian decomposition, p ≡ 1 mod 4),
  we have a Gaussian integer g = a + bi with norm(g) = p.
  
  In Z[i]/N (where N = M(p)/F1 or M(p)), the element g has order dividing:
    (q-1)^2 if q splits in Z[i] (i.e., q ≡ 1 mod 4)
    q^2-1   if q is inert in Z[i] (i.e., q ≡ 3 mod 4)
  
  For q | M(p) with q = 2kp+1, the order divides:
    Splits: 4k^2 * p^2
    Inert:  4kp * (kp + 1)
  
  If we run P-1-style exponentiation on g in Z[i]/N, then check:
    gcd(Re(g^E) - 1, N) and gcd(Im(g^E), N)
  we might find a factor where the order of g mod q_i is E-smooth but not all q_j.

  This is DIFFERENT from standard P-1 (which checks 2^E - 1) and P+1 (which uses Lucas).
  The order structure 4k^2*p^2 and 4kp(kp+1) is different from 2kp and 2kp+2.

ALGORITHM:
  Given p = a^2 + b^2 with p = 1237, a = 34, b = 9.
  N = M(p) / F1 (or M(p) if no known factor).
  
  Compute g = (a + bi) in Z[i]/N as pair (a, b).
  Stage 1: Raise g to power E = prod of prime powers <= B1.
    Multiplication in Z[i]/N: (u1, v1) * (u2, v2) = (u1*u2 - b^2*v1*v2 ... wait
    Actually: (u + vi)(x + yi) = (ux - vy) + (uy + vx)i. We're computing in Z[i]/N, so
    we reduce mod N. But the "i" is formal — i^2 = -1.
    Multiplication: (u1, v1) * (u2, v2) = ((u1*u2 - v1*v2) mod N, (u1*v2 + u2*v1) mod N)
    Squaring: (u, v)^2 = ((u^2 - v^2) mod N, (2uv) mod N)
  Stage 1 exponent E: prod of prime powers q^e <= B1, like P-1.
  At the end, check gcd(Re - 1, N), gcd(Im, N).
  Also check at intermediate steps (every 1000 primes or so).
"""

import sys
import time
import json
from pathlib import Path

import gmpy2
from gmpy2 import mpz, gcd, is_prime, powmod

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
LOG_FILE = BASE / 'logs/gi_p1.log'
LOG_FILE.parent.mkdir(exist_ok=True)


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')


def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]


def gauss_mult(g1, g2, N):
    """Multiply two Gaussian integers mod N.
    g = (u, v) represents u + v*i.
    (u1+v1*i)(u2+v2*i) = (u1*u2 - v1*v2) + (u1*v2 + u2*v1)*i
    """
    u1, v1 = g1
    u2, v2 = g2
    return ((u1 * u2 - v1 * v2) % N, (u1 * v2 + u2 * v1) % N)


def gauss_pow(g, k, N):
    """Compute g^k mod N using binary exponentiation."""
    result = (mpz(1), mpz(0))  # 1 + 0i
    base = g
    while k > 0:
        if k & 1:
            result = gauss_mult(result, base, N)
        base = gauss_mult(base, base, N)
        k >>= 1
    return result


def update_factor_file(p, factor):
    lines = FACTORS_FILE.read_text(encoding='utf-8').splitlines(keepends=True)
    out = []
    updated = False
    for line in lines:
        if line.startswith('#'):
            out.append(line); continue
        parts = line.split('\t')
        if len(parts) >= 2 and parts[0] == str(p):
            cur = parts[1].strip()
            if cur == '-1' or int(factor) < int(cur):
                out.append(f'{p}\t{factor}\n'); updated = True
            else:
                out.append(line)
        else:
            out.append(line)
    if updated:
        FACTORS_FILE.write_text(''.join(out), encoding='utf-8')
    return updated


def append_complete(p, factor, cofactor):
    with open(COMPLETE_FILE, 'a', encoding='utf-8') as f:
        f.write(f'{p}\tFULL\t{factor}\t{cofactor}\n')


def get_missing():
    lines = FACTORS_FILE.read_text(encoding='utf-8').splitlines()
    out = []
    for line in lines:
        if line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) >= 2 and parts[1].strip() == '-1':
            out.append(int(parts[0]))
    return sorted(out)


def find_gauss_decomp(p):
    """Find a, b with a^2 + b^2 = p."""
    for a in range(1, int(p**0.5) + 1):
        b_sq = p - a * a
        b = int(b_sq**0.5)
        if b * b == b_sq:
            return a, b
    return None, None


def gi_p1_factor(p, N, B1, log_lines=None, base_a=None, base_b=None):
    """Run Gaussian Integer P-1 on M(p) co-factor N.
    Use Gaussian base (a + bi) where a^2 + b^2 = p (or some other choice).
    """
    if base_a is None or base_b is None:
        # Use p = a^2 + b^2 decomposition
        base_a, base_b = find_gauss_decomp(p)
        if base_a is None:
            # p cannot be written as a^2 + b^2; use fallback (a=1, b=p-1 won't work, just use any)
            base_a, base_b = 1, 1
    
    g = (mpz(base_a), mpz(base_b))  # base + 0i
    
    primes = small_primes_up_to(B1)
    if log_lines is not None:
        log_lines.append(f'  GI-P1: base ({base_a}, {base_b}), norm = {base_a**2 + base_b**2}')
        log_lines.append(f'  Stage 1: {len(primes)} primes up to B1={B1}')
    
    # Stage 1: raise g to E = prod of prime powers <= B1
    check_interval = max(100, len(primes) // 100)
    for idx, q in enumerate(primes):
        e = 1
        while q ** (e + 1) <= B1:
            e += 1
        g = gauss_pow(g, q ** e, N)
        
        # Periodic gcd check
        if (idx + 1) % check_interval == 0:
            re_part, im_part = g
            # Check gcd(Re - 1, N): Re(g^E) ≡ 1 (mod q) catches "split" case
            G = gcd(re_part - 1, N)
            if 1 < G < N:
                if log_lines is not None:
                    log_lines.append(f'  Step {idx+1}/{len(primes)}: gcd(Re - 1, N) = {G} (FACTOR!)')
                return int(G)
            # Check gcd(Im, N): Im(g^E) ≡ 0 (mod q) catches "inert" case (g^E is purely real)
            G = gcd(im_part, N)
            if 1 < G < N:
                if log_lines is not None:
                    log_lines.append(f'  Step {idx+1}/{len(primes)}: gcd(Im, N) = {G} (FACTOR!)')
                return int(G)
            # Also gcd(Re + 1, N): Re ≡ -1 (mod q), i.e., order is exactly 2*E
            G = gcd(re_part + 1, N)
            if 1 < G < N:
                if log_lines is not None:
                    log_lines.append(f'  Step {idx+1}/{len(primes)}: gcd(Re + 1, N) = {G} (FACTOR!)')
                return int(G)
    
    # Final gcd checks
    re_part, im_part = g
    G = gcd(re_part - 1, N)
    if 1 < G < N:
        if log_lines is not None:
            log_lines.append(f'  Final: gcd(Re - 1, N) = {G} (FACTOR!)')
        return int(G)
    G = gcd(im_part, N)
    if 1 < G < N:
        if log_lines is not None:
            log_lines.append(f'  Final: gcd(Im, N) = {G} (FACTOR!)')
        return int(G)
    G = gcd(re_part + 1, N)
    if 1 < G < N:
        if log_lines is not None:
            log_lines.append(f'  Final: gcd(Re + 1, N) = {G} (FACTOR!)')
        return int(G)
    
    # Also check gcd(Norm - p, N) — norm(g^E) ≡ p^E (mod N). If q | (p^E - 1), then...
    # Norm(g) = base_a^2 + base_b^2 = p. Norm(g^E) = p^E.
    # If p^E ≡ 1 (mod q), then... hmm, this is just gcd(p^E - 1, N), which is P-1 with base p!
    # Not particularly new.
    
    if log_lines is not None:
        log_lines.append(f'  No factor found in stage 1')
    return None


def main():
    p = 1237
    F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
    M = mpz(2)**p - 1
    N = M // F1
    
    log('=' * 70)
    log('Gaussian Integer P-1 (GI-P1) — novel method')
    log(f'  Target: M({p})/F1, {len(str(N))} digits')
    
    # Verify p = a^2 + b^2
    a, b = find_gauss_decomp(p)
    log(f'  p = {p} = {a}^2 + {b}^2')
    log(f'  Gaussian base: ({a} + {b}i)')
    log(f'  Norm(base) = p = {p}')
    log(f'  In Z[i]/N: base order divides (q-1)^2 (split) or q^2-1 (inert) for q | N')
    log('=' * 70)
    
    if is_prime(N):
        log('N is already prime — done')
        return
    
    # Try with multiple B1 values
    for B1 in [1_000_000, 10_000_000]:
        log_lines = []
        log(f'Trying B1 = {B1}')
        t0 = time.time()
        factor = gi_p1_factor(p, N, B1, log_lines=log_lines)
        elapsed = time.time() - t0
        for line in log_lines:
            log(line)
        log(f'  Total time: {elapsed:.1f}s')
        
        if factor is not None:
            log(f'  >>> FACTOR FOUND: {factor} ({len(str(factor))} digits)')
            if not is_prime(factor):
                f_int = factor
                sub = []
                for sp in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]:
                    while f_int % sp == 0:
                        sub.append(sp)
                        f_int //= sp
                if f_int > 1 and is_prime(f_int):
                    sub.append(f_int)
                log(f'  Composite, sub-factors: {sub}')
                smallest = min(sub) if sub else None
                if smallest is not None and smallest < int(F1):
                    log(f'  Updating factors file with {smallest}')
                    update_factor_file(p, smallest)
                    cofactor = M // smallest
                    append_complete(p, smallest, cofactor)
            else:
                if factor < int(F1):
                    log(f'  Updating factors file with {factor}')
                    update_factor_file(p, factor)
                    cofactor = M // factor
                    append_complete(p, factor, cofactor)
            break
        
        if time.time() - t0 > 100:
            break
    
    # Now try on all 204 missing primes
    log('')
    log('=' * 70)
    log(f'Trying GI-P1 on all 204 missing primes')
    log('=' * 70)
    
    missing = get_missing()
    # Filter to primes that can be written as a^2 + b^2 (p ≡ 1 mod 4)
    missing_with_decomp = []
    missing_no_decomp = []
    for mp in missing:
        a, b = find_gauss_decomp(mp)
        if a is not None:
            missing_with_decomp.append((mp, a, b))
        else:
            missing_no_decomp.append(mp)
    log(f'  Primes with a^2+b^2 decomposition: {len(missing_with_decomp)}')
    log(f'  Primes without (p ≡ 3 mod 4): {len(missing_no_decomp)}')
    
    total_found = 0
    t_start = time.time()
    B1 = 1_000_000  # fast B1
    
    for idx, (mp, a, b) in enumerate(missing_with_decomp, 1):
        if time.time() - t_start > 95:
            log(f'  Time budget exceeded at p={mp}')
            break
        t0 = time.time()
        log(f'  [{idx}/{len(missing_with_decomp)}] p={mp} = {a}^2 + {b}^2, GI-P1 with B1={B1}')
        Mp = mpz(2)**mp - 1
        log_lines_p = []
        factor = gi_p1_factor(mp, Mp, B1, log_lines=log_lines_p, base_a=a, base_b=b)
        elapsed_p = time.time() - t0
        for line in log_lines_p[-5:]:
            log(line)
        log(f'    time: {elapsed_p:.1f}s')
        if factor is not None:
            log(f'  >>> p={mp}: FACTOR: {factor} ({len(str(factor))} digits)')
            if not is_prime(factor):
                f_int = factor
                sub = []
                for sp in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]:
                    while f_int % sp == 0:
                        sub.append(sp)
                        f_int //= sp
                if f_int > 1 and is_prime(f_int):
                    sub.append(f_int)
                smallest = min(sub) if sub else None
                if smallest is not None:
                    update_factor_file(mp, smallest)
                    cofactor = Mp // smallest
                    append_complete(mp, smallest, cofactor)
                    total_found += 1
            else:
                update_factor_file(mp, factor)
                cofactor = Mp // factor
                append_complete(mp, factor, cofactor)
                total_found += 1
            log(f'    Updated factors file!')
    
    elapsed_total = time.time() - t_start
    log('')
    log('=' * 70)
    log(f'GI-P1 complete. Total {total_found} factor(s) found in {elapsed_total:.1f}s')
    log('=' * 70)


if __name__ == '__main__':
    main()
