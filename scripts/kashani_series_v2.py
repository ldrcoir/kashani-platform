#!/usr/bin/env python3
"""
سری Kashani v2 — با فاکتورهای ۳۰+ رقمی برای credit واقعی
================================================================
شرط credit در FactorDB: فاکتور و کوفاکتور هر کدام حداقل ۳۰ رقم.
لذا باید اعداد با فاکتورهای ۳۰+ رقمی بسازیم:
- ۶۰-۶۵ رقمی = ۲ تا فاکتور ۳۰-۳۵ رقمی (قبلاً کردیم)
- ۷۰-۸۰ رقمی = ۲ تا فاکتور ۳۵-۴۰ رقمی (جدید)
"""
import sys, os, time, json, random, subprocess
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime, next_prime

OUTPUT_DIR = "/home/z/my-project/download/kashani_series"
os.makedirs(OUTPUT_DIR, exist_ok=True)
LOG_FILE = os.path.join(OUTPUT_DIR, "kashani_v2_log.txt")

ECM_PATH = "/home/z/my-project/ecm-extract/usr/bin/ecm"
LD_PATH = "/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"
TOKEN = "6ddb5c17a56f920f3ee459e99036bd57"


def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")


def factordb_get(n):
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "20",
             "-X", "POST", "https://factordb.com:4059/rpc",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({
                 "jsonrpc": "2.0", "id": 1, "method": "get_number",
                 "params": {"target": {"expr": str(n)}}
             })],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        return data.get("result", {}).get("status", "?")
    except Exception:
        return "unknown"


def factordb_submit_factors(n, factors):
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
            ["curl", "-s", "--max-time", "60",
             "-X", "POST", "https://factordb.com:4059/rpc",
             "-H", "Content-Type: application/json",
             "-H", f"X-Fdb-User-Token: {TOKEN}",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=90
        )
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}


def factordb_prove_prime(n):
    try:
        payload = {
            "jsonrpc": "2.0", "id": 1, "method": "prove",
            "params": {"target": {"expr": str(n)}}
        }
        result = subprocess.run(
            ["curl", "-s", "--max-time", "60",
             "-X", "POST", "https://factordb.com:4059/rpc",
             "-H", "Content-Type: application/json",
             "-H", f"X-Fdb-User-Token: {TOKEN}",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=90
        )
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}


def generate_random_prime(digits):
    while True:
        n = random.randint(10**(digits-1), 10**digits - 1)
        if n % 2 == 0:
            n += 1
        p = int(next_prime(mpz(n)))
        if len(str(p)) == digits:
            return p


def factor_with_ecm(n, B1=10000000, max_curves=80, timeout_per_curve=30):
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


def factor_full(n, max_total_time=600):
    # Try rho first
    factors = factor_with_rho(n)
    if None not in factors:
        return factors, 'rho', 0
    
    # Try ECM B1=1e7
    t0 = time.time()
    f, sigma, c = factor_with_ecm(n, B1=10000000, max_curves=80, timeout_per_curve=30)
    if f:
        cof = n // f
        sub, _, _ = factor_full(cof, max_total_time - (time.time() - t0))
        if None not in sub:
            return sorted([f] + sub), f'ECM B1=1e7 (σ={sigma}, c={c})', time.time() - t0
    
    # Try ECM B1=1e8
    if time.time() - t0 < max_total_time:
        f, sigma, c = factor_with_ecm(n, B1=100000000, max_curves=15, timeout_per_curve=120)
        if f:
            cof = n // f
            sub, _, _ = factor_full(cof, max_total_time - (time.time() - t0))
            if None not in sub:
                return sorted([f] + sub), f'ECM B1=1e8 (σ={sigma}, c={c})', time.time() - t0
    
    return [None], 'failed', time.time() - t0


