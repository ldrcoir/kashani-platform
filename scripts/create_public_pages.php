<?php
// article.php, scientists.php, scientist.php, network.php, download.php, chat.php, api.php
// همه‌ی این‌ها رو در یک فایل script بسازیم

// Create article.php
$article_php = '<?php
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
<style>body{font-family:"Vazirmatn",Tahoma,sans-serif}.article-content p{margin-bottom:1em;line-height:1.8}.article-content h2{font-weight:bold;font-size:1.5em;margin-top:1.5em}.article-content code{background:#f3f4f6;padding:2px 4px;border-radius:3px;direction:ltr}.article-content pre{background:#1e293b;color:#e2e8f0;padding:1em;border-radius:8px;direction:ltr}</style>
</head><body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50"><div class="max-w-3xl mx-auto px-4 py-3 flex justify-between"><a href="magazine.php" class="text-sm text-gray-600">← بازگشت</a><a href="index.php" class="text-sm text-gray-600">🏠</a></div></header>
<article class="max-w-3xl mx-auto p-4">
<h1 class="text-3xl font-bold mb-2 text-gray-900"><?= sanitize($article["title"]) ?></h1>
<div class="flex items-center gap-3 text-sm text-gray-500 mb-6 border-b pb-3">
<?php if ($article["author_name"]): ?><span>✍️ <?= sanitize($article["author_name"]) ?></span><?php endif; ?>
<span>📅 <?= date("Y/m/d", strtotime($article["created_at"])) ?></span>
<span>👁️ <?= number_format($article["views"]) ?></span>
<?php if ($article["is_ai"]): ?><span class="bg-purple-100 text-purple-700 px-2 py-1 rounded">🤖 AI</span><?php endif; ?>
</div>
<?php if ($article["excerpt"]): ?><p class="text-lg text-gray-600 mb-6 italic"><?= sanitize($article["excerpt"]) ?></p><?php endif; ?>
<div class="article-content prose max-w-none"><?= sanitize_html($article["content"]) ?></div>
<?php if ($article["tags"]): ?>
<div class="mt-6 flex flex-wrap gap-2"><?php foreach (explode(",", $article["tags"]) as $tag): ?><span class="text-xs bg-gray-100 px-2 py-1 rounded">#<?= sanitize(trim($tag)) ?></span><?php endforeach; ?></div>
<?php endif; ?>
<section class="mt-8 bg-white rounded-xl shadow p-5">
<h2 class="font-bold text-lg mb-3">💬 نظرات (<?= count($comments) ?>)</h2>
<?php if (empty($comments)): ?><p class="text-sm text-gray-400 mb-3">اولین نظر را ثبت کنید</p>
<?php else: foreach ($comments as $c): ?>
<div class="border-r-2 border-gray-200 pr-3 py-2"><div class="font-medium text-sm"><?= sanitize($c["user_name"]) ?> <span class="text-xs text-gray-400"><?= date("Y/m/d", strtotime($c["created_at"])) ?></span></div><div class="text-sm"><?= sanitize($c["content"]) ?></div></div>
<?php endforeach; endif; ?>
<?php if ($user): ?>
<form method="post" action="api.php" class="mt-3">
<input type="hidden" name="action" value="comment_article">
<input type="hidden" name="csrf_token" value="<?= csrf_token() ?>">
<input type="hidden" name="article_id" value="<?= $article["id"] ?>">
<textarea name="content" rows="2" placeholder="نظر شما..." class="w-full px-3 py-2 border rounded text-sm" required></textarea>
<button class="mt-2 bg-blue-600 text-white px-4 py-1 rounded text-sm">ارسال</button>
</form>
<?php else: ?><p class="text-sm text-gray-500">برای نظر دادن <a href="auth/phone.php" class="text-blue-600">وارد شوید</a></p><?php endif; ?>
</section>
</article>
</body></html>';
file_put_contents('/home/z/my-project/download/php_site/article.php', $article_php);
echo "✓ article.php\n";

// scientists.php
$scientists_php = '<?php
require_once __DIR__ . "/functions.php";
secure_session_start();
$lang = $_GET["lang"] ?? $_COOKIE["lang"] ?? "fa";
$dir = in_array($lang, ["fa","ar","ur"]) ? "rtl" : "ltr";
$pdo = Database::getInstance();
try { $scientists = $pdo->query("SELECT * FROM scientists ORDER BY sort_order, century")->fetchAll(); } catch (Exception $e) { $scientists = []; }
?>
<!DOCTYPE html><html lang="<?= $lang ?>" dir="<?= $dir ?>"><head>
<meta charset="UTF-8"><title>🎓 دانشمندان</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:"Vazirmatn",Tahoma,sans-serif}</style>
</head><body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50"><div class="max-w-7xl mx-auto px-4 py-3 flex justify-between"><div class="flex items-center gap-3"><span class="text-3xl">🎓</span><h1 class="text-xl font-bold">موزه‌ی دانشمندان</h1></div><a href="index.php" class="px-4 py-2 bg-gray-100 rounded text-sm">🏠 خانه</a></div></header>
<div class="max-w-7xl mx-auto p-4">
<div class="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-6 mb-6 text-center">
<h2 class="text-2xl font-bold mb-2">🎓 دانشمندان پارسی-اسلامی</h2>
<p class="text-sm text-gray-600">از خوارزمی تا کاشانی، از ابن‌سینا تا رازی...</p>
</div>
<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
<?php if (empty($scientists)): ?>
<div class="col-span-full bg-white rounded-xl shadow p-8 text-center text-gray-500"><div class="text-5xl mb-3">📭</div><p>دانشمندان در حال بارگذاری...</p></div>
<?php else: foreach ($scientists as $s): $name_field = "name_$lang"; $bio_field = "bio_$lang"; $name = $s[$name_field] ?? $s["name_en"]; $bio = $s[$bio_field] ?? $s["bio_en"] ?? $s["bio_fa"] ?? ""; ?>
<a href="scientist.php?slug=<?= urlencode($s["slug"]) ?>" class="bg-white rounded-xl shadow-sm p-5 hover:shadow-md block">
<div class="flex items-center gap-3 mb-3"><span class="text-4xl"><?= $s["icon"] ?? "🎓" ?></span><div><h3 class="font-bold"><?= sanitize($name) ?></h3><p class="text-xs text-gray-400" dir="ltr"><?= sanitize($s["full_name_en"] ?? $s["name_en"]) ?></p></div></div>
<p class="text-sm text-gray-600 mb-3 line-clamp-2"><?= sanitize($bio) ?></p>
<div class="flex justify-between text-xs text-gray-400"><span>📅 <?= $s["born_year"] ?> - <?= $s["died_year"] ?></span><span>🌍 <?= sanitize($s["born_place"]) ?></span></div>
</a>
<?php endforeach; endif; ?>
</div></div></body></html>';
file_put_contents('/home/z/my-project/download/php_site/scientists.php', $scientists_php);
echo "✓ scientists.php\n";

