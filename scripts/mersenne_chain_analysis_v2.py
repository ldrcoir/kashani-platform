#!/usr/bin/env python3
"""
بررسی پدیده‌ی زنجیره‌ی مرسن روی فایل بزرگ (p ≤ 8000)
"""
import sys, os, re, json
from collections import defaultdict
sys.set_int_max_str_digits(100000)
sys.path.insert(0, '/home/z/my-project/scripts')

from mersenne_chain_phenomenon import (
    MERSENNE_PRIME_EXPONENTS,
    find_mersenne_chains,
    analyze_sinus_method_on_mersennes,
)
from gmpy2 import mpz, is_prime

OUTPUT_DIR = "/home/z/my-project/download/sinus_method"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def parse_factorizations_v2(filepath):
    """
    تجزیه‌ی فایل فرمت جدید:
      M(11): [FULLY FACTORED]  (4 digits)
        M(11) = 2^11 - 1
        digits = 4
        factors (compact): P2 * P2
        factors (full):    23(P2) * 89(P2)
    """
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Pattern برای پیدا کردن هر بلوک M(p)
    pattern = re.compile(
        r'M\((\d+)\):\s*\[(.+?)\]\s*\((\d+)\s+digits\)\s*\n\s*M\(\d+\)\s*=\s*2\^\d+\s*-\s*1\s*\n\s*digits\s*=\s*\d+\s*\n\s*factors\s*\(compact\):\s*(.+?)\s*\n\s*factors\s*\(full\):\s*(.+?)\s*\n',
        re.MULTILINE
    )
    
    results = []
    for m in pattern.finditer(content):
        p = int(m.group(1))
        status = m.group(2).strip()
        n_digits = int(m.group(3))
        compact = m.group(4).strip()
        full = m.group(5).strip()
        
        # فقط فاکتوربندی‌های کامل رو می‌گیریم
        if 'FULLY FACTORED' not in status:
            continue
        
        # تجزیه‌ی عوامل: 23(P2) * 89(P2)
        factor_pattern = re.compile(r'(\d+)\(P(\d+)\)')
        factors = []
        for fm in factor_pattern.finditer(full):
            factors.append(int(fm.group(1)))
        
        if not factors:
            continue
        
        results.append({
            'p': p,
            'factors': factors,
            'n_factors': len(factors),
            'n_digits': n_digits,
        })
    
    return results


def main():
    print("=" * 80)
    print("🔗 پدیده‌ی زنجیره‌ی مرسن — تحلیل روی p ≤ 8000")
    print("=" * 80)
    
    filepath = "/home/z/my-project/download/A136030_Mersenne_composite_factorizations_to_8000.txt"
    facts = parse_factorizations_v2(filepath)
    print(f"\n📂 تعداد مرسن‌های مرکب فاکتوربندی‌شده (FULLY FACTORED): {len(facts)}")
    
    # پدیده‌ی زنجیره
    chains = find_mersenne_chains(facts)
    type_a = [c for c in chains if c['chain_type'] == 'A']
    type_b = [c for c in chains if c['chain_type'] == 'B']
    type_c = [c for c in chains if c['chain_type'] == 'C']
    
    print(f"\n🔗 زنجیره‌ی مرسن (p ≤ 8000):")
    print(f"   TYPE-A (q | M(p) و q ∈ Mersenne prime exponents): {len(type_a)} مورد")
    print(f"   TYPE-B (q اول ولی M(q) مرکب): {len(type_b)} مورد")
    print(f"   TYPE-C (q مرکب): {len(type_c)} مورد")
    
    print("\n📌 تمام TYPE-A (زنجیره‌های کامل):")
    print(f"{'M(p)':<10} {'عامل q':<25} {'q رقم':<8} {'وضعیت M(q)':<30}")
    print('-' * 80)
    for c in type_a:
        print(f"M({c['p']:<5})  {c['q_factor']:<25} {c['q_digits']:<8} {c['M_q_status']}")
    
    # اعتبارسنجی سینوس
    sinus_results = analyze_sinus_method_on_mersennes(facts)
    consistent = 0
    inconsistent_list = []
    for r in sinus_results:
        ok = (r['M_p_in_neg_class'] and r['neg_count_parity'] == 'odd') or \
             (not r['M_p_in_neg_class'] and r['neg_count_parity'] == 'even')
        if ok:
            consistent += 1
        else:
            inconsistent_list.append(r)
    
    total = len(sinus_results)
    print(f"\n🌊 قضیه‌ی سینوس روی {total} مرسن مرکب (p ≤ 8000):")
    print(f"   سازگار: {consistent}/{total} ({100*consistent/total:.2f}%)")
    if inconsistent_list:
        print(f"   ناسازگار: {len(inconsistent_list)} مورد")
        for r in inconsistent_list[:20]:
            print(f"     M({r['p']}): neg_count={r['neg_count_factors']}, parity={r['neg_count_parity']}, M(p)%12={r['M_p_mod_12']}")
    
    # یافتن اعداد با تعداد عوامل ۳ (طبق تأکید کاربر)
    print("\n" + "=" * 80)
    print("🎯 مرسن‌های مرکب با دقیقاً ۳ عامل (طبق قضیه‌ی سینوس)")
    print("=" * 80)
    three_factor = [r for r in sinus_results if r['n_factors'] == 3]
    print(f"   تعداد: {len(three_factor)}")
    print(f"   (این‌ها اعدادی هستن که کاربر می‌گه: 'سه تا در واقع عامل داره')")
    
    print(f"\n   {'p':<6} {'#digits':<10} {'n_fac':<6} {'neg#':<6} {'parity':<8}")
    print("   " + "-" * 50)
    for r in three_factor[:30]:
        print(f"   {r['p']:<6} {r['M_p_digits']:<10} {r['n_factors']:<6} "
              f"{r['neg_count_factors']:<6} {r['neg_count_parity']:<8}")
    
    # یافتن عوامل بزرگ (80+ رقم)
    print("\n" + "=" * 80)
    print("📊 آمار اندازه‌ی عوامل مرسن‌های مرکب")
    print("=" * 80)
    all_factors = []
    for r in sinus_results:
        for f in r['factors']:
            all_factors.append({
                'p': r['p'],
                'factor': f,
                'digits': len(str(f)),
            })
    
    by_size = {
        'small (<10 digits)': sum(1 for f in all_factors if f['digits'] < 10),
        'medium (10-30 digits)': sum(1 for f in all_factors if 10 <= f['digits'] < 30),
        'large (30-60 digits)': sum(1 for f in all_factors if 30 <= f['digits'] < 60),
        'huge (60-80 digits)': sum(1 for f in all_factors if 60 <= f['digits'] < 80),
        'massive (80+ digits)': sum(1 for f in all_factors if f['digits'] >= 80),
    }
    for k, v in by_size.items():
        print(f"   {k}: {v} عامل")
    
    # ذخیره
    output = {
        'file': filepath,
        'total_fully_factored': len(facts),
        'mersenne_chains': {
            'type_A_complete': type_a,
            'type_B_broken_count': len(type_b),
            'type_C_composite_count': len(type_c),
        },
        'sinus_verification': {
            'consistent': consistent,
            'total': total,
            'consistent_rate': f"{consistent}/{total}",
            'inconsistent_cases': inconsistent_list[:20],
        },
        'three_factor_mersennes_count': len(three_factor),
        'three_factor_examples': three_factor[:30],
        'factor_size_distribution': by_size,
    }
    
    out_path = f"{OUTPUT_DIR}/mersenne_chain_analysis_p_to_8000.json"
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n💾 ذخیره شد: {out_path}")


if __name__ == '__main__':
    main()
