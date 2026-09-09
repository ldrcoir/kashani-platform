#!/usr/bin/env python3
"""
روش ابتکاری واقعی برای فاکتوریزاسیون F2 صحیح M(1237)
=====================================================
F2 = 932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281119369604215535391846857906233364905825622441048803673998858526737

این عدد 303 رقمی مرکب است و هنوز فاکتور نشده.

روش ابتکاری:
1. از ساختار فاکتور F1 استفاده کن (X1، X2 کشف شده)
2. از الگوی 3 × 7 استفاده کن (در هر دو فاکتور موجود بود)
3. P-1 با B1 های مختلف
4. ECM با پارامترهای بهینه
5. Trial Division با k های بزرگ (با gmpy2 سریع)

نکته مهم: همه محاسبات محلی هستن، بدون FactorDB.
"""

import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod, isqrt
import time
import json
import os
import subprocess

# ============================================================
#  داده‌ها
# ============================================================
P = 1237
M_1237 = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M_1237 // F1  # F2 صحیح

# فاکتورهای شناخته شده از F1 - 1 = 2 × 3 × 7 × 1237 × X1 × X2
X1 = mpz("110421384041193593117465987")
X2 = mpz("442440509040507330087115446251753610709")

WORKDIR = "/home/z/my-project/A136030_M1237_innovative_v2"
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
    return {'last_step': 0, 'factors_found': []}


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(state, f, indent=2)
    os.rename(tmp, STATE_FILE)


def verify_factor(factor):
    """تأیید چند باره فاکتور"""
    f = mpz(factor)
    if f <= 1 or f >= F2:
        return False
    if F2 % f != 0:
        return False
    # بررسی مجدد
    if F2 % f != 0:
        return False
    return True


def save_found_factor(method, factor, **kwargs):
    """ذخیره فاکتور پیدا شده با تأیید"""
    if not verify_factor(factor):
        log(f"⚠️ فاکتور تأیید نشد: {factor}")
        return False
    
    f = mpz(factor)
    cofactor = F2 // f
    
    log(f"✓✓✓ FACTOR FOUND!")
    log(f"  method: {method}")
    log(f"  factor: {f}")
    log(f"  factor digits: {len(str(f))}")
    log(f"  factor prime: {is_prime(f)}")
    log(f"  cofactor: {cofactor}")
    log(f"  cofactor digits: {len(str(cofactor))}")
    log(f"  cofactor prime: {is_prime(cofactor)}")
    
    # تأیید مجدد
    if f * cofactor != F2:
        log(f"⚠️ تأیید نهایی ناموفق!")
        return False
    
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


def trial_division_large(k_start, k_end, label=""):
    """
    Trial Division: q = 2 × 1237 × k + 1
    با gmpy2 سریع
    """
    log(f"Trial Division {label}: k=[{k_start}, {k_end}]")
    t0 = time.time()
    
    primes_tested = 0
    factors_found = 0
    last_report = time.time()
    
    for k in range(k_start, k_end + 1):
        # شرط mod 8: k ≡ 0 یا 3 (mod 4)
        if (k & 3) != 0 and (k & 3) != 3:
            continue
        
        q = 2 * P * k + 1
        if q > F2:
            break
        
        # تست اول بودن سریع با gmpy2
        if not is_prime(q):
            continue
        
        primes_tested += 1
        
        # بررسی فاکتور بودن
        if F2 % q == 0:
            factors_found += 1
            log(f"✓ FACTOR at k={k}")
            if save_found_factor("Trial Division", q, k=k):
                return True
        
        # گزارش دوره‌ای
        if time.time() - last_report > 30:
            elapsed = time.time() - t0
            log(f"  progress: k={k:,}, primes tested={primes_tested:,}, speed={k/t0 if t0 > 0 else 0:,.0f} k/s")
            last_report = time.time()
    
    elapsed = time.time() - t0
    log(f"تمام شد در {elapsed:.0f}s, primes tested={primes_tested}, factors={factors_found}")
    return False


