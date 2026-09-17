#!/usr/bin/env python3
"""
Fermat factorization on 16*N with modular constraint.
Runs persistently, saves state, logs progress.
Based on disc = 16*N discovery.
"""
import sys
sys.set_int_max_str_digits(1000000)
import gmpy2
from gmpy2 import mpz, isqrt, gcd, is_prime
import time
import json
from pathlib import Path

BASE = Path('/home/z/my-project')
LOG = BASE / 'logs/fermat_bg.log'
STATE = BASE / 'logs/fermat_state.json'
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'

N = mpz(932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281199369604215535391846857906233364905825622441048803673998858526737)

target = 16 * N
step = 39584
target_mod = 69276 % step

def log(msg):
    t = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{t}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')

def save_state(x, checked):
    state = {'x': str(x), 'checked': checked, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}
    STATE.write_text(json.dumps(state))

def load_state():
    if STATE.exists():
        s = json.loads(STATE.read_text())
        return mpz(s['x']), s['checked']
    return None, 0

def update_factor_file(factor):
    lines = FACTORS_FILE.read_text().splitlines(keepends=True)
    out = []
    for line in lines:
        if line.startswith('#'):
            out.append(line); continue
        parts = line.split('\t')
        if len(parts) >= 2 and parts[0] == '1237':
            cur = parts[1].strip()
            if cur == '-1' or factor < int(cur):
                out.append(f'1237\t{factor}\n')
            else:
                out.append(line)
        else:
            out.append(line)
    FACTORS_FILE.write_text(''.join(out))

# Load state or initialize
x, checked = load_state()
if x is None:
    x = isqrt(target)
    if x * x < target:
        x += 1
    x_mod = int(x) % step
    if x_mod != target_mod:
        x += (target_mod - x_mod) % step
    checked = 0

remainder = x * x - target
log(f'Starting Fermat: x has {len(str(x))} digits, checked={checked}')

t_start = time.time()
batch_save = 1_000_000  # Save state every 1M iterations
batch_log = 100_000  # Log every 100K

while True:
    if remainder >= 0:
        y = isqrt(remainder)
        if y * y == remainder:
            factor1 = int(x - y)
            factor2 = int(x + y)
            log(f'>>> FOUND at iteration {checked}!')
            log(f'  (x-y) = {factor1} ({len(str(factor1))} digits)')
            log(f'  (x+y) = {factor2} ({len(str(factor2))} digits)')
            # Try to extract factors of N
            for a in [1, 2, 4, 8, 16]:
                if factor1 % a == 0 and factor2 % (16 // a) == 0:
                    q1 = factor1 // a
                    q2 = factor2 // (16 // a)
                    if q1 * q2 == int(N) and q1 > 1 and q2 > 1:
                        log(f'  >>> N = {q1} * {q2}')
                        log(f'  q1 is_prime: {is_prime(q1)}')
                        log(f'  q2 is_prime: {is_prime(q2)}')
                        smallest = min(q1, q2)
                        update_factor_file(smallest)
                        log('  Updated factors table!')
                        sys.exit(0)
            # Try gcd
            g = gcd(factor1, int(N))
            if 1 < int(g) < int(N):
                log(f'  FACTOR via gcd: {g} ({len(str(g))} digits)')
                log(f'  is_prime: {is_prime(int(g))}')
                update_factor_file(int(g))
                sys.exit(0)
            g = gcd(factor2, int(N))
            if 1 < int(g) < int(N):
                log(f'  FACTOR via gcd: {g} ({len(str(g))} digits)')
                update_factor_file(int(g))
                sys.exit(0)
            # Even if direct extraction fails, the factorization is found
            log(f'  Factorization found but extraction failed - manual analysis needed')
            sys.exit(0)
    
    remainder += 2 * step * x + step * step
    x += step
    checked += 1
    
    if checked % batch_log == 0:
        elapsed = time.time() - t_start
        rate = batch_log / elapsed if elapsed > 0 else 0
        search_range = checked * step
        log(f'iter={checked}, rate={rate:.0f}/s, x_range={search_range} ({len(str(search_range))} digits)')
        t_start = time.time()
    
    if checked % batch_save == 0:
        save_state(x, checked)
        # Also save to worklog
