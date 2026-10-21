<?php
require_once __DIR__ . '/functions.php';
secure_session_start();
$lang = $_GET['lang'] ?? $_COOKIE['lang'] ?? 'fa';
$dir = in_array($lang, ['fa','ar','ur']) ? 'rtl' : 'ltr';
?>
<!DOCTYPE html>
<html lang="<?= $lang ?>" dir="<?= $dir ?>">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="canonical" href="<?= site_url() ?>/download">
<title>📥 نرم‌افزار — پلتفرم علمی</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>
body{font-family:'Vazirmatn',sans-serif;background:#0f172a;color:#e2e8f0}
.card{background:#1e293b;border-radius:20px;transition:all 0.3s}
.card:hover{transform:translateY(-4px);box-shadow:0 12px 32px rgba(79,70,229,0.3)}
.platform-icon{font-size:3rem;margin-bottom:0.5rem}
.cmd-box{background:#0c1929;border:1px solid #334155;border-radius:12px;padding:1rem;font-family:monospace;font-size:0.85rem;color:#94a3b8;direction:ltr}
.cmd-box .cmd-prompt{color:#3b82f6}
.cmd-box .cmd-output{color:#34d399}
.gradient-text{background:linear-gradient(135deg,#818cf8,#c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
</style>
</head>
<body class="min-h-screen">
<header class="bg-slate-900/80 backdrop-blur sticky top-0 z-50 border-b border-slate-800">
<div class="max-w-5xl mx-auto px-4 py-3 flex justify-between">
<div class="flex items-center gap-2"><span class="text-2xl">📥</span><span class="font-bold text-sm">نرم‌افزار</span></div>
<a href="/" class="text-xs text-slate-400">🏠 خانه</a>
</div>
</header>

<div class="max-w-5xl mx-auto px-4 py-8">
<!-- Hero -->
<div class="text-center mb-8">
<h1 class="text-3xl font-bold gradient-text mb-2">دانلود نرم‌افزار</h1>
<p class="text-sm text-slate-400">پلتفرم علمی چندرسته‌ای — همه‌ی پلتفرم‌ها</p>
</div>

<!-- Platform cards -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">

<!-- Desktop (Windows/Linux/Mac) -->
<div class="card p-6">
<div class="platform-icon text-center">🖥️</div>
<h2 class="text-xl font-bold text-center mb-2">دسکتاپ</h2>
<p class="text-xs text-slate-400 text-center mb-4">Windows • Linux • macOS</p>
<div class="space-y-2">
<div class="bg-slate-800 rounded-lg p-3 text-center">
<div class="text-sm font-bold">🪟 Windows</div>
<div class="text-xs text-slate-400">volunteer-client.exe (938KB)</div>
<a href="https://github.com/ldrcoir/science-platform/releases" class="block mt-2 bg-blue-600 text-white py-2 rounded-lg text-sm">📥 دانلود</a>
</div>
<div class="bg-slate-800 rounded-lg p-3 text-center">
<div class="text-sm font-bold">🐧 Linux</div>
<div class="text-xs text-slate-400">volunteer-client (938KB)</div>
<a href="https://github.com/ldrcoir/science-platform/releases" class="block mt-2 bg-blue-600 text-white py-2 rounded-lg text-sm">📥 دانلود</a>
</div>
<div class="bg-slate-800 rounded-lg p-3 text-center">
<div class="text-sm font-bold">🍎 macOS</div>
<div class="text-xs text-slate-400">Build from source (Cargo)</div>
<a href="https://github.com/ldrcoir/science-platform" class="block mt-2 bg-blue-600 text-white py-2 rounded-lg text-sm">📦 Source</a>
</div>
</div>
</div>

<!-- Android -->
<div class="card p-6">
<div class="platform-icon text-center">📱</div>
<h2 class="text-xl font-bold text-center mb-2">اندروید</h2>
<p class="text-xs text-slate-400 text-center mb-4">APK — WebView</p>
<div class="bg-slate-800 rounded-lg p-4 text-center">
<div class="text-sm font-bold">🤖 Android 5+</div>
<div class="text-xs text-slate-400 mt-1">APK ساخته‌شده توسط GitHub Actions</div>
<a href="https://github.com/ldrcoir/science-platform/actions" class="block mt-3 bg-emerald-600 text-white py-2 rounded-lg text-sm">📥 دانلود APK</a>
<div class="text-xs text-slate-500 mt-2">یا از Actions tab در GitHub دانلود کنید</div>
</div>
</div>

<!-- Web / PWA -->
<div class="card p-6">
<div class="platform-icon text-center">🌐</div>
<h2 class="text-xl font-bold text-center mb-2">وب</h2>
<p class="text-xs text-slate-400 text-center mb-4">مرورگر — PWA</p>
<div class="bg-slate-800 rounded-lg p-4 text-center">
<div class="text-sm font-bold">سایت</div>
<div class="text-xs text-slate-400 mt-1">بدون نصب — مستقیم در مرورگر</div>
<a href="/" class="block mt-3 bg-purple-600 text-white py-2 rounded-lg text-sm">🌐 باز کردن</a>
<div class="text-xs text-slate-500 mt-2">برای نصب روی موبایل: Add to Home Screen</div>
</div>
</div>

</div>

<!-- CLI Commands -->
<div class="card p-6 mb-6">
<h2 class="text-xl font-bold mb-4">⌨️ دستورات خط فرمان (CLI)</h2>
<p class="text-sm text-slate-400 mb-4">برای نرم‌افزار دسکتاپ (Rust) — خروجی انگلیسی</p>
<div class="space-y-3">
<div class="cmd-box">
<span class="cmd-prompt">$</span> volunteer-client --benchmark<br>
<span class="cmd-output"># Run speed test — count primes, factor numbers</span>
</div>
<div class="cmd-box">
<span class="cmd-prompt">$</span> volunteer-client --list-languages<br>
<span class="cmd-output"># Show 29 supported languages</span>
</div>
<div class="cmd-box">
<span class="cmd-prompt">$</span> volunteer-client --show-specs<br>
<span class="cmd-output"># Show CPU, RAM, Disk info</span>
</div>
<div class="cmd-box">
<span class="cmd-prompt">$</span> volunteer-client --storage-report<br>
<span class="cmd-output"># Disk space report (for decentralized hosting)</span>
</div>
<div class="cmd-box">
<span class="cmd-prompt">$</span> volunteer-client --process-tasks tasks.txt --output results.txt<br>
<span class="cmd-output"># Factor all numbers in tasks.txt, save to results.txt</span>
</div>
<div class="cmd-box">
<span class="cmd-prompt">$</span> volunteer-client --server https://your-domain.com --api-key YOUR_KEY<br>
<span class="cmd-output"># Connect to server and start volunteering</span>
</div>
</div>
</div>

<!-- Features -->
<div class="card p-6 mb-6">
<h2 class="text-xl font-bold mb-4">✨ ویژگی‌ها</h2>
<div class="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
<div class="bg-slate-800 rounded-lg p-3">⚡ 13M numbers/sec</div>
<div class="bg-slate-800 rounded-lg p-3">🌍 29 languages</div>
<div class="bg-slate-800 rounded-lg p-3">🛡️ Anti-debug</div>
<div class="bg-slate-800 rounded-lg p-3">💾 938KB binary</div>
<div class="bg-slate-800 rounded-lg p-3">📊 Disk report</div>
<div class="bg-slate-800 rounded-lg p-3">🔧 Task processing</div>
<div class="bg-slate-800 rounded-lg p-3">🔗 Server connection</div>
<div class="bg-slate-800 rounded-lg p-3">📱 Android APK</div>
<div class="bg-slate-800 rounded-lg p-3">🌐 PWA support</div>
</div>
</div>

</div>
</body>
</html>
