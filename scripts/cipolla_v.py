#!/usr/bin/env python3
"""
NOVEL approach: Berlekamp-Massey + Minimal Polynomial of LL sequence mod N.

Insight:
  The Lucas-Lehmer sequence s_0=4, s_{n+1} = s_n^2 - 2 mod N satisfies:
    s_n = α^(2^n) + β^(2^n) where α = 2+√3, β = 2-√3.
  In Z[√3]/N, the sequence s_n mod q_i (for each prime factor q_i of N) has 
  a specific minimal polynomial that's related to the algebraic structure.
  
  If N = q1 * q2, the sequence mod q1 and mod q2 have DIFFERENT behaviors.
  By detecting the period or structure differences, we might factor N.

Algorithm:
  1. Generate a sequence x_0, x_1, x_2, ... where x_n = s_n mod N (LL sequence).
  2. Run Berlekamp-Massey to find the minimal polynomial.
  3. Factor the minimal polynomial mod small primes.
  
But the LL sequence is highly non-linear (s_{n+1} = s_n^2 - 2), so linear recurrence 
methods don't apply directly.

NEW IDEA: Use MODULAR DIFFERENCES instead.
  Compute r_n = s_n - 2 mod N for many n.
  gcd(r_n, N) might be non-trivial if r_n ≡ 0 mod q_i but not mod q_j.

OR: Use POWER PROJECTION.
  Compute the sequence a_n = 2^n mod N (which is just powers of 2).
  The order of 2 mod q_i is 1237 (for q_i | N).
  For N = q1 * q2 with both having ord = 1237, the order mod N is also 1237.
  So 2^k mod N is periodic with period 1237.
  
NEW IDEA: Use the algebraic structure of the period.
  For each k in [0, 1236], compute 2^k mod N. We get 1237 distinct values.
  Compute the POLYNOMIAL ∏ (x - 2^k) for k=0..1236 mod N. This is Phi_1237(x) mod N.
  Wait, that's just (x^1237 - 1) / (x - 1) = Phi_1237(x) ≡ 0 mod N (since 2^1237 ≡ 1 mod N).
  
NEW IDEA: Use RESULTANT.
  Compute Res(Phi_1237(x), Phi_q(x)) for various small primes q.
  If q is a "factor of N" in the cyclotomic sense (i.e., Phi_1237(2) and Phi_q(2) share a factor),
  the resultant is non-trivial.

Actually, the simplest CREATIVE approach:

SQUARE ROOT DIFFERENTIATION:
  We know (2p/N) = +1, so sqrt(2p) mod N exists.
  We computed sqrt(2p) mod N via a^((N-1)/4) for many a, and got "other" values
  (neither ±1). These "other" values r satisfy r^2 ≡ 2p mod q1 AND r^2 ≡ 2p mod q2
  with different signs.
  
  For each "witness" a, we computed r_a = a^((N-1)/4) mod N.
  r_a^2 = a^((N-1)/2) mod N.
  Mod q1: r_a^2 = a^((N-1)/2 mod (q1-1)) mod q1 = a^((q2-1)/2 mod (q1-1)) mod q1
  Mod q2: r_a^2 = a^((q1-1)/2 mod (q2-1)) mod q2
  
  These are different (since q1, q2 are different).
  For each a, r_a = (r_a mod q1, r_a mod q2) via CRT.
  If we collect r_a for many a, we get many points in Z/NZ × Z/NZ (via CRT).
  
  Maybe STATISTICAL ANALYSIS of these r_a values reveals factors!
  
  Specifically: 
    - r_a - 1 mod N is 0 mod q1 iff r_a ≡ 1 mod q1.
    - The number of a with r_a ≡ 1 mod q1 is approximately 1/4 of all a.
    - Similarly for q2.
    - If we accumulate the PRODUCT ∏(r_a - 1) over many a, this product will
      have q1 as a factor (if any r_a ≡ 1 mod q1 for some a in our sample),
      giving non-trivial gcd with N.

But we tried this before (half-GCD trick) and it didn't work.

NEW IDEA (different from before): 
  Use POLYNOMIAL APPROACH.
  Compute P(x) = ∏_{i=1}^{n} (x - r_i) mod N for n small prime numbers r_i.
  Then gcd(P(0), N) is non-trivial if any r_i divides N.
  But r_i are just small primes, this is trial division.
  
  Better: Compute P(x) = ∏_{a in our sample} (x - r_a) mod N.
  Then evaluate P at specific values: P(2^k mod N), P(2^k - 1), etc.
  Any of these might share a factor with N.

ALTERNATIVELY: Use RATIONAL FUNCTION approach.
  Compute the polynomial P(x) = ∏(x - r_a) mod N.
  If we then compute P(x) at x = 2^k for k = 0, ..., p-1, we get p values.
  These p values, when gcd'd with N, might give factors.

THIS IS NOVEL and computationally feasible.

ACTUALLY, here's the most creative idea:
  Compute P(x) = ∏_{j=0}^{p-1} (x - 2^j) mod N = Phi_p(x) mod N.
  But Phi_p(2) ≡ 0 mod N, so P(2) ≡ 0 mod N. Trivial.
  
  Compute P(x) = ∏_{j=0}^{p-1, j != 0} (x - 2^j) mod N = (Phi_p(x) - (x - 1))/(x-1) ... hmm no.
  
  Actually, ∏_{j=0}^{p-1} (x - 2^j) is the minimal polynomial of 2 mod q_i (for each q_i | N),
  which is Phi_p(x) for q_i (since ord_q_i(2) = p).
  So ∏(x - 2^j) ≡ Phi_p(x) ≡ 0 mod q_i for all i.
  Hence ∏(x - 2^j) ≡ 0 mod N (as a polynomial? no, only at specific x values).
  
Hmm.

Let me try a CONCRETE creative approach:
  Compute r_a = a^((N-1)/4) mod N for many a.
  Compute the product P = ∏ r_a mod N.
  This product is some specific value in Z/NZ.
  gcd(P, N), gcd(P-1, N), gcd(P+1, N) might be non-trivial.

We tried this. It didn't work.

NEW CREATIVE IDEA:
  The values r_a = a^((N-1)/4) are different for each a. They have CRT structure 
  (r_a mod q1, r_a mod q2).
  The "statistical" structure of these CRT values is determined by q1, q2.
  
  Specifically: r_a mod q1 takes each value in F_{q1} with roughly equal probability 
  (as a varies), UNLESS there's specific structure.
  
  If we compute MANY r_a values and look at their DISTRIBUTION mod small primes,
  we can detect anomalous distributions.
  
  E.g., compute r_a mod 5 for many a. The distribution of r_a mod 5 follows a 
  specific pattern depending on q1 mod 5 and q2 mod 5.
  
  If we observe that r_a mod 5 is always even, or has a specific bias, this 
  tells us about q1, q2 mod 5.
  
  Combined across many small primes, we can DERIVE q1, q2 mod (something).

This is genuinely novel. Let me try it.

Actually wait - I should look at this differently. We KNOW:
  r_a = a^((N-1)/4) mod N
  r_a^2 = a^((N-1)/2) mod N

(N-1)/2 has specific value. Let's call it h = (N-1)/2.

a^h mod q1 = a^(h mod (q1-1)) mod q1
a^h mod q2 = a^(h mod (q2-1)) mod q2

These are different exponents! 

Let e1 = h mod (q1-1), e2 = h mod (q2-1).
For random a, a^e1 mod q1 is uniformly distributed in F_{q1}* (or 0).
Similarly for a^e2 mod q2.

So r_a mod q1 = a^((e1+1)/2) mod q1 (if e1+1 = h/2 is even, wait I'm confusing myself).

Actually:
r_a = a^((N-1)/4) mod N
r_a^2 = a^((N-1)/2) mod N = a^h mod N (via CRT)
So r_a mod q1 = a^(h/2) mod q1 = a^((N-1)/4 mod (q1-1)) mod q1 = a^e1 mod q1
And r_a mod q2 = a^e2 mod q2

For random a, these are random in F_{q1}*, F_{q2}* (assuming e1, e2 are coprime to q1-1, q2-1 resp., or various).

OK enough theory. Let me try a CONCRETE creative experiment:

Compute r_a = a^((N-1)/4) mod N for many small a (say a = 2, 3, 5, ..., 1000).
For each r_a, compute r_a mod small primes (5, 7, 11, 13, ...).
Look for patterns.

Specifically, if all r_a mod 5 are equal to some constant c mod 5, that would mean 
e1, e2 are such that a^e1 ≡ a^e2 ≡ c mod 5 for all a (only possible if e1 ≡ e2 ≡ 0 mod 4,
i.e., q1 ≡ 1, q2 ≡ 1 mod 4 and 5-1 = 4 divides q_i - 1 in some specific way).

We could detect q1 mod 5, q2 mod 5 from these distributions.

Better idea: compute r_a for many a, then gcd of (r_a - r_b) for many pairs (a, b).
This is essentially the previous approach.

ACTUALLY, here's a really creative idea I haven't tried:
  Compute r_a = a^((N-1)/4) mod N for many a.
  Consider the SET of distinct values {r_a}.
  In Z/q1, r_a takes ~q1 distinct values (roughly).
  In Z/q2, r_a takes ~q2 distinct values (roughly).
  
  By CRT, r_a mod N takes ~q1*q2 = N distinct values (in principle).
  But our sample is much smaller, so we get collisions when r_a ≡ r_b mod q1 but ≠ mod q2,
  or vice versa.
  
  If we find a collision (r_a ≡ r_b mod q1 but ≠ mod q2), then gcd(r_a - r_b, N) = q1.
  
  The probability of collision after T samples is roughly T^2 / (2 q_min).
  For q_min = 75 digits, T = 10^38 needed. Infeasible.

OK let me think differently.

CREATIVE IDEA: Use Chinese Remainder Theorem IN REVERSE.
  We know:
    2p ≡ r_a^2 mod N
    Specifically, sqrt(2p) mod N exists with multiple values.
    
  If we can ENUMERATE some sqrt(2p) mod N values, we can compare with r_a.
  When two values are equal mod q_i but not mod q_j, we get a factor.

The PELL approach gives one sqrt(2p) mod N.
The Cipolla approach gives another.
If they differ, gcd gives a factor.

The issue: I haven't been able to compute Pell successfully.

Let me try yet another approach: GENERATE sqrt(2p) mod N via DIRECT methods.

For prime q, sqrt(2p) mod q can be computed via Tonelli-Shanks.
For composite N = q1 * q2, we can't use Tonelli-Shanks directly.
BUT we can use Cipolla, which works for prime moduli but gives partial results for composite.

For Cipolla with composite N:
  Pick random t with Jacobi(t^2 - 2p, N) = -1.
  Run Cipolla ladder (t + x)^((N+1)/2) in F_N[x]/(x^2 - (t^2 - 2p)).
  If x-coefficient vanishes (cur_v = 0), we get r with r^2 ≡ 2p mod N.
  Otherwise, we get a "non-trivial" pair (cur_u, cur_v) that satisfies the algebraic 
  identity but isn't a sqrt.
  
  When cur_v != 0, gcd(cur_v, N) might be non-trivial!

Wait, that's an interesting observation. Let me think more carefully.

In Cipolla's algorithm for sqrt(a) mod N:
  Pick t with (t^2 - a | N) = -1.
  Compute (t + x)^((N+1)/2) in F_N[x]/(x^2 - (t^2 - a)).
  Result is u + v*x.
  If v = 0: u^2 ≡ a mod N (in the prime case, this works; for composite, only if 
            u^2 - a ≡ 0 mod ALL factors).
  If v != 0: u^2 + 2uv*x + v^2*(t^2 - a) = (t+x)^{N+1} ≡ t^2 - a mod N (in prime case).
             This gives u^2 + v^2*(t^2 - a) = t^2 - a, i.e., u^2 = (1 - v^2)(t^2 - a).
             Not directly useful.

For composite N, when v != 0, gcd(v, N) is often non-trivial!

Let me try this with many t values and check gcd(v, N).
"""

