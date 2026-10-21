#!/usr/bin/env python3
"""
ساختن اعداد مرکب جدید، بررسی در FactorDB (فقط query، بدون submission)،
و فکتور کردن محلی.

استراتژی:
1. تولید ۵ عدد ۶۵-۷۰ رقمی با ضرب دو prime ۳۰-۳۵ رقمی
2. برای هر عدد:
   - بررسی در FactorDB (آیا فکتور شده؟)
   - اگه نه → ECM locally
   - ذخیره در پایگاه محلی به اسم Kashai
"""
import sys
import os
import json
import time
import subprocess
import random

sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime, next_prime

OUTPUT_DIR = "/home/z/my-project/download/kashani_db"
os.makedirs(OUTPUT_DIR, exist_ok=True)
DB_FILE = os.path.join(OUTPUT_DIR, "factored_numbers.json")
LOG_FILE = os.path.join(OUTPUT_DIR, "kashani_log.txt")

ECM_PATH = "/home/z/my-project/ecm-extract/usr/bin/ecm"
LD_PATH = "/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"


def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")


def generate_random_prime(digits):
    """تولید یه عدد اول با تعداد رقم مشخص"""
    while True:
        # Random number with specified digits
        n = random.randint(10**(digits-1), 10**digits - 1)
        if n % 2 == 0:
            n += 1
        # Find next prime >= n
        p = int(next_prime(mpz(n)))
        if len(str(p)) == digits:
            return p


