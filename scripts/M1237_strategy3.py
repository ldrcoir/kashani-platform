#!/usr/bin/env python3
"""
استراتژی هوشمندانه برای فاکتوریزاسیون F2 (C303)
================================================
تحلیل: فاکتورهای F2 باید به فرم q = 2·1237·k + 1 باشن
- F1 (70 رقم) از k = 1025952760647003960927729692600190168224029465083428191794675550443 (67 رقم)
  یعنی k_F1 ≈ 10^67

- اگه فاکن دیگه‌ای وجود داشته باشه، باید q ≤ sqrt(F2) ≈ 10^151
  یعنی k ≤ 10^151 / (2·1237) ≈ 10^148

استراتژی بهینه:
1. P-1 با B1 متناسب با اندازه فاکن مورد نظر
2. ECM با B1 و curves متناسب با اندازه فاکن
3. هر مرحله رو در فایل جداگانه اجرا می‌کنیم تا قابل resume باشه
"""

import json
import time
import urllib.request
import urllib.parse
import subprocess
import os
import sys
import gmpy2
from gmpy2 import mpz, is_prime

F2_STR = "932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281199369604215535391846857906233364905825622441048803673998858526737"
F2 = mpz(F2_STR)

P = 1237

WORKDIR = "/home/z/my-project/A136030_M1237_strategy3"
os.makedirs(WORKDIR, exist_ok=True)

ECM = "/home/z/my-project/ecm-extract/usr/bin/ecm"
LD_PATH = "/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"

LOG_FILE = f"{WORKDIR}/strategy.log"
FOUND_FILE = f"{WORKDIR}/FOUND_factors.txt"
PROGRESS_FILE = f"{WORKDIR}/progress.txt"
STATE_FILE = f"{WORKDIR}/state.json"


def log(msg):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")


def query_factordb(n_str):
    try:
        url = f"http://factordb.com/api?query={urllib.parse.quote(n_str)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e), 'factors': []}


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {'phase': 'start', 'last_step': 0}


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(state, f, indent=2)
    os.rename(tmp, STATE_FILE)


def run_ecm_with_log(B1, curves, log_file, sigma_start=None):
    """اجرای ECM و ذخیره log"""
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    cmd = [ECM, '-c', str(curves), '-v', '-timestamp', str(B1)]
    if sigma_start:
        cmd.extend(['-sigma', str(sigma_start)])
    
    with open(log_file, 'w') as out:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=out,
            stderr=subprocess.STDOUT,
            env=env
        )
        proc.communicate(input=F2_STR.encode())
        return proc.returncode


def check_found_in_log(log_file):
    """چک کردن آیا فاکتور پیدا شده در log"""
    if not os.path.exists(log_file):
        return None
    with open(log_file) as f:
        content = f.read()
    
    # ECM وقتی فاکتور پیدا می‌کنه، این پیام‌ها رو می‌ده
    if 'Factor found' in content:
        # استخراج فاکتور
        for line in content.split('\n'):
            if 'Factor found' in line or 'found' in line.lower():
                return line.strip()
    return None


def check_factor_divides_F2(factor_str):
    """بررسی اینکه آیا فاکتور واقعاً فاکتور F2 هست"""
    try:
        f = mpz(factor_str)
        if F2 % f == 0:
            return True
        return False
    except:
        return False


