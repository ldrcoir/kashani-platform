#!/usr/bin/env python3
"""
Williams P+1 factoring on the M(1237) cofactor.

WHY THIS IS DIFFERENT FROM P-1:
  - P-1 finds q when q-1 is smooth.
  - P+1 finds q when q+1 is smooth (using Lucas sequences V_k).
  - For Mersenne factors q = 2*1237*k + 1:
      q - 1 = 2 * 1237 * k              (P-1 needs k smooth)
      q + 1 = 2 * (1237*k + 1)          (P+1 needs 1237*k + 1 smooth)
  - These are DIFFERENT smoothness conditions.
  - P+1 finds factors that P-1 misses.

ALGORITHM:
  - Lucas sequence V_n(P, Q): V_0=2, V_1=P, V_{n+1} = P*V_n - Q*V_{n-1}
  - Key identity: V_m - 2 is divisible by primes q where P^2 - 4Q has order
    dividing m in (Z/qZ)*, BUT only when the Jacobi symbol (D/q) = -1
    (i.e., when the Lucas sequence "acts like" P+1 method).
  - So we choose bases P such that (D/q) = -1 might hold for q | N.

  Stage 1: compute V_k mod N for k = prod of prime powers <= B1.
           Check gcd(V_k - 2, N).
  Stage 2: for primes p in (B1, B2], multiply V_k by V_p using addition chain.
           Check gcd after each prime.

We start from B1 = 10^8 (high, no low stages).
"""

import sys
import time
import json
import random
from pathlib import Path
from math import gcd, isqrt

import gmpy2
from gmpy2 import mpz, gcd as gmpy_gcd, is_prime, invert, powmod, jacobi

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
LOG_FILE = BASE / 'logs/M1237_pp1.log'
STATE_FILE = BASE / 'logs/M1237_pp1_state.json'

M = mpz(2)**1237 - 1
F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)


def small_primes_up_to(limit):
    """Sieve of Eratosthenes."""
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]


def lucas_V_double(V_n, V_n1, Q_n, P, Q, N):
    """Compute V_{2n} and V_{2n+1} from V_n, V_{n+1}, Q^n.
    V_{2n}   = V_n^2 - 2*Q^n
    V_{2n+1} = V_n*V_{n+1} - P*Q^n
    Also Q^{2n} = (Q^n)^2.
    Returns (V_{2n}, V_{2n+1}, Q^{2n}).
    """
    V2n = (V_n * V_n - 2 * Q_n) % N
    V2n1 = (V_n * V_n1 - P * Q_n) % N
    Q2n = (Q_n * Q_n) % N
    return V2n, V2n1, Q2n


def lucas_V_chain(k, P, Q, N):
    """Compute V_k(P, Q) mod N using Montgomery ladder.
    Returns (V_k, Q^k) mod N.

    Standard Lucas V ladder (correct version):
      Maintain (U_n, U_{n+1}) where U_k = V_k(P, Q).
      Start: (V_0, V_1) = (2, P mod N), Qn = 1 (i.e., Q^0).
      For each bit of k (MSB to LSB, after the leading 1):
        if bit == 0:
          V_{2n}   = V_n^2 - 2*Q^n
          V_{2n+1} = V_n*V_{n+1} - P*Q^n       (since V_{m+n} + V_{m-n}*Q^n = V_m*V_n
                                              with m=n+1, m-n=1: V_{2n+1} = V_n*V_{n+1} - Q^n*V_1 = V_n*V_{n+1} - P*Q^n)
          Q^{2n}   = (Q^n)^2
        if bit == 1:
          V_{2n+1} = V_n*V_{n+1} - P*Q^n       (same formula, with current n)
          V_{2n+2} = V_{n+1}^2 - 2*Q^{n+1}      (V_{2(n+1)})
          Q^{2n+1} = (Q^n)^2 * Q
          (we now treat the result as if base was n+1, so swap roles)

    Actually a cleaner ladder (Lucas "U/V" Montgomery ladder):
      Maintain (V_n, V_{n+1}, Q^n).
      Start with n=0: (V_0=2, V_1=P, Q^0=1).
      For each bit of k from MSB to LSB (process ALL bits):
        - Doubling step:
            V_{2n}   = V_n^2 - 2*Q^n
            V_{2n+1} = V_n*V_{n+1} - P*Q^n
            Q^{2n}   = (Q^n)^2
        - If bit is 1:
            Advance by 1: (V_{2n+1}, V_{2n+2}, Q^{2n+1})
            V_{2n+2} = V_{n+1}^2 - 2*Q^{n+1}    (but we need Q^{n+1}!)
            Q^{2n+1} = Q^{2n} * Q

      Problem: we need Q^{n+1} which we don't track separately.

      Better: maintain (V_n, V_{n+1}, Q^n, Q^{n+1}). Then:
        Doubling:
          V_{2n}   = V_n^2 - 2*Q^n
          V_{2n+1} = V_n*V_{n+1} - P*Q^n     (uses V_1=P and Q^n)
          V_{2n+2} = V_{n+1}^2 - 2*Q^{n+1}
          Q^{2n}   = (Q^n)^2
          Q^{2n+1} = Q^n * Q^{n+1}
        If bit=0: keep (V_{2n}, V_{2n+1}, Q^{2n}, Q^{2n+1})
        If bit=1: keep (V_{2n+1}, V_{2n+2}, Q^{2n+1}, Q^{2n+2})
                  Need Q^{2n+2} = (Q^{n+1})^2.
    """
    P = mpz(P) % N
    Q = mpz(Q) % N
    # Start with n=0: V_0=2, V_1=P, Q^0=1, Q^1=Q
    Vn = mpz(2)
    Vn1 = P
    Qn = mpz(1)
    Qn1 = Q

    # Process bits of k from MSB
    bits = bin(k)[2:]
    for bit in bits:
        # Doubling step
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


