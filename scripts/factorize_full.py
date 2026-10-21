#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full factorization of Mersenne numbers M(p) = 2^p - 1
for the first 191 entries of A136030.

Uses:
1. Cunningham table (for p < 1500) - has full factorizations
2. GIMPS factors (smallest factor) + sympy for complete factorization of cofactor
3. Online check via factordb if needed

Output: A136030_first_191_full_factorizations.txt
"""

import sys
import re
import json
import urllib.request
from sympy import primerange, factorint
from gmpy2 import is_prime as gmpy_is_prime, mpz

MERSENNE_PRIME_EXPONENTS = {2,3,5,7,13,17,19,31,61,89,107,127,521,607,1279,2203,2281,3217,4253,4423}

# Load A136030
seq = {}
with open('/home/z/my-project/download/A136030_1_to_8000.txt') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) == 2:
            seq[int(parts[0])] = int(parts[1])

all_primes = list(primerange(2, 100000))
candidate_primes = [p for p in all_primes if p not in MERSENNE_PRIME_EXPONENTS]
target_primes = candidate_primes[:8000]

# Parse Cunningham table
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
    current_text = ""
    
    for line in table_lines:
        if 'Table 2' in line or 'Prime Factors' in line:
            continue
        if not line.strip():
            if current_n is not None:
                factors_by_n[current_n] = current_text
                current_n = None
                current_text = ""
            continue
        
        m = re.match(r'^\s+(\d+)\s+(.*)$', line)
        if m:
            if current_n is not None:
                factors_by_n[current_n] = current_text
            current_n = int(m.group(1))
            current_text = m.group(2).strip()
        else:
            stripped = line.strip()
            if stripped and current_n is not None:
                if stripped[0] not in '1234567890.':
                    continue
                current_text += " " + stripped
    
    if current_n is not None:
        factors_by_n[current_n] = current_text
    
    return factors_by_n

print("Loading Cunningham table...", file=sys.stderr)
cunningham = parse_cunningham('/tmp/cun_pmain126.txt')
print(f"  {len(cunningham)} entries", file=sys.stderr)

def format_factorization(factors_dict):
    """Format a factorization dict as 'p1^e1 * p2^e2 * ...'."""
    parts = []
    for f in sorted(factors_dict.keys()):
        e = factors_dict[f]
        if e == 1:
            parts.append(str(f))
        else:
            parts.append("{}^{}".format(f, e))
    return " * ".join(parts)

def factorize_with_cunningham(p):
    """Get full factorization from Cunningham table."""
    if p not in cunningham:
        return None
    
    text = cunningham[p]
    # Remove parens (these refer to factors of M(d) for d|n, which are already accounted for in prime p)
    # For prime p, there should be no parens
    no_parens = re.sub(r'\([^)]*\)', '', text)
    
    # Parse factors
    factors = {}
    parts = no_parens.replace('*', ' ').replace('.', ' ').split()
    for part in parts:
        part = part.rstrip('*')
        if part.isdigit():
            f = int(part)
            factors[f] = factors.get(f, 0) + 1
        elif part.startswith('P') and part[1:].isdigit():
            # Unknown prime of that many digits
            return None  # Can't get full factorization
        elif part.startswith('C') and part[1:].isdigit():
            # Composite - unknown
            return None
    
    return factors

def factorize_with_sympy(M, smallest_factor, time_limit_seconds=10):
    """Use sympy to fully factorize M given the smallest factor."""
    import signal
    
    def handler(signum, frame):
        raise TimeoutError("Timed out")
    
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(time_limit_seconds)
    
    try:
        # Start with the known smallest factor
        factors = {}
        q = M
        # Divide by smallest_factor
        while q % smallest_factor == 0:
            factors[smallest_factor] = factors.get(smallest_factor, 0) + 1
            q //= smallest_factor
        
        # Use sympy to factorize the cofactor
        if q > 1:
            cofactor_factors = factorint(q)
            for f, e in cofactor_factors.items():
                factors[f] = factors.get(f, 0) + e
        
        signal.alarm(0)
        return factors
    except TimeoutError:
        signal.alarm(0)
        return None
    except Exception as e:
        signal.alarm(0)
        return None

def factorize_with_factordb(p):
    """Query factordb for full factorization."""
    try:
        num = (1 << p) - 1
        url = "http://factordb.com/api?query={}".format(num)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            import json as j
            data = j.loads(resp.read().decode('utf-8', errors='ignore'))
        
        status = data.get('status')
        factors_list = data.get('factors', [])
        
        if status in ('FF', 'CF') and factors_list:
            factors = {}
            for f_str, e in factors_list:
                if f_str.isdigit():
                    f = int(f_str)
                    factors[f] = factors.get(f, 0) + e
            if status == 'FF':
                return factors
            else:
                return factors  # Partial - but at least what we have
        return None
    except Exception as e:
        return None

# Process first 191 entries
output_lines = []
stats = {'cunningham': 0, 'sympy': 0, 'factordb': 0, 'failed': 0, 'partial': 0}

for idx in range(1, 192):
    p = target_primes[idx-1]
    smallest = seq[idx]
    M = (1 << p) - 1
    
    factors = None
    source = ""
    
    # Method 1: Cunningham table (fastest, most accurate)
    if p < 1500:
        factors = factorize_with_cunningham(p)
        if factors:
            source = "Cunningham"
            stats['cunningham'] += 1
    
    # Method 2: factordb (online)
    if not factors:
        factors = factorize_with_factordb(p)
        if factors:
            # Verify
            product = 1
            for f, e in factors.items():
                product *= f**e
            if product == M:
                source = "factordb"
                stats['factordb'] += 1
            else:
                # Partial factorization
                source = "factordb (partial)"
                stats['partial'] += 1
                factors = None  # Don't use partial
    
    # Method 3: sympy with smallest factor
    if not factors and smallest > 0:
        factors = factorize_with_sympy(M, smallest, time_limit_seconds=15)
        if factors:
            # Verify
            product = 1
            for f, e in factors.items():
                product *= f**e
            if product == M:
                source = "sympy"
                stats['sympy'] += 1
            else:
                factors = None
    
    if factors:
        factor_str = format_factorization(factors)
        line = "[{}] M({}) = {}".format(idx, p, factor_str)
    else:
        # Just show smallest
        if smallest > 0:
            cofactor = M // smallest
            if gmpy_is_prime(cofactor):
                line = "[{}] M({}) = {} * {} (هر دو اول)".format(idx, p, smallest, cofactor)
            else:
                line = "[{}] M({}) = {} * C{} (تجزیه کامل موجود نیست)".format(
                    idx, p, smallest, len(str(cofactor)))
        else:
            line = "[{}] M({}) = عامل پیدا نشد".format(idx, p)
        stats['failed'] += 1
    
    print(line, flush=True)
    output_lines.append((idx, line, source))

# Save to file with sources
with open('/home/z/my-project/download/A136030_first_191_full_factorizations.txt', 'w', encoding='utf-8') as f:
    f.write("تجزیه کامل اعداد مرسن M(p) = 2^p - 1\n")
    f.write("برای 191 ورودی اول دنباله A136030\n")
    f.write("=" * 70 + "\n\n")
    for idx, line, source in output_lines:
        f.write(line + "\n")
    f.write("\n" + "=" * 70 + "\n")
    f.write("آمار:\n")
    f.write("  Cunningham: {}\n".format(stats['cunningham']))
    f.write("  factordb: {}\n".format(stats['factordb']))
    f.write("  sympy: {}\n".format(stats['sympy']))
    f.write("  partial: {}\n".format(stats['partial']))
    f.write("  failed (فقط عامل کوچک‌ترین): {}\n".format(stats['failed']))

print("\n" + "=" * 70, file=sys.stderr)
print("آمار:", file=sys.stderr)
for k, v in stats.items():
    print("  {}: {}".format(k, v), file=sys.stderr)
print("ذخیره شد در: A136030_first_191_full_factorizations.txt", file=sys.stderr)
