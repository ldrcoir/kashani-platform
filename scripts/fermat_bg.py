#!/usr/bin/env python3
"""Fermat on disc = 16*N with Pell equation. Uses CORRECT N = M(1237)//F1."""
import sys; sys.set_int_max_str_digits(1000000)
import gmpy2; from gmpy2 import mpz, isqrt, gcd, is_prime
import time, json
from pathlib import Path

BASE = Path('/home/z/my-project')
LOG = BASE / 'logs/fermat_bg.log'
STATE = BASE / 'logs/fermat_state.json'
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'

M = mpz(2)**1237 - 1
F1 = mpz(2538207129840687799335203259492870476186248896616401346500027311795983)
N = M // F1

# disc = 16*N, Pell: (e-4948d)(e+4948d) = 16*N
# Fermat: x^2 - 16*N = y^2, step = 9896, x ≡ B/2 mod 4948
target = 16 * int(N)
step = 9896
B_val = 277092  # = 2*56*2474 + 4
target_mod = (B_val // 2) % 4948  # = 138546 mod 4948

def log(msg):
    t = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{t}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f: f.write(line + '\n')

def save_state(x, checked):
    STATE.write_text(json.dumps({'x': str(x), 'checked': checked, 'ts': time.strftime('%Y-%m-%d %H:%M:%S')}))

def load_state():
    if STATE.exists():
        s = json.loads(STATE.read_text())
        return mpz(s['x']), s['checked']
    return None, 0

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

x, checked = load_state()
if x is None:
    x = isqrt(mpz(target))
    if x * x < target: x += 1
    x_mod = int(x) % 4948
    if x_mod != target_mod: x += (target_mod - x_mod) % 4948
    checked = 0

remainder = x * x - target
log(f'Fermat on 16*N (CORRECT N), step={step}, checked={checked}')

t_start = time.time()
while True:
    if remainder >= 0:
        y = isqrt(remainder)
        if y * y == remainder:
            f1 = int(x - y)
            f2 = int(x + y)
            log(f'>>> FOUND at iter {checked}! (x-y)={len(str(f1))}d (x+y)={len(str(f2))}d')
            # Extract q1, q2
            for a in [1,2,4,8,16]:
                if f1 % a == 0 and f2 % (16//a) == 0:
                    q1 = f1 // a
                    q2 = f2 // (16//a)
                    if q1 * q2 == int(N) and q1 > 1 and q2 > 1:
                        log(f'>>> N = {q1} * {q2}')
                        log(f'q1 is_prime: {is_prime(q1)}, q2 is_prime: {is_prime(q2)}')
                        update_factors(min(q1, q2))
                        sys.exit(0)
            g = gcd(f1, int(N))
            if 1 < int(g) < int(N) and int(M) % int(g) == 0:
                log(f'FACTOR via gcd: {g}')
                update_factors(int(g))
                sys.exit(0)
            g = gcd(f2, int(N))
            if 1 < int(g) < int(N) and int(M) % int(g) == 0:
                log(f'FACTOR via gcd: {g}')
                update_factors(int(g))
                sys.exit(0)
    remainder += 2 * step * x + step * step
    x += step
    checked += 1
    if checked % 100000 == 0:
        elapsed = time.time() - t_start
        log(f'iter={checked}, rate={100000/elapsed:.0f}/s, range={checked*step}')
        t_start = time.time()
    if checked % 1000000 == 0:
        save_state(x, checked)
