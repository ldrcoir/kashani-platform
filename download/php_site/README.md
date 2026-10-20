# پلتفرم علمی چندرسته‌ای پارسی — به افتخار غیاث‌الدین جمشید کاشانی

پلتفرم بین‌المللی برای پردازش‌های علمی، آموزشی، پژوهشی و مشارکتی در علوم مختلف (ریاضی، فیزیک، پزشکی، داروسازی، کامپیوتر).

## 🌐 دامنه پیشنهادی (آزاد)

چک‌شده با `whois.nic.ir` — این دامنه‌ها آزادن:

| دامنه | معنی |
|-------|------|
| `platform-oloom.ir` | پلتفرم علوم ⭐ |
| `shabakeh-oloom.ir` | شبکه‌ی علوم |
| `all-science.ir` | همه‌ی علوم |
| `oloom-paye.ir` | علوم پایه |
| `oloom-iran.ir` | علوم ایران |
| `danesh-platform.ir` | دانش پلتفرم |
| `khayyam-biruni.ir` | خیام و بیرونی |
| `alkashani.ir` | الکاشانی |

**پیشنهاد:** `platform-oloom.ir`

## 📁 ساختار

```
php_site/
├── index.php              صفحه‌ی اصلی چندزبانه (10 زبان)
├── factor.php            آزمایشگاه فاکتور (Pollard rho، مرسن، سینوس)
├── lessons.php           فهرست درس‌ها
├── lesson.php            نمایش درس با تمرین تعاملی
├── magazine.php          مجله
├── article.php           نمایش مقاله
├── chat.php              چت بین‌المللی (WebSocket)
├── scientists.php        موزه‌ی دانشمندان
├── scientist.php         صفحه‌ی یک دانشمند
├── network.php           شبکه‌ی داوطلبین
├── download.php          دانلود نرم‌افزار
├── install.php           نصب خودکار
├── api.php                REST API
│
├── admin/                پنل ادمین
│   ├── index.php         داشبورد
│   ├── setup.php         ساخت ادمین
│   ├── users.php         مدیریت کاربران
│   ├── articles.php      مقالات (با AI generator)
│   ├── lessons.php      درس‌ها (با AI generator)
│   ├── work_queue.php    مدیریت توزیع کار
│   ├── nodes.php         نودهای داوطلب
│   ├── ai.php            پنل AI
│   ├── settings.php      تنظیمات کامل
│   ├── backup.php        پشتیبان‌گیری
│   └── logout.php
│
├── auth/
│   ├── phone.php         ورود با موبایل (SMS)
│   └── logout.php
│
├── ai/
│   ├── chat.php          چت با AI دستیار
│   └── api.php           API برای AI (chat، translate، generate)
│
├── chat-server/          سرور چت Node.js WebSocket
│   ├── server.js
│   ├── package.json
│   └── README.md
│
├── complete_install.sql  تمام جداول دیتابیس
├── default_lessons.sql   ۸ درس پیش‌فرض
├── config.php            تنظیمات
├── database.php          کلاس DB
├── functions.php         توابع + i18n + security + FactorDB
├── .htaccess            pretty URLs + security
├── manifest.json         PWA
└── sw.js                 Service Worker
```

## 🚀 نصب روی cPanel (ParsWebHost)

### ۱. آپلود
فایل `kashani_platform.zip` را در `public_html/` آپلود و اکسترکت کنید.

### ۲. ساخت دیتابیس
cPanel → **MySQL Databases** → ساخت database + user

### ۳. اجرای نصب
به `https://platform-oloom.ir/install.php` بروید:
- اطلاعات MySQL را وارد کنید
- URL سایت را وارد کنید
- نصب خودکار تمام جداول

### ۴. ساخت ادمین
به `https://platform-oloom.ir/admin/setup.php` بروید و ادمین بسازید.

### ۵. تنظیمات
به پنل ادمین → تنظیمات بروید:
- FactorDB Token: `6ddb5c17a56f920f3ee459e99036bd57`
- AI: Provider (Z.ai) + API Key
- چت سرور URL

