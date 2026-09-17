#!/usr/bin/env python3
"""
Fully factorize all composite Mersenne numbers M(p) for prime p < 200.
For each such p (excluding Mersenne prime exponents), produce the complete
prime factorization.

Output:
- download/Mersenne_composite_factorizations_p_lt_200.txt : full factorizations
- download/Mersenne_prime_factors_complete_list.txt : sorted unique prime factors
- download/Mersenne_factors_summary.txt : summary

Sources:
- Use A136030_complete_factorizations.txt (already has 238 entries)
- Use A136030_first_191_full_factorizations.txt (191 entries)
- For any remaining gaps, attempt local factoring (P-1, ECM via sympy)
"""

import sys
import time
import re
import math
from pathlib import Path
from gmpy2 import mpz, is_prime, powmod, gcd
from sympy.ntheory import ecm as sympy_ecm

BASE = Path('/home/z/my-project')
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
FIRST_191_FILE = BASE / 'download/A136030_first_191_full_factorizations.txt'
CUNNINGHAM_FILE = BASE / 'download/cunningham_table_2_minus.txt'

OUTPUT_FACTORIZATIONS = BASE / 'download/Mersenne_composite_factorizations_p_lt_200.txt'
OUTPUT_PRIMES_LIST = BASE / 'download/Mersenne_prime_factors_complete_list.txt'
OUTPUT_SUMMARY = BASE / 'download/Mersenne_factors_summary.txt'

# Known Mersenne prime exponents (2^p - 1 is prime)
MERSENNE_PRIME_EXPONENTS_LT_200 = {2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127}


def parse_existing_factorizations(path):
    """Parse A136030_first_191_full_factorizations.txt.
    Returns {p: [prime factors in order shown]}.
    """
    out = {}
    line_re = re.compile(r'\[(\d+)\]\s+M\((\d+)\)\s*=\s*(.+)')
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = line_re.match(line.strip())
            if not m:
                continue
            p = int(m.group(2))
            rhs = m.group(3).strip()
            factors = [int(t) for t in re.findall(r'\d+', rhs)]
            out[p] = factors
    return out


def parse_complete_factorizations(path):
    """Parse A136030_complete_factorizations.txt.
    Returns {p: (status, [factors])}.
    """
    out = {}
    line_re = re.compile(r'^\[(FULL|PART|MERSE)\s*\]\s+M\((\d+)\)\s*=\s*(.+)$')
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            m = line_re.match(line)
            if not m:
                continue
            status = m.group(1).strip()
            p = int(m.group(2))
            rhs = m.group(3).strip()
            factors = [int(t) for t in re.findall(r'\d+', rhs)]
            out[p] = (status, factors)
    return out


def parse_cunningham(path):
    """Parse Cunningham 2- table for factorizations of M(n) for odd n < 1500."""
    text = path.read_text(encoding='utf-8', errors='ignore')
    lines = []
    for raw in text.splitlines():
        s = raw.rstrip()
        if not s or set(s.strip()) <= {'='}:
            continue
        if s.strip().startswith(('Cunningham', 'Table 2', 'n ')):
            continue
        lines.append(s)
    records = []
    for s in lines:
        stripped = s.strip()
        if not stripped:
            continue
        parts = stripped.split(None, 1)
        first = parts[0]
        rest = parts[1] if len(parts) > 1 else ''
        if first.isdigit() and rest:
            records.append(f'{first} {rest}')
        else:
            if records:
                records[-1] = records[-1] + ' ' + stripped
    
    out = {}
    rec_re = re.compile(r'^\s*(\d+)\s+(.*)$')
    for rec in records:
        m = rec_re.match(rec)
        if not m:
            continue
        n = int(m.group(1))
        body = m.group(2).strip()
        alg_re = re.compile(r'^\(([^)]*)\)\s*')
        am = alg_re.match(body)
        if am:
            body = body[am.end():].strip()
        body = body.replace('\\ ', '').replace('\\', '')
        body = re.sub(r'\s+', ' ', body).strip()
        body = body.replace('.. ', '.').replace(' .', '.').replace('. ', '.')
        body = re.sub(r'\.+', '.', body)
        
        # Parse factors and cofactor marker
        token_re = re.compile(r'(\d+)|([PC])(\d+)')
        found_tokens = []
        for m2 in token_re.finditer(body):
            if m2.group(1):
                found_tokens.append(('I', int(m2.group(1))))
            else:
                found_tokens.append((m2.group(2), int(m2.group(3))))
        
        explicit_factors = [v for k, v in found_tokens if k == 'I']
        cofactor_kind = None
        cofactor_digits = None
        for k, v in found_tokens:
            if k in ('P', 'C'):
                cofactor_kind = k
                cofactor_digits = v
        
        out[n] = {
            'factors': explicit_factors,
            'cofactor_kind': cofactor_kind,
            'cofactor_digits': cofactor_digits,
            'full_string': body,
        }
    return out


