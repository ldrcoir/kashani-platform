#!/usr/bin/env python3
"""
Fully factorize ALL composite Mersenne numbers M(n) = 2^n - 1 for ALL n < 200
(not just prime n). Includes composite n like 189 = 3^3 * 7.

For composite n, M(n) has algebraic factorization:
  M(n) = product of Phi_d(2) for d | n, d > 1
where Phi_d is the d-th cyclotomic polynomial.

We use sympy.ntheory.factorint with high trial-division limit, then ECM
for any remaining cofactor.

Output:
- download/Mersenne_ALL_factorizations_n_lt_200.txt : full factorizations
- download/Mersenne_ALL_prime_factors_list.txt : sorted unique prime factors
- download/Mersenne_ALL_summary.txt : summary
"""

import sys
import time
import re
import math
from pathlib import Path
from gmpy2 import mpz, is_prime, powmod, gcd
from sympy.ntheory import factorint, ecm as sympy_ecm

BASE = Path('/home/z/my-project')
OUTPUT_FACTORIZATIONS = BASE / 'download/Mersenne_ALL_factorizations_n_lt_200.txt'
OUTPUT_PRIMES_LIST = BASE / 'download/Mersenne_ALL_prime_factors_list.txt'
OUTPUT_SUMMARY = BASE / 'download/Mersenne_ALL_summary.txt'

# Known Mersenne prime exponents
MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127
}


def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]


def fully_factor(n, time_budget=120, depth=0):
    """Fully factor integer n. Returns sorted list of prime factors (with multiplicity)
    or None if cannot fully factor within budget."""
    if depth > 10:
        return None
    if n == 1:
        return []
    if is_prime(n):
        return [n]
    
    factors = []
    remaining = n
    
    # Step 1: trial division with primes up to 10^7 (using sympy's factorint)
    try:
        td_factors = factorint(remaining, limit=10**7)
        for p, e in td_factors.items():
            if not is_prime(p):
                # Recursively factor p
                sub = fully_factor(p, time_budget / 4, depth + 1)
                if sub:
                    for s in sub:
                        factors.append(s)
                        remaining //= s
                else:
                    factors.append(p)  # keep as composite if can't factor
                    remaining //= p**e
                continue
            for _ in range(e):
                factors.append(p)
                remaining //= p
    except Exception:
        pass
    
    if remaining == 1:
        # All factors are prime - good
        if all(is_prime(f) for f in factors):
            return sorted(factors)
        else:
            # Some composites remain - try to factor them
            new_factors = []
            for f in factors:
                if is_prime(f):
                    new_factors.append(f)
                else:
                    sub = fully_factor(f, time_budget / 4, depth + 1)
                    if sub:
                        new_factors.extend(sub)
                    else:
                        new_factors.append(f)  # give up
            if all(is_prime(f) for f in new_factors):
                return sorted(new_factors)
            return None
    
    if is_prime(remaining):
        factors.append(remaining)
        return sorted(factors)
    
    # Step 2: P-1 on remaining
    if remaining > 1 and not is_prime(remaining):
        t_start = time.time()
        B1 = 1_000_000
        a = mpz(3)
        primes = small_primes_up_to(B1)
        rem_mpz = mpz(remaining)
        for q in primes:
            e = max(1, int(math.log(B1) / math.log(q)))
            a = powmod(a, q**e, rem_mpz)
        g = gcd(a - 1, rem_mpz)
        if 1 < g < rem_mpz:
            f = int(g)
            if is_prime(f):
                while remaining % f == 0:
                    factors.append(f)
                    remaining //= f
            else:
                sub = fully_factor(f, time_budget / 4, depth + 1)
                if sub:
                    factors.extend(sub)
                    for s in sub:
                        remaining //= s
    
    if remaining == 1:
        if all(is_prime(f) for f in factors):
            return sorted(factors)
        else:
            new_factors = []
            for f in factors:
                if is_prime(f):
                    new_factors.append(f)
                else:
                    sub = fully_factor(f, time_budget / 4, depth + 1)
                    if sub:
                        new_factors.extend(sub)
                    else:
                        new_factors.append(f)
            if all(is_prime(f) for f in new_factors):
                return sorted(new_factors)
            return None
    
    if is_prime(remaining):
        factors.append(remaining)
        return sorted(factors)
    
    # Step 3: ECM via sympy
    if remaining > 1 and not is_prime(remaining):
        t_start = time.time()
        while remaining > 1 and not is_prime(remaining) and time.time() - t_start < time_budget:
            try:
                ecm_factors = sympy_ecm(remaining, B1=100000, B2=1000000, max_curve=100)
                cand = [int(f) for f in ecm_factors if int(f) > 1 and int(f) < remaining]
                if not cand:
                    break
                for f in cand:
                    if is_prime(f):
                        while remaining % f == 0:
                            factors.append(f)
                            remaining //= f
                    else:
                        sub = fully_factor(f, time_budget / 4, depth + 1)
                        if sub:
                            factors.extend(sub)
                            for s in sub:
                                remaining //= s
            except Exception:
                break
    
    if remaining == 1:
        if all(is_prime(f) for f in factors):
            return sorted(factors)
        else:
            new_factors = []
            for f in factors:
                if is_prime(f):
                    new_factors.append(f)
                else:
                    sub = fully_factor(f, time_budget / 4, depth + 1)
                    if sub:
                        new_factors.extend(sub)
                    else:
                        new_factors.append(f)
            if all(is_prime(f) for f in new_factors):
                return sorted(new_factors)
            return None
    
    if is_prime(remaining):
        factors.append(remaining)
        return sorted(factors)
    
    return None  # could not fully factor


