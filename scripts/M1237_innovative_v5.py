#!/usr/bin/env python3
"""
روش ابتکاری v5: فاکتوریزاسیون Z + P-1 هوشمند
================================================
ایده کلیدی:
1. F2 - 1 = 2^4 × 3 × 7 × 1237 × Z
2. Z (298 رقم) مرکب هست - اگه فاکتورهای Z رو پیدا کنیم
3. اگه فاکتور q از F2 به فرم q = 2 × 1237 × k + 1 باشه
   و k شامل فاکتورهای Z باشه، P-1 با extra_factors پیدا می‌کنه

روش:
1. فاکتوریزاسیون Z با ECM (Z کوچک‌تر از F2 هست)
2. استفاده از فاکتورهای Z در P-1 برای F2
3. تکرار با پارامترهای مختلف
"""

import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod
import time
import json
import os
import subprocess

P = 1237
M_1237 = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M_1237 // F1

# F2 - 1 = 2^4 × 3 × 7 × 1237 × Z
Z = (F2 - 1) // (2**4 * 3 * 7 * 1237)

WORKDIR = "/home/z/my-project/A136030_M1237_innovative_v5"
os.makedirs(WORKDIR, exist_ok=True)

ECM = "/home/z/my-project/ecm-extract/usr/bin/ecm"
LD_PATH = "/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"

LOG_FILE = f"{WORKDIR}/search.log"
FOUND_FILE = f"{WORKDIR}/FOUND_factors.txt"
PROGRESS_FILE = f"{WORKDIR}/progress.txt"
STATE_FILE = f"{WORKDIR}/state.json"
Z_FACTORS_FILE = f"{WORKDIR}/Z_factors.txt"


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
    return {'last_step': 0, 'z_factors': [], 'factors_found': []}


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(state, f, indent=2)
    os.rename(tmp, STATE_FILE)


def verify_and_save(method, factor, **kwargs):
    """تأیید چندباره فاکتور F2"""
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
    
    log(f"✓✓✓ FACTOR OF F2 FOUND!")
    log(f"  method: {method}")
    log(f"  factor: {f}")
    log(f"  factor digits: {len(str(f))}")
    log(f"  factor prime: {is_prime(f)}")
    log(f"  cofactor: {cofactor}")
    log(f"  cofactor digits: {len(str(cofactor))}")
    log(f"  cofactor prime: {is_prime(cofactor)}")
    
    with open(FOUND_FILE, 'a') as out:
        out.write(f"\n=== FACTOR OF F2 FOUND ===\n")
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


def factorize_Z_with_ecm(B1, curves, label):
    """فاکتوریزاسیون Z با ECM"""
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    log_file = f"{WORKDIR}/Z_ecm_{label}.log"
    log(f"ECM on Z {label}: B1={B1}, curves={curves}")
    t0 = time.time()
    
    cmd = [ECM, '-c', str(curves), '-v', '-timestamp', str(B1)]
    
    with open(log_file, 'w') as out:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=out,
            stderr=subprocess.STDOUT,
            env=env
        )
        proc.communicate(input=str(Z).encode())
    
    elapsed = time.time() - t0
    log(f"تمام شد در {elapsed:.0f}s")
    
    # چک کردن فاکتورهای Z
    z_factors_found = []
    if os.path.exists(log_file):
        with open(log_file) as f:
            content = f.read()
        
        if 'Factor found' in content or 'found' in content.lower():
            import re
            matches = re.findall(r'(\d{10,})', content)
            for m in matches:
                f_z = mpz(m)
                if f_z > 1 and f_z < Z and Z % f_z == 0:
                    z_factors_found.append(str(f_z))
                    log(f"  Z factor found: {f_z}")
    
    return z_factors_found


