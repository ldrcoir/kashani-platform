#!/usr/bin/env python3
"""
روش‌های ابتکاری مبتنی بر سینوس برای فاکتورینگ
==============================================
سه روش:
1. استفاده از sin(π·x) برای تولید اعداد جبری به‌عنوان candidate فاکتور
2. تحلیل Fourier برای پیدا کردن دوره‌های پنهان در دنباله‌ی رقم‌ها
3. تولید اعداد از sin(n) برای فاکتور کردن

به افتخار EhsanMoradMaryamAlasvandi و Jamshid al-Kashi
"""
import sys, os, time, json, math, random
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime

import mpmath
mpmath.mp.dps = 100

OUTPUT_DIR = "/home/z/my-project/download/sinus_method"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_numbers_from_sin(method_id, count=20):
    """تولید اعداد با روش‌های مختلف مبتنی بر سینوس"""
    numbers = []
    
    if method_id == 1:
        # روش ۱: floor(10^k * sin(1))
        # استفاده از sin(1) به‌عنوان «عدد پی»‌مان
        sin_1 = mpmath.sin(1)
        for k in range(20, 100):
            n = int(mpmath.floor(mpmath.power(10, k) * sin_1))
            numbers.append({
                'n': n,
                'method': f'floor(10^{k} * sin(1))',
                'source': 'sin(1)',
                'digits': k,
            })
            if len(numbers) >= count:
                break
    
    elif method_id == 2:
        # روش ۲: floor(10^k * sin(p)) برای p اول
        primes = [p for p in range(2, 200) if is_prime(p)]
        for p in primes:
            sin_p = mpmath.sin(p)
            for k in [30, 50, 70]:
                n = int(mpmath.floor(mpmath.power(10, k) * sin_p))
                numbers.append({
                    'n': n,
                    'method': f'floor(10^{k} * sin({p}))',
                    'source': f'sin({p})',
                    'digits': k,
                    'prime_arg': p,
                })
                if len(numbers) >= count:
                    return numbers
    
    elif method_id == 3:
        # روش ۳: اعداد ساخته‌شده از sin(π·k/n)
        # اعداد جبری: sin(π/3) = √3/2, sin(π/5) = √(10-2√5)/4
        # این اعداد جبری می‌تونن فاکتورهای سرنخ‌دار باشن
        for n in range(2, 50):
            sin_pi_n = mpmath.sin(mpmath.pi / n)
            # ضرب در 10^k برای تبدیل به عدد صحیح
            k = 40
            value = mpmath.power(10, k) * sin_pi_n
            # عدد بزرگ
            n_int = int(mpmath.floor(value))
            if n_int > 0:
                numbers.append({
                    'n': n_int,
                    'method': f'floor(10^{k} * sin(π/{n}))',
                    'source': f'sin(π/{n})',
                    'digits': len(str(n_int)),
                    'n_param': n,
                })
    
    elif method_id == 4:
        # روش ۴: ترکیب sin و cos: sin²(x) + cos²(x) = 1
        # اعداد نوع (sin(x), cos(x)) که cos(x) = sqrt(1 - sin²(x))
        # این اعداد جبری‌اند
        for x_deg in [30, 45, 60, 22.5, 18, 36]:
            x_rad = mpmath.mpf(x_deg) * mpmath.pi / 180
            sin_x = mpmath.sin(x_rad)
            for k in [40, 50, 60]:
                n = int(mpmath.floor(mpmath.power(10, k) * sin_x))
                if n > 0:
                    numbers.append({
                        'n': n,
                        'method': f'floor(10^{k} * sin({x_deg}°))',
                        'source': f'sin({x_deg}°)',
                        'digits': len(str(n)),
                        'angle': x_deg,
                    })
    
    return numbers


def factor_with_rho(n, max_iter=200000):
    if n == 1: return []
    if n % 2 == 0:
        return [2] + factor_with_rho(n // 2, max_iter)
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


def main():
    print("=" * 80)
    print("🌊 روش‌های ابتکاری مبتنی بر سینوس")
    print("=" * 80)
    
    all_results = {}
    
    for method_id in [1, 2, 3, 4]:
        print(f"\n--- روش {method_id} ---")
        numbers = generate_numbers_from_sin(method_id, count=15)
        results = []
        
        for n_info in numbers:
            n = n_info['n']
            print(f"\n  {n_info['method']} ({n_info['digits']} رقم)")
            
            # Check primality first
            if is_prime(mpz(n)):
                print(f"    ✅ عدد اول!")
                n_info['status'] = 'P'
                n_info['factors'] = [n]
            else:
                # Try factoring
                factors = factor_with_rho(n)
                if None in factors:
                    print(f"    ❌ rho نتوانست فاکتور کنه")
                    n_info['status'] = '?'
                    n_info['factors'] = [f for f in factors if f is not None]
                else:
                    print(f"    ✅ فاکتور شد: {' × '.join(map(str, factors))}")
                    n_info['status'] = 'C'
                    n_info['factors'] = factors
            results.append(n_info)
        
        all_results[f'method_{method_id}'] = results
    
    # Save
    with open(f"{OUTPUT_DIR}/sinus_method_results.json", 'w') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 خلاصه روش‌های مبتنی بر سینوس")
    print("=" * 80)
    print(f"{'روش':<10} {'تعداد':<8} {'اول':<8} {'مرکب':<8} {'شکست':<8}")
    print(f"{'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    
    for method_id, results in all_results.items():
        total = len(results)
        primes = sum(1 for r in results if r.get('status') == 'P')
        composites = sum(1 for r in results if r.get('status') == 'C')
        failed = sum(1 for r in results if r.get('status') == '?')
        print(f"{method_id:<10} {total:<8} {primes:<8} {composites:<8} {failed:<8}")
    
    # Look for patterns
    print("\n" + "=" * 80)
    print("🔍 الگوهای کشف‌شده")
    print("=" * 80)
    
    # Pattern 1: اگه از sin(π/n) استفاده کنیم، آیا n در فاکتورها ظاهر می‌شه؟
    if 'method_3' in all_results:
        print("\nالگو ۱: آیا n در فاکتورهای floor(10^k * sin(π/n)) ظاهر می‌شه؟")
        for r in all_results['method_3']:
            if r['status'] == 'C' and 'n_param' in r:
                n = r['n_param']
                factors = r['factors']
                if n in factors or any(f == n for f in factors):
                    print(f"  ✅ n={n} در فاکتورها ظاهر شد!")
                else:
                    # Check if n divides any factor
                    for f in factors:
                        if f % n == 0 and f != n:
                            print(f"  ⚠️ n={n} فاکتور {f} رو بخش می‌کنه")
                            break
    
    print(f"\n💾 ذخیره شد: {OUTPUT_DIR}/sinus_method_results.json")


if __name__ == '__main__':
    main()
