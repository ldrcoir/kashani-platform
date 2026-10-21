# 🦀 نرم‌افزار Rust برای شبکه داوطلبین پردازش
## به افتخار Jamshid al-Kashi (الکاشی)

### ساختار:
```
volunteer-client/
├── Cargo.toml
├── src/
│   ├── main.rs          // ورودی اصلی
│   ├── factor.rs        // فاکتور کردن (rho, ECM wrapper)
│   ├── network.rs       // ارتباط با سرور
│   ├── auth.rs          // احراز هویت (Gmail, phone)
│   ├── benchmark.rs     // benchmark سخت‌افزار
│   └── config.rs        // تنظیمات
```

### ویژگی‌ها:
1. **سرعت بالا**: Rust + Assembly برای محاسبات سنگین
2. **احراز هویت**: Gmail OAuth + شماره موبایل ایرانی
3. **شبکه**: WebSocket برای دریافت/ارسال work units
4. **Credit tracking**: ثبت خودکار credit در FactorDB
5. **Auto-update**: آپدیت خودکار نرم‌افزار
6. **Cross-platform**: Windows, Linux, macOS
7. **Security**: رمزنگاری end-to-end

### پروتکل:
```
1. کاربر لاگین می‌کنه (Gmail یا موبایل)
2. سرور یه work unit می‌فرسته (بازه‌ی اعداد)
3. کلاینت فاکتور می‌کنه (با Rust + Assembly)
4. نتایج رو برمی‌گردونه
5. سرور ثبت می‌کنه + credit می‌ده
```
