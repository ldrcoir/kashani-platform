<?php
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
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="canonical" href="<?= site_url() ?>/scientists.php">
<title>🎓 موزه‌ی دانشمندان</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',sans-serif}.card{transition:all 0.2s}.card:hover{transform:translateY(-3px);box-shadow:0 8px 20px rgba(0,0,0,0.1)}</style>
</head>
<body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50">
<div class="max-w-6xl mx-auto px-4 py-2 flex justify-between">
<div class="flex items-center gap-2"><span class="text-2xl">🎓</span><span class="font-bold text-sm">دانشمندان</span></div>
<a href="index.php" class="text-xs text-gray-500">🏠 خانه</a>
</div>
</header>
<div class="max-w-6xl mx-auto p-4">
<div class="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-4 mb-4 text-center">
<h2 class="text-lg font-bold">🎓 موزه‌ی دانشمندان پارسی و جهانی</h2>
<p class="text-xs text-gray-600">از اقلیدس تا انیشتین، از خوارزمی تا تورینگ</p>
</div>
<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
<?php if (empty($scientists)): ?>
<div class="col-span-full text-center text-gray-400 py-8">هنوز دانشمندی ثبت نشده. <a href="install.php" class="text-blue-600">نصب</a></div>
<?php else: foreach ($scientists as $s):
$name_field = "name_$lang"; $bio_field = "bio_$lang";
$name = $s[$name_field] ?? $s['name_en'];
$bio = $s[$bio_field] ?? $s['bio_en'] ?? $s['bio_fa'] ?? '';
?>
<a href="scientist.php?slug=<?= urlencode($s['slug']) ?>" class="card bg-white rounded-xl shadow p-3 text-center block">
<div class="text-3xl mb-1"><?= $s['icon'] ?? '🎓' ?></div>
<div class="font-bold text-xs"><?= sanitize($name) ?></div>
<div class="text-xs text-gray-400" dir="ltr"><?= sanitize($s['full_name_en'] ?? $s['name_en']) ?></div>
<div class="text-xs text-gray-500 mt-1"><?= sanitize($s['field']) ?></div>
<div class="text-xs text-gray-400"><?= $s['century'] > 0 ? "قرن {$s['century']}" : "ق.م" ?></div>
</a>
<?php endforeach; endif; ?>
</div>
</div>
</body>
</html>
