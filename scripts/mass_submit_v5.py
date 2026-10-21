#!/usr/bin/env python3
"""
🔧 mass_submit_v5.py
====================
قوانین:
  ۱. فقط فاکتورهای ۳۰+ رقم ثبت می‌شوند (بقیه اصلا ثبت نمی‌شوند)
  ۲. تممرکز روی ۴ و ۵ عاملی
  ۳. ۲ و ۳ عاملی نگه‌داری محلی (ثبت نمی‌شوند)
  ۴. اعداد پنهان (بدون ۳۰) ذخیره برای بعد
"""
import sys, os, time, json, subprocess, random
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, next_prime

TOKEN = "6ddb5c17a56f920f3ee459e99036bd57"
OUTPUT_DIR = "/home/z/my-project/download/auto_factor"
os.makedirs(OUTPUT_DIR, exist_ok=True)
LOG_FILE = os.path.join(OUTPUT_DIR, "mass_submit_v5.log")
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


def gen_factors(num_factors, digit_combo):
    """تولید عامل‌ها با رقم‌های مشخص"""
    factors = []
    for d in digit_combo:
        if d <= 1:
            p = random.randint(2, 1000)
        else:
            base = 10**(d-1) + random.randint(0, 9*10**(d-1))
            p = int(next_prime(mpz(base)))
        factors.append(p)
    return sorted(factors)


def generate_number(num_factors):
    """تولید عدد — فقط ۳۰+ رقم عامل‌ها ثبت می‌شوند
    
    استراتژی:
      - ۷۰٪: همه‌ی عامل‌ها ۳۰+ رقم (برای ثبت)
      - ۳۰٪: عامل‌های مخلوط (۱۵/۲۰/۲۵) → ذخیره محلی، ثبت نشد
    """
    hold = random.random() < 0.30  # 30% hold locally
    
    if hold:
        # پنهان — بدون ۳۰ رقمی → ذخیره محلی
        if num_factors == 4:
            combos = [[15,15,20,20], [20,20,20,20], [15,20,25,25], [25,25,25,25], [15,15,15,25]]
        elif num_factors == 5:
            combos = [[15,15,15,20,20], [20,20,20,20,20], [15,20,25,20,25]]
        elif num_factors == 3:
            combos = [[15,20,25], [20,20,20], [25,25,25]]
        else:
            combos = [[20]*num_factors]
        digits = random.choice(combos)
        random.shuffle(digits)
        factors = gen_factors(num_factors, digits)
        n = 1
        for f in factors: n *= f
        return n, factors, digits, True  # hold=True
    
    # ثبت — همه‌ی عامل‌ها ۳۰+ رقم
    if num_factors == 4:
        combos = [
            [30,30,30,30],   # 120
            [35,30,30,30],   # 125
            [40,30,30,30],   # 130
            [35,35,30,30],   # 130
            [40,40,30,30],   # 140
            [35,35,35,30],   # 135
            [40,35,30,30],   # 135
            [30,30,30,35],   # 125
        ]
    elif num_factors == 5:
        combos = [
            [30,30,30,30,30],   # 150
            [35,30,30,30,30],   # 155
            [40,30,30,30,30],   # 160
            [35,35,30,30,30],   # 160
        ]
    elif num_factors == 3:
        combos = [
            [30,30,30],   # 90
            [35,30,30],   # 95
            [40,30,30],   # 100
            [35,35,30],   # 100
        ]
    elif num_factors == 6:
        combos = [[30,30,30,30,30,30], [35,30,30,30,30,30]]
    elif num_factors == 7:
        combos = [[30,30,30,30,30,30,30]]
    else:
        combos = [[30]*num_factors]
    
    digits = random.choice(combos)
    random.shuffle(digits)
    factors = gen_factors(num_factors, digits)
    n = 1
    for f in factors: n *= f
    return n, factors, digits, False  # hold=False → submit


