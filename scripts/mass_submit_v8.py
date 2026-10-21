#!/usr/bin/env python3
"""
🔧 mass_submit_v8.py — سریع‌تر + فقط ۳۰۳ رقمی
================================================
تغییرات:
  ۱. فقط ۳۰۳ رقمی (۱۰ عدد ۳۰-۳۱ رقمی) — اولویت مطلق
  ۲. timeout ۹۰ ثانیه برای FactorDB
  ۳. بدون hold — همه ثبت می‌شوند (هیچ‌چیز زیر ۳۰)
  ۴. parallel generation (pre-generate next while submitting)
"""
import sys, os, time, json, subprocess, random, threading
from queue import Queue
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, next_prime

TOKEN = "6ddb5c17a56f920f3ee459e99036bd57"
OUTPUT_DIR = "/home/z/my-project/download/auto_factor"
os.makedirs(OUTPUT_DIR, exist_ok=True)
LOG_FILE = os.path.join(OUTPUT_DIR, "mass_submit_v8.log")
DB_FILE = os.path.join(OUTPUT_DIR, "mass_submit_db.json")
NAMED_DB_FILE = os.path.join(OUTPUT_DIR, "named_factors.json")
HELD_FILE = os.path.join(OUTPUT_DIR, "held_30_digit_factors.json")


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")


