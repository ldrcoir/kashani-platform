import sys, os, json, subprocess, time
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime

TOKEN = "6ddb5c17a56f920f3ee459e99036bd57"

def factordb_get(n):
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "15",
             "-X", "POST", "https://factordb.com:4059/rpc",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({
                 "jsonrpc": "2.0", "id": 1, "method": "get_number",
                 "params": {"target": {"expr": str(n)}}
             })],
            capture_output=True, text=True, timeout=20
        )
        data = json.loads(result.stdout)
        return data.get("result", {}).get("status", "?")
    except Exception:
        return "unknown"

def factordb_get_with_detail(n):
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "15",
             "-X", "POST", "https://factordb.com:4059/rpc",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({
                 "jsonrpc": "2.0", "id": 1, "method": "get_number",
                 "params": {"target": {"expr": str(n)}, "detail": 1}
             })],
            capture_output=True, text=True, timeout=20
        )
        data = json.loads(result.stdout)
        return data.get("result", {})
    except Exception:
        return {}

# ====================================================================
# بخش ۱: آمار بازه‌های کامل
# ====================================================================
print("=" * 80)
print("📊 گزارش کامل بازه‌ها")
print("=" * 80)
print()

table_dir = "/home/z/my-project/download/complete_table"
tables = []
for f in sorted(os.listdir(table_dir)):
    if f.startswith("table_") and f.endswith(".json"):
        with open(os.path.join(table_dir, f)) as fh:
            d = json.load(fh)
            tables.append(d)
            print(f"  ✅ {d['range']}: {d['total_processed']:,} عدد، اول={d['primes']:,}, مرکب={d['composites_factored']:,}, شکست={d['unfactored_count']}")

total_primes = sum(t['primes'] for t in tables)
total_composites = sum(t['composites_factored'] for t in tables)
total_processed = sum(t['total_processed'] for t in tables)

print()
print(f"📊 جمع کل:")
print(f"  اعداد پردازش‌شده: {total_processed:,}")
print(f"  اعداد اول: {total_primes:,}")
print(f"  اعداد مرکب فاکتور شده: {total_composites:,}")
print(f"  شکست‌ها: {sum(t['unfactored_count'] for t in tables)}")
print()

# Count odd/even primes (all primes > 2 are odd)
print("📊 تفکیک زوج/فرد:")
print(f"  اعداد اول زوج: 1 (فقط عدد 2)")
print(f"  اعداد اول فرد: {total_primes - 1}")
print(f"  اعداد مرکب زوج: ~{total_composites // 2:,} (تقریبی)")
print(f"  اعداد مرکب فرد: ~{total_composites // 2:,} (تقریبی)")
print()

# ====================================================================
# بخش ۲: آمار اعداد π
# ====================================================================
print("=" * 80)
print("📊 گزارش اعداد π (سری Kashani-Pi)")
print("=" * 80)
print()

# Load all pi databases
pi_dir = "/home/z/my-project/download/kashani_pi"
pi_all = []

# Load pi_numbers.json (دسته ۱ و ۲)
pi_file = os.path.join(pi_dir, "pi_numbers.json")
if os.path.exists(pi_file):
    with open(pi_file) as f:
        d = json.load(f)
        for n in d.get('numbers', []):
            pi_all.append({
                'n': n['n'],
                'digits': n['digits'],
                'pi_pos': n['pi_position'],
                'factors': n.get('factors', []),
                'status': 'FF' if n.get('factors') else '?',
                'batch': 'دسته ۱/۲',
            })

# Load pi_large_numbers.json
pi_large_file = os.path.join(pi_dir, "pi_large_numbers.json")
if os.path.exists(pi_large_file):
    with open(pi_large_file) as f:
        d = json.load(f)
        for n in d.get('numbers', []):
            pi_all.append({
                'n': n['n'],
                'digits': n['digits'],
                'pi_pos': n['pi_position'],
                'factors': n.get('factors', []),
                'status': n.get('factordb_status_after', n.get('factordb_status_before', '?')),
                'batch': 'دسته ۲ بزرگ',
            })

