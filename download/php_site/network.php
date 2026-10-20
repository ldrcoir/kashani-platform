<?php
// ============================================================
// network.php — شبکه‌ی داوطلبین
// ============================================================
require_once __DIR__ . '/functions.php';
secure_session_start();
$lang = $_GET['lang'] ?? $_COOKIE['lang'] ?? 'fa';
$dir = in_array($lang, ['fa','ar','ur']) ? 'rtl' : 'ltr';
$pdo = Database::getInstance();
try {
    $nodes = $pdo->query("SELECT n.*, u.email, u.name as user_name FROM compute_nodes n LEFT JOIN users u ON n.user_id = u.id WHERE n.is_active = 1 ORDER BY n.total_work DESC LIMIT 50")->fetchAll();
    $total_work = $pdo->query("SELECT COALESCE(SUM(total_work), 0) FROM compute_nodes")->fetchColumn() ?: 0;
    $total_credit = $pdo->query("SELECT COALESCE(SUM(total_credit), 0) FROM compute_nodes")->fetchColumn() ?: 0;
} catch (Exception $e) { $nodes = []; $total_work = 0; $total_credit = 0; }
?>
<!DOCTYPE html>
<html lang="<?= $lang ?>" dir="<?= $dir ?>">
<head>
<meta charset="UTF-8">
<title>👥 شبکه‌ی داوطلبین</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
</head>
<body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 py-3 flex justify-between">
        <div class="flex items-center gap-3"><span class="text-3xl">👥</span><h1 class="text-xl font-bold">شبکه‌ی داوطلبین</h1></div>
        <a href="index.php" class="px-4 py-2 bg-gray-100 rounded text-sm">🏠 خانه</a>
    </div>
</header>
<div class="max-w-7xl mx-auto p-4">
    <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-white rounded-xl p-5 text-center shadow"><div class="text-3xl mb-2">💻</div><div class="text-3xl font-bold text-blue-600"><?= count($nodes) ?></div><div class="text-sm text-gray-500">نود ثبت‌شده</div></div>
        <div class="bg-white rounded-xl p-5 text-center shadow"><div class="text-3xl mb-2">🔢</div><div class="text-3xl font-bold text-amber-600"><?= number_format($total_work) ?></div><div class="text-sm text-gray-500">کل کار</div></div>
        <div class="bg-white rounded-xl p-5 text-center shadow"><div class="text-3xl mb-2">🏆</div><div class="text-3xl font-bold text-purple-600"><?= number_format($total_credit) ?></div><div class="text-sm text-gray-500">کل credit</div></div>
    </div>
    <div class="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-6 mb-6">
        <h2 class="text-2xl font-bold mb-3">🌍 به شبکه‌ی داوطلبین بپیوندید</h2>
        <p class="text-gray-700 mb-4">با نصب نرم‌افزار داوطلبین روی کامپیوتر خود، در پردازش‌های علمی مشارکت کنید. نرم‌افزار مشخصات سیستم شما را می‌گیرد و کار متناسب به شما می‌دهد.</p>
        <a href="download.php" class="inline-block bg-blue-600 text-white px-6 py-2 rounded font-bold">📥 دانلود نرم‌افزار</a>
    </div>
    <div class="bg-white rounded-xl shadow p-5">
        <h2 class="text-xl font-bold mb-4">🏆 برترین‌ها</h2>
        <table class="w-full text-sm">
            <thead class="bg-gray-100 text-xs uppercase"><tr><th class="text-right p-2">#</th><th class="text-right p-2">نام نود</th><th class="text-right p-2">کاربر</th><th class="text-right p-2">کار</th><th class="text-right p-2">credit</th></tr></thead>
            <tbody>
                <?php if (empty($nodes)): ?><tr><td colspan="5" class="text-center py-6 text-gray-400">هنوز نودی ثبت نشده</td></tr>
                <?php else: foreach ($nodes as $i=>$n): ?>
                <tr class="border-b">
                    <td class="p-2 text-xs"><?= $i<3?['🥇','🥈','🥉'][$i]:($i+1) ?></td>
                    <td class="p-2 font-medium"><?= sanitize($n['node_name']) ?></td>
                    <td class="p-2 text-xs"><?= sanitize($n['user_name'] ?? $n['email'] ?? '—') ?></td>
                    <td class="p-2 font-mono text-xs"><?= number_format($n['total_work']) ?></td>
                    <td class="p-2 text-xs"><?= number_format($n['total_credit']) ?></td>
                </tr>
                <?php endforeach; endif; ?>
            </tbody>
        </table>
    </div>
</div>
</body>
</html>
