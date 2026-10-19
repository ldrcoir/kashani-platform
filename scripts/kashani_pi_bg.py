"""سری Kashani پی — اجرای پس‌زمینه"""
import sys, os, time, json, random, subprocess
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime

OUTPUT_DIR = "/home/z/my-project/download/kashani_pi"
LOG = os.path.join(OUTPUT_DIR, "kashani_pi_bg.log")
PI_FILE = os.path.join(OUTPUT_DIR, "pi_100k_digits.txt")

ECM_PATH = "/home/z/my-project/ecm-extract/usr/bin/ecm"
LD_PATH = "/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + "\n")

def factor_with_rho(n, max_iter=200000):
    if n == 1: return []
    if n % 2 == 0:
        return [2] + factor_with_rho(n // 2, max_iter)
    if is_prime(n): return [int(n)]
    factors = []
    remaining = n
    p = 2
    while p * p <= remaining and p < 100000:
        while remaining % p == 0:
            factors.append(p)
            remaining //= p
        p += 1 if p == 2 else 2
    if remaining == 1: return sorted(factors)
    if is_prime(remaining):
        factors.append(int(remaining))
        return sorted(factors)
    while remaining > 1 and not is_prime(remaining):
        x = mpz(2); y = mpz(2); d = mpz(1)
        f = lambda x: (x*x + 1) % remaining
        for _ in range(max_iter):
            x = f(x); y = f(f(y))
            d = gmpy2.gcd(abs(x - y), remaining)
            if d != 1: break
        if d == remaining or d == 1:
            return sorted(factors) + [None]
        factors.append(int(d))
        remaining //= d
        while remaining % d == 0:
            factors.append(int(d))
            remaining //= d
    if remaining > 1:
        factors.append(int(remaining))
    return sorted(factors)

def run_ecm(n, B1=10000000, max_curves=40, timeout_per_curve=30):
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = LD_PATH + ":" + env.get("LD_LIBRARY_PATH", "")
    for i in range(max_curves):
        sigma = random.randint(1, 2**31)
        try:
            result = subprocess.run(
                [ECM_PATH, "-sigma", str(sigma), str(B1)],
                input=str(n), capture_output=True, text=True,
                timeout=timeout_per_curve, env=env
            )
            output = result.stdout + result.stderr
            if "Factor found" in output:
                for line in output.split('\n'):
                    if "Factor found" in line:
                        parts = line.strip().split()
                        if parts:
                            try:
                                factor = int(parts[-1])
                                if 1 < factor < n:
                                    return factor, sigma, i + 1
                            except ValueError:
                                pass
        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue
    return None, None, max_curves

def factor_full(n, max_total_time=300):
    factors = factor_with_rho(n)
    if None not in factors:
        return factors, 'rho', 0
    t0 = time.time()
    f, sigma, c = run_ecm(n, B1=10000000, max_curves=40, timeout_per_curve=30)
    if f:
        cof = n // f
        if is_prime(mpz(cof)):
            return sorted([f, int(cof)]), f'ECM B1=1e7', time.time() - t0
        sub, _, _ = factor_full(cof, max_total_time - (time.time() - t0))
        if None not in sub:
            return sorted([f] + sub), f'ECM B1=1e7', time.time() - t0
    return [None], 'failed', time.time() - t0

def main():
    log("=" * 70)
    log("🕌 سری Kashani پی (پس‌زمینه v2)")
    log("=" * 70)
    
    if not os.path.exists(PI_FILE):
        log("فایل π وجود ندارد")
        return
    
    with open(PI_FILE) as f:
        pi_decimal = f.read()
    log(f"بارگذاری {len(pi_decimal)} رقم اعشار π")
    
    # اعداد جدید از موقعیت‌های متفاوت
    sizes = [30, 40, 50, 60, 70, 80, 90, 100]
    pi_numbers = []
    pos = 5000
    for size in sizes:
        chunk = pi_decimal[pos:pos+size]
        while chunk.startswith('0'):
            pos += 1
            chunk = pi_decimal[pos:pos+size]
        n = int(chunk)
        pi_numbers.append({'n': n, 'size': size, 'pi_pos': pos})
        log(f"تولید {size}-digit at pos {pos}: {str(n)[:40]}...")
        pos += size
    
    for item in pi_numbers:
        n = item['n']
        size = item['size']
        log(f"\nفاکتور کردن {size}-digit: {str(n)[:40]}...")
        
        if is_prime(mpz(n)):
            log(f"  ✅ اول")
            item['status'] = 'P'
            item['factors'] = [n]
        else:
            t0 = time.time()
            factors, method, t = factor_full(n, max_total_time=300)
            if None not in factors:
                log(f"  ✅ فاکتور شد: {' × '.join(map(str, factors))}")
                item['status'] = 'C'
                item['factors'] = factors
            else:
                log(f"  ❌ فاکتور نشد")
                item['status'] = '?'
        
        with open(os.path.join(OUTPUT_DIR, "kashani_pi_bg.json"), 'w') as f:
            json.dump({'numbers': pi_numbers}, f, indent=2, ensure_ascii=False, default=str)
    
    log("\nتمام!")

if __name__ == '__main__':
    main()
