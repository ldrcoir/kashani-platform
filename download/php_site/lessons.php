<?php
// ============================================================
// lessons.php — فهرست درس‌ها (آموزش تعاملی)
// ============================================================
require_once __DIR__ . '/functions.php';
secure_session_start();

$lang = $_GET['lang'] ?? $_COOKIE['lang'] ?? 'fa';
$dir = in_array($lang, ['fa','ar','ur']) ? 'rtl' : 'ltr';

$category = $_GET['category'] ?? '';
$difficulty = $_GET['difficulty'] ?? '';
$search = $_GET['search'] ?? '';
$page = max(1, intval($_GET['page'] ?? 1));
$per_page = 9;
$offset = ($page - 1) * $per_page;

$where = ['is_published = 1'];
$params = [];
if ($category) { $where[] = 'category = ?'; $params[] = $category; }
if ($difficulty) { $where[] = 'difficulty = ?'; $params[] = $difficulty; }
if ($search) { $where[] = '(title LIKE ? OR description LIKE ?)'; $params[] = "%$search%"; $params[] = "%$search%"; }
$where_sql = 'WHERE ' . implode(' AND ', $where);

$pdo = Database::getInstance();
$stmt = $pdo->prepare("SELECT * FROM lessons $where_sql ORDER BY sort_order, created_at DESC LIMIT $per_page OFFSET $offset");
$stmt->execute($params);
$lessons = $stmt->fetchAll();

$total = $pdo->prepare("SELECT COUNT(*) FROM lessons $where_sql");
$total->execute($params);
$total = $total->fetchColumn();

$categories = [
    'math' => ['label' => 'ریاضی', 'icon' => '🔢', 'color' => 'blue'],
    'physics' => ['label' => 'فیزیک', 'icon' => '⚛️', 'color' => 'purple'],
    'medical' => ['label' => 'پزشکی', 'icon' => '⚕️', 'color' => 'rose'],
    'pharmacy' => ['label' => 'داروسازی', 'icon' => '💊', 'color' => 'emerald'],
    'computer' => ['label' => 'کامپیوتر', 'icon' => '💻', 'color' => 'cyan'],
    'science' => ['label' => 'علوم', 'icon' => '🔬', 'color' => 'amber'],
    'general' => ['label' => 'عمومی', 'icon' => '📚', 'color' => 'gray'],
];

$difficulties = [
    'beginner' => ['label' => 'مقدماتی', 'color' => 'green'],
    'intermediate' => ['label' => 'متوسط', 'color' => 'yellow'],
    'advanced' => ['label' => 'پیشرفته', 'color' => 'orange'],
    'expert' => ['label' => 'خبره', 'color' => 'red'],
];
?>
<!DOCTYPE html>
<html lang="<?= $lang ?>" dir="<?= $dir ?>">
<head>
    <meta charset="UTF-8">
    <link rel="canonical" href="<?= site_url() ?>/lessons.php">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📚 آموزش تعاملی</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
    <style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
</head>
<body class="bg-gray-50 min-h-screen">

<header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
        <div class="flex items-center gap-3">
            <span class="text-3xl">📚</span>
            <h1 class="text-xl font-bold">آموزش تعاملی</h1>
        </div>
        <a href="index.php" class="px-4 py-2 bg-gray-100 rounded text-sm">🏠 خانه</a>
    </div>
</header>

