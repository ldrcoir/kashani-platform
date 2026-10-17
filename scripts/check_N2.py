import sys
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod, isqrt, iroot

N = mpz(44970392094226224655193611221785951576628072532398031171908075269)
print(f"N = {N}")
print(f"Digits: {len(str(N))}")
print(f"Bit length: {N.bit_length()}")
print(f"N mod 2 = {N % 2}")
print(f"N mod 3 = {N % 3}")
print(f"N mod 5 = {N % 5}")
print(f"N mod 7 = {N % 7}")
print(f"N mod 11 = {N % 11}")
print(f"N mod 13 = {N % 13}")
print(f"N mod 17 = {N % 17}")
print(f"N mod 19 = {N % 19}")
print(f"N mod 23 = {N % 23}")
print(f"N mod 4 = {N % 4}")
print(f"N mod 6 = {N % 6}")
print(f"N mod 8 = {N % 8}")
print(f"N mod 12 = {N % 12}")

# Is N prime?
print(f"\nIs N prime? {is_prime(N)}")

# Trial division up to 10^7
print("\n=== Trial division up to 10^7 ===")
import time
start = time.time()
sieve = bytearray(b"\x01") * 10000001
small_factor = None
for p in range(2, 10000001):
    if sieve[p]:
        if N % p == 0:
            small_factor = p
            break
        for j in range(p*p, 10000001, p):
            sieve[j] = 0
print(f"Trial div to 10^7 took {time.time()-start:.1f}s")
if small_factor:
    print(f"Found small factor: {small_factor}")
else:
    print("No small factor < 10^7")

# Perfect power?
print("\n=== Perfect power check ===")
for k in range(2, 65):
    r, exact = iroot(N, k)
    if exact:
        print(f"N = {r}^{k}")
        break
else:
    print("N is NOT a perfect power")

log2_n = float(gmpy2.log2(N))
print(f"\nlog2(N) = {log2_n:.6f}")

# P-1 quick check
print("\n=== Pollard p-1 (B1=1e6) ===")
start = time.time()
B1 = 1000000
a = mpz(2)
for p in range(2, B1 + 1):
    if gmpy2.is_prime(p):
        pp = p
        while pp * p <= B1:
            pp *= p
        a = powmod(a, pp, N)
g = gcd(a - 1, N)
print(f"P-1 (B1=1e6): gcd = {g}, time = {time.time()-start:.1f}s")
if g > 1 and g < N:
    print(f"P-1 FACTOR: {g}")

# Pollard rho quick
print("\n=== Pollard rho (Brent, 5M iters) ===")
def pollard_brent(n, max_iter=5000000):
    if n % 2 == 0:
        return 2
    x = mpz(2); y = mpz(2); d = mpz(1)
    f = lambda x: (x*x + 1) % n
    for iters in range(max_iter):
        x = f(x); y = f(f(y))
        d = gcd(abs(x - y), n)
        if d != 1:
            break
    if d != n and d > 1:
        return d
    return None

start = time.time()
result = pollard_brent(N, 5000000)
print(f"Pollard rho (5M iters): {result}, time = {time.time()-start:.1f}s")
