#!/usr/bin/env python3
"""
ایده‌ی جدید: حذف k های بد با ساختار مقاوم‌تر

با توجه به اینکه:
- smart sieve تا k=100B رسیده و هیچ فاکتور پیدا نشده
- یعنی فاکتور (اگر وجود داشته باشد) باید با k > 100B باشد
- یعنی q > 2474 × 100B = 2.474 × 10^14

برای سرعت بیشتر، می‌توانیم از تکنیک‌های زیر استفاده کنیم:

۱. حذف k هایی که k mod (1237) = 0 (چون p = 2474k + 1، اگر k mod 1237 = 0، آن‌گاه p mod 1237 = 1، که OK است)
   - ولی: اگر k mod (1237 * 2474) = 0، یعنی p mod (1237 * 2474) = 1، که عادی است
   - این حذف نمی‌کند

۲. حذف k هایی که p = 2474k + 1 مرکب است — این کار قبلاً با sieve انجام شده

۳. روش جدید: استفاده از قانون چینی برای ساختن یک جدول بزرگ‌تر از good residues
   - با LCM(3, 5, 7, 11, 13, 17, 19, 23, 29, 31) = 200560490130
   - می‌توانیم good residues را برای این mod بزرگ محاسبه کنیم
   - این حذف بیشتری انجام می‌دهد (ولی memory بیشتری نیاز دارد)

۴. روش «پرش هوشمند»: به‌جای iterate کردن همه‌ی k ها، از ساختار p = 2474k + 1 استفاده کنیم
   - p = 2474k + 1، ما p را می‌خواهیم اول باشد
   - با next_prime از یک p شروع کنیم و به prime بعدی بپریم
   - این پرش از primality test اجتناب می‌کند

ایده‌ی ۴ بهترین است! بذار آن را پیاده کنم.
"""

import sys
sys.set_int_max_str_digits(1000000)
import gmpy2
from gmpy2 import mpz, is_prime, powmod, next_prime
import time
import json
import multiprocessing as mp
from pathlib import Path

P = 1237
TWO_P = 2474
M = mpz(2)**P - 1
P70 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
C303 = M // P70

BASE_DIR = Path('/home/z/my-project/download')
CHECKPOINT_FILE = BASE_DIR / 'c303_nextprime_checkpoint.json'
RESULTS_FILE = BASE_DIR / 'c303_nextprime_results.txt'

def worker_main(args):
    worker_id, q_start, q_end = args
    worker_progress_file = BASE_DIR / f'c303_np_w{worker_id}_progress.json'
    
    print(f"[W{worker_id}] START q=[{q_start:,}, {q_end:,})", flush=True)
    
    # Find first prime >= q_start
    q = int(gmpy2.next_prime(q_start - 1))
    local_tested = 0
    local_primes = 0
    local_pow_hits = 0
    last_save = time.time()
    last_log = time.time()
    t_start = time.time()
    
    while q < q_end:
        if RESULTS_FILE.exists():
            try:
                if 'FACTOR FOUND' in RESULTS_FILE.read_text():
                    return
            except:
                pass
        
        local_primes += 1
        
        # Check q ≡ 1 (mod 2474)
        if (q - 1) % TWO_P == 0:
            local_tested += 1
            k = (q - 1) // TWO_P
            
            # Check pow(2, 1237, q) == 1 (factor of M)
            if powmod(2, P, q) == 1:
                local_pow_hits += 1
                if C303 % q == 0:
                    # FACTOR FOUND!
                    cofactor = int(C303) // q
                    with open(RESULTS_FILE, 'a') as f:
                        f.write(f"=== FACTOR FOUND ===\n")
                        f.write(f"Worker: {worker_id}\n")
                        f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"k = {k}\n")
                        f.write(f"q = {q}\n")
                        f.write(f"q digits: {len(str(q))}\n")
                        f.write(f"cofactor digits: {len(str(cofactor))}\n")
                        f.write(f"is_prime(cofactor): {is_prime(cofactor)}\n")
                        f.write(f"===\n")
                    print(f"\n!!! FACTOR FOUND by W{worker_id} !!! k={k}, q={q}", flush=True)
                    return
        
        # Progress
        if local_primes % 100_000 == 0:
            now = time.time()
            if now - last_save > 30:
                with open(worker_progress_file, 'w') as f:
                    json.dump({
                        'worker_id': worker_id,
                        'last_q': q,
                        'last_k': (q - 1) // TWO_P if (q - 1) % TWO_P == 0 else None,
                        'primes': local_primes,
                        'tested': local_tested,
                        'pow_hits': local_pow_hits,
                        'elapsed': now - t_start,
                    }, f, indent=2)
                last_save = now
            if now - last_log > 15:
                elapsed = now - t_start
                rate = local_primes / elapsed if elapsed > 0 else 0
                print(f"[W{worker_id}] q={q:,}, primes={local_primes:,}, tested={local_tested:,}, pow_hits={local_pow_hits}, rate={rate:.0f} primes/s, elapsed={elapsed:.0f}s", flush=True)
                last_log = now
        
        # Jump to next prime
        q = int(gmpy2.next_prime(q))
    
    with open(worker_progress_file, 'w') as f:
        json.dump({
            'worker_id': worker_id,
            'last_q': q,
            'primes': local_primes,
            'tested': local_tested,
            'pow_hits': local_pow_hits,
            'elapsed': time.time() - t_start,
            'done': True,
        }, f, indent=2)
    print(f"[W{worker_id}] DONE at q={q:,}, primes={local_primes:,}", flush=True)

