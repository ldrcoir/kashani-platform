---
Task ID: ecm-1
Agent: main
Task: Use ECM (Elliptic Curve Method) to find factors for Mersenne numbers in the A136030 series, update the factors table, and commit to git.

Work Log:
- Parsed /home/z/my-project/download/A136030_first_191_full_factorizations.txt; extracted smallest prime factor for 191 prime exponents.
- Compared against /home/z/my-project/download/A136030_factors_1_to_8000.txt; found 328 entries marked -1 (unknown).
- Of those 328 missing entries, 46 had known factorizations in the full_factorizations file but were not propagated to the factors table. Propagated them (e.g. M(101) -> 7432339208719, M(103) -> 2550183799, M(137) -> 32032215596496435569, M(199) -> 164504919713, M(257) -> 535006138814359, ...). Missing count dropped from 328 to 282.
- Wrote /home/z/my-project/scripts/ecm_factor_missing.py to perform propagation + ECM in one pass.
- Ran ECM (sympy.ntheory.ecm) on the 8 smallest genuinely-unfactored Mersenne numbers: M(1277), M(1283), M(1291), M(1297), M(1301), M(1307), M(1319), M(1409). Time budget 15s/target. B1 schedule: 2000, 11000, 50000, 250000, 1000000.
- ECM did not find new factors in this short run. (Expected - these numbers have been heavily worked on by the math community for years; M(1277) in particular is the smallest Mersenne number of unknown character.)
- Generated report: /home/z/my-project/download/ECM_factor_report.txt
- Generated machine-readable summary: /home/z/my-project/download/ECM_factor_summary.json
- Updated /home/z/my-project/download/A136030_factors_1_to_8000.txt with the 46 propagated factors (missing count now 282, down from 328).

Stage Summary:
- 46 known factors propagated from full_factorizations.txt to the master factors table.
- 0 new factors found by ECM in this short local run (8 targets, 15s each).
- Artifacts produced:
  - scripts/ecm_factor_missing.py (persisted, re-runnable)
  - download/ECM_factor_report.txt (human-readable report)
  - download/ECM_factor_summary.json (machine-readable summary)
  - download/A136030_factors_1_to_8000.txt (updated in place; missing count 328 -> 282)
- Next step: git add + commit.