### ۶. چت سرور (Node.js)
```bash
cd public_html/chat-server
npm install
nohup node server.js > chat.log 2>&1 &
```

یا با Cron هر دقیقه:
```bash
cd /home/USER/public_html/chat-server && pgrep -f "node server.js" > /dev/null || nohup /usr/bin/node server.js > chat.log 2>&1 &
```

## 🌍 زبان‌های پشتیبانی
- 🇮🇷 فارسی (fa) — پیش‌فرض
- 🇬🇧 English (en)
- 🇸🇦 العربية (ar)
- 🇫🇷 Français (fr)
- 🇩🇪 Deutsch (de)
- 🇪🇸 Español (es)
- 🇷🇺 Русский (ru)
- 🇨🇳 中文 (zh)
- 🇹🇷 Türkçe (tr)
- 🇵🇰 اردو (ur)

## 🎓 ویژگی‌ها

### ✅ فاز ۱: سایت پایه + پنل ادمین
- [x] سایت چندزبانه (۱۰ زبان)
- [x] پنل ادمین قوی
- [x] احراز هویت (موبایل، Google OAuth)
- [x] REST API با rate limit
- [x] PWA (نصب روی موبایل)
- [x] نصب خودکار

### ✅ فاز ۲: چت بین‌المللی
- [x] WebSocket Node.js
- [x] روم‌های موضوعی
- [x] LaTeX با MathJax
- [x] Multi-device sync
- [x] Rate limiting

### ✅ فاز ۳: آزمایشگاه مجازی
- [x] فاکتور (Pollard rho در JS)
- [x] تولید عدد اول (Miller-Rabin)
- [x] تست قضیه‌ی سینوس
- [x] تست اعداد مرسن

### ✅ فاز ۴: هوش مصنوعی
- [x] چت با AI دستیار (Z.ai، OpenAI، Claude، Gemini)
- [x] تولید خودکار مقاله با AI
- [x] تولید خودکار درس با AI (با تمرین)
- [x] ترجمه با AI

### ✅ فاز ۵: آموزش تعاملی
- [x] ۸ درس پیش‌فرض (اعداد اول، قضیه‌ی سینوس، Pollard Rho، RSA، پروتئین فولدینگ، قضیه‌ی بنیادی حساب، مرسن، Miller-Rabin)
- [x] تمرین چندگزینه‌ای و تشریحی
- [x] پیگیری پیشرفت
- [x] نظرات

### ✅ فاز ۶: سیستم توزیع کار
- [x] ۱۴ نوع کار (ریاضی، پزشکی، فیزیک، کامپیوتر)
- [x] تشخیص مشخصات سیستم کاربر
- [x] توزیع بر اساس CPU, RAM, GPU
- [x] Credit و آمار

### 🔄 فاز ۷: نرم‌افزار دسکتاپ (Rust)
- [ ] CLI کامل
- [ ] GUI (آینده)
- [ ] آپدیت خودکار

## 🔌 API Endpoints
- `GET /api/stats` — آمار
- `POST /api/factor_submit` — ثبت فاکتور
- `GET /api/ranges` — بازه‌ها
- `GET /api/series` — سری‌ها
- `GET /api/articles` — مقالات
- `GET /api/lessons` — درس‌ها
- `GET /api/scientists` — دانشمندان
- `POST /api/comment_article` — نظر روی مقاله
- `POST /api/comment_lesson` — نظر روی درس
- `POST /api/lesson_complete` — تکمیل درس
- `POST /api/apikey` — ساخت API key

## 🛡️ امنیت
- ✅ CSRF token در همه‌ی فرم‌ها
- ✅ secure_session_start (httponly، samesite=Strict)
- ✅ regenerate_session بعد از login
- ✅ Rate limiting (60 req/min)
- ✅ sanitize_html برای محتوا
- ✅ Security headers (CSP, X-Frame-Options, ...)
- ✅ Audit log

## 📜 لایسنس
MIT License — Free for everyone

## 🎓 به افتخار
غیاث‌الدین جمشید کاشانی (۱۳۸۰-۱۴۲۹) — ریاضیدان و ستاره‌شناس پارسی که π را تا ۱۶ رقم محاسبه کرد.