def main():
    log("=" * 80)
    log("🚀 mass_submit_v5 — فقط ۳۰+ رقم عامل‌ها ثبت می‌شوند")
    log("  تمرکز: ۴ و ۵ عاملی | ۲ و ۳ نگه‌داری محلی")
    log("  ۳۰٪ اعداد پنهان (بدون ۳۰) → ذخیره محلی")
    log("=" * 80)
    
    random.seed(int(time.time()))
    
    # Load DBs
    existing = []
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE) as f:
                existing = json.load(f).get('numbers', [])
        except: pass
    log(f"DB قبلی: {len(existing)}")
    
    named = []
    if os.path.exists(NAMED_DB_FILE):
        try:
            with open(NAMED_DB_FILE) as f:
                named = json.load(f).get('named_factors', [])
        except: pass
    log(f"named قبلی: {len(named)}")
    
    held = []
    if os.path.exists(HELD_FILE):
        try:
            with open(HELD_FILE) as f:
                held = json.load(f).get('held', [])
        except: pass
    log(f"held قبلی: {len(held)}")
    
    # ⭐ تمرکز روی ۴ و ۵ عاملی
    configs = [
        (4, 500, "Quad-Composite (all 30+ digit factors) — تمرکز اصلی"),
        (5, 200, "Penta-Composite (all 30+ digit factors)"),
        (3, 50,  "Triple-Composite (all 30+ digit factors) — کم"),
        (6, 30,  "Hexa-Composite (all 30+ digit)"),
        (7, 15,  "Hepta-Composite (all 30+ digit)"),
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
                    # پنهان — ذخیره محلی
                    held_results.append({
                        'n': str(n), 'digits': len(str(n)),
                        'num_factors': num_factors,
                        'factor_name': FACTOR_NAMES.get(num_factors, f"{num_factors}-Composite"),
                        'factors': [str(f) for f in factors],
                        'digit_combo': digits,
                        'saved_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                    total_held += 1
                    if (i+1) % 20 == 0:
                        log(f"  [{i+1}/{count}] HELD (پنهان): {total_held} total held")
                    continue
                
                # چک: آیا همه‌ی عامل‌ها ۳۰+ رقم‌اند؟
                all_30_plus = all(len(str(f)) >= 30 for f in factors)
                if not all_30_plus:
                    # اصلا ثبت نکن — نگه‌دار محلی
                    held_results.append({
                        'n': str(n), 'digits': len(str(n)),
                        'num_factors': num_factors,
                        'factors': [str(f) for f in factors],
                        'digit_combo': digits,
                        'saved_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'reason': 'factors_under_30_digit',
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
                        'factor_name': FACTOR_NAMES.get(num_factors, f"{num_factors}-Composite"),
                        'factors': [str(f) for f in factors],
                        'credited': credited, 'status': status,
                        'digit_combo': digits,
                        'submitted_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                
                if (i+1) % 10 == 0:
                    log(f"  [{i+1}/{count}] sub={total_submitted} cred={total_credited} held={total_held} name={FACTOR_NAMES.get(num_factors)} combo={digits}")
                
                if (i+1) % 50 == 0:
                    with open(DB_FILE, 'w') as f:
                        json.dump({'numbers': all_results}, f, indent=2, ensure_ascii=False, default=str)
                    with open(NAMED_DB_FILE, 'w') as f:
                        json.dump({'named_factors': named_results}, f, indent=2, ensure_ascii=False, default=str)
                    with open(HELD_FILE, 'w') as f:
                        json.dump({'held': held_results}, f, indent=2, ensure_ascii=False, default=str)
                
                time.sleep(0.4)
            except Exception as e:
                log(f"  [{i+1}/{count}] EXCEPTION: {e}")
                total_failed += 1
                time.sleep(1)
    
    # Final save
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
    log(f"  held (پنهان): {total_held}")
    log(f"  failed: {total_failed}")
    log(f"  named total: {len(named_results)}")
    
    by_name = {}
    for r in named_results:
        by_name[r['factor_name']] = by_name.get(r['factor_name'], 0) + 1
    for name, count in sorted(by_name.items()):
        log(f"  {name}: {count}")


if __name__ == '__main__':
    main()
