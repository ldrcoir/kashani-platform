#!/usr/bin/env python3
"""
Mersenne-Aware Multi-Discriminant Williams P+1 Cascade.

WHY THIS IS DIFFERENT:
  Standard Williams P+1 uses random base P (random discriminant D = P^2 - 4Q).
  For Mersenne M(p) with p ≡ 1 (mod 4), Aurifeuillean factorization gives:
    M(p) = A^2 - 2p * B^2
  which implies (2p/q) = +1 for ALL prime factors q | M(p).
  This is a STRONG algebraic constraint on q.

  We use discriminants D that EXPLOIT this constraint:
    D = 8p:    (D/q) = (8p/q) = (2/q)(p/q) = (2/q)(+1) = (2/q)
               → finds q with q ≡ ±3 (mod 8)  [where (2/q)=-1, P+1 active]
    D = -8p:   (D/q) = (-8p/q) = (-1/q)(2/q)(p/q) = (-1/q)(2/q)
               → finds q with q ≡ 3 (mod 4) AND q ≡ ±1 (mod 8)
    D = p:     (D/q) = (p/q) = (q/p) by QR (since p ≡ 1 mod 4)
               → finds q with (q/p) = -1, i.e., q quadratic non-residue mod p
    D = 2p^2:  etc.

  Each D targets a DIFFERENT subset of factors. P+1 with random D only catches
  the subset matching that random D. With Mersenne-informed D, we cover more
  subsets systematically.

  Each D is parameterized by (P, Q) such that P^2 - 4Q = D.
"""

import sys
import time
import json
import random
from pathlib import Path
from math import gcd as math_gcd, log

import gmpy2
from gmpy2 import mpz, gcd as gmpy_gcd, is_prime, invert, powmod, jacobi

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
LOG_FILE = BASE / 'logs/M1237_mpp1.log'
STATE_FILE = BASE / 'logs/M1237_mpp1_state.json'

M = mpz(2)**1237 - 1
F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
p = 1237


def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]


def lucas_V_chain(k, P, Q, N):
    """Compute V_k(P, Q) mod N via Montgomery ladder.
    Returns (V_k, Q^k) mod N.
    Maintains (V_n, V_{n+1}, Q^n, Q^{n+1}) through ladder.
    """
    P = mpz(P) % N
    Q = mpz(Q) % N
    Vn = mpz(2)
    Vn1 = P
    Qn = mpz(1)
    Qn1 = Q
    bits = bin(k)[2:]
    for bit in bits:
        V2n = (Vn * Vn - 2 * Qn) % N
        V2n1 = (Vn * Vn1 - P * Qn) % N
        V2n2 = (Vn1 * Vn1 - 2 * Qn1) % N
        Q2n = (Qn * Qn) % N
        Q2n1 = (Qn * Qn1) % N
        Q2n2 = (Qn1 * Qn1) % N
        if bit == '0':
            Vn, Vn1, Qn, Qn1 = V2n, V2n1, Q2n, Q2n1
        else:
            Vn, Vn1, Qn, Qn1 = V2n1, V2n2, Q2n1, Q2n2
    return Vn, Qn


