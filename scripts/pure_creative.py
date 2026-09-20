#!/usr/bin/env python3
"""
بدون اسم، بدون روش‌های شناخته‌شده.
فقط ابتکار شخصی + اعداد خالص.

من یک عدد بزرگ M می‌گیرم. می‌دانم فقط یک فاکتورش را (F1).
می‌خواهم فاکتور دوم را پیدا کنم — اگر موجود باشد.

ایده‌ی کاملاً تازه:
- عدد M را در مبناهای مختلف بنویسم (مبنای 3, 7, 11, 13, ...)
- در هر مبنای نمایش، الگوهایی پنهان است که ممکن است به فاکتور اشاره کند
- مثلاً در مبنای 3، عدد M = 2^1237 - 1 چه شکلی است؟
- آیا فاکتور در مبنای خاصی به‌صورت "الگوی تکراری" ظاهر می‌شود؟

روش دیگر:
- M = 2^1237 - 1 = یک عدد با 372 رقم در مبنای 10
- اگر این عدد را به بلوک‌های k رقمی تقسیم کنم (k = 5, 10, 20, 50, ...)
- و روی هر بلوک یک تحویل کننده اعمال کنم (جمع، XOR, ...)
- ممکن است الگوی مرتبط با فاکتور پیدا شود
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime, gcd, powmod, next_prime, invert
import math
import time
import random
from pathlib import Path

P = 1237
M = mpz(2)**P - 1
F1 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
F2 = M // F1
N = int(F2)

LOG = Path('/home/z/my-project/download/pure_creative.log')
LOG.write_text('')
def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')

log(f'شروع: فقط با اعداد و ابتکار شخصی')
log(f'M = 2^1237 - 1 ({len(str(M))} digits)')
log(f'F1 = {F1} (شناخته‌شده)')
log(f'F2 = M / F1 ({len(str(F2))} digits)')
log(f'')

# ============================================================
# ابتکار ۱: نمایش در مبناهای مختلف
# ============================================================
log(f'ابتکار ۱: نمایش M در مبناهای مختلف')
log(f'')

for base in [3, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293]:
    digits_in_base = []
    n_temp = int(M)
    while n_temp > 0:
        digits_in_base.append(n_temp % base)
        n_temp //= base
    digits_in_base.reverse()
    
    # Count frequency of each digit
    from collections import Counter
    digit_freq = Counter(digits_in_base)
    
    # Look for repeating patterns
    pattern_3 = []
    for i in range(len(digits_in_base) - 2):
        pattern_3.append(tuple(digits_in_base[i:i+3]))
    pattern_3_freq = Counter(pattern_3)
    most_common_3 = pattern_3_freq.most_common(1)[0] if pattern_3_freq else None
    
    log(f'  مبنای {base}: {len(digits_in_base)} digits, پرتکرارترین 3-gram: {most_common_3}')

log(f'')

# ============================================================
# ابتکار ۲: M را به بلوک‌های کوچک تقسیم کن
# ============================================================
log(f'ابتکار ۲: تقسیم M به بلوک‌های k رقمی (مبنای 10) و بررسی ویژگی‌ها')
log(f'')

M_str = str(M)
M_int = int(M)

for block_size in [5, 10, 20, 50, 100, 200, 372]:
    if block_size > len(M_str):
        continue
    # Split into blocks
    n_blocks = (len(M_str) + block_size - 1) // block_size
    blocks = []
    for i in range(0, len(M_str), block_size):
        block = M_str[i:i+block_size]
        blocks.append(int(block))
    
    # Compute checksums
    sum_blocks = sum(blocks)
    xor_blocks = 0
    for b in blocks:
        xor_blocks ^= b
    
    # GCD of each block with M
    gcds = []
    for b in blocks[:20]:  # first 20
        g = gcd(b, M_int)
        if 1 < g < M_int:
            gcds.append((b, g))
    
    log(f'  بلوک {block_size}-رقمی: {n_blocks} بلوک، sum = {sum_blocks}, XOR = {xor_blocks}')
    if gcds:
        for b, g in gcds:
            log(f'    بلوک {b} → gcd با M = {g}')

log(f'')

# ============================================================
# ابتکار ۳: ساخت عدد جدید از روی F1 و دیدن چه می‌شود
# ============================================================
log(f'ابتکار ۳: اعداد ساخته‌شده از روی F1')
log(f'')

# ایده‌ها:
# - F1 برعکس شده
# - مجموع ارقام F1
# - جابجایی ارقام F1
# - F1 در مبناهای دیگر

F1_str = str(F1)
F1_int = int(F1)

# ۳.۱: F1 برعکس
F1_reversed = int(F1_str[::-1])
log(f'  F1 برعکس: {F1_reversed} ({len(str(F1_reversed))} digits, is_prime: {is_prime(F1_reversed)})')
g = gcd(F1_reversed, M_int)
log(f'    gcd(F1_rev, M) = {g}')
if 1 < g < M_int:
    log(f'    >>> FACTOR! {g}')

# ۳.۲: مجموع ارقام F1
digit_sum_F1 = sum(int(d) for d in F1_str)
log(f'  مجموع ارقام F1: {digit_sum_F1}')
g = gcd(digit_sum_F1, M_int)
log(f'    gcd(digit_sum, M) = {g}')

# ۳.۳: F1 ± 1, ±2, ±3, ...
for offset in range(-50, 51):
    val = F1_int + offset
    if val <= 1: continue
    g = gcd(val, M_int)
    if 1 < g < M_int:
        log(f'  F1 + {offset} = {val}, gcd با M = {g} → FACTOR!')

# ۳.۴: F1 به توان‌های کوچک
for k in range(2, 20):
    val = F1_int ** k
    if val > M_int: break
    g = gcd(val - 1, M_int)
    if 1 < g < M_int:
        log(f'  F1^{k} - 1, gcd با M = {g}')

log(f'')

# ============================================================
# ابتکار ۴: استفاده از «نسبت طلایی» و اعداد فیبوناچی
# ============================================================
log(f'ابتکار ۴: استفاده از دنباله‌ی فیبوناچی')
log(f'')

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# F1 mod fib(n) for various n
for n in range(2, 200):
    f = fib(n)
    if f == 0: continue
    rem_F1 = int(F1) % f
    rem_M = int(M) % f
    # اگر rem_F1 != 0 ولی rem_M == 0، آن‌گاه f شامل عامل M است
    if rem_F1 != 0 and rem_M == 0:
        log(f'  fib({n}) = {f}: F1 mod fib = {rem_F1}, M mod fib = 0 → فاکتور!')
        g = gcd(f, int(F2))
        if 1 < g < int(F2):
            log(f'    >>> FACTOR! {g}')
    
    # همچنین: gcd(F1, fib(n)) و gcd(M, fib(n))
    g_M = gcd(f, int(M))
    if 1 < g_M < int(M):
        log(f'  fib({n}) = {f}: gcd با M = {g_M} → FACTOR!')

log(f'')

# ============================================================
# ابتکار ۵: استفاده از اعداد کاتالان، بلامان، و ...
# ============================================================
log(f'ابتکار ۵: استفاده از دنباله‌های مرتبط با اعداد اول')
log(f'')

# اعداد مرکب: 4, 6, 8, 9, 10, 12, ... — مجموع ارقام
# اعداد مثلثی: 1, 3, 6, 10, 15, 21, 28, ...
# اعداد مربعی: 1, 4, 9, 16, 25, 36, ...
# اعداد کاتالان: 1, 1, 2, 5, 14, 42, 132, 429, ...

# محاسبه‌ی اعداد کاتالان
def catalan(n):
    if n <= 1: return 1
    c = 1
    for i in range(n):
        c = c * 2 * (2*i + 1) // (i + 2)
    return c

# Catalan numbers
for n in range(1, 50):
    c = catalan(n)
    if c <= 1: continue
    g = gcd(c, int(M))
    if 1 < g < int(M):
        log(f'  Catalan({n}) = {c}: gcd با M = {g} → FACTOR!')

log(f'')

# ============================================================
# ابتکار ۶: «متغیرهای کنجکاو» — عدد M را با اعداد غیرمعمول مقایسه کن
# ============================================================
log(f'ابتکار ۶: اعداد غیرمعمول و ارتباط با M')
log(f'')

# نسبت طلایی: φ = (1+√5)/2 ≈ 1.618
phi = (1 + math.sqrt(5)) / 2

# M / φ^k برای kهای مختلف — اگر برابر عدد صحیح شود یا نزدیک باشد
# Use integer division to avoid float overflow
log(f'  مبنای φ^k: تست با تقسیم صحیح M بر φ^k تقریبی')
phi_int = 1618  # φ × 1000 (integer approx)
M_int_local = M_int
for k in range(1, 100):
    phi_k = int(phi_int ** k)  # this is (φ×1000)^k = φ^k × 1000^k
    # M / φ^k ≈ M × 1000^k / phi_k
    # Use: M_int * (10^(3k)) // phi_k
    if phi_k > 10**(3*k + 50): break  # avoid huge computations
    val = (M_int_local * (10**(3*k))) // phi_k
    g = gcd(val, M_int_local)
    if 1 < g < M_int_local:
        log(f'  M / φ^{k} (approx) = {val}, gcd با M = {g} → FACTOR!')

log(f'')

# ============================================================
# ابتکار ۷: ساختن اعداد «کوچک» از روی F2 و دیدن آیا فاکتور دارند
# ============================================================
log(f'ابتکار ۷: ساخت اعداد کوچک از روی F2')
log(f'')

# F2 mod (k^j) برای k, j مختلف
for k in [2, 3, 5, 7, 11, 13, 100, 1000, 10^6, 10^9]:
    for j in range(1, 20):
        mod = k ** j
        if mod > int(F2): break
        rem = int(F2) % mod
        if rem == 0:
            log(f'  F2 mod {k}^{j} = F2 mod {mod} = 0 → FACTOR!')
            g = gcd(mod, int(F2))
            if 1 < g < int(F2):
                log(f'    >>> FACTOR! {g}')
                sys.exit(0)

log(f'')

# ============================================================
# ابتکار ۸: «رسم» F2 و دیدن الگو
# ============================================================
log(f'ابتکار ۸: تحلیل الگوی رقم‌های F2')
log(f'')

F2_str = str(F2)
F2_int = int(F2)

# موقعیت رقم‌ها
positions = {}
for i, d in enumerate(F2_str):
    if d not in positions:
        positions[d] = []
    positions[d].append(i)

log(f'  موقعیت رقم‌ها در F2 (303 digits):')
for d in sorted(positions.keys()):
    log(f'    رقم {d}: {len(positions[d])} بار در موقعیت‌های {positions[d][:10]}{"..." if len(positions[d]) > 10 else ""}')

log(f'')

# فاصله‌های بین رقم‌های یکسان
log(f'  فاصله‌های بین تکرارهای هر رقم:')
for d in sorted(positions.keys()):
    if len(positions[d]) > 1:
        diffs = [positions[d][i+1] - positions[d][i] for i in range(len(positions[d])-1)]
        log(f'    رقم {d}: فاصله‌ها = {diffs[:10]}{"..." if len(diffs) > 10 else ""}')

log(f'')

# ============================================================
# ابتکار ۹: ساخت گراف از رقم‌های F2
# ============================================================
log(f'ابتکار ۹: گراف رقم‌های F2 (ارقام متوالی)')
log(f'')

# هر رقم به عنوان گره، یال‌های بین ارقام متوالی
# تحلیل: درجه‌ی هر رقم، میانگین طول مسیر، ...
from collections import defaultdict

transitions = defaultdict(int)
for i in range(len(F2_str) - 1):
    transitions[(F2_str[i], F2_str[i+1])] += 1

# پیدا کردن متداول‌ترین انتقال‌ها
top_transitions = sorted(transitions.items(), key=lambda x: -x[1])[:20]
log(f'  متداول‌ترین انتقال‌ها در F2:')
for (a, b), count in top_transitions:
    log(f'    {a} → {b}: {count} بار')

# کم‌تکرارترین انتقال‌ها
bottom_transitions = sorted(transitions.items(), key=lambda x: x[1])[:10]
log(f'  کم‌تکرارترین انتقال‌ها:')
for (a, b), count in bottom_transitions:
    log(f'    {a} → {b}: {count} بار')

log(f'')

# ============================================================
# ابتکار ۱۰: ساختن عدد از روی F2 و گرفتن gcd
# ============================================================
log(f'ابتکار ۱۰: ساختن اعداد از روی F2')
log(f'')

# مثلاً: رقم‌های F2 در موقعیت‌های زوج و فرد را جدا کن
even_pos = int(''.join(F2_str[i] for i in range(0, len(F2_str), 2)))
odd_pos = int(''.join(F2_str[i] for i in range(1, len(F2_str), 2)))
log(f'  رقم‌های موقعیت زوج: {even_pos} ({len(str(even_pos))} digits)')
log(f'  رقم‌های موقعیت فرد: {odd_pos} ({len(str(odd_pos))} digits)')
g1 = gcd(even_pos, F2_int)
g2 = gcd(odd_pos, F2_int)
log(f'    gcd(zوج, F2) = {g1}')
log(f'    gcd(فرد, F2) = {g2}')

# اولین نصف F2 و دومین نصف
half = len(F2_str) // 2
first_half = int(F2_str[:half])
second_half = int(F2_str[half:])
log(f'  اولین نصف: {first_half} ({len(str(first_half))} digits)')
log(f'  دومین نصف: {second_half} ({len(str(second_half))} digits)')
g1 = gcd(first_half, F2_int)
g2 = gcd(second_half, F2_int)
log(f'    gcd(نصف اول, F2) = {g1}')
log(f'    gcd(نصف دوم, F2) = {g2}')

# جمع دو نصف
sum_halves = first_half + second_half
log(f'  جمع دو نصف: {sum_halves}')
g = gcd(sum_halves, F2_int)
log(f'    gcd(جمع, F2) = {g}')
if 1 < g < F2_int:
    log(f'    >>> FACTOR! {g}')

# تفاوت دو نصف
diff_halves = abs(first_half - second_half)
log(f'  تفاوت دو نصف: {diff_halves} ({len(str(diff_halves))} digits)')
g = gcd(diff_halves, F2_int)
log(f'    gcd(تفاوت, F2) = {g}')
if 1 < g < F2_int:
    log(f'    >>> FACTOR! {g}')

log(f'')

log(f'پایان')
