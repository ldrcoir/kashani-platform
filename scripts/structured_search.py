#!/usr/bin/env python3
"""
Hybrid approach: use KNOWN Mersenne factors from Cunningham table to seed search.

KEY IDEA (different from IFC):
  Instead of random k, generate k from STRUCTURED families:
  1. k = q1 (where q1 is a small Mersenne prime factor)
  2. k = q1^a * q2^b (smooth combinations of small Mersenne primes)
  3. k derived from cyclotomic structure

ALTERNATIVE IDEA:
  For each candidate q = 2*k*p + 1 with 70-100 digits:
    If q is prime AND 2^1237 ≡ 1 mod q:
      Check if q divides N = M(1237)/F1.
  
  The "2^1237 ≡ 1 mod q" check requires q ≡ 1 mod 1237, which is automatically true
  from q = 2*k*1237 + 1.
  
  But to actually divide M(1237), we need ord_q(2) = 1237, which is much rarer than
  just q ≡ 1 mod 1237.
  
  Probability: among primes q ≡ 1 mod 1237, the fraction with ord_q(2) = 1237 is:
    Phi(1237) / 1237 = 1236/1237 ≈ 1.
  Wait, that's the probability of ord_q(2) | 1237 (given q-1 divisible by 1237).
  Actually, in (Z/qZ)*, the elements of order dividing 1237 form a subgroup of size 1237.
  The probability that 2 has order exactly 1237 (given 1237 | q-1) is:
    Number of generators of Z/1237Z = Phi(1237) = 1236 (since 1237 is prime).
    Total elements of order dividing 1237: 1237 (including identity).
    So probability = 1236/1237 ≈ 0.9992.
  
  Wait that's HUGE. So if q is prime and q ≡ 1 mod 1237, then almost certainly 
  ord_q(2) = 1237 (since the only other option is ord_q(2) = 1, which means q | 1, impossible).
  
  Hmm, so probability ≈ 0.9992 that 2 has order 1237 in (Z/qZ)* given q ≡ 1 mod 2*1237.
  
  But that means 2^1237 ≡ 1 mod q for almost all primes q ≡ 1 mod 2*1237!
  Then q | M(1237) for almost all such primes? NO - q | M(1237) means q is one specific 
  prime divisor, not "almost all primes of a certain form."
  
  Wait, I'm confused. Let me reconsider.
  
  M(1237) = 2^1237 - 1 = product of prime factors q_i.
  Each q_i has ord_q_i(2) = 1237.
  The q_i are SPECIFIC primes, not "all primes with this property".
  
  But: how many primes q have ord_q(2) = 1237? Approximately N/Phi(N) where Phi is Euler's totient.
  By Dirichlet: primes q with q ≡ 1 mod 1237 are 1/Phi(1237) ≈ 1/1237 of all primes.
  Among these, fraction with ord_q(2) = 1237 (rather than 1): Phi(1237)/1237 ≈ 0.9992.
  
  So out of all primes q in a range, fraction with q | M(1237): 1/1237 * 0.9992 ≈ 1/1237.
  For 70-digit q range (10^69 to 10^70 - 1), # of primes is 10^70 / (70 * ln 10) ≈ 6.2 * 10^67.
  Of these, # with q | M(1237): 6.2 * 10^67 / 1237 ≈ 5 * 10^64.
  
  But M(1237) has at most ~373/log_10(70) ≈ 5.3 prime factors of 70 digits.
  So our chance of finding one of these specific factors among ALL primes in the range is
  ~ 5 / (5 * 10^64) = 10^-64.
  
  So random sampling 70-digit q's gives essentially zero chance. We need STRUCTURE.

ACTUAL STRUCTURED SEARCH:
  Use the fact that q = 2*k*1237 + 1, where k itself has structure.
  For example:
  - k = product of small primes (smooth)
  - k = power of 2 (gives specific q)
  - k = Mersenne number (2^j - 1) for some j
  
  Let's try k = 2^j - 1 for j = 200, 201, ..., 240 (gives k ≈ 60-72 digits, q ≈ 70-75 digits).
  Also k = 2^j + 1 (Fermat-like).
  
  Other structured k:
  - k = a^j for small a, j chosen so k ≈ 10^66-10^93
  - k = primorial (product of first m primes) — gives specific structure
  - k = m! for specific m
  
  These give ~few hundred candidates total. Check each.
"""

