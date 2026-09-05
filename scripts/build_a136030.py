#!/usr/bin/env python3
"""
Build A136030 sequence (smallest prime factor of M(p) = 2^p - 1 for prime p,
excluding Mersenne prime exponents) from index 1 to 8000.

Data sources:
1. OEIS b-file (188 known values)
2. GIMPS factors database (fetched from mersenne.org)
3. Cunningham table (parse from /tmp/cun_pmain126.txt)
4. Direct computation via ECM for missing entries (when feasible)

For each prime p (excluding Mersenne prime exponents):
- Find smallest prime factor of M(p)
- Use the smallest known factor from any source
- If no factor is known and ECM can't find one, mark as -1
"""

import sys
import re
import json
import sympy
from sympy import isprime, primerange

MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607,
    1279, 2203, 2281, 3217, 4253, 4423
}

# Load GIMPS data
print("Loading GIMPS factors data...", file=sys.stderr)
with open('/tmp/gimps_smallest_factors.json') as f:
    gimps_factors = json.load(f)
gimps_factors = {int(k): int(v) for k, v in gimps_factors.items()}
print(f"  GIMPS: {len(gimps_factors)} exponents", file=sys.stderr)

# Load OEIS data
print("Loading OEIS data...", file=sys.stderr)
oeis_data = {}
with open('/tmp/b136030.txt') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            oeis_data[int(parts[0])] = int(parts[1])
print(f"  OEIS: {len(oeis_data)} entries", file=sys.stderr)

# Parse Cunningham table for additional factors
print("Parsing Cunningham table...", file=sys.stderr)

def parse_cunningham(filename):
    with open(filename) as f:
        lines = f.readlines()
    
    # Find Table 2-
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if 'Table 2-' in line:
            start_idx = i
        elif start_idx is not None and 'Table 2' in line and i > start_idx:
            end_idx = i
            break
    if end_idx is None:
        end_idx = len(lines)
    
    table_lines = lines[start_idx:end_idx]
    
    factors_by_n = {}
    current_n = None
    current_factors_text = ""
    
    for line in table_lines:
        if 'Table 2' in line or 'Prime Factors' in line:
            continue
        if not line.strip():
            if current_n is not None:
                factors_by_n[current_n] = current_factors_text
                current_n = None
                current_factors_text = ""
            continue
        
        m = re.match(r'^\s+(\d+)\s+(.*)$', line)
        if m:
            if current_n is not None:
                factors_by_n[current_n] = current_factors_text
            current_n = int(m.group(1))
            current_factors_text = m.group(2).strip()
        else:
            stripped = line.strip()
            if stripped and current_n is not None:
                if stripped[0] not in '1234567890.':
                    continue
                current_factors_text += " " + stripped
    
    if current_n is not None:
        factors_by_n[current_n] = current_factors_text
    
    return factors_by_n

cunningham_factors = parse_cunningham('/tmp/cun_pmain126.txt')
print(f"  Cunningham: {len(cunningham_factors)} entries", file=sys.stderr)

def extract_smallest_factor_from_cunningham(p, factor_text):
    """For prime p, extract smallest prime factor from Cunningham text."""
    no_parens = re.sub(r'\([^)]*\)', '', factor_text)
    parts = no_parens.replace('*', ' ').replace('.', ' ').split()
    primes = []
    for part in parts:
        part = part.rstrip('*')
        if part.isdigit():
            primes.append(int(part))
        # Skip P<n> and C<n> (unknown prime/composite of n digits)
    if primes:
        return min(primes)
    return None

# Build smallest factor map combining all sources
smallest_factor = {}

# Add from Cunningham
for n, text in cunningham_factors.items():
    spf = extract_smallest_factor_from_cunningham(n, text)
    if spf:
        smallest_factor[n] = spf

# Override/add with GIMPS (more complete)
for n, factor in gimps_factors.items():
    if n in smallest_factor:
        smallest_factor[n] = min(smallest_factor[n], factor)
    else:
        smallest_factor[n] = factor