def pp1_one_curve(N, P, Q, B1, B2):
    """One P+1 run: returns factor or None.
    Stage 1: V_k mod N for k = prod of prime powers <= B1.
    Stage 2 (OPTIMIZED): giant-step / baby-step approach.
      Precompute V_d for small d in (B1, B1*D), then for each "giant step" G = B1 * D * i,
      compute V_G * V_d^{-1} and gcd.

    Implementation note: For P+1 stage 2, the standard "improved standard continuation"
    precomputes V_d for prime differences d in (B1, B1+D). Then for each prime p in (B1, B2],
    write p = B1 + i*D + d for small i and d, and V_p = V_{B1+i*D+d} = V_{B1+i*D} * V_d - Q^d * V_{...}.
    This is complex. A simpler approach: just do stage 1 with much higher B1, no stage 2.

    For now: skip stage 2, do stage 1 with B1 = max(B1, B2/10).
    """
    # If B2 > B1 and we can't do efficient stage 2, just bump B1
    B1_effective = max(B1, B2 // 10) if B2 > B1 else B1

    # Stage 1
    cur_V = mpz(P) % N
    cur_Q = mpz(Q) % N
    primes = small_primes_up_to(B1_effective)
    for q in primes:
        e = 1
        while q ** (e + 1) <= B1_effective:
            e += 1
        pe = q ** e
        new_V, new_Q = lucas_V_chain(pe, cur_V, cur_Q, N)
        cur_V = new_V
        cur_Q = new_Q

    g = gmpy_gcd(cur_V - 2, N)
    if 1 < g < N:
        return int(g)
    if g == N:
        return None  # bad base
    return None


def update_factor_file(p_n, factor):
    lines = FACTORS_FILE.read_text(encoding='utf-8').splitlines(keepends=True)
    out = []
    updated = False
    for line in lines:
        if line.startswith('#'):
            out.append(line); continue
        parts = line.split('\t')
        if len(parts) >= 2 and parts[0] == str(p_n):
            cur = parts[1].strip()
            if cur == '-1' or int(factor) < int(cur):
                out.append(f'{p_n}\t{factor}\n'); updated = True
            else:
                out.append(line)
        else:
            out.append(line)
    if updated:
        FACTORS_FILE.write_text(''.join(out), encoding='utf-8')
    return updated


def append_complete(p_n, factor, cofactor):
    with open(COMPLETE_FILE, 'a', encoding='utf-8') as f:
        f.write(f'{p_n}\tFULL\t{factor}\t{cofactor}\n')


def log_msg(msg):
    print(msg, file=sys.stderr)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')


def save_state(idx, total, found, stage, d_name):
    state = {
        'target': 'M(1237) cofactor (303 digits)',
        'method': 'Mersenne-aware multi-D P+1',
        'current_idx': idx,
        'total_attempts': total,
        'found_count': found,
        'stage': stage,
        'd_name': d_name,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding='utf-8')


def factor_with_base(N, P, Q, B1, B2, d_name, log_lines):
    """Try to factor N with this P+1 base. Returns factor or None."""
    D = (P * P - 4 * Q) % N
    try:
        j = jacobi(D, N)
        log_lines.append(f'    D={D}, Jacobi(D,N)={j}')
    except Exception:
        log_lines.append(f'    D={D}, Jacobi failed (N composite)')
    t0 = time.time()
    f = pp1_one_curve(N, P, Q, B1, B2)
    dt = time.time() - t0
    log_lines.append(f'    elapsed: {dt:.1f}s')
    return f


def process_factor(f, N, log_lines, total_found):
    """Process a found factor: split, update tables, reduce N. Returns new N."""
    if not is_prime(f):
        log_lines.append(f'    composite factor, splitting by trial division')
        f_int = f
        sub = []
        for sp in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]:
            while f_int % sp == 0:
                sub.append(sp)
                f_int //= sp
        if f_int > 1 and is_prime(f_int):
            sub.append(f_int)
        log_lines.append(f'    sub-factors: {sub}')
        for sf in sub:
            if sf < int(F1):
                log_lines.append(f'    new SMALLER than F1: {sf} → UPDATE TABLE')
                update_factor_file(1237, sf)
            while N % sf == 0:
                N //= sf
            log_lines.append(f'    reduced N by {sf}, new N digits: {len(str(N))}')
    else:
        log_lines.append(f'    prime factor: {f} ({len(str(f))} digits)')
        if f < int(F1):
            log_lines.append(f'    new SMALLER than F1: {f} → UPDATE TABLE')
            update_factor_file(1237, f)
        while N % f == 0:
            N //= f
        log_lines.append(f'    reduced N by {f}, new N digits: {len(str(N))}')

    if is_prime(N):
        log_lines.append(f'    N now prime — DONE')
    elif N == 1:
        log_lines.append(f'    N = 1 — DONE')
    return N, total_found + 1


