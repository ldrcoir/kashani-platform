#!/usr/bin/env python3
"""
Visualize the Riemann hypothesis analysis results.
"""

import sys
sys.set_int_max_str_digits(1000000)

import math
import cmath
from pathlib import Path
from collections import Counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Load primes
primes_file = Path('/home/z/my-project/download/first_50000_primes.txt')
primes = [int(line.strip()) for line in primes_file.read_text().splitlines() if line.strip()]

# Functions
def li_approx(x):
    if x < 2: return 0
    gamma = 0.5772156649
    ln_x = math.log(x)
    if ln_x == 0: return 0
    s = gamma + math.log(ln_x)
    for k in range(1, 50):
        try:
            term = (ln_x ** k) / (k * math.factorial(k))
            s += term
            if abs(term) < 1e-15: break
        except: break
    return s - 1.0451637801

def mobius(n):
    if n == 1: return 1
    p_factors = 0
    n_temp = n
    d = 2
    while d * d <= n_temp:
        if n_temp % d == 0:
            n_temp //= d
            p_factors += 1
            if n_temp % d == 0: return 0
        d += 1
    if n_temp > 1: p_factors += 1
    return -1 if p_factors % 2 else 1

def riemann_R(x, max_terms=20):
    s = 0
    for k in range(1, max_terms + 1):
        mu = mobius(k)
        if mu == 0: continue
        x_k = x ** (1.0 / k)
        if x_k < 2: continue
        s += mu / k * li_approx(x_k)
    return s

def psi(x, primes):
    s = 0
    for p in primes:
        if p > x: break
        p_power = p
        while p_power <= x:
            s += math.log(p)
            p_power *= p
    return s

# Create figure
fig, axes = plt.subplots(3, 2, figsize=(15, 16), constrained_layout=True)
fig.suptitle('تحلیل فرضیه‌ی ریمان با ۵۰٬۰۰۰ عدد اول نخست', fontsize=18, fontweight='bold')

# Subplot 1: π(x) vs Li(x) vs R(x)
ax = axes[0, 0]
x_vals = list(range(10, 611954, 1000))
pi_vals = [sum(1 for p in primes if p <= x) for x in x_vals]
li_vals = [li_approx(x) for x in x_vals]
R_vals = [riemann_R(x) for x in x_vals]
ax.plot(x_vals, pi_vals, linewidth=2, color='#2E86AB', label='π(x) واقعی')
ax.plot(x_vals, li_vals, linewidth=1.5, color='#F18F01', linestyle='--', label='Li(x)')
ax.plot(x_vals, R_vals, linewidth=1.5, color='#A23B72', linestyle=':', label='R(x) ریمان')
ax.set_xlabel('x')
ax.set_ylabel('تعداد')
ax.set_title('π(x) در برابر Li(x) و R(x)')
ax.legend()
ax.grid(True, alpha=0.3)

