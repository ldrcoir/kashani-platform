import sys
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime
import time

def factor_with_rho(n, max_iter=300000):
    if n == 1: return []
    if n % 2 == 0:
        sub = factor_with_rho(n // 2, max_iter)
        return [2] + sub if sub != [None] else [2, None]
    if is_prime(n): return [int(n)]
    
    factors = []
    remaining = n
    p = 2
    while p * p <= remaining and p < 100000:
        while remaining % p == 0:
            factors.append(p)
            remaining //= p
        p += 1 if p == 2 else 2
    
    if remaining == 1: return sorted(factors)
    if is_prime(remaining):
        factors.append(int(remaining))
        return sorted(factors)
    
    while remaining > 1 and not is_prime(remaining):
        x = mpz(2); y = mpz(2); d = mpz(1)
        f = lambda x: (x*x + 1) % remaining
        for _ in range(max_iter):
            x = f(x); y = f(f(y))
            d = gmpy2.gcd(abs(x - y), remaining)
            if d != 1: break
        if d == remaining or d == 1:
            return sorted(factors) + [None]
        factors.append(int(d))
        remaining //= d
        while remaining % d == 0:
            factors.append(int(d))
            remaining //= d
    
    if remaining > 1:
        factors.append(int(remaining))
    return sorted(factors)

def is_factored(n, max_iter=300000):
    if n == 1: return True
    if is_prime(n): return True
    factors = factor_with_rho(n, max_iter)
    return None not in factors

print("=" * 80)
print("جستجوی بازه‌های قابل جبران — ۲۰۰ نمونه در هر ۱۰^k")
print("=" * 80)
print()
print(f"{'k':<5} {'Frontier':<14} {'Gaps':<10} {'% Gaps':<10} {'First Gap':<32} {'Time':<10}")
print(f"{'-'*5} {'-'*14} {'-'*10} {'-'*10} {'-'*32} {'-'*10}")

results = {}
for k in [23, 24, 25, 26, 27, 28, 29, 30]:
    start = 10 ** k
    frontier = 0
    gaps_count = 0
    first_gap = None
    gap_positions = []
    t0 = time.time()
    
    for i in range(200):
        n = start + i
        if is_prime(n) or is_factored(n):
            if i == 0 or frontier == i:
                frontier = i + 1
        else:
            gaps_count += 1
            if first_gap is None:
                first_gap = n
            gap_positions.append((i, n))
    
    pct = 100 * gaps_count / 200
    results[k] = (frontier, gaps_count, first_gap, gap_positions, time.time() - t0)
    fg_str = str(first_gap) if first_gap else 'none'
    print(f"{k:<5} {frontier:<14}/200 {gaps_count:<10} {pct:.1f}%    {fg_str[:30]:<32} {time.time()-t0:.1f}s")

print()
print("=" * 80)
print("نمونه شکست‌ها در هر بازه:")
print("=" * 80)
for k in [23, 24, 25, 26]:
    if k in results:
        frontier, gaps_count, first_gap, gap_positions, t = results[k]
        print(f"\n10^{k} ({gaps_count} شکست):")
        for pos, n in gap_positions[:10]:
            print(f"  position {pos}: {n}")