def pm1_with_z_factors(B1, z_factors):
    """P-1 با extra_factors از Z"""
    log(f"P-1 با B1={B1} + {len(z_factors)} فاکتور Z")
    t0 = time.time()
    
    # تولید اعداد اول تا B1
    if B1 > 10**8:
        # استفاده از ecm -pm1
        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
        
        log_file = f"{WORKDIR}/pm1_B1_{B1}.log"
        with open(log_file, 'w') as out:
            proc = subprocess.Popen(
                [ECM, '-pm1', '-v', '-timestamp', str(B1)],
                stdin=subprocess.PIPE,
                stdout=out,
                stderr=subprocess.STDOUT,
                env=env
            )
            proc.communicate(input=str(F2).encode())
        
        # چک فاکتور
        with open(log_file) as f:
            content = f.read()
        
        if 'Factor found' in content:
            import re
            matches = re.findall(r'(\d{10,})', content)
            for m in matches:
                f = mpz(m)
                if f > 1 and f < F2 and F2 % f == 0:
                    if verify_and_save("P-1 with Z factors", m, B1=B1):
                        return True
        return False
    
    # P-1 محلی برای B1 کوچک
    sieve = bytearray([1]) * (B1 + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(B1**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, B1 + 1, i):
                sieve[j] = 0
    primes = [i for i in range(2, B1 + 1) if sieve[i]]
    
    # اضافه کردن فاکتورهای Z
    for zf in z_factors:
        zf_int = int(zf)
        if is_prime(mpz(zf_int)) and zf_int not in primes:
            primes.append(zf_int)
    
    log(f"تعداد اعداد اول: {len(primes)}")
    
    # P-1
    a = mpz(2)
    for p in primes:
        e = 1
        pe = p
        while pe * p <= B1:
            pe *= p
            e += 1
        a = powmod(a, pe, F2)
    
    g = gcd(a - 1, F2)
    elapsed = time.time() - t0
    
    log(f"تمام شد در {elapsed:.0f}s, gcd = {g}")
    
    if g > 1 and g < F2:
        if verify_and_save("P-1 with Z factors", g, B1=B1, z_factors=len(z_factors)):
            return True
    
    return False


def main():
    state = load_state()
    
    log("=" * 70)
    log("روش ابتکاری v5: فاکتوریزاسیون Z + P-1 هوشمند")
    log("=" * 70)
    log(f"F2 = {str(F2)[:60]}... ({len(str(F2))} رقم)")
    log(f"Z = {str(Z)[:60]}... ({len(str(Z))} رقم)")
    log(f"State: {state}")
    log("")
    log("ایده کلیدی:")
    log("  F2 - 1 = 2^4 × 3 × 7 × 1237 × Z")
    log("  اگه فاکتورهای Z رو پیدا کنیم، می‌تونیم در P-1 برای F2 استفاده کنیم")
    log("")
    
    # مراحل
    phases = [
        ('Z_ecm_1e6', 'Z_ecm', {'B1': '1e6', 'curves': 500, 'label': '1e6'}, 
         'ECM روی Z با B1=1e6 (فاکتورهای کوچک Z)'),
        ('Z_ecm_1e7', 'Z_ecm', {'B1': '1e7', 'curves': 1000, 'label': '1e7'}, 
         'ECM روی Z با B1=1e7 (فاکتورهای متوسط Z)'),
        ('Z_ecm_1e8', 'Z_ecm', {'B1': '1e8', 'curves': 2000, 'label': '1e8'}, 
         'ECM روی Z با B1=1e8 (فاکتورهای بزرگ Z)'),
        ('pm1_with_Z', 'pm1_z', {'B1': 10**8}, 
         'P-1 با فاکتورهای Z (اگه پیدا شد)'),
        ('Z_ecm_1e9', 'Z_ecm', {'B1': '1e9', 'curves': 3000, 'label': '1e9'}, 
         'ECM روی Z با B1=1e9 (فاکتورهای بزرگ‌تر Z)'),
        ('pm1_1e9_with_Z', 'pm1_z', {'B1': 10**9}, 
         'P-1 با B1=1e9 + فاکتورهای Z'),
    ]
    
    current_step = state.get('last_step', 0)
    z_factors = state.get('z_factors', [])
    
    for i, (phase_name, phase_type, params, desc) in enumerate(phases):
        if i < current_step:
            log(f"skipping phase {i}: {phase_name} (already done)")
            continue
        
        log("")
        log(f"=== مرحله {i+1}/{len(phases)}: {phase_name} - {desc} ===")
        
        t0 = time.time()
        found = False
        
        if phase_type == 'Z_ecm':
            new_z_factors = factorize_Z_with_ecm(
                params['B1'], params['curves'], params['label']
            )
            z_factors.extend(new_z_factors)
            # حذف تکراری‌ها
            z_factors = list(set(z_factors))
            state['z_factors'] = z_factors
            log(f"تعداد فاکتورهای Z تا الان: {len(z_factors)}")
            
            # ذخیره فاکتورهای Z
            with open(Z_FACTORS_FILE, 'w') as f:
                f.write(f"Z = {Z}\n\n")
                f.write(f"Z factors found:\n")
                for zf in z_factors:
                    f.write(f"  {zf}\n")
        
        elif phase_type == 'pm1_z':
            if not z_factors:
                log("هیچ فاکتور Z پیدا نشده، skip")
            else:
                found = pm1_with_z_factors(params['B1'], z_factors)
        
        elapsed = time.time() - t0
        
        state['last_step'] = i + 1
        state['last_phase'] = phase_name
        state['last_elapsed'] = elapsed
        save_state(state)
        
        with open(PROGRESS_FILE, 'w') as pf:
            pf.write(f"phase: {phase_name}\n")
            pf.write(f"step: {i+1}/{len(phases)}\n")
            pf.write(f"elapsed: {elapsed:.0f}s\n")
            pf.write(f"z_factors: {len(z_factors)}\n")
            pf.write(f"f2_factors: {len(state.get('factors_found', []))}\n")
            pf.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if found:
            log(f"✓✓✓ فاکتور F2 پیدا شد! توقف.")
            return
    
    log("")
    log("=== همه مراحل تموم شد ===")
    log(f"تعداد فاکتورهای Z: {len(z_factors)}")
    log(f"تعداد فاکتورهای F2: {len(state.get('factors_found', []))}")


if __name__ == "__main__":
    main()
