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

print("=" * 70)
print("۱) Frontier اعداد اول پیوسته")
print("=" * 70)
print()
print("توجه: اعداد اول تا مرزهای بسیار بزرگ محاسبه‌شده‌اند (OEIS A003869)")
print("ولی ما اینجا با محاسبه‌ی محلی تست می‌کنیم:")
print()
print(f"{'Range':<25} {'Last Prime (local)':<25} {'Note'}")
print(f"{'-'*25} {'-'*25} {'-'*40}")

t0 = time.time()
# 1 to 1000
last_prime = 0
for n in range(2, 1001):
    if is_prime(n):
        last_prime = n
print(f"{'1 to 1,000':<25} {last_prime:<25} {'(' + str(time.time()-t0)[:5] + 's)'}")

# 1 to 1M  
t0 = time.time()
last_prime = 0
for n in range(2, 1000001):
    if is_prime(n):
        last_prime = n
print(f"{'1 to 1,000,000':<25} {last_prime:<25,} {'(' + str(time.time()-t0)[:5] + 's)'}")

# 1 to 10^7
t0 = time.time()
last_prime = 0
for n in range(2, 10000001):
    if is_prime(n):
        last_prime = n
print(f"{'1 to 10,000,000':<25} {last_prime:<25,} {'(' + str(time.time()-t0)[:5] + 's)'}")

print()
print("=" * 70)
print("۲) Frontier اعداد مرکب تجزیه‌شده پیوسته")
print("   = آخرین n که همه‌ی 1..n یا اول هستن یا تجزیه‌شدن")
print("=" * 70)
print()

print(f"{'Range':<25} {'Frontier':<15} {'Gaps':<10} {'Time':<10}")
print(f"{'-'*25} {'-'*15} {'-'*10} {'-'*10}")

# 1 to 10^6 dense
t0 = time.time()
frontier = 0
for n in range(1, 1000001):
    if is_prime(n) or n == 1 or is_factored(n):
        if n == frontier + 1 or n == 1:
            frontier = n
print(f"{'1 to 10^6':<25} {frontier:<15,} {0:<10} {time.time()-t0:.1f}s")

# 10^k sparse tests
for k in [10, 15, 20, 25, 30, 35, 40, 45, 50]:
    start = 10 ** k
    frontier_local = 0
    gaps_count = 0
    t0 = time.time()
    
    for i in range(100):
        n = start + i
        if is_prime(n) or is_factored(n):
            if i == 0 or frontier_local == i:
                frontier_local = i + 1
        else:
            gaps_count += 1
    
    fr_str = f"{frontier_local}/100"
    print(f"{'10^' + str(k):<25} {fr_str:<15} {gaps_count:<10} {time.time()-t0:.1f}s")
