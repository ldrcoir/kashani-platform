#!/usr/bin/env python3
"""
🔧 mass_submit_v6.py
====================
قوانین کاربر:
  ۱. هیچ فاکتور زیر ۳۰ رقم ثبت نشود
  ۲. همه ۳۰ رقمی نباشد — متنوع: ۳۱، ۳۲، ۳۳، ... ۵۰
  ۳. تمرکز روی ۴ و ۵ عاملی
  ۴. ۳۰٪ پنهان → ذخیره محلی
"""
import sys, os, time, json, subprocess, random
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, next_prime

TOKEN = "6ddb5c17a56f920f3ee459e99036bd57"
OUTPUT_DIR = "/home/z/my-project/download/auto_factor"
os.makedirs(OUTPUT_DIR, exist_ok=True)
LOG_FILE = os.path.join(OUTPUT_DIR, "mass_submit_v6.log")
DB_FILE = os.path.join(OUTPUT_DIR, "mass_submit_db.json")
NAMED_DB_FILE = os.path.join(OUTPUT_DIR, "named_factors.json")
HELD_FILE = os.path.join(OUTPUT_DIR, "held_30_digit_factors.json")

FACTOR_NAMES = {3: "Triple", 4: "Quad", 5: "Penta", 6: "Hexa", 7: "Hepta", 8: "Octa"}


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
    """تولید عامل‌ها — همه باید ۳۰+ رقم باشند (برای ثبت)"""
    factors = []
    for d in digits_list:
        base = 10**(d-1) + random.randint(0, 9*10**(d-1))
        p = int(next_prime(mpz(base)))
        factors.append(p)
    return sorted(factors)


def generate_number(num_factors):
    """تولید عدد — فقط ۳۰+ رقم عامل‌ها، متنوع (۳۱-۵۰)"""
    hold = random.random() < 0.30  # 30% hold locally
    
    if hold:
        # پنهان — بدون ۳۰+ رقم → ذخیره محلی
        if num_factors == 4:
            combos = [[15,15,20,20], [20,20,20,20], [15,20,25,25], [25,25,25,25], [18,22,20,25]]
        elif num_factors == 5:
            combos = [[15,15,15,20,20], [20,20,20,20,20], [18,22,20,25,20]]
        elif num_factors == 3:
            combos = [[15,20,25], [20,20,20], [25,25,25], [18,22,20]]
        else:
            combos = [[20]*num_factors]
        digits = random.choice(combos)
        random.shuffle(digits)
        factors = gen_factors(digits)
        n = 1
        for f in factors: n *= f
        return n, factors, digits, True
    
    # ثبت — همه ۳۰+ رقم ولی متنوع (۳۰، ۳۱، ۳۲، ... ۵۰)
    if num_factors == 4:
        combos = [
            [30, 31, 32, 33],   # 126
            [31, 32, 33, 34],   # 130
            [30, 35, 40, 45],   # 150
            [32, 33, 34, 35],   # 134
            [30, 30, 31, 32],   # 123
            [35, 36, 37, 38],   # 146
            [30, 40, 45, 50],   # 165
            [33, 34, 35, 36],   # 138
            [31, 31, 31, 31],   # 124
            [40, 42, 44, 46],   # 172
            [30, 32, 34, 36],   # 132
            [35, 35, 35, 35],   # 140
            [30, 31, 40, 50],   # 151
            [38, 39, 40, 41],   # 158
            [30, 30, 30, 31],   # 121
            [42, 43, 44, 45],   # 174
        ]
    elif num_factors == 5:
        combos = [
            [30, 31, 32, 33, 34],   # 160
            [31, 32, 33, 34, 35],   # 165
            [30, 30, 31, 32, 33],   # 156
            [35, 36, 37, 38, 39],   # 185
            [30, 35, 40, 45, 50],   # 200
            [32, 33, 34, 35, 36],   # 170
        ]
    elif num_factors == 3:
        combos = [
            [30, 31, 32],   # 93
            [33, 34, 35],   # 102
            [40, 45, 50],   # 135
            [31, 32, 33],   # 96
            [35, 40, 45],   # 120
        ]
    elif num_factors == 6:
        combos = [
            [30, 31, 32, 33, 34, 35],
            [31, 31, 31, 31, 31, 31],
        ]
    elif num_factors == 7:
        combos = [[30, 31, 32, 33, 34, 35, 36]]
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
    log("🚀 mass_submit_v6 — فقط ۳۰+ رقم، متنوع (۳۰-۵۰)")
    log("  هیچ فاکتور زیر ۳۰ ثبت نشود")
    log("  تمرکز: ۴ و ۵ عاملی")
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
    
    configs = [
        (4, 500, "Quad (varied 30-50 digit factors) — تمرکز اصلی"),
        (5, 200, "Penta (varied 30-50 digit)"),
        (3, 50,  "Triple (varied 30-50) — کم"),
        (6, 30,  "Hexa (varied 30-50)"),
        (7, 15,  "Hepta (varied 30-50)"),
    ]
    
    all_results = existing
    named_results = named
    held_results = held
    total_credited = 0
    total_submitted = 0
    total_held = 0
    total_failed = 0
    
    for num_factors, count, display in configs:
        log(f"\n{'='*60}")
        log(f"📦 {display} — {count} عدد")
        log(f"{'='*60}")
        
        for i in range(count):
            try:
                n, factors, digits, hold = generate_number(num_factors)
                
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
                    if (i+1) % 20 == 0:
                        log(f"  [{i+1}/{count}] HELD: {total_held} total")
                    continue
                
                # چک نهایی: همه‌ی عامل‌ها ۳۰+ رقم؟
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
                    log(f"  [{i+1}/{count}] sub={total_submitted} cred={total_credited} held={total_held} combo={digits}")
                
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
    log(f"  failed: {total_failed}")
    
    by_name = {}
    for r in named_results:
        by_name[r['factor_name']] = by_name.get(r['factor_name'], 0) + 1
    for name, count in sorted(by_name.items()):
        log(f"  {name}: {count}")


if __name__ == '__main__':
    main()
