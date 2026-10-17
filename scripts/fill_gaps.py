#!/usr/bin/env python3
"""
پُر کردن gap ها با ECM
- می‌گیره لیست اعداد تجزیه‌نشده
- روی هر کدوم با GMP-ECM در B1=1e7 یا 1e8 حمله می‌کنه
- خروجی: لیست gapهای پُر شده با عوامل

استفاده:
  python3 fill_gaps.py --input gaps.txt --output gaps_filled.txt
"""
import sys
import os
import subprocess
import argparse
import time

ECM_PATH = "/home/z/my-project/ecm-extract/usr/bin/ecm"
LD_PATH = "/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"


def run_ecm(n, B1=10000000, max_curves=50, timeout_per_curve=30):
    """اجرای ECM روی عدد n با چند sigma"""
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = LD_PATH + ":" + env.get("LD_LIBRARY_PATH", "")
    
    for i in range(max_curves):
        sigma = (i + 1) * 7919  # pseudo-random sigma
        try:
            result = subprocess.run(
                [ECM_PATH, "-sigma", str(sigma), str(B1)],
                input=str(n),
                capture_output=True,
                text=True,
                timeout=timeout_per_curve,
                env=env
            )
            output = result.stdout + result.stderr
            if "Factor found" in output:
                # استخراج فاکتور
                for line in output.split('\n'):
                    if "Factor found" in line:
                        # آخرین عدد در خط
                        parts = line.strip().split()
                        factor = parts[-1]
                        return int(factor), output
        except subprocess.TimeoutExpired:
            continue
        except Exception as e:
            print(f"  Error curve {i+1}: {e}")
            continue
    
    return None, None


def fill_gap(n, B1=10000000, max_curves=50, verbose=True):
    """پُر کردن یه gap"""
    if verbose:
        print(f"  Trying ECM on n={n} (digits={len(str(n))})...")
    
    factor, output = run_ecm(n, B1=B1, max_curves=max_curves)
    
    if factor and factor != n and factor != 1:
        cofactor = n // factor
        return {
            'n': n,
            'factor1': factor,
            'cofactor': cofactor,
            'fully_factored': is_prime_simple(cofactor),
            'output': output
        }
    
    return {'n': n, 'factor': None, 'output': output}


def is_prime_simple(n):
    """بررسی اول بودن با gmpy2"""
    try:
        import gmpy2
        return bool(gmpy2.is_prime(n))
    except:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='فایل شامل لیست اعداد (هر خط یه عدد)')
    parser.add_argument('--output', required=True, help='فایل خروجی')
    parser.add_argument('--B1', type=int, default=10000000)
    parser.add_argument('--max-curves', type=int, default=50)
    parser.add_argument('--timeout', type=int, default=30, help='timeout per curve (seconds)')
    args = parser.parse_args()
    
    # خواندن لیست اعداد
    with open(args.input, 'r') as f:
        # فیلتر خطوط کامنت
        numbers = []
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    numbers.append(int(line))
                except:
                    pass
    
    print(f"پُر کردن {len(numbers)} gap با ECM (B1={args.B1}, max_curves={args.max_curves})")
    
    results = []
    filled = 0
    
    for i, n in enumerate(numbers):
        print(f"\n[{i+1}/{len(numbers)}] n={n}")
        result = fill_gap(n, B1=args.B1, max_curves=args.max_curves, verbose=True)
        
        if result.get('factor1'):
            filled += 1
            print(f"  ✓ FACTOR: {result['factor1']}")
            print(f"    cofactor: {result['cofactor']} (prime: {result['fully_factored']})")
            results.append({
                'n': n,
                'status': 'filled',
                **result
            })
        else:
            print(f"  ✗ failed (B1={args.B1}, {args.max_curves} curves)")
            results.append({
                'n': n,
                'status': 'still_gap',
            })
    
    # نوشتن خروجی
    with open(args.output, 'w') as f:
        f.write(f"# خلاصه پُر کردن gap\n")
        f.write(f"# B1={args.B1}, max_curves={args.max_curves}\n")
        f.write(f"# پُر شده: {filled}/{len(numbers)}\n\n")
        for r in results:
            if r['status'] == 'filled':
                f.write(f"{r['n']} = {r['factor1']} × {r['cofactor']}\n")
            else:
                f.write(f"{r['n']} = ? (still gap)\n")
    
    print(f"\n=== خلاصه ===")
    print(f"  پُر شده: {filled}/{len(numbers)}")
    print(f"  خروجی: {args.output}")


if __name__ == '__main__':
    main()