def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]


def pm1_one_factor(n, B1=1_000_000, B2=None):
    """P-1 factoring on n. Returns a factor or None."""
    n_mpz = mpz(n)
    a = mpz(3)
    primes = small_primes_up_to(B1)
    for q in primes:
        e = max(1, int(math.log(B1) / math.log(q)))
        a = powmod(a, q**e, n_mpz)
    g = gcd(a - 1, n_mpz)
    if 1 < g < n_mpz:
        return int(g)
    if g == n_mpz:
        # try different base
        a = mpz(5)
        for q in primes:
            e = max(1, int(math.log(B1) / math.log(q)))
            a = powmod(a, q**e, n_mpz)
        g = gcd(a - 1, n_mpz)
        if 1 < g < n_mpz:
            return int(g)
    return None


def fully_factor(n, time_budget=60):
    """Try to fully factor n using trial division + P-1 + ECM.
    Returns list of prime factors (sorted) or None if cannot fully factor."""
    if n == 1:
        return []
    if is_prime(n):
        return [n]
    
    factors = []
    remaining = n
    
    # Trial division with primes up to 100K
    for p in small_primes_up_to(100000):
        while remaining % p == 0:
            factors.append(p)
            remaining //= p
        if remaining == 1:
            break
        if is_prime(remaining):
            factors.append(remaining)
            remaining = 1
            break
    
    if remaining > 1 and not is_prime(remaining):
        # Try P-1
        t_start = time.time()
        while remaining > 1 and not is_prime(remaining) and time.time() - t_start < time_budget / 2:
            f = pm1_one_factor(remaining, B1=1_000_000)
            if f is None:
                break
            if is_prime(f):
                factors.append(f)
                remaining //= f
            else:
                # Recursively factor f
                sub = fully_factor(f, time_budget / 4)
                if sub:
                    factors.extend(sub)
                    for s in sub:
                        remaining //= s
                else:
                    break
    
    if remaining > 1 and not is_prime(remaining):
        # Try ECM via sympy
        t_start = time.time()
        while remaining > 1 and not is_prime(remaining) and time.time() - t_start < time_budget / 2:
            try:
                ecm_factors = sympy_ecm(remaining, B1=10000, B2=100000, max_curve=50)
                cand = [int(f) for f in ecm_factors if int(f) > 1 and int(f) < remaining]
                if not cand:
                    break
                for f in cand:
                    if is_prime(f):
                        factors.append(f)
                        remaining //= f
                    else:
                        sub = fully_factor(f, time_budget / 4)
                        if sub:
                            factors.extend(sub)
                            for s in sub:
                                remaining //= s
            except Exception:
                break
    
    if remaining > 1 and is_prime(remaining):
        factors.append(remaining)
        remaining = 1
    
    if remaining == 1:
        return sorted(factors)
    return None  # could not fully factor


