#!/usr/bin/env python3
"""
استراتژی جدید برای پیدا کردن فاکتورهای F2 (C303)
================================================
F2 = 932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281199369604215535391846857906233364905825622441048803673998858526737
                                                                                              (303 رقم)

نکته مهم: فاکتورهای F2 باید خودشون فاکتور M(1237) باشن
یعنی به فرم q = 2·1237·k + 1

استراتژی:
1. استعلام FactorDB برای وضعیت فعلی F2 (شاید فاکتور شده باشه)
2. اجرای ECM با B1 های بهینه برای فاکتورهای 40-60 رقمی
3. اجرای P-1 با B1 = 10^9
4. گزارش نتایج
"""

import json
import time
import urllib.request
import urllib.parse
import subprocess
import os
import gmpy2
from gmpy2 import mpz, is_prime

F2_STR = "932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281199369604215535391846857906233364905825622441048803673998858526737"
F2 = mpz(F2_STR)

WORKDIR = "/home/z/my-project/A136030_M1237_strategy2"
os.makedirs(WORKDIR, exist_ok=True)

ECM = "/home/z/my-project/ecm-extract/usr/bin/ecm"
LD_PATH = "/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"

LOG_FILE = f"{WORKDIR}/strategy.log"
FOUND_FILE = f"{WORKDIR}/FOUND_factors.txt"
PROGRESS_FILE = f"{WORKDIR}/progress.txt"


def log(msg):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")


def query_factordb(n_str):
    """استعلام FactorDB"""
    try:
        url = f"http://factordb.com/api?query={urllib.parse.quote(n_str)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e), 'factors': []}


def run_ecm(B1, curves, output_file):
    """اجرای ECM"""
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    cmd = [ECM, '-c', str(curves), '-v', '-timestamp', str(B1)]
    
    with open(output_file, 'w') as out:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=out,
            stderr=subprocess.STDOUT,
            env=env
        )
        proc.communicate(input=F2_STR.encode())
        return proc.returncode


def check_found(log_file):
    """چک کردن آیا فاکتور پیدا شده"""
    if not os.path.exists(log_file):
        return None
    with open(log_file) as f:
        content = f.read()
    if 'Factor found' in content or 'found' in content.lower():
        # پیدا کردن خط مربوطه
        for line in content.split('\n'):
            if 'factor' in line.lower() and 'found' in line.lower():
                return line
    return None


