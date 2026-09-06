---
Task ID: ecm-1
Agent: main
Task: Use ECM (Elliptic Curve Method) to find factors for Mersenne numbers in the A136030 series, update the factors table, and commit to git.

Work Log:
- Parsed /home/z/my-project/download/A136030_first_191_full_factorizations.txt; extracted smallest prime factor for 191 prime exponents.
- Compared against /home/z/my-project/download/A136030_factors_1_to_8000.txt; found 328 entries marked -1 (unknown).
- Of those 328 missing entries, 46 had known factorizations in the full_factorizations file but were not propagated to the factors table. Propagated them. Missing count dropped from 328 to 282.
- Ran sympy ECM on M(1277), M(1283), M(1291), M(1297), M(1301), M(1307), M(1319), M(1409). No new factors found.

Stage Summary:
- 46 known factors propagated; missing count 328 -> 282.
- 0 new factors from local ECM (expected).
- Artifacts: scripts/ecm_factor_missing.py, download/ECM_factor_report.txt, download/ECM_factor_summary.json, updated download/A136030_factors_1_to_8000.txt.

---
Task ID: cunningham-1
Agent: main
Task: Parse the Cunningham 2- table, extract known factors for Mersenne numbers, propagate to A136030_factors_1_to_8000.txt, assemble complete factorizations file, attempt ECM on smallest composite cofactors.

Work Log:
- Wrote scripts/parse_cunningham_propagate.py to parse cunningham_table_2_minus.txt (749 odd exponents n < 1500).
- Extracted explicit prime factors + P/C cofactor markers.
- Propagated 12 smallest factors from Cunningham into A136030_factors_1_to_8000.txt: M(1283), M(1291), M(1297), M(1301), M(1307), M(1319), M(1409), M(1427), M(1429), M(1471), M(1483), M(1487). Missing count 282 -> 270.
- Wrote scripts/assemble_complete_factorizations.py to combine the 191-entry existing file with Cunningham data. Result: 238 entries total, 221 FULL (fully factored), 17 PART (partial).
- Tried ECM on 4 smallest composite cofactors (C248 M(1217), C284 M(1229), C291 M(1381), C297 M(1213)). No new factors found (expected; well-studied composites).
- Wrote scripts/propagate_from_complete.py to propagate smallest factors from the complete file. No additional missing entries were coverable from this set (n > 1500 not in Cunningham).

Stage Summary:
- 12 more factors propagated from Cunningham; missing count 282 -> 270.
- A136030_complete_factorizations.txt now has 238 entries (221 FULL, 17 PART).
- Status breakdown of remaining 270 missing: 0 for n<=1000, 1 for 1001-1500 (M(1277)), 19 for 1501-2000, 45 for 2001-3000, 85 for 3001-5000, 120 for 5001-8000.
- Artifacts: scripts/parse_cunningham_propagate.py, scripts/assemble_complete_factorizations.py, scripts/propagate_from_complete.py, download/A136030_complete_factorizations.txt, download/A136030_status_report.txt, download/cunningham_propagation_report.txt, download/cunningham_propagation_summary.json, download/cofactor_ecm_log.txt.

---
Task ID: trial-div-1
Agent: main
Task: Trial division on smallest missing primes > 1500 (beyond Cunningham's range).

Work Log:
- Wrote scripts/trial_divide_missing.py with form 2*k*p+1 search (Mersenne-specific).
- Ran on M(1549), M(1571), M(1597) with 60s budget each, k up to ~16M.
- No factors found (smallest factors likely much larger than ~5e10).

Stage Summary:
- 0 new factors found via trial division in this short run.
- Artifacts: scripts/trial_divide_missing.py (re-runnable, adjustable budget), download/trial_division_log.txt.

---
Overall Progress (across all three task IDs):
- A136030_factors_1_to_8000.txt: missing count 328 -> 270 (58 entries recovered).
- A136030_complete_factorizations.txt: 238 entries (221 FULL, 17 PART, 0 MERSE).
- All n <= 1000 covered; only M(1277) missing in 1001-1500.
- 3 git commits: 218adee, 0434783, 1fe270b.
