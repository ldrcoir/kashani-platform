#!/usr/bin/env python3
"""
روش‌های ابتکاری با ارقام π برای فاکتوریزاسیون F2
================================================
۱. جستجوی اعداد اول بزرگ در ۱۰۰ هزار رقم π
۲. بررسی آیا این اعداد اول فاکتور F2 هستن
۳. روش‌های ابتکاری جدید:
   - الگوی ارقام π
   - ترکیب ارقام π با ساختار Mersenne
   - جستجوی هوشمند
"""

import gmpy2
from gmpy2 import mpz, is_prime, gcd, isqrt, iroot
import numpy as np
import time
import json
import os
import multiprocessing as mp

# ============================================================
#  داده‌ها
# ============================================================
P = 1237
M_1237 = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M_1237 // F1

PI_FILE = "/home/z/my-project/download/pi_100000_digits.txt"
WORKDIR = "/home/z/my-project/A136030_pi_factorization"
os.makedirs(WORKDIR, exist_ok=True)

LOG_FILE = f"{WORKDIR}/search.log"
FOUND_FILE = f"{WORKDIR}/FOUND_factors.txt"
STATE_FILE = f"{WORKDIR}/state.json"


def log(msg):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")


def load_pi_digits():
    """بارگذاری ارقام π"""
    with open(PI_FILE) as f:
        return f.read().strip()


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(state, f, indent=2)
    os.rename(tmp, STATE_FILE)


def verify_and_save(factor, method, **kwargs):
    """تأیید فاکتور F2"""
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
#  روش ۱: جستجوی اعداد اول در π و بررسی فاکتور F2
# ============================================================
def search_primes_in_pi_for_F2(pi_digits, start, end, length, result_queue):
    """
    جستجوی اعداد اول با طول مشخص در π و بررسی فاکتور F2
    """
    found_primes = []
    F2_mpz = F2
    
    for s in range(start, end):
        if s + length > len(pi_digits):
            break
        
        candidate_str = pi_digits[s:s+length].lstrip('0')
        if len(candidate_str) < length:
            continue
        
        candidate = mpz(candidate_str)
        
        # بررسی سریع: آیا فاکتور F2 هست؟
        if candidate > 1 and candidate < F2_mpz:
            if F2_mpz % candidate == 0:
                result_queue.put(('factor', str(candidate), s, length))
                return
        
        # اگه اول باشه، ذخیره کن
        if candidate > 1 and is_prime(candidate):
            found_primes.append((s, str(candidate)))
    
    result_queue.put(('done', found_primes, start, length))


def parallel_pi_search(pi_digits, lengths, num_workers=4):
    """
    جستجوی موازی اعداد اول در π
    """
    total_len = len(pi_digits)
    
    for length in lengths:
        log(f"\nجستجوی اعداد اول {length} رقمی در π...")
        t0 = time.time()
        
        # تقسیم کار بین workers
        chunk_size = (total_len - length + 1) // num_workers
        processes = []
        result_queue = mp.Queue()
        
        for i in range(num_workers):
            start = i * chunk_size
            end = min((i + 1) * chunk_size + length, total_len)
            
            p = mp.Process(
                target=search_primes_in_pi_for_F2,
                args=(pi_digits, start, end, length, result_queue)
            )
            p.start()
            processes.append(p)
        
        # جمع‌آوری نتایج
        all_primes = []
        factor_found = None
        
        for _ in range(num_workers):
            try:
                msg_type, data, start_pos, length_val = result_queue.get(timeout=3600)
                if msg_type == 'factor':
                    factor_found = data
                    log(f"✓✓✓ FACTOR FOUND! موقعیت {start_pos}, طول {length_val}")
                    log(f"  factor = {data}")
                    break
                elif msg_type == 'done':
                    all_primes.extend(data)
            except:
                pass
        
        # wait for all
        for p in processes:
            p.terminate()
            p.join(timeout=5)
        
        elapsed = time.time() - t0
        log(f"  زمان: {elapsed:.1f}s, اعداد اول پیدا شده: {len(all_primes)}")
        
        if factor_found:
            if verify_and_save(factor_found, 'Pi-search', length=length):
                return factor_found
        
        # ذخیره اعداد اول پیدا شده
        if all_primes:
            with open(f'{WORKDIR}/primes_{length}digit.txt', 'w') as f:
                for pos, prime in all_primes[:100]:
                    f.write(f"position {pos}: {prime}\n")
    
    return None


# ============================================================
#  روش ۲: جستجوی هوشمند - الگوی Mersenne در π
# ============================================================
def mersenne_pattern_search(pi_digits):
    """
    روش ابتکاری: جستجوی اعداد به فرم Mersenne در π
    
    فاکتور F2 باید به فرم q = 2×1237×k + 1 باشه
    پس q ≡ 1 (mod 2474)
    
    ایده: ارقام π رو به اعداد تبدیل کن و بررسی کن
    آیا به فرم Mersenne هستن
    """
    log("\n=== روش ۲: جستجوی الگوی Mersenne در π ===")
    
    F2_mpz = F2
    two_p = 2 * P  # 2474
    
    # برای طول‌های مختلف
    for length in [10, 15, 20, 25, 30, 40, 50, 60, 70]:
        log(f"  طول {length}...")
        
        count = 0
        for start in range(min(10000, len(pi_digits) - length + 1)):
            candidate_str = pi_digits[start:start+length].lstrip('0')
            if len(candidate_str) < length:
                continue
            
            candidate = mpz(candidate_str)
            
            # شرط ۱: q ≡ 1 (mod 2474)
            if (candidate - 1) % two_p != 0:
                continue
            
            count += 1
            
            # شرط ۲: q ≡ ±1 (mod 8)
            mod8 = int(candidate % 8)
            if mod8 != 1 and mod8 != 7:
                continue
            
            # شرط ۳: q اول باشه
            if not is_prime(candidate):
                continue
            
            log(f"    کاندید Mersenne در موقعیت {start}: {candidate}")
            
            # شرط ۴: q فاکتور F2 باشه
            if F2_mpz % candidate == 0:
                log(f"    ✓✓✓ FACTOR FOUND!")
                if verify_and_save(candidate, 'Pi-Mersenne-pattern', 
                                   position=start, length=length):
                    return candidate
        
        log(f"    کاندید‌های mod 2474: {count}")
    
    return None


