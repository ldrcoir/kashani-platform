import sys, os, json
sys.set_int_max_str_digits(100000)

PI_FILE = "/home/z/my-project/download/kashani_pi/pi_100k_digits.txt"
with open(PI_FILE) as f:
    pi_decimal = f.read()

print("=" * 80)
print("🎯 مقایسه دو روش برای تعریف سری کاشانی")
print("=" * 80)
print()

# روش ۱: متوالی بدون پوشانی
print("🔵 روش ۱: متوالی بدون پوشانی (پیشنهاد فعلی)")
print("  قاعده: اعداد به‌صورت متوالی از اعشار π گرفته می‌شن")
print("  مثال: pos 0 → 30 رقم، pos 30 → 40 رقم، pos 70 → 50 رقم، ...")
print("  مزیت: ساده، هر رقم فقط یه بار استفاده می‌شه")
print("  عیب: اعداد به هم وابسته‌ان (هر کدوم ادامه‌ی قبلیه)")
print()

# روش ۲: از ۱ شروع، تعداد ارقام = عدد اول
print("🟢 روش ۲: تعداد ارقام = عدد اول (پیشنهاد شما)")
print("  قاعده: عدد اول n رو انتخاب می‌کنیم، بعد n رقم از اعشار π می‌گیریم")
print("  مثال: n=3 → 3 رقم، n=5 → 5 رقم، n=7 → 7 رقم، n=11 → 11 رقم، ...")
print("  مزیت: زیبا و معنادار — هر 'اندازه' یه عدد اول هست")
print("  عیب: برای n بزرگ (مثلاً ۱۰۰۰)، عدد ۱۰۰۰ رقمی ساخته می‌شه")
print()

# روش ۳: ترکیبی
print("🟡 روش ۳: ترکیبی — شروع از pos=1، هر بار به اندازه‌ی یه عدد اول بریم جلو")
print("  قاعده: عدد اول n رو انتخاب می‌کنیم، n رقم از π می‌گیریم، بعد n+1 رقم بعدی")
print("  مثال: n=3 → 3 رقم (pos 0-2)، n=5 → 5 رقم (pos 3-7)، n=7 → 7 رقم (pos 8-14)")
print("  مزیت: هم زیبای روش ۲، هم بدون پوشانی روش ۱")
print()

# Generate examples for each method
print("=" * 80)
print("📊 نمونه‌های هر روش")
print("=" * 80)
print()

# روش ۱: متوالی
print("🔵 روش ۱ (متوالی):")
pos = 0
for size in [30, 40, 50, 60, 70]:
    chunk = pi_decimal[pos:pos+size]
    while chunk.startswith('0'):
        pos += 1
        chunk = pi_decimal[pos:pos+size]
    print(f"  {size}d at pos {pos}: {chunk[:30]}...")
    pos += size

print()

# روش ۲: تعداد ارقام = عدد اول
print("🟢 روش ۲ (تعداد ارقام = عدد اول):")
primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
pos = 0
for p in primes[:10]:
    chunk = pi_decimal[pos:pos+p]
    while chunk.startswith('0'):
        pos += 1
        chunk = pi_decimal[pos:pos+p]
    print(f"  {p}d at pos {pos}: {chunk[:30]}{'...' if p > 30 else ''}")
    pos += p

print()

# روش ۳: ترکیبی
print("🟡 روش ۳ (ترکیبی):")
pos = 0
for p in primes[:10]:
    chunk = pi_decimal[pos:pos+p]
    while chunk.startswith('0'):
        pos += 1
        chunk = pi_decimal[pos:pos+p]
    print(f"  {p}d at pos {pos}: {chunk[:30]}{'...' if p > 30 else ''}")
    pos += p

print()

# مقایسه
print("=" * 80)
print("📊 مقایسه")
print("=" * 80)
print()
print(f"{'ویژگی':<25} {'روش ۱':<20} {'روش ۲':<20} {'روش ۳':<20}")
print(f"{'-'*25} {'-'*20} {'-'*20} {'-'*20}")
print(f"{'پوشانی':<25} {'ندارد':<20} {'ندارد':<20} {'ندارد':<20}")
print(f"{'ساده بودن':<25} {'بله':<20} {'بله':<20} {'بله':<20}")
print(f"{'معناداری ریاضی':<25} {'خیر':<20} {'بله!':<20} {'بله!':<20}")
print(f"{'دلیل انتخاب اندازه':<25} {'دلخواه':<20} {'عدد اول':<20} {'عدل اول':<20}")
print(f"{'قابل انتشار':<25} {'بله':<20} {'بله (زیبا!)':<20} {'بله (زیبا!)':<20}")
print()
print("💡 پیشنهاد من: روش ۲ یا ۳")
print("   چون: 'هر عضو سری Kashani به اندازه‌ی یه عدد اول از اعشار π ساخته می‌شه'")
print("   این یه تعریف ریاضی زیبا و قابل انتشار هست!")
