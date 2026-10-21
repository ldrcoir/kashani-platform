#!/usr/bin/env python3
"""
Parse Cunningham table for 2^n-1 factorizations and compute A136030 sequence.

A136030: smallest prime factor of M(p) = 2^p - 1 for prime p, 
excluding Mersenne prime exponents (where M(p) is itself prime).
Indexed sequentially by prime p (skipping Mersenne prime exponents).
"""

import sys
import re
import sympy
from sympy import isprime

MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607,
    1279, 2203, 2281, 3217, 4253, 4423
}

def parse_cunningham_table(filename):
    """Parse the Cunningham Table 2- for factorizations of 2^n-1, n odd."""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Find Table 2- (lines 1-752 based on inspection)
    # Find first "Table 2-" line and stop at next "Table 2"
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if 'Table 2-' in line:
            start_idx = i
        elif start_idx is not None and 'Table 2' in line:
            end_idx = i
            break
    if end_idx is None:
        end_idx = len(lines)
    
    table_lines = lines[start_idx:end_idx]
    
    # Parse each entry: "  n   factors" possibly multi-line
    # Format: lines starting with spaces, then n, then factors
    # Multi-line entries have continuation lines starting with more spaces
    
    # Strategy: scan for lines starting with "  <digits>" - these are new entries
    # Continuation lines start with whitespace only (no digit at start of trimmed content)
    # OR with "." for continued multiplication
    
    factors_by_n = {}
    current_n = None
    current_factors_text = ""
    
    for line in table_lines:
        # Skip header lines
        if 'Table 2' in line or 'Prime Factors' in line or 'n ' in line and 'n<' in line:
            continue
        if not line.strip():
            if current_n is not None:
                factors_by_n[current_n] = current_factors_text
                current_n = None
                current_factors_text = ""
            continue
        
        # Check if this is a new entry (starts with optional spaces, then digits, then more spaces, then content)
        m = re.match(r'^\s+(\d+)\s+(.*)$', line)
        if m:
            # New entry
            if current_n is not None:
                factors_by_n[current_n] = current_factors_text
            current_n = int(m.group(1))
            current_factors_text = m.group(2).strip()
        else:
            # Continuation line - check if it's a real continuation
            stripped = line.strip()
            if stripped and (stripped.startswith('.') or stripped.startswith('L') or 
                             stripped.startswith('M') or stripped[0].isdigit() or
                             re.match(r'^[0-9LMP\.]', stripped)):
                # Continuation
                if current_n is not None:
                    current_factors_text += " " + stripped
    
    if current_n is not None:
        factors_by_n[current_n] = current_factors_text
    
    return factors_by_n

def extract_smallest_prime_factor(n, factor_text):
    """Extract smallest prime factor from Cunningham factor text.
    Format examples:
      '23.89' -> 23
      '(3,5) 151' -> 3 (3 is in parens, but it's a known factor from M(3))
      '47.178481' -> 47
      '(3,7) 7*.337' -> 3
      '(7) 4432676798593' -> 7 (M(7)=127, so factor 7 doesn't divide M(n) directly... wait)
      
    Actually the (p,q,r) notation means factors of M(d) for d|n where d = p, q, r.
    So if (3) is in the entry for n, that means M(3) = 7 divides M(n) (since 3|n).
    So the smallest prime factor of M(n) when (3) is shown is 7, not 3.
    
    Hmm, that's not right either. Let me re-read Cunningham notation.
    
    Cunningham notation: 
    - "(3)" in the entry for n means M(3) divides M(n), i.e., 7 divides M(n).
    - "(3,5)" means M(3)=7 and M(5)=31 both divide M(n).
    - Numbers outside parens are NEW prime factors not coming from smaller M(d).
    
    So smallest prime factor of M(n) = min over all prime factors of M(d) for d|n.
    If n has small prime divisor like 3, then 7 divides M(n).
    """
    # Get prime factorization of n to know which M(d) divide M(n)
    # Actually for the sequence A136030, we only care about prime p (not composite n).
    # For prime p, the only divisors are 1 and p itself.
    # M(1) = 1, doesn't divide anything in a useful way.
    # So for prime p, M(p) has factors not coming from smaller M(d) (except for trivial cases).
    
    # So for prime p, the factor text should NOT have parentheses (since p has no proper divisors
    # other than 1). Let me verify.
    
    # If p is prime and the entry has parens, that's strange. Let me just parse the numbers
    # outside parens.
    
    # Find numbers outside parens
    # Strategy: remove parenthesized parts, then split by .
    no_parens = re.sub(r'\([^)]*\)', '', factor_text)
    # Remove L and M (these are aurifeuillean factors, only appear for n with special form)
    # For prime n, there should be no L/M
    
    # Split by . and extract numbers
    parts = no_parens.replace('*', ' ').replace('.', ' ').split()
    primes = []
    for part in parts:
        # Strip any trailing characters like * 
        part = part.rstrip('*')
        if part.isdigit():
            primes.append(int(part))
        elif part.startswith('P') and part[1:].isdigit():
            # P followed by digits means an unknown prime of that many digits
            # We can't use this - the factor is unknown
            pass
        elif part.startswith('C') and part[1:].isdigit():
            # Composite - unknown
            pass
    
    if primes:
        return min(primes)
    return None

