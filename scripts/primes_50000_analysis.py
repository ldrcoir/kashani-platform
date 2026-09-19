#!/usr/bin/env python3
"""
Deep statistical analysis of the first 50,000 primes.

Tests to perform:
1. PNT verification — fit p_n vs n*ln(n) and measure deviation
2. Gap distribution — fit to exponential decay, check twin prime density
3. Mod 6 distribution — all primes > 3 are ±1 mod 6
4. Mod 30 distribution — primes avoid residues divisible by 2,3,5
5. Twin prime counting — π_2(x) and conjectural fit
6. Cramér-Granville conjecture test — max gap vs (ln p_n)^2
7. Prime k-tuples density (triplets, quadruplets)
8. Bertrand's postulate verification
9. Prime number race (mod 4, mod 3)
10. Chebyshev's bias
11. Riemann Hypothesis indicator — π(x) vs Li(x)
12. Ulam spiral diagonal analysis — density on major diagonals
13. Distribution of last digits (mod 10)
14. Repunit-like checks
15. Additive energy / additive combinatorics
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, next_prime
import math
import time
import json
from pathlib import Path
from collections import Counter, defaultdict

print("=" * 70)
print("  تحلیل عمیق آماری ۵۰٬۰۰۰ عدد اول نخست")
print("=" * 70)
print()

# Load primes from file
primes_file = Path('/home/z/my-project/download/first_50000_primes.txt')
primes = [int(line.strip()) for line in primes_file.read_text().splitlines() if line.strip()]
print(f"تعداد: {len(primes)}")
print(f"p_1 = {primes[0]}, p_50000 = {primes[-1]}")
print()

# ============================================================
# Analysis 1: PNT verification — p_n vs n*ln(n)
# ============================================================
print("=" * 70)
print("  ۱. بررسی قضیه‌ی اعداد اول (PNT)")
print("=" * 70)

# PNT: p_n ~ n * ln(n) as n → ∞
# Better approximation: p_n ~ n * (ln(n) + ln(ln(n)) - 1)
# Even better: p_n ~ n * (ln(n) + ln(ln(n)) - 1 + (ln(ln(n)) - 2)/ln(n))

n_values = list(range(1, len(primes)+1))
pnt_simple = [n * math.log(n) if n > 1 else 0 for n in n_values]
pnt_better = [n * (math.log(n) + math.log(math.log(n)) - 1) if n > 2 else 0 for n in n_values]
pnt_best = [n * (math.log(n) + math.log(math.log(n)) - 1 + (math.log(math.log(n)) - 2)/math.log(n)) if n > 2 else 0 for n in n_values]

# Compute relative errors
rel_errors_simple = [abs(primes[i] - pnt_simple[i]) / primes[i] for i in range(2, len(primes))]
rel_errors_better = [abs(primes[i] - pnt_better[i]) / primes[i] for i in range(2, len(primes))]
rel_errors_best = [abs(primes[i] - pnt_best[i]) / primes[i] for i in range(2, len(primes))]

print(f"خطای نسبی تقریب PNT (در p_50000):")
print(f"  ساده:       n*ln(n)                              : {rel_errors_simple[-1]*100:.4f}%")
print(f"  بهتر:       n*(ln(n) + ln(ln(n)) - 1)            : {rel_errors_better[-1]*100:.4f}%")
print(f"  بهترین:     n*(ln(n) + ln(ln(n)) - 1 + ...)       : {rel_errors_best[-1]*100:.4f}%")
print(f"  واقعی:      p_50000 = {primes[-1]}")
print(f"  تقریب ساده: {pnt_simple[-1]:.0f}")
print(f"  تقریب بهتر: {pnt_better[-1]:.0f}")
print()

# Riemann Hypothesis indicator: π(x) vs Li(x)
print(f"شاخص فرضیه‌ی ریمان: π(x) در برابر Li(x) = ∫_2^x dt/ln(t)")
# Compute Li(x) using asymptotic series
def li_approx(x):
    """Approximate Li(x) = ∫_2^x dt/ln(t) using asymptotic expansion."""
    if x < 2: return 0
    gamma = 0.5772156649  # Euler-Mascheroni
    ln_x = math.log(x)
    # Li(x) = li(x) - li(2) where li(x) ~ gamma + ln(ln(x)) + sum_{k=1}^∞ (ln(x))^k / (k * k!)
    s = gamma + math.log(ln_x)
    term = ln_x
    for k in range(1, 30):
        term_k = (ln_x ** k) / (k * math.factorial(k))
        s += term_k
    # Subtract li(2) ≈ 1.0451
    return s - 1.0451637801

# Compute π(x) at sample points and compare to Li(x)
sample_points = [100, 1000, 10000, 50000, 100000, 200000, 500000, 611953]
print(f"  {'x':>10} {'π(x)':>8} {'Li(x)':>10} {'π-Li':>10} {'نسبت':>10}")
for x in sample_points:
    # Count primes <= x
    pi_x = sum(1 for p in primes if p <= x)
    li_x = li_approx(x)
    diff = pi_x - li_x
    ratio = pi_x / li_x if li_x > 0 else 0
    print(f"  {x:>10} {pi_x:>8} {li_x:>10.2f} {diff:>10} {ratio:>10.6f}")
print()

# ============================================================
# Analysis 2: Gap distribution
# ============================================================
print("=" * 70)
print("  ۲. تحلیل توزیع gap")
print("=" * 70)

gaps = [primes[i+1] - primes[i] for i in range(len(primes)-1)]
gap_counter = Counter(gaps)

print(f"میانگین gap: {sum(gaps)/len(gaps):.4f}")
print(f"میانه‌ی gap: {sorted(gaps)[len(gaps)//2]}")
print(f"بزرگ‌ترین gap: {max(gaps)} (بین {primes[gaps.index(max(gaps))]} و {primes[gaps.index(max(gaps))+1]})")
print()

# Top 10 most common gaps
print("۱۰ gap پرتکرارترین:")
for gap, count in gap_counter.most_common(10):
    pct = count / len(gaps) * 100
    print(f"  gap = {gap}: {count} بار ({pct:.2f}%)")
print()

# Twin prime density
twin_prime_count = sum(1 for g in gaps if g == 2)
twin_prime_pairs = []
for i in range(len(primes)-1):
    if primes[i+1] - primes[i] == 2:
        twin_prime_pairs.append((primes[i], primes[i+1]))

print(f"اعداد اول دوقلو (gap = 2): {twin_prime_count} جفت")
print(f"نسبت: {twin_prime_count/len(gaps)*100:.2f}% از gap ها")
print(f"طبق حدس Hardy-Littlewood: π_2(x) ~ 2*C_2 * x / ln(x)^2")
print(f"  C_2 = 0.6601618... (تwin prime constant)")
C2 = 0.6601618158
x_max = primes[-1]
predicted_twin = 2 * C2 * x_max / (math.log(x_max) ** 2)
print(f"  پیش‌بینی برای x = {x_max}: {predicted_twin:.0f} جفت")
print(f"  واقعی: {twin_prime_count} جفت")
print(f"  نسبت: {twin_prime_count / predicted_twin:.4f}")
print()

# Cousin primes (gap = 4)
cousin_count = sum(1 for g in gaps if g == 4)
print(f"اعداد اول پسرعمو (gap = 4): {cousin_count} جفت")
# Sexy primes (gap = 6)
sexy_count = sum(1 for g in gaps if g == 6)
print(f"اعداد اول سکسی (gap = 6): {sexy_count} جفت")
print()

# Cramér-Granville conjecture: max gap ~ (ln p_n)^2
# Cramér conjectured: max gap in [1, x] ~ ln(x)^2
# Granville修正: max gap ~ 2*e^(-gamma) * ln(x)^2 ≈ 1.12 * ln(x)^2
x = primes[-1]
cramer_pred = math.log(x) ** 2
granville_factor = 2 * math.e ** (-0.5772156649)
granville_pred = granville_factor * math.log(x) ** 2
print(f"حدس Cramér: max gap در [1, {x}] ≈ ln(x)^2 = {cramer_pred:.2f}")
print(f"حدس Granville: max gap ≈ 2*e^(-γ)*ln(x)^2 = {granville_pred:.2f}")
print(f"واقعی: {max(gaps)}")
print()

# ============================================================
# Analysis 3: Distribution mod small numbers
# ============================================================
print("=" * 70)
print("  ۳. توزیع بر حسب باقی‌مانده‌ها")
print("=" * 70)

# Mod 6: primes > 3 should be 1 or 5 mod 6
primes_mod_6 = Counter(p % 6 for p in primes if p > 3)
print("primes > 3 بر حسب mod 6:")
for r in [1, 5]:
    print(f"  mod 6 = {r}: {primes_mod_6[r]} ({primes_mod_6[r]/sum(primes_mod_6.values())*100:.2f}%)")
print()

# Mod 30: primes > 5 should be in {1, 7, 11, 13, 17, 19, 23, 29}
primes_mod_30 = Counter(p % 30 for p in primes if p > 5)
print("primes > 5 بر حسب mod 30 (۸ باقی‌مانده‌ی ممکن):")
for r in [1, 7, 11, 13, 17, 19, 23, 29]:
    print(f"  mod 30 = {r}: {primes_mod_30[r]} ({primes_mod_30[r]/sum(primes_mod_30.values())*100:.2f}%)")
print()

# Mod 210: primes > 7 should be in {1, 11, 13, ...} - 48 residues
primes_mod_210 = Counter(p % 210 for p in primes if p > 7)
total = sum(primes_mod_210.values())
print(f"primes > 7 بر حسب mod 210 (48 باقی‌مانده‌ی ممکن):")
print(f"  total: {total}")
print(f"  توزیع یکنواخت انتظار: {total/48:.0f} هر کلاسه")
# Chi-squared test
expected_per_class = total / 48
chi_sq = sum((primes_mod_210[r] - expected_per_class)**2 / expected_per_class for r in primes_mod_210)
print(f"  Chi-squared: {chi_sq:.2f} (با df=47، انتظار ~47)")
print()

# ============================================================
# Analysis 4: Prime number race
# ============================================================
print("=" * 70)
print("  ۴. Prime Race (Chebyshev's bias)")
print("=" * 70)

# Mod 4: primes > 2 are 1 or 3 mod 4
# Chebyshev observed: primes 3 mod 4 lead most of the time
count_1_mod4 = 0
count_3_mod4 = 0
lead_history = []
for p in primes:
    if p > 2:
        if p % 4 == 1:
            count_1_mod4 += 1
        elif p % 4 == 3:
            count_3_mod4 += 1
    lead_history.append(count_1_mod4 - count_3_mod4)

print(f"Mod 4:")
print(f"  1 mod 4: {count_1_mod4} ({count_1_mod4/sum(1 for p in primes if p>2)*100:.2f}%)")
print(f"  3 mod 4: {count_3_mod4} ({count_3_mod4/sum(1 for p in primes if p>2)*100:.2f}%)")
print(f"  اختلاف (1 mod 4 - 3 mod 4): {count_1_mod4 - count_3_mod4}")
print(f"  بیشترین preponderance: 3 mod 4 lead by {min(lead_history)}")
print(f"  پیشتازی‌های 3 mod 4: {sum(1 for x in lead_history if x < 0)} از {len(lead_history)}")
print()

# Mod 3 race
count_1_mod3 = 0
count_2_mod3 = 0
for p in primes:
    if p > 3:
        if p % 3 == 1:
            count_1_mod3 += 1
        elif p % 3 == 2:
            count_2_mod3 += 1
print(f"Mod 3:")
print(f"  1 mod 3: {count_1_mod3} ({count_1_mod3/(count_1_mod3+count_2_mod3)*100:.2f}%)")
print(f"  2 mod 3: {count_2_mod3} ({count_2_mod3/(count_1_mod3+count_2_mod3)*100:.2f}%)")
print()

# ============================================================
# Analysis 5: Bertrand's postulate
# ============================================================
print("=" * 70)
print("  ۵. بررسی postulate Bertrand")
print("=" * 70)
print("حدس Bertrand: برای هر n > 1، حداقل یک عدد اول بین n و 2n وجود دارد.")

# Check for n = each prime in our list (well, first 100)
bertrand_violations = 0
for i, p in enumerate(primes[:100]):
    next_prime_idx = i + 1
    # Find smallest prime > p
    found = False
    for j in range(i+1, len(primes)):
        if primes[j] <= 2 * p:
            found = True
            break
        else:
            break
    if not found:
        bertrand_violations += 1
        print(f"  نقض در p = {p}")

print(f"بررسی برای ۱۰۰ عدد اول نخست: {bertrand_violations} نقض")
print()

# ============================================================
# Analysis 6: Additive combinatorics — additive energy
# ============================================================
print("=" * 70)
print("  ۶. انرژی جمعی (Additive energy)")
print("=" * 70)

# Count pairs (a, b) with a + b = c + d, where a, b, c, d are primes (using first 100 primes for speed)
sample_primes = primes[:100]
sums = Counter()
for i, a in enumerate(sample_primes):
    for b in sample_primes[i:]:
        sums[a + b] += 1

# Additive energy = sum of count^2 over all sums
additive_energy = sum(c**2 for c in sums.values())
print(f"برای ۱۰۰ عدد اول نخست:")
print(f"  تعداد جمع‌های یکتا (a + b, a ≤ b): {len(sums)}")
print(f"  انرژی جمعی E(A): {additive_energy}")
print(f"  انتظار برای مجموعه‌ی random: ~2*N^2 = {2*100*100}")
print(f"  نسبت: {additive_energy / (2*100*100):.4f}")
print()

# ============================================================
# Analysis 7: Last digit distribution (mod 10)
# ============================================================
print("=" * 70)
print("  ۷. توزیع رقم آخر (mod 10)")
print("=" * 70)

last_digit = Counter(p % 10 for p in primes if p > 5)
print("primes > 5 بر حسب رقم آخر:")
for d in [1, 3, 7, 9]:
    count = last_digit[d]
    print(f"  آخرین رقم {d}: {count} ({count/sum(last_digit.values())*100:.2f}%)")
print()

# ============================================================
# Analysis 8: Ulam spiral diagonal density
# ============================================================
print("=" * 70)
print("  ۸. مارپیچ اولام — تراکم روی قطرها")
print("=" * 70)

# Generate Ulam spiral for primes <= 50000
primes_set = set(primes)
N_ulam = 50000
spiral = {}
x, y = 0, 0
dx, dy = 1, 0
steps_in_dir = 1
step_count = 0
turn_count = 0
for n in range(1, N_ulam + 1):
    if n in primes_set:
        spiral[n] = (x, y)
    x += dx
    y += dy
    step_count += 1
    if step_count == steps_in_dir:
        dx, dy = -dy, dx
        step_count = 0
        turn_count += 1
        if turn_count % 2 == 0:
            steps_in_dir += 1

# Count primes on major diagonals
# Diagonal directions: y = x, y = -x, y = 0, x = 0
on_diag_yx = sum(1 for p, (px, py) in spiral.items() if px == py and px != 0)
on_diag_y_neg_x = sum(1 for p, (px, py) in spiral.items() if px == -py and px != 0)
on_diag_x0 = sum(1 for p, (px, py) in spiral.items() if px == 0 and py != 0)
on_diag_y0 = sum(1 for p, (px, py) in spiral.items() if py == 0 and px != 0)

total_primes_ulam = len(spiral)
print(f"تعداد اعداد اول در مارپیچ اولام (N = {N_ulam}): {total_primes_ulam}")
print(f"  روی قطر y = x: {on_diag_yx}")
print(f"  روی قطر y = -x: {on_diag_y_neg_x}")
print(f"  روی محور x (y = 0): {on_diag_x0}")
print(f"  روی محور y (x = 0): {on_diag_y0}")
print()

# ============================================================
# Analysis 9: Prime triplets and quadruplets
# ============================================================
print("=" * 70)
print("  ۹. اعداد سه‌گانه و چهارگانه‌ی اول")
print("=" * 70)

# Prime triplet: (p, p+2, p+6) or (p, p+4, p+6)
triplet_count = 0
for i in range(len(primes) - 2):
    if primes[i+2] - primes[i] == 6 and (primes[i+1] - primes[i] == 2 or primes[i+1] - primes[i] == 4):
        triplet_count += 1

# Prime quadruplet: (p, p+2, p+6, p+8)
quadruplet_count = 0
for i in range(len(primes) - 3):
    if primes[i+3] - primes[i] == 8 and primes[i+1] - primes[i] == 2 and primes[i+2] - primes[i] == 6:
        quadruplet_count += 1

print(f"اعداد سه‌گانه‌ی اول (p, p+2, p+6) یا (p, p+4, p+6): {triplet_count}")
print(f"اعداد چهارگانه‌ی اول (p, p+2, p+6, p+8): {quadruplet_count}")
print()

# ============================================================
# Analysis 10: Sum of first N primes
# ============================================================
print("=" * 70)
print("  ۱۰. مجموع اعداد اول نخست")
print("=" * 70)

for n in [10, 100, 1000, 10000, 50000]:
    s = sum(primes[:n])
    # Asymptotic: sum of first n primes ~ n^2 * ln(n) / 2
    predicted = (n ** 2) * math.log(n) / 2
    print(f"  sum(p_1..p_{n}) = {s}, پیش‌بینی ~ n^2 ln(n)/2 = {predicted:.0f}")
print()

# Save analysis results
analysis = {
    "count": len(primes),
    "pnt_errors": {
        "simple_at_50000": rel_errors_simple[-1],
        "better_at_50000": rel_errors_better[-1],
        "best_at_50000": rel_errors_best[-1],
    },
    "gaps": {
        "average": sum(gaps)/len(gaps),
        "median": sorted(gaps)[len(gaps)//2],
        "max": max(gaps),
        "twin_prime_count": twin_prime_count,
        "cousin_count": cousin_count,
        "sexy_count": sexy_count,
    },
    "mod_distribution": {
        "mod_6": dict(primes_mod_6),
        "mod_30": dict(primes_mod_30),
    },
    "prime_race": {
        "mod4_count_1": count_1_mod4,
        "mod4_count_3": count_3_mod4,
        "mod3_count_1": count_1_mod3,
        "mod3_count_2": count_2_mod3,
    },
    "ulam_diagonals": {
        "y_equals_x": on_diag_yx,
        "y_equals_neg_x": on_diag_y_neg_x,
        "x_axis": on_diag_x0,
        "y_axis": on_diag_y0,
    },
    "triplets": triplet_count,
    "quadruplets": quadruplet_count,
}

with open('/home/z/my-project/download/primes_50000_analysis.json', 'w') as f:
    json.dump(analysis, f, indent=2)
print()
print("تحلیل ذخیره شد: /home/z/my-project/download/primes_50000_analysis.json")