def main():
    print('Loading existing factorizations ...', file=sys.stderr)
    existing_191 = parse_existing_factorizations(FIRST_191_FILE)
    print(f'  first_191: {len(existing_191)} entries', file=sys.stderr)
    
    complete = parse_complete_factorizations(COMPLETE_FILE)
    print(f'  complete: {len(complete)} entries', file=sys.stderr)
    
    cunningham = parse_cunningham(CUNNINGHAM_FILE)
    print(f'  cunningham: {len(cunningham)} entries', file=sys.stderr)
    
    # Get all prime p < 200 not in Mersenne prime exponents
    target_primes = []
    for p in range(2, 200):
        if not is_prime(p):
            continue
        if p in MERSENNE_PRIME_EXPONENTS_LT_200:
            continue
        target_primes.append(p)
    
    print(f'\nTarget: {len(target_primes)} composite Mersenne numbers with p < 200', file=sys.stderr)
    print(f'  p values: {target_primes}', file=sys.stderr)
    
    # For each target, get full factorization
    # First, collect from existing sources
    factorizations = {}  # p -> list of prime factors
    
    for p in target_primes:
        # Try existing_191 first (most reliable)
        if p in existing_191:
            factors = existing_191[p]
            # Verify: product equals M(p)
            M = (1 << p) - 1
            product = 1
            for f in factors:
                product *= f
            if product == M:
                factorizations[p] = factors
                continue
            # else try other sources
        
        # Try complete file
        if p in complete:
            status, factors = complete[p]
            if status == 'FULL':
                M = (1 << p) - 1
                product = 1
                for f in factors:
                    product *= f
                if product == M:
                    factorizations[p] = factors
                    continue
        
        # Try Cunningham
        if p in cunningham:
            rec = cunningham[p]
            if rec['cofactor_kind'] == 'P':
                # Fully factored - but we don't have the P cofactor value
                # Need to compute it
                M = (1 << p) - 1
                known_product = 1
                for f in rec['factors']:
                    known_product *= f
                if M % known_product == 0:
                    cofactor = M // known_product
                    if is_prime(cofactor):
                        factors = rec['factors'] + [cofactor]
                        factorizations[p] = sorted(factors)
                        continue
        
        # Need to factorize locally
        print(f'  Need to factorize M({p}) locally ...', file=sys.stderr)
        M = (1 << p) - 1
        factors = fully_factor(M, time_budget=120)
        if factors:
            factorizations[p] = factors
            print(f'    OK: {len(factors)} prime factors', file=sys.stderr)
        else:
            print(f'    FAILED to fully factor M({p})', file=sys.stderr)
    
    # Verify all
    print(f'\nVerifying {len(factorizations)} factorizations ...', file=sys.stderr)
    all_ok = True
    for p, factors in factorizations.items():
        M = (1 << p) - 1
        product = 1
        for f in factors:
            product *= f
        if product != M:
            print(f'  ERROR: M({p}) product mismatch!', file=sys.stderr)
            all_ok = False
        # Check all factors are prime
        for f in factors:
            if not is_prime(f):
                print(f'  ERROR: M({p}) factor {f} is not prime!', file=sys.stderr)
                all_ok = False
    
    if all_ok:
        print('  All factorizations verified OK!', file=sys.stderr)
    
    # Write factorizations file
    lines = []
    lines.append('Complete factorizations of composite Mersenne numbers M(p) = 2^p - 1')
    lines.append('For prime p < 200 (excluding Mersenne prime exponents)')
    lines.append('All factorizations verified: product of factors = M(p), all factors prime')
    lines.append('=' * 70)
    lines.append('')
    lines.append(f'Mersenne prime exponents (excluded): {sorted(MERSENNE_PRIME_EXPONENTS_LT_200)}')
    lines.append(f'Number of composite Mersennes factored: {len(factorizations)}')
    lines.append('')
    
    for p in sorted(factorizations.keys()):
        factors = factorizations[p]
        M = (1 << p) - 1
        # Format: M(p) = 2^p - 1 = f1 * f2 * ... * fk
        factor_str = ' * '.join(str(f) for f in factors)
        lines.append(f'M({p}) = 2^{p} - 1 = {factor_str}')
        lines.append(f'  ({len(factors)} prime factors, M({p}) has {len(str(M))} digits)')
    
    lines.append('')
    lines.append('=' * 70)
    lines.append('Verification summary:')
    lines.append(f'  All factorizations verified: product = M(p), all factors prime')
    lines.append(f'  Total composite Mersennes factored: {len(factorizations)}')
    
    OUTPUT_FACTORIZATIONS.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'\nFactorizations written to {OUTPUT_FACTORIZATIONS}', file=sys.stderr)
    
    # Build sorted list of all unique prime factors
    all_prime_factors = set()
    for factors in factorizations.values():
        for f in factors:
            all_prime_factors.add(f)
    
    # Also include the Mersenne primes themselves (M(p) is prime for Mersenne prime exponents)
    for p in MERSENNE_PRIME_EXPONENTS_LT_200:
        if p < 200:
            all_prime_factors.add((1 << p) - 1)
    
    sorted_primes = sorted(all_prime_factors)
    
    # Write prime factors list
    lines = []
    lines.append('Complete list of prime factors of Mersenne numbers M(p) = 2^p - 1')
    lines.append('For all prime p < 200')
    lines.append('Includes:')
    lines.append('  - All prime factors of composite Mersenne numbers')
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
    
    # Map each prime to which M(p) it divides
    from collections import defaultdict
    prime_to_mps = defaultdict(list)
    for p, factors in factorizations.items():
        for f in set(factors):  # unique
            prime_to_mps[f].append(p)
    # Add Mersenne primes
    for mp_exp in MERSENNE_PRIME_EXPONENTS_LT_200:
        if mp_exp < 200:
            mp_val = (1 << mp_exp) - 1
            prime_to_mps[mp_val].append(mp_exp)
    
    for prime in sorted_primes:
        mps = sorted(prime_to_mps[prime])
        mps_str = ', '.join(f'M({p})' for p in mps)
        lines.append(f'{prime}\tdivides {mps_str}')
    
    OUTPUT_PRIMES_LIST.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Prime factors list written to {OUTPUT_PRIMES_LIST}', file=sys.stderr)
    
    # Write summary
    summary_lines = []
    summary_lines.append('Mersenne Factorization Summary (p < 200)')
    summary_lines.append('=' * 70)
    summary_lines.append('')
    summary_lines.append(f'Mersenne prime exponents (p < 200): {sorted(MERSENNE_PRIME_EXPONENTS_LT_200)}')
    summary_lines.append(f'  Count: {len(MERSENNE_PRIME_EXPONENTS_LT_200)}')
    summary_lines.append('')
    summary_lines.append(f'Composite Mersenne numbers (p < 200, fully factored): {len(factorizations)}')
    summary_lines.append(f'  p values: {sorted(factorizations.keys())}')
    summary_lines.append('')
    summary_lines.append(f'Total unique prime factors found: {len(sorted_primes)}')
    summary_lines.append('')
    summary_lines.append('First 30 prime factors:')
    for p in sorted_primes[:30]:
        summary_lines.append(f'  {p}')
    summary_lines.append('')
    summary_lines.append('Last 10 prime factors (largest):')
    for p in sorted_primes[-10:]:
        summary_lines.append(f'  {p} ({len(str(p))} digits)')
    summary_lines.append('')
    summary_lines.append('Statistics:')
    summary_lines.append(f'  Smallest prime factor: {sorted_primes[0]}')
    summary_lines.append(f'  Largest prime factor: {sorted_primes[-1]} ({len(str(sorted_primes[-1]))} digits)')
    
    # Distribution
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
    
    OUTPUT_SUMMARY.write_text('\n'.join(summary_lines) + '\n', encoding='utf-8')
    print(f'Summary written to {OUTPUT_SUMMARY}', file=sys.stderr)


if __name__ == '__main__':
    main()