print(f"Combined: {len(smallest_factor)} exponents with known smallest factor", file=sys.stderr)

# Now build the A136030 sequence
# Need: primes p (excluding Mersenne prime exponents) in increasing order
# For each, get smallest factor of M(p)
# Need 8000 entries

print("\nBuilding A136030 sequence...", file=sys.stderr)

# Get primes incrementally - we need 8000 + (Mersenne primes in range) total primes
# Conservative: 8050 primes, then filter out Mersenne prime exponents
# 8050th prime is approximately 82500

# Generate primes up to 100000 to be safe
all_primes = list(primerange(2, 100000))
print(f"  Generated {len(all_primes)} primes up to 100000", file=sys.stderr)

# Filter: exclude Mersenne prime exponents
candidate_primes = [p for p in all_primes if p not in MERSENNE_PRIME_EXPONENTS]
print(f"  After excluding Mersenne prime exponents: {len(candidate_primes)} primes", file=sys.stderr)

# Take first 8000
target_primes = candidate_primes[:8000]
print(f"  Using first 8000: primes from {target_primes[0]} to {target_primes[-1]}", file=sys.stderr)

# Build sequence
sequence = []
missing = []
for idx, p in enumerate(target_primes, 1):
    if p in smallest_factor:
        # Verify the factor is actually a factor of M(p)
        factor = smallest_factor[p]
        # Quick check: factor should divide 2^p - 1, i.e., 2^p ≡ 1 (mod factor)
        if pow(2, p, factor) == 1:
            sequence.append((idx, p, factor))
        else:
            # This shouldn't happen but just in case
            sequence.append((idx, p, None))
            missing.append((idx, p))
    else:
        sequence.append((idx, p, None))
        missing.append((idx, p))

print(f"\nSequence built:", file=sys.stderr)
print(f"  Total entries: {len(sequence)}", file=sys.stderr)
print(f"  With factor: {sum(1 for _, _, f in sequence if f is not None)}", file=sys.stderr)
print(f"  Missing: {len(missing)}", file=sys.stderr)
if missing:
    print(f"  First 10 missing (idx, p): {missing[:10]}", file=sys.stderr)

# Verify first 188 entries match OEIS
print(f"\nVerifying against OEIS (first 188 entries):", file=sys.stderr)
mismatches = 0
for idx, p, factor in sequence[:188]:
    oeis_val = oeis_data.get(idx)
    if oeis_val is not None:
        if factor != oeis_val:
            print(f"  MISMATCH idx={idx}, p={p}, ours={factor}, oeis={oeis_val}", file=sys.stderr)
            mismatches += 1
if mismatches == 0:
    print(f"  All OEIS values match!", file=sys.stderr)
else:
    print(f"  {mismatches} mismatches found", file=sys.stderr)

# Save final output
output_path = '/home/z/my-project/download/A136030_1_to_8000.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("# A136030: Smallest prime factor of Mersenne number M(p) = 2^p - 1\n")
    f.write("# For prime p, excluding Mersenne prime exponents (where M(p) is itself prime)\n")
    f.write("# Indexed sequentially by prime p (skipping Mersenne prime exponents)\n")
    f.write("# Format: index<TAB>smallest_prime_factor\n")
    f.write("# Value -1 means no factor is known in our sources (GIMPS, Cunningham, OEIS)\n")
    for idx, p, factor in sequence:
        if factor is None:
            f.write(f"{idx}\t-1\n")
        else:
            f.write(f"{idx}\t{factor}\n")

print(f"\nWritten to {output_path}", file=sys.stderr)
print(f"\nFirst 30 entries:", file=sys.stderr)
for idx, p, factor in sequence[:30]:
    print(f"  [{idx}] M({p}): {factor}", file=sys.stderr)
print(f"\nLast 5 entries:", file=sys.stderr)
for idx, p, factor in sequence[-5:]:
    print(f"  [{idx}] M({p}): {factor}", file=sys.stderr)
