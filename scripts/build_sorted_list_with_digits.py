#!/usr/bin/env python3
"""
Build a complete sorted list of all prime factors of Mersenne numbers
with the digit count in parentheses next to each prime.

Format:
  3 (1 digit)
  7 (1 digit)
  23 (2 digits)
  31 (2 digits)
  ...

Includes:
- All prime factors of all M(n) for n in [2, 199] (from previous full factorization)
- All prime factors from A136030_first_191_full_factorizations.txt (M(p) for prime p up to 1259)
- All prime factors from A136030_complete_factorizations.txt
- All prime factors from Cunningham table propagation

Cuts off at 75-digit primes (user request: "ta adad avale 75 raghami pish boro").
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
from gmpy2 import is_prime

BASE = Path('/home/z/my-project')
ALL_LT_200_FILE = BASE / 'download/Mersenne_ALL_factorizations_n_lt_200.txt'
FIRST_191_FILE = BASE / 'download/A136030_first_191_full_factorizations.txt'
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
OUTPUT_FILE = BASE / 'download/Mersenne_prime_factors_sorted_with_digits.txt'

MAX_DIGITS = 75  # cutoff per user request


def parse_factorizations_file(path):
    """Parse a file with lines like 'M(n) = 2^n - 1 = f1 * f2 * ...'.
    Returns dict {n: [factors]}.
    """
    out = {}
    line_re = re.compile(r'M\((\d+)\)\s*=\s*2\^\d+\s*-\s*1\s*=\s*(.+?)(?:\s*\[|$)')
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = line_re.search(line)
            if not m:
                continue
            n = int(m.group(1))
            rhs = m.group(2).strip()
            # Parse factors - may have exponents like 7^2
            factors = []
            for token in rhs.split('*'):
                token = token.strip()
                if not token:
                    continue
                # Handle p^e
                if '^' in token:
                    base, exp = token.split('^')
                    base = int(base.strip())
                    exp = int(exp.strip())
                    for _ in range(exp):
                        factors.append(base)
                else:
                    factors.append(int(token))
            out[n] = factors
    return out


def parse_first_191(path):
    """Parse A136030_first_191_full_factorizations.txt.
    Format: [idx] M(p) = f1 * f2 * ...
    """
    out = {}
    line_re = re.compile(r'\[\d+\]\s+M\((\d+)\)\s*=\s*(.+)')
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = line_re.match(line.strip())
            if not m:
                continue
            p = int(m.group(1))
            rhs = m.group(2).strip()
            factors = [int(t) for t in re.findall(r'\d+', rhs)]
            out[p] = factors
    return out


def parse_complete(path):
    """Parse A136030_complete_factorizations.txt.
    Format: [STATUS] M(p) = f1 * f2 * ...
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
            # Strip annotations
            rhs = re.sub(r'\s*\([^)]*\)\s*$', '', rhs)
            factors = [int(t) for t in re.findall(r'\d+', rhs)]
            out[p] = (status, factors)
    return out


def main():
    print('Loading factorizations ...', file=sys.stderr)
    
    # Source 1: all n < 200 factorizations
    all_lt_200 = parse_factorizations_file(ALL_LT_200_FILE)
    print(f'  all_lt_200: {len(all_lt_200)} entries', file=sys.stderr)
    
    # Source 2: first 191 (prime p up to 1259)
    first_191 = parse_first_191(FIRST_191_FILE)
    print(f'  first_191: {len(first_191)} entries', file=sys.stderr)
    
    # Source 3: complete file
    complete = parse_complete(COMPLETE_FILE)
    print(f'  complete: {len(complete)} entries', file=sys.stderr)
    
    # Merge: collect all prime factors
    # Map each prime to the set of M(n) values it divides
    prime_to_mns = defaultdict(set)
    
    # From all_lt_200
    for n, factors in all_lt_200.items():
        for f in set(factors):
            prime_to_mns[f].add(n)
    
    # From first_191 (these are M(p) for prime p, FULL factorization)
    for p, factors in first_191.items():
        for f in set(factors):
            prime_to_mns[f].add(p)
    
    # From complete (only FULL status)
    for p, (status, factors) in complete.items():
        if status in ('FULL', 'MERSE'):
            for f in set(factors):
                prime_to_mns[f].add(p)
    
    # Build sorted list of unique primes
    all_primes = sorted(prime_to_mns.keys())
    print(f'\nTotal unique primes: {len(all_primes)}', file=sys.stderr)
    
    # Filter to those with <= MAX_DIGITS digits
    primes_with_digits = []
    for p in all_primes:
        digits = len(str(p))
        if digits <= MAX_DIGITS:
            primes_with_digits.append((p, digits))
    
    print(f'Primes with <= {MAX_DIGITS} digits: {len(primes_with_digits)}', file=sys.stderr)
    
    # Sort by value
    primes_with_digits.sort()
    
    # Write output
    lines = []
    lines.append('Complete sorted list of prime factors of Mersenne numbers M(n) = 2^n - 1')
    lines.append(f'Limited to primes with at most {MAX_DIGITS} digits')
    lines.append('=' * 70)
    lines.append('')
    lines.append(f'Total primes listed: {len(primes_with_digits)}')
    lines.append('')
    lines.append('Each line: prime (N digits) - divides M(n1), M(n2), ...')
    lines.append('')
    
    for p, digits in primes_with_digits:
        mns = sorted(prime_to_mns[p])
        if len(mns) <= 10:
            mns_str = ', '.join(f'M({n})' for n in mns)
        else:
            mns_str = f'M({mns[0]}), ..., M({mns[-1]}) ({len(mns)} Mersennes)'
        lines.append(f'{p} ({digits} digits) - divides {mns_str}')
    
    # Also write a clean comma-separated list of just the primes
    lines.append('')
    lines.append('=' * 70)
    lines.append('Comma-separated list of all primes:')
    lines.append(', '.join(str(p) for p, _ in primes_with_digits))
    
    OUTPUT_FILE.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'\nWritten to {OUTPUT_FILE}', file=sys.stderr)
    
    # Summary
    print(f'\nSummary:', file=sys.stderr)
    print(f'  Total primes: {len(primes_with_digits)}', file=sys.stderr)
    print(f'  Smallest: {primes_with_digits[0][0]} ({primes_with_digits[0][1]} digits)', file=sys.stderr)
    print(f'  Largest:  {primes_with_digits[-1][0]} ({primes_with_digits[-1][1]} digits)', file=sys.stderr)
    
    # Distribution by digit count
    print(f'\nDistribution by digit count:', file=sys.stderr)
    by_digits = defaultdict(int)
    for _, d in primes_with_digits:
        by_digits[d] += 1
    for d in sorted(by_digits.keys()):
        print(f'  {d} digits: {by_digits[d]} primes', file=sys.stderr)


if __name__ == '__main__':
    main()