def generate_composite(digits_target):
    """تولید یه عدد مرکب با تعداد رقم مشخص (با ضرب دو prime)"""
    # Try various splits
    while True:
        d1 = random.randint(digits_target // 2 - 2, digits_target // 2 + 2)
        d2 = digits_target - d1
        p1 = generate_random_prime(d1)
        p2 = generate_random_prime(d2)
        n = p1 * p2
        if len(str(n)) == digits_target:
            return n, p1, p2


def check_factordb(n):
    """بررسی FactorDB: آیا عدد قبلاً ثبت/فکتور شده؟"""
    try:
        env = os.environ.copy()
        result = subprocess.run(
            ["curl", "-s", "--max-time", "30",
             "-X", "POST", "https://factordb.com:4059/rpc",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({
                 "jsonrpc": "2.0",
                 "id": 1,
                 "method": "get_number",
                 "params": {"target": {"expr": str(n)}}
             })],
            capture_output=True, text=True, timeout=45, env=env
        )
        data = json.loads(result.stdout)
        if "result" in data:
            r = data["result"]
            status = r.get("status", "?")
            return status, r
        return None, data
    except Exception as e:
        return None, {"error": str(e)}


def run_ecm(n, B1=10000000, max_curves=80, timeout_per_curve=30):
    """اجرای ECM با چندین sigma"""
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
                # Find the factor
                for line in output.split('\n'):
                    if "Factor found" in line:
                        # Last number on the line
                        parts = line.strip().split()
                        if parts:
                            try:
                                factor = int(parts[-1])
                                if 1 < factor < n:
                                    return factor, output, sigma
                            except ValueError:
                                pass
        except subprocess.TimeoutExpired:
            continue
        except Exception as e:
            log(f"  ECM curve {i+1} error: {e}")
            continue
    
    return None, None, None


def load_db():
    """بارگذاری پایگاه داده‌ی محلی"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            return json.load(f)
    return {"numbers": [], "credited_to": "Jamshid Kashai (Al-Kashi) — Ghiyath al-Din Jamshid Mas'ud al-Kashi (1380-1429)"}


def save_db(db):
    """ذخیره پایگاه داده‌ی محلی"""
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


def factor_composite(n, max_total_time=600):
    """تلاش برای فکتور کردن با ECM"""
    start = time.time()
    
    # Try B1=1e7 first (fast, finds 30-35 digit factors)
    log(f"  مرحله ۱: ECM با B1=1e7 (max ۸۰ منحنی)")
    factor, output, sigma = run_ecm(n, B1=10000000, max_curves=80, timeout_per_curve=30)
    if factor:
        return factor, 1e7, sigma, time.time() - start
    
    if time.time() - start > max_total_time:
        return None, None, None, time.time() - start
    
    # Try B1=1e8 (slower, finds 35-40 digit factors)
    log(f"  مرحله ۲: ECM با B1=1e8 (max ۲۰ منحنی)")
    factor, output, sigma = run_ecm(n, B1=100000000, max_curves=20, timeout_per_curve=120)
    if factor:
        return factor, 1e8, sigma, time.time() - start
    
    return None, None, None, time.time() - start


def main():
    log("=" * 70)
    log("پروژه‌ی Kashani: ساختن اعداد جدید، بررسی، و فکتور محلی")
    log("به افتخار: Ghiyath al-Din Jamshid Kashai (1380-1429)")
    log("=" * 70)
    
    db = load_db()
    log(f"پایگاه محلی بارگذاری شد: {len(db['numbers'])} عدد موجود")
    
    # Phase 1: تولید اعداد
    log("\n--- مرحله ۱: تولید اعداد مرکب ---")
    candidates = []
    targets = [65, 66, 67, 68, 69]  # پنج عدد با ۶۵-۶۹ رقم
    random.seed(int(time.time()))
    
    for digits in targets:
        log(f"تولید عدد {digits}-رقمی...")
        n, p1, p2 = generate_composite(digits)
        log(f"  ساخته شد: {n}")
        log(f"  (پنهان: {p1} × {p2})")
        candidates.append({
            'n': n,
            'digits': digits,
            'known_factors': [p1, p2],  # برای verify
        })
    
    # Phase 2: بررسی در FactorDB
    log("\n--- مرحله ۲: بررسی در FactorDB (فقط query، بدون submission) ---")
    for c in candidates:
        n = c['n']
        log(f"بررسی {n} ({c['digits']} رقم)...")
        status, info = check_factordb(n)
        if status is None:
            log(f"  ❌ نتونستیم بررسی کنیم (شبکه؟)")
            c['factordb_status'] = 'unknown'
        elif status == 'C':
            log(f"  ✅ در FactorDB هست ولی فکتور نشده (status=C)")
            c['factordb_status'] = 'C'
        elif status == 'FF':
            log(f"  ⚠️ در FactorDB هست و فکتور شده (status=FF)")
            c['factordb_status'] = 'FF'
        elif status == 'P':
            log(f"  ⚠️ در FactorDB به‌عنوان اول ثبت شده؟")
            c['factordb_status'] = 'P'
        elif status == 'U':
            log(f"  ⚠️ در FactorDB هست ولی status=U (نامشخص)")
            c['factordb_status'] = 'U'
        else:
            log(f"  ? status={status}")
            c['factordb_status'] = status
        time.sleep(1)  # respectful delay
    
    # Phase 3: فکتور کردن اعداد جدید
    log("\n--- مرحله ۳: فکتور کردن محلی ---")
    for c in candidates:
        n = c['n']
        digits = c['digits']
        
        # Skip if already factored in FactorDB
        if c.get('factordb_status') == 'FF':
            log(f"\nعدد {n}: از قبل در FactorDB فکتور شده — skip")
            continue
        if c.get('factordb_status') == 'unknown':
            log(f"\nعدد {n}: نتونستیم بررسی کنیم — skip (محتمل به از قبل فکتور شده)")
            continue
        
        log(f"\nحمله به {n} ({digits} رقم):")
        factor, B1, sigma, elapsed = factor_composite(n, max_total_time=600)
        
        if factor:
            cofactor = n // factor
            log(f"  ✅ فاکتور پیدا شد در {elapsed:.1f}s")
            log(f"  factor = {factor} ({len(str(factor))} رقم)")
            log(f"  cofactor = {cofactor} ({len(str(cofactor))} رقم)")
            log(f"  B1={B1}, sigma={sigma}")
            
            # Verify
            if factor * cofactor == n:
                log(f"  ✅ تأیید: factor × cofactor = n")
            else:
                log(f"  ❌ تأیید ناموفق!")
                continue
            
            # Check if cofactor is prime
            cofactor_mpz = mpz(cofactor)
            cofactor_prime = bool(is_prime(cofactor_mpz))
            factor_prime = bool(is_prime(mpz(factor)))
            log(f"  factor prime? {factor_prime}")
            log(f"  cofactor prime? {cofactor_prime}")
            
            # Save to local database
            entry = {
                'n': n,
                'digits': digits,
                'factor1': factor,
                'factor2': cofactor,
                'factor1_digits': len(str(factor)),
                'factor2_digits': len(str(cofactor)),
                'factor1_prime': factor_prime,
                'factor2_prime': cofactor_prime,
                'method': 'ECM',
                'B1': B1,
                'sigma': sigma,
                'time_seconds': elapsed,
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'factordb_status_before': c.get('factordb_status', 'unknown'),
                'submitted_to_factordb': False,
                'credited_to': 'Jamshid Kashai (Al-Kashi)',
            }
            db['numbers'].append(entry)
            save_db(db)
            log(f"  ✅ در پایگاه Kashani ذخیره شد (محلی، بدون ارسال به FactorDB)")
        else:
            log(f"  ❌ فکتور نشد در {elapsed:.1f}s")
            entry = {
                'n': n,
                'digits': digits,
                'status': 'unfactored_locally',
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'factordb_status_before': c.get('factordb_status', 'unknown'),
                'credited_to': 'Jamshid Kashai (Al-Kashi)',
            }
            db['numbers'].append(entry)
            save_db(db)
    
    # Summary
    log("\n" + "=" * 70)
    log("خلاصه‌ی نهایی")
    log("=" * 70)
    log(f"پایگاه محلی Kashani: {len(db['numbers'])} عدد")
    factored_count = sum(1 for e in db['numbers'] if 'factor1' in e)
    log(f"  فکتور شده: {factored_count}")
    log(f"  فکتور نشده محلی: {len(db['numbers']) - factored_count}")
    log(f"\nفایل‌ها:")
    log(f"  پایگاه داده: {DB_FILE}")
    log(f"  گزارش: {LOG_FILE}")


if __name__ == '__main__':
    main()
