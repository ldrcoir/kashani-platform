import sys, time
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime

N = mpz(53557420296729856940815708470943351869321072980535994936566260779217)
print(f"N = {N}")
print(f"Digits: {len(str(N))}")
print(f"Bit length: {N.bit_length()}")
print(f"N mod 2 = {N % 2}, mod 3 = {N % 3}, mod 5 = {N % 5}, mod 7 = {N % 7}")
print(f"Is prime? {is_prime(N)}")

# Trial division to 1e7
print("\n=== Trial division up to 1e7 ===")
import math
t0 = time.time()
small_f = None
sieve = bytearray(b"\x01") * 10000001
for p in range(2, 10000001):
    if sieve[p]:
        if N % p == 0:
            small_f = p
            break
        for j in range(p*p, 10000001, p):
            sieve[j] = 0
print(f"Took {time.time()-t0:.1f}s")
print(f"Small factor: {small_f}" if small_f else "No small factor < 1e7")

# Perfect power check
print("\n=== Perfect power check ===")
for k in range(2, 65):
    r, exact = gmpy2.iroot(N, k)
    if exact:
        print(f"N = {r}^{k}")
        break
else:
    print("N is NOT a perfect power")
