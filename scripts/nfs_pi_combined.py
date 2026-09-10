#!/usr/bin/env python3
"""
جستجوی فاکتور F2 با:
1. msieve (NFS/QS) در پس‌زمینه
2. جستجوی هوشمند در ۱ میلیون رقم π
3. روش‌های ابتکاری جدید
"""

import gmpy2
from gmpy2 import mpz, is_prime, gcd
import numpy as np
import time
import json
import os
import subprocess
import multiprocessing as mp

P = 1237
M_1237 = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M_1237 // F1
F2_STR = str(F2)

PI_FILE = "/home/z/my-project/download/pi_1million_digits.txt"
MSIEVE = "/tmp/msieve-master/msieve"
LD_PATH = "/tmp/gmp-dev/usr/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu"

WORKDIR = "/home/z/my-project/A136030_nfs_pi_search"
os.makedirs(WORKDIR, exist_ok=True)

LOG_FILE = f"{WORKDIR}/search.log"
FOUND_FILE = f"{WORKDIR}/FOUND_factors.txt"


def log(msg):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")


def verify_and_save(factor, method, **kwargs):
    f = mpz(factor)
    if f <= 1 or f >= F2:
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
    
    with open(FOUND_FILE, 'w') as out:
        out.write(f"=== FACTOR OF F2 FOUND ===\n")
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