// scientist.php
$scientist_php = '<?php
require_once __DIR__ . "/functions.php";
secure_session_start();
$slug = $_GET["slug"] ?? "";
if (!$slug) { header("Location: scientists.php"); exit; }
$pdo = Database::getInstance();
$stmt = $pdo->prepare("SELECT * FROM scientists WHERE slug = ?"); $stmt->execute([$slug]);
$s = $stmt->fetch();
if (!$s) { http_response_code(404); die("404"); }
$lang = $_GET["lang"] ?? $_COOKIE["lang"] ?? "fa";
$dir = in_array($lang, ["fa","ar","ur"]) ? "rtl" : "ltr";
$name_field = "name_$lang"; $full_field = "full_name_$lang"; $bio_field = "bio_$lang"; $ach_field = "achievements_$lang";
$name = $s[$name_field] ?? $s["name_en"]; $full = $s[$full_field] ?? $s["full_name_en"]; $bio = $s[$bio_field] ?? $s["bio_en"] ?? $s["bio_fa"] ?? ""; $ach = $s[$ach_field] ?? $s["achievements_en"] ?? "";
?>
<!DOCTYPE html><html lang="<?= $lang ?>" dir="<?= $dir ?>"><head>
<meta charset="UTF-8"><title>🎓 <?= sanitize($name) ?></title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:"Vazirmatn",Tahoma,sans-serif}</style>
</head><body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50"><div class="max-w-5xl mx-auto px-4 py-3 flex justify-between"><a href="scientists.php" class="text-sm text-gray-600">← بازگشت</a><a href="index.php" class="text-sm text-gray-600">🏠</a></div></header>
<article class="max-w-5xl mx-auto p-4">
<div class="bg-gradient-to-br from-<?= $s["color"] ?? "amber" ?>-100 to-<?= $s["color"] ?? "amber" ?>-200 rounded-2xl p-8 mb-6 text-center">
<div class="text-8xl mb-3"><?= $s["icon"] ?? "🎓" ?></div>
<h1 class="text-3xl font-bold mb-1"><?= sanitize($name) ?></h1>
<p class="text-lg text-gray-700" dir="ltr"><?= sanitize($full) ?></p>
<div class="mt-3 flex flex-wrap justify-center gap-2 text-sm">
<span class="bg-white px-3 py-1 rounded">📚 <?= sanitize($s["field"]) ?></span>
<span class="bg-white px-3 py-1 rounded">📅 قرن <?= $s["century"] ?></span>
<span class="bg-white px-3 py-1 rounded" dir="ltr"><?= $s["born_year"] ?> - <?= $s["died_year"] ?></span>
<?php if ($s["born_place"]): ?><span class="bg-white px-3 py-1 rounded">🌍 <?= sanitize($s["born_place"]) ?></span><?php endif; ?>
</div></div>
<div class="bg-white rounded-xl shadow p-6 mb-4"><h2 class="text-xl font-bold mb-3">📖 بیوگرافی</h2><p class="text-gray-700 leading-relaxed"><?= sanitize($bio) ?></p></div>
<?php if ($ach): ?><div class="bg-white rounded-xl shadow p-6 mb-4"><h2 class="text-xl font-bold mb-3">🏆 دستاوردها</h2><p class="text-gray-700"><?= sanitize($ach) ?></p></div><?php endif; ?>
<?php if ($s["oeis_ref"]): ?><div class="bg-blue-50 rounded-xl p-4 mb-4 text-center"><a href="https://oeis.org/<?= urlencode($s["oeis_ref"]) ?>" target="_blank" class="text-blue-700">🔢 OEIS: <?= sanitize($s["oeis_ref"]) ?></a></div><?php endif; ?>
</article></body></html>';
file_put_contents('/home/z/my-project/download/php_site/scientist.php', $scientist_php);
echo "✓ scientist.php\n";

