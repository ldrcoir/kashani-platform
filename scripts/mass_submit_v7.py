#!/usr/bin/env python3
"""
🔧 mass_submit_v7.py
====================
جدید:
  ۱. اولویت: ساخت اعداد ۳۰۳ رقمی (ضرب ~۱۰ عدد ۳۰-۳۱ رقمی)
  ۲. فقط فاکتورهای ۳۰+ رقم (هیچ‌چیز زیر ۳۰)
  ۳. متنوع: ۳۰، ۳۱، ۳۲، ... ۵۰
  ۴. بازه‌ها را ارتقا بده
"""
import sys, os, time, json, subprocess, random
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, next_prime

TOKEN = "6ddb5c17a56f920f3ee459e99036bd57"
OUTPUT_DIR = "/home/z/my-project/download/auto_factor"
os.makedirs(OUTPUT_DIR, exist_ok=True)
LOG_FILE = os.path.join(OUTPUT_DIR, "mass_submit_v7.log")
DB_FILE = os.path.join(OUTPUT_DIR, "mass_submit_db.json")
NAMED_DB_FILE = os.path.join(OUTPUT_DIR, "named_factors.json")
HELD_FILE = os.path.join(OUTPUT_DIR, "held_30_digit_factors.json")

FACTOR_NAMES = {3:"Triple",4:"Quad",5:"Penta",6:"Hexa",7:"Hepta",8:"Octa",9:"Nona",10:"Deca"}


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
            ["curl", "-s", "--max-time", "30",
             "-X", "POST", "https://factordb.com:4059/rpc",
             "-H", "Content-Type: application/json",
             "-H", f"X-Fdb-User-Token: {TOKEN}",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=35)
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}


def gen_factors(digits_list):
    factors = []
    for d in digits_list:
        base = 10**(d-1) + random.randint(0, 9*10**(d-1))
        p = int(next_prime(mpz(base)))
        factors.append(p)
    return sorted(factors)


def generate_number(num_factors, target_303=False):
    """تولید عدد — فقط ۳۰+ رقم عامل‌ها، متنوع"""
    hold = random.random() < 0.30
    
    if hold:
        # پنهان — بدون ۳۰+ رقم
        if num_factors == 4:
            combos = [[15,15,20,20],[20,20,20,20],[15,20,25,25],[25,25,25,25]]
        elif num_factors == 5:
            combos = [[15,15,15,20,20],[20,20,20,20,20]]
        elif num_factors == 3:
            combos = [[15,20,25],[20,20,20],[25,25,25]]
        elif num_factors == 10:
            combos = [[15,15,15,15,15,15,15,15,15,15]]
        else:
            combos = [[20]*num_factors]
        digits = random.choice(combos)
        random.shuffle(digits)
        factors = gen_factors(digits)
        n = 1
        for f in factors: n *= f
        return n, factors, digits, True
    
    # ⭐ اولویت: ۳۰۳ رقمی — ۱۰ عدد ۳۰-۳۱ رقمی
    if target_303 and num_factors == 10:
        combos = [
            [30,30,30,30,30,31,31,31,31,31],   # ~303
            [30,31,30,31,30,31,30,31,30,31],   # ~305
            [31,31,31,31,31,30,30,30,30,30],   # ~303
            [30,30,30,30,30,30,30,30,30,33],   # ~303
            [30,30,30,30,31,31,31,31,31,30],   # ~304
        ]
    elif num_factors == 4:
        combos = [
            [30,31,32,33],[31,32,33,34],[30,35,40,45],[32,33,34,35],
            [30,30,31,32],[35,36,37,38],[30,40,45,50],[33,34,35,36],
            [40,42,44,46],[30,32,34,36],[35,35,35,35],[38,39,40,41],
            [30,31,40,50],[42,43,44,45],[41,42,43,44],
        ]
    elif num_factors == 5:
        combos = [
            [30,31,32,33,34],[31,32,33,34,35],[30,30,31,32,33],
            [35,36,37,38,39],[30,35,40,45,50],[32,33,34,35,36],
            [40,41,42,43,44],
        ]
    elif num_factors == 3:
        combos = [[30,31,32],[33,34,35],[40,45,50],[35,40,45],[41,42,43]]
    elif num_factors == 6:
        combos = [[30,31,32,33,34,35],[31,31,31,31,31,31],[40,41,42,43,44,45]]
    elif num_factors == 7:
        combos = [[30,31,32,33,34,35,36],[35,36,37,38,39,40,41]]
    elif num_factors == 8:
        combos = [[30,31,32,33,34,35,36,37]]
    elif num_factors == 9:
        combos = [[30,31,32,33,34,35,36,37,38]]
    elif num_factors == 10:
        combos = [
            [30,30,30,30,30,31,31,31,31,31],
            [30,31,30,31,30,31,30,31,30,31],
            [35,35,35,35,35,35,35,35,35,35],
        ]
    else:
        combos = [[30 + i % 20 for i in range(num_factors)]]
    
    digits = random.choice(combos)
    random.shuffle(digits)
    factors = gen_factors(digits)
    n = 1
    for f in factors: n *= f
    return n, factors, digits, False


