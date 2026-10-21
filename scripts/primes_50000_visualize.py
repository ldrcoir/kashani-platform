#!/usr/bin/env python3
"""
Generate the first 50,000 prime numbers and visualize their shape/distribution.

Visualizations to create:
1. Prime number distribution: p_n vs n
2. Prime gaps: g_n = p_{n+1} - p_n vs n
3. Prime density histogram (primes per [x, x+1000] bucket)
4. Ulam spiral of first 50,000 primes
5. Logarithmic plot: log(p_n) vs log(n) — should be linear per PNT
6. Mod distribution: count of primes in each residue class mod small numbers
7. Quadratic residues visualization
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, next_prime
import math
import time
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Setup fonts (Persian/Farsi may not render in matplotlib; fall back to default)
try:
    fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
except Exception as e:
    print(f"Font setup warning: {e}")
plt.rcParams['axes.unicode_minus'] = False

print("=" * 70)
print("  تولید ۵۰٬۰۰۰ عدد اول نخست و رسم شکل آن‌ها")
print("=" * 70)
print()

# ============================================================
# Step 1: Generate first 50,000 primes
# ============================================================
print("مرحله ۱: تولید ۵۰٬۰۰۰ عدد اول...")
t0 = time.time()
primes = []
p = 2
while len(primes) < 50000:
    primes.append(p)
    p = int(next_prime(mpz(p)))
t1 = time.time()
print(f"  {len(primes)} عدد اول در {t1-t0:.2f}s")
print(f"  بزرگ‌ترین: {primes[-1]}")
print(f"  p_50000 = {primes[-1]}")
print(f"  طبق PNT: p_n ≈ n ln n, p_50000 ≈ 50000 * ln(50000) ≈ {50000 * math.log(50000):.0f}")
print()

# Save to file
output_dir = Path('/home/z/my-project/download')
primes_file = output_dir / 'first_50000_primes.txt'
with open(primes_file, 'w') as f:
    for p in primes:
        f.write(f'{p}\n')
print(f"  ذخیره شد: {primes_file}")
print()

# ============================================================
# Step 2: Compute statistics
# ============================================================
print("مرحله ۲: محاسبه‌ی آمار...")
gaps = [primes[i+1] - primes[i] for i in range(len(primes)-1)]
n_values = list(range(1, len(primes)+1))

# Mod distribution
mod_counts = {m: {r: 0 for r in range(m)} for m in [3, 5, 7, 11, 13]}
for p in primes:
    for m in mod_counts:
        mod_counts[m][p % m] += 1

# Density
print(f"  آمار:")
print(f"    کوچک‌ترین: {primes[0]}")
print(f"    بزرگ‌ترین: {primes[-1]}")
print(f"    میانگین gap: {sum(gaps)/len(gaps):.2f}")
print(f"    بزرگ‌ترین gap: {max(gaps)} (بین {primes[gaps.index(max(gaps))]} و {primes[gaps.index(max(gaps))+1]})")
print(f"    کوچک‌ترین gap: {min(gaps)}")
print()

# ============================================================
# Step 3: Create visualizations
# ============================================================
print("مرحله ۳: رسم شکل‌ها...")

# Plot 1: p_n vs n (linear scale)
fig, axes = plt.subplots(2, 2, figsize=(15, 12), constrained_layout=True)
fig.suptitle('۵۰٬۰۰۰ عدد اول نخست — شکل و توزیع', fontsize=16, fontweight='bold')

# Subplot 1: p_n vs n
ax1 = axes[0, 0]
ax1.plot(n_values, primes, linewidth=0.5, color='#2E86AB')
ax1.set_xlabel('n (شماره‌ی عدد اول)')
ax1.set_ylabel('p_n (مقدار)')
ax1.set_title('رشد اعداد اول: p_n بر حسب n')
ax1.grid(True, alpha=0.3)

# Subplot 2: log-log plot (PNT verification)
ax2 = axes[0, 1]
log_n = [math.log(n) for n in n_values if n > 1]
log_p = [math.log(p) for p in primes[1:]]
ax2.plot(log_n, log_p, linewidth=0.5, color='#A23B72')
# PNT line: log(p_n) ≈ log(n) + log(log(n))
pnt_line = [ln + math.log(ln) for ln in log_n]
ax2.plot(log_n, pnt_line, linewidth=1.5, color='#F18F01', linestyle='--', label='PNT: ln(n) + ln(ln(n))')
ax2.set_xlabel('ln(n)')
ax2.set_ylabel('ln(p_n)')
ax2.set_title('قضیه‌ی اعداد اول (PNT) — خط تقریب')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Subplot 3: Prime gaps
ax3 = axes[1, 0]
ax3.plot(range(len(gaps)), gaps, linewidth=0.3, color='#C73E1D', alpha=0.7)
ax3.set_xlabel('n')
ax3.set_ylabel('gap = p_{n+1} - p_n')
ax3.set_title('فاصله‌های بین اعداد اول متوالی')
ax3.grid(True, alpha=0.3)

# Subplot 4: Density histogram
ax4 = axes[1, 1]
bucket_size = max(1, (primes[-1] - primes[0]) // 100)
buckets = [0] * 100
for p in primes:
    idx = min(99, (p - primes[0]) // bucket_size)
    buckets[idx] += 1
ax4.bar(range(100), buckets, color='#3B1F2B', alpha=0.7)
ax4.set_xlabel(f'بازه‌ی [{primes[0]}, {primes[-1]}] تقسیم به ۱۰۰ قسمت')
ax4.set_ylabel('تعداد اعداد اول')
ax4.set_title('تراکم اعداد اول در بازه‌ها')
ax4.grid(True, alpha=0.3)

plt.savefig('/home/z/my-project/download/primes_50000_main.png', dpi=120, bbox_inches='tight')
plt.close()
print("  شکل ۱: primes_50000_main.png")

# Plot 2: Ulam Spiral
fig, axes = plt.subplots(1, 2, figsize=(15, 7), constrained_layout=True)
fig.suptitle('مارپیچ اولام و توزیع مودی', fontsize=16, fontweight='bold')

# Subplot 1: Ulam spiral
ax1 = axes[0]
# Place first N primes on Ulam spiral
# Spiral position: start at origin, go right 1, up 1, left 2, down 2, right 3, up 3, ...
primes_set = set(primes)
N_ulam = primes[-1]  # all primes up to this number
# Generate Ulam spiral coordinates for numbers 1 to N_ulam
# But that's 611953, which is too many points.
# Use only first 50000 numbers and mark which are prime
N_ulam = 50000
positions = {}
x, y = 0, 0
dx, dy = 1, 0
steps_in_dir = 1
step_count = 0
turn_count = 0
prime_xs, prime_ys = [], []
for n in range(1, N_ulam + 1):
    if n in primes_set:
        prime_xs.append(x)
        prime_ys.append(y)
    x += dx
    y += dy
    step_count += 1
    if step_count == steps_in_dir:
        # turn left
        dx, dy = -dy, dx
        step_count = 0
        turn_count += 1
        if turn_count % 2 == 0:
            steps_in_dir += 1

ax1.scatter(prime_xs, prime_ys, s=0.3, color='#2E86AB', alpha=0.7)
ax1.set_aspect('equal')
ax1.set_title(f'مارپیچ اولام — اعداد اول تا {N_ulam}')
ax1.grid(True, alpha=0.3)

# Subplot 2: Mod distribution
ax2 = axes[1]
mods_to_show = [3, 5, 7, 11]
data_for_plot = []
labels_for_plot = []
for m in mods_to_show:
    counts = [mod_counts[m][r] for r in range(m)]
    data_for_plot.append(counts)
    labels_for_plot.append(f'mod {m}')

x_positions = range(max(mods_to_show))
width = 0.2
for i, m in enumerate(mods_to_show):
    ax2.bar([r + i*width - 1.5*width for r in range(m)], 
            data_for_plot[i], 
            width=width, 
            label=f'mod {m}', 
            alpha=0.7)
ax2.set_xlabel('باقی‌مانده')
ax2.set_ylabel('تعداد')
ax2.set_title('توزیع اعداد اول بر حسب باقی‌مانده')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.savefig('/home/z/my-project/download/primes_50000_ulam_mod.png', dpi=120, bbox_inches='tight')
plt.close()
print("  شکل ۲: primes_50000_ulam_mod.png")

# Plot 3: Gap distribution histogram + zoomed view
fig, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)
fig.suptitle('تحلیل gap های اعداد اول', fontsize=16, fontweight='bold')

# Subplot 1: Gap histogram
ax1 = axes[0, 0]
ax1.hist(gaps, bins=80, color='#5C4D7D', alpha=0.7, edgecolor='black')
ax1.set_xlabel('gap')
ax1.set_ylabel('تعداد')
ax1.set_title('هیستوگرام gap های بین اعداد اول')
ax1.grid(True, alpha=0.3)

# Subplot 2: Gap vs n (zoomed to first 5000)
ax2 = axes[0, 1]
ax2.plot(range(5000), gaps[:5000], linewidth=0.5, color='#C73E1D', alpha=0.7)
ax2.set_xlabel('n (first 5000)')
ax2.set_ylabel('gap')
ax2.set_title('gap برای ۵۰۰۰ عدد اول نخست')
ax2.grid(True, alpha=0.3)

# Subplot 3: Cumulative prime count vs n
ax3 = axes[1, 0]
cum_primes = list(range(1, len(primes)+1))
ax3.plot(primes, cum_primes, linewidth=0.8, color='#2E86AB')
ax3.set_xlabel('x (محدوده‌ی اعداد)')
ax3.set_ylabel('π(x) = تعداد اعداد اول ≤ x')
ax3.set_title('تابع شمارش اعداد اول π(x)')
ax3.grid(True, alpha=0.3)

# Subplot 4: p_n vs n*log(n) (PNT visualization)
ax4 = axes[1, 1]
pnt_estimate = [n * math.log(n) if n > 1 else 0 for n in n_values]
ax4.plot(n_values, primes, linewidth=1.5, color='#2E86AB', label='p_n واقعی')
ax4.plot(n_values, pnt_estimate, linewidth=1.5, color='#F18F01', linestyle='--', label='n ln(n) (PNT)')
ax4.set_xlabel('n')
ax4.set_ylabel('مقدار')
ax4.set_title('p_n در برابر تقریب PNT')
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.savefig('/home/z/my-project/download/primes_50000_gaps.png', dpi=120, bbox_inches='tight')
plt.close()
print("  شکل ۳: primes_50000_gaps.png")

# Plot 4: Special visualizations — polar prime spiral and prime race
fig, axes = plt.subplots(1, 2, figsize=(15, 7), constrained_layout=True)
fig.suptitle('مارپیچ قطبی اعداد اول و Prime Race', fontsize=16, fontweight='bold')

# Subplot 1: Polar prime spiral — each prime p at angle p, radius sqrt(p)
ax1 = axes[0]
ax1.remove()
ax1 = fig.add_subplot(121, projection='polar')
angles = [p for p in primes[:5000]]  # use first 5000 primes
radii = [math.sqrt(p) for p in primes[:5000]]
ax1.scatter(angles, radii, s=0.5, color='#A23B72', alpha=0.5)
ax1.set_title('مارپیچ قطبی اعداد اول (اولین ۵۰۰۰ عدد)', pad=20)

# Subplot 2: Prime race — mod 4 race
ax2 = axes[1]
primes_mod1 = []  # primes ≡ 1 mod 4
primes_mod3 = []  # primes ≡ 3 mod 4
count_1 = 0
count_3 = 0
lead_history = []
for i, p in enumerate(primes):
    if p > 2:
        if p % 4 == 1:
            count_1 += 1
        elif p % 4 == 3:
            count_3 += 1
    lead_history.append(count_1 - count_3)

ax2.plot(range(len(lead_history)), lead_history, linewidth=0.8, color='#C73E1D')
ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
ax2.set_xlabel('n (تعداد اعداد اول پردازش‌شده)')
ax2.set_ylabel('π(1 mod 4) - π(3 mod 4)')
ax2.set_title('Prime Race: 1 mod 4 در برابر 3 mod 4')
ax2.grid(True, alpha=0.3)

plt.savefig('/home/z/my-project/download/primes_50000_special.png', dpi=120, bbox_inches='tight')
plt.close()
print("  شکل ۴: primes_50000_special.png")

# ============================================================
# Save statistics
# ============================================================
stats = {
    "count": len(primes),
    "first_prime": primes[0],
    "last_prime": primes[-1],
    "average_gap": sum(gaps) / len(gaps),
    "max_gap": max(gaps),
    "min_gap": min(gaps),
    "mod_distribution": {str(m): {str(r): mod_counts[m][r] for r in mod_counts[m]} for m in mod_counts},
    "pnt_estimate_at_50000": 50000 * math.log(50000),
    "actual_p_50000": primes[-1],
}

stats_file = output_dir / 'primes_50000_stats.json'
with open(stats_file, 'w') as f:
    json.dump(stats, f, indent=2)
print(f"\nآمار ذخیره شد: {stats_file}")
print()

# Print summary
print("=" * 70)
print("خلاصه")
print("=" * 70)
print(f"  تعداد اعداد اول تولید‌شده: {len(primes):,}")
print(f"  p_1 = {primes[0]}")
print(f"  p_10 = {primes[9]}")
print(f"  p_100 = {primes[99]}")
print(f"  p_1000 = {primes[999]}")
print(f"  p_10000 = {primes[9999]}")
print(f"  p_50000 = {primes[-1]}")
print(f"  میانگین gap: {sum(gaps)/len(gaps):.2f}")
print(f"  بزرگ‌ترین gap: {max(gaps)} (بین p_{gaps.index(max(gaps))+1}={primes[gaps.index(max(gaps))]} و p_{gaps.index(max(gaps))+2}={primes[gaps.index(max(gaps))+1]})")
print()
print("شکل‌های تولیدشده:")
print("  1. primes_50000_main.png — شکل اصلی (۴ نمودار)")
print("  2. primes_50000_ulam_mod.png — مارپیچ اولام و توزیع mod")
print("  3. primes_50000_gaps.png — تحلیل gap ها")
print("  4. primes_50000_special.png — مارپیچ قطبی و Prime Race")
print()
print(f"فایل اعداد اول: download/first_50000_primes.txt")
print(f"آمار: download/primes_50000_stats.json")
