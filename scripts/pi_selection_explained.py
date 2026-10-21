import sys, os, json
sys.set_int_max_str_digits(100000)
import gmpy2
from gmpy2 import mpz, is_prime

# Load pi digits
PI_FILE = "/home/z/my-project/download/kashani_pi/pi_100k_digits.txt"
with open(PI_FILE) as f:
    pi_decimal = f.read()

print("=" * 80)
print("🔢 اعداد π: چطور انتخاب می‌شن؟")
print("=" * 80)
print()
print(f"کل ارقام اعشار π: {len(pi_decimal)} رقم")
print(f"نمونه: π = 3.{pi_decimal[:50]}...")
print()
print("روش انتخاب:")
print("  ۱. یه 'موقعیت' (pos) در دنباله‌ی اعشار انتخاب می‌کنیم")
print("  ۲. از اون موقعیت، به اندازه‌ی 'size' رقم می‌گیریم")
print("  ۳. اگه عدد با ۰ شروع شه، یه رقم جلو می‌ریم")
print()

# Show the selection for the current batch
print("🟢 دسته فعلی (pos=5000 شروع):")
print()
pos = 5000
sizes = [30, 40, 50, 60, 70, 80, 90, 100]
print(f"{'#':<3} {'size':<6} {'pos شروع':<10} {'pos پایان':<10} {'پوشانی؟':<10} {'عدد (۳۰ رقم اول)'}")
print(f"{'-'*3} {'-'*6} {'-'*10} {'-'*10} {'-'*10} {'-'*50}")

for i, size in enumerate(sizes, 1):
    chunk = pi_decimal[pos:pos+size]
    while chunk.startswith('0'):
        pos += 1
        chunk = pi_decimal[pos:pos+size]
    
    start_pos = pos
    end_pos = pos + size - 1
    overlap = "❌ ندارد"  # چون متوالی هستن
    if i > 1:
        overlap = "❌ ندارد"  # هر کدوم بعد از قبلی شروع می‌شه
    
    n = int(chunk)
    print(f"{i:<3} {size:<6} {start_pos:<10} {end_pos:<10} {overlap:<10} {str(n)[:40]}")
    pos += size

print()
print("✅ نتیجه: هیچ پوشانی وجود نداره!")
print("   هر عدد بعد از قبلی شروع می‌شه، و ادامه‌ی دنباله‌ست")
print()

# Show overlap analysis for all our pi batches
print("=" * 80)
print("📊 تحلیل پوشانی همه‌ی دسته‌های π")
print("=" * 80)
print()

# Earlier batches
print("دسته ۱ (از جلسه قبلی، pos 0):")
earlier_positions = [(28, 0), (30, 28), (35, 58), (45, 93), (60, 138), (65, 198), (75, 264), (80, 340)]
print(f"  pos 0 → 420 (تمام ۸ عدد بدون پوشانی)")
print()

print("دسته ۲ (از جلسه قبلی، اعداد بزرگ‌تر):")
earlier_large = [(100, 0), (120, 100), (150, 220), (180, 370), (200, 550)]
print(f"  pos 0 → 750 (پوشانی با دسته ۱ در ۰-۴۲۰!)")
print()

print("دسته ۳ (فعلی، pos 5000 شروع):")
print(f"  pos 5000 → 5800 (هیچ پوشانی با قبلی‌ها!)")
print()

print("💡 نتیجه:")
print("  - دسته ۱ و ۲ پوشانی داشتن (هر دو از pos 0 شروع شده بودن)")
print("  - دسته ۳ از pos 5000 شروع می‌شه → هیچ پوشانی با قبلی‌ها")
print("  - می‌تونیم دسته‌های بعدی رو از pos 10000, 20000, ... شروع کنیم")
print()

# Available positions
print("📍 موقعیت‌های موجود:")
print(f"  کل: 0 تا {len(pi_decimal)-1}")
print(f"  استفاده‌شده: 0-750, 5000-5800")
print(f"  موجود: 750-5000, 5800-{len(pi_decimal)-1}")
print(f"  یعنی {5000 - 750} + {len(pi_decimal) - 5800} = {5000 - 750 + len(pi_decimal) - 5800} رقم موجود")
