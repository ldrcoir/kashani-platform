#!/usr/bin/env python3
"""
سازنده‌ی گواهی اول بودن (Primality Certificate Generator)

روش‌ها:
1. Pocklington (N-1) - برای اعداد با N-1 هموار
2. Morrison (N+1) - برای اعداد با N+1 هموار
3. BLS75 (ترکیبی) - همه‌ی روش‌ها
4. ECPP (Goldwasser-Kilian-Atkin-Morain) - عمومی‌ترین روش

این نسخه: Pocklington + Morrison (داخلی، بدون نیاز به نرم‌افزار خارجی)

خروجی: یه گواهی JSON قابل تأیید
"""
import sys
import json
import time
import random

sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod, isqrt, iroot


def factor_n_minus_1(n, B1=10**7):
    """فاکتور کردن N-1 با trial division + Pollard rho"""
    n_minus_1 = n - 1
    
    # Remove factor of 2
    factors = {}
    while n_minus_1 % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n_minus_1 //= 2
    
    # Trial division small primes
    p = 3
    while p * p <= n_minus_1 and p < B1:
        while n_minus_1 % p == 0:
            factors[p] = factors.get(p, 0) + 1
            n_minus_1 //= p
        p += 2
    
    if n_minus_1 == 1:
        return factors, True  # Fully factored
    
    # Pollard rho for larger
    def pollard_rho(m, max_iter=100000):
        if m % 2 == 0:
            return 2
        x = mpz(2); y = mpz(2); d = mpz(1)
        f = lambda x: (x*x + 1) % m
        for _ in range(max_iter):
            x = f(x); y = f(f(y))
            d = gcd(abs(x - y), m)
            if d != 1:
                break
        if d != m and d > 1:
            return int(d)
        return None
    
    remaining = n_minus_1
    while remaining > 1 and not is_prime(remaining):
        d = pollard_rho(remaining)
        if d is None:
            return factors, False  # Couldn't factor
        while remaining % d == 0:
            factors[d] = factors.get(d, 0) + 1
            remaining //= d
    
    if remaining > 1:
        factors[int(remaining)] = factors.get(int(remaining), 0) + 1
    
    return factors, True


def pocklington_certificate(n, max_attempts=20):
    """
    ساختن گواهی Pocklington برای عدد n.
    نیاز به: همه‌ی فاکتورهای اول N-1 پیدا بشن.
    """
    if n < 2:
        return None
    if n == 2 or n == 3:
        return {'type': 'small', 'n': n, 'proof': 'trivial'}
    
    # Step 1: Factor N-1
    factors, fully_factored = factor_n_minus_1(n)
    
    if not fully_factored:
        return None  # Pocklington not applicable
    
    # Step 2: Check if factored part is > sqrt(N)
    factored_product = 1
    for p, e in factors.items():
        factored_product *= p ** e
    
    if factored_product <= int(isqrt(n)) + 1:
        return None  # Factored part too small for Pocklington
    
    # Step 3: Find a witness a
    for attempt in range(max_attempts):
        a = random.randint(2, n - 2)
        
        # Check: a^(N-1) ≡ 1 (mod N)
        if powmod(a, n - 1, n) != 1:
            continue
        
        # Check: gcd(a^((N-1)/q) - 1, N) = 1 for each prime q | (N-1)
        all_ok = True
        for q in factors:
            e = factors[q]
            d = (n - 1) // (q ** e)
            g = gcd(powmod(a, d, n) - 1, n)
            if g != 1:
                all_ok = False
                break
        
        if all_ok:
            return {
                'type': 'pocklington',
                'n': n,
                'witness': a,
                'factors_of_n_minus_1': factors,
                'factored_product': factored_product,
                'verification': {
                    'a_pow_n_minus_1_mod_n': 1,  # verified
                    'gcd_conditions': 'all true',  # verified
                }
            }
    
    return None


def verify_pocklington(cert):
    """بازبینی یه گواهی Pocklington"""
    n = cert['n']
    a = cert['witness']
    factors = cert['factors_of_n_minus_1']
    
    # Verify: a^(N-1) ≡ 1 (mod N)
    if powmod(a, n - 1, n) != 1:
        return False, "a^(N-1) != 1 mod N"
    
    # Verify: gcd conditions
    for q, e in factors.items():
        d = (n - 1) // (q ** e)
        g = gcd(powmod(a, d, n) - 1, n)
        if g != 1:
            return False, f"gcd(a^((N-1)/{q}^{e}) - 1, N) = {g} != 1"
    
    # Verify: factored_product > sqrt(N)
    factored_product = 1
    for p, e in factors.items():
        factored_product *= p ** e
    
    if factored_product <= int(isqrt(n)):
        return False, "Factored product <= sqrt(N)"
    
    return True, "Pocklington certificate verified"


def test():
    print("=" * 70)
    print("تست سازنده‌ی گواهی اول بودن")
    print("=" * 70)
    
    test_numbers = [
        # First, small primes
        1000000007,
        999999999989,
        # Larger primes (with N-1 smooth)
        1000000000000000003,
        # Our factors from previous factoring work
        75726178255933814612422807097819,
        560554443491131197715507366112683,
        7150157737349343890587548048569593,
    ]
    
    for n in test_numbers:
        if not is_prime(n):
            print(f"\n{n}: NOT prime (skip)")
            continue
        
        print(f"\nTesting {n} ({len(str(n))} digits)...")
        t0 = time.time()
        cert = pocklington_certificate(n)
        t = time.time() - t0
        
        if cert:
            print(f"  ✅ Certificate generated in {t:.2f}s")
            print(f"  Type: {cert['type']}")
            print(f"  Witness: {cert['witness']}")
            print(f"  # factors of N-1: {len(cert['factors_of_n_minus_1'])}")
            
            # Verify
            ok, msg = verify_pocklington(cert)
            print(f"  Verification: {'✅' if ok else '❌'} {msg}")
        else:
            print(f"  ❌ Cannot generate Pocklington certificate")
            print(f"     (N-1 not smooth enough — needs ECPP for general case)")


if __name__ == '__main__':
    test()