# ============================================================
#  روش ۳: جستجوی مضارب ارقام π
# ============================================================
def pi_multiple_search(pi_digits):
    """
    روش ابتکاری: استفاده از مضارب ارقام π
    
    ایده: اگه ارقام π رو در اعداد اول ضرب کنیم،
    شاید به فاکتور F2 برسیم
    """
    log("\n=== روش ۳: جستجوی مضارب ارقام π ===")
    
    F2_mpz = F2
    
    # اعداد اول کوچک برای ضرب
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 
                    53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113]
    
    for length in [5, 10, 15, 20]:
        log(f"  طول {length}...")
        
        for start in range(min(1000, len(pi_digits) - length + 1)):
            candidate_str = pi_digits[start:start+length].lstrip('0')
            if len(candidate_str) < length:
                continue
            
            base = mpz(candidate_str)
            
            for mult in small_primes:
                candidate = base * mult
                
                if candidate > 1 and candidate < F2_mpz:
                    if F2_mpz % candidate == 0:
                        log(f"  ✓✓✓ FACTOR FOUND!")
                        log(f"  base = {base} (موقعیت {start})")
                        log(f"  mult = {mult}")
                        if verify_and_save(candidate, 'Pi-multiple',
                                           base=base, mult=mult, position=start):
                            return candidate
    
    return None


# ============================================================
#  روش ۴: تحلیل طیفی ارقام π
# ============================================================
def spectral_pi_search(pi_digits):
    """
    روش ابتکاری: تحلیل طیفی ارقام π
    
    ایده: FFT ارقام π رو بگیریم و فرکانس‌های غالب رو
    به‌عنوان کاندید فاکتور بررسی کنیم
    """
    log("\n=== روش ۴: تحلیل طیفی ارقام π ===")
    
    F2_mpz = F2
    
    # FFT ارقام π
    N = 10000
    pi_signal = np.array([int(d) for d in pi_digits[:N]], dtype=np.float64)
    pi_signal = pi_signal - np.mean(pi_signal)
    
    fft_result = np.fft.fft(pi_signal)
    magnitude = np.abs(fft_result)
    freqs = np.fft.fftfreq(N, d=1.0)
    
    # فرکانس‌های غالب
    mag_for_peaks = magnitude[:N//2].copy()
    mag_for_peaks[0] = 0
    peak_indices = np.argsort(mag_for_peaks)[-100:][::-1]
    
    log(f"  ۱۰۰ فرکانس غالب بررسی می‌شن...")
    
    for idx in peak_indices:
        freq = freqs[idx]
        if freq == 0:
            continue
        period = 1.0 / freq
        period_int = int(round(period))
        
        # بررسی period به‌عنوان فاکتور
        if period_int > 1 and period_int < F2_mpz:
            g = gcd(F2_mpz, period_int)
            if g > 1 and g < F2_mpz:
                log(f"  ✓✓✓ FACTOR FOUND!")
                if verify_and_save(g, 'Pi-spectral', freq=freq, period=period_int):
                    return g
        
        # بررسی مضارب
        for mult in range(1, 1000):
            candidate = period_int * mult
            if candidate > 1 and candidate < F2_mpz:
                g = gcd(F2_mpz, candidate)
                if g > 1 and g < F2_mpz:
                    log(f"  ✓✓✓ FACTOR FOUND!")
                    if verify_and_save(g, 'Pi-spectral-mult', 
                                       freq=freq, period=period_int, mult=mult):
                        return g
    
    log(f"  فاکتوری پیدا نشد")
    return None


# ============================================================
#  main
# ============================================================
def main():
    log("=" * 70)
    log("  روش‌های ابتکاری با ارقام π برای فاکتوریزاسیون F2")
    log("=" * 70)
    
    # بارگذاری π
    pi_digits = load_pi_digits()
    log(f"ارقام π بارگذاری شد: {len(pi_digits)} رقم")
    log(f"F2 = {str(F2)[:50]}... ({len(str(F2))} رقم)")
    log("")
    
    # روش ۱: جستجوی موازی اعداد اول در π
    log("\n=== روش ۱: جستجوی موازی اعداد اول در π ===")
    lengths = [10, 15, 20, 30, 50, 70]
    result = parallel_pi_search(pi_digits, lengths, num_workers=4)
    if result:
        return
    
    # روش ۲: الگوی Mersenne
    result = mersenne_pattern_search(pi_digits)
    if result:
        return
    
    # روش ۳: مضارب
    result = pi_multiple_search(pi_digits)
    if result:
        return
    
    # روش ۴: تحلیل طیفی
    result = spectral_pi_search(pi_digits)
    if result:
        return
    
    log("\n=== همه روش‌ها تموم شد ===")
    log("فاکتور F2 در ارقام π پیدا نشده")


if __name__ == "__main__":
    try:
        mp.set_start_method('fork', force=True)
    except:
        pass
    main()
