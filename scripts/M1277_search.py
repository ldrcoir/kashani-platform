#!/usr/bin/env python3
"""
فاکتوریزاسیون M(1277) = 2^1277 - 1
====================================
این عدد مرسن شماره 192 در لیست composite Mersenne هست.
M(1277) معروف به کوچک‌ترین عدد مرسن بدون هیچ فاکتور شناخته‌شده است!

تعداد ارقام: 385
وضعیت: C (Composite, no factors known)

استراتژی:
1. Trial Division با k تا 10^8 (برای فاکتورهای کوچک)
2. P-1 با B1 های مختلف
3. ECM با B1 های مختلف
4. هر فاکتور پیدا شده رو با کد پایتون تأیید می‌کنیم
"""

import json
import time
import subprocess
import os
import sys
import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod

P = 1277
M = mpz(2)**P - 1
M_STR = str(M)

WORKDIR = "/home/z/my-project/A136030_M1277_search"
os.makedirs(WORKDIR, exist_ok=True)

ECM = "/home/z/my-project/ecm-extract/usr/bin/ecm"
LD_PATH = "/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"

LOG_FILE = f"{WORKDIR}/search.log"
FOUND_FILE = f"{WORKDIR}/FOUND_factors.txt"
PROGRESS_FILE = f"{WORKDIR}/progress.txt"
STATE_FILE = f"{WORKDIR}/state.json"


def log(msg):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {'last_step': 0, 'factors_found': []}


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(state, f, indent=2)
    os.rename(tmp, STATE_FILE)


def run_ecm(B1, curves, log_file):
    """اجرای ECM"""
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    cmd = [ECM, '-c', str(curves), '-v', '-timestamp', str(B1)]
    
    with open(log_file, 'w') as out:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=out,
            stderr=subprocess.STDOUT,
            env=env
        )
        proc.communicate(input=M_STR.encode())
        return proc.returncode


def run_pm1(B1, log_file):
    """اجرای P-1"""
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    with open(log_file, 'w') as out:
        proc = subprocess.Popen(
            [ECM, '-pm1', '-v', '-timestamp', str(B1)],
            stdin=subprocess.PIPE,
            stdout=out,
            stderr=subprocess.STDOUT,
            env=env
        )
        proc.communicate(input=M_STR.encode())
        return proc.returncode


def check_found_in_log(log_file):
    """چک کردن آیا فاکتور پیدا شده"""
    if not os.path.exists(log_file):
        return None
    with open(log_file) as f:
        content = f.read()
    
    if 'Factor found' in content or 'Found' in content:
        import re
        # پیدا کردن اعداد بزرگ (حداقل 10 رقم)
        matches = re.findall(r'(\d{10,})', content)
        for m in matches:
            try:
                f = mpz(m)
                # بررسی: فاکتور واقعی M(1277)؟
                if f > 1 and f < M and M % f == 0:
                    return str(f)
            except:
                pass
    return None


def trial_division(k_start, k_end):
    """
    Trial Division: q = 2 × 1277 × k + 1
    فقط k هایی که q ≡ ±1 (mod 8)
    """
    found_factors = []
    primes_tested = 0
    
    for k in range(k_start, k_end + 1):
        # شرط mod 8: k ≡ 0 یا 3 (mod 4)
        if (k & 3) != 0 and (k & 3) != 3:
            continue
        
        q = 2 * P * k + 1
        if q > M:
            break
        
        # تست اول بودن سریع
        if not is_prime(q):
            continue
        
        primes_tested += 1
        
        # بررسی فاکتور بودن
        if M % q == 0:
            found_factors.append((k, int(q)))
            log(f"✓✓✓ FACTOR FOUND! k={k}, q={q} ({len(str(q))} digits)")
            
            # ذخیره
            with open(FOUND_FILE, 'a') as f:
                f.write(f"\n=== FACTOR FOUND ===\n")
                f.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"method: Trial Division\n")
                f.write(f"k = {k}\n")
                f.write(f"q = {q}\n")
                f.write(f"q digits = {len(str(q))}\n")
                f.write(f"q prime = {is_prime(mpz(q))}\n")
                other = M // q
                f.write(f"cofactor = {other}\n")
                f.write(f"cofactor digits = {len(str(other))}\n")
                f.write(f"cofactor prime = {is_prime(other)}\n")
    
    return found_factors, primes_tested


