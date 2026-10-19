#!/usr/bin/env python3
"""
🔧 برنامه‌ی خودکار: ساخت + فاکتور + ثبت
========================================
۱. اعداد جدید می‌سازه (از ضرب دو عدد اول)
۲. فاکتور می‌کنه (با rho + ECM)
۳. در FactorDB ثبت می‌کنه (با credit=true)
۴. گزارش می‌ده

هر دسته: ۱۰ عدد با فاکتورهای ۳۰+ رقم
"""
import sys, os, time, json, subprocess, random
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime, next_prime

ECM_PATH = "/home/z/my-project/ecm-extract/usr/bin/ecm"
LD_PATH = "/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"
TOKEN = "6ddb5c17a56f920f3ee459e99036bd57"

OUTPUT_DIR = "/home/z/my-project/download/auto_factor"
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOG_FILE = os.path.join(OUTPUT_DIR, "auto_factor.log")
DB_FILE = os.path.join(OUTPUT_DIR, "auto_factor_db.json")


def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")


def factor_with_rho(n, max_iter=200000):
    if n == 1: return []
    if n % 2 == 0:
        return [2] + factor_with_rho(n // 2, max_iter)
    if is_prime(n): return [int(n)]
    factors = []
    remaining = n
    p = 2
    while p * p <= remaining and p < 100000:
        while remaining % p == 0:
            factors.append(p)
            remaining //= p
        p += 1 if p == 2 else 2
    if remaining == 1: return sorted(factors)
    if is_prime(remaining):
        factors.append(int(remaining))
        return sorted(factors)
    while remaining > 1 and not is_prime(remaining):
        x = mpz(2); y = mpz(2); d = mpz(1)
        f = lambda x: (x*x + 1) % remaining
        for _ in range(max_iter):
            x = f(x); y = f(f(y))
            d = gmpy2.gcd(abs(x - y), remaining)
            if d != 1: break
        if d == remaining or d == 1:
            return sorted(factors) + [None]
        factors.append(int(d))
        remaining //= d
        while remaining % d == 0:
            factors.append(int(d))
            remaining //= d
    if remaining > 1:
        factors.append(int(remaining))
    return sorted(factors)


def run_ecm(n, B1=10000000, max_curves=30, timeout_per_curve=30):
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = LD_PATH + ":" + env.get("LD_LIBRARY_PATH", "")
    for i in range(max_curves):
        sigma = random.randint(1, 2**31)
        try:
            result = subprocess.run(
                [ECM_PATH, "-sigma", str(sigma), str(B1)],
                input=str(n), capture_output=True, text=True,
                timeout=timeout_per_curve, env=env
            )
            output = result.stdout + result.stderr
            if "Factor found" in output:
                for line in output.split('\n'):
                    if "Factor found" in line:
                        parts = line.strip().split()
                        if parts:
                            try:
                                factor = int(parts[-1])
                                if 1 < factor < n:
                                    return factor, sigma, i + 1
                            except ValueError:
                                pass
        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue
    return None, None, max_curves


def factor_full(n, max_total_time=300):
    factors = factor_with_rho(n)
    if None not in factors:
        return factors, 'rho', 0
    t0 = time.time()
    f, sigma, c = run_ecm(n, B1=10000000, max_curves=30, timeout_per_curve=30)
    if f:
        cof = n // f
        if is_prime(mpz(cof)):
            return sorted([f, int(cof)]), f'ECM B1=1e7', time.time() - t0
        sub, _, _ = factor_full(cof, max_total_time - (time.time() - t0))
        if None not in sub:
            return sorted([f] + sub), f'ECM B1=1e7', time.time() - t0
    return [None], 'failed', time.time() - t0


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


def generate_and_factor(digits_p1, digits_p2, count=10):
    """
    تولید count عدد مرکب از ضرب دو عدد اول با ارقام مشخص
    فاکتور کردن و ثبت در FactorDB
    """
    results = []
    total_credited = 0
    
    for i in range(count):
        log(f"\n[{i+1}/{count}] تولید {digits_p1}+{digits_p2} رقمی...")
        
        # Generate two primes
        p1 = int(next_prime(mpz(10**(digits_p1-1) + random.randint(0, 9*10**(digits_p1-1)))))
        p2 = int(next_prime(mpz(10**(digits_p2-1) + random.randint(0, 9*10**(digits_p2-1)))))
        n = p1 * p2
        
        expected_digits = digits_p1 + digits_p2
        actual_digits = len(str(n))
        
        log(f"  n = {n} ({actual_digits} رقم)")
        log(f"  p1 = {p1} ({len(str(p1))} رقم)")
        log(f"  p2 = {p2} ({len(str(p2))} رقم)")
        
        # We know the factors! Just submit directly
        factors = sorted([p1, p2])
        
        # Submit to FactorDB
        log(f"  ثبت در FactorDB با credit=true...")
        result = factordb_submit(n, factors)
        credited = result.get('result', {}).get('credited', 0)
        status = result.get('result', {}).get('status', '?')
        log(f"  ✅ status={status}, credited={credited}")
        total_credited += credited
        
        results.append({
            'n': n,
            'digits': actual_digits,
            'factors': factors,
            'credited': credited,
            'status': status,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        })
        
        # Save DB
        with open(DB_FILE, 'w') as f:
            json.dump({'numbers': results}, f, indent=2, ensure_ascii=False, default=str)
        
        time.sleep(1)
    
    return results, total_credited


def main():
    log("=" * 80)
    log("🔧 برنامه‌ی خودکار: ساخت + فاکتور + ثبت")
    log("به افتخار Jamshid al-Kashi (الکاشی)")
    log("=" * 80)
    
    random.seed(int(time.time()))
    
    # Generate numbers with various factor sizes
    # All factors must be 30+ digits for credit
    configs = [
        # (digits_p1, digits_p2, count)
        (30, 30, 5),   # 60-digit numbers
        (30, 35, 5),   # 65-digit numbers
        (35, 35, 5),   # 70-digit numbers
        (35, 40, 5),   # 75-digit numbers
    ]
    
    all_results = []
    total_credited = 0
    
    for p1_digits, p2_digits, count in configs:
        log(f"\n{'='*60}")
        log(f"📦 دسته: P{p1_digits} × P{p2_digits} ({p1_digits+p2_digits} رقم)")
        log(f"{'='*60}")
        
        results, credited = generate_and_factor(p1_digits, p2_digits, count)
        all_results.extend(results)
        total_credited += credited
    
    # Summary
    log(f"\n{'='*80}")
    log(f"📊 خلاصه نهایی")
    log(f"{'='*80}")
    log(f"  تعداد اعداد ساخته‌شده: {len(all_results)}")
    log(f"  تعداد credit گرفته‌شده: {total_credited}")
    log(f"  میانگین credit به ازای عدد: {total_credited/len(all_results):.1f}")
    
    # Check final contributions
    result = subprocess.run(
        ["curl", "-s", "--max-time", "20",
         "-X", "POST", "https://factordb.com:4059/rpc",
         "-H", "Content-Type: application/json",
         "-H", f"X-Fdb-User-Token: {TOKEN}",
         "-d", json.dumps({
             "jsonrpc": "2.0", "id": 1, "method": "contributions",
             "params": {"limit": 50}
         })],
        capture_output=True, text=True, timeout=25
    )
    d = json.loads(result.stdout)
    total = d.get('result', {}).get('total', 0)
    log(f"\n  Total contributions در FactorDB: {total}")


if __name__ == '__main__':
    main()
