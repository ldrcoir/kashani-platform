# Worklog

---
Task ID: 1
Agent: main (Z.ai)
Task: Factor 125 large composites (3-6 prime factors of 30-50 digits each) from 4 challenge files and deliver everything as a ZIP.

Work Log:
- Checked environment: 2 CPU cores, no gmpy2/sympy on py3.13 initially, no GMP-ECM.
- Installed/used: gmpy2 2.3.2 (py3.13), sympy 1.14 (py3.12), GMP-ECM 7.0.6 extracted from Debian .deb (no root needed, LD_LIBRARY_PATH workaround).
- Parsed 4 challenge files -> work/numbers.json: quad 50 numbers (122-172d), penta 30 (157-199d), triple 30 (92-135d), hexa 15 (184-194d).
- Structural checks: no cross-number GCDs, no perfect powers, no small factors — numbers are honestly hard.
- Wrote scripts/factor_pipeline.py: 2-worker async scheduler, P-1/P+1 lottery (B1=10M) on all 125, then ECM ladder (B1 250k->1M->3M->11M) prioritized by (k, digits).
- Key parsing lesson: `ecm -q` prints per input line "<found factors...> <remaining cofactor>"; last token is the cofactor, not a find. Fixed parser accordingly (man-page verified).
- Harness kills background children between bash calls; switched to foreground resumable chunks (state.json persistence), 7 chunks x ~9 min.
- Found factors: 15 triples fully factored; 1 more triple + 2 quads got 1 prime each (partial). P-1 lottery scored 44d (001:17) and 36d (001:42) factors.
- Generated results in exact requested format (n=, factors=, ---) for full solutions only; all_status.csv covers every number incl. partials.
- Verified: all 45 factors of the 15 full solutions are prime per gmpy2 AND sympy (independent impl), factor counts match k, products reconstruct n exactly.

Stage Summary:
- Deliverable: /home/z/my-project/download/factorization_results.zip (+ unpacked dir factorization_results/)
- Results: 15/125 full (all triple group), 3 partial, 107 unfactored — remaining numbers need factor sizes beyond ~70 CPU-min on 2 cores (ECM t35+ / GNFS territory).
- Resume path documented in README: rerun factor_pipeline.py with BUDGET_SEC to add compute, then make_results.py.