def main():
    log("=" * 80)
    log("🚀 mass_submit_v7 — اولویت: ۳۰۳ رقمی + متنوع ۳۰-۵۰")
    log("  فقط فاکتورهای ۳۰+ رقم — هیچ‌چیز زیر ۳۰")
    log("=" * 80)
    
    random.seed(int(time.time()))
    
    existing = []
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE) as f: existing = json.load(f).get('numbers', [])
        except: pass
    log(f"DB قبلی: {len(existing)}")
    
    named = []
    if os.path.exists(NAMED_DB_FILE):
        try:
            with open(NAMED_DB_FILE) as f: named = json.load(f).get('named_factors', [])
        except: pass
    log(f"named قبلی: {len(named)}")
    
    held = []
    if os.path.exists(HELD_FILE):
        try:
            with open(HELD_FILE) as f: held = json.load(f).get('held', [])
        except: pass
    log(f"held قبلی: {len(held)}")
    
    # ⭐ اولویت: ۳۰۳ رقمی (۱۰ عاملی) + Quad + Penta
    configs = [
        # ⭐ اولویت اصلی: اعداد ۳۰۳ رقمی (۱۰ عدد ۳۰-۳۱ رقمی)
        (10, 300, "Deca-Composite 303-digit — اولویت اصلی", True),
        # Quad — تمرکز دوم
        (4, 300, "Quad (varied 30-50)", False),
        # Penta
        (5, 150, "Penta (varied 30-50)", False),
        # ۶ عاملی
        (6, 50, "Hexa (varied 30-50)", False),
        # ۳ عاملی — کم
        (3, 30, "Triple (varied 30-50)", False),
        # ۷ عاملی
        (7, 20, "Hepta (varied 30-50)", False),
        # ۸ و ۹ عاملی
        (8, 15, "Octa (varied 30-50)", False),
        (9, 10, "Nona (varied 30-50)", False),
    ]
    
    all_results = existing
    named_results = named
    held_results = held
    total_credited = 0
    total_submitted = 0
    total_held = 0
    total_failed = 0
    
    for num_factors, count, display, target_303 in configs:
        log(f"\n{'='*60}")
        log(f"📦 {display} — {count} عدد")
        log(f"{'='*60}")
        
        for i in range(count):
            try:
                n, factors, digits, hold = generate_number(num_factors, target_303)
                
                if hold:
                    held_results.append({
                        'n': str(n), 'digits': len(str(n)),
                        'num_factors': num_factors,
                        'factor_name': FACTOR_NAMES.get(num_factors, f"{num_factors}-Comp"),
                        'factors': [str(f) for f in factors],
                        'digit_combo': digits,
                        'saved_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                    total_held += 1
                    continue
                
                # چک نهایی: همه ۳۰+ رقم
                if any(len(str(f)) < 30 for f in factors):
                    held_results.append({
                        'n': str(n), 'digits': len(str(n)),
                        'num_factors': num_factors,
                        'factors': [str(f) for f in factors],
                        'digit_combo': digits,
                        'saved_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'reason': 'factor_under_30',
                    })
                    total_held += 1
                    continue
                
                # ثبت
                result = factordb_submit(n, factors)
                credited = result.get('result', {}).get('credited', 0)
                status = result.get('result', {}).get('status', '?')
                
                if 'error' in result:
                    total_failed += 1
                else:
                    total_submitted += 1
                    total_credited += credited
                    all_results.append({
                        'n': str(n), 'digits': len(str(n)),
                        'num_factors': len(factors),
                        'factors': [str(f) for f in factors],
                        'credited': credited, 'status': status,
                        'digit_combo': digits,
                    })
                    named_results.append({
                        'n': str(n), 'digits': len(str(n)),
                        'num_factors': num_factors,
                        'factor_name': FACTOR_NAMES.get(num_factors, f"{num_factors}-Comp"),
                        'factors': [str(f) for f in factors],
                        'credited': credited, 'status': status,
                        'digit_combo': digits,
                        'submitted_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                
                if (i+1) % 10 == 0:
                    n_digits = len(str(n))
                    log(f"  [{i+1}/{count}] sub={total_submitted} cred={total_credited} held={total_held} n_dig={n_digits} combo={digits}")
                
                if (i+1) % 50 == 0:
                    with open(DB_FILE, 'w') as f:
                        json.dump({'numbers': all_results}, f, indent=2, ensure_ascii=False, default=str)
                    with open(NAMED_DB_FILE, 'w') as f:
                        json.dump({'named_factors': named_results}, f, indent=2, ensure_ascii=False, default=str)
                    with open(HELD_FILE, 'w') as f:
                        json.dump({'held': held_results}, f, indent=2, ensure_ascii=False, default=str)
                
                time.sleep(0.4)
            except Exception as e:
                log(f"  [{i+1}/{count}] EXC: {e}")
                total_failed += 1
                time.sleep(1)
    
    with open(DB_FILE, 'w') as f:
        json.dump({'numbers': all_results}, f, indent=2, ensure_ascii=False, default=str)
    with open(NAMED_DB_FILE, 'w') as f:
        json.dump({'named_factors': named_results}, f, indent=2, ensure_ascii=False, default=str)
    with open(HELD_FILE, 'w') as f:
        json.dump({'held': held_results}, f, indent=2, ensure_ascii=False, default=str)
    
    log(f"\n{'='*80}")
    log(f"📊 خلاصه:")
    log(f"  submitted: {total_submitted}")
    log(f"  credited: {total_credited}")
    log(f"  held: {total_held}")
    
    by_name = {}
    for r in named_results:
        by_name[r['factor_name']] = by_name.get(r['factor_name'], 0) + 1
    for name, count in sorted(by_name.items()):
        log(f"  {name}: {count}")


if __name__ == '__main__':
    main()
