#!/usr/bin/env python3
"""
Update A136030_factors_1_to_8000.txt with new factors from factordb.
"""
import urllib.request
import urllib.parse
import re
import json
import time
from pathlib import Path

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
LOG = BASE / 'logs/factordb_update.log'

# Load results from previous run
with open(BASE / 'logs/factordb_new_factors.json', 'r') as f:
    new_factors = json.load(f)

print(f"Loaded {len(new_factors)} Mersennes with new factor info from factordb")

def query_factor_value(factor_id):
    """Query factordb for a specific factor ID to get the full value."""
    url = f"http://factordb.com/index.php?id={factor_id}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
        # The full value appears as input value in some pages, or in <font color="#002099">NUMBER</font>
        # Try several patterns
        # Pattern 1: input value
        m = re.search(r'name="query"\s+value="(\d+)"', html)
        if m:
            return m.group(1)
        # Pattern 2: in result table
        m = re.search(r'<font color="#\w+">(\d+)</font><sub>', html)
        if m:
            return m.group(1)
        # Pattern 3: just <font color="#\w+">digits</font>
        tables = re.findall(r'<table border=0 width="98%">(.*?)</table>', html, re.DOTALL)
        for t in tables:
            if 'Result' in t:
                m = re.search(r'<font color="#\w+">(\d+)</font>', t)
                if m:
                    return m.group(1)
        return None
    except Exception as e:
        return None

# For each M(p), get the smallest factor's full value
print("Fetching smallest factor for each newly-discovered Mersenne...")
results = []
t_start = time.time()
for p, parsed in new_factors:
    if time.time() - t_start > 100:
        print(f"  Time budget exceeded at p={p}")
        break
    factors = parsed['factors']
    if not factors:
        continue
    # Find the smallest factor (by digit count, then by value)
    # Skip the factor that's the full M(p) itself (its digit count matches parsed['digits'])
    smallest = None
    smallest_id = None
    for fid, fdisp, fdig in factors:
        fdig_int = int(fdig)
        # The full M(p) has many digits; we want a factor that's not the full number
        # Actually any factor in the list is a prime factor (or the unfactored composite cofactor)
        # We want the smallest PRIME factor.
        # If status is FF, all factors are prime.
        # If status is CF, the factors include both primes and one large composite (the "C" cofactor).
        # The largest factor in the list is usually the composite cofactor (when status is CF).
        # The smallest factor is what we want.
        if smallest is None or fdig_int < smallest:
            smallest = fdig_int
            smallest_id = fid
            smallest_disp = fdisp
    
    if smallest_id is None:
        continue
    
    # Fetch the full value
    val = query_factor_value(smallest_id)
    if val:
        # Verify it's the smallest by checking length
        if len(val) == smallest:
            results.append((p, int(val), parsed['status'], len(factors)))
            print(f"  M({p}): smallest factor = {val[:50]}... ({smallest} digits), status={parsed['status']}")
    time.sleep(0.3)

print()
print(f"Got smallest factors for {len(results)} Mersennes")

# Update A136030_factors_1_to_8000.txt
print()
print("Updating factors table...")
lines = FACTORS_FILE.read_text().splitlines(keepends=True)
updates = {p: val for p, val, _, _ in results}
out = []
updated_count = 0
for line in lines:
    if line.startswith('#'):
        out.append(line)
        continue
    parts = line.split('\t')
    if len(parts) >= 2:
        p_val = int(parts[0])
        f_val = parts[1].strip()
        if p_val in updates and (f_val == '-1' or int(updates[p_val]) < int(f_val)):
            out.append(f'{p_val}\t{updates[p_val]}\n')
            updated_count += 1
        else:
            out.append(line)
    else:
        out.append(line)

FACTORS_FILE.write_text(''.join(out), encoding='utf-8')
print(f"  Updated {updated_count} entries in factors table")

# Save results
with open(BASE / 'logs/factordb_smallest_factors.json', 'w') as f:
    json.dump(results, f, indent=2)

print()
print(f"Total time: {time.time() - t_start:.1f}s")
print(f"Total entries updated: {updated_count}")
PYEOF