import sys
import time
import random
from pathlib import Path
import gmpy2
from gmpy2 import mpz, gcd as gmpy_gcd, powmod, jacobi, is_prime, invert

sys.set_int_max_str_digits(1000000)

BASE = Path('/home/z/my-project')
LOG = BASE / 'logs/cipolla_v.log'
LOG.parent.mkdir(exist_ok=True)

def log(msg):
    print(msg, flush=True)
    with open(LOG, 'a') as f:
        f.write(msg + '\n')


def main():
    p = 1237
    M_p = mpz(2)**p - 1
    F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
    N = M_p // F1
    
    a = 2 * p  # = 2474
    
    log('=' * 70)
    log('Cipolla with v-coefficient analysis')
    log(f'  Target: N = M({p})/F1, {len(str(N))} digits')
    log(f'  Find sqrt({a}) mod N via Cipolla; check gcd(v, N) when v != 0')
    log('=' * 70)
    
    log(f'(a/N) = {jacobi(a, int(N))} (need +1 for sqrt to exist)')
    
    # Cipolla: try many t, check v
    log('')
    log('Running Cipolla with many t values...')
    
    t_start = time.time()
    factor_found = None
    nontrivial_v_count = 0
    tested_count = 0
    
    random.seed(42)
    
    for trial in range(2000):
        if time.time() - t_start > 100:
            log(f'  Time budget at trial {trial}')
            break
        
        # Pick random t
        t = mpz(random.randint(2, int(N) - 1))
        d = (t * t - a) % N  # = t^2 - a mod N
        
        if d == 0:
            # t itself is sqrt of a mod N
            if (t * t - a) % N == 0:
                log(f'  >>> trial {trial}: t = {t} is sqrt of {a} mod N directly!')
                # Try gcd(t ± something, N) - probably not useful
            continue
        
        # Cipolla ladder
        u, v = t, mpz(1)
        exp = (N + 1) // 2
        bits = bin(int(exp))[2:]
        cur_u, cur_v = mpz(1), mpz(0)
        for bit in bits:
            new_u = (cur_u * cur_u + d * cur_v * cur_v) % N
            new_v = (2 * cur_u * cur_v) % N
            cur_u, cur_v = new_u, new_v
            if bit == '1':
                new_u = (cur_u * t + d * cur_v) % N
                new_v = (cur_u + cur_v * t) % N
                cur_u, cur_v = new_u, new_v
        
        tested_count += 1
        
        if cur_v != 0:
            nontrivial_v_count += 1
            # Check gcd(cur_v, N) - might give a factor!
            g = gmpy_gcd(cur_v, N)
            if 1 < int(g) < int(N):
                log(f'  >>> trial {trial}: gcd(v, N) = {g}  FACTOR FOUND!')
                log(f'      Factor has {len(str(g))} digits')
                factor_found = int(g)
                break
            
            # Also try gcd(cur_u - 1, N), gcd(cur_u + 1, N)
            g1 = gmpy_gcd(cur_u - 1, N)
            if 1 < int(g1) < int(N):
                log(f'  >>> trial {trial}: gcd(u - 1, N) = {g1}  FACTOR FOUND!')
                factor_found = int(g1)
                break
            g2 = gmpy_gcd(cur_u + 1, N)
            if 1 < int(g2) < int(N):
                log(f'  >>> trial {trial}: gcd(u + 1, N) = {g2}  FACTOR FOUND!')
                factor_found = int(g2)
                break
        # Else cur_v = 0, we have a sqrt; check gcd(cur_u - existing_sqrt, N)
    
    elapsed = time.time() - t_start
    log(f'  Tested {tested_count} t values in {elapsed:.1f}s')
    log(f'  Non-trivial v: {nontrivial_v_count}')
    
    if factor_found:
        log('')
        log(f'FACTOR FOUND: {factor_found}')
        log(f'Digits: {len(str(factor_found))}')
        cofactor = int(N) // factor_found
        log(f'Cofactor: {cofactor}')
        log(f'is_prime(factor): {is_prime(factor_found)}')
        log(f'is_prime(cofactor): {is_prime(cofactor)}')
        
        # Update factor file
        lines = (BASE / 'download/A136030_factors_1_to_8000.txt').read_text().splitlines(keepends=True)
        out = []
        for line in lines:
            if line.startswith('#'):
                out.append(line); continue
            parts = line.split('\t')
            if len(parts) >= 2 and parts[0] == str(p):
                cur = parts[1].strip()
                if cur == '-1' or factor_found < int(cur):
                    out.append(f'{p}\t{factor_found}\n')
                else:
                    out.append(line)
            else:
                out.append(line)
        (BASE / 'download/A136030_factors_1_to_8000.txt').write_text(''.join(out))
        log('Updated factors table!')
    else:
        log('')
        log('No factor found via Cipolla v-coefficient')


if __name__ == '__main__':
    main()
