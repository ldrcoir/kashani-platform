<?php
// ============================================================
// index.php — صفحه‌ی اصلی پلتفرم علمی چندرشته‌ای پارسی
// طراحی: کم‌اسکرول، آی‌کن‌های کلیک‌دار، گرافیک مدرن
// ============================================================
require_once __DIR__ . '/functions.php';
secure_session_start();

$lang = $_GET['lang'] ?? $_COOKIE['lang'] ?? 'fa';
if (!in_array($lang, ['fa','en','ar','fr','de','es','ru','zh','tr','ur'])) $lang = 'fa';
setcookie('lang', $lang, time() + 86400 * 30, '/');
$dir = in_array($lang, ['fa','ar','ur']) ? 'rtl' : 'ltr';

try { $stats = get_site_stats(); } catch (Exception $e) {
    $stats = ['users' => 0, 'articles' => 0, 'factors' => 0, 'series' => 0, 'contributions' => 24000, 'largest_factor' => 50, 'frontier' => 200000000];
}
try { $series = get_math_series(); } catch (Exception $e) { $series = []; }
$user = current_user();

$ranges = [
    ['range' => '۱ - ۲۰۰M', 'primes' => 110789, 'composites' => 0, 'complete' => true],
    ['range' => '۲۰۰M - ۱B', 'primes' => 0, 'composites' => 0, 'complete' => false, 'in_progress' => true],
];
?>
<!DOCTYPE html>
<html lang="<?= $lang ?>" dir="<?= $dir ?>">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="canonical" href="<?= site_url() ?>/">
    <title>پلتفرم علمی چندرشته‌ای پارسی</title>
    <meta name="description" content="پلتفرم بین‌المللی علوم: ریاضی، فیزیک، پزشکی، داروسازی، کامپیوتر — آموزش، چت، پردازش">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#3b82f6">
    <style>
        body { font-family: 'Vazirmatn', sans-serif; }
        .card { transition: all 0.2s; }
        .card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.12); }
        .icon-btn { width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; border-radius: 20px; font-size: 2rem; cursor: pointer; }
        .icon-btn:hover { transform: scale(1.1); }
        .progress { height: 6px; border-radius: 3px; background: #e5e7eb; overflow: hidden; }
        .progress-bar { height: 100%; background: #3b82f6; border-radius: 3px; transition: width 0.5s; }
    </style>
</head>
<body class="bg-gray-50">

<!-- Compact Header with Icon Navigation -->
<header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-4 py-2 flex items-center justify-between">
        <div class="flex items-center gap-2">
            <span class="text-2xl">🔬</span>
            <span class="font-bold text-sm">پلتفرم علمی پارسی</span>
        </div>
        <div class="flex items-center gap-1">
            <!-- Icon navigation — compact, no text -->
            <a href="factor.php" class="icon-btn bg-blue-50 hover:bg-blue-100" title="آزمایشگاه">🧮</a>
            <a href="lessons.php" class="icon-btn bg-emerald-50 hover:bg-emerald-100" title="آموزش">📚</a>
            <a href="magazine.php" class="icon-btn bg-amber-50 hover:bg-amber-100" title="مجله">📰</a>
            <a href="chat.php" class="icon-btn bg-purple-50 hover:bg-purple-100" title="چت">💬</a>
            <a href="ai/chat.php" class="icon-btn bg-rose-50 hover:bg-rose-100" title="AI">🤖</a>
            <a href="scientists.php" class="icon-btn bg-indigo-50 hover:bg-indigo-100" title="دانشمندان">🎓</a>
            <a href="network.php" class="icon-btn bg-cyan-50 hover:bg-cyan-100" title="شبکه داوطلبین">👥</a>
            <?php if ($user): ?>
            <a href="profile.php" class="icon-btn bg-gray-100" title="پروفایل">👤</a>
            <?php else: ?>
            <a href="auth/phone.php" class="icon-btn bg-gray-100" title="ورود">🔑</a>
            <?php endif; ?>
        </div>
    </div>
</header>

<!-- Hero Section — compact -->
<section class="bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-8">
    <div class="max-w-6xl mx-auto px-4 text-center">
        <h1 class="text-3xl font-bold mb-2">🔬 پلتفرم علمی چندرشته‌ای</h1>
        <p class="text-sm opacity-90 mb-4">ریاضی • فیزیک • پزشکی • داروسازی • کامپیوتر</p>
        <div class="flex justify-center gap-4 text-center">
            <div><span class="text-2xl font-bold"><?= number_format($stats['contributions']) ?></span><br><span class="text-xs opacity-80">مشارکت</span></div>
            <div><span class="text-2xl font-bold"><?= number_format($stats['frontier']) ?></span><br><span class="text-xs opacity-80">فرانتیر</span></div>
            <div><span class="text-2xl font-bold"><?= number_format($stats['users']) ?></span><br><span class="text-xs opacity-80">کاربر</span></div>
            <div><span class="text-2xl font-bold"><?= number_format($stats['articles']) ?></span><br><span class="text-xs opacity-80">مقاله</span></div>
        </div>
    </div>
</section>

<!-- Main content — grid, compact, no long scroll -->
<section class="max-w-6xl mx-auto px-4 py-6">
    <!-- Quick Access Cards — 4 columns, compact -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <a href="factor.php" class="card bg-white rounded-xl p-4 text-center shadow">
            <div class="text-3xl mb-1">🧮</div>
            <div class="font-bold text-sm">آزمایشگاه</div>
            <div class="text-xs text-gray-500">فاکتور • اول • مرسن</div>
        </a>
        <a href="lessons.php" class="card bg-white rounded-xl p-4 text-center shadow">
            <div class="text-3xl mb-1">📚</div>
            <div class="font-bold text-sm">آموزش</div>
            <div class="text-xs text-gray-500">درس تعاملی</div>
        </a>
        <a href="ai/chat.php" class="card bg-white rounded-xl p-4 text-center shadow">
            <div class="text-3xl mb-1">🤖</div>
            <div class="font-bold text-sm">دستیار AI</div>
            <div class="text-xs text-gray-500">سوال بپرس</div>
        </a>
        <a href="chat.php" class="card bg-white rounded-xl p-4 text-center shadow">
            <div class="text-3xl mb-1">💬</div>
            <div class="font-bold text-sm">چت</div>
            <div class="text-xs text-gray-500">بین‌المللی</div>
        </a>
        <a href="magazine.php" class="card bg-white rounded-xl p-4 text-center shadow">
            <div class="text-3xl mb-1">📰</div>
            <div class="font-bold text-sm">مجله</div>
            <div class="text-xs text-gray-500">مقالات</div>
        </a>
        <a href="scientists.php" class="card bg-white rounded-xl p-4 text-center shadow">
            <div class="text-3xl mb-1">🎓</div>
            <div class="font-bold text-sm">دانشمندان</div>
            <div class="text-xs text-gray-500">پارسی و جهانی</div>
        </a>
        <a href="network.php" class="card bg-white rounded-xl p-4 text-center shadow">
            <div class="text-3xl mb-1">👥</div>
            <div class="font-bold text-sm">شبکه داوطلبین</div>
            <div class="text-xs text-gray-500">پردازش مشارکتی</div>
        </a>
        <a href="download.php" class="card bg-white rounded-xl p-4 text-center shadow">
            <div class="text-3xl mb-1">📥</div>
            <div class="font-bold text-sm">نرم‌افزار</div>
            <div class="text-xs text-gray-500">دسکتاپ</div>
        </a>
    </div>

    <!-- Progress Bar — compact -->
    <div class="bg-white rounded-xl shadow p-4 mb-4">
        <h3 class="font-bold text-sm mb-2">📈 پیشرفت بازه‌ها</h3>
        <?php foreach ($ranges as $r): ?>
        <div class="mb-2">
            <div class="flex justify-between text-xs mb-1">
                <span class="font-mono" dir="ltr"><?= $r['range'] ?></span>
                <span class="<?= $r['complete']?'text-green-600':'text-yellow-600' ?>"><?= $r['complete']?'✅ کامل':'⏳ در حال' ?></span>
            </div>
            <div class="progress"><div class="progress-bar" style="width: <?= $r['complete']?100:30 ?>%"></div></div>
        </div>
        <?php endforeach; ?>
    </div>

    <!-- Math Series — compact grid -->
    <?php if (!empty($series)): ?>
    <div class="bg-white rounded-xl shadow p-4 mb-4">
        <h3 class="font-bold text-sm mb-2">🧮 سری‌های ریاضی</h3>
        <div class="grid grid-cols-3 md:grid-cols-6 gap-2">
            <?php foreach ($series as $s): ?>
            <div class="text-center p-2 rounded-lg bg-<?= $s['color'] ?? 'blue' ?>-50">
                <div class="text-2xl"><?= $s['icon'] ?? '🔢' ?></div>
                <div class="text-xs font-bold"><?= sanitize($s['name'] ?? '') ?></div>
            </div>
            <?php endforeach; ?>
        </div>
    </div>
    <?php endif; ?>
</section>

<!-- Footer — compact -->
<footer class="bg-slate-900 text-slate-400 py-3">
    <div class="max-w-6xl mx-auto px-4 flex justify-between text-xs">
        <span>© 2026 — پلتفرم علمی پارسی</span>
        <div class="flex gap-3">
            <a href="admin/" class="hover:text-white">🔐 ادمین</a>
            <a href="api.php" class="hover:text-white">🔌 API</a>
            <a href="oeis.php" class="hover:text-white">🔢 OEIS</a>
        </div>
    </div>
</footer>

</body>
</html>
