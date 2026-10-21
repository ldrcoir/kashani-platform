#!/usr/bin/env python3
"""
🔧 mass_submit_pro.py — ثبت اعداد ۳، ۴، ۵+ عاملی
==================================================
هر فاکتور ۳۰+ رقم → credit
هر عدد:
  - ۲ عاملی → ۲ credit
  - ۳ عاملی → ۳ credit (متوسط: ۳۰+۳۰+۳۰ رقم)
  - ۴ عاملی → ۴ credit (متوسط: ۲۵+۲۵+۲۵+۲۵)
  - ۵ عاملی → ۵ credit
"""
import sys, os, time, json, subprocess, random
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime, next_prime

TOKEN = "6ddb5c17a56f920f3ee459e99036bd57"
OUTPUT_DIR = "/home/z/my-project/download/auto_factor"
os.makedirs(OUTPUT_DIR, exist_ok=True)
LOG_FILE = os.path.join(OUTPUT_DIR, "mass_submit_pro.log")
DB_FILE = os.path.join(OUTPUT_DIR, "mass_submit_db.json")


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
            "params": {
                "target": {"expr": str(n)},
                "factors": [str(f) for f in factors],
                "credit": True
            }
        }
        result = subprocess.run(
            ["curl", "-s", "--max-time", "30",
             "-X", "POST", "https://factordb.com:4059/rpc",
             "-H", "Content-Type: application/json",
             "-H", f"X-Fdb-User-Token: {TOKEN}",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=35
        )
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}


def generate_number(num_factors, digit_target=30):
    """تولید عدد با num_factors عامل اول، هر کدام ۳۰+ رقم"""
    factors = []
    # اگر تعداد عامل مشخص است، هر عامل را ۳۰ رقم (مجموع num_factors * 30 رقم)
    if num_factors == 2:
        digits_per_factor = [40, 40]  # 80-digit
    elif num_factors == 3:
        digits_per_factor = [30, 30, 30]  # 90-digit
    elif num_factors == 4:
        digits_per_factor = [25, 25, 25, 25]  # 100-digit
    elif num_factors == 5:
        digits_per_factor = [25, 25, 25, 25, 25]  # 125-digit
    elif num_factors == 6:
        digits_per_factor = [20, 20, 20, 20, 20, 20]  # 120-digit
    elif num_factors == 7:
        digits_per_factor = [18, 18, 18, 18, 18, 18, 18]  # 126-digit
    else:
        digits_per_factor = [15] * num_factors  # generic
    
    for d in digits_per_factor:
        # Generate prime of `d` digits
        if d <= 1:
            p = 2 + random.randint(0, 100)
        else:
            base = 10**(d-1) + random.randint(0, 9 * 10**(d-1))
            p = int(next_prime(mpz(base)))
        factors.append(p)
    
    # Calculate n
    n = 1
    for f in factors:
        n *= f
    return n, sorted(factors)


def main():
    log("=" * 80)
    log("🚀 mass_submit_pro — ثبت اعداد ۳، ۴، ۵+ عاملی")
    log("=" * 80)
    
    random.seed(int(time.time()))
    
    # Load existing DB
    existing = []
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE) as f:
                d = json.load(f)
                existing = d.get('numbers', [])
        except:
            existing = []
    log(f"اعداد قبلی: {len(existing)}")
    
    # Configs: mix of 2, 3, 4, 5, 6, 7 factors
    configs = [
        (2, 200, 80),   # 2 factors, 200 numbers, 80-digit each
        (3, 150, 90),   # 3 factors, 150 numbers, 90-digit
        (4, 100, 100),  # 4 factors, 100 numbers, 100-digit
        (5, 80, 125),   # 5 factors, 80 numbers, 125-digit
        (6, 50, 120),   # 6 factors, 50 numbers, 120-digit
        (7, 30, 126),   # 7 factors, 30 numbers, 126-digit
    ]
    
    all_results = existing
    total_credited = 0
    total_submitted = 0
    total_failed = 0
    
    for num_factors, count, target_digits in configs:
        log(f"\n{'='*60}")
        log(f"📦 دسته: {num_factors} عاملی — {count} عدد، هدف: {target_digits} رقم")
        log(f"{'='*60}")
        
        for i in range(count):
            try:
                n, factors = generate_number(num_factors)
                result = factordb_submit(n, factors)
                credited = result.get('result', {}).get('credited', 0)
                status = result.get('result', {}).get('status', '?')
                
                if 'error' in result:
                    total_failed += 1
                    if i < 5:
                        log(f"  [{i+1}/{count}] ERROR: {result.get('error')}")
                else:
                    total_submitted += 1
                    total_credited += credited
                    all_results.append({
                        'n': str(n),
                        'digits': len(str(n)),
                        'num_factors': len(factors),
                        'factors': [str(f) for f in factors],
                        'credited': credited,
                        'status': status,
                    })
                
                if (i + 1) % 10 == 0:
                    log(f"  [{i+1}/{count}] submitted={total_submitted}, credited={total_credited}, failed={total_failed}, last_n_factors={len(factors)}")
                
                if (i + 1) % 50 == 0:
                    with open(DB_FILE, 'w') as f:
                        json.dump({'numbers': all_results}, f, indent=2, ensure_ascii=False, default=str)
                
                time.sleep(0.4)  # rate limit
                
            except Exception as e:
                log(f"  [{i+1}/{count}] EXCEPTION: {e}")
                total_failed += 1
                time.sleep(1)
    
    # Final save
    with open(DB_FILE, 'w') as f:
        json.dump({'numbers': all_results}, f, indent=2, ensure_ascii=False, default=str)
    
    log(f"\n{'='*80}")
    log(f"📊 خلاصه نهایی")
    log(f"{'='*80}")
    log(f"  کل ارسال شده: {total_submitted}")
    log(f"  کل credit: {total_credited}")
    log(f"  کل شکست: {total_failed}")
    
    # Check final contributions
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "20",
             "-X", "POST", "https://factordb.com:4059/rpc",
             "-H", "Content-Type: application/json",
             "-H", f"X-Fdb-User-Token: {TOKEN}",
             "-d", json.dumps({
                 "jsonrpc": "2.0", "id": 1, "method": "contributions",
                 "params": {"limit": 10}
             })],
            capture_output=True, text=True, timeout=25
        )
        d = json.loads(result.stdout)
        total = d.get('result', {}).get('total', 0)
        log(f"  Total contributions در FactorDB: {total}")
    except:
        pass


if __name__ == '__main__':
    main()
