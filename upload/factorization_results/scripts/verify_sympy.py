#!/usr/bin/env python3.12
"""Independent verification of FULL results using sympy (different implementation than gmpy2)."""
import json
from sympy import isprime, Integer

rows = json.load(open("/home/z/my-project/work/factor/verify_rows.json"))
bad = 0
for rid, ndigits, k, factor, _ in rows:
    if not isprime(Integer(factor)):
        bad += 1
        print(f"NOT PRIME (sympy): {rid} factor ...{factor[-12:]}")
print(f"sympy cross-check: {len(rows)} prime factors verified, {bad} failures")

# also verify counts per full entry
from collections import Counter
c = Counter(r[0] for r in rows)
for rid, cnt in c.items():
    k = rows[[r[0] for r in rows].index(rid)][2]
    if cnt != k:
        print(f"COUNT MISMATCH {rid}: {cnt} != {k}")
print("count check done")
