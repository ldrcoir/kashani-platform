#!/usr/bin/env python3
"""Persistent ECM on CORRECT N = M(1237)/F1. Runs until killed."""
import sys; sys.set_int_max_str_digits(1000000)
import gmpy2; from gmpy2 import mpz, gcd, is_prime, powmod, isqrt, invert
import time, random, json
from pathlib import Path

BASE = Path('/home/z/my-project')
LOG = BASE / 'logs/ecm_bg.log'
STATE = BASE / 'logs/ecm_state.json'
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'

M = mpz(2)**1237 - 1
F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
N = M // F1

def log(msg):
    t = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{t}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f: f.write(line + '\n')

def update_factors(factor):
    lines = FACTORS_FILE.read_text().splitlines(keepends=True)
    out = []
    for line in lines:
        if line.startswith('#'): out.append(line); continue
        parts = line.split('\t')
        if len(parts) >= 2 and parts[0] == '1237':
            cur = parts[1].strip()
            if cur == '-1' or factor < int(cur): out.append(f'1237\t{factor}\n')
            else: out.append(line)
        else: out.append(line)
    FACTORS_FILE.write_text(''.join(out))

def small_primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]: sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

B1 = 10_000_000
primes = small_primes_up_to(B1)
log(f'ECM persistent: N={len(str(N))}d, B1={B1}, {len(primes)} primes')

def ec_mul(k, x, y, a, N):
    rx, ry = None, None
    ax, ay = x, y
    while k > 0:
        if k & 1:
            if rx is None: rx, ry = ax, ay
            elif ax is not None:
                if rx == ax:
                    if ry == ay:
                        num = (3*rx*rx + a) % N; den = (2*ry) % N
                    else: rx, ry = None, None; k >>= 1; continue
                else:
                    num = (ay - ry) % N; den = (ax - rx) % N
                g = gcd(den, N)
                if 1 < int(g) < int(N): return g
                if int(g) == int(N): rx, ry = None, None; k >>= 1; continue
                lam = (num * invert(den, N)) % N
                x3 = (lam*lam - rx - ax) % N
                y3 = (lam*(rx - x3) - ry) % N
                rx, ry = x3, y3
        if ax is not None:
            num = (3*ax*ax + a) % N; den = (2*ay) % N
            g = gcd(den, N)
            if 1 < int(g) < int(N): return g
            if int(g) == int(N): ax, ay = None, None
            else:
                lam = (num * invert(den, N)) % N
                x3 = (lam*lam - ax - ax) % N
                y3 = (lam*(ax - x3) - ay) % N
                ax, ay = x3, y3
        k >>= 1
    return None

random.seed(int(time.time()))
trial = 0
while True:
    trial += 1
    a_curve = random.randint(1, 10000)
    b_curve = random.randint(1, 10000)
    # Find a point
    found = False
    for x_try in range(200):
        rhs = (x_try**3 + a_curve * x_try + b_curve) % int(N)
        y_try = int(isqrt(mpz(rhs)))
        if y_try * y_try == rhs:
            x, y = x_try, y_try
            found = True
            break
    if not found: continue
    
    for q in primes:
        e=1; pe=q
        while pe*q<=B1: pe*=q; e+=1
        g = ec_mul(pe, x, y, a_curve, N)
        if g is not None and 1 < int(g) < int(N):
            log(f'FACTOR FOUND! trial={trial}, a={a_curve}, b={b_curve}: {g} ({len(str(g))} digits)')
            log(f'is_prime: {is_prime(int(g))}')
            cof = int(N) // int(g)
            log(f'cofactor: {cof} ({len(str(cof))} digits)')
            log(f'is_prime(cofactor): {is_prime(cof)}')
            update_factors(int(g))
            log('Updated factors table!')
            sys.exit(0)
    
    if trial % 10 == 0:
        log(f'{trial} curves done')
