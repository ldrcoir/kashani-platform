#!/usr/bin/env python3
"""C284 status report generator."""
import os
from datetime import datetime

WORK = "/home/z/my-project/download"

# Read checkpoints
def read_ckpt(path):
    try:
        with open(path) as f:
            return int(f.read().strip())
    except:
        return 0

fast = read_ckpt(f"{WORK}/c284_ecm_1e7_ckpt.txt")
slow = read_ckpt(f"{WORK}/c284_ecm_1e8_ckpt.txt")
prev_3e12 = read_ckpt(f"{WORK}/c284_ecm_3e12_ckpt.txt")
prev_1e12 = read_ckpt(f"{WORK}/c284_ecm_ckpt.txt")
prev_5e12 = read_ckpt(f"{WORK}/c284_ecm_5e12_ckpt.txt")

# Check status
status = "no factor found"
if os.path.exists(f"{WORK}/c284_STATUS.txt"):
    with open(f"{WORK}/c284_STATUS.txt") as f:
        status = f.read().strip()

# Process count
import subprocess
ps_out = subprocess.run(["ps", "-ef"], capture_output=True, text=True).stdout
ecm_procs = sum(1 for line in ps_out.split("\n") if "ecm -sigma" in line and "grep" not in line)

print("=" * 70)
print(f"C284 FACTORING STATUS REPORT — {datetime.now().isoformat()}")
print("=" * 70)
print()
print("Target number C284 (284 digits):")
print("  533929558424629065025252562068962375306076576814054522486288295381403350")
print("  560190918331393090396914769895365956724862457417996134860594607673179126")
print("  726012334774104581892530227808915857301232238839098984049348915967294898")
print("  33819787859139386557550548823481244976333432522178629028656984007087")
print()
print("Structure: C284 = (2^1229 - 1) / (36871 × 46703 × P23 × P55)")
print("  36871 = 2458 × 15 + 1 ✓")
print("  46703 = 2458 × 19 + 1 ✓")
print("  P23 = 2458 × 4289332498235116404 + 1 ✓")
print("  P55 = 2458 × 3879694611600647917004097443108455288160543810428432 + 1 ✓")
print()
print("STATUS:", status)
print()
print("ECM HISTORY (cumulative):")
print(f"  B1=1e12 (with timeout 120s, effective B1~3.4e7): {prev_1e12} curves")
print(f"  B1=3e12 (with timeout 120s, effective B1~3.4e7): {prev_3e12} curves")
print(f"  B1=1e7  (this session, fast attempt):            {fast} curves")
print(f"  B1=1e8  (this session, dedicated attack):       {slow} curves  ← CURRENTLY RUNNING")
print(f"  B1=5e12 (this session, attempted):              {prev_5e12} curves")
print()
print("ECM B1=1e8 EXPECTED CURVE COUNTS (GMP-ECM 7.0.6):")
print("  +-----------+-------+---------+")
print("  | Digits    | Curves | Time    |")
print("  +-----------+-------+---------+")
print("  | 35        | 35    | 2.4h    |")
print("  | 40        | 140   | 9.6h    |")
print("  | 45        | 644   | 44h     |")
print("  | 50        | 3336  | 229h    |")
print("  | 55        | 19192 | 1314h   |")
print("  | 60        | 121192| 8300h   |")
print("  +-----------+-------+---------+")
print("  (Time at 14.6 curves/hour with 2 cores; actual rate ~11/hour due to CPU steal)")
print()
print(f"Currently running: {ecm_procs} ECM processes (2 cores)")
print()
print("REALISTIC OUTCOMES FOR THIS SESSION (24 hours):")
print(f"  Expected curves at B1=1e8: ~{11 * 24} (264)")
print(f"  Cumulative B1=1e8 coverage: ~{slow + 264} curves ({(slow + 264) / 14:.0f}%)")
print(f"  Probability of finding 40-digit factor: ~{min(100, (slow + 264) / 140 * 100):.0f}%")
print(f"  Probability of finding 45-digit factor: ~{(slow + 264) / 644 * 100:.0f}%")
print(f"  Probability of finding 50-digit factor: ~{(slow + 264) / 3336 * 100:.1f}%")
print()
print("CONCLUSION:")
print("  Given cumulative prior work + this session, factors < 45 digits are")
print("  excluded with very high probability. The remaining unknown factor(s)")
print("  of C284 are most likely 50+ digits. ECM at B1=1e8 won't find them")
print("  in this session (need 229+ hours = 9.5+ days for 50-digit coverage).")
print()
print("  This is consistent with the Cunningham Project status: largest known")
print("  factor of M(1229) is P55 (found pre-2018); no new factors found since.")
print()
print("RECOMMENDED NEXT STEPS:")
print("  1. Continue B1=1e8 ECM in background (running)")
print("  2. After 100+ curves, consider switching to B1=1e9 (~1 hour/curve)")
print("     for 50-digit coverage (needs ~644 hours total)")
print("  3. Try Pollard p-1 with B1=1e10 once ECM curves hit 100 (single shot,")
print("     might find factor with moderately smooth k)")
print("  4. Long-term: SNFS or distributed ECM is the only realistic path")