# Parse the table
print("Parsing Cunningham table...", file=sys.stderr)
factors_by_n = parse_cunningham_table('/tmp/cun_pmain.txt')
print(f"  Parsed {len(factors_by_n)} entries.", file=sys.stderr)

# Show sample
print("\nSample factorizations for prime n:", file=sys.stderr)
for n in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103]:
    if n in factors_by_n:
        print(f"  M({n}): {factors_by_n[n]}", file=sys.stderr)

# Get primes up to 1200 (coverage of Cunningham table)
primes_up_to_1200 = [p for p in sympy.primerange(2, 1200)]
print(f"\nPrimes up to 1200: {len(primes_up_to_1200)}", file=sys.stderr)

# Build A136030 sequence
sequence = []
for p in primes_up_to_1200:
    if p in MERSENNE_PRIME_EXPONENTS:
        continue  # Skip Mersenne prime exponents
    if p in factors_by_n:
        spf = extract_smallest_prime_factor(p, factors_by_n[p])
        if spf:
            sequence.append((p, spf))
        else:
            sequence.append((p, None))
    else:
        sequence.append((p, None))

print(f"\nA136030 sequence (prime exponent, smallest factor):", file=sys.stderr)
print(f"  Total entries (composite Mersenne exponents up to 1200): {len(sequence)}", file=sys.stderr)
print(f"  With known factor: {sum(1 for _, v in sequence if v is not None)}", file=sys.stderr)
print(f"  Unknown: {sum(1 for _, v in sequence if v is None)}", file=sys.stderr)

# Compare with OEIS data
oeis_data = {}
with open('/tmp/b136030.txt') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            oeis_data[int(parts[0])] = int(parts[1])

print(f"\nOEIS has {len(oeis_data)} entries", file=sys.stderr)

# Verify our sequence matches OEIS
print("\nFirst 30 entries comparison:", file=sys.stderr)
matches = 0
mismatches = 0
for i, (p, spf) in enumerate(sequence[:30], 1):
    oeis_val = oeis_data.get(i)
    status = ""
    if oeis_val is not None:
        if spf == oeis_val:
            matches += 1
            status = "OK"
        else:
            mismatches += 1
            status = f"MISMATCH (oeis={oeis_val})"
    print(f"  [{i}] p={p}, smallest factor={spf} {status}", file=sys.stderr)

# Full comparison
print(f"\nFull comparison with OEIS:", file=sys.stderr)
all_match = True
for i, (p, spf) in enumerate(sequence, 1):
    oeis_val = oeis_data.get(i)
    if oeis_val is not None and spf != oeis_val:
        print(f"  MISMATCH at index {i}: p={p}, ours={spf}, oeis={oeis_val}", file=sys.stderr)
        all_match = False

if all_match:
    print(f"  All {len(oeis_data)} OEIS entries match!", file=sys.stderr)