# Subplot 2: π(x) - Li(x) deviation vs RH bound
ax = axes[0, 1]
diff_vals = [pi_vals[i] - li_vals[i] for i in range(len(x_vals))]
rh_bound = [math.sqrt(x) * math.log(x) for x in x_vals]
neg_rh_bound = [-b for b in rh_bound]
ax.plot(x_vals, diff_vals, linewidth=1.2, color='#C73E1D', label='π(x) - Li(x)')
ax.plot(x_vals, rh_bound, linewidth=1.0, color='green', linestyle='--', label='+√x·ln(x) (RH bound)')
ax.plot(x_vals, neg_rh_bound, linewidth=1.0, color='green', linestyle='--', label='-√x·ln(x)')
ax.set_xlabel('x')
ax.set_ylabel('اختلاف')
ax.set_title('π(x) - Li(x) در برابر RH bound')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Subplot 3: ψ(x) - x deviation
ax = axes[1, 0]
psi_vals = [psi(x, primes) for x in x_vals]
psi_diff = [psi_vals[i] - x_vals[i] for i in range(len(x_vals))]
psi_bound = [math.sqrt(x) * (math.log(x) ** 2) for x in x_vals]
ax.plot(x_vals, psi_diff, linewidth=1.2, color='#5C4D7D', label='ψ(x) - x')
ax.plot(x_vals, psi_bound, linewidth=1.0, color='orange', linestyle='--', label='+√x·ln²(x)')
ax.plot(x_vals, [-b for b in psi_bound], linewidth=1.0, color='orange', linestyle='--', label='-√x·ln²(x)')
ax.set_xlabel('x')
ax.set_ylabel('اختلاف')
ax.set_title('ψ(x) - x (تابع Chebyshev)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Subplot 4: Mertens M(x)
ax = axes[1, 1]
# Compute Mertens via linear sieve
max_n = 50000
mu_arr = [0] * (max_n + 1)
mu_arr[1] = 1
primes_for_sieve = []
is_composite = [False] * (max_n + 1)
for i in range(2, max_n + 1):
    if not is_composite[i]:
        primes_for_sieve.append(i)
        mu_arr[i] = -1
    for p in primes_for_sieve:
        if i * p > max_n: break
        is_composite[i * p] = True
        if i % p == 0:
            mu_arr[i * p] = 0
            break
        else:
            mu_arr[i * p] = -mu_arr[i]

M_vals = [0] * (max_n + 1)
for n in range(1, max_n + 1):
    M_vals[n] = M_vals[n-1] + mu_arr[n]

x_mertens = list(range(1, max_n + 1))  # 1 to 50000
sqrt_x = [math.sqrt(x) for x in x_mertens]
ax.plot(x_mertens, M_vals[1:max_n+1], linewidth=0.5, color='#3B1F2B', label='M(x)')
ax.plot(x_mertens, sqrt_x, linewidth=1.0, color='red', linestyle='--', label='+√x')
ax.plot(x_mertens, [-s for s in sqrt_x], linewidth=1.0, color='red', linestyle='--', label='-√x')
ax.set_xlabel('x')
ax.set_ylabel('M(x)')
ax.set_title('تابع Mertens M(x) در برابر ±√x')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Subplot 5: Euler product verification
ax = axes[2, 0]
def zeta_euler(s, primes_list, n_primes):
    p = 1.0
    for prime in primes_list[:n_primes]:
        p *= 1.0 / (1.0 - prime ** (-s))
    return p

def zeta_partial(s, n_terms):
    total = 0.0
    for n in range(1, n_terms + 1):
        total += 1.0 / (n ** s)
    return total

s_values = [1.1, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]
euler_vals = [zeta_euler(s, primes, 50000) for s in s_values]
partial_vals = [zeta_partial(s, 100000) for s in s_values]
ratios = [euler_vals[i] / partial_vals[i] for i in range(len(s_values))]

ax.semilogy(s_values, euler_vals, 'o-', linewidth=1.5, color='#2E86AB', label='Euler product (50K primes)')
ax.semilogy(s_values, partial_vals, 's--', linewidth=1.5, color='#F18F01', label='Partial sum (100K terms)')
ax.set_xlabel('s (Re(s) > 1)')
ax.set_ylabel('ζ(s)')
ax.set_title('ζ(s): Euler product در برابر partial sum')
ax.legend()
ax.grid(True, alpha=0.3)

# Subplot 6: Zeta zeros on critical line (conceptual)
ax = axes[2, 1]
# Draw critical strip
ax.axvline(x=0, color='black', linewidth=0.5)
ax.axvline(x=1, color='black', linewidth=0.5)
ax.axvline(x=0.5, color='red', linewidth=1.0, linestyle='--', label='خط بحرانی Re=1/2')

# Plot first 10 non-trivial zeros
zeros_imaginary = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062, 37.586178, 
                    40.918719, 43.327073, 48.005151, 49.773832, 52.970316, 56.446248,
                    59.347044, 60.831786, 65.112541, 67.079211, 69.546402, 72.067158,
                    75.704691, 77.144840]
for gamma in zeros_imaginary:
    ax.plot(0.5, gamma, 'bo', markersize=8)

ax.set_xlim(-0.5, 1.5)
ax.set_ylim(0, 80)
ax.set_xlabel('Re(s)')
ax.set_ylabel('Im(s)')
ax.set_title('۲۰ صفر نخست ζ روی خط بحرانی')
ax.legend()
ax.grid(True, alpha=0.3)

plt.savefig('/home/z/my-project/download/primes_50000_riemann.png', dpi=120, bbox_inches='tight')
plt.close()
print("Image saved: /home/z/my-project/download/primes_50000_riemann.png")
