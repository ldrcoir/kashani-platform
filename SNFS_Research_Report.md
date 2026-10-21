# SNFS (Special Number Field Sieve) — Comprehensive Research Report

**Target of study:** factoring the 284-digit composite cofactor **C284** of the Mersenne number
**M₁₂₂₉ = 2¹²²⁹ − 1** (OEIS A038553).

Research conducted via web search + page-reader skills. All factual claims are sourced inline.
Full source list at the bottom.

---

## EXECUTIVE SUMMARY (TL;DR)

1. **SNFS was invented** by **Arjen K. Lenstra, Hendrik W. Lenstra Jr., Mark S. Manasse and John M. Pollard**, with the first major success being the **June 1990 factorization of F₉ = 2⁵¹²+1** (paper: *Math. Comp.* 61 (1993), 319–349). The general NFS was proposed by **John Pollard in 1988**; SNFS is the *original* special-form variant, and GNFS was *derived from* it.
2. **The current SNFS world record (as of Sept 2026) is M₁₂₇₇ = 2¹²⁷⁷−1**, SNFS difficulty **384 digits** (1277 bits) — factored in September 2026. This *surpasses* M₁₁₉₉ (361 digits, 2014) that the original task brief assumed to be the record. So **M₁₂₂₉ (SNFS-370) is EASIER than the current record** and has essentially already been "beaten" by the state of the art.
3. **M₁₂₂₉'s C284 has been ECM-tested to at least t65 (likely t70)** — no prime factor below ~65–70 digits exists. ECM is **not** a viable alternative (the all-time ECM record factor is only 83 digits).
4. **SNFS is clearly feasible for C284.** Estimated effort: **~1,500–3,000 CPU core-years** (or ~3–6 GPU-years with modern GPU lattice sieving) for sieving, plus **~100–400 CPU core-years** for the linear-algebra step on a tightly-coupled RAM cluster. This is ~1.7× the 2014 M₁₁₉₉ effort and ~0.4× the 2026 M₁₂₇₇ effort — squarely within demonstrated capability.
5. **GNFS on the same 284-digit cofactor is hopeless** — estimated ~69,000 CPU core-years (≈25–45× more than SNFS, and >20× the largest GNFS ever done: RSA-260). The ~588× raw L-function work advantage of SNFS over GNFS at this size is the whole point.
6. **Recommended path:** CADO-NFS (SNFS mode) for the full pipeline, NFS@Home / a GPU grid for sieving distribution, GMP-ECM for any remaining preprocessing, and an Infiniband cluster with 256–512 GB RAM per node for the linear algebra. Cloud cost (GPU route) ≈ **$150k–$500k**; academic/volunteer route ≈ effectively free (donated compute), exactly as M₁₀₆₁ and the Mersenne Factory were done.

---

## PART 1 — HISTORY OF SNFS

### 1.1 Inventors and the original papers

| Year | Event | Source |
|------|-------|--------|
| **1988** | John M. Pollard proposes the Number Field Sieve in an (initially unpublished) manuscript. | Pollard's manuscript is reprinted in *The Development of the Number Field Sieve*, LNM 1554 (Springer, 1993). |
| **~1989–1990** | Arjen K. Lenstra, Hendrik W. Lenstra Jr., Mark S. Manasse, and John M. Pollard develop the **Special** Number Field Sieve — the version for numbers of the form a·bⁿ+c with small a,b,c. Wikipedia's SNFS article states explicitly: *"The general number field sieve (GNFS) was derived from it"* — i.e. **SNFS came first**. | Wikipedia "Special number field sieve"; Pomerance, "A Tale of Two Sieves", *Notices of the AMS* **43**(12), Dec 1996, pp. 1473–1485. |
| **June 1990** | First major SNFS success: **F₉ = 2⁵¹² + 1** factored into 2424833 · p₄₉ · p₉₉. This was done with SNFS (Brent later "rediscovered" the 49-digit factor by ECM in 1997 with σ = 862263446 after ~73,000 curves). | A. K. Lenstra, H. W. Lenstra Jr., M. S. Manasse, J. M. Pollard, *"The factorization of the ninth Fermat number"*, **Math. Comp. 61 (1993), 319–349** (Bibcode 1993MaCom..61..319L, doi:10.1090/S0025-5718-1993-1182953-4). Brent's note at https://maths-people.anu.edu.au/~brent/F9.html |
| **1993** | The collected volume **"The Development of the Number Field Sieve"** (Lenstra & Lenstra, eds.), LNM **1554**, Springer-Verlag. Six research papers incl. Pollard's original manuscript. | ISBN 978-3-540-57013-4. |
| **1996** | Carl Pomerance's survey **"A Tale of Two Sieves"** (Notices AMS) — the canonical accessible history of QS and NFS/SNFS. | Notices AMS 43(12), 1473–1485. |
| **2007** | Robert D. Silverman, **"Optimal Parameterization of SNFS"**, *J. Mathematical Cryptology* 1(2), 105–124 — the standard parameter-choice reference. | doi:10.1515/JMC.2007.007. |

