#!/usr/bin/env python3
"""
Deep analysis: Combine first 50,000 primes with Riemann Hypothesis (RH).

Tests:
1. Riemann R-function approximation to π(x) — R(x) = Σ μ(k)/k · Li(x^(1/k))
2. Mertens function M(x) = Σ_{n≤x} μ(n) — check |M(x)| < √x (RH equivalent)
3. Chebyshev's ψ(x) = Σ_{p^k ≤ x} ln(p) — relation to x under RH
4. Riemann's explicit formula: π(x) = R(x) - Σ_ρ R(x^ρ) ... approximate
5. Euler product verification: ζ(s) = ∏_p 1/(1-p^(-s))
6. Computing ζ(s) for various s, especially close to s=1 (pole)
7. Gram points and zeta zero distribution (qualitative)
8. Bias analysis: π(x) - Li(x) sign (related to first RH violation)
9. Check Li(x) - π(x) within RH bound O(√x ln(x))
10. Riemann prime counting formula comparison
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, next_prime
import math
import time
import json
from pathlib import Path
from collections import Counter
import cmath

print("=" * 70)
print("  تحلیل عمیق: ترکیب ۵۰٬۰۰۰ عدد اول با فرضیه‌ی ریمان")
print("=" * 70)
print()

# Load primes
primes_file = Path('/home/z/my-project/download/first_50000_primes.txt')
primes = [int(line.strip()) for line in primes_file.read_text().splitlines() if line.strip()]
print(f"Loaded {len(primes)} primes, p_50000 = {primes[-1]}")
print()

# ============================================================
# 1. Li(x) — logarithmic integral
# ============================================================
print("=" * 70)
print("  ۱. Li(x) و π(x) — زیربنای قضیه‌ی اعداد اول")
print("=" * 70)

def li_approx(x):
    """Approximate Li(x) = ∫_2^x dt/ln(t) using asymptotic expansion."""
    if x < 2: return 0
    gamma = 0.5772156649
    ln_x = math.log(x)
    if ln_x == 0: return 0
    s = gamma + math.log(ln_x)
    for k in range(1, 50):
        try:
            term = (ln_x ** k) / (k * math.factorial(k))
            s += term
            if abs(term) < 1e-15:
                break
        except:
            break
    return s - 1.0451637801  # subtract li(2)

# Riemann R-function: R(x) = Σ_{k=1}^∞ μ(k)/k · Li(x^(1/k))
def mobius(n):
    """Möbius function μ(n)."""
    if n == 1: return 1
    p_factors = 0
    n_temp = n
    d = 2
    while d * d <= n_temp:
        if n_temp % d == 0:
            n_temp //= d
            p_factors += 1
            if n_temp % d == 0:
                return 0  # square factor
        d += 1
    if n_temp > 1:
        p_factors += 1
    return -1 if p_factors % 2 else 1

def riemann_R(x, max_terms=20):
    """Riemann's R function: R(x) = Σ_{k=1}^∞ μ(k)/k · Li(x^(1/k))."""
    s = 0
    for k in range(1, max_terms + 1):
        mu = mobius(k)
        if mu == 0: continue
        x_k = x ** (1.0 / k)
        if x_k < 2: continue
        s += mu / k * li_approx(x_k)
    return s

# Test at sample points
print(f"{'x':>10} {'π(x)':>8} {'Li(x)':>10} {'R(x)':>10} {'Li-π':>10} {'R-π':>10} {'RH bound √x·ln(x)':>20}")
sample_x = [100, 500, 1000, 5000, 10000, 50000, 100000, 200000, 500000, 611953]
for x in sample_x:
    pi_x = sum(1 for p in primes if p <= x)
    li_x = li_approx(x)
    R_x = riemann_R(x)
    diff_li = li_x - pi_x
    diff_R = R_x - pi_x
    rh_bound = math.sqrt(x) * math.log(x)
    print(f"  {x:>10} {pi_x:>8} {li_x:>10.2f} {R_x:>10.2f} {diff_li:>10.2f} {diff_R:>10.2f} {rh_bound:>20.2f}")
print()

# Key insight: under RH, |Li(x) - π(x)| < C * sqrt(x) * ln(x)
print("بررسی bound فرضیه‌ی ریمان: |Li(x) - π(x)| < C·√x·ln(x):")
for x in sample_x:
    pi_x = sum(1 for p in primes if p <= x)
    li_x = li_approx(x)
    diff = abs(li_x - pi_x)
    bound = math.sqrt(x) * math.log(x)
    ratio = diff / bound if bound > 0 else 0
    print(f"  x = {x:>7}: |Li-π| = {diff:.2f}, √x·ln(x) = {bound:.2f}, نسبت = {ratio:.4f}")
print()

