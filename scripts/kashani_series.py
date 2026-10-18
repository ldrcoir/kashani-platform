#!/usr/bin/env python3
"""
سری Jamshid Kashani
==================
ساختن، فکتور کردن، و ثبت در FactorDB مجموعه‌ای از اعداد مرکب
به افتخار Ghiyath al-Din Jamshid Mas'ud al-Kashi (1380-1429)

استراتژی:
1. تولید اعداد مرکب با ساختارهای متنوع (2-6 عامل)
2. بررسی در FactorDB (آیا وجود داره؟)
3. اگه status=C (unfactored) → فکتور کردن با ECM
4. ثبت در FactorDB با credit=True (به اسم ehsanmorad)
5. ذخیره‌ی گواهی‌ها و metadata
"""
import sys
import os
import time
import json
import random
import subprocess

sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime, next_prime

OUTPUT_DIR = "/home/z/my-project/download/kashani_series"
os.makedirs(OUTPUT_DIR, exist_ok=True)
DB_FILE = os.path.join(OUTPUT_DIR, "kashani_series.json")
LOG_FILE = os.path.join(OUTPUT_DIR, "kashani_series_log.txt")

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
    """بررسی وضعیت عدد در FactorDB"""
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
    """ثبت فاکتورها در FactorDB با credit=True"""
    try:
        payload = {
            "jsonrpc": "2.0", "id": 1, "method": "report_factors",
            "params": {
                "target": {"expr": str(n)},
                "factors": [str(f) for f in factors],
                "credit": True  # ← این مهمه!
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
    """ثبت قطعی اول بودن (prove) برای عامل‌های اول"""
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
    """تولید عدد اول با تعداد رقم مشخص"""
    while True:
        n = random.randint(10**(digits-1), 10**digits - 1)
        if n % 2 == 0:
            n += 1
        p = int(next_prime(mpz(n)))
        if len(str(p)) == digits:
            return p


def generate_kashani_numbers():
    """تولید اعداد متنوع برای سری Kashani"""
    numbers = []
    
    # استراتژی‌های متنوع:
    # 1. عدد ۲۸ رقمی از ضرب دو P14
    log("تولید: ۲ عدد ۲۸ رقمی (P14 × P14)")
    for _ in range(2):
        p1 = generate_random_prime(14)
        p2 = generate_random_prime(14)
        n = p1 * p2
        if len(str(n)) == 28:
            numbers.append({
                'n': n, 'expected_factors': [p1, p2],
                'strategy': 'P14 × P14 (28 digits)',
                'expected_digits': 28,
            })
    
    # 2. عدد ۳۰ رقمی از ضرب سه P10
    log("تولید: ۲ عدد ۳۰ رقمی (P10 × P10 × P10)")
    for _ in range(2):
        p1 = generate_random_prime(10)
        p2 = generate_random_prime(10)
        p3 = generate_random_prime(10)
        n = p1 * p2 * p3
        if len(str(n)) == 30:
            numbers.append({
                'n': n, 'expected_factors': [p1, p2, p3],
                'strategy': 'P10 × P10 × P10 (30 digits)',
                'expected_digits': 30,
            })
    
    # 3. عدد ۳۵ رقمی از ضرب P14 × P21
    log("تولید: ۲ عدد ۳۵ رقمی (P14 × P21)")
    for _ in range(2):
        p1 = generate_random_prime(14)
        p2 = generate_random_prime(21)
        n = p1 * p2
        if len(str(n)) == 35:
            numbers.append({
                'n': n, 'expected_factors': [p1, p2],
                'strategy': 'P14 × P21 (35 digits)',
                'expected_digits': 35,
            })
    
    # 4. عدد ۴۰ رقمی از ضرب چهار P10
    log("تولید: ۲ عدد ۴۰ رقمی (P10^4)")
    for _ in range(2):
        ps = [generate_random_prime(10) for _ in range(4)]
        n = 1
        for p in ps:
            n *= p
        if len(str(n)) == 40:
            numbers.append({
                'n': n, 'expected_factors': ps,
                'strategy': 'P10 × P10 × P10 × P10 (40 digits)',
                'expected_digits': 40,
            })
    
    # 5. عدد ۴۵ رقمی از ضرب سه P15
    log("تولید: ۲ عدد ۴۵ رقمی (P15^3)")
    for _ in range(2):
        ps = [generate_random_prime(15) for _ in range(3)]
        n = 1
        for p in ps:
            n *= p
        if len(str(n)) == 45:
            numbers.append({
                'n': n, 'expected_factors': ps,
                'strategy': 'P15 × P15 × P15 (45 digits)',
                'expected_digits': 45,
            })
    
    return numbers


def factor_with_ecm(n, B1=10000000, max_curves=80, timeout_per_curve=30):
    """فکتور کردن با ECM"""
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = LD_PATH + ":" + env.get("LD_LIBRARY_PATH", "")
    
    for i in range(max_curves):
        sigma = random.randint(1, 2**31)
        try:
            result = subprocess.run(
                [ECM_PATH, "-sigma", str(sigma), str(B1)],
                input=str(n),
                capture_output=True, text=True,
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
    """فکتور کردن کامل: rho + ECM B1=1e7 + ECM B1=1e8"""
    # First try rho
    def factor_with_rho(m, max_iter=200000):
        if m == 1: return []
        if m % 2 == 0:
            return [2] + factor_with_rho(m // 2, max_iter)
        if is_prime(m): return [int(m)]
        factors = []
        remaining = m
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
    
    # Try rho
    factors = factor_with_rho(n)
    if None not in factors:
        return factors, 'rho', 0
    
    # Try ECM B1=1e7
    t0 = time.time()
    f, sigma, c = factor_with_ecm(n, B1=10000000, max_curves=80, timeout_per_curve=30)
    if f:
        cof = n // f
        # Recursively factor cof
        sub_factors, sub_method, _ = factor_full(cof, max_total_time - (time.time() - t0))
        if None not in sub_factors:
            return sorted([f] + sub_factors), f'ECM B1=1e7 (σ={sigma}, c={c})', time.time() - t0
    
    # Try ECM B1=1e8
    if time.time() - t0 < max_total_time:
        f, sigma, c = factor_with_ecm(n, B1=100000000, max_curves=10, timeout_per_curve=120)
        if f:
            cof = n // f
            sub_factors, sub_method, _ = factor_full(cof, max_total_time - (time.time() - t0))
            if None not in sub_factors:
                return sorted([f] + sub_factors), f'ECM B1=1e8 (σ={sigma}, c={c})', time.time() - t0
    
    return [None], 'failed', time.time() - t0


def main():
    log("=" * 80)
    log("🕌 سری Jamshid Kashani — آغاز")
    log("به افتخار: Ghiyath al-Din Jamshid Mas'ud al-Kashi (1380-1429)")
    log("=" * 80)
    
    random.seed(int(time.time()))
    
    # مرحله ۱: تولید اعداد
    log("\n--- مرحله ۱: تولید اعداد ---")
    numbers = generate_kashani_numbers()
    log(f"تعداد اعداد تولید شده: {len(numbers)}")
    
    # مرحله ۲: بررسی در FactorDB
    log("\n--- مرحله ۲: بررسی در FactorDB ---")
    for i, num in enumerate(numbers, 1):
        n = num['n']
        digits = num['expected_digits']
        status = factordb_get(n)
        num['factordb_status_before'] = status
        log(f"  [{i}/{len(numbers)}] {n} ({digits} رقم) — status: {status}")
        time.sleep(0.5)
    
    # مرحله ۳: فکتور کردن و ثبت
    log("\n--- مرحله ۳: فکتور کردن و ثبت ---")
    
    db = {
        'series_name': 'Jamshid Kashani Series',
        'dedicated_to': 'Ghiyath al-Din Jamshid Mas\'ud al-Kashi (1380-1429)',
        'description': 'سری اعداد ساخته‌شده به افتخار ریاضیدان و ستاره‌شناس پارسی قرن ۱۵',
        'credited_to': 'ehsanmorad (EhsanMoradMaryamAlasvandi)',
        'numbers': [],
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    submitted_count = 0
    credited_count = 0
    
    for i, num in enumerate(numbers, 1):
        n = num['n']
        digits = num['expected_digits']
        log(f"\n[{i}/{len(numbers)}] پردازش {n} ({digits} رقم)")
        log(f"  استراتژی: {num['strategy']}")
        
        # Skip if already fully factored in FactorDB
        if num['factordb_status_before'] == 'FF':
            log(f"  ⚠️ قبلاً در FactorDB فکتور شده — skip")
            continue
        if num['factordb_status_before'] == 'unknown':
            log(f"  ⚠️ نتونستیم بررسی کنیم — skip")
            continue
        
        # Factor
        t0 = time.time()
        factors, method, factor_time = factor_full(n)
        elapsed = time.time() - t0
        
        if None in factors:
            log(f"  ❌ فکتور نشد در {elapsed:.1f}s")
            db['numbers'].append({
                'n': n,
                'digits': digits,
                'strategy': num['strategy'],
                'status': 'unfactored_locally',
                'time_seconds': elapsed,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'factordb_status_before': num['factordb_status_before'],
            })
            continue
        
        log(f"  ✅ فکتور شد در {elapsed:.1f}s با {method}")
        log(f"  عامل‌ها: {' × '.join(map(str, factors))}")
        
        # Verify
        product = 1
        for f in factors:
            product *= f
        if product != n:
            log(f"  ❌ تأیید ناموفق!")
            continue
        
        # Check primality of each factor
        all_prime = all(is_prime(mpz(f)) for f in factors)
        log(f"  همه عامل‌ها اول هستن: {all_prime}")
        
        # مرحله ۴: ثبت در FactorDB
        log(f"  ثبت در FactorDB با credit=True...")
        submit_result = factordb_submit_factors(n, factors)
        log(f"  نتیجه ثبت: {json.dumps(submit_result, ensure_ascii=False)[:200]}")
        credited = submit_result.get('result', {}).get('credited', 0)
        log(f"  تعداد credit داده شده: {credited}")
        
        # مرحله ۵: prove اعداد اول
        log(f"  اثبات اول بودن عامل‌ها (prove)...")
        proven_count = 0
        for f in set(factors):
            if is_prime(mpz(f)):
                prove_result = factordb_prove_prime(f)
                if prove_result.get('result', {}).get('proved', False):
                    proven_count += 1
                time.sleep(0.3)
        log(f"  اثبات شده: {proven_count} عامل")
        
        db['numbers'].append({
            'n': n,
            'digits': digits,
            'strategy': num['strategy'],
            'factors': factors,
            'factor_count': len(factors),
            'all_prime': all_prime,
            'method': method,
            'time_seconds': elapsed,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'factordb_status_before': num['factordb_status_before'],
            'submitted_to_factordb': True,
            'credited': credited,
            'proven': proven_count,
        })
        
        submitted_count += 1
        credited_count += credited
        
        # Save DB after each number
        with open(DB_FILE, 'w') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        
        time.sleep(1)  # rate limit
    
    # Summary
    log("\n" + "=" * 80)
    log("📊 خلاصه‌ی نهایی")
    log("=" * 80)
    log(f"تعداد اعداد تولید شده: {len(numbers)}")
    log(f"تعداد ارسال شده به FactorDB: {submitted_count}")
    log(f"تعداد credit داده شده: {credited_count}")
    log(f"فایل: {DB_FILE}")


if __name__ == '__main__':
    main()