def main():
    state = load_state()
    
    log("=" * 70)
    log("استراتژی هوشمندانه برای فاکتوریزاسیون F2 (C303)")
    log("=" * 70)
    log(f"F2 = {F2_STR[:60]}... ({len(F2_STR)} رقم)")
    log(f"sqrt(F2) ≈ 10^{len(str(gmpy2.isqrt(F2)))}")
    log(f"State: {state}")
    log("")
    
    # مرحله 1: استعلام FactorDB
    log("=== مرحله 1: استعلام FactorDB ===")
    result = query_factordb(F2_STR)
    status = result.get('status', 'U')
    factors = result.get('factors', [])
    log(f"وضعیت FactorDB: {status}")
    log(f"تعداد فاکتورها: {len(factors)}")
    
    if status == 'FF':
        log("✓✓✓ F2 کاملاً فاکتور شده!")
        with open(FOUND_FILE, 'w') as f:
            f.write(f"F2 fully factored!\n{json.dumps(factors, indent=2)}\n")
        return
    log("")
    
    # مرحله 2: اجرای گام‌های ECM و P-1 به‌ترتیب
    # استراتژی بهینه بر اساس اندازه فاکن:
    # 
    # اندازه فاکن | B1 پیشنهادی | curves | زمان تخمینی (هر curve)
    # 30 رقم     | 50K         | 250    | ~1s
    # 35 رقم     | 250K        | 600    | ~2s
    # 40 رقم     | 1M          | 1500   | ~5s
    # 45 رقم     | 5M          | 5000   | ~15s
    # 50 رقم     | 25M         | 10000  | ~50s
    # 55 رقم     | 100M        | 20000  | ~150s
    # 60 رقم     | 500M        | 50000  | ~500s
    #
    # زمان کل برای هر مرحله:
    # 30: 250s, 35: 1200s, 40: 7500s, 45: 75000s, 50: 500000s, 55: 3000000s
    
    phases = [
        # (phase_name, B1, curves, description)
        ('ecm_50K', '5e4', 250, 'برای فاکتور 30 رقمی'),
        ('ecm_250K', '2.5e5', 600, 'برای فاکتور 35 رقمی'),
        ('ecm_1M', '1e6', 1500, 'برای فاکتور 40 رقمی'),
        ('ecm_5M', '5e6', 2000, 'برای فاکتور 45 رقمی (ادامه)'),
        ('ecm_25M', '25e6', 1000, 'برای فاکتور 50 رقمی'),
        ('pm1_1G', '1e9', 1, 'P-1 با B1=1e9 (برای k smooth)'),
        ('pm1_10G', '1e10', 1, 'P-1 با B1=1e10'),
    ]
    
    # پیدا کردن گام بعدی از state
    current_step = state.get('last_step', 0)
    
    for i, (phase_name, B1, curves, desc) in enumerate(phases):
        if i < current_step:
            log(f"skipping phase {i}: {phase_name} (already done)")
            continue
        
        log("")
        log(f"=== مرحله {i+1}/{len(phases)}: {phase_name} - {desc} ===")
        log(f"B1={B1}, curves={curves}")
        
        # بررسی FactorDB قبل از اجرا
        result = query_factordb(F2_STR)
        if result.get('status') == 'FF':
            log("✓✓✓ F2 کاملاً فاکتور شده در FactorDB!")
            with open(FOUND_FILE, 'w') as f:
                f.write(f"F2 fully factored!\n{json.dumps(result.get('factors', []), indent=2)}\n")
            return
        
        log_file = f"{WORKDIR}/{phase_name}.log"
        t0 = time.time()
        
        if phase_name.startswith('ecm'):
            log(f"اجرای ECM...")
            run_ecm_with_log(B1, curves, log_file)
        else:  # pm1
            log(f"اجرای P-1...")
            env = os.environ.copy()
            env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
            with open(log_file, 'w') as out:
                proc = subprocess.Popen(
                    [ECM, '-pm1', '-v', '-timestamp', B1],
                    stdin=subprocess.PIPE,
                    stdout=out,
                    stderr=subprocess.STDOUT,
                    env=env
                )
                proc.communicate(input=F2_STR.encode())
        
        elapsed = time.time() - t0
        log(f"تموم شد در {elapsed:.0f}s ({elapsed/60:.1f} دقیقه)")
        
        # چک کردن فاکتور
        found = check_found_in_log(log_file)
        if found:
            log(f"✓✓✓ FACTOR FOUND: {found}")
            
            # استخراج فاکتور از log
            with open(log_file) as f:
                content = f.read()
            
            # پیدا کردن عدد فاکتور (معمولاً بعد از "Factor found")
            import re
            # الگو: "Factor found in step ..." یا "Found ...-digit factor"
            matches = re.findall(r'(?:Factor found|found)(?:[^0-9]*?)(\d{10,})', content)
            
            with open(FOUND_FILE, 'a') as f:
                f.write(f"\n=== FACTOR FOUND ===\n")
                f.write(f"phase: {phase_name}\n")
                f.write(f"B1: {B1}\n")
                f.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"log line: {found}\n")
                if matches:
                    for m in matches:
                        f.write(f"factor candidate: {m}\n")
                        if check_factor_divides_F2(m):
                            f.write(f"✓✓✓ divides F2!\n")
                            other = F2 // mpz(m)
                            f.write(f"F2 / factor = {other}\n")
                            f.write(f"  digits: {len(str(other))}\n")
                            f.write(f"  prime: {is_prime(other)}\n")
                f.write(f"\n=== Full log ===\n")
                f.write(content[-2000:])
            
            log(f"فاکتور در FOUND_factors.txt ذخیره شد")
            return  # فاکتور پیدا شد
        else:
            log(f"فاکتوری پیدا نشد در این مرحله")
        
        # به‌روزرسانی state
        state['last_step'] = i + 1
        state['last_phase'] = phase_name
        state['last_elapsed'] = elapsed
        save_state(state)
        
        # به‌روزرسانی progress
        with open(PROGRESS_FILE, 'w') as pf:
            pf.write(f"phase: {phase_name}\n")
            pf.write(f"step: {i+1}/{len(phases)}\n")
            pf.write(f"B1: {B1}\n")
            pf.write(f"curves: {curves}\n")
            pf.write(f"elapsed: {elapsed:.0f}s\n")
            pf.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    log("")
    log("=== همه مراحل تموم شد ===")
    log(f"تاریخ: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("اگه فاکتوری پیدا نشده باشه، باید از روش‌های قوی‌تر استفاده کنیم (NFS)")


if __name__ == "__main__":
    main()