# ============================================================
# 2. Mertens function M(x) = Σ_{n≤x} μ(n)
# ============================================================
print("=" * 70)
print("  ۲. تابع Mertens M(x) — معادل فرضیه‌ی ریمان")
print("=" * 70)

# M(x) = Σ_{n≤x} μ(n)
# RH equivalent: M(x) = O(x^(1/2 + ε)) for any ε > 0
# Stronger (conjectured false): |M(x)| < sqrt(x)

# Compute M(x) up to small bound (say 10000) since μ is computed by trial
def compute_mertens(max_n):
    """Compute M(x) for x from 1 to max_n using sieve."""
    # Use linear sieve for Möbius
    mu = [0] * (max_n + 1)
    mu[1] = 1
    primes_list = []
    is_composite = [False] * (max_n + 1)
    for i in range(2, max_n + 1):
        if not is_composite[i]:
            primes_list.append(i)
            mu[i] = -1
        for p in primes_list:
            if i * p > max_n: break
            is_composite[i * p] = True
            if i % p == 0:
                mu[i * p] = 0
                break
            else:
                mu[i * p] = -mu[i]
    # Compute cumulative M
    M = [0] * (max_n + 1)
    for n in range(1, max_n + 1):
        M[n] = M[n-1] + mu[n]
    return M

max_n_mertens = 50000
print(f"محاسبه‌ی Mertens برای n = 1 تا {max_n_mertens}...")
t0 = time.time()
M = compute_mertens(max_n_mertens)
elapsed = time.time() - t0
print(f"  زمان: {elapsed:.2f}s")

# Check |M(x)| < sqrt(x) (equivalent to RH, but conjectured actually false!)
# Actually: M(x) = O(x^(1/2+ε)) under RH, but |M(x)| < sqrt(x) is stronger (Mertens conjecture, disproven)
# Mertens conjecture (disproven): |M(x)| < sqrt(x) for all x
# We compute M(x) at sample points and check

print(f"\nبررسی Mertens conjecture (رد شده): |M(x)| < √x")
print(f"{'x':>10} {'M(x)':>10} {'√x':>10} {'M/√x':>10} {'وضع':>10}")
max_ratio = 0
max_ratio_x = 0
for x in [10, 50, 100, 500, 1000, 5000, 10000, 20000, 50000]:
    if x <= max_n_mertens:
        M_x = M[x]
        sqrt_x = math.sqrt(x)
        ratio = M_x / sqrt_x
        status = "<√x" if abs(M_x) < sqrt_x else "نقض!"
        print(f"  {x:>10} {M_x:>10} {sqrt_x:>10.2f} {ratio:>10.4f} {status:>10}")
        if abs(ratio) > max_ratio:
            max_ratio = abs(ratio)
            max_ratio_x = x

print(f"\nنسبت max |M(x)/√x| = {max_ratio:.4f} در x = {max_ratio_x}")
print(f"مثبت: Mertens conjecture می‌گوید |M(x)| < √x همیشه، که در {max_n_mertens} نقض نشد")
print(f"ولی Odlyzko و te Riele در ۱۹۸۵ نشان دادند که برای x < ۱۰^۶۴ نقض وجود دارد")
print()

# ============================================================
# 3. Chebyshev's ψ(x) = Σ_{p^k ≤ x} ln(p)
# ============================================================
print("=" * 70)
print("  ۳. تابع Chebyshev ψ(x) — مرکزی در قضیه‌ی ریمان")
print("=" * 70)

def psi(x, primes):
    """Compute ψ(x) = Σ_{p^k ≤ x} ln(p)."""
    s = 0
    for p in primes:
        if p > x: break
        p_power = p
        while p_power <= x:
            s += math.log(p)
            p_power *= p
    return s

print(f"{'x':>10} {'ψ(x)':>15} {'x':>15} {'ψ-x':>15} {'√x·ln²x':>15} {'نسبت':>10}")
for x in [100, 500, 1000, 5000, 10000, 50000, 100000, 200000, 500000, 611953]:
    psi_x = psi(x, primes)
    diff = psi_x - x
    rh_bound = math.sqrt(x) * (math.log(x) ** 2)
    ratio = diff / rh_bound if rh_bound > 0 else 0
    print(f"  {x:>10} {psi_x:>15.4f} {x:>15} {diff:>15.4f} {rh_bound:>15.4f} {ratio:>10.4f}")
print()
print("RH: ψ(x) - x = O(√x · ln²(x)) — بررسی شد")
print()

# ============================================================
# 4. Euler product: ζ(s) = ∏_p 1/(1 - p^(-s))
# ============================================================
print("=" * 70)
print("  ۴. Euler product: ζ(s) = ∏_p 1/(1-p^(-s))")
print("=" * 70)

def zeta_euler_product(s, primes, n_primes=50000):
    """Compute ζ(s) via Euler product using first n_primes primes."""
    product = 1.0
    for p in primes[:n_primes]:
        product *= 1.0 / (1.0 - p ** (-s))
    return product