import sys
import time
from pathlib import Path

import gmpy2
from gmpy2 import mpz, is_prime, powmod, gcd

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
LOG_FILE = BASE / 'logs/structured_search.log'
LOG_FILE.parent.mkdir(exist_ok=True)


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')


def update_factor_file(p, factor):
    lines = FACTORS_FILE.read_text(encoding='utf-8').splitlines(keepends=True)
    out = []
    updated = False
    for line in lines:
        if line.startswith('#'):
            out.append(line); continue
        parts = line.split('\t')
        if len(parts) >= 2 and parts[0] == str(p):
            cur = parts[1].strip()
            if cur == '-1' or int(factor) < int(cur):
                out.append(f'{p}\t{factor}\n'); updated = True
            else:
                out.append(line)
        else:
            out.append(line)
    if updated:
        FACTORS_FILE.write_text(''.join(out), encoding='utf-8')
    return updated


def append_complete(p, factor, cofactor):
    complete_file = BASE / 'download/A136030_complete_factorizations.txt'
    with open(complete_file, 'a', encoding='utf-8') as f:
        f.write(f'{p}\tFULL\t{factor}\t{cofactor}\n')


def check_q(q_cand, p, M, F1, log):
    """Check if q_cand is a factor of M(p)."""
    q_cand = mpz(q_cand)
    if q_cand < 2:
        return False
    if not is_prime(q_cand):
        return False
    # Check 2^p mod q_cand == 1
    if powmod(2, p, q_cand) != 1:
        return False
    # q_cand is a Mersenne factor! Check if it divides M(p)/F1 (the cofactor we care about).
    N = M // F1
    if int(N) % int(q_cand) == 0:
        log(f'  >>> q = {q_cand} ({len(str(q_cand))} digits) divides M({p})/F1!')
        log(f'      FACTOR FOUND!')
        update_factor_file(p, int(q_cand))
        cofactor = int(N) // int(q_cand)
        append_complete(p, int(q_cand), cofactor)
        return True
    else:
        # q divides M(p) but maybe it's actually a factor of F1 or a different product.
        # Actually if q | M(p) and q is prime, it's a prime factor of M(p).
        log(f'  Note: q = {q_cand} ({len(str(q_cand))} digits) is prime and 2^{p} ≡ 1 mod q, but q does not divide N = M(p)/F1.')
        # Maybe q divides F1? Check.
        if int(F1) % int(q_cand) == 0:
            log(f'    q divides F1.')
        else:
            log(f'    q is a new prime factor of M(p) but does not divide N. This is suspicious.')
            # Hmm, if q | M(p) and q doesn't divide F1, then q must divide N = M(p)/F1.
            # So this case shouldn't happen. Let me double check.
            # Maybe my is_prime check failed, or powmod check was incorrect.
            # Check M(p) mod q directly
            Mp_mod_q = powmod(2, p, q_cand) - 1  # = (2^p - 1) mod q = M(p) mod q
            log(f'    M(p) mod q = {Mp_mod_q}')
            if Mp_mod_q == 0:
                log(f'      q does divide M(p)!')
                log(f'      Checking F1 mod q: {int(F1) % int(q_cand)}')
                log(f'      Checking N mod q: {int(N) % int(q_cand)}')
        return False