def main():
    N = M // F1
    log_msg('=' * 70)
    log_msg('Mersenne-Aware Multi-Discriminant Williams P+1 Cascade')
    log_msg(f'  Target: M(1237) cofactor, {len(str(N))} digits')
    log_msg(f'  Known F1 = {F1} ({len(str(F1))} digits)')
    log_msg(f'  Mersenne p = 1237')
    log_msg(f'  Strategy: Use discriminants D ∈ {{8p, -8p, p, 5, 13, 17}}')
    log_msg(f'  Each D targets a different subset of factors via Jacobi symbol')
    log_msg('=' * 70)

    if is_prime(N):
        log_msg('N is already prime — done')
        return

    # Mersenne-informed discriminants
    # D = 8p = 9896, P^2 ≡ 0 mod 4 (P even): e.g., P=2, Q=-2473
    # D = -8p = -9896, P even: P=2, Q=2475
    # D = p = 1237, P odd: P=35, Q=-3 (35^2 - 4*(-3) = 1225 + 12 = 1237)
    # D = 5: P=3, Q=1
    # D = 13: P=7, Q=9 (49 - 36 = 13)
    # D = 17: P=9, Q=16 (81 - 64 = 17)
    # D = -3: P=1, Q=1 (1 - 4 = -3) — wait, 1-4 = -3, but P=1 odd, P^2 - 4Q = 1 - 4 = -3
    # D = 29: P=11, Q=23 (121 - 92 = 29)
    # D = -7: P=3, Q=4 (9 - 16 = -7)
    # D = -11: P=3, Q=5 (9 - 20 = -11)
    # D = -15: P=1, Q=4 (1 - 16 = -15)
    # D = 37: P=7, Q=3 (49 - 12 = 37)
    # D = -p = -1237: P^2 - 4Q = -1237. P odd: P^2 ≡ 1, 4Q = 1 + 1237 = 1238, Q = 309.5 (no).
    #                 P even: P^2 ≡ 0, 4Q = 1237, Q = 309.25 (no).  Skip.
    # D = 2p = 2474, 2 mod 4: no integer (P,Q).

    # Mersenne-informed D's (primary)
    # NOTE: Jacobi(8p, N) = +1, Jacobi(-8p, N) = +1, Jacobi(p, N) = +1
    # This means ALL factors q | N have (8p/q) = (p/q) = (2p/q) = +1.
    # P+1 with D = 8p, -8p, p CANNOT find any factor (acts as P-1).
    # The factors of N satisfy additional constraints beyond Aurifeuillean!

    # D's with Jacobi = -1 (active P+1):
    #   D = 5: Jacobi = -1  → at least one factor has (5/q) = -1
    #   D = 37: Jacobi = -1
    #   D = -15: Jacobi = -1
    # D's with Jacobi = +1 (P+1 acts as P-1, less effective):
    #   D = 13, 17, 29, -3, -7, -11, 2p, 8p, -8p, p, -p
    # Strategy: focus on D's with Jacobi = -1, since those have at least one
    # factor with (D/q) = -1, meaning P+1 stage 1 actually works on that factor.

    bases_active = [
        # D = 5: P=3, Q=1
        (3, 1, "D=5 (Jacobi=-1)"),
        (5, 5, "D=5 alt"),
        (11, 29, "D=5 alt2"),
        # D = 37: P=7, Q=3 (49-12=37)
        (7, 3, "D=37 (Jacobi=-1)"),
        # D = -15: P=1, Q=4 (1-16=-15)
        (1, 4, "D=-15 (Jacobi=-1)"),
        # D = -3: P=1, Q=1 (1-4=-3) — Jacobi=+1 but covers different case
        (1, 1, "D=-3 (Jacobi=+1, different)"),
    ]

    # Less active D's — run them but with lower priority
    bases_passive = [
        (7, 9, "D=13"),
        (9, 16, "D=17"),
        (11, 23, "D=29"),
        (3, 4, "D=-7"),
        (3, 5, "D=-11"),
    ]

    all_bases = bases_active + bases_passive

    B1 = 10_000_000  # 1e7 — fast (~30s per base)
    B2 = 100_000_000  # 1e8

    log_msg(f'B1 = {B1}, B2 = {B2}')
    log_msg(f'Total bases: {len(all_bases)}')
    log_msg('')

    total_found = 0
    current_N = N
    for idx, (P, Q, d_name) in enumerate(all_bases, 1):
        log_lines = []
        log_msg(f'=== [{idx}/{len(all_bases)}] P={P}, Q={Q}, {d_name} ===')
        if is_prime(current_N):
            log_msg(f'  N is prime — stopping')
            break
        f = factor_with_base(current_N, P, Q, B1, B2, d_name, log_lines)
        for line in log_lines:
            log_msg(line)
        if f is not None:
            log_msg(f'  >>> FOUND factor: {f} ({len(str(f))} digits)')
            current_N, total_found = process_factor(f, current_N, [], total_found)
            save_state(idx, len(all_bases), total_found, 'found', d_name)
        else:
            log_msg(f'  no factor with this D')
            save_state(idx, len(all_bases), total_found, 'no_factor', d_name)
        log_msg('')

    log_msg('')
    log_msg('=' * 70)
    log_msg(f'Final: {total_found} factor(s) found')
    log_msg(f'Remaining N: {len(str(current_N))} digits, is_prime={is_prime(current_N)}')
    log_msg('=' * 70)


if __name__ == '__main__':
    main()