def pp1_stage1(N, P, Q, B1, log_lines=None):
    """Stage 1: compute V_k mod N for k = prod of prime powers <= B1.
    Returns factor or None."""
    # k = prod of q^e for q prime, q^e <= B1
    # We compute V_k incrementally: V_{k*pp} from V_k, V_{k*pp/p}, ...
    # Simpler: compute V_k for k = each prime power, then chain multiply.
    # Actually, Lucas V satisfies V_{ab} = V_a(V_b, Q^b) - so we can do nested.
    # Even simpler: compute k = prod(q^e), then V_k via ladder ONCE.
    # But k is HUGE (10^big), so we can't store k as int and do ladder.
    # We need to incrementally multiply V values.

    # Standard approach: compute V_k by doing ladder with k = prime power, then
    # "compose" two V values: V_{ab} from V_a and V_b.
    # V_{ab} = V_a(V_b(P, Q), Q^b) - i.e., compute V_a with base P' = V_b, Q' = Q^b.
    # Equivalently: V_{ab}(P, Q) = V_b(P, Q)^2 - 2*Q^{b*(a-1)} ... it's complex.

    # Cleanest: maintain current V_n and Q^n. For each prime power q^e, do
    # ladder with exponent q^e (using current P, Q replaced by Q = Q^{n}).
    # Actually the right approach is "P+1 power-ladder":
    #   Maintain (V_n, Q^n). To multiply by q^e:
    #     Compute V_{n * q^e} via ladder with exponent q^e, treating current
    #     state as the "base".
    #   The ladder step uses P_eff = V_{n+1} / V_n  (mod N), but that's tricky.

    # Alternative clean approach: just compute V_k for k = prod of prime powers,
    # using the ladder in "streaming" fashion: chain together prime power
    # exponents as a single bit string. Each prime power q^e has bit-length
    # log2(q^e) <= log2(B1). We concatenate bit-strings and do ladder.
    # The ladder naturally computes V_{k1 * k2 * k3 ...} if we use the chain rule.

    # Actually no — the ladder is just V_k for a single integer k.
    # If k = k1 * k2, we need V_{k1*k2}, not V_{k1+k2}.
    # V_{k1*k2} = V_{k1}(P'=V_{k2}(P,Q), Q'=Q^{k2})
    # So we compute V_{k2} first, then "compose" with V_{k1} using new base.

    # Let me just implement the standard incremental approach:
    #   cur_V = V_k (current), cur_Q = Q^k (current)
    #   For each prime q, with exponent e (so q^e <= B1):
    #     We want to update: V_k -> V_{k * q^e}
    #     V_{k * q^e}(P, Q) = V_{q^e}(P'=V_k, Q'=Q^k) ? NO
    #     The correct identity: V_{ab}(P, Q) = V_a(V_b(P,Q), Q^b)
    #     i.e., compute V_a using base P' = V_b, Q' = Q^b.
    #     So if we have V_b and Q^b, we can compute V_a with the ladder
    #     using P' = V_b, Q' = Q^b.
    #     Then the result V_a(P', Q') = V_{a*b}(P, Q).
    #     And Q^{a*b} = (Q^b)^a = (Q')^a.
    #   So we maintain (cur_V, cur_Q) and for each prime q with exponent e,
    #   run ladder with P_eff = cur_V, Q_eff = cur_Q, exponent q^e.
    #   Result: new (cur_V, cur_Q) corresponding to V_{k * q^e}.

    cur_V = mpz(P) % N  # V_1
    cur_Q = mpz(1)       # Q^1 = Q... wait, Q^1 = Q. We need to track Q^k.
    # Actually: V_1 = P, and Q^1 = Q.
    # Let me start with cur_V = P, cur_Q = Q (representing V_1, Q^1).
    cur_Q = mpz(Q) % N

    primes = small_primes_up_to(B1)
    if log_lines is not None:
        log_lines.append(f'  P+1 Stage 1: {len(primes)} primes up to B1={B1}')

    import math
    for q in primes:
        e = 1
        while q ** (e + 1) <= B1:
            e += 1
        pe = q ** e
        # Compute V_{pe}(P'=cur_V, Q'=cur_Q) -> this gives V_{k*pe}(P, Q)
        new_V, new_Q = lucas_V_chain(pe, cur_V, cur_Q, N)
        cur_V = new_V
        cur_Q = new_Q
        # Periodic gcd check (cheap)
        # Actually only check at end of stage 1 to save time

    # Stage 1 gcd: gcd(V_k - 2, N)
    g = gmpy_gcd(cur_V - 2, N)
    if 1 < g < N:
        if log_lines is not None:
            log_lines.append(f'  Stage 1 found factor: {g}')
        return int(g), cur_V, cur_Q
    if g == N:
        if log_lines is not None:
            log_lines.append(f'  Stage 1 gcd = N (bad base)')
        return None, cur_V, cur_Q
    if log_lines is not None:
        log_lines.append(f'  Stage 1: no factor (gcd=1)')
    return None, cur_V, cur_Q