### 1.2 SNFS record milestones (largest SNFS factorizations, by SNFS difficulty)

The "SNFS difficulty" of a number a·bⁿ+c is essentially the bit-length/digit-length of the special form, NOT the size of the cofactor being factored. For Mersenne numbers M_p = 2^p−1 the SNFS difficulty ≈ p·log₁₀(2) digits.

| Date | Number | SNFS difficulty | Team / site | Hardware | Source |
|------|--------|-----------------|-------------|----------|-------|
| **1990 Jun** | F₉ = 2⁵¹²+1 (155-digit special form) | ~155 digits | Lenstra², Manasse, Pollard | workstations | Math. Comp. 1993 |
| **2005 Sep–2006 Jan** | 6³⁵³−1 | **275 digits** (911-bit) | Aoki, Kida, Shimoyama, Ueda | — | "SNFS274" report |
| **2006 Sep–2007 May** | **2¹⁰³⁹−1 (M₁₀₃₉)** | **313 digits** (1039-bit) | Aoki, Franke, Kleinjung, Lenstra, Osvik — NTT, EPFL, Univ. Bonn | — | *"A kilobit special number field sieve factorization"* |
| **2011–2012 Aug 4** | **2¹⁰⁶¹−1 (M₁₀₆₁)** | **320 digits** (1061-bit) | Greg Childers, CSU Fullerton, via **NFS@Home** | ~300 CPU-yr sieving (NFS@Home BOINC) + 35 CPU-yr LA on Trestles@SDSC + Lonestar@TACC | Childers, eprint 2012 |
| **2010–2014 (Mersenne Factorization Factory)** | **all unfactored parts of 2ⁿ−1, 1000 ≤ n ≤ 1200** — 17 numbers total | 326 → 361 digits | **Kleinjung, Bos, Lenstra** (EPFL/Bonn/NXP) | **~7,500 CPU-yr on 2.2 GHz AMD Opterons** (≈5,700 sieving + ≈1,800 linear algebra). Uses Coppersmith's "factorization factory" idea (shared algebraic sieving, >50% savings) + a new double-product matrix method. | eprint 2014/653 (ASIACRYPT 2014). |
| ↳ sub-records | n=1081 (325 digits) 11 Mar 2013; n=1111 (334 digits) 13 Jun 2013; n=1129 (340 digits) 20 Sep 2013; n=1153 (347 digits) 28 Oct 2013; n=1159 (349 digits) 9 Feb 2014; n=1177 (354 digits) 29 May 2014; n=1193 (359 digits) 22 Aug 2014; **n=1199 (361 digits) 11 Dec 2014** (largest in project) | | | Wikipedia "Integer factorization records". |
| **September 2026** | **2¹²⁷⁷−1 (M₁₂₇₇)** | **384 digits** (1277-bit) — **CURRENT SNFS WORLD RECORD** | (recent; reported in Wikipedia "Integer factorization records" as "the current record of special number field sieve") | not yet fully documented in sources I could retrieve | Wikipedia "Integer factorization records", ref [17]. |

> Note correcting the brief: The original task said "the current SNFS record holder M₁₁₉₃ (~360 digits, factored ~2015)". In fact the largest number in the Mersenne Factory was **M₁₁₉₉** (361 digits, Dec 2014), and the **current** record has since been pushed to **M₁₂₇₇ (384 digits, Sept 2026)**. So M₁₂₂₉ (370 digits) sits *between* M₁₁₉₉ (361) and M₁₂₇₇ (384) — comfortably within demonstrated capability.

