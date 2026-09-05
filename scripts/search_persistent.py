#!/usr/bin/env python3
"""
Persistent search for smallest factor of M(1277), M(1619), M(1753).
- Saves checkpoint every chunk
- Logs progress every chunk  
- Queries factordb periodically for any newly-discovered factors
- Resumable from checkpoint
"""
import time
import sys
import json
import os
import urllib.request
import re
import gmpy2
from gmpy2 import is_prime as gmpy_is_prime
import numpy as np

# Force line buffering
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

OUTPUT = '/home/z/my-project/download/A136030_1_to_8000.txt'
CHECKPOINT = '/home/z/my-project/scripts/search_ckpt.json'
LOG = '/home/z/my-project/scripts/search_live.log'

# 3 small missing values
TARGETS = [(192, 1277), (241, 1619), (258, 1753)]

# Long time budget
TOTAL_BUDGET = 5000  # ~83 min

def log(msg):
    ts = time.strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    with open(LOG, 'a') as f:
        f.write(line + "\n")
    print(line, flush=True)

def query_factordb(p):
    """Check factordb for known factors of M(p)."""
    try:
        num = (1 << p) - 1
        url = f"http://factordb.com/api?query={num}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))
        status = data.get('status')
        factors = data.get('factors', [])
        if status == 'FF' or status == 'CF':
            # Some factors known
            if factors:
                # smallest factor
                smallest = min(int(f[0]) for f in factors if f[0].isdigit())
                return smallest
        return None
    except Exception as e:
        log(f"  factordb error for M({p}): {e}")
        return None

def build_small_primes(limit=5000):
    sa = np.ones(limit + 1, dtype=bool)
    sa[0] = sa[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sa[i]:
            sa[i*i::i] = False
    return [int(i) for i in np.flatnonzero(sa)]

def search_chunk(p, k_start, k_end, small_primes):
    """Search one chunk for factor of M(p). Returns (factor, last_k_checked)."""
    p_mod4 = p & 3
    valid_residues = (0, 3) if p_mod4 == 1 else (0, 1)
    two_p = 2 * p
    size = k_end - k_start
    is_composite = np.zeros(size, dtype=bool)
    
    for r in small_primes:
        if r == 2: continue
        t = two_p % r
        if t == 0: continue
        try:
            inv = pow(int(t), -1, r)
        except: continue
        k_0 = (-inv) % r
        if k_0 < k_start:
            offset = (k_start - k_0 + r - 1) // r
            k_0 = k_0 + offset * r
        if k_0 >= k_end: continue
        idx = k_0 - k_start
        is_composite[idx::r] = True
    
    for i in range(size):
        k = k_start + i
        if (k & 3) not in valid_residues: continue
        if is_composite[i]: continue
        q = 2 * k * p + 1
        if gmpy_is_prime(q) and pow(2, p, q) == 1:
            return q, k
    
    return None, k_end - 1

def save_seq(seq):
    with open(OUTPUT, 'w') as f:
        for i in range(1, 8001):
            f.write(f"{i}\t{seq[i]}\n")

def main():
    open(LOG, 'w').close()
    log("=" * 60)
    log("جستجوی پایدار عوامل گمشده Mersenne")
    log(f"اهداف: M(1277), M(1619), M(1753)")
    log(f"بودجه کل: {TOTAL_BUDGET}s ({TOTAL_BUDGET/60:.1f} min)")
    log("=" * 60)
    
    # Load sequence
    seq = {}
    with open(OUTPUT) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                seq[int(parts[0])] = int(parts[1])
    
    # Load checkpoint
    ckpt = {}
    try:
        with open(CHECKPOINT) as f:
            ckpt = json.load(f)
        log(f"چکپوینت بارگذاری شد: {len(ckpt)} کلید")
    except:
        pass
    
    # Build small primes
    log("ساخت سیو اعداد اول...")
    small_primes = build_small_primes(5000)
    log(f"  {len(small_primes)} عدد اول کوچک")
    
    t_start = time.time()
    K_LIMIT = 5 * 10**9  # 5 billion - q up to ~10^13
    chunk_size = 5 * 10**7  # 50M per chunk = ~15s per chunk
    
    log(f"K_LIMIT = {K_LIMIT:,}, chunk_size = {chunk_size:,}")
    
    for idx, p in TARGETS:
        elapsed = time.time() - t_start
        if elapsed > TOTAL_BUDGET:
            log(f"⏰ بودجه کل تمام شد")
            break
        
        log("")
        log(f"=== پردازش M({p}) [idx={idx}] ===")
        log(f"  مقدار فعلی: {seq[idx]}")
        
        # Check factordb first
        log(f"  بررسی factordb...")
        fdb_factor = query_factordb(p)
        if fdb_factor:
            log(f"  ✓ factordb عامل دارد: {fdb_factor}")
            seq[idx] = fdb_factor
            save_seq(seq)
            continue
        else:
            log(f"  ✗ factordب هیچ عاملی ندارد (status=C)")
        
        # Get checkpoint position
        ckpt_key = f"{idx}_k"
        k_start = ckpt.get(ckpt_key, 1)
        log(f"  ادامه از k={k_start:,}")
        log(f"  max q = {2*K_LIMIT*p+1:.2e}")
        
        # Time budget for this prime
        per_prime_budget = (TOTAL_BUDGET - elapsed) / max(1, len(TARGETS) - TARGETS.index((idx, p)))
        log(f"  بودجه این عدد: {per_prime_budget:.0f}s")
        
        # Search
        found = False
        chunk_count = 0
        for chunk_start in range(k_start, K_LIMIT + 1, chunk_size):
            chunk_end = min(chunk_start + chunk_size, K_LIMIT + 1)
            
            factor, last_k = search_chunk(p, chunk_start, chunk_end, small_primes)
            chunk_count += 1
            
            if factor:
                elapsed = time.time() - t_start
                log(f"  *** ✓ پیدا شد! M({p}) = {factor} (k={last_k}, time={elapsed:.0f}s)")
                seq[idx] = factor
                save_seq(seq)
                ckpt[str(idx)] = factor
                with open(CHECKPOINT, 'w') as f:
                    json.dump(ckpt, f)
                found = True
                break
            
            # Save checkpoint
            ckpt[ckpt_key] = chunk_end - 1
            with open(CHECKPOINT, 'w') as f:
                json.dump(ckpt, f)
            
            # Progress report
            elapsed = time.time() - t_start
            max_q = 2 * (chunk_end - 1) * p + 1
            log(f"  چانک {chunk_count}: k={chunk_end-1:,}, max_q={max_q:.2e}, time={elapsed:.0f}s")
            
            if elapsed - t_start > 0 and (time.time() - t_start) > elapsed + per_prime_budget:
                log(f"  بودجه این عدد تمام شد")
                break
            
            total_elapsed = time.time() - t_start
            if total_elapsed > TOTAL_BUDGET:
                log(f"  ⏰ بودجه کل تمام شد")
                break
        
        if not found:
            log(f"  ✗ برای M({p}) عامل پیدا نشد (تا k={ckpt.get(ckpt_key, 0):,})")
    
    # Final report
    log("")
    log("=" * 60)
    log("گزارش نهایی:")
    log(f"  idx 192 (M(1277)): {seq[192]}")
    log(f"  idx 241 (M(1619)): {seq[241]}")
    log(f"  idx 258 (M(1753)): {seq[258]}")
    log(f"  کل زمان: {time.time()-t_start:.0f}s")
    log("=" * 60)

if __name__ == "__main__":
    main()