def pp1_stage2(N, cur_V, cur_Q, B1, B2, log_lines=None):
    """Stage 2: for primes p in (B1, B2], check gcd(V_p - 2, N).
    We use the identity: V_{p+1}*V_{p-1} - V_p^2 = ... and incremental approach.

    Standard P+1 stage 2: precompute V_d for small d, then for each prime p in
    (B1, B2], compute V_p by V_p = V_{prev_p + delta} via addition formula.
    V_{m+n} = V_m*V_n - Q^n*V_{m-n}
    So V_{p+delta} = V_p * V_delta - Q^delta * V_{p-delta}.

    Simple implementation: for each prime p in (B1, B2], compute V_p from
    scratch using ladder with exponent p. (Slow but correct.)
    """
    if B2 <= B1:
        return None
    primes2 = [p for p in small_primes_up_to(B2) if p > B1]
    if log_lines is not None:
        log_lines.append(f'  P+1 Stage 2: {len(primes2)} primes in ({B1}, {B2}]')

    for p in primes2:
        V_p, Q_p = lucas_V_chain(p, cur_V, cur_Q, N)
        # Wait — V_p(cur_V, cur_Q) gives V_{1*p} with base (cur_V, cur_Q) which
        # equals V_{k * p}(P, Q) where k was the stage-1 exponent.
        # We want gcd(V_{k*p} - 2, N) for each prime p (in stage 2, we extend
        # the exponent by multiplying by p).
        g = gmpy_gcd(V_p - 2, N)
        if 1 < g < N:
            if log_lines is not None:
                log_lines.append(f'  Stage 2 found factor at prime {p}: {g}')
            return int(g)
        if g == N:
            continue  # bad, try next prime
    return None


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


def log(msg):
    print(msg, file=sys.stderr)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')


def save_state(bases_done, stage, found_count):
    state = {
        'target': 'M(1237) cofactor (303 digits)',
        'method': 'Williams P+1',
        'bases_done': bases_done,
        'stage': stage,
        'found_count': found_count,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding='utf-8')


