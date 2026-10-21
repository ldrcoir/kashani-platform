import sys
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod, isqrt, iroot

N = mpz(42448645709965179520186712586272410887949285176201216206957538377)
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

# Try small primes up to 10^7
print("\n=== Trial division up to 10^7 ===")
import time
start = time.time()
small_factor = None
# Use sieve for efficiency
sieve = bytearray(b"\x01") * 10000001
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

# Check if N is a perfect power
print("\n=== Perfect power check ===")
for k in range(2, 65):
    r, exact = iroot(N, k)
    if exact:
        print(f"N = {r}^{k}")
        break
else:
    print("N is NOT a perfect power")

# log2 N
log2_n = float(gmpy2.log2(N))
print(f"\nlog2(N) = {log2_n:.6f}")
print(f"N ≈ 2^{log2_n:.4f}")

# Try Pollard p-1 with various B1
print("\n=== Pollard p-1 (B1=1e6) ===")
start = time.time()
B1 = 1000000
a = mpz(2)
# efficient power ladder
for p in range(2, B1 + 1):
    if gmpy2.is_prime(p):
        pp = p
        while pp * p <= B1:
            pp *= p
        a = powmod(a, pp, N)
g = gcd(a - 1, N)
print(f"Time: {time.time()-start:.1f}s, gcd = {g}")
if g > 1 and g < N:
    print(f"FACTOR FOUND by P-1: {g}")
    print(f"N / factor = {N // g}")
else:
    print("P-1 did not find factor with B1=1e6")

# Try Pollard rho (Brent's variant)
print("\n=== Pollard rho (Brent) ===")
def pollard_brent(n, max_iter=1000000):
    if n % 2 == 0:
        return 2
    x = mpz(2)
    y = mpz(2)
    d = mpz(1)
    f = lambda x: (x*x + 1) % n
    iters = 0
    while d == 1 and iters < max_iter:
        x = f(x)
        y = f(f(y))
        d = gcd(abs(x - y), n)
        iters += 1
    if d != n and d > 1:
        return d, iters
    return None, iters

start = time.time()
result, iters = pollard_brent(N, 10000000)
print(f"Time: {time.time()-start:.1f}s, iters: {iters}")
if result:
    print(f"FACTOR FOUND by Pollard rho: {result}")
else:
    print("Pollard rho did not find factor in 10M iters")