def main():
    p = 1237
    M = mpz(2)**p - 1
    F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
    N = M // F1
    
    log('=' * 70)
    log('Structured k Search for M(1237) factors')
    log(f'  Target: q = 2*k*p + 1, q prime, q | M(p)')
    log(f'  Try structured k: powers of 2, Mersenne-like, smooth, etc.')
    log('=' * 70)
    
    # Strategy 1: k = 2^j for various j (q = 2^(j+1) * p + 1)
    log('')
    log('Strategy 1: k = 2^j for j = 60 to 230 (gives q ≈ 18 to 70+ digits)')
    for j in range(60, 231):
        k = (1 << j)  # 2^j
        q_cand = 2 * k * p + 1
        if is_prime(q_cand):
            log(f'  k = 2^{j} = (small), q has {len(str(q_cand))} digits')
            if check_q(q_cand, p, M, F1, log):
                return
    
    # Strategy 2: k = 2^j - 1 (Mersenne-like)
    log('')
    log('Strategy 2: k = 2^j - 1 (Mersenne-like)')
    for j in range(60, 240):
        k = (1 << j) - 1
        q_cand = 2 * k * p + 1
        if is_prime(q_cand):
            log(f'  k = 2^{j}-1, q has {len(str(q_cand))} digits')
            if check_q(q_cand, p, M, F1, log):
                return
    
    # Strategy 3: k = 2^j + 1 (Fermat-like)
    log('')
    log('Strategy 3: k = 2^j + 1 (Fermat-like)')
    for j in range(60, 240):
        k = (1 << j) + 1
        q_cand = 2 * k * p + 1
        if is_prime(q_cand):
            log(f'  k = 2^{j}+1, q has {len(str(q_cand))} digits')
            if check_q(q_cand, p, M, F1, log):
                return
    
    # Strategy 4: k = a^j for small a (2, 3, 5, 7) and various j
    log('')
    log('Strategy 4: k = a^j for small a, various j')
    for a in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
        for j in range(20, 200):
            k = a ** j
            if k > 10**150:
                break
            q_cand = 2 * k * p + 1
            if is_prime(q_cand):
                log(f'  k = {a}^{j}, q has {len(str(q_cand))} digits')
                if check_q(q_cand, p, M, F1, log):
                    return
    
    # Strategy 5: k = factorial(j) for j up to 50
    log('')
    log('Strategy 5: k = j! for j up to 70')
    fact = 1
    for j in range(1, 71):
        fact *= j
        if fact > 10**150:
            break
        k = fact
        q_cand = 2 * k * p + 1
        if is_prime(q_cand):
            log(f'  k = {j}!, q has {len(str(q_cand))} digits')
            if check_q(q_cand, p, M, F1, log):
                return
    
    # Strategy 6: k = primorial (product of first m primes)
    log('')
    log('Strategy 6: k = primorial(m) for m up to 60')
    primorial = 1
    primes_under_300 = [i for i in range(2, 300) if is_prime(i)]
    for m in range(0, 60):
        if m < len(primes_under_300):
            primorial *= primes_under_300[m]
        if primorial > 10**150:
            break
        k = primorial
        q_cand = 2 * k * p + 1
        if is_prime(q_cand):
            log(f'  k = primorial({m+1}), q has {len(str(q_cand))} digits')
            if check_q(q_cand, p, M, F1, log):
                return
    
    # Strategy 7: k = product of small primes to some power (smooth k)
    log('')
    log('Strategy 7: k = product of small primes to powers, k ≈ 10^66 (70-digit q)')
    # Generate k = 2^a * 3^b * 5^c * 7^d with a + b*log2(3) + c*log2(5) + d*log2(7) ≈ 220
    import random
    random.seed(42)
    for _ in range(2000):
        a = random.randint(0, 220)
        b = random.randint(0, int(220 / 1.58))
        c = random.randint(0, int(220 / 2.32))
        d = random.randint(0, int(220 / 2.81))
        k = (2**a) * (3**b) * (5**c) * (7**d)
        if k < 10**60 or k > 10**100:
            continue
        q_cand = 2 * k * p + 1
        if is_prime(q_cand):
            log(f'  k = 2^{a} * 3^{b} * 5^{c} * 7^{d}, q has {len(str(q_cand))} digits')
            if check_q(q_cand, p, M, F1, log):
                return
    
    log('')
    log('No factor found via structured search')


if __name__ == '__main__':
    main()
