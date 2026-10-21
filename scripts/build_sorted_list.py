#!/usr/bin/env python3
"""
Build a sorted list of all smallest prime factors found in A136030.
Format: prime numbers (smallest prime factors of Mersenne numbers) sorted ascending,
starting from 2 onwards.

Also generates range statistics showing:
- How many primes exist in each range
- How many Mersenne prime exponents (which produce prime Mersenne numbers)
- How many primes need a factor (total - Mersenne)
- How many we have found a factor for
- How many are missing
- Coverage percentage

Up to n=12000 as requested.
"""

import sys
import json
from pathlib import Path
from gmpy2 import is_prime

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_50000.txt'
SORTED_LIST_FILE = BASE / 'download/A136030_sorted_smallest_factors.txt'
STATS_FILE = BASE / 'download/A136030_range_statistics.txt'

MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607,
    1279, 2203, 2281, 3217, 4253, 4423, 9689, 9941, 11213,
    19937, 21701, 23209, 44497
}


def main():
    # Read factors table
    rows = []
    with open(FACTORS_FILE, encoding='utf-8') as f:
        for line in f:
            if '\t' in line and not line.startswith('#'):
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    try:
                        n, v = int(parts[0]), parts[1]
                        rows.append((n, v))
                    except ValueError:
                        continue

    # Collect smallest prime factors
    # For each n where we have a factor (v != -1 and v != 0), v is the smallest prime factor of M(n)
    # For n=1, M(1)=1, value is 1 (special)
    # For Mersenne prime exponents, M(n) is itself prime, so the "smallest prime factor" is M(n) = 2^n - 1
    
    smallest_factors = []  # list of (factor_value, n) tuples
    
    for n, v in rows:
        if n > 12000:  # limit to n=12000 as requested
            continue
        if v == '-1':
            continue
        if v == '0':
            # Mersenne prime - the prime factor is M(n) itself = 2^n - 1
            if n in MERSENNE_PRIME_EXPONENTS:
                mersenne_val = (1 << n) - 1
                smallest_factors.append((mersenne_val, n, 'Mersenne prime'))
            continue
        if v == '1':
            # n=1, M(1)=1, no prime factors
            continue
        # Regular smallest prime factor
        try:
            factor = int(v)
            smallest_factors.append((factor, n, 'factor'))
        except ValueError:
            continue
    
    # Sort by factor value
    smallest_factors.sort()
    
    # Write sorted list
    lines = []
    lines.append('# Sorted list of smallest prime factors of Mersenne numbers M(n) = 2^n - 1')
    lines.append('# For n from 2 to 12000')
    lines.append('# Format: factor_value | n | type (factor or Mersenne prime)')
    lines.append('# Sorted by factor_value ascending')
    lines.append(f'# Total entries: {len(smallest_factors)}')
    lines.append('')
    
    # Also write a comma-separated list of just the factor values (deduplicated)
    seen_factors = set()
    unique_factors = []
    for factor, n, type_ in smallest_factors:
        if factor not in seen_factors:
            seen_factors.add(factor)
            unique_factors.append(factor)
    
    lines.append(f'# Unique factor values (sorted): {len(unique_factors)}')
    lines.append('')
    lines.append('=== Full sorted list (factor_value, n, type) ===')
    for factor, n, type_ in smallest_factors:
        lines.append(f'{factor}\t{n}\t{type_}')
    
    lines.append('')
    lines.append('=== First 100 unique smallest factor values ===')
    lines.append(', '.join(str(f) for f in unique_factors[:100]))
    
    SORTED_LIST_FILE.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Sorted list written to {SORTED_LIST_FILE}', file=sys.stderr)
    print(f'  Total entries: {len(smallest_factors)}', file=sys.stderr)
    print(f'  Unique factor values: {len(unique_factors)}', file=sys.stderr)
    print(f'  First 10 unique factors: {unique_factors[:10]}', file=sys.stderr)
    
    # Generate range statistics
    stats_lines = []
    stats_lines.append('A136030 Range Statistics')
    stats_lines.append('=' * 80)
    stats_lines.append('')
    stats_lines.append('For each range [lo, hi], shows:')
    stats_lines.append('  - Total primes: count of prime numbers in range')
    stats_lines.append('  - Mersenne: count of Mersenne prime exponents in range')
    stats_lines.append('  - Need factor: total primes minus Mersenne exponents')
    stats_lines.append('  - Found: count of primes where we have a smallest factor')
    stats_lines.append('  - Missing: count of primes still marked -1')
    stats_lines.append('  - Coverage: Found / Need factor * 100')
    stats_lines.append('')
    stats_lines.append(f'{"Range":<18} {"Total primes":<14} {"Mersenne":<10} {"Need factor":<12} {"Found":<8} {"Missing":<8} {"Coverage":<10}')
    stats_lines.append('-' * 80)
    
    ranges = [(2, 100), (101, 200), (201, 500), (501, 1000), (1001, 2000),
              (2001, 3000), (3001, 5000), (5001, 8000), (8001, 12000)]
    
    total_primes = 0
    total_mersenne = 0
    total_need = 0
    total_found = 0
    
    for lo, hi in ranges:
        primes_in_range = [n for n in range(lo, hi+1) if is_prime(n)]
        total = len(primes_in_range)
        mersenne = sum(1 for n in primes_in_range if n in MERSENNE_PRIME_EXPONENTS)
        need_factor = total - mersenne
        # Count found: primes where v != -1 and v != 0 (or v == 0 for Mersenne)
        found = 0
        missing_count = 0
        for n in primes_in_range:
            # Find this n in rows
            for r_n, r_v in rows:
                if r_n == n:
                    if r_v == '-1':
                        missing_count += 1
                    elif r_v == '0':
                        # Mersenne prime - count as "found"
                        found += 1
                    else:
                        found += 1
                    break
        missing_count = need_factor - (found - mersenne)  # adjust: found includes Mersenne
        # Actually let me recalculate
        # need_factor = total - mersenne
        # found_in_range = count of primes where we have a factor (v != -1)
        # missing = need_factor - found_in_range
        # But "found" includes Mersenne primes (v == 0)
        # So: found_non_mersenne = found - mersenne (those with actual factor value)
        # missing = need_factor - found_non_mersenne
        
        found_with_factor = 0  # primes with v != -1 and v != 0 (actual factor found)
        found_mersenne = 0  # Mersenne primes (v == 0)
        missing_count = 0
        for n in primes_in_range:
            for r_n, r_v in rows:
                if r_n == n:
                    if r_v == '-1':
                        missing_count += 1
                    elif r_v == '0':
                        found_mersenne += 1
                    else:
                        found_with_factor += 1
                    break
        
        coverage = found_with_factor / need_factor * 100 if need_factor > 0 else 100
        stats_lines.append(f'[{lo}, {hi}]{"":<8} {total:<14} {mersenne:<10} {need_factor:<12} {found_with_factor:<8} {missing_count:<8} {coverage:.1f}%')
        
        total_primes += total
        total_mersenne += mersenne
        total_need += need_factor
        total_found += found_with_factor
    
    stats_lines.append('-' * 80)
    coverage_total = total_found / total_need * 100 if total_need > 0 else 100
    stats_lines.append(f'{"Total":<16} {total_primes:<14} {total_mersenne:<10} {total_need:<12} {total_found:<8} {total_need - total_found:<8} {coverage_total:.1f}%')
    
    STATS_FILE.write_text('\n'.join(stats_lines) + '\n', encoding='utf-8')
    print(f'Statistics written to {STATS_FILE}', file=sys.stderr)


if __name__ == '__main__':
    main()