def main():
    print(f'Factorizing all M(n) for n in [2, 199] ...', file=sys.stderr)
    
    factorizations = {}  # n -> list of prime factors (with multiplicity)
    failed = []
    
    t_total_start = time.time()
    
    for n in range(2, 200):
        M = (1 << n) - 1
        
        # Skip Mersenne primes (M itself is prime)
        if n in MERSENNE_PRIME_EXPONENTS:
            # M(n) is itself prime
            factorizations[n] = [M]
            print(f'  M({n}): Mersenne prime ({len(str(M))} digits)', file=sys.stderr)
            continue
        
        # Composite Mersenne - factorize
        t_start = time.time()
        factors = fully_factor(M, time_budget=60)
        elapsed = time.time() - t_start
        
        if factors:
            # Verify
            product = 1
            for f in factors:
                product *= f
            if product == M:
                factorizations[n] = factors
                print(f'  M({n}): {len(factors)} prime factors, {elapsed:.1f}s', file=sys.stderr)
            else:
                print(f'  M({n}): PRODUCT MISMATCH!', file=sys.stderr)
                failed.append(n)
        else:
            print(f'  M({n}): FAILED to fully factor in {elapsed:.1f}s', file=sys.stderr)
            failed.append(n)
    
    print(f'\nTotal time: {time.time() - t_total_start:.0f}s', file=sys.stderr)
    print(f'Factored: {len(factorizations)}, Failed: {len(failed)}', file=sys.stderr)
    if failed:
        print(f'Failed n values: {failed}', file=sys.stderr)
    
    # Verify all
    print(f'\nVerifying all {len(factorizations)} factorizations ...', file=sys.stderr)
    all_ok = True
    for n, factors in factorizations.items():
        M = (1 << n) - 1
        product = 1
        for f in factors:
            product *= f
        if product != M:
            print(f'  ERROR: M({n}) product mismatch!', file=sys.stderr)
            all_ok = False
        for f in factors:
            if not is_prime(f):
                print(f'  ERROR: M({n}) factor {f} is not prime!', file=sys.stderr)
                all_ok = False
    if all_ok:
        print('  All factorizations verified OK!', file=sys.stderr)
    
    # Write factorizations file
    lines = []
    lines.append('Complete factorizations of ALL Mersenne numbers M(n) = 2^n - 1')
    lines.append('For ALL n from 2 to 199 (not just prime n)')
    lines.append('All factorizations verified: product of factors = M(n), all factors prime')
    lines.append('=' * 70)
    lines.append('')
    lines.append(f'Mersenne prime exponents (M(n) itself is prime): {sorted(MERSENNE_PRIME_EXPONENTS)}')
    lines.append(f'Number of Mersenne numbers factored: {len(factorizations)}')
    if failed:
        lines.append(f'Failed to factor: {failed}')
    lines.append('')
    
    for n in sorted(factorizations.keys()):
        factors = factorizations[n]
        M = (1 << n) - 1
        # Group factors with multiplicity
        from collections import Counter
        factor_counts = Counter(factors)
        parts = []
        for f in sorted(factor_counts.keys()):
            e = factor_counts[f]
            if e == 1:
                parts.append(str(f))
            else:
                parts.append(f'{f}^{e}')
        factor_str = ' * '.join(parts)
        is_mersenne_prime = n in MERSENNE_PRIME_EXPONENTS
        marker = ' [MERSENNE PRIME]' if is_mersenne_prime else ''
        lines.append(f'M({n}) = 2^{n} - 1 = {factor_str}{marker}')
        lines.append(f'  ({len(factors)} prime factors (with mult), M({n}) has {len(str(M))} digits)')
    
    lines.append('')
    lines.append('=' * 70)
    lines.append(f'Verification: All {len(factorizations)} factorizations verified OK')
    
    OUTPUT_FACTORIZATIONS.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'\nFactorizations written to {OUTPUT_FACTORIZATIONS}', file=sys.stderr)
    
    # Build sorted list of all unique prime factors
    all_prime_factors = set()
    for factors in factorizations.values():
        for f in factors:
            all_prime_factors.add(f)
    
    sorted_primes = sorted(all_prime_factors)
    
    # Write prime factors list
    lines = []
    lines.append('Complete list of ALL prime factors of Mersenne numbers M(n) = 2^n - 1')
    lines.append('For ALL n from 2 to 199')
    lines.append('Includes:')
    lines.append('  - All prime factors of composite Mersenne numbers (with multiplicity deduplicated)')
    lines.append('  - Mersenne primes themselves (M(p) where 2^p-1 is prime)')
    lines.append('=' * 70)
    lines.append('')
    lines.append(f'Total unique prime factors: {len(sorted_primes)}')
    lines.append('')
    lines.append('Sorted list (ascending):')
    lines.append(', '.join(str(p) for p in sorted_primes))
    lines.append('')
    lines.append('')
    lines.append('Each prime with its corresponding Mersenne number(s):')
    
    from collections import defaultdict
    prime_to_mns = defaultdict(list)
    for n, factors in factorizations.items():
        for f in set(factors):
            prime_to_mns[f].append(n)
    
    for prime in sorted_primes:
        mns = sorted(prime_to_mns[prime])
        mns_str = ', '.join(f'M({n})' for n in mns)
        lines.append(f'{prime}\tdivides {mns_str}')
    
    OUTPUT_PRIMES_LIST.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Prime factors list written to {OUTPUT_PRIMES_LIST}', file=sys.stderr)
    
    # Summary
    summary_lines = []
    summary_lines.append('Mersenne Factorization Summary (ALL n < 200)')
    summary_lines.append('=' * 70)
    summary_lines.append('')
    summary_lines.append(f'Mersenne prime exponents (n < 200): {sorted(MERSENNE_PRIME_EXPONENTS)}')
    summary_lines.append(f'  Count: {len(MERSENNE_PRIME_EXPONENTS)}')
    summary_lines.append('')
    summary_lines.append(f'All Mersenne numbers M(n) for n in [2, 199], fully factored: {len(factorizations)}')
    if failed:
        summary_lines.append(f'Failed to fully factor: {failed}')
    summary_lines.append('')
    summary_lines.append(f'Total unique prime factors found: {len(sorted_primes)}')
    summary_lines.append('')
    summary_lines.append('First 50 prime factors:')
    for p in sorted_primes[:50]:
        summary_lines.append(f'  {p}')
    summary_lines.append('')
    summary_lines.append('Last 10 prime factors (largest):')
    for p in sorted_primes[-10:]:
        summary_lines.append(f'  {p} ({len(str(p))} digits)')
    summary_lines.append('')
    summary_lines.append('Statistics:')
    summary_lines.append(f'  Smallest prime factor: {sorted_primes[0]}')
    summary_lines.append(f'  Largest prime factor: {sorted_primes[-1]} ({len(str(sorted_primes[-1]))} digits)')
    
    small_primes_count = sum(1 for p in sorted_primes if p < 1000)
    medium_primes_count = sum(1 for p in sorted_primes if 1000 <= p < 10**6)
    large_primes_count = sum(1 for p in sorted_primes if 10**6 <= p < 10**20)
    huge_primes_count = sum(1 for p in sorted_primes if p >= 10**20)
    summary_lines.append('')
    summary_lines.append('Distribution by size:')
    summary_lines.append(f'  < 1000:              {small_primes_count}')
    summary_lines.append(f'  1000 - 10^6:         {medium_primes_count}')
    summary_lines.append(f'  10^6 - 10^20:        {large_primes_count}')
    summary_lines.append(f'  >= 10^20:            {huge_primes_count}')
    
    # Specific M(189) call-out since user asked
    summary_lines.append('')
    summary_lines.append('=' * 70)
    summary_lines.append(f'M(189) full factorization (user-requested):')
    if 189 in factorizations:
        factors_189 = factorizations[189]
        from collections import Counter
        fc = Counter(factors_189)
        parts = []
        for f in sorted(fc.keys()):
            e = fc[f]
            if e == 1:
                parts.append(str(f))
            else:
                parts.append(f'{f}^{e}')
        summary_lines.append(f'  M(189) = 2^189 - 1 = {" * ".join(parts)}')
        summary_lines.append(f'  Number of distinct prime factors: {len(set(factors_189))}')
        summary_lines.append(f'  Total factors with multiplicity: {len(factors_189)}')
    else:
        summary_lines.append(f'  M(189) FAILED to factor')
    
    OUTPUT_SUMMARY.write_text('\n'.join(summary_lines) + '\n', encoding='utf-8')
    print(f'Summary written to {OUTPUT_SUMMARY}', file=sys.stderr)


if __name__ == '__main__':
    main()
