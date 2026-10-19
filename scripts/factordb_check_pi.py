import sys, os, json, subprocess, time
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime

def factordb_get_detail(n):
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "15",
             "-X", "POST", "https://factordb.com:4059/rpc",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({
                 "jsonrpc": "2.0", "id": 1, "method": "get_number",
                 "params": {"target": {"expr": str(n)}, "detail": 2}
             })],
            capture_output=True, text=True, timeout=20
        )
        data = json.loads(result.stdout)
        return data.get("result", {})
    except Exception:
        return {}

# Load all pi numbers
pi_dir = "/home/z/my-project/download/kashani_pi"
pi_all = []

for fname in ['pi_numbers.json', 'pi_large_numbers.json', 'kashani_pi_bg.json']:
    path = os.path.join(pi_dir, fname)
    if os.path.exists(path):
        with open(path) as f:
            d = json.load(f)
            for n in d.get('numbers', []):
                if 'n' in n:
                    pi_all.append({
                        'n': n['n'],
                        'digits': n.get('digits', n.get('size', 0)),
                        'pi_pos': n.get('pi_position', n.get('pi_pos', 0)),
                        'local_factors': n.get('factors', []),
                        'file': fname,
                    })

print("=" * 80)
print("📊 بررسی وضعیت تمام اعداد π در FactorDB")
print("=" * 80)
print()
print(f"تعداد کل: {len(pi_all)}")
print()

print(f"{'#':<3} {'رقم':<6} {'π pos':<8} {'FactorDB':<10} {'تاریخ ایجاد':<12} {'توسط ما؟':<10} {'فاکتورها'}")
print(f"{'-'*3} {'-'*6} {'-'*8} {'-'*10} {'-'*12} {'-'*10} {'-'*40}")

was_in_factordb_before = 0
we_factored = 0
already_factored = 0
we_proved_prime = 0

for i, p in enumerate(pi_all, 1):
    n = p['n']
    detail = factordb_get_detail(n)
    status = detail.get('status', '?')
    created = detail.get('created', '?')
    
    # Check if we factored it (created date = 2026-10-17 or 18)
    our_contribution = '❌ نه' if '2026' not in str(created) else '✅ بله'
    
    if '2026' in str(created):
        if status == 'FF':
            we_factored += 1
        elif status == 'P':
            we_proved_prime += 1
    else:
        already_factored += 1
    
    # Get factor count from FactorDB
    factor_info = detail.get('factors', {}).get('factors', [])
    factor_str = ' × '.join(f.get('base', '?')[:15] for f in factor_info[:3])
    if len(factor_info) > 3:
        factor_str += f' × ... ({len(factor_info)} فاکتور)'
    
    print(f"{i:<3} {p['digits']:<6} {p['pi_pos']:<8} {status:<10} {str(created)[:10]:<12} {our_contribution:<10} {factor_str[:38]}")
    
    time.sleep(0.3)

print()
print("=" * 80)
print("📊 آمار نهایی FactorDB")
print("=" * 80)
print()
print(f"  از قبل در FactorDB بودن (تا 2025): {already_factored}")
print(f"  ما در 2026 فاکتور کردیم: {we_factored}")
print(f"  ما اثبات اول کردیم: {we_proved_prime}")
print(f"  کل: {already_factored + we_factored + we_proved_prime}")
print()
