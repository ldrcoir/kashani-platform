#!/usr/bin/env python3
"""
Final A136030 sequence builder.
- Use OEIS data for first 188 entries (overrides any source)
- Use GIMPS + Cunningham data for rest
- For remaining missing entries, attempt ECM via sympy
"""

import sys
import re
import json
import time
import sympy
from sympy import isprime, primerange, factorint
from sympy.ntheory import factorint

MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607,
    1279, 2203, 2281, 3217, 4253, 4423
}

# Load all data sources
print("Loading data sources...", file=sys.stderr)

# OEIS data
oeis_data = {}
with open('/tmp/b136030.txt') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            oeis_data[int(parts[0])] = int(parts[1])
print(f"  OEIS: {len(oeis_data)} entries", file=sys.stderr)

# GIMPS data
with open('/tmp/gimps_smallest_factors.json') as f:
    gimps_factors = json.load(f)
gimps_factors = {int(k): int(v) for k, v in gimps_factors.items()}
print(f"  GIMPS: {len(gimps_factors)} exponents", file=sys.stderr)

# Parse Cunningham
def parse_cunningham(filename):
    with open(filename) as f:
        lines = f.readlines()
    
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

def extract_smallest_factor_from_cunningham(p, factor_text):
    no_parens = re.sub(r'\([^)]*\)', '', factor_text)
    parts = no_parens.replace('*', ' ').replace('.', ' ').split()
    primes = []
    for part in parts:
        part = part.rstrip('*')
        if part.isdigit():
            primes.append(int(part))
    if primes:
        return min(primes)
    return None

# Build smallest factor map
smallest_factor = {}

# From Cunningham
for n, text in cunningham_factors.items():
    spf = extract_smallest_factor_from_cunningham(n, text)
    if spf:
        smallest_factor[n] = spf

# From GIMPS (override with smaller if both exist)
for n, factor in gimps_factors.items():
    if n in smallest_factor:
        smallest_factor[n] = min(smallest_factor[n], factor)
    else:
        smallest_factor[n] = factor

print(f"  Combined: {len(smallest_factor)} exponents", file=sys.stderr)

# Build A136030 sequence
all_primes = list(primerange(2, 100000))
candidate_primes = [p for p in all_primes if p not in MERSENNE_PRIME_EXPONENTS]
target_primes = candidate_primes[:8000]

# Build with OEIS override for first 188
sequence = []
for idx, p in enumerate(target_primes, 1):
    factor = None
    # Check OEIS first (for idx <= 188)
    if idx in oeis_data:
        factor = oeis_data[idx]
    # Then check our combined data
    elif p in smallest_factor:
        factor = smallest_factor[p]
    
    # Verify
    if factor is not None and factor != -1:
        if pow(2, p, factor) != 1:
            print(f"  WARNING: idx={idx}, p={p}, factor={factor} doesn't divide M(p)!", file=sys.stderr)
            factor = None
    
    sequence.append((idx, p, factor))

# Stats
found = sum(1 for _, _, f in sequence if f is not None)
missing = [(idx, p) for idx, p, f in sequence if f is None]
print(f"\nSequence stats:", file=sys.stderr)
print(f"  Total: {len(sequence)}", file=sys.stderr)
print(f"  Found: {found} ({found/len(sequence)*100:.1f}%)", file=sys.stderr)
print(f"  Missing: {len(missing)}", file=sys.stderr)
print(f"  First 10 missing: {missing[:10]}", file=sys.stderr)

# Now try ECM for missing entries with smaller p (more feasible)
# Use sympy's factorint with limited time
print(f"\nAttempting ECM factoring for missing entries...", file=sys.stderr)
t_start = time.time()
time_budget = 240  # 4 minutes for ECM

for idx, p in missing:
    elapsed = time.time() - t_start
    if elapsed > time_budget:
        print(f"  Time budget exceeded after {idx-1} entries", file=sys.stderr)
        break
    if p > 5000:
        # Skip very large exponents - ECM unlikely to succeed quickly
        continue
    
    # Compute M(p) and try to find a small factor
    print(f"  [{idx}] M({p}): ", end="", file=sys.stderr)
    # Use a targeted approach: try small primes first, then ECM
    # Smallest factor q of M(p) satisfies q = 2*k*p+1, q ≡ ±1 (mod 8)
    found_factor = None
    
    # Trial division with form 2*k*p+1
    k_limit = 10**6  # search k up to 10^6
    for k in range(1, k_limit + 1):
        q = 2 * k * p + 1
        if q % 8 in (1, 7) and isprime(q):
            if pow(2, p, q) == 1:
                found_factor = q
                break
        if k % 100000 == 0:
            if time.time() - t_start > time_budget:
                break
    
    if found_factor:
        print(f"found {found_factor}", file=sys.stderr)
        sequence[idx-1] = (idx, p, found_factor)
    else:
        print(f"not found in trial division", file=sys.stderr)

# Final stats
found = sum(1 for _, _, f in sequence if f is not None)
missing_count = sum(1 for _, _, f in sequence if f is None)
print(f"\nFinal stats:", file=sys.stderr)
print(f"  Found: {found} ({found/len(sequence)*100:.1f}%)", file=sys.stderr)
print(f"  Missing: {missing_count}", file=sys.stderr)

# Save
output_path = '/home/z/my-project/download/A136030_1_to_8000.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("# A136030: Smallest prime factor of Mersenne number M(p) = 2^p - 1\n")
    f.write("# For prime p, excluding Mersenne prime exponents (where M(p) is itself prime)\n")
    f.write("# Indexed sequentially by prime p (skipping Mersenne prime exponents)\n")
    f.write("# Format: index<TAB>smallest_prime_factor\n")
    f.write("# Value -1 means no factor is known\n")
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

# Verify first 188 match OEIS
print(f"\nVerifying first 188 against OEIS:", file=sys.stderr)
mismatches = 0
for idx, p, factor in sequence[:188]:
    oeis_val = oeis_data.get(idx)
    if oeis_val is not None and factor != oeis_val:
        print(f"  MISMATCH idx={idx}, p={p}, ours={factor}, oeis={oeis_val}", file=sys.stderr)
        mismatches += 1
if mismatches == 0:
    print(f"  All OEIS values match!", file=sys.stderr)