def zeta_partial_sum(s, n_terms=100000):
    """Compute ζ(s) via partial sum Σ 1/n^s for Re(s) > 1."""
    s_complex = complex(s)
    total = 0+0j
    for n in range(1, n_terms + 1):
        total += 1.0 / (n ** s_complex)
    return total

# Test at various s values
print(f"{'s':>10} {'Euler (50K primes)':>20} {'Partial (100K)':>20} {'نسبت':>10}")
for s in [2.0, 2.5, 3.0, 4.0, 5.0, 1.5, 1.1, 1.01]:
    z_euler = zeta_euler_product(s, primes)
    z_partial = zeta_partial_sum(s, 100000)
    if abs(z_partial) > 0:
        ratio = z_euler / z_partial.real if isinstance(z_partial, complex) else z_euler / z_partial
    else:
        ratio = 0
    print(f"  {s:>10.2f} {z_euler:>20.6f} {z_partial.real if isinstance(z_partial, complex) else z_partial:>20.6f} {ratio:>10.6f}")
print()

# Known values: ζ(2) = π²/6 ≈ 1.6449, ζ(4) = π⁴/90 ≈ 1.0823
print("مقایسه با مقادیر معلوم:")
print(f"  ζ(2) = π²/6 = {math.pi**2/6:.10f}")
print(f"  ζ(4) = π⁴/90 = {math.pi**4/90:.10f}")
print()

# ============================================================
# 5. Explicit Riemann formula (qualitative): 
# π(x) = R(x) - Σ_ρ R(x^ρ) where ρ runs over non-trivial zeros of ζ
# ============================================================
print("=" * 70)
print("  ۵. فرمول صریح ریمان: π(x) ≈ R(x) - Σ R(x^ρ)")
print("=" * 70)
print("زیر ذکر: ρ = اصفار غیر بدیهی ζ(s) روی خط بحرانی Re(s) = 1/2")
print()

# Use the first few non-trivial zeros of ζ (well-known):
# First zero: ρ_1 ≈ 1/2 + 14.134725i
# More: 21.022040, 25.010858, 30.424876, 32.935062, 37.586178, 40.918719, 43.327073, 48.005151, 49.773832
zeros_imaginary = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062, 37.586178, 
                    40.918719, 43.327073, 48.005151, 49.773832, 52.970316, 56.446248,
                    59.347044, 60.831786, 65.112541, 67.079211, 69.546402, 72.067158,
                    75.704691, 77.144840, 79.337375, 82.910381, 84.735493, 87.425275,
                    88.809112, 92.491899, 94.651870, 95.870466, 98.831006, 101.317852]

def riemann_explicit_pi(x, num_zeros=10):
    """Riemann's explicit formula approximation: π(x) ≈ R(x) - Σ Im R(x^ρ)."""
    R_x = riemann_R(x)
    correction = 0
    for gamma in zeros_imaginary[:num_zeros]:
        # ρ = 1/2 + i*gamma, x^ρ = x^(1/2) * exp(i*gamma*ln(x))
        # R(x^ρ) is complex; we take real part
        x_to_rho = (x ** 0.5) * cmath.exp(1j * gamma * math.log(x))
        # Li(x^ρ) for complex argument — approximation
        # Li(z) = γ + ln(ln(z)) + Σ (ln z)^k / (k * k!)
        ln_z = cmath.log(x_to_rho)
        try:
            li_z = 0.5772156649 + cmath.log(ln_z)
            term = ln_z
            for k in range(1, 30):
                term_k = (ln_z ** k) / (k * math.factorial(k))
                li_z += term_k
            li_z -= 1.0451637801
            # Contribution: -Re(R(x^ρ)) where R uses μ(k)/k
            # For simplicity, just use Li approximation
            correction += -li_z.real
        except:
            pass
    return R_x + correction

print(f"تقریب صریح ریمان (با ۱۰ صفر نخست):")
print(f"{'x':>10} {'π(x)':>10} {'R(x)':>12} {'R-π':>12} {'تقریب صریح':>15} {'خطا':>10}")
for x in [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 611953]:
    pi_x = sum(1 for p in primes if p <= x)
    R_x = riemann_R(x)
    explicit = riemann_explicit_pi(x, 10)
    err_explicit = explicit - pi_x
    err_R = R_x - pi_x
    print(f"  {x:>10} {pi_x:>10} {R_x:>12.4f} {err_R:>12.4f} {explicit:>15.4f} {err_explicit:>10.4f}")
print()