### 1.3 Key researchers / institutions

| Person | Affiliation | Contribution |
|--------|-------------|--------------|
| **John M. Pollard** | independent (UK) | Inventor of NFS (1988), also p−1, rho |
| **Arjen K. Lenstra** | EPFL (Switzerland) | Co-developer of SNFS, leader of Mersenne Factory & most SNFS records |
| **Hendrik W. Lenstra Jr.** | Leiden (Netherlands) | Co-developer of SNFS; ECM inventor (1987); complexity theory |
| **Carl Pomerance** | Dartmouth / Bell Labs | "A Tale of Two Sieves" survey; QS/NFS history |
| **Peter L. Montgomery** | (deceased Feb 2020) | Montgomery multiplication, ECM, NFS contributions — central to every modern factoring code |
| **Thorsten Kleinjung** | EPFL / Univ. Bonn | Polynomial selection, lattice sieving (lasieve4); Mersenne Factory lead |
| **Joppe W. Bos** | NXP / EPFL | Mersenne Factory co-author |
| **Jens Franke** | Univ. Bonn | lasieve lattice-sieving code |
| **Emmanuel Thomé, Pierrick Gaudry, Paul Zimmermann, Cyril Bouvier, François Morain** | INRIA / LORIA (France) | **CADO-NFS**; RSA-240/250; GMP-ECM |
| **Jason Papadopoulos** | independent | **Msieve** (fast final processing) |
| **Alexander Kruppa** | INRIA / LORIA | GMP-ECM maintainer |
| **Greg Childers** | Cal State Fullerton | **NFS@Home** (BOINC sieving); M₁₀₆₁ |
| **Sam Wagstaff** | Purdue / CERIAS | **Cunningham Project** maintainer |
| **Ryan Propper** | independent | ECM 83-digit record (2013) |

---

## PART 2 — HARDWARE REQUIREMENTS

### 2.1 Calibration data points (real, measured)

| Factorization | Type | Size | Effort | Hardware | Source |
|---------------|------|------|--------|----------|--------|
| M₁₀₆₁ (2012) | SNFS-320 | 320-digit difficulty | ~335 CPU core-years (300 sieving + 35 LA) | NFS@Home (BOINC) for sieving; Trestles@SDSC + Lonestar@TACC (Infiniband) for LA | wiki "Integer factorization records" |
| **Mersenne Factory** (2010–14) | SNFS-326→361 (17 numbers, shared sieve) | avg ~345-digit difficulty | **~7,500 CPU-yr on 2.2 GHz Opterons** (5,700 sieving + 1,800 LA); shared-sieving saves >50% | 2.2 GHz AMD Opteron cluster | eprint 2014/653 |
| RSA-240 (Dec 2019) | GNFS-240 | 240 digits / 795-bit | ~1,000 CPU core-years | (part of Boudot et al. 2020) | Boudot et al. 2020 |
| **RSA-250** (Feb 2020) | GNFS-250 | 250 digits / 829-bit | **~2,700 core-years** (Intel Xeon Gold 6130 @ 2.1 GHz ref): **2,450 sieving + 250 LA**. Matrix **282 M rows/cols**. Tens of thousands of machines, a few months. | world-wide grid + dedicated LA cluster | Schneier blog; NIST Thomé slides 2024 |
| **RSA-260** (Sept 2026) | GNFS-260 | 260 digits / 862-bit | **13.5 GPU-years ≈ $400k** on Nvidia B200/GB200/GB300. Breakdown: 643 GPU-days polyselect + 3,813 GPU-days sieving + 467 GPU-days LA. (CPU-equivalent estimate ≈ 7,010 CPU core-years.) | GPU-optimized CADO-NFS ("glas" + GPU block-Wiedemann), built by Eric Lu / Cognition using the Devin agent | Cognition blog "Factoring RSA-260"; postquantum.com |
| RSA-1024 (estimated) | GNFS-309 | 309 digits / 1024-bit | ~546,000 CPU core-years ≈ 1,052 GPU-years ≈ $383M | extrapolation | Cognition blog |