# Load kashani_pi_bg.json
pi_bg_file = os.path.join(pi_dir, "kashani_pi_bg.json")
if os.path.exists(pi_bg_file):
    with open(pi_bg_file) as f:
        d = json.load(f)
        for n in d.get('numbers', []):
            pi_all.append({
                'n': n['n'],
                'digits': n['size'],
                'pi_pos': n['pi_pos'],
                'factors': n.get('factors', []),
                'status': 'FF' if n.get('factors') else n.get('status', '?'),
                'batch': 'دسته ۳ (pos 5000)',
            })

print(f"تعداد کل اعداد π ساخته‌شده: {len(pi_all)}")
print()

# Show all
print(f"{'#':<3} {'دسته':<15} {'رقم':<6} {'π pos':<8} {'وضعیت':<8} {'تعداد فاکتور':<12} {'زوج/فرد'}")
print(f"{'-'*3} {'-'*15} {'-'*6} {'-'*8} {'-'*8} {'-'*12} {'-'*8}")

odd_count = 0
even_count = 0
primes_count = 0
composites_count = 0
factored_by_us = 0

for i, p in enumerate(pi_all, 1):
    n = p['n']
    is_odd = n % 2 == 1
    if is_odd:
        odd_count += 1
    else:
        even_count += 1
    
    if p['factors']:
        if len(p['factors']) == 1 and p['factors'][0] == n:
            status = 'P'
            primes_count += 1
        else:
            status = 'FF'
            composites_count += 1
            factored_by_us += 1
        factor_count = len(p['factors'])
    else:
        status = '?'
        factor_count = 0
    
    zog_fard = 'فرد' if is_odd else 'زوج'
    print(f"{i:<3} {p['batch'][:13]:<15} {p['digits']:<6} {p['pi_pos']:<8} {status:<8} {factor_count:<12} {zog_fard}")

print()
print(f"📊 آمار:")
print(f"  کل اعداد π: {len(pi_all)}")
print(f"  زوج: {even_count}")
print(f"  فرد: {odd_count}")
print(f"  اول: {primes_count}")
print(f"  مرکب فاکتور شده: {composites_count}")
print(f"  فاکتور نشده: {len(pi_all) - primes_count - composites_count}")
print(f"  خودمون فاکتور کردیم: {factored_by_us}")
print()

# Check FactorDB status
print("=" * 80)
print("📊 وضعیت ثبت در FactorDB")
print("=" * 80)
print()

# Check a sample
print("بررسی وضعیت اعداد π در FactorDB...")
sample_to_check = pi_all[:5] if len(pi_all) >= 5 else pi_all

ff_in_factordb = 0
c_in_factordb = 0
unknown_count = 0

for p in sample_to_check:
    status = factordb_get(p['n'])
    print(f"  {p['digits']}d (pos {p['pi_pos']}): {status}")
    if status == 'FF':
        ff_in_factordb += 1
    elif status == 'C':
        c_in_factordb += 1
    else:
        unknown_count += 1
    time.sleep(0.5)

print()
print(f"📊 در FactorDB:")
print(f"  FF (فکتور شده): {ff_in_factordb}")
print(f"  C (فکتور نشده): {c_in_factordb}")
print(f"  ناشناخته: {unknown_count}")
print()

# Check contributions
print("=" * 80)
print("📊 contributions شما در FactorDB")
print("=" * 80)
print()

try:
    result = subprocess.run(
        ["curl", "-s", "--max-time", "20",
         "-X", "POST", "https://factordb.com:4059/rpc",
         "-H", "Content-Type: application/json",
         "-H", f"X-Fdb-User-Token: {TOKEN}",
         "-d", json.dumps({
             "jsonrpc": "2.0", "id": 1, "method": "contributions",
             "params": {"limit": 20}
         })],
        capture_output=True, text=True, timeout=25
    )
    d = json.loads(result.stdout)
    r = d.get('result', {})
    total = r.get('total', 0)
    largest = r.get('largest_digits', 0)
    print(f"  تعداد contributions: {total}")
    print(f"  بزرگ‌ترین فاکتور: {largest} رقم")
    print()
    if r.get('rows'):
        print(f"  لیست contributions:")
        for i, row in enumerate(r.get('rows', [])[:10], 1):
            print(f"    {i}. {row['digits']}d (parent {row['parent_digits']}d): {row['preview']}")
except Exception as e:
    print(f"  خطا: {e}")