def main():
    print("=" * 70)
    print("  C303 Sieve v5 — using next_prime (much faster)")
    print("=" * 70)
    
    NUM_WORKERS = 2
    
    # Range: from k=100B to k=1T (q = 2474*100B = 2.474e14 to 2474*1T = 2.474e15)
    K_START = 100_000_000_000
    K_END = 1_000_000_000_000
    Q_START = TWO_P * K_START + 1
    Q_END = TWO_P * K_END + 1
    
    # Check checkpoint
    start_q = Q_START
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE) as f:
                cp = json.load(f)
            saved_q = cp.get('last_q_processed', 0)
            if saved_q > start_q:
                start_q = saved_q + 1
                print(f"Resume from q={start_q:,}")
        except:
            pass
    
    print(f"Range: q = [{start_q:,}, {Q_END:,})")
    print(f"Workers: {NUM_WORKERS}")
    print(f"Expected rate: ~224,000 primes/s per worker")
    
    # Clear old worker progress files
    for i in range(NUM_WORKERS):
        wp_file = BASE_DIR / f'c303_np_w{i}_progress.json'
        if wp_file.exists():
            wp_file.unlink()
    
    total_q = Q_END - start_q
    chunk_size = total_q // NUM_WORKERS
    
    ctx = mp.get_context('fork')
    workers = []
    for i in range(NUM_WORKERS):
        w_start = start_q + i * chunk_size
        w_end = Q_END if i == NUM_WORKERS - 1 else w_start + chunk_size
        p = ctx.Process(target=worker_main, args=((i, w_start, w_end),))
        p.start()
        workers.append(p)
        print(f"  W{i}: q=[{w_start:,}, {w_end:,}) PID {p.pid}")
    
    print()
    print("Workers started. Monitoring...")
    print("=" * 70)
    
    t_start = time.time()
    last_checkpoint = time.time()
    
    while any(p.is_alive() for p in workers):
        time.sleep(15)
        
        if RESULTS_FILE.exists() and 'FACTOR FOUND' in RESULTS_FILE.read_text():
            print("\n!!! FACTOR FOUND !!! Stopping...", flush=True)
            for p in workers:
                if p.is_alive():
                    p.terminate()
            break
        
        total_q_processed = 0
        total_tested = 0
        total_primes = 0
        for i in range(NUM_WORKERS):
            wp_file = BASE_DIR / f'c303_np_w{i}_progress.json'
            if wp_file.exists():
                try:
                    with open(wp_file) as f:
                        wp = json.load(f)
                    total_q_processed = max(total_q_processed, wp.get('last_q', 0))
                    total_tested += wp.get('tested', 0)
                    total_primes += wp.get('primes', 0)
                except:
                    pass
        
        elapsed = time.time() - t_start
        # Compute rate in terms of k processed
        # q = 2474*k + 1, so k = (q-1)/2474
        # But we scan primes, not k. Density of primes per q is ~1/ln(q).
        # So rate of k progress = primes_per_sec / (density_primes_per_k) = primes_per_sec / (2474/ln(q))
        # = primes_per_sec * ln(q) / 2474
        ln_q = 33  # approx for q in [10^14, 10^15]
        k_rate = total_primes * ln_q / TWO_P / elapsed if elapsed > 0 else 0
        eta_h = (K_END - (total_q_processed - 1) // TWO_P) / k_rate / 3600 if k_rate > 0 else float('inf')
        
        print(f"[{time.strftime('%H:%M:%S')}] elapsed={elapsed:.0f}s, max_q={total_q_processed:,}, tested={total_tested:,}, primes={total_primes:,}, k_rate={k_rate:.0f} k/s, ETA={eta_h:.1f}h", flush=True)
        
        if time.time() - last_checkpoint > 60:
            with open(CHECKPOINT_FILE, 'w') as f:
                json.dump({
                    'last_q_processed': total_q_processed,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_tested': total_tested,
                    'total_primes': total_primes,
                    'elapsed': elapsed,
                }, f, indent=2)
            last_checkpoint = time.time()
    
    for p in workers:
        if p.is_alive():
            p.join(timeout=5)
    
    print()
    print("=" * 70)
    print("Done")
    print("=" * 70)
    
    if RESULTS_FILE.exists() and 'FACTOR FOUND' in RESULTS_FILE.read_text():
        print("!!! FACTOR FOUND !!!")
        print(RESULTS_FILE.read_text())
    else:
        print("No factor found")

if __name__ == '__main__':
    main()
