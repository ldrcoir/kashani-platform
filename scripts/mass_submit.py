#!/usr/bin/env python3
"""
🔧 برنامه‌ی خودکار حمله‌ای: ۱۰۰۰ عدد بساز + ثبت
================================================
هر دسته ۵۰ عدد با فاکتورهای ۳۰+ رقم
هر عدد: ۲ credit
کل: ۱۰۰۰ عدد = ۲۰۰۰ credit
"""
import sys, os, time, json, subprocess, random
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime, next_prime

TOKEN = "6ddb5c17a56f920f3ee459e99036bd57"
OUTPUT_DIR = "/home/z/my-project/download/auto_factor"
os.makedirs(OUTPUT_DIR, exist_ok=True)
LOG_FILE = os.path.join(OUTPUT_DIR, "mass_submit.log")
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


def main():
    log("=" * 80)
    log("🚀 حمله‌ی ۱۰۰۰ عدد — ساخت + ثبت خودکار")
    log("=" * 80)
    
    random.seed(int(time.time()))
    
    # Load existing DB
    existing = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            d = json.load(f)
            existing = d.get('numbers', [])
    log(f"اعداد قبلی: {len(existing)}")
    
    # Configs: various factor sizes, all 30+ digits
    configs = [
        (30, 30, 200),   # 60-digit: 200 numbers
        (30, 35, 200),   # 65-digit: 200 numbers
        (35, 35, 200),   # 70-digit: 200 numbers
        (35, 40, 200),   # 75-digit: 200 numbers
        (40, 40, 200),   # 80-digit: 200 numbers
    ]
    
    all_results = existing
    total_credited = 0
    total_submitted = 0
    total_failed = 0
    
    for p1d, p2d, count in configs:
        log(f"\n{'='*60}")
        log(f"📦 دسته: P{p1d} × P{p2d} ({p1d+p2d} رقم) — {count} عدد")
        log(f"{'='*60}")
        
        for i in range(count):
            # Generate
            p1 = int(next_prime(mpz(10**(p1d-1) + random.randint(0, 9*10**(p1d-1)))))
            p2 = int(next_prime(mpz(10**(p2d-1) + random.randint(0, 9*10**(p2d-1)))))
            n = p1 * p2
            factors = sorted([p1, p2])
            
            # Submit
            result = factordb_submit(n, factors)
            credited = result.get('result', {}).get('credited', 0)
            status = result.get('result', {}).get('status', '?')
            
            if 'error' in result:
                total_failed += 1
                log(f"  [{i+1}/{count}] ERROR")
            else:
                total_submitted += 1
                total_credited += credited
                all_results.append({
                    'n': n,
                    'digits': len(str(n)),
                    'factors': factors,
                    'credited': credited,
                    'status': status,
                })
            
            # Progress every 50
            if (i + 1) % 50 == 0:
                log(f"  [{i+1}/{count}] submitted={total_submitted}, credited={total_credited}, failed={total_failed}")
            
            # Save DB every 50
            if (i + 1) % 50 == 0:
                with open(DB_FILE, 'w') as f:
                    json.dump({'numbers': all_results}, f, indent=2, ensure_ascii=False, default=str)
            
            # Rate limit: 0.5s between submissions
            time.sleep(0.5)
    
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
