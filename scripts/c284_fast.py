#!/usr/bin/env python3
"""C284 ultra-fast sieve — pure Python, no numpy overhead."""

import sys
sys.set_int_max_str_digits(1000000)
import gmpy2
from gmpy2 import mpz, is_prime, powmod
import time, json, multiprocessing as mp, bisect
from pathlib import Path

P = 1229
TWO_P = 2458
C284 = mpz(53392955842462906502525256206896237530607657681405452248628829538140335056019091833139309039691476989536595672486245741799613486059460767317912672601233477410458189253022780891585730123223883909898404934891596729489833819787859139386557550548823481244976333432522178629028656984007087)

BASE = Path('/home/z/my-project/download')
CKPT = BASE / 'c284_fast_ckpt.json'
RESULTS = BASE / 'c284_fast_results.txt'

# Wheel: primes 3-19, mod 4849845
WP = [3,5,7,11,13,17,19]
WM = 1
for p in WP: WM *= p

# Precompute blocked residues for wheel
wb = {}
for r in WP:
    wb[r] = (-pow(TWO_P, -1, r)) % r

# Precompute good residues
import pickle
GF = Path('/home/z/my-project/download/good_residues_p1229.pkl')
if GF.exists():
    GOOD = pickle.load(open(GF, 'rb'))
else:
    GOOD = []
    for k in range(WM):
        ok = True
        for r in WP:
            if k % r == wb[r]:
                ok = False; break
        if ok: GOOD.append(k)
    pickle.dump(GOOD, open(GF, 'wb'))

SG = sorted(GOOD)
NG = len(SG)
STEPS = []
for i in range(NG):
    ni = (i+1) % NG
    STEPS.append((WM - SG[i] + SG[0]) if ni == 0 else (SG[ni] - SG[i]))

# Extra sieve: primes 23-997
import math
def small_primes(n):
    s = bytearray([1])*(n+1)
    s[0] = s[1] = 0
    for i in range(2, int(n**0.5)+1):
        if s[i]: s[i*i::i] = b'\x00'*len(s[i*i::i])
    return [i for i in range(2, n+1) if s[i]]

EXTRA = []
for r in small_primes(1000):
    if r == 2 or r == P or r in WP: continue
    EXTRA.append((r, (-pow(TWO_P, -1, r)) % r))

# Known factor k's to skip
KNOWN_KS = set()
for q in [36871, 46703, 10543179280661916121033, 9536289355314392579996071515160583098298616686033085857]:
    if (q-1) % TWO_P == 0: KNOWN_KS.add((q-1)//TWO_P)

def worker(args):
    wid, k_start, k_end = args
    wf = BASE / f'c284_fast_w{wid}.json'
    
    k = k_start
    km = k % WM
    idx = bisect.bisect_left(SG, km)
    if idx == NG: idx = 0; k += WM - km + SG[0]
    else: k += SG[idx] - km
    
    tested = primes = 0
    t0 = time.time()
    last_log = t0
    
    while k < k_end:
        if RESULTS.exists() and 'FACTOR' in RESULTS.read_text(): return
        
        # Extra sieve (fast Python loop with early exit)
        skip = False
        for r, b in []:
            if k % r == b:
                skip = True; break
        if not skip:
            tested += 1
            q = TWO_P * k + 1
            if is_prime(q):
                primes += 1
                if k not in KNOWN_KS:
                    if powmod(2, P, q) == 1:
                        if C284 % q == 0:
                            cof = int(C284) // q
                            open(RESULTS, 'a').write(
                                f"FACTOR FOUND!\nk={k}\nq={q}\nq_digits={len(str(q))}\n"
                                f"cofactor={cof}\ncofactor_digits={len(str(cof))}\n"
                                f"is_prime_cof={is_prime(cof)}\n"
                            )
                            print(f"\n!!! FACTOR! k={k} q={q} !!!", flush=True)
                            return
        
        k += STEPS[idx]
        idx = (idx + 1) % NG
        
        now = time.time()
        if now - last_log > 15:
            elapsed = now - t0
            rate = (k - k_start) / elapsed
            print(f"[W{wid}] k={k:,} tested={tested:,} primes={primes:,} rate={rate:.0f} k/s t={elapsed:.0f}s", flush=True)
            last_log = now
        
        if now - t0 > 30 and not (tested % 10000):
            json.dump({'wid': wid, 'last_k': k, 'tested': tested, 'primes': primes}, open(wf, 'w'))
    
    json.dump({'wid': wid, 'last_k': k, 'tested': tested, 'primes': primes, 'done': True}, open(wf, 'w'))
    print(f"[W{wid}] DONE k={k:,} tested={tested:,} primes={primes:,}", flush=True)

def main():
    print(f"C284 digits={len(str(C284))} mod4={C284%4}")
    
    NW = 4
    KS = 1
    KE = 10_000_000_000_000  # 10T
    
    sk = KS
    if CKPT.exists():
        cp = json.load(open(CKPT))
        sk = max(KS, cp.get('last_k', 0) + 1)
        print(f"Resume from k={sk:,}")
    
    print(f"Range: k=[{sk:,}, {KE:,}) Workers={NW}")
    
    for i in range(NW):
        wf = BASE / f'c284_fast_w{i}.json'
        if wf.exists(): wf.unlink()
    
    ck = (KE - sk) // NW
    ctx = mp.get_context('fork')
    workers = []
    for i in range(NW):
        ws = sk + i * ck
        we = KE if i == NW-1 else ws + ck
        p = ctx.Process(target=worker, args=((i, ws, we),))
        p.start(); workers.append(p)
        print(f"  W{i}: k=[{ws:,}, {we:,})")
    
    t0 = time.time()
    while any(p.is_alive() for p in workers):
        time.sleep(15)
        if RESULTS.exists() and 'FACTOR' in RESULTS.read_text():
            print("!!! FACTOR FOUND !!!")
            for p in workers:
                if p.is_alive(): p.terminate()
            break
        
        mk = tt = tp = 0
        for i in range(NW):
            wf = BASE / f'c284_fast_w{i}.json'
            if wf.exists():
                w = json.load(open(wf))
                mk = max(mk, w.get('last_k', 0))
                tt += w.get('tested', 0)
                tp += w.get('primes', 0)
        
        el = time.time() - t0
        r = (mk - sk) / el if el > 0 else 0
        eta = (KE - mk) / r / 3600 if r > 0 else float('inf')
        print(f"el={el:.0f}s k={mk:,} tested={tt:,} primes={tp:,} rate={r:.0f} k/s ETA={eta:.1f}h", flush=True)
        
        if time.time() - t0 > 60:
            json.dump({'last_k': mk, 'ts': time.strftime('%H:%M:%S'), 'tested': tt, 'primes': tp}, open(CKPT, 'w'))
    
    for p in workers:
        if p.is_alive(): p.join(5)
    
    if RESULTS.exists() and 'FACTOR' in RESULTS.read_text():
        print(RESULTS.read_text())
    else:
        print("No factor found.")

if __name__ == '__main__':
    main()
