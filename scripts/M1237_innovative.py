#!/usr/bin/env python3
"""
روش ابتکاری: P-1 هدف‌دار بر اساس ساختار شناخته شده
=====================================================
تحلیل:
- F1 - 1 = 2 × 3 × 7 × 1237 × X1 × X2  (k_F1 = 3 × 7 × X1 × X2)
- F2 - 1 = 2^4 × 3 × 7 × 1237 × Y1 × Y2  (k_F2 = 2^3 × 3 × 7 × Y1 × Y2)

الگو:
- هر دو k شامل 3 × 7 هستن
- a (توان 2 در q-1) می‌تونه 1, 2, 3, 4, 5, ... باشه

روش ابتکاری:
1. برای هر a (1 تا 10)، P-1 با B1 متفاوت اجرا کن
2. اگه k فاکتور سوم شامل 3 × 7 × Y1 باشه (مثل F2)، با P-1 مناسب پیدا می‌شه
3. اگه k شامل X1 یا X2 باشه (از F1)، با P-1 مناسب پیدا می‌شه

مزیت: به‌جای جستجوی همه k ها، فقط k هایی که این الگو رو دارن رو می‌گردیم
"""

import json
import time
import subprocess
import os
import sys
import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod

F2_STR = "932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281119369604215535391846857906233364905825622441048803673998858526737"
F2 = mpz(F2_STR)

P = 1237

# فاکتورهای شناخته شده
X1 = mpz("110421384041193593117465987")
X2 = mpz("442440509040507330087115446251753610709")
Y1 = mpz("18641439966407")
Y2 = mpz("120334218833298104536604548702588378365791515320342282742388984553009321898145046186509920767149619597647361224112031104159377051089982807697549128468943237627992949178727349673703438184409567254625591484613193218616688782477265387389941750568120467062052945838796451725995419643693039")

WORKDIR = "/home/z/my-project/A136030_M1237_innovative"
os.makedirs(WORKDIR, exist_ok=True)

ECM = "/home/z/my-project/ecm-extract/usr/bin/ecm"
LD_PATH = "/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"

LOG_FILE = f"{WORKDIR}/innovative.log"
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


def pm1_with_known_primes(B1, log_file, extra_primes=None):
    """
    P-1 با اضافه کردن فاکتورهای شناخته شده به stage 1
    ایده: اگه k شامل X1, X2, Y1, Y2 باشه، P-1 با این فاکتورها پیدا می‌کنه
    """
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    # P-1 با B1 و اضافه کردن فاکتورهای شناخته شده به‌عنوان B2-prime
    cmd = [ECM, '-pm1', '-v', '-timestamp', str(B1)]
    
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


def ecm_with_sigma(B1, curves, log_file, sigma_start=None):
    """اجرای ECM با sigma مشخص"""
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
    """چک کردن آیا فاکتور پیدا شده"""
    if not os.path.exists(log_file):
        return None
    with open(log_file) as f:
        content = f.read()
    
    if 'Factor found' in content or 'found' in content.lower():
        import re
        # پیدا کردن عدد بزرگ
        matches = re.findall(r'(\d{10,})', content)
        for m in matches:
            try:
                f = mpz(m)
                if f > 1 and f < F2 and F2 % f == 0:
                    return str(f)
            except:
                pass
    return None