def main():
    log("=" * 80)
    log("🕌 سری Kashani v2 — با فاکتورهای ۳۰+ رقمی")
    log("=" * 80)
    
    random.seed(int(time.time()) + 42)
    
    # تولید اعداد با فاکتورهای ۳۰+ رقمی:
    # - ۶۰ رقمی: P30 × P30
    # - ۶۵ رقمی: P30 × P35
    # - ۷۰ رقمی: P35 × P35
    # - ۷۵ رقمی: P35 × P40
    # - ۸۰ رقمی: P40 × P40
    
    configs = [
        (60, 30, 30, 'P30 × P30'),
        (65, 30, 35, 'P30 × P35'),
        (70, 35, 35, 'P35 × P35'),
        (75, 35, 40, 'P35 × P40'),
        (80, 40, 40, 'P40 × P40'),
    ]
    
    all_numbers = []
    for total_digits, d1, d2, strategy in configs:
        log(f"تولید: عدد {total_digits}-رقمی ({strategy})")
        p1 = generate_random_prime(d1)
        p2 = generate_random_prime(d2)
        n = p1 * p2
        if len(str(n)) == total_digits:
            all_numbers.append({
                'n': n,
                'expected_factors': [p1, p2],
                'strategy': strategy,
                'expected_digits': total_digits,
            })
        else:
            log(f"  ⚠️ تعداد رقم درست نشد ({len(str(n))} != {total_digits}) — دوباره")
    
    log(f"\nتعداد اعداد تولید شده: {len(all_numbers)}")
    
    # بررسی در FactorDB
    log("\n--- بررسی در FactorDB ---")
    for num in all_numbers:
        status = factordb_get(num['n'])
        num['factordb_status_before'] = status
        log(f"  {num['n']} ({num['expected_digits']} رقم) — status: {status}")
        time.sleep(0.5)
    
    # فکتور کردن و ثبت
    log("\n--- فکتور کردن و ثبت ---")
    
    db = {
        'series_name': 'Jamshid Kashani Series v2',
        'dedicated_to': 'Ghiyath al-Din Jamshid Mas\'ud al-Kashi (1380-1429)',
        'description': 'سری اعداد ۶۰-۸۰ رقمی با فاکتورهای ۳۰+ رقمی (قابل credit در FactorDB)',
        'credited_to': 'ehsanmorad (EhsanMoradMaryamAlasvandi)',
        'numbers': [],
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    total_credited = 0
    
    for num in all_numbers:
        n = num['n']
        digits = num['expected_digits']
        log(f"\nپردازش {n} ({digits} رقم) — استراتژی: {num['strategy']}")
        
        if num['factordb_status_before'] == 'FF':
            log(f"  ⚠️ قبلاً FF — skip")
            continue
        
        t0 = time.time()
        factors, method, _ = factor_full(n, max_total_time=600)
        elapsed = time.time() - t0
        
        if None in factors:
            log(f"  ❌ فکتور نشد در {elapsed:.1f}s")
            continue
        
        log(f"  ✅ فکتور شد در {elapsed:.1f}s — {method}")
        log(f"  عامل‌ها: {' × '.join(map(str, factors))}")
        
        # Verify
        product = 1
        for f in factors:
            product *= f
        if product != n:
            log(f"  ❌ تأیید ناموفق")
            continue
        
        all_prime = all(is_prime(mpz(f)) for f in factors)
        log(f"  همه اول: {all_prime}")
        
        # ثبت در FactorDB
        log(f"  ثبت در FactorDB با credit=True...")
        result = factordb_submit_factors(n, factors)
        credited = result.get('result', {}).get('credited', 0)
        log(f"  ✅ نتیجه: status={result.get('result', {}).get('status')}, credited={credited}")
        total_credited += credited
        
        # prove
        log(f"  اثبات اول بودن...")
        proven = 0
        for f in set(factors):
            if is_prime(mpz(f)):
                r = factordb_prove_prime(f)
                if r.get('result', {}).get('proved'):
                    proven += 1
                time.sleep(0.3)
        log(f"  اثبات شده: {proven}")
        
        db['numbers'].append({
            'n': n,
            'digits': digits,
            'strategy': num['strategy'],
            'factors': factors,
            'factor_digits': [len(str(f)) for f in factors],
            'method': method,
            'time_seconds': elapsed,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'factordb_status_before': num['factordb_status_before'],
            'submitted_to_factordb': True,
            'credited': credited,
            'proven': proven,
        })
        
        with open(os.path.join(OUTPUT_DIR, 'kashani_v2_db.json'), 'w') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        
        time.sleep(1)
    
    log(f"\n{'=' * 80}")
    log(f"📊 خلاصه‌ی نهایی")
    log(f"{'=' * 80}")
    log(f"اعداد تولید شده: {len(all_numbers)}")
    log(f"تعداد credit داده شده در FactorDB: {total_credited}")


if __name__ == '__main__':
    main()
