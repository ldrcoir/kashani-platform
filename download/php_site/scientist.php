<?php
// ============================================================
// scientist.php — صفحه‌ی یک دانشمند
// ============================================================
require_once __DIR__ . '/functions.php';
secure_session_start();
$slug = $_GET['slug'] ?? '';
if (!$slug) { header('Location: scientists.php'); exit; }
$pdo = Database::getInstance();
$stmt = $pdo->prepare("SELECT * FROM scientists WHERE slug = ?");
$stmt->execute([$slug]);
$s = $stmt->fetch();
if (!$s) { http_response_code(404); die('<h1>404 — دانشمند یافت نشد</h1>'); }
$lang = $_GET['lang'] ?? $_COOKIE['lang'] ?? 'fa';
$dir = in_array($lang, ['fa','ar','ur']) ? 'rtl' : 'ltr';
$name_field = "name_$lang"; $full_field = "full_name_$lang"; $bio_field = "bio_$lang"; $ach_field = "achievements_$lang";
$name = $s[$name_field] ?? $s['name_en'];
$full = $s[$full_field] ?? $s['full_name_en'];
$bio = $s[$bio_field] ?? $s['bio_en'] ?? $s['bio_fa'] ?? '';
$ach = $s[$ach_field] ?? $s['achievements_en'] ?? '';
?>
<!DOCTYPE html>
<html lang="<?= $lang ?>" dir="<?= $dir ?>">
<head>
<meta charset="UTF-8">
    <link rel="canonical" href="<?= site_url() ?>/scientist.php?slug=<?= urlencode($s['slug']) ?>">

<title>🎓 <?= sanitize($name) ?></title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
</head>
<body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-5xl mx-auto px-4 py-3 flex justify-between">
        <a href="scientists.php" class="text-sm text-gray-600">← بازگشت</a>
        <a href="index.php" class="text-sm text-gray-600">🏠</a>
    </div>
</header>
<article class="max-w-5xl mx-auto p-4">
    <div class="bg-gradient-to-br from-<?= $s['color'] ?? 'amber' ?>-100 to-<?= $s['color'] ?? 'amber' ?>-200 rounded-2xl p-8 mb-6 text-center">
        <div class="text-8xl mb-3"><?= $s['icon'] ?? '🎓' ?></div>
        <h1 class="text-3xl font-bold mb-1"><?= sanitize($name) ?></h1>
        <p class="text-lg text-gray-700" dir="ltr"><?= sanitize($full) ?></p>
        <div class="mt-3 flex flex-wrap justify-center gap-2 text-sm">
            <span class="bg-white px-3 py-1 rounded">📚 <?= sanitize($s['field']) ?></span>
            <span class="bg-white px-3 py-1 rounded">📅 قرن <?= $s['century'] ?></span>
            <span class="bg-white px-3 py-1 rounded" dir="ltr"><?= $s['born_year'] ?> - <?= $s['died_year'] ?></span>
            <?php if ($s['born_place']): ?><span class="bg-white px-3 py-1 rounded">🌍 <?= sanitize($s['born_place']) ?></span><?php endif; ?>
        </div>
    </div>
    <div class="bg-white rounded-xl shadow p-6 mb-4">
        <h2 class="text-xl font-bold mb-3">📖 بیوگرافی</h2>
        <p class="text-gray-700 leading-relaxed"><?= sanitize($bio) ?></p>
    </div>
    <?php if ($ach): ?>
    <div class="bg-white rounded-xl shadow p-6 mb-4">
        <h2 class="text-xl font-bold mb-3">🏆 دستاوردها</h2>
        <p class="text-gray-700"><?= sanitize($ach) ?></p>
    </div>
    <?php endif; ?>
    <?php if ($s['oeis_ref']): ?>
    <div class="bg-blue-50 rounded-xl p-4 mb-4 text-center">
        <a href="https://oeis.org/<?= urlencode($s['oeis_ref']) ?>" target="_blank" class="text-blue-700">🔢 OEIS: <?= sanitize($s['oeis_ref']) ?></a>
    </div>
    <?php endif; ?>
</article>
</body>
</html>