def custom_pm1(B1, extra_factors, label=""):
    """
    P-1 سفارشی با اضافه کردن extra_factors به stage 1
    """
    log(f"P-1 {label}: B1={B1}, extra_factors={len(extra_factors)}")
    t0 = time.time()
    
    # تولید اعداد اول تا B1
    if B1 > 10**8:
        log(f"B1 خیلی بزرگ برای sieve، skip")
        return False
    
    sieve = bytearray([1]) * (B1 + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(B1**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, B1 + 1, i):
                sieve[j] = 0
    primes = [i for i in range(2, B1 + 1) if sieve[i]]
    
    # اضافه کردن extra_factors
    for ef in extra_factors:
        if is_prime(ef) and ef not in primes:
            primes.append(int(ef))
    
    log(f"تعداد اعداد اول: {len(primes)}")
    
    # محاسبه a = 2^(product of prime powers) mod F2
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
    elapsed = time.time() - t0
    
    log(f"تمام شد در {elapsed:.0f}s, gcd = {g}")
    
    if g > 1 and g < F2:
        log(f"✓✓✓ FACTOR FOUND via P-1!")
        if save_found_factor("P-1 custom", g, B1=B1, extra_factors=len(extra_factors)):
            return True
    
    return False


def run_ecm(B1, curves, label=""):
    """اجرای ECM با gmp-ecm"""
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    log_file = f"{WORKDIR}/ecm_{label}_B1_{B1}.log"
    log(f"ECM {label}: B1={B1}, curves={curves}")
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
        proc.communicate(input=str(F2).encode())
    
    elapsed = time.time() - t0
    log(f"تمام شد در {elapsed:.0f}s ({elapsed/60:.1f} دقیقه)")
    
    # چک کردن فاکتور در log
    if os.path.exists(log_file):
        with open(log_file) as f:
            content = f.read()
        
        if 'Factor found' in content or 'found' in content.lower():
            import re
            matches = re.findall(r'(\d{10,})', content)
            for m in matches:
                if verify_factor(m):
                    log(f"✓✓✓ FACTOR FOUND via ECM!")
                    if save_found_factor("ECM", m, B1=B1, curves=curves):
                        return True
    
    return False


def main():
    state = load_state()
    
    log("=" * 70)
    log("روش ابتکاری واقعی برای فاکتوریزاسیون F2 صحیح")
    log("=" * 70)
    log(f"F2 = {str(F2)[:60]}... ({len(str(F2))} رقم)")
    log(f"State: {state}")
    log("")
    
    # مراحل جستجو
    phases = [
        # (name, type, params, description)
        ('trial_1e6', 'trial', {'k_start': 1, 'k_end': 10**6}, 
         'Trial Division k ≤ 10^6'),
        ('trial_1e7', 'trial', {'k_start': 10**6 + 1, 'k_end': 10**7}, 
         'Trial Division k ≤ 10^7'),
        ('trial_1e8', 'trial', {'k_start': 10**7 + 1, 'k_end': 10**8}, 
         'Trial Division k ≤ 10^8'),
        ('pm1_with_X1', 'pm1_custom', {'B1': 10**7, 'extra': [X1]}, 
         'P-1 با B1=10^7 + X1 (فرض: k شامل X1)'),
        ('pm1_with_X2', 'pm1_custom', {'B1': 10**7, 'extra': [X2]}, 
         'P-1 با B1=10^7 + X2 (فرض: k شامل X2)'),
        ('pm1_with_X1_X2', 'pm1_custom', {'B1': 10**7, 'extra': [X1, X2]}, 
         'P-1 با B1=10^7 + X1 + X2'),
        ('ecm_1e6', 'ecm', {'B1': '1e6', 'curves': 1000, 'label': 'phase1'}, 
         'ECM B1=1e6 (فاکتور 35-40 رقمی)'),
        ('ecm_1e7', 'ecm', {'B1': '1e7', 'curves': 2000, 'label': 'phase2'}, 
         'ECM B1=1e7 (فاکتور 40-45 رقمی)'),
        ('ecm_1e8', 'ecm', {'B1': '1e8', 'curves': 3000, 'label': 'phase3'}, 
         'ECM B1=1e8 (فاکتور 45-50 رقمی)'),
        ('ecm_1e9', 'ecm', {'B1': '1e9', 'curves': 5000, 'label': 'phase4'}, 
         'ECM B1=1e9 (فاکتور 50-55 رقمی)'),
    ]
    
    current_step = state.get('last_step', 0)
    
    for i, (phase_name, phase_type, params, desc) in enumerate(phases):
        if i < current_step:
            log(f"skipping phase {i}: {phase_name} (already done)")
            continue
        
        log("")
        log(f"=== مرحله {i+1}/{len(phases)}: {phase_name} - {desc} ===")
        
        t0 = time.time()
        found = False
        
        if phase_type == 'trial':
            found = trial_division_large(
                params['k_start'], params['k_end'], label=phase_name
            )
        elif phase_type == 'pm1_custom':
            found = custom_pm1(
                params['B1'], params['extra'], label=phase_name
            )
        elif phase_type == 'ecm':
            found = run_ecm(
                params['B1'], params['curves'], label=params['label']
            )
        
        elapsed = time.time() - t0
        
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
        
        if found:
            log(f"✓✓✓ فاکتور پیدا شد! توقف.")
            return
    
    log("")
    log("=== همه مراحل تموم شد ===")
    log(f"تعداد فاکتورهای پیدا شده: {len(state.get('factors_found', []))}")


if __name__ == "__main__":
    main()