def main():
    state = load_state()
    
    log("=" * 70)
    log("جستجوی فاکتورهای M(1277) = 2^1277 - 1")
    log("=" * 70)
    log(f"M(1277) ارقام: {len(M_STR)}")
    log(f"State: {state}")
    log("")
    
    # مراحل جستجو
    phases = [
        # (name, type, params, description)
        ('trial_1e6', 'trial', {'k_start': 1, 'k_end': 10**6}, 
         'Trial Division k ≤ 10^6 (برای فاکتورهای کوچک)'),
        ('trial_1e7', 'trial', {'k_start': 10**6 + 1, 'k_end': 10**7}, 
         'Trial Division k ≤ 10^7'),
        ('trial_1e8', 'trial', {'k_start': 10**7 + 1, 'k_end': 10**8}, 
         'Trial Division k ≤ 10^8'),
        ('pm1_1e8', 'pm1', {'B1': '1e8'}, 
         'P-1 با B1=1e8 (k smooth تا 10^8)'),
        ('ecm_1e6', 'ecm', {'B1': '1e6', 'curves': 1000}, 
         'ECM با B1=1e6 (فاکتور 35-40 رقمی)'),
        ('pm1_1e9', 'pm1', {'B1': '1e9'}, 
         'P-1 با B1=1e9 (k smooth تا 10^9)'),
        ('ecm_1e7', 'ecm', {'B1': '1e7', 'curves': 2000}, 
         'ECM با B1=1e7 (فاکتور 40-45 رقمی)'),
        ('ecm_1e8', 'ecm', {'B1': '1e8', 'curves': 3000}, 
         'ECM با B1=1e8 (فاکتور 45-50 رقمی)'),
        ('pm1_1e10', 'pm1', {'B1': '1e10'}, 
         'P-1 با B1=1e10'),
        ('ecm_1e9', 'ecm', {'B1': '1e9', 'curves': 5000}, 
         'ECM با B1=1e9 (فاکتور 50-55 رقمی)'),
    ]
    
    current_step = state.get('last_step', 0)
    
    for i, (phase_name, phase_type, params, desc) in enumerate(phases):
        if i < current_step:
            log(f"skipping phase {i}: {phase_name} (already done)")
            continue
        
        log("")
        log(f"=== مرحله {i+1}/{len(phases)}: {phase_name} - {desc} ===")
        
        log_file = f"{WORKDIR}/{phase_name}.log"
        t0 = time.time()
        
        if phase_type == 'trial':
            log(f"اجرای Trial Division k=[{params['k_start']}, {params['k_end']}]")
            factors, primes_tested = trial_division(params['k_start'], params['k_end'])
            elapsed = time.time() - t0
            log(f"تموم شد در {elapsed:.0f}s, primes tested: {primes_tested}, factors: {len(factors)}")
            
            if factors:
                state['factors_found'] = state.get('factors_found', []) + [
                    {'k': k, 'q': str(q)} for k, q in factors
                ]
                save_state(state)
        
        elif phase_type == 'pm1':
            log(f"اجرای P-1 با B1={params['B1']}")
            run_pm1(params['B1'], log_file)
            elapsed = time.time() - t0
            log(f"تموم شد در {elapsed:.0f}s ({elapsed/60:.1f} دقیقه)")
            
            found = check_found_in_log(log_file)
            if found:
                log(f"✓✓✓ FACTOR FOUND: {found}")
                with open(FOUND_FILE, 'a') as f:
                    f.write(f"\n=== FACTOR FOUND ===\n")
                    f.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"method: P-1\n")
                    f.write(f"B1: {params['B1']}\n")
                    f.write(f"factor: {found}\n")
                    f.write(f"factor digits: {len(found)}\n")
                    f.write(f"factor prime: {is_prime(mpz(found))}\n")
                    other = M // mpz(found)
                    f.write(f"cofactor: {other}\n")
                    f.write(f"cofactor digits: {len(str(other))}\n")
                    f.write(f"cofactor prime: {is_prime(other)}\n")
                
                state['factors_found'] = state.get('factors_found', []) + [
                    {'method': 'P-1', 'B1': params['B1'], 'factor': found}
                ]
                save_state(state)
            else:
                log(f"فاکتوری پیدا نشد")
        
        elif phase_type == 'ecm':
            log(f"اجرای ECM با B1={params['B1']}, curves={params['curves']}")
            run_ecm(params['B1'], params['curves'], log_file)
            elapsed = time.time() - t0
            log(f"تموم شد در {elapsed:.0f}s ({elapsed/60:.1f} دقیقه)")
            
            found = check_found_in_log(log_file)
            if found:
                log(f"✓✓✓ FACTOR FOUND: {found}")
                with open(FOUND_FILE, 'a') as f:
                    f.write(f"\n=== FACTOR FOUND ===\n")
                    f.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"method: ECM\n")
                    f.write(f"B1: {params['B1']}\n")
                    f.write(f"curves: {params['curves']}\n")
                    f.write(f"factor: {found}\n")
                    f.write(f"factor digits: {len(found)}\n")
                    f.write(f"factor prime: {is_prime(mpz(found))}\n")
                    other = M // mpz(found)
                    f.write(f"cofactor: {other}\n")
                    f.write(f"cofactor digits: {len(str(other))}\n")
                    f.write(f"cofactor prime: {is_prime(other)}\n")
                
                state['factors_found'] = state.get('factors_found', []) + [
                    {'method': 'ECM', 'B1': params['B1'], 'factor': found}
                ]
                save_state(state)
            else:
                log(f"فاکتوری پیدا نشد")
        
        # به‌روزرسانی state
        state['last_step'] = i + 1
        state['last_phase'] = phase_name
        state['last_elapsed'] = elapsed
        save_state(state)
        
        with open(PROGRESS_FILE, 'w') as pf:
            pf.write(f"phase: {phase_name}\n")
            pf.write(f"step: {i+1}/{len(phases)}\n")
            pf.write(f"elapsed: {elapsed:.0f}s\n")
            pf.write(f"factors_found: {len(state.get('factors_found', []))}\n")
            pf.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    log("")
    log("=== همه مراحل تموم شد ===")
    log(f"تعداد فاکتورهای پیدا شده: {len(state.get('factors_found', []))}")


if __name__ == "__main__":
    main()
