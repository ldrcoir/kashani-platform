<?php
require_once __DIR__ . "/functions.php";
secure_session_start();
$slug = $_GET["slug"] ?? "";
if (!$slug) { header("Location: magazine.php"); exit; }
$pdo = Database::getInstance();
$stmt = $pdo->prepare("SELECT a.*, u.name as author_name FROM articles a LEFT JOIN users u ON a.author_id = u.id WHERE a.slug = ? AND a.is_published = 1");
$stmt->execute([$slug]);
$article = $stmt->fetch();
if (!$article) { http_response_code(404); die("<h1>404</h1>"); }
$pdo->prepare("UPDATE articles SET views = views + 1 WHERE id = ?")->execute([$article["id"]]);
$lang = $_GET["lang"] ?? $_COOKIE["lang"] ?? "fa";
$dir = in_array($lang, ["fa","ar","ur"]) ? "rtl" : "ltr";
$comments = $pdo->prepare("SELECT c.*, u.name as user_name FROM comments c JOIN users u ON c.user_id = u.id WHERE c.article_id = ? AND c.is_approved = 1 ORDER BY c.created_at");
$comments->execute([$article["id"]]);
$comments = $comments->fetchAll();
$user = current_user();
?>
<!DOCTYPE html><html lang="<?= $lang ?>" dir="<?= $dir ?>"><head>
<meta charset="UTF-8"><title><?= sanitize($article["title"]) ?></title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.min.js"></script>
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}.article-content p{margin-bottom:1em;line-height:1.8}.article-content h2{font-weight:bold;font-size:1.5em;margin-top:1.5em}.article-content code{background:#f3f4f6;padding:2px 4px;border-radius:3px;direction:ltr}.article-content pre{background:#1e293b;color:#e2e8f0;padding:1em;border-radius:8px;direction:ltr}</style>
</head><body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50"><div class="max-w-3xl mx-auto px-4 py-3 flex justify-between"><a href="magazine.php" class="text-sm text-gray-600">← بازگشت</a><a href="index.php" class="text-sm text-gray-600">🏠</a></div></header>
<article class="max-w-3xl mx-auto p-4">
<h1 class="text-3xl font-bold mb-2 text-gray-900"><?= sanitize($article["title"]) ?></h1>
<div class="flex items-center gap-3 text-sm text-gray-500 mb-6 border-b pb-3">
<?php if ($article["author_name"]): ?><span>✍️ <?= sanitize($article["author_name"]) ?></span><?php endif; ?>
<span>📅 <?= date("Y/m/d", strtotime($article["created_at"])) ?></span>
<span>👁️ <?= number_format($article["views"]) ?></span>
</div>
<div class="article-content prose max-w-none"><?= sanitize_html($article["content"]) ?></div>
<section class="mt-8 bg-white rounded-xl shadow p-5">
<h2 class="font-bold text-lg mb-3">💬 نظرات (<?= count($comments) ?>)</h2>
<?php if (empty($comments)): ?><p class="text-sm text-gray-400 mb-3">اولین نظر را ثبت کنید</p>
<?php else: foreach ($comments as $c): ?>
<div class="border-r-2 border-gray-200 pr-3 py-2"><div class="font-medium text-sm"><?= sanitize($c["user_name"]) ?></div><div class="text-sm"><?= sanitize($c["content"]) ?></div></div>
<?php endforeach; endif; ?>
</section>
</article></body></html>