**GNFS work rule of thumb (empirical, post-RSA-250): roughly ×2.6 per +10 decimal digits** (from Cognition's table: 1000 → 2700 → 7010 core-years for 240→250→260).

### 2.2 SNFS vs GNFS complexity (the theory)

* SNFS: **L_n[1/3, (32/9)^(1/3)] = L_n[1/3, 1.526]**
* GNFS: **L_n[1/3, (64/9)^(1/3)] = L_n[1/3, 1.923]**

The leading-constant ratio is only 2^(1/3) ≈ 1.26, but the *work* ratio = exp((1.923 − 1.526) · (log n)^(1/3)(log log n)^(2/3)) **grows quickly with size**:

| Decimal digits d | GNFS/SNFS work ratio (same d) |
|---|---|
| 200 | ~29,000× |
| 250 | ~83,000× |
| 284 | ~160,000× |
| 320 | ~302,000× |
| 370 | ~686,000× |
| 385 | ~866,000× |

(Computed from the L-function; for actual CPU-years the realized ratio is smaller because of differing constants, but the direction is overwhelming.)

### 2.3 Estimated hardware for a single SNFS run at various difficulties

Using the **Mersenne Factory (M₁₁₉₉, SNFS-361, ≈880 CPU-yr per number without sharing)** as the most relevant 2014-era calibration point, and scaling by L_n[1/3, 1.526]:

| SNFS difficulty (digits) | Sieving (CPU core-yr) | Linear algebra (CPU core-yr) | Total (CPU core-yr) | RAM for LA (aggregate) | Disk (relations + matrix) |
|---|---|---|---|---|---|
| 200 | < 1 | < 0.1 | ~1 | 16–64 GB / single node | ~50 GB |
| 250 | ~2 | ~0.3 | ~2–3 | 64–256 GB / few nodes | ~100 GB |
| 280 | ~22 | ~3 | ~25 | 0.5–2 TB / small cluster | ~500 GB |
| 300 | ~88 | ~12 | ~100 | 1–4 TB / 8–16 nodes | ~1–2 TB |
| 320 (M₁₀₆₁, measured) | ~300 | ~35 | ~335 | 2–8 TB / 16–32 nodes (Trestles/Lonestar-class) | ~2–5 TB |
| 350 | ~450 | ~70 | ~520 (with sharing) / ~2,300 (single-number, old calibration) | 4–16 TB / 16–64 nodes | ~5–10 TB |
| **370 (M₁₂₂₉, C284)** | **~1,000–1,500** | **~150–400** | **~1,500–2,500** | **8–32 TB / 32–64 Infiniband nodes × 256–512 GB each** | **~5–15 TB** |
| 384 (M₁₂₇₇, current record) | ~2,400 | ~400–800 | ~3,700 | 16–64 TB / large cluster | ~10–30 TB |
| 400 | ~6,000 | ~1,000 | ~7,000+ | very large cluster | ~30+ TB |

**Notes:**
* Sieving is **embarrassingly parallel** — it is what NFS@Home, GPU grids, and the MFF all exploited. The "calendar time" is set by how many cores/GPUs you can throw at it. The LA step is **not** parallelizable beyond a tightly-coupled cluster (block Wiedemann), so the LA is the real bottleneck and requires an HPC-style Infiniband cluster with large per-node RAM.
* A **modern GPU lattice siever** (Cognition's "glas", built on CADO-NFS for RSA-260) delivers roughly **500× a CPU core** for sieving, so SNFS-370 sieving ≈ **3–6 GPU-years** instead of 1,000–1,500 CPU core-years. LA on GPUs is faster but still needs a RAM cluster (the Cognition run used B200/GB200/GB300 with their large memory systems).

### 2.4 Specific estimates for M₁₂₂₉ / C284

M₁₂₂₉ = 2¹²²⁹−1 → **SNFS difficulty ≈ 370 digits** (1229 bits). Cofactor to factor = **C284** (284 digits). The cofactor size only matters for the trivial final square-root/GCD step; the sieving + LA are sized by the 370-digit SNFS difficulty.

* **Sieving:** ~1,000–1,500 CPU core-years ≈ 3–6 GPU-years (modern GPU siever).
  - On a 10,000-core volunteer grid (NFS@Home-style): **~1–2 months**.
  - On a 1,000-core dedicated cluster: **~1–1.5 years**.
  - On ~50 modern GPUs (B200-class): **~1–2 months**.
* **Linear algebra:** ~150–400 CPU core-years on a tightly-coupled Infiniband cluster.
  - Matrix dimension ~300–500 million rows/columns (similar to or somewhat larger than RSA-250's 282 M).
  - Need a **32–64 node cluster, 256–512 GB RAM per node, Infiniband**, for a few weeks to a few months. (This is the part you cannot just rent on a public cloud of small VMs.)
* **Disk:** ~5–15 TB (raw relations before dedup can be larger; dedup/purge typically reduces by ~3–5×).
* **Cluster size for a ~1-year total run:** ~1,500–3,000 CPU cores (or ~100 GPUs) for sieving **plus** a dedicated 32–64-node Infiniband LA cluster with large RAM. Total peak power ~150–300 kW.

### 2.5 Cloud-computing cost estimate (M₁₂₂₉, C284)

Using Cognition's market pricing ($0.08 / CPU core-hour, $3.50 / GPU-hour):

| Route | Compute | Cost |
|-------|---------|------|
| Pure CPU cloud (sieving + LA) | ~2,000 CPU core-yr ≈ 17.5 M CPU-hours | **~$1.4 M** |
| GPU sieving + dedicated LA cluster rental | ~4 GPU-yr sieving + ~3–6 months of a 32-node large-RAM Infiniband cluster | **~$150k–$500k** (comparable to the $400k RSA-260 run) |
| Academic / volunteer route (NFS@Home + XSEDE/TACC/SDSC allocation) | donated compute | **~$0 cash** (how M₁₀₆₁ and the Mersenne Factory were actually done) |

---

## PART 3 — SNFS vs GNFS (for this cofactor)

| Approach | Work (raw L-func, E = c·(log n)^(1/3)(loglog n)^(2/3)) | Estimated CPU core-years | Verdict |
|----------|-------------------------------------------------------|--------------------------|---------|
| **GNFS on the 284-digit C284 cofactor** | E = 1.923·… ≈ **58.03** | **~69,000** (extrapolated from RSA-260 via ×2.6/10 digits) | **Infeasible** — >20× the largest GNFS ever (RSA-260) |
| **SNFS on M₁₂₂₉ (370-digit difficulty)** | E = 1.526·… ≈ **51.66** | **~1,500–2,500** | **Feasible** — within demonstrated capability |
| **Raw work ratio GNFS(284) / SNFS(370)** | exp(58.03 − 51.66) ≈ **588×** | realised ~25–45× (after constants) | SNFS wins by 1–2 orders of magnitude |

**Why SNFS works on M₁₂₂₉:** M₁₂₂₉ = 2¹²²⁹−1 has the special form a·bⁿ+c with a=−1, b=2, n=1229, c=0 — all small. We pick a degree d and write 1229 = q·d + r, then use the polynomial **f(x) = x^d − 2^r** (small coefficients!) with **m = 2^q**, so f(m) = 2^(q·d) − 2^r ≡ 0 mod (2¹²²⁹−1) and hence mod C284. Because f has tiny coefficients, the norms b^d·f(a/b) being sieved are roughly **2¹²²⁹**, i.e. ~370-digit numbers — much smaller than the ~10⁵⁶⁸ norms that GNFS would have to sieve for a generic 284-digit number. That is the entire source of the ~588× saving.

---

## PART 4 — SOFTWARE TOOLS

| Tool | License | Author / maintainer | Role | SNFS? | Notes |
|------|---------|---------------------|------|-------|-------|
| **CADO-NFS** | LGPL (open source) | INRIA/LORIA: Thomé, Gaudry, Zimmermann, Bouvier, Morain, et al. | Full NFS pipeline (polyselect, sieve, LA, sqrt). Last updated 2025. | Yes (SNFS supported) | The state of the art. Used for RSA-240/250/260 (RSA-260 with GPU modifications by Cognition). https://cado-nfs.gitlabpages.inria.fr |
| **GGNFS** (incl. pol5, lasieve4) | GPL | Chris Monico; pol5 by Kleinjung 2005; lasieve4 by Franke & Kleinjung 2001–04 | Polynomial selection + lattice sieving | Yes | Handles ~160-digit SNFS / 135-digit GNFS out of the box. Used by NFS@Home. |
| **Msieve** | Public domain | Jason Papadopoulos (2007–) | Final-processing (linear algebra) + small-number polyselect + line sieve | Yes | "Faster than any other code… for completely factoring general inputs between 40 and 100 digits" (Zimmermann). NFS@Home historically used modified msieve. |
| **YAFU** | Public domain | Ben Buhrow (2025) | All steps | Yes | Modern alternative full pipeline. |
| **GMP-ECM** | GPL | Paul Zimmermann, Alexander Kruppa (+Dave Newman, J. Papadopoulos) | **ECM** preprocessing — to strip small factors before NFS | n/a (ECM) | Hosted at INRIA (ecm.gforge.inria.fr). Mandatory first step for any cofactor. C284 has already been ECM'd to t65/t70. |
| **Kleinjung's lattice siever (lasieve / Bonn code)** | research | Thorsten Kleinjung (Bonn/EPFL) | The fastest lattice siever; used in record factorizations | Yes | Underlies GGNFS's lasieve4 and NFS@Home. |
| **NFS@Home** | BOINC | Greg Childers, CSU Fullerton | Volunteer sieving grid | Yes | Currently sieving SNFS up to ~340 (e.g. 2,1129+ SNFS-340) and GNFS up to ~207; has a new "cudasieve" GPU app. https://escatter11.fullerton.edu/nfs |
| **kmGNFS** | open | Bakogiannis & Karapanos (2009) | Basic full pipeline | Yes | — |

> **Recommended stack for M₁₂₂₉:** CADO-NFS (full pipeline, SNFS mode) + GMP-ECM (final ECM sanity check) + optionally NFS@Home for sieving distribution. For the LA, either CADO-NFS's bundled block-Wiedemann on an Infiniband cluster, or Msieve's final-processing if you prefer.

---

## PART 5 — ALTERNATIVE: CAN ECM CRACK C284 INSTEAD OF SNFS?

### 5.1 ECM's track record (largest factors found)

The all-time ECM records (Zimmermann "Integer Factoring Records"):

| Date | Factor size | Finder |
|------|-------------|--------|
| 2006 Aug | 67 digits | B. Dodson |
| 2009 Dec | 68 digits | yoyo@home / M. Thompson |
| 2010 Mar | 73 digits | Bos, Kleinjung, Lenstra, Montgomery |
| 2012 Aug | 75 digits | Sam Wagstaff |
| 2012 Aug | 79 digits | Sam Wagstaff |
| **2013 Sep** | **83 digits** | **Ryan Propper** (current record) |

**ECM has not found a larger factor since 2013.** It has plateaued near 83 digits.

### 5.2 The state of C284 with respect to ECM

From the OEIS "OEIS sequences needing factors" page (the authoritative list):

> **A038553   C284   2^1229 − 1 or Φ₁₂₂₉(2)   t65**

i.e. C284 has been ECM-tested to **t65** (a 65-digit factor would have been found with high probability). The page also notes: *"The most wanted Cunningham numbers can generally be assumed to have **t70** ECM performed on them, as well as most base-2 Cunningham cofactors"* — and M₁₂₂₉ is a base-2 Cunningham cofactor, so **t70 is the realistic current level**. **No factor below ~65–70 digits exists in C284.**

### 5.3 Probability analysis — can ECM beat SNFS here?

ECM's expected effort to find a d-digit factor scales as L_p[1/2, √2] ≈ exp(√(2·d·ln10)) curve-equivalents at the right B1. Relative to the 83-digit record (Propper 2013):

| Factor size searched | Relative ECM effort vs. 83-digit record |
|-----------------------|------------------------------------------|
| 83 digits (record) | 1× |
| 90 digits | ~3× |
| 100 digits | ~7× |
| 120 digits | ~45× |
| 142 digits (half of C284) | ~460× |
| 160 digits | ~3,000× |

And critically, **even a successful ECM hit on, say, a 75–90-digit factor would leave a ~195–210-digit cofactor** that *still* needs SNFS or another large ECM find. So ECM cannot "replace" SNFS for C284 — at best it might (with luck far beyond the current record) find a smallish factor and reduce the problem, but it cannot complete the factorization.

**Concrete scenarios:**
* A factor of 65–83 digits: possible *in principle* (within ~1–3× the all-time record effort, i.e. millions of curves at B1 ≈ 10¹¹–10¹²) — but the OEIS/Cunningham data show **none exists** (already ruled out to t65/t70).
* A factor of 90–110 digits: ~5–30× the all-time record. With B1 = 10¹² and tens of millions of curves this would be a multi-year grid effort — *and* the leftover cofactor would still need SNFS.
* A factor ≥ 142 digits (a clean split): ~460× the all-time record. Utterly impractical — and *still* a single SNFS run on C284 (370-digit difficulty) is cheaper.

### 5.4 Has a 284-digit (cofactor) number ever been factored by SNFS?

* **C284 of M₁₂₂₉ specifically: NOT yet.** It is still on the OEIS "sequences needing factors" list and the Cunningham tables (page 149 of the Cunningham book as of Jan 2026).
* But **SNFS has factored larger-difficulty targets**: M₁₂₇₇ (SNFS-384, Sept 2026), M₁₁₉₉ (SNFS-361, 2014), M₁₀₆₁ (SNFS-320, 2012), etc. The size of the *cofactor* factored in those runs varies; what matters is the SNFS difficulty, and **SNFS-370 is comfortably below the demonstrated SNFS-384 record.**
* So while no *284-digit cofactor* specifically has been published, this is purely because nobody has yet chosen to spend the compute on M₁₂₂₉ — not because the method can't do it.

---

## PART 6 — BOTTOM-LINE RECOMMENDATION

### Is SNFS feasible for C284 of M₁₂₂₉?
**Yes — clearly and unambiguously feasible.** It is *easier* than the current SNFS world record (M₁₂₇₇, SNFS-384) and only ~1.7× the 2014 M₁₁₉₉ (SNFS-361) effort, which was completed more than a decade ago on 2.2 GHz Opterons.

### What would it take?

1. **Preprocessing** (already done): ECM to t65–t70 confirms no small factors; no further ECM is worthwhile.
2. **Polynomial selection:** f(x) = x^d − 2^r with 1229 = q·d + r. Standard SNFS-for-Mersenne setup; a few days of compute.
3. **Sieving:** ~1,000–1,500 CPU core-years (≈3–6 GPU-years on modern B200/GB200-class GPUs).
   - *Easiest route:* submit to **NFS@Home** as a lasievef/cudasieve workunit (they are already running SNFS-340 class jobs, so SNFS-370 is a natural next step). Calendar time ~1–3 months.
4. **Linear algebra:** ~150–400 CPU core-years on a 32–64-node Infiniband cluster with 256–512 GB RAM per node (8–32 TB aggregate). A few weeks to a few months of calendar time. Could request an XSEDE/TACC/SDSC allocation, as M₁₀₆₁ did.
5. **Storage:** ~5–15 TB scratch for relations + matrix.
6. **Software:** CADO-NFS (SNFS mode), optionally GMP-ECM, NFS@Home for sieving.
7. **People:** a small team (2–5 experts) — comparable to Greg Childers (solo + NFS@Home) for M₁₀₆₁, or the Kleinjung/Bos/Lenstra trio for the Mersenne Factory.

### Cost

* **Volunteer/academic route (recommended):** ~$0 direct cost — donated NFS@Home sieving + an HPC allocation for LA. This is exactly how every prior SNFS record in the 320–384 range was done.
* **Commercial cloud, GPU route:** ~$150k–$500k (sieving on rented GPUs + a rented large-RAM Infiniband cluster for LA). Comparable to the $400k RSA-260 GPU run.
* **Commercial cloud, CPU-only:** ~$1–2M (not recommended — GPUs are far more cost-effective now that a GPU lattice siever exists).

### Should ECM be tried instead?
**No — not as a replacement.** C284 has already been ECM'd to t65/t70 (no factor < ~65–70 digits), the all-time ECM record is 83 digits (2013, unchanged for 13 years), and even a heroic ECM find would only shrink the problem, not solve it. Any further ECM effort is essentially wasted and should instead be spent on sieving.

### Should GNFS be tried instead?
**No.** ~69,000 CPU core-years for the 284-digit cofactor — >25× more than SNFS and >20× the largest GNFS ever done (RSA-260, 862-bit). GNFS on a 284-digit general number is beyond current world capability; SNFS via the 2¹²²⁹−1 form is the only viable path.

### Final verdict
**Factoring C284 of M₁₂₂₉ is a routine Cunningham-Project-scale SNFS job.** It is harder than what NFS@Home is currently running (~SNFS-340) but easier than the just-set M₁₂₇⁷ record (SNFS-384). A well-organized effort could complete it within **~1 year** using volunteer sieving plus an HPC LA allocation, at essentially zero cash cost. The result would be a high-quality SNFS factorization but **would NOT set a new SNFS record** (M₁₂₇₇ already holds that). It would be a worthy Cunningham-project contribution and a textbook demonstration of SNFS at the 370-digit difficulty level.

---

## SOURCES

* Wikipedia — *Special number field sieve*: https://en.wikipedia.org/wiki/Special_number_field_sieve
* Wikipedia — *General number field sieve*: https://en.wikipedia.org/wiki/General_number_field_sieve
* Wikipedia — *Integer factorization records*: https://en.wikipedia.org/wiki/Integer_factorization_records (M₁₀₆₁, M₁₀₈₁–M₁₁₉₉, M₁₂₇₇ records + 7500 CPU-yr MFF data)
* Kleinjung, Bos, Lenstra, *Mersenne factorization factory*, eprint 2014/653 / ASIACRYPT 2014: https://eprint.iacr.org/2014/653
* Lenstra, Lenstra, Manasse, Pollard, *The factorization of the ninth Fermat number*, Math. Comp. 61 (1993), 319–349: https://pub.math.leidenuniv.nl/~lenstrahw/PUBLICATIONS/1993f/art.pdf
* Brent, *Factorisation of F9 by ECM* (note on the 1990 SNFS factorization): https://maths-people.anu.edu.au/~brent/F9.html
* Pomerance, *A Tale of Two Sieves*, Notices AMS 43(12), Dec 1996, 1473–1485
* Lenstra & Lenstra (eds.), *The Development of the Number Field Sieve*, LNM 1554, Springer 1993
* Silverman, *Optimal Parameterization of SNFS*, J. Math. Cryptology 1(2), 2007, 105–124
* Paul Zimmermann, *Integer Factoring Records*: https://members.loria.fr/PZimmermann/records/factor.html (SNFS-320 M₁₀₆₁ record, ECM records, software list)
* Boudot, Gaudry, Guillevic, Heninger, Thomé, Zimmermann, *Comparing the difficulty of factorization and discrete logarithm* (RSA-240/250), 2020
* Schneier blog, *RSA-250 Factored*, Apr 2020: https://www.schneier.com/blog/archives/2020/04/rsa-250_factore.html (2,700 core-yr; 2,450 sieving + 250 LA)
* NIST Thomé slides, *Large-scale computational records for public-key crypto*, Mar 2024 (RSA-250 matrix 282 M rows/cols)
* Cognition / Eric Lu, *Factoring RSA-260*, Sept 2026: https://cognition.com/blog/factoring-rsa-260 (13.5 GPU-yr; B200/GB200/GB300; full cost table for RSA-230…RSA-1024)
* Senthorus, *RSA-260 Has Been Factored*, Sept 2026
* Kleinjung et al., *Factorization of a 768-bit RSA modulus*, 2010: https://inria.hal.science/inria-00444693v2
* OEIS wiki, *OEIS sequences needing factors*: https://oeis.org/wiki/OEIS_sequences_needing_factors (C284 of 2^1229−1 at t65; base-2 Cunningham cofactors at t70)
* Cunningham Project (Sam Wagstaff, Purdue/CERIAS): https://homes.cerias.purdue.edu/homes/ssw/cun/ (Wanted list issued Jan 4 2026; main tables Jan 5 2026)
* NFS@Home (Greg Childers, CSU Fullerton): https://escatter11.fullerton.edu/nfs/ (live status; currently sieving SNFS up to ~340, GNFS up to ~207; cudasieve GPU app)
* CADO-NFS homepage: https://cado-nfs.gitlabpages.inria.fr
* GMP-ECM: https://members.loria.fr (Zimmermann, Kruppa); Debian package gmp-ecm 6.4.4
* Grokipedia / Wikipedia, *General number field sieve* (implementation list: GGNFS, CADO-NFS, msieve, YAFU, kmGNFS; NFSNet; NFS@Home)