def main():
    log("=" * 70)
    log("استراتژی جدید برای فاکتوریزاسیون F2 (C303)")
    log("=" * 70)
    log(f"F2 = {F2_STR[:60]}... ({len(F2_STR)} رقم)")
    log("")
    
    # مرحله 1: استعلام FactorDB
    log("=== مرحله 1: استعلام FactorDB ===")
    result = query_factordb(F2_STR)
    status = result.get('status', 'U')
    factors = result.get('factors', [])
    log(f"وضعیت FactorDB: {status}")
    log(f"تعداد فاکتورها: {len(factors)}")
    for f_str, exp in factors:
        f = mpz(f_str)
        is_p = is_prime(f)
        log(f"  {f_str[:60]}{'...' if len(f_str)>60 else ''} ({len(f_str)} رقم, {'P' if is_p else 'C'}, ^{exp})")
    log("")
    
    if status == 'FF':
        log("✓✓✓ F2 کاملاً فاکتور شده!")
        with open(FOUND_FILE, 'w') as f:
            f.write(f"F2 fully factored!\n{json.dumps(factors, indent=2)}\n")
        return
    
    # مرحله 2: استعلام فاکتورهای C از FactorDB (شاید فاکتور شده باشن)
    log("=== مرحله 2: بررسی فاکتورهای C در FactorDB ===")
    for f_str, exp in factors:
        f = mpz(f_str)
        if is_prime(f):
            continue
        # این یک C هست - استعلام مجدد
        log(f"استعلام C{len(f_str)} از FactorDB...")
        sub_result = query_factordb(f_str)
        sub_status = sub_result.get('status', 'U')
        sub_factors = sub_result.get('factors', [])
        log(f"  وضعیت: {sub_status}, فاکتورها: {len(sub_factors)}")
        if sub_status == 'FF' and len(sub_factors) > 1:
            log(f"  ✓✓✓ فاکتور جدید پیدا شد!")
            with open(FOUND_FILE, 'a') as out:
                out.write(f"\n=== Factor from FactorDB ===\n")
                out.write(f"C{len(f_str)} factored as:\n")
                for sf, se in sub_factors:
                    out.write(f"  {sf} (^{se})\n")
            # بررسی آیا این فاکتورها واقعاً فاکتور F2 هستن
            for sf, se in sub_factors:
                sf_mpz = mpz(sf)
                if F2 % sf_mpz == 0:
                    log(f"  ✓✓✓ {sf} فاکتور F2 هست!")
                    with open(FOUND_FILE, 'a') as out:
                        out.write(f"✓✓✓ {sf} divides F2!\n")
        time.sleep(1)
    log("")
    
    # مرحله 3: اجرای ECM با B1 های مختلف
    log("=== مرحله 3: اجرای ECM ===")
    
    # بر اساس تخمین ECM:
    # - فاکتور 30 رقمی: B1=50K, ~250 curves
    # - فاکتور 35 رقمی: B1=250K, ~600 curves  
    # - فاکتور 40 رقمی: B1=1M, ~1500 curves
    # - فاکتور 45 رقمی: B1=5M, ~5000 curves
    # - فاکتور 50 رقمی: B1=25M, ~10000 curves
    # - فاکتور 55 رقمی: B1=100M, ~20000 curves
    
    ecm_runs = [
        ('1e6', 500),     # برای فاکتور 35-40 رقمی
        ('5e6', 500),     # برای فاکتور 40-45 رقمی
        ('25e6', 300),    # برای فاکتور 45-50 رقمی
        ('1e8', 200),     # برای فاکتور 50-55 رقمی
    ]
    
    for B1, curves in ecm_runs:
        log(f"اجرای ECM با B1={B1}, curves={curves}")
        ecm_log = f"{WORKDIR}/ecm_B1_{B1}.log"
        
        t0 = time.time()
        run_ecm(B1, curves, ecm_log)
        elapsed = time.time() - t0
        log(f"  تموم شد در {elapsed:.0f}s")
        
        # چک کردن فاکتور
        found = check_found(ecm_log)
        if found:
            log(f"  ✓✓✓ FACTOR FOUND: {found}")
            with open(FOUND_FILE, 'a') as f:
                f.write(f"\n=== ECM Factor (B1={B1}) ===\n")
                f.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{found}\n")
                # کپی کل log
                with open(ecm_log) as el:
                    f.write(el.read())
            return  # فاکتور پیدا شد، پایان
        else:
            log(f"  فاکتوری پیدا نشد")
        
        # به‌روزرسانی progress
        with open(PROGRESS_FILE, 'w') as pf:
            pf.write(f"last_B1: {B1}\n")
            pf.write(f"last_curves: {curves}\n")
            pf.write(f"elapsed: {elapsed:.0f}s\n")
            pf.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    log("")
    log("=== مرحله 4: P-1 با B1=1e9 ===")
    # اجرای P-1
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    pm1_log = f"{WORKDIR}/pm1.log"
    log("اجرای P-1 با B1=1e9")
    
    with open(pm1_log, 'w') as out:
        proc = subprocess.Popen(
            [ECM, '-pm1', '-v', '-timestamp', '1e9'],
            stdin=subprocess.PIPE,
            stdout=out,
            stderr=subprocess.STDOUT,
            env=env
        )
        proc.communicate(input=F2_STR.encode())
    
    found = check_found(pm1_log)
    if found:
        log(f"✓✓✓ P-1 FOUND: {found}")
        with open(FOUND_FILE, 'a') as f:
            f.write(f"\n=== P-1 Factor ===\n")
            f.write(f"{found}\n")
    else:
        log("P-1 فاکتوری پیدا نکرد")
    
    log("")
    log("=== پایان ===")
    log(f"تاریخ: {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
