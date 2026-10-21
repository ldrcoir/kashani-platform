<?php
require_once __DIR__ . '/functions.php';
secure_session_start();
$lang = $_GET['lang'] ?? $_COOKIE['lang'] ?? 'fa';
$dir = in_array($lang, ['fa','ar','ur']) ? 'rtl' : 'ltr';
$category = $_GET['category'] ?? '';
$where = ['is_published = 1']; $params = [];
if ($category) { $where[] = 'category = ?'; $params[] = $category; }
$where_sql = 'WHERE ' . implode(' AND ', $where);
$pdo = Database::getInstance();
$stmt = $pdo->prepare("SELECT * FROM lessons $where_sql ORDER BY sort_order, created_at DESC LIMIT 30");
$stmt->execute($params);
$lessons = $stmt->fetchAll();
$cats = ['math'=>['ریاضی','🔢'],'physics'=>['فیزیک','⚛️'],'medical'=>['پزشکی','⚕️'],'pharmacy'=>['داروسازی','💊'],'computer'=>['کامپیوتر','💻'],'science'=>['علوم','🔬'],'general'=>['عمومی','📚']];
?>
<!DOCTYPE html>
<html lang="<?= $lang ?>" dir="<?= $dir ?>">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="canonical" href="<?= site_url() ?>/lessons.php">
<title>📚 آموزش</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',sans-serif}.card{transition:all 0.2s}.card:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(0,0,0,0.08)}</style>
</head>
<body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50">
<div class="max-w-6xl mx-auto px-4 py-2 flex justify-between">
<div class="flex items-center gap-2"><span class="text-2xl">📚</span><span class="font-bold text-sm">آموزش</span></div>
<a href="index.php" class="text-xs text-gray-500">🏠 خانه</a>
</div>
</header>
<div class="max-w-6xl mx-auto p-4">
<!-- Category filter — icon-based -->
<div class="flex gap-2 mb-4 flex-wrap">
<?php foreach ($cats as $k=>$c): ?>
<a href="?category=<?= $k ?>" class="px-3 py-1 rounded-full text-xs <?= $category==$k?'bg-blue-600 text-white':'bg-white shadow-sm' ?>"><?= $c[1] ?> <?= $c[0] ?></a>
<?php endforeach; ?>
<a href="lessons.php" class="px-3 py-1 rounded-full text-xs <?= !$category?'bg-blue-600 text-white':'bg-white shadow-sm' ?>">همه</a>
</div>
<!-- Lessons grid — compact -->
<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
<?php if (empty($lessons)): ?>
<div class="col-span-full text-center text-gray-400 py-8">درسی یافت نشد</div>
<?php else: foreach ($lessons as $l): $cat = $cats[$l['category']] ?? $cats['general']; ?>
<a href="lesson.php?slug=<?= urlencode($l['slug']) ?>" class="card bg-white rounded-xl shadow p-3 block">
<div class="text-2xl mb-1"><?= $cat[1] ?></div>
<div class="font-bold text-xs line-clamp-2"><?= sanitize($l['title']) ?></div>
<div class="text-xs text-gray-400 mt-1"><?= $l['duration_minutes'] ?> دقیقه • <?= $l['difficulty'] ?></div>
<div class="flex justify-between text-xs text-gray-400 mt-1"><span>👁️ <?= number_format($l['views']) ?></span><span>✓ <?= number_format($l['completions']) ?></span></div>
</a>
<?php endforeach; endif; ?>
</div>
</div>
</body>
</html>