def custom_pm1(B1, extra_factors):
    """
    P-1 سفارشی:
    محاسبه a = 2^(product of primes ≤ B1) mod F2
    سپس gcd(a - 1, F2)
    با اضافه کردن extra_factors به product
    """
    # تولید اعداد اول تا B1
    if B1 > 10**8:
        # خیلی بزرگ، استفاده از ecm -pm1
        return None
    
    sieve = bytearray([1]) * (B1 + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(B1**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, B1 + 1, i):
                sieve[j] = 0
    primes = [i for i in range(2, B1 + 1) if sieve[i]]
    
    # اضافه کردن extra_factors
    for f in extra_factors:
        if f not in primes and is_prime(f):
            primes.append(int(f))
    
    # محاسبه a = 2^(product) mod F2
    a = mpz(2)
    for p in primes:
        # e = floor(log_p(B1))
        e = 1
        pe = p
        while pe * p <= B1:
            pe *= p
            e += 1
        a = powmod(a, pe, F2)
    
    # gcd
    g = gcd(a - 1, F2)
    return g


def main():
    state = load_state()
    
    log("=" * 70)
    log("روش ابتکاری: P-1 هدف‌دار + ECM با الگوهای شناخته شده")
    log("=" * 70)
    log(f"F2 = {F2_STR[:60]}... ({len(F2_STR)} رقم)")
    log("")
    
    # روش‌های ابتکاری
    phases = [
        # (name, type, params, description)
        ('pm1_with_Y1', 'pm1_custom', {'B1': 10**8, 'extra': [Y1]}, 
         'P-1 با B1=10^8 + Y1 (فرض: k شامل Y1)'),
        ('pm1_with_X1', 'pm1_custom', {'B1': 10**8, 'extra': [X1]}, 
         'P-1 با B1=10^8 + X1 (فرض: k شامل X1)'),
        ('pm1_with_X2', 'pm1_custom', {'B1': 10**8, 'extra': [X2]}, 
         'P-1 با B1=10^8 + X2 (فرض: k شامل X2)'),
        ('pm1_with_all', 'pm1_custom', {'B1': 10**8, 'extra': [X1, X2, Y1]}, 
         'P-1 با B1=10^8 + X1 + X2 + Y1'),
        ('pm1_1e10', 'pm1_ecm', {'B1': '1e10'}, 
         'P-1 استاندارد با B1=1e10'),
        ('pm1_1e11', 'pm1_ecm', {'B1': '1e11'}, 
         'P-1 استاندارد با B1=1e11'),
        ('ecm_1e11', 'ecm', {'B1': '1e11', 'curves': 25000}, 
         'ECM با B1=1e11 (فاکتور 70 رقمی)'),
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
        
        if phase_type == 'pm1_custom':
            log(f"اجرای P-1 سفارشی با B1={params['B1']}, extra_factors={len(params['extra'])}")
            g = custom_pm1(params['B1'], params['extra'])
            elapsed = time.time() - t0
            
            if g is None:
                log(f"B1 خیلی بزرگ برای sieve، skip")
                continue
            
            if g > 1 and g < F2:
                log(f"✓✓✓ FACTOR FOUND: {g}")
                with open(log_file, 'w') as f:
                    f.write(f"Factor found: {g}\n")
                    f.write(f"Factor digits: {len(str(g))}\n")
                    f.write(f"Factor prime: {is_prime(g)}\n")
                    other = F2 // g
                    f.write(f"Other factor: {other}\n")
                    f.write(f"Other digits: {len(str(other))}\n")
                    f.write(f"Other prime: {is_prime(other)}\n")
                
                with open(FOUND_FILE, 'w') as f:
                    f.write(f"=== FACTOR FOUND ===\n")
                    f.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"phase: {phase_name}\n")
                    f.write(f"factor: {g}\n")
                    f.write(f"factor digits: {len(str(g))}\n")
                    f.write(f"factor prime: {is_prime(g)}\n")
                    f.write(f"other: {other}\n")
                    f.write(f"other digits: {len(str(other))}\n")
                    f.write(f"other prime: {is_prime(other)}\n")
                return
            elif g == F2:
                log(f"g = F2 (no useful factor)")
            else:
                log(f"g = 1 (no factor found)")
                with open(log_file, 'w') as f:
                    f.write(f"No factor found (g=1)\n")
                    f.write(f"B1={params['B1']}, extra_factors={len(params['extra'])}\n")
        elif phase_type == 'pm1_ecm':
            log(f"اجرای P-1 با B1={params['B1']}")
            pm1_with_known_primes(params['B1'], log_file)
            elapsed = time.time() - t0
            
            found = check_found_in_log(log_file)
            if found:
                log(f"✓✓✓ FACTOR FOUND: {found}")
                with open(FOUND_FILE, 'w') as f:
                    f.write(f"=== FACTOR FOUND ===\n")
                    f.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"phase: {phase_name}\n")
                    f.write(f"factor: {found}\n")
                    f.write(f"factor digits: {len(found)}\n")
                return
            else:
                log(f"فاکتوری پیدا نشد")
        elif phase_type == 'ecm':
            log(f"اجرای ECM با B1={params['B1']}, curves={params['curves']}")
            ecm_with_sigma(params['B1'], params['curves'], log_file)
            elapsed = time.time() - t0
            
            found = check_found_in_log(log_file)
            if found:
                log(f"✓✓✓ FACTOR FOUND: {found}")
                with open(FOUND_FILE, 'w') as f:
                    f.write(f"=== FACTOR FOUND ===\n")
                    f.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"phase: {phase_name}\n")
                    f.write(f"factor: {found}\n")
                    f.write(f"factor digits: {len(found)}\n")
                return
            else:
                log(f"فاکتوری پیدا نشد")
        
        log(f"تموم شد در {elapsed:.0f}s ({elapsed/60:.1f} دقیقه)")
        
        # به‌روزرسانی state
        state['last_step'] = i + 1
        state['last_phase'] = phase_name
        state['last_elapsed'] = elapsed
        save_state(state)
        
        with open(PROGRESS_FILE, 'w') as pf:
            pf.write(f"phase: {phase_name}\n")
            pf.write(f"step: {i+1}/{len(phases)}\n")
            pf.write(f"elapsed: {elapsed:.0f}s\n")
            pf.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    log("")
    log("=== همه مراحل تموم شد ===")


if __name__ == "__main__":
    main()