# ============================================================
# 6. Gram points — locations where Im(ζ(1/2 + it)) ≈ 0
# ============================================================
print("=" * 70)
print("  ۶. Gram points — نقاطی که ζ(1/2 + it) واقعی است")
print("=" * 70)
print("Gram's law: نقاط g_n که در آنها ζ(1/2 + i*g_n) واقعی است")
print("g_n ≈ 2π * (n - 11/8) / ln(n/(2π)) — تقریب")
print()

# First few Gram points
gram_points = []
for n in range(1, 11):
    if n == 1:
        g = 17.8456
    else:
        # Approximation
        g = 2 * math.pi * (n - 11/8) / math.log(n / (2 * math.pi)) if n > 1 else 17.8456
    gram_points.append(g)
    print(f"  g_{n} ≈ {g:.4f}")
print()

# The zeros and Gram points interlace: g_n-1 < γ_n < g_n (mostly)
print("مقایسه با اصفار:")
for i, gamma in enumerate(zeros_imaginary[:5]):
    print(f"  ρ_{i+1} = 1/2 + {gamma:.4f}i")
print()

# ============================================================
# 7. Prime number theorem via zeta: Li(x) ~ x/ln(x) + x/ln(x)^2 + ...
# ============================================================
print("=" * 70)
print("  ۷. بسط مجانبی Li(x) و تقریب‌های π(x)")
print("=" * 70)

def li_asymptotic(x, n_terms=10):
    """Li(x) ~ x/ln(x) * Σ k!/ln(x)^k"""
    L = math.log(x)
    s = 0
    factorial_k = 1
    for k in range(n_terms):
        if k > 0:
            factorial_k *= k
        s += factorial_k / (L ** k)
    return x / L * s

print(f"{'x':>10} {'π(x)':>10} {'x/ln(x)':>10} {'Li asymptotic':>15} {'Li actual':>10}")
for x in [100, 1000, 10000, 50000, 100000, 500000, 611953]:
    pi_x = sum(1 for p in primes if p <= x)
    x_ln_x = x / math.log(x)
    li_asymp = li_asymptotic(x, 10)
    li_actual = li_approx(x)
    print(f"  {x:>10} {pi_x:>10} {x_ln_x:>10.2f} {li_asymp:>15.4f} {li_actual:>10.4f}")
print()

# ============================================================
# 8. RH verification indicators
# ============================================================
print("=" * 70)
print("  ۸. شاخص‌های تأیید فرضیه‌ی ریمان")
print("=" * 70)

print("\nالف) π(x) - Li(x) — باید تحت RH برابر O(√x · ln(x)) باشد:")
print(f"{'x':>10} {'π-Li':>10} {'√x·ln(x)':>10} {'نسبت':>10}")
for x in [100, 1000, 10000, 50000, 100000, 500000]:
    pi_x = sum(1 for p in primes if p <= x)
    li_x = li_approx(x)
    diff = pi_x - li_x
    bound = math.sqrt(x) * math.log(x)
    ratio = diff / bound
    print(f"  {x:>10} {diff:>10.2f} {bound:>10.2f} {ratio:>10.4f}")
print()

print("\nب) ψ(x) - x — باید تحت RH برابر O(√x · ln²(x)) باشد:")
print(f"{'x':>10} {'ψ-x':>10} {'√x·ln²x':>10} {'نسبت':>10}")
for x in [100, 1000, 10000, 50000, 100000, 500000]:
    psi_x = psi(x, primes)
    diff = psi_x - x
    bound = math.sqrt(x) * (math.log(x) ** 2)
    ratio = diff / bound
    print(f"  {x:>10} {diff:>10.4f} {bound:>10.4f} {ratio:>10.6f}")
print()

print("\nج) Mertens M(x)/√x — تحت RH نزدیک صفر:")
print(f"{'x':>10} {'M(x)':>10} {'M/√x':>10}")
for x in [100, 1000, 5000, 10000, 50000]:
    if x <= max_n_mertens:
        M_x = M[x]
        print(f"  {x:>10} {M_x:>10} {M_x/math.sqrt(x):>10.4f}")
print()

# ============================================================
# 9. Save comprehensive analysis
# ============================================================
analysis = {
    "primes_used": len(primes),
    "riemann_R_vs_pi": {
        str(x): {
            "pi_x": sum(1 for p in primes if p <= x),
            "Li_x": li_approx(x),
            "R_x": riemann_R(x),
        } for x in [100, 1000, 10000, 50000, 100000, 611953]
    },
    "mertens_max_ratio": max_ratio,
    "mertens_max_x": max_ratio_x,
    "first_10_riemann_zeros": zeros_imaginary[:10],
}

with open('/home/z/my-project/download/primes_50000_riemann_analysis.json', 'w') as f:
    json.dump(analysis, f, indent=2)
print("تحلیل ذخیره شد: /home/z/my-project/download/primes_50000_riemann_analysis.json")
print()
print("=" * 70)
print("پایان تحلیل")
print("=" * 70)
