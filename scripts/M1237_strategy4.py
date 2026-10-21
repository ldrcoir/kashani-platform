#!/usr/bin/env python3
"""
استراتژی 4: جستجوی فاکتورهای 70+ رقمی F2
=========================================
تحلیل کاربر:
- F1 (70 رقم) پیدا شده
- پس فاکتور بعدی احتمالاً 70+ رقمی هست
- باید از 70 رقم به بالا بگردیم

برای فاکتورهای 70+ رقمی، ECM به این پارامترها نیاز داره:
- B1 = 1e11, ~25000 curves برای فاکتور 60 رقمی
- B1 = 1e12, ~60000 curves برای فاکتور 65 رقمی  
- B1 = 1e13, ~150000 curves برای فاکتور 70 رقمی
- B1 = 1e14, ~400000 curves برای فاکتور 75 رقمی

استراتژی:
1. اجرای ECM با B1 های بزرگ به صورت موازی
2. P-1 با B1 های بزرگ (1e10, 1e11, 1e12)
3. استفاده از تمام CPU cores
"""

import json
import time
import subprocess
import os
import sys
import multiprocessing as mp
import gmpy2
from gmpy2 import mpz, is_prime

F2_STR = "932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281199369604215535391846857906233364905825622441048803673998858526737"
F2 = mpz(F2_STR)

WORKDIR = "/home/z/my-project/A136030_M1237_strategy4"
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


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {'last_step': 0}


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(state, f, indent=2)
    os.rename(tmp, STATE_FILE)


def run_ecm(B1, curves, log_file, sigma=None):
    """اجرای ECM"""
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    cmd = [ECM, '-c', str(curves), '-v', '-timestamp', str(B1)]
    if sigma:
        cmd.extend(['-sigma', str(sigma)])
    
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
        proc.communicate(input=F2_STR.encode())
        return proc.returncode


def check_found_in_log(log_file):
    """چک کردن آیا فاکتور پیدا شده"""
    if not os.path.exists(log_file):
        return None
    with open(log_file) as f:
        content = f.read()
    
    if 'Factor found' in content:
        import re
        # الگوهای مختلف
        # "Factor found in step ..."
        # "Found ...-digit factor"
        matches = re.findall(r'(\d{10,})', content)
        for m in matches:
            try:
                f = mpz(m)
                if F2 % f == 0 and f > 1 and f < F2:
                    return str(f)
            except:
                pass
    return None


def main():
    state = load_state()
    
    log("=" * 70)
    log("استراتژی 4: جستجوی فاکتورهای 70+ رقمی F2")
    log("=" * 70)
    log(f"F2 = {F2_STR[:60]}... ({len(F2_STR)} رقم)")
    log(f"State: {state}")
    log("")
    
    # مراحل جستجو - از 60 رقم به بالا
    phases = [
        # (phase_name, B1, curves, description)
        ('ecm_1e9',   '1e9',  5000,  'برای فاکتور 50-55 رقمی'),
        ('ecm_5e9',   '5e9',  5000,  'برای فاکتور 55-60 رقمی'),
        ('ecm_1e10',  '1e10', 10000, 'برای فاکتور 60 رقمی'),
        ('pm1_1e11',  '1e11', 1,     'P-1 با B1=1e11 (k smooth تا 10^11)'),
        ('ecm_5e10',  '5e10', 15000, 'برای فاکتور 65 رقمی'),
        ('ecm_1e11',  '1e11', 25000, 'برای فاکتور 70 رقمی'),
        ('pm1_1e12',  '1e12', 1,     'P-1 با B1=1e12'),
        ('ecm_5e11',  '5e11', 60000, 'برای فاکتور 75 رقمی'),
    ]
    
    current_step = state.get('last_step', 0)
    
    for i, (phase_name, B1, curves, desc) in enumerate(phases):
        if i < current_step:
            log(f"skipping phase {i}: {phase_name} (already done)")
            continue
        
        log("")
        log(f"=== مرحله {i+1}/{len(phases)}: {phase_name} - {desc} ===")
        log(f"B1={B1}, curves={curves}")
        
        log_file = f"{WORKDIR}/{phase_name}.log"
        t0 = time.time()
        
        if phase_name.startswith('ecm'):
            log(f"اجرای ECM...")
            run_ecm(B1, curves, log_file)
        else:  # pm1
            log(f"اجرای P-1...")
            run_pm1(B1, log_file)
        
        elapsed = time.time() - t0
        log(f"تموم شد در {elapsed:.0f}s ({elapsed/60:.1f} دقیقه, {elapsed/3600:.2f} ساعت)")
        
        # چک کردن فاکتور
        found = check_found_in_log(log_file)
        if found:
            log(f"✓✓✓ FACTOR FOUND: {found}")
            other = F2 // mpz(found)
            log(f"F2 = factor × {other}")
            log(f"  factor digits: {len(found)}")
            log(f"  other digits: {len(str(other))}")
            log(f"  factor prime: {is_prime(mpz(found))}")
            log(f"  other prime: {is_prime(other)}")
            
            with open(FOUND_FILE, 'w') as f:
                f.write(f"=== FACTOR FOUND ===\n")
                f.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"phase: {phase_name}\n")
                f.write(f"B1: {B1}\n")
                f.write(f"factor: {found}\n")
                f.write(f"factor digits: {len(found)}\n")
                f.write(f"factor prime: {is_prime(mpz(found))}\n")
                f.write(f"other: {other}\n")
                f.write(f"other digits: {len(str(other))}\n")
                f.write(f"other prime: {is_prime(other)}\n")
            return
        else:
            log(f"فاکتوری پیدا نشد در این مرحله")
        
        # به‌روزرسانی state
        state['last_step'] = i + 1
        state['last_phase'] = phase_name
        state['last_elapsed'] = elapsed
        save_state(state)
        
        with open(PROGRESS_FILE, 'w') as pf:
            pf.write(f"phase: {phase_name}\n")
            pf.write(f"step: {i+1}/{len(phases)}\n")
            pf.write(f"B1: {B1}\n")
            pf.write(f"curves: {curves}\n")
            pf.write(f"elapsed: {elapsed:.0f}s ({elapsed/3600:.2f}h)\n")
            pf.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    log("")
    log("=== همه مراحل تموم شد ===")


if __name__ == "__main__":
    main()
