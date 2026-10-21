#!/usr/bin/env python3
"""
تولید اعداد ۳۰۳ رقمی با روش سینوس — نسخه‌ی پیشرفته
================================================
هر عدد:
  - دقیقاً ۳ عامل اول دارد
  - هر عامل ۸۰+ رقم دارد
  - هر عامل ≡ 7 یا 11 (mod 12) → sin(30·pi°) = -0.5
  - بنابراین sin(30·n°) = -0.5 (۳ = فرد)

کاربر می‌خواهد:
  - اعداد ۳۰۳ رقمی
  - عوامل ۸۰+ رقم
  - sin(30·n°) = -0.5 (اولویت)
  - ذخیره در DB + خروجی JSON

به افتخار EhsanMoradMaryamAlasvandi — روش سینوس
"""
import sys, os, json, time, sqlite3, random
sys.set_int_max_str_digits(200000)

import gmpy2
from gmpy2 import mpz, is_prime, next_prime, powmod

OUTPUT_DIR = "/home/z/my-project/download/sinus_method"
DB_PATH = "/home/z/my-project/db/sinus_303.db"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


# ============================================================
# ۱) راه‌اندازی DB
# ============================================================
def init_db(db_path):
    """جدول SQLite برای ذخیره‌ی اعداد ۳۰۳ رقمی"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS numbers_303 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            n TEXT NOT NULL UNIQUE,        -- خود عدد ۳۰۳ رقمی
            n_digits INTEGER NOT NULL,
            p1 TEXT NOT NULL,
            p2 TEXT NOT NULL,
            p3 TEXT NOT NULL,
            p1_digits INTEGER NOT NULL,
            p2_digits INTEGER NOT NULL,
            p3_digits INTEGER NOT NULL,
            p1_mod12 INTEGER NOT NULL,
            p2_mod12 INTEGER NOT NULL,
            p3_mod12 INTEGER NOT NULL,
            sin_30n REAL NOT NULL,         -- +0.5 یا -0.5
            sin_class TEXT NOT NULL,       -- 'POS' یا 'NEG'
            n_neg_factors INTEGER NOT NULL, -- تعداد عوامل با sin = -0.5
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sin_class ON numbers_303(sin_class)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_n ON numbers_303(n)")
    conn.commit()
    return conn


# ============================================================
# ۲) تولید عدد اول با محدودیت mod 12
# ============================================================
def gen_prime_in_class(target_digits, mod12_target, max_attempts=1000):
    """
    تولید عدد اول با تعداد رقم مشخص که ≡ mod12_target (mod 12)
    mod12_target ∈ {7, 11}  → sin(30·p°) = -0.5  (NEG class)
    mod12_target ∈ {1, 5}   → sin(30·p°) = +0.5  (POS class)
    
    روش: 
      ۱. یک عدد رندوم در بازه‌ی 10^(digits-1) تا 10^digits - 1 بساز
      ۲. تطبیق کن با mod 12
      ۳. next_prime بگیر
      ۴. اگه از کلاس درست نبود، یکی دیگه امتحان کن
    """
    low = mpz(10) ** (target_digits - 1)
    high = mpz(10) ** target_digits - 1
    
    for _ in range(max_attempts):
        # عدد رندوم در بازه
        n = mpz(random.randint(int(low), int(high)))
        # تطبیق با mod 12
        n = n - (n % 12) + mod12_target
        if n < low:
            n += 12
        if n > high:
            n -= 12
        # اول بعد از n
        p = next_prime(n)
        # اگه از کلاس درست بود و در بازه بود
        if p < high and p % 12 == mod12_target and p > low:
            return p
    return None


def gen_prime_with_digits(target_digits, prefer_class='NEG', max_attempts=2000):
    """
    تولید عدد اول با تعداد رقم مشخص.
    prefer_class = 'NEG' → اولویت کلاس‌های 7 یا 11 (sin = -0.5)
    prefer_class = 'POS' → اولویت کلاس‌های 1 یا 5 (sin = +0.5)
    """
    if prefer_class == 'NEG':
        candidates = [7, 11]
    else:
        candidates = [1, 5]
    random.shuffle(candidates)
    
    for mod12 in candidates:
        p = gen_prime_in_class(target_digits, mod12, max_attempts)
        if p is not None:
            return p, mod12
    return None, None


# ============================================================
# ۳) تولید عدد ۳۰۳ رقمی با ۳ عامل
# ============================================================
def gen_303_with_3_factors(sin_class='NEG', digit_pattern=None):
    """
    تولید عدد ۳۰۳ رقمی به‌فرم p1 × p2 × p3
    هر سه عامل ۸۰+ رقم.
    sin_class = 'NEG' → هر سه عامل در کلاس 7 یا 11 (sin = -0.5) → ۳ = فرد → sin(30n°) = -0.5
    sin_class = 'POS' → هر سه عامل در کلاس 1 یا 5 (sin = +0.5) → ۳ = فرد → sin(30n°) = -0.5?
        نه — ۳ عامل با sin = +0.5 → تعداد عوامل با sin = -0.5 برابر ۰ (زوج) → sin = +0.5
        پس اگه sin_class = 'POS': ۲ عامل POS + ۱ عامل NEG → ۱ (فرد) → sin(30n°) = -0.5
        یا ۳ عامل POS → ۰ عامل NEG (زوج) → sin = +0.5 ✓
    """
    # توزیع رقم: ۳ عامل ۸۰+ رقم جمع بشن ۳۰۳
    # نمونه‌ها: (80, 80, 143), (80, 100, 123), (100, 100, 103), (90, 110, 103), ...
    if digit_pattern is None:
        # توزیع‌های مختلف
        patterns = [
            (80, 80, 143),   # ۲ عامل کوچک + ۱ بزرگ
            (80, 100, 123),
            (80, 110, 113),
            (90, 100, 113),
            (100, 100, 103), # برابر
            (85, 105, 113),
            (80, 90, 133),
            (95, 100, 108),
        ]
        digit_pattern = random.choice(patterns)
    
    if sin_class == 'NEG':
        # هر سه عامل NEG → ۳ (فرد) → sin(30n°) = -0.5
        classes_needed = ['NEG', 'NEG', 'NEG']
    elif sin_class == 'POS':
        # ۳ عامل POS → ۰ NEG (زوج) → sin(30n°) = +0.5
        classes_needed = ['POS', 'POS', 'POS']
    elif sin_class == 'MIXED_POS':
        # ۲ POS + ۱ NEG → ۱ NEG (فرد) → sin = -0.5
        classes_needed = ['POS', 'POS', 'NEG']
    else:
        # ۱ POS + ۲ NEG → ۲ NEG (زوج) → sin = +0.5
        classes_needed = ['POS', 'NEG', 'NEG']
    
    primes = []
    mods = []
    for i, (digits, cls) in enumerate(zip(digit_pattern, classes_needed)):
        p, mod = gen_prime_with_digits(digits, cls)
        if p is None:
            return None
        primes.append(p)
        mods.append(mod)
    
    # محاسبه‌ی عدد ۳۰۳ رقمی
    n = primes[0] * primes[1] * primes[2]
    n_digits = len(str(n))
    
    # اگه دقیقاً ۳۰۳ رقم نبود، رد کن
    if n_digits != 303:
        return None
    
    # شمارش عوامل NEG
    n_neg = sum(1 for m in mods if m in (7, 11))
    sin_30n = -0.5 if n_neg % 2 == 1 else +0.5
    final_class = 'NEG' if sin_30n == -0.5 else 'POS'
    
    return {
        'n': str(n),
        'n_digits': n_digits,
        'p1': str(primes[0]),
        'p2': str(primes[1]),
        'p3': str(primes[2]),
        'p1_digits': len(str(primes[0])),
        'p2_digits': len(str(primes[1])),
        'p3_digits': len(str(primes[2])),
        'p1_mod12': mods[0],
        'p2_mod12': mods[1],
        'p3_mod12': mods[2],
        'sin_30n': sin_30n,
        'sin_class': final_class,
        'n_neg_factors': n_neg,
    }


# ============================================================
# ۴) حلقه‌ی اصلی
# ============================================================
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=100, help='تعداد اعداد تولیدی')
    parser.add_argument('--sin', choices=['NEG', 'POS', 'MIXED_POS', 'MIXED_NEG'], default='NEG',
                        help='کلاس سینوس هدف (NEG = -0.5)')
    parser.add_argument('--db', type=str, default=DB_PATH)
    args = parser.parse_args()
    
    print("=" * 80)
    print("🌊 تولید اعداد ۳۰۳ رقمی با روش سینوس")
    print("=" * 80)
    print(f"   تعداد درخواستی: {args.count}")
    print(f"   کلاس سینوس هدف: {args.sin}")
    print(f"   هر عدد: ۳ عامل × ۸۰+ رقم")
    print(f"   DB: {args.db}")
    
    # اگر کاربر NEG می‌خواد، یعنی sin(30n°) = -0.5
    if args.sin == 'NEG':
        print("   → هر ۳ عامل در کلاس 7 یا 11 (mod 12) → sin = -0.5")
        print("   → ۳ (فرد) عامل NEG → sin(30n°) = -0.5 ✓")
    
    conn = init_db(args.db)
    cur = conn.cursor()
    
    generated = 0
    failed_attempts = 0
    pos_count = 0
    neg_count = 0
    start_time = time.time()
    
    while generated < args.count and failed_attempts < args.count * 10:
        result = gen_303_with_3_factors(sin_class=args.sin)
        if result is None:
            failed_attempts += 1
            continue
        
        # درج در DB
        try:
            cur.execute("""
                INSERT INTO numbers_303 
                (n, n_digits, p1, p2, p3, p1_digits, p2_digits, p3_digits,
                 p1_mod12, p2_mod12, p3_mod12, sin_30n, sin_class, n_neg_factors)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result['n'], result['n_digits'],
                result['p1'], result['p2'], result['p3'],
                result['p1_digits'], result['p2_digits'], result['p3_digits'],
                result['p1_mod12'], result['p2_mod12'], result['p3_mod12'],
                result['sin_30n'], result['sin_class'], result['n_neg_factors'],
            ))
            conn.commit()
            generated += 1
            if result['sin_class'] == 'NEG':
                neg_count += 1
            else:
                pos_count += 1
            
            if generated % 10 == 0 or generated <= 5:
                elapsed = time.time() - start_time
                rate = generated / elapsed if elapsed > 0 else 0
                print(f"  [{generated}/{args.count}] {result['sin_class']} "
                      f"n_digits={result['n_digits']} "
                      f"p=[{result['p1_digits']},{result['p2_digits']},{result['p3_digits']}] "
                      f"mod12=[{result['p1_mod12']},{result['p2_mod12']},{result['p3_mod12']}] "
                      f"rate={rate:.1f}/s")
        except sqlite3.IntegrityError:
            # عدد تکراری
            pass
    
    elapsed = time.time() - start_time
    rate = generated / elapsed if elapsed > 0 else 0
    
    print("\n" + "=" * 80)
    print("📊 خلاصه")
    print("=" * 80)
    print(f"   تولید شده: {generated}/{args.count}")
    print(f"   تلاش ناموفق: {failed_attempts}")
    print(f"   زمان: {elapsed:.2f} ثانیه")
    print(f"   سرعت: {rate:.2f} عدد/ثانیه")
    print(f"   کلاس NEG (sin=-0.5): {neg_count}")
    print(f"   کلاس POS (sin=+0.5): {pos_count}")
    
    # آمار DB
    cur.execute("SELECT COUNT(*) FROM numbers_303")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM numbers_303 WHERE sin_class = 'NEG'")
    neg_db = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM numbers_303 WHERE sin_class = 'POS'")
    pos_db = cur.fetchone()[0]
    print(f"\n   📂 کل در DB: {total}")
    print(f"      NEG (sin=-0.5): {neg_db}")
    print(f"      POS (sin=+0.5): {pos_db}")
    
    # نمایش نمونه‌ها
    print("\n📋 نمونه‌های اخیر (۵ عدد اول):")
    cur.execute("""
        SELECT id, n_digits, p1_digits, p2_digits, p3_digits,
               p1_mod12, p2_mod12, p3_mod12, sin_class, n_neg_factors
        FROM numbers_303 ORDER BY id LIMIT 5
    """)
    print(f"{'id':<5} {'n_dig':<6} {'p1':<5} {'p2':<5} {'p3':<5} {'m1':<3} {'m2':<3} {'m3':<3} {'class':<5} {'neg#':<4}")
    for row in cur.fetchall():
        print(f"{row[0]:<5} {row[1]:<6} {row[2]:<5} {row[3]:<5} {row[4]:<5} "
              f"{row[5]:<3} {row[6]:<3} {row[7]:<3} {row[8]:<5} {row[9]:<4}")
    
    conn.close()
    print(f"\n💾 DB: {args.db}")


if __name__ == '__main__':
    main()
