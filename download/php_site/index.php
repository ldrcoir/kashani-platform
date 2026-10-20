<?php
// ============================================================
// index.php — صفحه‌ی اصلی پلتفرم
// ============================================================
require_once __DIR__ . '/functions.php';
secure_session_start();

$lang = $_GET['lang'] ?? $_COOKIE['lang'] ?? Settings::get('language_default', 'fa');
if (!in_array($lang, $supported_langs)) $lang = 'fa';
setcookie('lang', $lang, time() + 86400 * 30, '/');
$dir = in_array($lang, ['fa','ar','ur']) ? 'rtl' : 'ltr';

try { $stats = get_site_stats(); } catch (Exception $e) {
    $stats = ['users' => 0, 'articles' => 0, 'factors' => 0, 'series' => 0, 'contributions' => 0, 'largest_factor' => 0, 'frontier' => 200000000];
}
try { $series = get_math_series(); } catch (Exception $e) { $series = []; }
try { $scientists = get_scientists(); } catch (Exception $e) { $scientists = []; }
try { $lessons = get_lessons(4); } catch (Exception $e) { $lessons = []; }
try { $articles = get_articles(3); } catch (Exception $e) { $articles = []; }

$user = current_user();

$ranges = [
    ['range' => '۱ - ۱۰۰ هزار', 'digits' => '۵', 'primes' => 9592, 'composites' => 90407, 'complete' => true],
    ['range' => '۱ - ۱ میلیون', 'digits' => '۶', 'primes' => 78498, 'composites' => 921501, 'complete' => true],
    ['range' => '۱ - ۱۰ میلیون', 'digits' => '۷', 'primes' => 664579, 'composites' => 9335420, 'complete' => true],
    ['range' => '۱ - ۱۰۰ میلیون', 'digits' => '۸', 'primes' => 5761455, 'composites' => 94238544, 'complete' => true],
    ['range' => '۱ - ۲۰۰ میلیون', 'digits' => '۹', 'primes' => 5317482, 'composites' => 94682519, 'complete' => true],
    ['range' => '۲۰۰M - ۱B', 'digits' => '۹', 'primes' => 0, 'composites' => 0, 'complete' => false, 'in_progress' => true],
];
?>
<!DOCTYPE html>
<html lang="<?= $lang ?>" dir="<?= $dir ?>">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="canonical" href="<?= site_url() ?>/">
    <?= seo_meta(t('title', $lang) . ' — ' . t('dedicated', $lang), t('subtitle', $lang) ?>
    <?= seo_jsonld_website() ?>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#f59e0b">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="علم پارسی">
    <style>
        body { font-family: 'Vazirmatn', 'Segoe UI', Tahoma, sans-serif; }
        .gradient-amber { background: linear-gradient(135deg, #f59e0b, #ea580c); }
        .gradient-emerald { background: linear-gradient(135deg, #10b981, #0d9488); }
        .gradient-blue { background: linear-gradient(135deg, #3b82f6, #6366f1); }
        .gradient-purple { background: linear-gradient(135deg, #a855f7, #7c3aed); }
        .gradient-rose { background: linear-gradient(135deg, #f43f5e, #ec4899); }
        .gradient-cyan { background: linear-gradient(135deg, #06b6d4, #3b82f6); }
        .card-hover { transition: transform 0.2s, box-shadow 0.2s; }
        .card-hover:hover { transform: translateY(-4px); box-shadow: 0 12px 24px rgba(0,0,0,0.15); }
        .progress-bar { transition: width 0.5s ease; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen flex flex-col">

<header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-3">
            <span class="text-3xl">🎓</span>
            <div>
                <h1 class="text-lg font-bold text-gray-800"><?= t('title', $lang) ?></h1>
                <p class="text-xs text-gray-500"><?= t('subtitle', $lang) ?></p>
            </div>
        </div>
        <div class="flex items-center gap-2">
            <details class="relative">
                <summary class="list-none cursor-pointer px-3 py-1 rounded bg-gray-100 hover:bg-gray-200 text-sm">🌐 <?= strtoupper($lang) ?></summary>
                <div class="absolute top-full mt-1 right-0 bg-white shadow-lg rounded-lg p-2 grid grid-cols-2 gap-1 text-xs w-48 z-50">
                    <?php foreach ($supported_langs as $l):
                        $flags = ['fa'=>'🇮🇷','en'=>'🇬🇧','ar'=>'🇸🇦','fr'=>'🇫🇷','de'=>'🇩🇪','es'=>'🇪🇸','ru'=>'🇷🇺','zh'=>'🇨🇳','tr'=>'🇹🇷','ur'=>'🇵🇰'];
                    ?>
                    <a href="?lang=<?= $l ?>" class="px-2 py-1 rounded hover:bg-blue-100 flex items-center gap-1 <?= $lang==$l?'bg-blue-600 text-white':'' ?>">
                        <span><?= $flags[$l] ?></span> <?= strtoupper($l) ?>
                    </a>
                    <?php endforeach; ?>
                </div>
            </details>
            
            <?php if ($user): ?>
            <a href="profile.php" class="px-3 py-1 rounded bg-blue-100 text-blue-700 text-sm">👤 <?= sanitize($user['name'] ?? $user['email']) ?></a>
            <?php else: ?>
            <a href="auth/phone.php" class="px-3 py-1 rounded bg-gray-100 text-sm">📱 ورود</a>
            <?php endif; ?>
        </div>
    </div>
    
    <nav class="border-b bg-gray-50">
        <div class="max-w-7xl mx-auto px-4 py-2 flex gap-3 text-sm overflow-x-auto">
            <a href="index.php" class="text-blue-600 font-bold whitespace-nowrap">🏠 خانه</a>
            <a href="factor.php" class="text-gray-700 hover:text-blue-600 whitespace-nowrap">🧮 آزمایشگاه</a>
            <a href="lessons.php" class="text-gray-700 hover:text-blue-600 whitespace-nowrap">📚 آموزش</a>
            <a href="magazine.php" class="text-gray-700 hover:text-blue-600 whitespace-nowrap">📰 مجله</a>
            <a href="chat.php" class="text-gray-700 hover:text-blue-600 whitespace-nowrap">💬 چت</a>
            <a href="scientists.php" class="text-gray-700 hover:text-blue-600 whitespace-nowrap">🎓 دانشمندان</a>
            <a href="network.php" class="text-gray-700 hover:text-blue-600 whitespace-nowrap">👥 شبکه‌ی داوطلبین</a>
            <a href="ai/chat.php" class="text-gray-700 hover:text-blue-600 whitespace-nowrap">🤖 AI</a>
            <a href="download.php" class="text-gray-700 hover:text-blue-600 whitespace-nowrap">📥 نرم‌افزار</a>
        </div>
    </nav>
</header>

<!-- Hero -->
<section class="max-w-7xl mx-auto px-4 py-12 text-center">
    <div class="text-6xl mb-4">🎓</div>
    <h2 class="text-4xl font-bold mb-4 bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
        <?= t('title', $lang) ?>
    </h2>
    <p class="text-lg text-gray-600 mb-2"><?= t('subtitle', $lang) ?></p>
    <span class="inline-block bg-amber-100 text-amber-800 px-4 py-1 rounded-full text-sm">
        🎓 <?= t('dedicated', $lang) ?> (1380-1429)
    </span>
    <div class="mt-6 flex flex-wrap justify-center gap-3">
        <a href="factor.php" class="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700">🧮 آزمایشگاه</a>
        <a href="lessons.php" class="px-6 py-3 bg-emerald-600 text-white rounded-lg font-semibold hover:bg-emerald-700">📚 آموزش</a>
        <a href="network.php" class="px-6 py-3 border-2 border-blue-600 text-blue-600 rounded-lg font-semibold hover:bg-blue-50">👥 شبکه‌ی داوطلبین</a>
        <a href="ai/chat.php" class="px-6 py-3 border-2 border-purple-600 text-purple-600 rounded-lg font-semibold hover:bg-purple-50">🤖 AI دستیار</a>
        <a href="chat.php" class="px-6 py-3 border-2 border-emerald-600 text-emerald-600 rounded-lg font-semibold hover:bg-emerald-50">💬 چت بین‌المللی</a>
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
            <div class="text-3xl mb-2">📚</div>
            <div class="text-3xl font-bold text-purple-600"><?= number_format($stats['articles']) ?></div>
            <div class="text-sm text-gray-500">مقالات</div>
        </div>
        <div class="bg-white rounded-xl p-6 text-center shadow-sm card-hover">
            <div class="text-3xl mb-2">👥</div>
            <div class="text-3xl font-bold text-blue-600"><?= number_format($stats['users']) ?></div>
            <div class="text-sm text-gray-500"><?= t('users_count', $lang) ?></div>
        </div>
    </div>
</section>

<!-- Features (expanded) -->
<section class="max-w-7xl mx-auto px-4 py-8">
    <h3 class="text-2xl font-bold text-center mb-6">🌟 قابلیت‌های پلتفرم</h3>
    <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-6 card-hover">
            <div class="text-4xl mb-3">💻</div>
            <h3 class="font-bold text-lg mb-2">پردازش چندرشته‌ای</h3>
            <p class="text-sm text-gray-600">ریاضی، فیزیک، پزشکی، داروسازی، کامپیوتر — همه با هم</p>
        </div>
        <div class="bg-gradient-to-br from-emerald-50 to-green-50 rounded-xl p-6 card-hover">
            <div class="text-4xl mb-3">💬</div>
            <h3 class="font-bold text-lg mb-2">چت بین‌المللی</h3>
            <p class="text-sm text-gray-600">روم‌های موضوعی + چت خصوصی + LaTeX</p>
        </div>
        <div class="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-6 card-hover">
            <div class="text-4xl mb-3">🧮</div>
            <h3 class="font-bold text-lg mb-2">آزمایشگاه مجازی</h3>
            <p class="text-sm text-gray-600">فاکتور، تولید اول، تست قضیه‌ی سینوس</p>
        </div>
        <div class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 card-hover">
            <div class="text-4xl mb-3">🤖</div>
            <h3 class="font-bold text-lg mb-2">AI داخلی</h3>
            <p class="text-sm text-gray-600">دستیار هوشمند، تولید مقاله، ترجمه</p>
        </div>
        <div class="bg-gradient-to-br from-rose-50 to-red-50 rounded-xl p-6 card-hover">
            <div class="text-4xl mb-3">📚</div>
            <h3 class="font-bold text-lg mb-2">آموزش تعاملی</h3>
            <p class="text-sm text-gray-600">درس‌های ریاضی، فیزیک، پزشکی با تمرین</p>
        </div>
        <div class="bg-gradient-to-br from-cyan-50 to-blue-50 rounded-xl p-6 card-hover">
            <div class="text-4xl mb-3">👥</div>
            <h3 class="font-bold text-lg mb-2">شبکه‌ی داوطلبین</h3>
            <p class="text-sm text-gray-600">نرم‌افزار چندسکویی، credit، مدال</p>
        </div>
        <div class="bg-gradient-to-br from-yellow-50 to-amber-50 rounded-xl p-6 card-hover">
            <div class="text-4xl mb-3">🎓</div>
            <h3 class="font-bold text-lg mb-2">موزه‌ی دانشمندان</h3>
            <p class="text-sm text-gray-600">صفحه‌ی چندزبانه برای هر دانشمند</p>
        </div>
        <div class="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-6 card-hover">
            <div class="text-4xl mb-3">🎮</div>
            <h3 class="font-bold text-lg mb-2">بازی‌های علمی</h3>
            <p class="text-sm text-gray-600">شکار اعداد اول، فاکتورزن، مسابقه‌ی روزانه</p>
        </div>
    </div>
</section>

<!-- Math Series -->
<?php if (!empty($series)): ?>
<section class="max-w-7xl mx-auto px-4 py-8">
    <h3 class="text-2xl font-bold text-center mb-6">🧮 <?= t('series_count', $lang) ?></h3>
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        <?php foreach ($series as $s): ?>
        <div class="rounded-xl p-6 text-white card-hover <?= 'gradient-'.$s['color'] ?>">
            <div class="text-4xl mb-2"><?= $s['icon'] ?></div>
            <h4 class="text-xl font-bold"><?= $lang=='fa' ? $s['name'] : ($lang=='ar' ? ($s['name_ar'] ?? $s['name_en']) : $s['name_en']) ?></h4>
            <p class="text-sm opacity-90 mb-2"><?= $lang=='fa' ? $s['description'] : ($s['description_en'] ?? $s['description']) ?></p>
            <?php if ($s['oeis_ref']): ?>
            <a href="https://oeis.org/<?= urlencode($s['oeis_ref']) ?>" target="_blank" class="text-xs bg-white bg-opacity-20 px-2 py-1 rounded">OEIS: <?= $s['oeis_ref'] ?></a>
            <?php endif; ?>
        </div>
        <?php endforeach; ?>
    </div>
</section>
<?php endif; ?>

<!-- Lessons Preview -->
<?php if (!empty($lessons)): ?>
<section class="max-w-7xl mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
        <h3 class="text-2xl font-bold">📚 آموزش‌های ویژه</h3>
        <a href="lessons.php" class="text-blue-600 text-sm">همه‌ی درس‌ها →</a>
    </div>
    <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        <?php foreach ($lessons as $l): ?>
        <a href="lesson.php?slug=<?= urlencode($l['slug']) ?>" class="bg-white rounded-xl shadow p-4 card-hover block">
            <div class="text-3xl mb-2">📘</div>
            <h4 class="font-bold text-sm"><?= sanitize($l['title']) ?></h4>
            <p class="text-xs text-gray-500 mt-1 line-clamp-2"><?= sanitize($l['description']) ?></p>
            <div class="text-xs text-gray-400 mt-2"><?= $l['duration_minutes'] ?> دقیقه • <?= $l['difficulty'] ?></div>
        </a>
        <?php endforeach; ?>
    </div>
</section>
<?php endif; ?>

<!-- Range Progress -->
<section class="max-w-7xl mx-auto px-4 py-8">
    <h3 class="text-2xl font-bold text-center mb-6">📈 پیشرفت بازه‌ها</h3>
    <div class="bg-white rounded-xl shadow-sm p-6">
        <?php foreach ($ranges as $r): ?>
        <div class="mb-4">
            <div class="flex items-center justify-between mb-1">
                <div class="flex items-center gap-2">
                    <span class="px-2 py-1 rounded text-xs <?= $r['complete'] ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700' ?>">
                        <?= $r['complete'] ? '✅ '.t('range_complete',$lang) : '⏳ '.t('range_in_progress',$lang) ?>
                    </span>
                    <span class="font-mono text-sm" dir="ltr"><?= $r['range'] ?></span>
                    <span class="text-xs text-gray-400">(<?= $r['digits'] ?> <?= t('digits',$lang) ?>)</span>
                </div>
                <span class="text-sm text-gray-500" dir="ltr"><?= $r['primes'] > 0 ? number_format($r['primes']).' '.t('primes',$lang) : '—' ?></span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-blue-600 h-2 rounded-full progress-bar" style="width: <?= $r['complete'] ? 100 : 30 ?>%"></div>
            </div>
        </div>
        <?php endforeach; ?>
    </div>
</section>

<!-- Quick Access -->
<section class="max-w-7xl mx-auto px-4 py-8">
    <h3 class="text-2xl font-bold text-center mb-6">⚡ دسترسی سریع</h3>
    <div class="grid md:grid-cols-3 lg:grid-cols-4 gap-4">
        <a href="factor.php" class="bg-white rounded-xl p-5 text-center card-hover shadow"><div class="text-4xl mb-2">🧮</div><div class="font-bold text-blue-700">آزمایشگاه</div></a>
        <a href="lessons.php" class="bg-white rounded-xl p-5 text-center card-hover shadow"><div class="text-4xl mb-2">📚</div><div class="font-bold text-emerald-700">آموزش</div></a>
        <a href="magazine.php" class="bg-white rounded-xl p-5 text-center card-hover shadow"><div class="text-4xl mb-2">📰</div><div class="font-bold text-amber-700">مجله</div></a>
        <a href="chat.php" class="bg-white rounded-xl p-5 text-center card-hover shadow"><div class="text-4xl mb-2">💬</div><div class="font-bold text-purple-700">چت</div></a>
        <a href="ai/chat.php" class="bg-white rounded-xl p-5 text-center card-hover shadow"><div class="text-4xl mb-2">🤖</div><div class="font-bold text-rose-700">AI</div></a>
        <a href="network.php" class="bg-white rounded-xl p-5 text-center card-hover shadow"><div class="text-4xl mb-2">👥</div><div class="font-bold text-cyan-700">شبکه داوطلبین</div></a>
        <a href="scientists.php" class="bg-white rounded-xl p-5 text-center card-hover shadow"><div class="text-4xl mb-2">🎓</div><div class="font-bold text-indigo-700">دانشمندان</div></a>
        <a href="download.php" class="bg-white rounded-xl p-5 text-center card-hover shadow"><div class="text-4xl mb-2">📥</div><div class="font-bold text-emerald-700">نرم‌افزار</div></a>
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

<footer class="mt-auto bg-slate-900 text-slate-300 py-6">
    <div class="max-w-7xl mx-auto px-4">
        <div class="grid md:grid-cols-3 gap-6">
            <div>
                <h4 class="font-bold text-white mb-2"><?= t('title', $lang) ?></h4>
                <p class="text-xs text-slate-400"><?= t('subtitle', $lang) ?></p>
                <p class="text-xs mt-2">🎓 <?= t('dedicated', $lang) ?> (1380-1429)</p>
            </div>
            <div>
                <h4 class="font-bold text-white mb-2">🔗 لینک‌ها</h4>
                <div class="text-xs space-y-1">
                    <a href="factor.php" class="block hover:text-white">🧮 آزمایشگاه</a>
                    <a href="lessons.php" class="block hover:text-white">📚 آموزش</a>
                    <a href="magazine.php" class="block hover:text-white">📰 مجله</a>
                    <a href="chat.php" class="block hover:text-white">💬 چت</a>
                    <a href="ai/chat.php" class="block hover:text-white">🤖 AI</a>
                    <a href="network.php" class="block hover:text-white">👥 شبکه‌ی داوطلبین</a>
                </div>
            </div>
            <div>
                <h4 class="font-bold text-white mb-2">🌐 منابع</h4>
                <div class="text-xs space-y-1">
                    <a href="https://factordb.com" class="block hover:text-white">FactorDB</a>
                    <a href="https://oeis.org" class="block hover:text-white">OEIS</a>
                    <a href="https://www.mersenne.org" class="block hover:text-white">GIMPS</a>
                    <a href="admin/" class="block hover:text-white">🔐 پنل مدیریت</a>
                    <a href="api.php" class="block hover:text-white">🔌 API</a>
                </div>
            </div>
        </div>
        <hr class="my-4 border-slate-700">
        <p class="text-center text-xs text-slate-500"><?= t('copyright', $lang) ?></p>
    </div>
</footer>

</body>
</html>