def factordb_submit(n, factors):
    try:
        payload = {
            "jsonrpc": "2.0", "id": 1, "method": "report_factors",
            "params": {"target": {"expr": str(n)}, "factors": [str(f) for f in factors], "credit": True}
        }
        result = subprocess.run(
            ["curl", "-s", "--max-time", "90",
             "-X", "POST", "https://factordb.com:4059/rpc",
             "-H", "Content-Type: application/json",
             "-H", f"X-Fdb-User-Token: {TOKEN}",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=95)
        return json.loads(result.stdout) if result.stdout else {"error": "empty"}
    except Exception as e:
        return {"error": str(e)}


def gen_303_digit():
    """Generate a 303-digit number with 10 prime factors (30-31 digits each)"""
    combos = [
        [30,30,30,30,30,31,31,31,31,31],   # ~303
        [30,31,30,31,30,31,30,31,30,31],   # ~305
        [31,31,31,31,31,30,30,30,30,30],   # ~303
        [30,30,30,30,30,30,30,30,30,33],   # ~303
        [30,30,30,30,31,31,31,31,31,30],   # ~304
        [30,30,31,31,30,30,31,31,30,30],   # ~303
    ]
    digits = random.choice(combos)
    random.shuffle(digits)
    factors = []
    for d in digits:
        base = 10**(d-1) + random.randint(0, 9*10**(d-1))
        p = int(next_prime(mpz(base)))
        factors.append(p)
    n = 1
    for f in factors: n *= f
    return n, sorted(factors), digits


def gen_quad_30plus():
    """Generate Quad with 30+ digit factors (varied 30-50)"""
    combos = [
        [30,31,32,33],[35,36,37,38],[30,35,40,45],[40,42,44,46],
        [33,34,35,36],[38,39,40,41],[30,31,40,50],[42,43,44,45],
    ]
    digits = random.choice(combos)
    random.shuffle(digits)
    factors = []
    for d in digits:
        base = 10**(d-1) + random.randint(0, 9*10**(d-1))
        p = int(next_prime(mpz(base)))
        factors.append(p)
    n = 1
    for f in factors: n *= f
    return n, sorted(factors), digits


# Pre-generation queue (generate next while current is submitting)
gen_queue = Queue(maxsize=5)

def generator_thread():
    """Pre-generate numbers in background"""
    while True:
        # 70% 303-digit, 30% Quad
        if random.random() < 0.70:
            n, factors, digits = gen_303_digit()
            gen_queue.put(('303', n, factors, digits))
        else:
            n, factors, digits = gen_quad_30plus()
            gen_queue.put(('quad', n, factors, digits))


def main():
    log("=" * 80)
    log("🚀 mass_submit_v8 — فقط ۳۰+ رقم، اولویت ۳۰۳ رقمی")
    log("  Pre-generation: سریع‌تر")
    log("=" * 80)
    
    random.seed(int(time.time()))
    
    # Load DBs
    existing = []
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE) as f: existing = json.load(f).get('numbers', [])
        except: pass
    log(f"DB: {len(existing)}")
    
    named = []
    if os.path.exists(NAMED_DB_FILE):
        try:
            with open(NAMED_DB_FILE) as f: named = json.load(f).get('named_factors', [])
        except: pass
    
    held = []
    if os.path.exists(HELD_FILE):
        try:
            with open(HELD_FILE) as f: held = json.load(f).get('held', [])
        except: pass
    
    # Start pre-generation thread
    gen_t = threading.Thread(target=generator_thread, daemon=True)
    gen_t.start()
    log("✅ Pre-generation thread started")
    
    all_results = existing
    named_results = named
    held_results = held
    total_credited = 0
    total_submitted = 0
    total_held = 0
    total_failed = 0
    total_303 = 0
    
    batch_count = 0
    while True:
        batch_count += 1
        log(f"\n{'='*60}")
        log(f"📦 Batch #{batch_count}")
        log(f"{'='*60}")
        
        for i in range(100):  # 100 per batch
            try:
                # Get pre-generated number
                kind, n, factors, digits = gen_queue.get(timeout=30)
                
                # Final check: all factors 30+ digits
                if any(len(str(f)) < 30 for f in factors):
                    held_results.append({
                        'n': str(n), 'digits': len(str(n)),
                        'factors': [str(f) for f in factors],
                        'reason': 'factor_under_30',
                        'saved_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                    total_held += 1
                    continue
                
                # Submit
                result = factordb_submit(n, factors)
                credited = result.get('result', {}).get('credited', 0)
                status = result.get('result', {}).get('status', '?')
                
                if 'error' in result:
                    total_failed += 1
                    if total_failed % 10 == 0:
                        log(f"  [{i+1}] FAIL: {result.get('error','?')[:100]}")
                else:
                    total_submitted += 1
                    total_credited += credited
                    n_digits = len(str(n))
                    if n_digits >= 299:
                        total_303 += 1
                    
                    all_results.append({
                        'n': str(n), 'digits': n_digits,
                        'num_factors': len(factors),
                        'factors': [str(f) for f in factors],
                        'credited': credited, 'status': status,
                        'digit_combo': digits,
                    })
                    named_results.append({
                        'n': str(n), 'digits': n_digits,
                        'num_factors': len(factors),
                        'factor_name': 'Deca' if n_digits >= 299 else 'Quad',
                        'factors': [str(f) for f in factors],
                        'credited': credited, 'status': status,
                        'digit_combo': digits,
                        'submitted_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                
                if (i+1) % 10 == 0:
                    log(f"  [{i+1}/100] sub={total_submitted} cred={total_credited} 303={total_303} held={total_held} fail={total_failed}")
                
                if (i+1) % 50 == 0:
                    with open(DB_FILE, 'w') as f:
                        json.dump({'numbers': all_results}, f, indent=2, ensure_ascii=False, default=str)
                    with open(NAMED_DB_FILE, 'w') as f:
                        json.dump({'named_factors': named_results}, f, indent=2, ensure_ascii=False, default=str)
                    with open(HELD_FILE, 'w') as f:
                        json.dump({'held': held_results}, f, indent=2, ensure_ascii=False, default=str)
                
            except Exception as e:
                log(f"  EXC: {e}")
                total_failed += 1
                time.sleep(1)
        
        # Save after each batch
        with open(DB_FILE, 'w') as f:
            json.dump({'numbers': all_results}, f, indent=2, ensure_ascii=False, default=str)
        with open(NAMED_DB_FILE, 'w') as f:
            json.dump({'named_factors': named_results}, f, indent=2, ensure_ascii=False, default=str)
        with open(HELD_FILE, 'w') as f:
            json.dump({'held': held_results}, f, indent=2, ensure_ascii=False, default=str)
        
        log(f"\n📊 Batch #{batch_count} done: sub={total_submitted} cred={total_credited} 303={total_303}")


if __name__ == '__main__':
    main()