// network.php
$network_php = '<?php
require_once __DIR__ . "/functions.php";
secure_session_start();
$lang = $_GET["lang"] ?? $_COOKIE["lang"] ?? "fa";
$dir = in_array($lang, ["fa","ar","ur"]) ? "rtl" : "ltr";
$pdo = Database::getInstance();
$nodes = $pdo->query("SELECT n.*, u.email, u.name as user_name FROM compute_nodes n LEFT JOIN users u ON n.user_id = u.id WHERE n.is_active = 1 ORDER BY n.total_work DESC LIMIT 50")->fetchAll();
$total_work = $pdo->query("SELECT COALESCE(SUM(total_work), 0) FROM compute_nodes")->fetchColumn() ?: 0;
$total_credit = $pdo->query("SELECT COALESCE(SUM(total_credit), 0) FROM compute_nodes")->fetchColumn() ?: 0;
?>
<!DOCTYPE html><html lang="<?= $lang ?>" dir="<?= $dir ?>"><head>
<meta charset="UTF-8"><title>👥 شبکه‌ی داوطلبین</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:"Vazirmatn",Tahoma,sans-serif}</style>
</head><body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50"><div class="max-w-7xl mx-auto px-4 py-3 flex justify-between"><div class="flex items-center gap-3"><span class="text-3xl">👥</span><h1 class="text-xl font-bold">شبکه‌ی داوطلبین</h1></div><a href="index.php" class="px-4 py-2 bg-gray-100 rounded text-sm">🏠 خانه</a></div></header>
<div class="max-w-7xl mx-auto p-4">
<div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
<div class="bg-white rounded-xl p-5 text-center shadow"><div class="text-3xl mb-2">💻</div><div class="text-3xl font-bold text-blue-600"><?= count($nodes) ?></div><div class="text-sm text-gray-500">نود ثبت‌شده</div></div>
<div class="bg-white rounded-xl p-5 text-center shadow"><div class="text-3xl mb-2">🔢</div><div class="text-3xl font-bold text-amber-600"><?= number_format($total_work) ?></div><div class="text-sm text-gray-500">کل کار</div></div>
<div class="bg-white rounded-xl p-5 text-center shadow"><div class="text-3xl mb-2">🏆</div><div class="text-3xl font-bold text-purple-600"><?= number_format($total_credit) ?></div><div class="text-sm text-gray-500">کل credit</div></div>
</div>
<div class="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-6 mb-6">
<h2 class="text-2xl font-bold mb-3">🌍 به شبکه‌ی داوطلبین بپیوندید</h2>
<p class="text-gray-700 mb-4">با نصب نرم‌افزار داوطلبین روی کامپیوتر خود، در پردازش‌های علمی مشارکت کنید.</p>
<a href="download.php" class="inline-block bg-blue-600 text-white px-6 py-2 rounded font-bold">📥 دانلود نرم‌افزار</a>
</div>
<div class="bg-white rounded-xl shadow p-5">
<h2 class="text-xl font-bold mb-4">🏆 برترین‌ها</h2>
<table class="w-full text-sm"><thead class="bg-gray-100 text-xs uppercase"><tr><th class="text-right p-2">#</th><th class="text-right p-2">نام نود</th><th class="text-right p-2">کاربر</th><th class="text-right p-2">کار</th><th class="text-right p-2">credit</th></tr></thead><tbody>
<?php if (empty($nodes)): ?><tr><td colspan="5" class="text-center py-6 text-gray-400">هنوز نودی ثبت نشده</td></tr>
<?php else: foreach ($nodes as $i=>$n): ?>
<tr class="border-b"><td class="p-2 text-xs"><?= $i<3?["🥇","🥈","🥉"][$i]:($i+1) ?></td><td class="p-2 font-medium"><?= sanitize($n["node_name"]) ?></td><td class="p-2 text-xs"><?= sanitize($n["user_name"] ?? $n["email"] ?? "—") ?></td><td class="p-2 font-mono text-xs"><?= number_format($n["total_work"]) ?></td><td class="p-2 text-xs"><?= number_format($n["total_credit"]) ?></td></tr>
<?php endforeach; endif; ?>
</tbody></table></div></div></body></html>';
file_put_contents('/home/z/my-project/download/php_site/network.php', $network_php);
echo "✓ network.php\n";

