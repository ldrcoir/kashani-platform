# 📱 اپ اندروید (WebView)

## ساخت اپ:
1. Android Studio را باز کنید
2. New Project → Empty Activity
3. کد زیر را در MainActivity.java قرار دهید
4. URL سایت را در `SITE_URL` قرار دهید
5. Build → APK

## فایل‌ها:
- `MainActivity.java` — اکتیویتی اصلی با WebView
- `activity_main.xml` — لایه‌ی XML
- `AndroidManifest.xml` — دسترسی‌ها
- `build.gradle` — پیکربندی

## ویژگی‌ها:
- WebView با JavaScript فعال
- آفلاین: پیام "نیاز به اینترنت" (نه صفحه‌ی خالی)
- پشتیبانی از چت صوتی
- پشتیبانی از دوربین (برای آواتار)
- Local Storage فعال
