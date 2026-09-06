---
Task ID: ecm-1
Agent: main
Task: Use ECM (Elliptic Curve Method) to find factors for Mersenne numbers in the A136030 series, update the factors table, and commit to git.

Work Log:
- Parsed /home/z/my-project/download/A136030_first_191_full_factorizations.txt; extracted smallest prime factor for 191 prime exponents.
- Compared against /home/z/my-project/download/A136030_factors_1_to_8000.txt; found 328 entries marked -1 (unknown).
- Propagated 46 known factors from full_factorizations into the master table. Missing: 328 -> 282.
- Ran sympy ECM on M(1277)..M(1409); no new factors (expected, well-studied).

Stage Summary:
- 46 known factors propagated; missing 328 -> 282.
- Artifacts: scripts/ecm_factor_missing.py, download/ECM_factor_report.txt.

---
Task ID: cunningham-1
Agent: main
Task: Parse the Cunningham 2- table, extract known factors, propagate to A136030_factors_1_to_8000.txt, assemble complete factorizations file.

Work Log:
- Parsed cunningham_table_2_minus.txt (749 odd exponents n < 1500).
- Propagated 12 factors from Cunningham into A136030_factors_1_to_8000.txt.
- Wrote A136030_complete_factorizations.txt combining existing + Cunningham data.
- Tried ECM on 4 smallest composite cofactors; no new factors.
- Missing: 282 -> 270.

Stage Summary:
- 12 more factors propagated.
- A136030_complete_factorizations.txt: 238 entries (221 FULL, 17 PART).
- 0 missing for n <= 1000; only M(1277) missing in 1001-1500.

---
Task ID: p1-1
Agent: main
Task: P-1 factoring on smallest missing primes > 1500 (Cunningham's range ends at 1499).

Work Log:
- Installed gmpy2 for fast modular arithmetic.
- Wrote scripts/pm1_factor.py implementing P-1 with Stage 1 (B1) and Stage 2 (B2).
- P-1 is especially effective for Mersenne factors: any prime q | M(p) has q-1 = 2*k*p, so q-1 is highly smooth if k is smooth.
- Initial run with B1=10M, B2=1G found factors of M(1549) and M(1571) - missing 270 -> 268.
- Subsequent runs with B1=2M, B2=100M and B1=2M, B2=30M found many more factors.

DISCOVERED BUG (commits 00501da5 onwards):
- The script's --specific flag let users target primes that already had smaller factors.
- The script blindly overwrote existing smaller factors with P-1 gcd results.
- The P-1 gcd can return a composite product of multiple prime factors.
- The script treated this composite as "the factor" and stored it.

FIX (commit 0a336a1):
- Reset to commit 63656cd (last good commit).
- Modified update_factor() to only update if existing value is -1 OR new factor is smaller AND prime.
- Modified --specific to filter out primes that are not -1.
- Added composite-gcd detection: when gcd is composite, trial-divide to extract smallest prime factor; if no small prime factor is found, skip the result.

After fix, continued P-1 runs systematically through missing primes by range.
Stage 2 bound B2 reduced to 30M for faster iteration cycles.

Stage Summary:
- 67+ new factors found via P-1 across all ranges.
- Missing count progression: 270 (start) -> 268 -> 257 -> 253 -> 250 -> 245 -> 240 -> 234 -> 232 -> 228 -> 226 -> 225 -> 223 -> 221 -> 220 -> 216 -> 215 -> 212 -> 209 -> 207 -> 206 -> 205 -> 204.
- Notable tiny factors found: M(3623) -> 7247 (k=1, smoothest possible), M(3581) -> 21487 (k=3).
- Notable large factors found: M(3613) -> 467326338237609615909534163488286772503714077551 (Stage 1, 48 digits).
- The composite-gcd detection correctly rejected several results that would have corrupted the table.

---
Overall Progress (across all task IDs):
- A136030_factors_1_to_8000.txt: missing count 328 -> 204 (124 entries recovered, 37.8% reduction).
- A136030_complete_factorizations.txt: 238 entries (221 FULL, 17 PART).
- Coverage by range:
  - n in [1, 1000]: 0 missing (fully covered)
  - n in [1001, 1500]: 1 missing (M(1277), famous open case)
  - n in [1501, 2000]: ~16 missing (was 19)
  - n in [2001, 3000]: ~36 missing (was 45)
  - n in [3001, 5000]: ~75 missing (was 85)
  - n in [5001, 8000]: ~76 missing (was 120)
- 30+ git commits documenting the work.
- Re-runnable scripts: scripts/pm1_factor.py, scripts/trial_divide_fast.py, scripts/ecm_factor_missing.py, scripts/parse_cunningham_propagate.py, scripts/assemble_complete_factorizations.py.
