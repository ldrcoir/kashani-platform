<?php
// ============================================================
// index.php — صفحه‌ی اصلی سایت PHP
// پلتفرم ریاضی پارسی — چندزبانه (فارسی/انگلیسی/عربی 🇵🇸)
// به افتخار Jamshid al-Kashi (الکاشی)
// Compatible with cPanel / Linux hosting
// ============================================================

session_start();
require_once __DIR__ . '/functions.php';

// Detect language
$lang = $_GET['lang'] ?? $_COOKIE['lang'] ?? 'fa';
if (!in_array($lang, ['fa', 'en', 'ar'])) $lang = 'fa';
setcookie('lang', $lang, time() + 86400 * 30, '/');

$dir = ($lang === 'fa' || $lang === 'ar') ? 'rtl' : 'ltr';
$stats = get_site_stats();
$series = get_math_series();

$ranges = [
    ['range' => '1 - 100K', 'digits' => 5, 'primes' => 9592, 'composites' => 90407, 'complete' => true],
    ['range' => '1 - 1M', 'digits' => 6, 'primes' => 78498, 'composites' => 921501, 'complete' => true],
    ['range' => '1 - 10M', 'digits' => 7, 'primes' => 664579, 'composites' => 9335420, 'complete' => true],
    ['range' => '1 - 100M', 'digits' => 8, 'primes' => 5761455, 'composites' => 94238544, 'complete' => true],
    ['range' => '1 - 200M', 'digits' => 9, 'primes' => 5317482, 'composites' => 94682519, 'complete' => true],
    ['range' => '200M - 1B', 'digits' => 9, 'primes' => 0, 'composites' => 0, 'complete' => false],
];
?>
<!DOCTYPE html>
<html lang="<?= $lang ?>" dir="<?= $dir ?>">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <?= seo_meta(t('title', $lang) . ' — ' . t('dedicated', $lang), t('subtitle', $lang)) ?>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Vazirmatn', 'Segoe UI', Tahoma, sans-serif; }
        .gradient-amber { background: linear-gradient(135deg, #f59e0b, #ea580c); }
        .gradient-emerald { background: linear-gradient(135deg, #10b981, #0d9488); }
        .gradient-blue { background: linear-gradient(135deg, #3b82f6, #6366f1); }
        .gradient-purple { background: linear-gradient(135deg, #a855f7, #7c3aed); }
        .gradient-rose { background: linear-gradient(135deg, #f43f5e, #ec4899); }
        .gradient-cyan { background: linear-gradient(135deg, #06b6d4, #3b82f6); }
        .gradient-yellow { background: linear-gradient(135deg, #eab308, #f59e0b); }
        .card-hover { transition: transform 0.2s, box-shadow 0.2s; }
        .card-hover:hover { transform: translateY(-4px); box-shadow: 0 12px 24px rgba(0,0,0,0.15); }
        .progress-bar { transition: width 0.5s ease; }
        .flag { font-size: 1.2em; }
    </style>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
</head>
<body class="bg-gray-50 min-h-screen flex flex-col">

<!-- Header -->
<header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-3">
            <span class="text-3xl">🕌</span>
            <div>
                <h1 class="text-xl font-bold text-gray-800"><?= t('title', $lang) ?></h1>
                <p class="text-xs text-gray-500"><?= t('subtitle', $lang) ?></p>
            </div>
        </div>
        <div class="flex items-center gap-2">
            <a href="?lang=fa" class="px-3 py-1 rounded <?= $lang=='fa'?'bg-blue-600 text-white':'bg-gray-100' ?>">🇮🇷</a>
            <a href="?lang=en" class="px-3 py-1 rounded <?= $lang=='en'?'bg-blue-600 text-white':'bg-gray-100' ?>">🇬🇧</a>
            <a href="?lang=ar" class="px-3 py-1 rounded <?= $lang=='ar'?'bg-blue-600 text-white':'bg-gray-100' ?>">🇵🇸</a>
        </div>
    </div>
</header>

<!-- Hero -->
<section class="max-w-7xl mx-auto px-4 py-12 text-center">
    <div class="text-6xl mb-4">🔢</div>
    <h2 class="text-4xl font-bold mb-4 bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
        <?= t('title', $lang) ?>
    </h2>
    <p class="text-lg text-gray-600 mb-2"><?= t('subtitle', $lang) ?></p>
    <span class="inline-block bg-amber-100 text-amber-800 px-4 py-1 rounded-full text-sm">
        <?= t('dedicated', $lang) ?> (1380-1429)
    </span>
    <div class="mt-6 flex flex-wrap justify-center gap-3">
        <a href="factor.php" class="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700">
            🧮 <?= t('start_factoring', $lang) ?>
        </a>
        <a href="network.php" class="px-6 py-3 border-2 border-blue-600 text-blue-600 rounded-lg font-semibold hover:bg-blue-50">
            👥 <?= t('join_network', $lang) ?>
        </a>
        <a href="magazine.php" class="px-6 py-3 border-2 border-gray-400 text-gray-600 rounded-lg font-semibold hover:bg-gray-100">
            📚 <?= t('read_magazine', $lang) ?>
        </a>
    </div>
</section>

<!-- Stats -->
<section class="max-w-7xl mx-auto px-4 py-8">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl p-6 text-center shadow-sm card-hover">
            <div class="text-3xl mb-2">🏆</div>
            <div class="text-3xl font-bold text-amber-600"><?= number_format($stats['contributions']) ?></div>
            <div class="text-sm text-gray-500"><?= t('contributions', $lang) ?></div>
        </div>
        <div class="bg-white rounded-xl p-6 text-center shadow-sm card-hover">
            <div class="text-3xl mb-2">📊</div>
            <div class="text-3xl font-bold text-emerald-600"><?= number_format($stats['frontier']) ?></div>
            <div class="text-sm text-gray-500"><?= t('frontier', $lang) ?></div>
        </div>
        <div class="bg-white rounded-xl p-6 text-center shadow-sm card-hover">
            <div class="text-3xl mb-2">⭐</div>
            <div class="text-3xl font-bold text-purple-600"><?= $stats['series'] ?></div>
            <div class="text-sm text-gray-500"><?= t('series_count', $lang) ?></div>
        </div>
        <div class="bg-white rounded-xl p-6 text-center shadow-sm card-hover">
            <div class="text-3xl mb-2">👥</div>
            <div class="text-3xl font-bold text-blue-600"><?= $stats['users'] ?></div>
            <div class="text-sm text-gray-500"><?= t('users_count', $lang) ?></div>
        </div>
    </div>
</section>

<!-- Features -->
<section class="max-w-7xl mx-auto px-4 py-8">
    <div class="grid md:grid-cols-3 gap-6">
        <div class="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-6 card-hover">
            <div class="text-4xl mb-3">💻</div>
            <h3 class="font-bold text-lg mb-2"><?= t('for_processing', $lang) ?></h3>
            <p class="text-sm text-gray-600"><?= $lang=='fa' ? 'پردازش ریاضی، علمی، پزشکی و دارویی با شبکه داوطلبین' : ($lang=='ar' ? 'معالجة رياضية وعلمية وطبية' : 'Math, science, medical processing') ?></p>
        </div>
        <div class="bg-gradient-to-br from-emerald-50 to-green-50 rounded-xl p-6 card-hover">
            <div class="text-4xl mb-3">🛡️</div>
            <h3 class="font-bold text-lg mb-2"><?= t('secure_platform', $lang) ?></h3>
            <p class="text-sm text-gray-600"><?= $lang=='fa' ? 'امنیت بالا، احراز هویت با Gmail و شماره موبایل' : ($lang=='ar' ? 'أمان عالٍ' : 'High security, Gmail + phone auth') ?></p>
        </div>
        <div class="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-6 card-hover">
            <div class="text-4xl mb-3">🌐</div>
            <h3 class="font-bold text-lg mb-2"><?= t('volunteer_network', $lang) ?></h3>
            <p class="text-sm text-gray-600"><?= $lang=='fa' ? 'نرم‌افزار Rust برای پردازش سریع' : ($lang=='ar' ? 'برنامج Rust' : 'Rust software for fast processing') ?></p>
        </div>
    </div>
</section>

<!-- Login -->
<section class="max-w-7xl mx-auto px-4 py-8">
    <div class="bg-white rounded-xl shadow-sm p-6 text-center max-w-md mx-auto">
        <h3 class="font-bold text-lg mb-4"><?= $lang=='fa' ? 'ورود / ثبت‌نام' : ($lang=='ar' ? 'تسجيل الدخول' : 'Login / Register') ?></h3>
        <div class="flex flex-wrap justify-center gap-3">
            <a href="auth/google.php" class="px-6 py-3 border-2 border-gray-300 rounded-lg font-semibold hover:border-red-500 hover:text-red-500">
                📧 <?= t('login_gmail', $lang) ?>
            </a>
            <a href="auth/phone.php" class="px-6 py-3 border-2 border-gray-300 rounded-lg font-semibold hover:border-green-500 hover:text-green-500">
                📱 <?= t('login_phone', $lang) ?>
            </a>
        </div>
    </div>
</section>

<!-- Math Series -->
<section class="max-w-7xl mx-auto px-4 py-8">
    <h3 class="text-2xl font-bold text-center mb-6"><?= t('series_count', $lang) ?></h3>
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        <?php foreach ($series as $s): ?>
        <div class="rounded-xl p-6 text-white card-hover <?= 'gradient-'.$s['color'] ?>">
            <div class="text-4xl mb-2"><?= $s['icon'] ?></div>
            <h4 class="text-xl font-bold"><?= $lang=='fa' ? $s['name'] : ($lang=='ar' ? $s['name_ar'] : $s['name_en']) ?></h4>
            <p class="text-sm opacity-90 mb-2"><?= $lang=='fa' ? $s['description'] : ($s['description_en'] ?? $s['description']) ?></p>
            <?php if ($s['oeis_ref']): ?>
            <span class="text-xs bg-white bg-opacity-20 px-2 py-1 rounded">OEIS: <?= $s['oeis_ref'] ?></span>
            <?php endif; ?>
        </div>
        <?php endforeach; ?>
    </div>
</section>

<!-- Range Progress -->
<section class="max-w-7xl mx-auto px-4 py-8">
    <h3 class="text-2xl font-bold text-center mb-6"><?= $lang=='fa' ? 'پیشرفت بازه‌ها' : ($lang=='ar' ? 'تقدم النطاقات' : 'Range Progress') ?></h3>
    <div class="bg-white rounded-xl shadow-sm p-6">
        <?php foreach ($ranges as $r): ?>
        <div class="mb-4">
            <div class="flex items-center justify-between mb-1">
                <div class="flex items-center gap-2">
                    <span class="px-2 py-1 rounded text-xs <?= $r['complete'] ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700' ?>">
                        <?= $r['complete'] ? '✅ '.t('range_complete',$lang) : '⏳ '.t('range_in_progress',$lang) ?>
                    </span>
                    <span class="font-mono text-sm"><?= $r['range'] ?></span>
                    <span class="text-xs text-gray-400">(<?= $r['digits'] ?> <?= t('digits',$lang) ?>)</span>
                </div>
                <span class="text-sm text-gray-500"><?= $r['primes'] > 0 ? number_format($r['primes']).' '.t('primes',$lang) : '—' ?></span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-blue-600 h-2 rounded-full progress-bar" style="width: <?= $r['complete'] ? 100 : 30 ?>%"></div>
            </div>
            <div class="flex justify-between text-xs text-gray-400 mt-1">
                <span><?= $r['composites'] > 0 ? number_format($r['composites']).' '.t('composites',$lang) : '—' ?></span>
                <span><?= $r['complete'] ? '✅ '.t('no_gaps',$lang) : '' ?></span>
            </div>
        </div>
        <?php endforeach; ?>
    </div>
</section>

<!-- Motivation -->
<section class="max-w-7xl mx-auto px-4 py-12 text-center">
    <div class="text-5xl mb-3">🏆</div>
    <p class="text-2xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
        <?= t('motivation', $lang) ?>
    </p>
    <p class="text-sm text-gray-500 mt-3"><?= t('eff_prize', $lang) ?></p>
</section>

<!-- Footer -->
<footer class="mt-auto bg-white border-t py-6">
    <div class="max-w-7xl mx-auto px-4 text-center">
        <p class="text-sm text-gray-500"><?= t('copyright', $lang) ?> — <?= t('dedicated', $lang) ?></p>
        <div class="flex justify-center gap-4 mt-2 text-xs text-gray-400">
            <a href="https://factordb.com" class="hover:text-blue-600">FactorDB</a>
            <a href="https://oeis.org" class="hover:text-blue-600">OEIS</a>
            <a href="https://www.mersenne.org" class="hover:text-blue-600">GIMPS</a>
            <a href="admin/" class="hover:text-blue-600"><?= t('admin_panel', $lang) ?></a>
            <a href="download/" class="hover:text-blue-600"><?= t('download_software', $lang) ?></a>
        </div>
    </div>
</footer>

</body>
</html>
