#!/usr/bin/env python3
"""
استراتژی v4: جستجوی مستقیم فاکتورهای 70+ رقمی
================================================
تحلیل کاربر: اگر فاکتور زیر 70 رقم بود، قبلاً پیدا می‌شد.
پس مستقیم بریم سراغ B1 بزرگ برای فاکتورهای 70+ رقمی.

برای فاکتورهای 70+ رقمی:
- ECM B1=1e10, ~15000 curves (فاکتور 60-65 رقمی)
- ECM B1=5e10, ~25000 curves (فاکتور 65-70 رقمی)
- ECM B1=1e11, ~40000 curves (فاکتور 70 رقمی)
- ECM B1=5e11, ~100000 curves (فاکتور 75 رقمی)
- P-1 B1=1e11 (اگه k smooth تا 10^11)
- P-1 B1=1e12 (اگه k smooth تا 10^12)
"""

import gmpy2
from gmpy2 import mpz, is_prime
import time
import json
import os
import subprocess

P = 1237
M_1237 = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M_1237 // F1

WORKDIR = "/home/z/my-project/A136030_M1237_strategy_v4"
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


def verify_and_save(method, factor, **kwargs):
    """تأیید چندباره فاکتور"""
    f = mpz(factor)
    
    if f <= 1 or f >= F2:
        return False
    if F2 % f != 0:
        return False
    if F2 % f != 0:
        return False
    
    cofactor = F2 // f
    if f * cofactor != F2:
        return False
    
    log(f"✓✓✓ FACTOR FOUND!")
    log(f"  method: {method}")
    log(f"  factor: {f}")
    log(f"  factor digits: {len(str(f))}")
    log(f"  factor prime: {is_prime(f)}")
    log(f"  cofactor: {cofactor}")
    log(f"  cofactor digits: {len(str(cofactor))}")
    log(f"  cofactor prime: {is_prime(cofactor)}")
    
    with open(FOUND_FILE, 'a') as out:
        out.write(f"\n=== FACTOR FOUND ===\n")
        out.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"method: {method}\n")
        for k, v in kwargs.items():
            out.write(f"{k}: {v}\n")
        out.write(f"factor: {f}\n")
        out.write(f"factor digits: {len(str(f))}\n")
        out.write(f"factor prime: {is_prime(f)}\n")
        out.write(f"cofactor: {cofactor}\n")
        out.write(f"cofactor digits: {len(str(cofactor))}\n")
        out.write(f"cofactor prime: {is_prime(cofactor)}\n")
        out.write(f"\nVERIFICATION:\n")
        out.write(f"F2 mod factor = {F2 % f}\n")
        out.write(f"factor × cofactor = F2? {f * cofactor == F2}\n")
    
    return True


def run_method(method, B1, curves, label):
    """اجرای ECM/P-1/P+1"""
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    log_file = f"{WORKDIR}/{method}_{label}.log"
    log(f"{method} {label}: B1={B1}, curves={curves}")
    t0 = time.time()
    
    if method == 'ecm':
        cmd = [ECM, '-c', str(curves), '-v', '-timestamp', str(B1)]
    elif method == 'pm1':
        cmd = [ECM, '-pm1', '-v', '-timestamp', str(B1)]
    elif method == 'pp1':
        cmd = [ECM, '-pp1', '-v', '-timestamp', str(B1)]
    
    with open(log_file, 'w') as out:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=out,
            stderr=subprocess.STDOUT,
            env=env
        )
        proc.communicate(input=str(F2).encode())
    
    elapsed = time.time() - t0
    log(f"تمام شد در {elapsed:.0f}s ({elapsed/3600:.2f} ساعت)")
    
    if os.path.exists(log_file):
        with open(log_file) as f:
            content = f.read()
        
        if 'Factor found' in content or 'found' in content.lower():
            import re
            matches = re.findall(r'(\d{10,})', content)
            for m in matches:
                f = mpz(m)
                if f > 1 and f < F2 and F2 % f == 0:
                    if verify_and_save(method, m, B1=B1, curves=curves, label=label):
                        return True
    
    return False


def main():
    state = load_state()
    
    log("=" * 70)
    log("استراتژی v4: جستجوی مستقیم فاکتورهای 70+ رقمی")
    log("=" * 70)
    log(f"F2 = {str(F2)[:60]}... ({len(str(F2))} رقم)")
    log(f"State: {state}")
    log("")
    log("تحلیل: فاکتورهای زیر 55 رقم قبلاً بررسی شده‌اند.")
    log("تمرکز: فاکتورهای 65-80 رقمی")
    log("")
    
    # مراحل - فقط B1 بزرگ برای فاکتورهای 70+
    phases = [
        ('pm1_1e11', 'pm1', {'B1': '1e11', 'curves': 1, 'label': 'B1_1e11'}, 
         'P-1 با B1=1e11 (k smooth تا 10^11)'),
        ('pp1_1e11', 'pp1', {'B1': '1e11', 'curves': 1, 'label': 'B1_1e11'}, 
         'P+1 با B1=1e11 (اگه p+1 smooth)'),
        ('ecm_1e10', 'ecm', {'B1': '1e10', 'curves': 15000, 'label': 'B1_1e10'}, 
         'ECM B1=1e10 (فاکتور 60-65 رقمی)'),
        ('ecm_5e10', 'ecm', {'B1': '5e10', 'curves': 25000, 'label': 'B1_5e10'}, 
         'ECM B1=5e10 (فاکتور 65-70 رقمی)'),
        ('pm1_1e12', 'pm1', {'B1': '1e12', 'curves': 1, 'label': 'B1_1e12'}, 
         'P-1 با B1=1e12 (k smooth تا 10^12)'),
        ('ecm_1e11', 'ecm', {'B1': '1e11', 'curves': 40000, 'label': 'B1_1e11'}, 
         'ECM B1=1e11 (فاکتور 70 رقمی)'),
        ('ecm_5e11', 'ecm', {'B1': '5e11', 'curves': 100000, 'label': 'B1_5e11'}, 
         'ECM B1=5e11 (فاکتور 75 رقمی)'),
    ]
    
    current_step = state.get('last_step', 0)
    
    for i, (phase_name, method, params, desc) in enumerate(phases):
        if i < current_step:
            log(f"skipping phase {i}: {phase_name} (already done)")
            continue
        
        log("")
        log(f"=== مرحله {i+1}/{len(phases)}: {phase_name} - {desc} ===")
        
        t0 = time.time()
        found = run_method(
            method, params['B1'], params['curves'], params['label']
        )
        elapsed = time.time() - t0
        
        state['last_step'] = i + 1
        state['last_phase'] = phase_name
        state['last_elapsed'] = elapsed
        save_state(state)
        
        with open(PROGRESS_FILE, 'w') as pf:
            pf.write(f"phase: {phase_name}\n")
            pf.write(f"step: {i+1}/{len(phases)}\n")
            pf.write(f"elapsed: {elapsed:.0f}s ({elapsed/3600:.2f}h)\n")
            pf.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if found:
            log(f"✓✓✓ فاکتور پیدا شد! توقف.")
            return
    
    log("")
    log("=== همه مراحل تموم شد ===")


if __name__ == "__main__":
    main()
