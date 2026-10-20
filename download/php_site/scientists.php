<?php
// ============================================================
// scientists.php — موزه‌ی دانشمندان
// ============================================================
require_once __DIR__ . '/functions.php';
secure_session_start();
$lang = $_GET['lang'] ?? $_COOKIE['lang'] ?? 'fa';
$dir = in_array($lang, ['fa','ar','ur']) ? 'rtl' : 'ltr';
$pdo = Database::getInstance();
try { $scientists = $pdo->query("SELECT * FROM scientists ORDER BY sort_order, century")->fetchAll(); } catch (Exception $e) { $scientists = []; }
?>
<!DOCTYPE html>
<html lang="<?= $lang ?>" dir="<?= $dir ?>">
<head>
<meta charset="UTF-8">
    <link rel="canonical" href="<?= site_url() ?>/scientists.php">

<title>🎓 موزه‌ی دانشمندان</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
</head>
<body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 py-3 flex justify-between">
        <div class="flex items-center gap-3"><span class="text-3xl">🎓</span><h1 class="text-xl font-bold">موزه‌ی دانشمندان</h1></div>
        <a href="index.php" class="px-4 py-2 bg-gray-100 rounded text-sm">🏠 خانه</a>
    </div>
</header>
<div class="max-w-7xl mx-auto p-4">
    <div class="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-6 mb-6 text-center">
        <h2 class="text-2xl font-bold mb-2">🎓 دانشمندان پارسی-اسلامی</h2>
        <p class="text-sm text-gray-600">از خوارزمی تا کاشانی، از ابن‌سینا تا رازی...</p>
    </div>
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        <?php if (empty($scientists)): ?>
        <div class="col-span-full bg-white rounded-xl shadow p-8 text-center text-gray-500">
            <div class="text-5xl mb-3">📭</div>
            <p>دانشمندان در حال بارگذاری. <a href="install.php" class="text-blue-600">نصب پلتفرم</a></p>
        </div>
        <?php else: foreach ($scientists as $s): 
            $name_field = "name_$lang"; $bio_field = "bio_$lang";
            $name = $s[$name_field] ?? $s['name_en'];
            $bio = $s[$bio_field] ?? $s['bio_en'] ?? $s['bio_fa'] ?? '';
        ?>
        <a href="scientist.php?slug=<?= urlencode($s['slug']) ?>" class="bg-white rounded-xl shadow-sm p-5 hover:shadow-md block">
            <div class="flex items-center gap-3 mb-3">
                <span class="text-4xl"><?= $s['icon'] ?? '🎓' ?></span>
                <div>
                    <h3 class="font-bold"><?= sanitize($name) ?></h3>
                    <p class="text-xs text-gray-400" dir="ltr"><?= sanitize($s['full_name_en'] ?? $s['name_en']) ?></p>
                </div>
            </div>
            <p class="text-sm text-gray-600 mb-3 line-clamp-2"><?= sanitize($bio) ?></p>
            <div class="flex justify-between text-xs text-gray-400">
                <span>📅 <?= $s['born_year'] ?> - <?= $s['died_year'] ?></span>
                <span>🌍 <?= sanitize($s['born_place']) ?></span>
            </div>
        </a>
        <?php endforeach; endif; ?>
    </div>
</div>
</body>
</html>
