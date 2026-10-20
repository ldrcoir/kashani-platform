<?php
// ============================================================
// magazine.php — مجله‌ی علمی
// ============================================================
require_once __DIR__ . '/functions.php';
secure_session_start();
$lang = $_GET['lang'] ?? $_COOKIE['lang'] ?? 'fa';
$dir = in_array($lang, ['fa','ar','ur']) ? 'rtl' : 'ltr';
$category = $_GET['category'] ?? '';
$search = $_GET['search'] ?? '';
$page = max(1, intval($_GET['page'] ?? 1));
$per_page = 9;
$offset = ($page - 1) * $per_page;
$where = ['is_published = 1']; $params = [];
if ($category) { $where[] = 'category = ?'; $params[] = $category; }
if ($search) { $where[] = '(title LIKE ? OR excerpt LIKE ?)'; $params[] = "%$search%"; $params[] = "%$search%"; }
$where_sql = 'WHERE ' . implode(' AND ', $where);
$pdo = Database::getInstance();
$stmt = $pdo->prepare("SELECT * FROM articles $where_sql ORDER BY created_at DESC LIMIT $per_page OFFSET $offset");
$stmt->execute($params);
$articles = $stmt->fetchAll();
$total = $pdo->prepare("SELECT COUNT(*) FROM articles $where_sql"); $total->execute($params); $total = $total->fetchColumn();
$categories = ['math'=>['label'=>'ریاضی','icon'=>'🔢'],'science'=>['label'=>'علوم','icon'=>'🔬'],'medical'=>['label'=>'پزشکی','icon'=>'⚕️'],'pharmacy'=>['label'=>'داروسازی','icon'=>'💊'],'physics'=>['label'=>'فیزیک','icon'=>'⚛️'],'computer'=>['label'=>'کامپیوتر','icon'=>'💻'],'general'=>['label'=>'عمومی','icon'=>'📰']];
?>
<!DOCTYPE html>
<html lang="<?= $lang ?>" dir="<?= $dir ?>"><head>
<meta charset="UTF-8">
    <link rel="canonical" href="<?= site_url() ?>/magazine.php">
<title>📚 مجله</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style></head>
<body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 py-3 flex justify-between">
        <div class="flex items-center gap-3"><span class="text-3xl">📚</span><h1 class="text-xl font-bold">مجله‌ی علمی</h1></div>
        <a href="index.php" class="px-4 py-2 bg-gray-100 rounded text-sm">🏠 خانه</a>
    </div>
</header>
<div class="max-w-7xl mx-auto p-4">
    <form method="get" class="bg-white rounded-xl shadow p-4 mb-4 flex flex-wrap gap-3">
        <div><label class="block text-xs text-gray-500 mb-1">جستجو</label><input type="text" name="search" value="<?= sanitize($search) ?>" class="px-3 py-2 border rounded text-sm"></div>
        <div><label class="block text-xs text-gray-500 mb-1">دسته</label><select name="category" class="px-3 py-2 border rounded text-sm"><option value="">همه</option>
        <?php foreach ($categories as $k=>$c): ?><option value="<?= $k ?>" <?= $category==$k?'selected':'' ?>><?= $c['icon'] ?> <?= $c['label'] ?></option><?php endforeach; ?>
        </select></div>
        <button class="bg-blue-600 text-white px-4 py-2 rounded text-sm">🔍</button>
    </form>
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        <?php if (empty($articles)): ?>
        <div class="col-span-full bg-white rounded-xl shadow p-8 text-center text-gray-500">
            <div class="text-5xl mb-3">📭</div><p>مقاله‌ای یافت نشد. <a href="admin/articles.php?action=new" class="text-blue-600">مقاله جدید</a></p>
        </div>
        <?php else: foreach ($articles as $a): $cat = $categories[$a['category']] ?? $categories['general']; ?>
        <a href="article.php?slug=<?= urlencode($a['slug']) ?>" class="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md block">
            <div class="w-full h-32 bg-gradient-to-br from-blue-100 to-cyan-300 flex items-center justify-center"><span class="text-6xl"><?= $cat['icon'] ?></span></div>
            <div class="p-4">
                <div class="flex items-center gap-2 mb-2"><span class="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded"><?= $cat['icon'] ?> <?= $cat['label'] ?></span><?php if ($a['is_ai']): ?><span class="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">AI</span><?php endif; ?></div>
                <h3 class="font-bold mb-1 line-clamp-2"><?= sanitize($a['title']) ?></h3>
                <p class="text-sm text-gray-500 line-clamp-2 mb-2"><?= sanitize($a['excerpt'] ?: mb_substr(strip_tags($a['content']), 0, 150)) ?></p>
                <div class="flex justify-between text-xs text-gray-400"><span>👁️ <?= number_format($a['views']) ?></span><span><?= date('Y/m/d', strtotime($a['created_at'])) ?></span></div>
            </div>
        </a>
        <?php endforeach; endif; ?>
    </div>
    <?php if ($total > $per_page): ?>
    <div class="mt-6 flex justify-center gap-2"><?php for ($i = 1; $i <= ceil($total / $per_page); $i++): ?><a href="?page=<?= $i ?>&category=<?= urlencode($category) ?>&search=<?= urlencode($search) ?>" class="px-3 py-1 rounded <?= $i==$page?'bg-blue-600 text-white':'bg-white' ?>"><?= $i ?></a><?php endfor; ?></div>
    <?php endif; ?>
</div>
</body></html>
