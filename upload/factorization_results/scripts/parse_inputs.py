#!/usr/bin/env python3.13
"""Parse the 4 factorization challenge files, verify counts/sizes, run structural quick-checks."""
import json, re, itertools, sys
from gmpy2 import mpz, is_power, gcd

UP = "/home/z/my-project/upload"
FILES = [
    ("001", "quad",   "prompt_001_quad_factor.txt",       4),
    ("002", "penta",  "prompt_002_penta_composite.txt",   5),
    ("003", "triple", "prompt_003_triple_composite.txt",  3),
    ("004", "hexa",   "prompt_004_hexa_composite.txt",    6),
]

data = {}
for fid, name, fname, k in FILES:
    nums = []
    with open(f"{UP}/{fname}") as f:
        for line in f:
            m = re.match(r"\s*n=(\d+)\s*$", line)
            if m:
                nums.append(mpz(m.group(1)))
    data[fid] = {"name": name, "k": k, "file": fname, "numbers": nums}
    digits = [len(str(n)) for n in nums]
    print(f"[{fid} {name}] expected={k}-primes  count={len(nums)}  "
          f"digits min={min(digits)} max={max(digits)} avg={sum(digits)/len(digits):.1f}")
    pp = [i for i, n in enumerate(nums) if is_power(n)]
    if pp: print(f"   !! perfect powers at idx {pp}")

# cross-number GCD check (shared prime pool?)
print("\nCross-number GCD matrix:")
pairs_found = 0
all_ids = [(fid, i) for fid in data for i in range(len(data[fid]["numbers"]))]
for (f1, i), (f2, j) in itertools.combinations(all_ids, 2):
    n1, n2 = data[f1]["numbers"][i], data[f2]["numbers"][j]
    if n1 == n2:
        print(f"  DUPLICATE: {f1}[{i}] == {f2}[{j}]"); pairs_found += 1; continue
    g = gcd(n1, n2)
    if g != 1:
        print(f"  SHARED FACTOR gcd={g} ({f1}[{i}] & {f2}[{j}])")
        pairs_found += 1
if pairs_found == 0:
    print("  none — no shared factors or duplicates across all 125 numbers")

# save canonical JSON (decimal strings)
out = {fid: {"name": d["name"], "k": d["k"], "file": d["file"],
             "numbers": [str(n) for n in d["numbers"]]} for fid, d in data.items()}
with open("/home/z/my-project/work/numbers.json", "w") as f:
    json.dump(out, f, indent=1)
print("\nSaved work/numbers.json")
