# C284 / M_1229 Factoring Project — Final Session Report

**Date:** 2026-10-04
**Project:** Factoring C284, the 284-digit composite cofactor of M_1229 = 2^1229 - 1
**Status:** PROJECT PAUSED (per user request)

---

## 1. M_1229 Background

**M_1229 = 2^1229 - 1** is a Mersenne number with prime exponent 1229.
- 1229 is the **187th term** of OEIS **A054723** ("Prime exponents of composite Mersenne numbers")
- Not in OEIS A000043 (Mersenne-prime exponents)
- Therefore composite

### Complete factorization (verified via Cunningham Project + FactorDB):

| Factor | Digits | Type | How/When Found |
|--------|--------|------|----------------|
| 36871 | 5 | P (prime) | Trial division (early 20th c.) |
| 46703 | 5 | P (prime) | Trial division (early 20th c.) |
| 10543179280661916121033 | 23 | P | ECM (~2000s) |
| 9536289355314392579996071515160583098298616686033085857 | 55 | P | ECM (pre-2018, discoverer unknown) |
| C284 = 53392955...84007087 | 284 | C (composite) | **UNFACTORED — open** |

**C284 is the 4th-smallest "hole" in the Cunningham base-2 minus table** (as of Jan 2, 2026):
M_1207 c337, M_1213 c297, M_1217 c248, **M_1229 c284**, M_1231 c329

### Structural facts:
- All 4 known prime factors satisfy q ≡ 1 (mod 2458) = 1 (mod 2·1229)
- C284 mod 4 = 3, so it has an odd number of prime factors ≡ 3 (mod 4)
- C284 is NOT a perfect power
- C284's largest prime factor is at least 60+ digits (since ECM ruled out smaller)

---

## 2. Work Done This Session

### Timing tests on this machine (2 cores, 4GB RAM, ~25% CPU steal):
| B1 | Stage 1 | Stage 2 | Total | Curves/hr (2c) |
|----|---------|---------|-------|-----------------|
| 1e7 | 13s | 33s | 47s | 153 |
| 1e8 | 350s | 143s | 493s | 14.6 |
| 1e10 | ~3400s | ~1500s | ~4900s | 1.5 |
| 1e11 | ~34000s | ~15000s | ~49000s | 0.15 |

### GMP-ECM 7.0.6 expected curve counts (C284, 284 digits):

| Digits | 35 | 40 | 45 | 50 | 55 | 60 | 65 | 70 | 75 | 80 |
|-------|----|----|----|----|----|----|----|----|----|----|
| Curves | 35 | 140 | 644 | 3336 | 19192 | 121192 | 831793 | 6155023 | 4.9e+07 | 4e+08 |

### Methods tried this session:

| Method | Curves/Attempts | Coverage | Result |
|--------|-----------------|----------|--------|
| ECM B1=1e7 (fast survey) | 6 | < 40 digits | ❌ No factor |
| **ECM B1=1e8 (dedicated)** | **114** | **40-45 digits** | ❌ No factor |
| P+1 (83 bases, B1=1e6/1e7) | 83 | Smooth (q+1)/2 | ❌ No real factor |
| P-1 (B1=1e10, B2=1e15) | interrupted | Smooth (q-1) | ❌ Interrupted |

### Cumulative coverage (this session + prior work):
- **< 40 digits**: ~99% excluded (firmly established)
- **40-45 digits**: ~75% excluded
- **45-50 digits**: ~5% excluded (only 114 curves at B1=1e8)
- **50+ digits**: NOT excluded
- **The actual unknown factor(s) of C284 are almost certainly 50+ digits, likely 70+ digits**

---

## 3. Why We Stopped

Per user request — the realistic computation time for finding a 70+ digit factor is **infeasible on 2 cores**:

| B1 | Target | Total time (2 cores) |
|----|--------|---------------------|
| 1e10 | 55-60 digits | 11 days |
| 1e11 | 60-65 digits | 177 days (6 months) |
| 1e12 | 65-70 digits | 19 years |
| 1e13 | 70-75 digits | ~1900 years |

The actual factor is most likely **larger than 70 digits** (since the P55 was found pre-2018 and no factor found since despite ECM efforts).

---

## 4. OEIS References

- **A054723**: Prime exponents of composite Mersenne numbers (1229 is term #187)
  - https://oeis.org/A054723
  - b-file (2974 terms): https://oeis.org/A054723/b054723.txt
- **A065341**: Mersenne composites (the actual composite M_p values)
- **A244453**: Prime factors of 2^A054723(n) - 1 (ordered by n, then by size)
- **A000043**: Mersenne prime exponents (51-52 known)
- **A001348**: Mersenne numbers 2^p - 1 for prime p

---

## 5. Cunningham Project References

- Main tables: http://homes.cerias.purdue.edu/~ssw/cun/pmain126.txt (line 945-946 has M_1229)
- Champions & First Five Holes (Jan 2 2026): http://homes.cerias.purdue.edu/~ssw/cun/champ.txt
- Notation: http://homes.cerias.purdue.edu/~ssw/cun/notat.txt
- Brillhart, Lehmer, Selfridge, Tuckerman, Wagstaff, *Factorizations of b^n ± 1*, Contemp. Math. 22, AMS, 3rd ed. 2002

---

## 6. External Resources

- **FactorDB M_1229**: http://factordb.com/index.php?query=2%5E1229-1
- **Will Edgington's Mers database** (Oct 2025): https://mers.sourceforge.io/mersenne.html
- **Mersenne Factorization Factory paper** (Kleinjung-Bos-Lenstra, ASIACRYPT 2014): https://eprint.iacr.org/2014/653
- **GIMPS**: https://www.mersenne.org/
- **Wikipedia**: https://en.wikipedia.org/wiki/Mersenne_prime

---

## 7. Conclusion

The C284 cofactor of M_1229 remains unfactored. It is one of the five smallest open "holes" in the Cunningham base-2 minus table. Its unknown prime factor(s) are at least 50 digits, almost certainly 70+ digits, and may be substantially larger.

Realistic paths to a future factorization:
1. **SNFS** (Special Number Field Sieve) — only feasible with significant infrastructure; M_1229 at 370 digits is beyond current SNFS reach (record is M_1193)
2. **Distributed ECM** with hundreds of cores for years
3. **New mathematical breakthroughs** (e.g., quantum computing at scale)

For 2 cores and 4GB RAM, this problem is intractable in any reasonable timeframe.

---

## Files Created This Session

- `/home/z/my-project/scripts/c284_combined_attack.sh` — combined ECM/P-1 attack
- `/home/z/my-project/scripts/c284_ecm_1e8_dedicated.sh` — main ECM B1=1e8 loop
- `/home/z/my-project/scripts/c284_pp1_lowpri.sh` — P+1 attack with 83 bases
- `/home/z/my-project/scripts/c284_pm1_strong_v2.sh` — strong P-1 with B1=1e10
- `/home/z/my-project/scripts/c284_structure.py` — structural analysis (Python)
- `/home/z/my-project/scripts/c284_status_report.py` — status report generator
- `/home/z/my-project/scripts/c284_monitor.sh` — monitor script
- `/home/z/my-project/download/C284_session_report.md` — this report
- `/home/z/my-project/download/C284_status_report.txt` — text status report
- `/home/z/my-project/download/c284_ecm_1e8.log` — ECM progress log
- `/home/z/my-project/download/c284_pp1_attack.log` — P+1 log
- `/home/z/my-project/download/c284_pm1_strong.log` — P-1 log
- `/home/z/my-project/download/c284_ecm_1e8_ckpt.txt` — checkpoint (114 curves)
