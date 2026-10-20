<?php
// admin/nodes.php — مدیریت نودها
require_once __DIR__ . '/../functions.php';
secure_session_start();
$user = current_user();
if (!$user || !in_array($user['role'], ['admin', 'superadmin'])) { header('Location: index.php'); exit; }
$pdo = Database::getInstance();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify($_POST['csrf_token'] ?? '') or die('🛡️ CSRF');
    if ($_POST['action'] === 'delete' && $_POST['id']) {
        $pdo->prepare("DELETE FROM compute_nodes WHERE id = ?")->execute([intval($_POST['id'])]);
    }
    header('Location: nodes.php'); exit;
}

try {
    $nodes = $pdo->query("SELECT n.*, u.email, u.name as user_name FROM compute_nodes n LEFT JOIN users u ON n.user_id = u.id ORDER BY n.last_seen DESC")->fetchAll();
    $total_work = $pdo->query("SELECT COALESCE(SUM(total_work), 0) FROM compute_nodes")->fetchColumn() ?: 0;
    $total_credit = $pdo->query("SELECT COALESCE(SUM(total_credit), 0) FROM compute_nodes")->fetchColumn() ?: 0;
} catch (Exception $e) { $nodes = []; $total_work = 0; $total_credit = 0; }
?>
<!DOCTYPE html>
<html lang="fa" dir="rtl"><head>
<meta charset="UTF-8"><title>💻 نودها</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
</head><body class="bg-gray-100 min-h-screen">
<div class="flex">
<aside class="bg-slate-900 text-white w-64 min-h-screen fixed right-0 top-0 bottom-0 p-4 overflow-y-auto">
<div class="mb-6"><h1 class="text-xl font-bold">🔐 پنل مدیریت</h1></div>
<nav class="space-y-1">
<a href="index.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📊 داشبورد</a>
<a href="nodes.php" class="block px-3 py-2 rounded text-sm bg-blue-600">💻 نودها</a>
<a href="work_queue.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">🚀 توزیع کار</a>
<a href="settings.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">⚙️ تنظیمات</a>
<hr class="my-2 border-slate-700"><a href="../" class="block px-3 py-2 rounded text-sm text-slate-300">🏠 سایت</a>
<a href="logout.php" class="block px-3 py-2 rounded text-sm text-red-300">🚪 خروج</a>
</nav></aside>

<main class="flex-1 mr-64 p-6">
<header class="bg-white rounded-xl shadow-sm p-4 mb-6"><h2 class="text-2xl font-bold">💻 نودهای داوطلب</h2></header>

<div class="grid grid-cols-3 gap-4 mb-6">
<div class="bg-white rounded-xl p-4 shadow text-center"><div class="text-3xl font-bold text-blue-600"><?= count($nodes) ?></div><div class="text-xs text-gray-500">کل نودها</div></div>
<div class="bg-white rounded-xl p-4 shadow text-center"><div class="text-3xl font-bold text-amber-600"><?= number_format($total_work) ?></div><div class="text-xs text-gray-500">کل کار</div></div>
<div class="bg-white rounded-xl p-4 shadow text-center"><div class="text-3xl font-bold text-purple-600"><?= number_format($total_credit) ?></div><div class="text-xs text-gray-500">کل credit</div></div>
</div>

<div class="bg-white rounded-xl shadow overflow-x-auto">
<table class="w-full text-sm"><thead class="bg-gray-100 text-xs uppercase"><tr>
<th class="text-right p-2">نام</th><th class="text-right p-2">کاربر</th><th class="text-right p-2">OS</th><th class="text-right p-2">CPU</th><th class="text-right p-2">RAM</th><th class="text-right p-2">کار</th><th class="text-right p-2">credit</th><th class="text-right p-2">آخرین</th><th class="text-right p-2">عملیات</th>
</tr></thead><tbody>
<?php if (empty($nodes)): ?><tr><td colspan="9" class="text-center py-6 text-gray-400">هنوز نودی ثبت نشده</td></tr>
<?php else: foreach ($nodes as $n): ?>
<tr class="border-b hover:bg-gray-50">
<td class="p-2 font-medium"><?= sanitize($n['node_name']) ?></td>
<td class="p-2 text-xs"><?= sanitize($n['user_name'] ?? $n['email'] ?? '—') ?></td>
<td class="p-2 text-xs" dir="ltr"><?= sanitize($n['os']) ?></td>
<td class="p-2 text-xs"><?= $n['cpu_cores'] ?>c</td>
<td class="p-2 text-xs"><?= number_format($n['ram_mb']) ?> MB</td>
<td class="p-2 text-xs font-mono"><?= number_format($n['total_work']) ?></td>
<td class="p-2 text-xs"><?= number_format($n['total_credit']) ?></td>
<td class="p-2 text-xs text-gray-400"><?= $n['last_seen'] ?? '—' ?></td>
<td class="p-2">
<form method="post" onsubmit="return confirm('حذف؟')" class="inline"><?= csrf_field() ?><input type="hidden" name="action" value="delete"><input type="hidden" name="id" value="<?= $n['id'] ?>"><button class="text-red-600 text-xs">🗑️</button></form>
</td></tr>
<?php endforeach; endif; ?>
</tbody></table></div>
</main></div></body></html>
