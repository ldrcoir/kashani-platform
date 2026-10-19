import sys, os, time, json, subprocess, random
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime, next_prime

TOKEN = "6ddb5c17a56f920f3ee459e99036bd57"
OUTPUT_DIR = "/home/z/my-project/download/auto_factor"
LOG_FILE = os.path.join(OUTPUT_DIR, "mass_submit_v2.log")
DB_FILE = os.path.join(OUTPUT_DIR, "mass_submit_v2_db.json")

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
    log("🚀 Mass Submit v2 — 1000 more numbers (40+40, 40+45, 45+45)")
    random.seed(int(time.time()) + 42)
    
    configs = [
        (40, 40, 300),   # 80-digit
        (40, 45, 300),   # 85-digit
        (45, 45, 400),   # 90-digit
    ]
    
    all_results = []
    total_credited = 0
    total_submitted = 0
    
    for p1d, p2d, count in configs:
        log(f"\n📦 P{p1d} × P{p2d} ({p1d+p2d} رقم) — {count} عدد")
        
        for i in range(count):
            p1 = int(next_prime(mpz(10**(p1d-1) + random.randint(0, 9*10**(p1d-1)))))
            p2 = int(next_prime(mpz(10**(p2d-1) + random.randint(0, 9*10**(p2d-1)))))
            n = p1 * p2
            factors = sorted([p1, p2])
            
            result = factordb_submit(n, factors)
            credited = result.get('result', {}).get('credited', 0)
            
            if credited > 0:
                total_submitted += 1
                total_credited += credited
                all_results.append({
                    'n': n, 'digits': len(str(n)), 'factors': factors, 'credited': credited,
                })
            
            if (i + 1) % 100 == 0:
                log(f"  [{i+1}/{count}] submitted={total_submitted}, credited={total_credited}")
            
            if (i + 1) % 50 == 0:
                with open(DB_FILE, 'w') as f:
                    json.dump({'numbers': all_results}, f, indent=2, ensure_ascii=False, default=str)
            
            time.sleep(0.5)
    
    with open(DB_FILE, 'w') as f:
        json.dump({'numbers': all_results}, f, indent=2, ensure_ascii=False, default=str)
    
    log(f"\n📊 نهایی: {total_submitted} عدد, {total_credited} credit")

if __name__ == '__main__':
    main()