def main():
    N = M // F1
    log('='*70)
    log(f'Williams P+1 factoring of M(1237) cofactor')
    log(f'  N has {len(str(N))} digits')
    log(f'  Known factor F1 = {F1} ({len(str(F1))} digits)')
    log('='*70)

    if is_prime(N):
        log(f'N is already prime — no further factoring needed')
        return

    log(f'N is composite. Starting Williams P+1 with HIGH bounds.')
    log(f'  B1 = 100_000_000 (1e8) — skipping low stages')
    log(f'  B2 = 10_000_000_000 (1e10)')
    log(f'')

    # Multiple Lucas bases — for each, check Jacobi symbol (D/q) = -1 for some q | N
    # (only when D = P^2 - 4Q has Jacobi = -1 does V_k-2 actually catch q).
    # Try multiple P values, Q = 1.
    bases_P = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    Q = 1
    B1 = 100_000_000
    B2 = 10_000_000_000

    total_found = 0
    for idx, P in enumerate(bases_P, 1):
        log(f'=== Base P={P}, Q={Q} ({idx}/{len(bases_P)}) ===')
        t0 = time.time()
        prime_log = []
        # Check Jacobi symbol (D/N) — if +1, P+1 likely won't work for this base
        # but we try anyway (it might still catch some factors).
        D = (P * P - 4 * Q) % N
        # If D is a perfect square mod N (Jacobi=1), P+1 acts like P-1 for this base.
        # Still worth trying.
        log(f'  D = P^2-4Q = {D}')
        try:
            j = jacobi(D, N)
            log(f'  Jacobi(D, N) = {j}')
        except Exception:
            log(f'  Jacobi computation failed (N composite), continuing')

        f, cur_V, cur_Q = pp1_stage1(N, P, Q, B1, prime_log)
        for line in prime_log:
            log(f'  {line}')
        if f is not None:
            log(f'  >>> Stage 1 FOUND: {f} ({len(str(f))} digits)')
            # Process factor
            if not is_prime(f):
                log(f'  factor is composite, splitting with trial division')
                f_int = f
                factors = []
                for sp in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]:
                    while f_int % sp == 0:
                        factors.append(sp)
                        f_int //= sp
                if f_int > 1:
                    if is_prime(f_int):
                        factors.append(f_int)
                log(f'  split: {factors}')
                for sf in factors:
                    if sf < int(F1):
                        log(f'  new smaller factor than F1: {sf} — UPDATE TABLE')
                        update_factor_file(1237, sf)
                    # Check if sf divides N
                    if N % sf == 0:
                        N //= sf
                        log(f'  reduced N by {sf}, new N digits: {len(str(N))}')
                if is_prime(N):
                    log(f'  N now prime — done')
                    break
            else:
                if f < int(F1):
                    log(f'  new smaller factor than F1 — UPDATE TABLE')
                    update_factor_file(1237, f)
                if N % f == 0:
                    N //= f
                    log(f'  reduced N by {f}, new N digits: {len(str(N))}')
                if is_prime(N):
                    log(f'  N now prime — done')
                    break
            total_found += 1
            save_state(idx, 'stage1_found', total_found)
            continue

        # Stage 2
        log(f'  starting stage 2 with B2={B2}')
        f2 = pp1_stage2(N, cur_V, cur_Q, B1, B2, prime_log)
        for line in prime_log:
            if 'Stage 2' in line or 'Stage 1' in line:
                log(f'  {line}')
        if f2 is not None:
            log(f'  >>> Stage 2 FOUND: {f2} ({len(str(f2))} digits)')
            if not is_prime(f2):
                log(f'  factor is composite, splitting')
                f_int = f2
                factors = []
                for sp in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47]:
                    while f_int % sp == 0:
                        factors.append(sp)
                        f_int //= sp
                if f_int > 1 and is_prime(f_int):
                    factors.append(f_int)
                log(f'  split: {factors}')
                for sf in factors:
                    if sf < int(F1):
                        update_factor_file(1237, sf)
                    if N % sf == 0:
                        N //= sf
                if is_prime(N):
                    log(f'  N now prime — done')
                    break
            else:
                if f2 < int(F1):
                    update_factor_file(1237, f2)
                if N % f2 == 0:
                    N //= f2
                if is_prime(N):
                    log(f'  N now prime — done')
                    break
            total_found += 1
            save_state(idx, 'stage2_found', total_found)
        else:
            log(f'  no factor found for base P={P}')
            save_state(idx, 'no_factor', total_found)

        elapsed = time.time() - t0
        log(f'  base P={P} elapsed: {elapsed:.1f}s')
        log('')

    log('')
    log('='*70)
    log(f'Williams P+1 complete. Found {total_found} new factor(s).')
    log(f'Remaining cofactor: {len(str(N))} digits, is_prime={is_prime(N)}')
    log('='*70)


if __name__ == '__main__':
    main()