# ============================================================
#  روش ۱: msieve (NFS/QS)
# ============================================================
def run_msieve(timeout=3600):
    """اجرای msieve روی F2"""
    log("=" * 70)
    log("  روش ۱: msieve (NFS/QS) روی F2")
    log("=" * 70)
    
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{LD_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    log_file = f"{WORKDIR}/msieve_f2.log"
    log(f"اجرای msieve روی F2 ({len(F2_STR)} رقم)...")
    log(f"timeout: {timeout}s")
    
    t0 = time.time()
    try:
        with open(log_file, 'w') as out:
            proc = subprocess.Popen(
                [MSIEVE, '-v', '-e', F2_STR],
                stdout=out,
                stderr=subprocess.STDOUT,
                env=env
            )
            proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.terminate()
        log(f"msieve timeout بعد از {timeout}s")
    except Exception as e:
        log(f"خطا: {e}")
    
    elapsed = time.time() - t0
    log(f"msieve تموم شد در {elapsed:.0f}s ({elapsed/3600:.2f} ساعت)")
    
    # بررسی فاکتور
    if os.path.exists(log_file):
        with open(log_file) as f:
            content = f.read()
        
        if 'factor:' in content:
            import re
            for line in content.split('\n'):
                if 'factor:' in line:
                    parts = line.split('factor:')
                    if len(parts) > 1:
                        factor_str = parts[1].strip()
                        if factor_str.isdigit():
                            factor = mpz(factor_str)
                            if factor > 1 and factor < F2 and F2 % factor == 0:
                                verify_and_save(factor, 'msieve')
                                return factor
    
    return None


# ============================================================
#  روش ۲: جستجوی هوشمند در ۱ میلیون رقم π
# ============================================================
def search_pi_worker(pi_digits, start, end, length, result_queue):
    """Worker برای جستجوی موازی در π"""
    F2_mpz = F2
    
    for s in range(start, end):
        if s + length > len(pi_digits):
            break
        
        candidate_str = pi_digits[s:s+length].lstrip('0')
        if len(candidate_str) < 2:
            continue
        
        candidate = mpz(candidate_str)
        
        if candidate > 1 and candidate < F2_mpz:
            # بررسی سریع: F2 mod candidate
            if F2_mpz % candidate == 0:
                result_queue.put(('factor', str(candidate), s, length))
                return
    
    result_queue.put(('done', None, start, length))


def parallel_pi_search(pi_digits, lengths, num_workers=4):
    """جستجوی موازی در π"""
    log("\n=== روش ۲: جستجوی موازی در ۱ میلیون رقم π ===")
    
    total_len = len(pi_digits)
    log(f"تعداد ارقام π: {total_len:,}")
    
    for length in lengths:
        log(f"\nجستجوی اعداد {length} رقمی در π...")
        t0 = time.time()
        
        chunk_size = (total_len - length + 1) // num_workers
        processes = []
        result_queue = mp.Queue()
        
        for i in range(num_workers):
            start = i * chunk_size
            end = min((i + 1) * chunk_size + length, total_len)
            
            p = mp.Process(
                target=search_pi_worker,
                args=(pi_digits, start, end, length, result_queue)
            )
            p.start()
            processes.append(p)
        
        factor_found = None
        
        for _ in range(num_workers):
            try:
                msg_type, data, start_pos, length_val = result_queue.get(timeout=3600)
                if msg_type == 'factor':
                    factor_found = data
                    log(f"✓✓✓ FACTOR FOUND در موقعیت {start_pos}!")
                    break
            except:
                pass
        
        for p in processes:
            p.terminate()
            p.join(timeout=5)
        
        elapsed = time.time() - t0
        log(f"  زمان: {elapsed:.1f}s")
        
        if factor_found:
            if verify_and_save(factor_found, 'Pi-search-1M', 
                               position=start_pos, length=length):
                return factor_found
    
    return None


# ============================================================
#  روش ۳: الگوی Mersenne در π (بهبود یافته)
# ============================================================
def mersenne_pi_search(pi_digits):
    """جستجوی اعداد به فرم Mersenne در π"""
    log("\n=== روش ۳: الگوی Mersenne در π ===")
    
    two_p = 2 * P  # 2474
    total_len = len(pi_digits)
    
    for length in range(5, 80, 5):
        log(f"  طول {length}...")
        
        count = 0
        for start in range(min(50000, total_len - length + 1)):
            candidate_str = pi_digits[start:start+length].lstrip('0')
            if len(candidate_str) < 2:
                continue
            
            candidate = mpz(candidate_str)
            
            # شرط Mersenne: q ≡ 1 (mod 2474)
            if (candidate - 1) % two_p != 0:
                continue
            
            count += 1
            
            # شرط mod 8
            mod8 = int(candidate % 8)
            if mod8 != 1 and mod8 != 7:
                continue
            
            # بررسی فاکتور F2
            if candidate > 1 and candidate < F2:
                if F2 % candidate == 0:
                    log(f"    ✓✓✓ FACTOR FOUND!")
                    if verify_and_save(candidate, 'Pi-Mersenne',
                                       position=start, length=length):
                        return candidate
        
        log(f"    کاندید‌های mod 2474: {count}")
    
    return None


# ============================================================
#  روش ۴: تحلیل طیفی π برای فاکتور F2
# ============================================================
def spectral_pi_factor(pi_digits):
    """تحلیل طیفی ارقام π برای فاکتور F2"""
    log("\n=== روش ۴: تحلیل طیفی π ===")
    
    # FFT ارقام π
    N = min(100000, len(pi_digits))
    pi_signal = np.array([int(d) for d in pi_digits[:N]], dtype=np.float64)
    pi_signal = pi_signal - np.mean(pi_signal)
    
    fft_result = np.fft.fft(pi_signal)
    magnitude = np.abs(fft_result)
    freqs = np.fft.fftfreq(N, d=1.0)
    
    # فرکانس‌های غالب
    mag_for_peaks = magnitude[:N//2].copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-500:][::-1]
    
    log(f"  بررسی ۵۰۰ فرکانس غالب...")
    
    for idx in peak_indices:
        freq = freqs[idx]
        if freq == 0:
            continue
        period = 1.0 / freq
        period_int = int(round(period))
        
        # بررسی period و ضرایب
        for mult in range(1, 5000):
            candidate = period_int * mult
            if candidate > 1 and candidate < F2:
                g = gcd(F2, candidate)
                if g > 1 and g < F2:
                    log(f"  ✓✓✓ FACTOR FOUND!")
                    if verify_and_save(g, 'Pi-spectral',
                                       freq=freq, period=period_int, mult=mult):
                        return g
    
    log(f"  فاکتوری پیدا نشد")
    return None


# ============================================================
#  main
# ============================================================
def main():
    log("=" * 70)
    log("  جستجوی فاکتور F2: msieve + π + روش‌های ابتکاری")
    log("=" * 70)
    log(f"F2 = {F2_STR[:50]}... ({len(F2_STR)} رقم)")
    log("")
    
    # بارگذاری π
    with open(PI_FILE) as f:
        pi_digits = f.read().strip()
    log(f"π بارگذاری شد: {len(pi_digits):,} رقم")
    log("")
    
    # روش ۱: msieve (در پس‌زمینه با timeout)
    # msieve برای 303 رقم خیلی طول می‌کشه، ولی اجرا می‌کنیم
    log("شروع msieve در پس‌زمینه (timeout=1 ساعت)...")
    
    # اجرای msieve در process جداگانه
    msieve_proc = mp.Process(target=run_msieve, args=(3600,))
    msieve_proc.start()
    
    # همزمان: روش‌های π
    log("\nهمزمان: جستجوی π...")
    
    # روش ۲: جستجوی موازی در π
    lengths = [5, 10, 15, 20, 30, 50, 70, 100, 150]
    result = parallel_pi_search(pi_digits, lengths, num_workers=4)
    if result:
        msieve_proc.terminate()
        return
    
    # روش ۳: الگوی Mersenne
    result = mersenne_pi_search(pi_digits)
    if result:
        msieve_proc.terminate()
        return
    
    # روش ۴: تحلیل طیفی
    result = spectral_pi_factor(pi_digits)
    if result:
        msieve_proc.terminate()
        return
    
    # صبر برای msieve
    log("\nصبر برای msieve...")
    msieve_proc.join(timeout=3600)
    
    if msieve_proc.is_alive():
        msieve_proc.terminate()
    
    log("\n=== همه روش‌ها تموم شد ===")
    log("فاکتور F2 پیدا نشده")


if __name__ == "__main__":
    try:
        mp.set_start_method('fork', force=True)
    except:
        pass
    main()
