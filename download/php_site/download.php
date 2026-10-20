<?php
// ============================================================
// download.php — دانلود نرم‌افزار
// ============================================================
require_once __DIR__ . '/functions.php';
secure_session_start();
$lang = $_GET['lang'] ?? $_COOKIE['lang'] ?? 'fa';
$dir = in_array($lang, ['fa','ar','ur']) ? 'rtl' : 'ltr';
?>
<!DOCTYPE html>
<html lang="<?= $lang ?>" dir="<?= $dir ?>">
<head>
<meta charset="UTF-8">
    <link rel="canonical" href="<?= site_url() ?>/download.php">

<title>📥 دانلود نرم‌افزار</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
</head>
<body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 py-3 flex justify-between">
        <div class="flex items-center gap-3"><span class="text-3xl">📥</span><h1 class="text-xl font-bold">دانلود نرم‌افزار</h1></div>
        <a href="index.php" class="px-4 py-2 bg-gray-100 rounded text-sm">🏠 خانه</a>
    </div>
</header>
<div class="max-w-4xl mx-auto p-4">
    <div class="bg-gradient-to-br from-amber-50 to-rose-50 rounded-xl p-6 mb-6">
        <h2 class="text-2xl font-bold mb-2">🚀 نرم‌افزار داوطلبین (Python)</h2>
        <p class="text-sm text-gray-700 mb-4">نرم‌افزار دسکتاپ چندسکویی برای مشارکت در پردازش‌های علمی. با Python + tkinter نوشته شده و بر روی ویندوز، مک و لینوکس کار می‌کند.</p>
        <div class="bg-white rounded-lg p-4 text-sm">
            <strong>ویژگی‌ها:</strong>
            <ul class="list-disc mr-5 mt-2 space-y-1">
                <li>🖥️ GUI زیبا با ۴ تب (اتصال، سیستم، کار، لاگ)</li>
                <li>💻 تشخیص خودکار CPU، RAM، GPU، disk</li>
                <li>🧠 دریافت کار متناسب با سیستم شما</li>
                <li>⚡ اجرای محاسبات (فاکتور، prime hunt، benchmark)</li>
                <li>🏆 ثبت credit در حساب شما</li>
                <li>🔄 حالت آفلاین (اگر سرور قطع باشد)</li>
                <li>🚀 چندسکویی (ویندوز، مک، لینوکس)</li>
                <li>🔐 امن (HTTPS، API key محلی)</li>
                <li>📦 قابل‌تبدیل به executable (.exe)</li>
            </ul>
            <div class="mt-3 bg-blue-50 p-3 rounded">
                <strong class="text-blue-700">📥 نصب سریع:</strong>
                <pre class="mt-2 text-xs bg-slate-900 text-emerald-400 p-2 rounded" dir="ltr">pip install psutil  # اختیاری
python3 volunteer_app.py</pre>
            </div>
            <div class="mt-3 bg-purple-50 p-3 rounded">
                <strong class="text-purple-700">📦 ساخت executable:</strong>
                <pre class="mt-2 text-xs bg-slate-900 text-emerald-400 p-2 rounded" dir="ltr">pip install pyinstaller
pyinstaller --onefile --windowed volunteer_app.py</pre>
            </div>
        </div>
    </div>
    <div class="grid md:grid-cols-3 gap-4 mb-6">
        <a href="#" class="bg-white rounded-xl shadow p-6 text-center"><div class="text-4xl mb-2">🪟</div><h3 class="font-bold text-lg">ویندوز</h3><p class="text-xs text-gray-500 mb-3">Windows 10/11 x64</p><span class="text-sm bg-blue-600 text-white px-4 py-2 rounded inline-block">📥 دانلود</span></a>
        <a href="#" class="bg-white rounded-xl shadow p-6 text-center"><div class="text-4xl mb-2">🍎</div><h3 class="font-bold text-lg">macOS</h3><p class="text-xs text-gray-500 mb-3">Universal Binary</p><span class="text-sm bg-blue-600 text-white px-4 py-2 rounded inline-block">📥 دانلود</span></a>
        <a href="#" class="bg-white rounded-xl shadow p-6 text-center"><div class="text-4xl mb-2">🐧</div><h3 class="font-bold text-lg">لینوکس</h3><p class="text-xs text-gray-500 mb-3">AppImage + deb</p><span class="text-sm bg-blue-600 text-white px-4 py-2 rounded inline-block">📥 دانلود</span></a>
    </div>
    <div class="bg-white rounded-xl shadow p-5">
        <h3 class="font-bold text-lg mb-2">⚙️ راه‌اندازی</h3>
        <ol class="list-decimal mr-5 space-y-1 text-sm">
            <li>دانلود و اجرا</li>
            <li>با حساب سایت لاگین (یا API key از پنل کاربری)</li>
            <li>نرم‌افزار مشخصات سیستم شما را می‌گیرد (CPU، RAM، GPU، disk)</li>
            <li>سرور کار متناسب به شما می‌دهد (مثلاً GPU دارید → ML training)</li>
            <li>کار پردازش می‌شود، credit جمع می‌شود</li>
        </ol>
    </div>
</div>
</body>
</html>
