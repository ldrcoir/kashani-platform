#!/usr/bin/env python3.13
"""Build result files (exact requested format), status report, and verify."""
import json, csv, os
from gmpy2 import mpz, is_prime

WORK = "/home/z/my-project/work/factor"
OUT = "/home/z/my-project/download/factorization_results"
os.makedirs(OUT, exist_ok=True)

with open("/home/z/my-project/work/numbers.json") as f:
    RAW = json.load(f)
st = json.load(open(f"{WORK}/state.json"))

GROUPS = [("001", "quad", 4), ("002", "penta", 5), ("003", "triple", 3), ("004", "hexa", 6)]

def state_entry(fid, i):
    return st.get(f"{fid}:{i}", {"factors": []})["factors"]

def prod(flist):
    r = mpz(1)
    for f in flist:
        r *= mpz(f)
    return r

summary = []
verify_rows = []
for fid, name, k in GROUPS:
    lines = []
    n_full = n_partial = n_none = 0
    for i, s in enumerate(RAW[fid]["numbers"]):
        n = mpz(s)
        fl = state_entry(fid, i)
        fl_unique = sorted(set(fl), key=lambda x: mpz(x))
        full = bool(fl) and all(is_prime(mpz(f)) for f in fl_unique) and prod(fl_unique) == n
        if full:
            n_full += 1
            lines.append(f"n={s}")
            lines.append("factors=" + ",".join(fl_unique))
            lines.append("---")
            for f in fl_unique:
                verify_rows.append((f"{fid}:{i}", len(s), k, f, is_prime(mpz(f))))
        elif fl:
            n_partial += 1
        else:
            n_none += 1
    with open(f"{OUT}/results_{fid}_{name}.txt", "w") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))
    summary.append((fid, name, k, len(RAW[fid]["numbers"]), n_full, n_partial, n_none))

# status CSV for every number
with open(f"{OUT}/all_status.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "group", "digits", "expected_prime_factors",
                "status", "found_factors_count", "found_factors",
                "all_prime_so_far", "product_matches"])
    for fid, name, k in GROUPS:
        for i, s in enumerate(RAW[fid]["numbers"]):
            n = mpz(s)
            fl = sorted(set(state_entry(fid, i)), key=lambda x: mpz(x))
            full = bool(fl) and all(is_prime(mpz(f)) for f in fl) and prod(fl) == n
            status = "full" if full else ("partial" if fl else "unfactored")
            w.writerow([f"{fid}:{i}", name, len(s), k, status, len(fl),
                        ";".join(fl), all(is_prime(mpz(f)) for f in fl) if fl else "",
                        prod(fl) == n if fl else ""])

# quick gmpy2 self-verification of full rows
bad = [r for r in verify_rows if not r[4]]
prod_ok = True
for fid, name, k in GROUPS:
    for i, s in enumerate(RAW[fid]["numbers"]):
        fl = sorted(set(state_entry(fid, i)), key=lambda x: mpz(x))
        if fl and all(is_prime(mpz(f)) for f in fl) and prod(fl) != mpz(s):
            prod_ok = False
            print(f"PRODUCT MISMATCH {fid}:{i}")

print("=== SUMMARY ===")
tot = [0, 0, 0]
for fid, name, k, cnt, fu, pa, no in summary:
    print(f"{fid} {name:7s} k={k}: total={cnt:3d} FULL={fu:3d} partial={pa:3d} unfactored={no:3d}")
    tot[0] += fu; tot[1] += pa; tot[2] += no
print(f"TOTAL: FULL={tot[0]} partial={tot[1]} unfactored={tot[2]} / {sum(t[0]+t[1]+t[2] for t in [tot])}")
print(f"prime-check failures: {len(bad)} | product mismatches: {0 if prod_ok else 1}")

# dump verify rows for the sympy cross-check
with open(f"{WORK}/verify_rows.json", "w") as f:
    json.dump(verify_rows, f)