<div class="max-w-7xl mx-auto p-4">
    <!-- Hero -->
    <div class="bg-gradient-to-br from-emerald-100 to-cyan-100 rounded-xl p-6 mb-6 text-center">
        <h2 class="text-2xl font-bold mb-2">📚 یاد بگیر، آموزش بده</h2>
        <p class="text-sm text-gray-600">درس‌های تعاملی ریاضی، فیزیک، پزشکی، داروسازی و کامپیوتر با تمرین و راهنمایی</p>
    </div>
    
    <!-- Filters -->
    <form method="get" class="bg-white rounded-xl shadow-sm p-4 mb-4 flex flex-wrap gap-3 items-end">
        <div>
            <label class="block text-xs text-gray-500 mb-1">🔍 جستجو</label>
            <input type="text" name="search" value="<?= sanitize($search) ?>" class="px-3 py-2 border rounded text-sm">
        </div>
        <div>
            <label class="block text-xs text-gray-500 mb-1">دسته</label>
            <select name="category" class="px-3 py-2 border rounded text-sm">
                <option value="">همه</option>
                <?php foreach ($categories as $k=>$c): ?>
                <option value="<?= $k ?>" <?= $category==$k?'selected':'' ?>><?= $c['icon'] ?> <?= $c['label'] ?></option>
                <?php endforeach; ?>
            </select>
        </div>
        <div>
            <label class="block text-xs text-gray-500 mb-1">سطح</label>
            <select name="difficulty" class="px-3 py-2 border rounded text-sm">
                <option value="">همه</option>
                <?php foreach ($difficulties as $k=>$d): ?>
                <option value="<?= $k ?>" <?= $difficulty==$k?'selected':'' ?>><?= $d['label'] ?></option>
                <?php endforeach; ?>
            </select>
        </div>
        <button class="bg-blue-600 text-white px-4 py-2 rounded text-sm">🔍 فیلتر</button>
        <a href="lessons.php" class="px-4 py-2 bg-gray-100 rounded text-sm">پاک</a>
    </form>
    
    <!-- Lessons grid -->
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        <?php if (empty($lessons)): ?>
        <div class="col-span-full bg-white rounded-xl shadow-sm p-8 text-center text-gray-500">
            <div class="text-5xl mb-3">📭</div>
            <p>درسی یافت نشد. <a href="admin/lessons.php?action=new" class="text-blue-600">درس جدید بسازید (ادمین)</a></p>
        </div>
        <?php else: foreach ($lessons as $l): 
            $cat = $categories[$l['category']] ?? $categories['general'];
            $diff = $difficulties[$l['difficulty']] ?? $difficulties['beginner'];
        ?>
        <a href="lesson.php?slug=<?= urlencode($l['slug']) ?>" class="bg-white rounded-xl shadow-sm p-5 card-hover block">
            <div class="flex items-center gap-2 mb-3">
                <span class="text-3xl"><?= $cat['icon'] ?></span>
                <div>
                    <span class="text-xs bg-<?= $cat['color'] ?>-100 text-<?= $cat['color'] ?>-700 px-2 py-1 rounded"><?= $cat['label'] ?></span>
                    <span class="text-xs bg-<?= $diff['color'] ?>-100 text-<?= $diff['color'] ?>-700 px-2 py-1 rounded mr-1"><?= $diff['label'] ?></span>
                </div>
            </div>
            <h3 class="font-bold text-lg mb-2"><?= sanitize($l['title']) ?></h3>
            <p class="text-sm text-gray-600 line-clamp-2 mb-3"><?= sanitize($l['description']) ?></p>
            <div class="flex justify-between text-xs text-gray-400">
                <span>⏱️ <?= $l['duration_minutes'] ?> دقیقه</span>
                <span>👁️ <?= number_format($l['views']) ?> • ✓ <?= number_format($l['completions']) ?></span>
            </div>
        </a>
        <?php endforeach; endif; ?>
    </div>
    
    <?php if ($total > $per_page): ?>
    <div class="mt-6 flex justify-center gap-2">
        <?php for ($i = 1; $i <= ceil($total / $per_page); $i++): ?>
        <a href="?page=<?= $i ?>&category=<?= urlencode($category) ?>&difficulty=<?= urlencode($difficulty) ?>&search=<?= urlencode($search) ?>" 
           class="px-3 py-1 rounded <?= $i==$page?'bg-blue-600 text-white':'bg-white' ?>"><?= $i ?></a>
        <?php endfor; ?>
    </div>
    <?php endif; ?>
</div>

</body>
</html>