// download.php
$download_php = '<?php
require_once __DIR__ . "/functions.php";
secure_session_start();
$lang = $_GET["lang"] ?? $_COOKIE["lang"] ?? "fa";
$dir = in_array($lang, ["fa","ar","ur"]) ? "rtl" : "ltr";
?>
<!DOCTYPE html><html lang="<?= $lang ?>" dir="<?= $dir ?>"><head>
<meta charset="UTF-8"><title>📥 دانلود نرم‌افزار</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:"Vazirmatn",Tahoma,sans-serif}</style>
</head><body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50"><div class="max-w-7xl mx-auto px-4 py-3 flex justify-between"><div class="flex items-center gap-3"><span class="text-3xl">📥</span><h1 class="text-xl font-bold">دانلود نرم‌افزار</h1></div><a href="index.php" class="px-4 py-2 bg-gray-100 rounded text-sm">🏠 خانه</a></div></header>
<div class="max-w-4xl mx-auto p-4">
<div class="bg-gradient-to-br from-amber-50 to-rose-50 rounded-xl p-6 mb-6">
<h2 class="text-2xl font-bold mb-2">🚀 نرم‌افزار داوطلبین (Rust)</h2>
<p class="text-sm text-gray-700 mb-4">نرم‌افزار دسکتاپ برای مشارکت در پردازش‌های علمی. چندسکویی (ویندوز، مک، لینوکس) با Rust نوشته شده.</p>
</div>
<div class="grid md:grid-cols-3 gap-4 mb-6">
<a href="#" class="bg-white rounded-xl shadow p-6 text-center"><div class="text-4xl mb-2">🪟</div><h3 class="font-bold text-lg">ویندوز</h3><p class="text-xs text-gray-500 mb-3">Windows 10/11 x64</p><span class="text-sm bg-blue-600 text-white px-4 py-2 rounded inline-block">📥 دانلود</span></a>
<a href="#" class="bg-white rounded-xl shadow p-6 text-center"><div class="text-4xl mb-2">🍎</div><h3 class="font-bold text-lg">macOS</h3><p class="text-xs text-gray-500 mb-3">Universal Binary</p><span class="text-sm bg-blue-600 text-white px-4 py-2 rounded inline-block">📥 دانلود</span></a>
<a href="#" class="bg-white rounded-xl shadow p-6 text-center"><div class="text-4xl mb-2">🐧</div><h3 class="font-bold text-lg">لینوکس</h3><p class="text-xs text-gray-500 mb-3">AppImage + deb</p><span class="text-sm bg-blue-600 text-white px-4 py-2 rounded inline-block">📥 دانلود</span></a>
</div>
<div class="bg-white rounded-xl shadow p-5">
<h3 class="font-bold text-lg mb-2">⚙️ راه‌اندازی</h3>
<ol class="list-decimal mr-5 space-y-1 text-sm"><li>دانلود و اجرا</li><li>با حساب سایت لاگین (یا API key)</li><li>نرم‌افزار خودکار به سرور متصل می‌شود</li><li>کارها به‌صورت خودکار دانلود و پردازش می‌شوند</li><li>credit جمع می‌شود</li></ol>
</div></div></body></html>';
file_put_contents('/home/z/my-project/download/php_site/download.php', $download_php);
echo "✓ download.php\n";

echo "All public pages created\n";
