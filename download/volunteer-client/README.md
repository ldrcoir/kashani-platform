# 🖥️ نرم‌افزار پردازشی پلتفرم علمی چندرشته‌ای پارسی

نرم‌افزار دسکتاپ برای مشارکت در پردازش‌های علمی — به افتخار غیاث‌الدین جمشید کاشانی

## 📦 نصب

### نصب ساده (ویندوز، مک، لینوکس)
```bash
# فقط Python 3.8+ نیاز است
python3 volunteer_app.py
```

### نصب با psutil (اختیاری، برای مشخصات دقیق‌تر)
```bash
pip install psutil
```

### ساخت executable (بدون نیاز به Python)
```bash
pip install pyinstaller
# ویندوز:
pyinstaller --onefile --windowed volunteer_app.py
# لینوکس:
pyinstaller --onefile volunteer_app.py
# خروجی در dist/volunteer_app (یا .exe در ویندوز)
```

## 🚀 استفاده

### حالت GUI (پیشنهادی)
```bash
python3 volunteer_app.py
```

سپس در پنجره:
1. به تب «اتصال» بروید
2. آدرس سرور: `https://platform-oloom.ir`
3. API Key خود را وارد کنید
4. نام نود (اختیاری)
5. روی «🚀 شروع» کلیک کنید

### حالت CLI
```bash
python3 volunteer_app.py --cli --server https://platform-oloom.ir --api-key YOUR_KEY
```

### نمایش مشخصات سیستم
```bash
python3 volunteer_app.py --show-specs
```

## 🎯 کارهایی که انجام می‌دهد

### ۱. جمع‌آوری مشخصات سیستم
- CPU: مدل، تعداد هسته، threads
- RAM: کل، در دسترس
- Disk: کل، آزاد، نوع (HDD/SSD/NVMe)
- GPU: مدل، VRAM، CUDA support (با nvidia-smi یا lspci)
- OS: نام، نسخه، معماری

### ۲. اتصال به سرور
- ثبت نود با مشخصات سیستم
- دریافت لیست کارهای قابل اجرا
- Heartbeat هر ۶۰ ثانیه

### ۳. اجرای کار
انواع کار:
- `factor_small` / `factor_medium` / `factor_large` — فاکتور کردن اعداد
- `prime_hunt` — پیدا کردن اعداد اول
- `mersenne_check` — تست اعداد مرسن
- `data_analysis` — تحلیل آماری داده
- `benchmark` — تست سرعت سیستم

### ۴. ثبت credit
هر کار موفق → credit به حساب کاربر اضافه می‌شود

### ۵. حالت آفلاین
اگر سرور در دسترس نباشد:
- اجرای محلی (شمارش اعداد اول)
- آمار محلی
- تلاش مجدد برای اتصال

## 📊 تب‌ها

### 🔌 اتصال
- تنظیمات سرور و API key
- شروع/توقف worker

### 💻 سیستم
- نمایش مشخصات سیستم شما
- به‌روزرسانی زنده

### 🚀 کار
- آمار کار انجام‌شده
- credit جمع‌شده
- کار جاری

### 📜 لاگ
- لاگ‌های زنده‌ی فعالیت

## 🔑 گرفتن API Key

۱. به `https://platform-oloom.ir` بروید
۲. با موبایل یا Gmail وارد شوید
۳. به پروفایل کاربری بروید
۴. روی «ساخت API Key» کلیک کنید
۵. کپی و در نرم‌افزار وارد کنید

## 🌐 چندسکویی

| سیستم‌عامل | پشتیبانی | تست شده |
|-----------|---------|---------|
| 🪟 Windows 10/11 | ✅ | با Python 3.8+ |
| 🍎 macOS | ✅ | با Python 3.8+ |
| 🐧 Linux | ✅ | با Python 3.8+ |

## 🛡️ امنیت

- تمام ارتباطات HTTPS
- API key فقط محلی ذخیره می‌شود
- هیچ داده‌ی حساسی به سرور ارسال نمی‌شود (فقط مشخصات سخت‌افزاری)
- Rate limiting (۶۰ req/min)

## 📜 لایسنس
MIT License — Free for everyone

## 🎓 به افتخار
غیاث‌الدین جمشید کاشانی (۱۳۸۰-۱۴۲۹) — ریاضیدان و ستاره‌شناس پارسی
