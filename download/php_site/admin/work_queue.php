<?php
// admin/work_queue.php — مدیریت توزیع کار (نمایش ساده)
require_once __DIR__ . '/../functions.php';
secure_session_start();
$user = current_user();
if (!$user || !in_array($user['role'], ['admin', 'superadmin'])) { header('Location: index.php'); exit; }
$pdo = Database::getInstance();

// Stats
try {
    $stats = [
        'pending' => $pdo->query("SELECT COUNT(*) FROM work_queue WHERE status='pending'")->fetchColumn(),
        'running' => $pdo->query("SELECT COUNT(*) FROM work_queue WHERE status='running'")->fetchColumn(),
        'completed' => $pdo->query("SELECT COUNT(*) FROM work_queue WHERE status='completed'")->fetchColumn(),
        'failed' => $pdo->query("SELECT COUNT(*) FROM work_queue WHERE status='failed'")->fetchColumn(),
    ];
    $work_types = $pdo->query("SELECT * FROM work_types ORDER BY priority, sort_order")->fetchAll();
    $active_nodes = $pdo->query("SELECT n.*, u.email, u.name as user_name, ns.cpu_model, ns.cpu_cores, ns.ram_total_mb, ns.gpu_model, ns.preferred_work_types FROM compute_nodes n LEFT JOIN users u ON n.user_id = u.id LEFT JOIN node_specs ns ON n.id = ns.node_id WHERE n.last_seen > DATE_SUB(NOW(), INTERVAL 10 MINUTE) ORDER BY n.last_seen DESC")->fetchAll();
} catch (Exception $e) {
    $stats = ['pending' => 0, 'running' => 0, 'completed' => 0, 'failed' => 0];
    $work_types = []; $active_nodes = [];
}
?>
<!DOCTYPE html>
<html lang="fa" dir="rtl"><head>
<meta charset="UTF-8"><title>🚀 توزیع کار</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
</head><body class="bg-gray-100 min-h-screen">
<div class="flex">
<aside class="bg-slate-900 text-white w-64 min-h-screen fixed right-0 top-0 bottom-0 p-4 overflow-y-auto">
<div class="mb-6"><h1 class="text-xl font-bold">🔐 پنل مدیریت</h1></div>
<nav class="space-y-1">
<a href="index.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📊 داشبورد</a>
<a href="nodes.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">💻 نودها</a>
<a href="work_queue.php" class="block px-3 py-2 rounded text-sm bg-blue-600">🚀 توزیع کار</a>
<a href="settings.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">⚙️ تنظیمات</a>
<hr class="my-2 border-slate-700"><a href="../" class="block px-3 py-2 rounded text-sm text-slate-300">🏠 سایت</a>
<a href="logout.php" class="block px-3 py-2 rounded text-sm text-red-300">🚪 خروج</a>
</nav></aside>

<main class="flex-1 mr-64 p-6">
<header class="bg-white rounded-xl shadow-sm p-4 mb-6"><h2 class="text-2xl font-bold">🚀 توزیع کار</h2></header>

<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
<div class="bg-white rounded-xl p-4 shadow text-center"><div class="text-3xl font-bold text-yellow-600"><?= $stats['pending'] ?></div><div class="text-xs text-gray-500">در انتظار</div></div>
<div class="bg-white rounded-xl p-4 shadow text-center"><div class="text-3xl font-bold text-cyan-600"><?= $stats['running'] ?></div><div class="text-xs text-gray-500">در حال اجرا</div></div>
<div class="bg-white rounded-xl p-4 shadow text-center"><div class="text-3xl font-bold text-emerald-600"><?= $stats['completed'] ?></div><div class="text-xs text-gray-500">تکمیل شده</div></div>
<div class="bg-white rounded-xl p-4 shadow text-center"><div class="text-3xl font-bold text-red-600"><?= $stats['failed'] ?></div><div class="text-xs text-gray-500">شکست</div></div>
</div>

<div class="bg-white rounded-xl shadow p-5 mb-4">
<h3 class="font-bold text-lg mb-3">📋 انواع کار (<?= count($work_types) ?>)</h3>
<table class="w-full text-sm"><thead class="bg-gray-100 text-xs uppercase"><tr><th class="text-right p-2">آیکن</th><th class="text-right p-2">نام</th><th class="text-right p-2">دسته</th><th class="text-right p-2">CPU</th><th class="text-right p-2">RAM</th><th class="text-right p-2">GPU</th><th class="text-right p-2">credit</th></tr></thead><tbody>
<?php if (empty($work_types)): ?><tr><td colspan="7" class="text-center py-4 text-gray-400">هنوز نوع کاری تعریف نشده</td></tr>
<?php else: foreach ($work_types as $wt): ?>
<tr class="border-b"><td class="p-2 text-2xl"><?= $wt['icon'] ?></td><td class="p-2"><?= sanitize($wt['name']) ?></td><td class="p-2 text-xs"><?= sanitize($wt['category']) ?></td><td class="p-2 text-xs"><?= $wt['min_cpu_cores'] ?>c</td><td class="p-2 text-xs"><?= $wt['min_ram_mb'] ?>MB</td><td class="p-2 text-xs"><?= $wt['requires_gpu']?'✓':'—' ?></td><td class="p-2 text-xs font-bold"><?= $wt['credit_per_task'] ?></td></tr>
<?php endforeach; endif; ?>
</tbody></table></div>

<div class="bg-white rounded-xl shadow p-5">
<h3 class="font-bold text-lg mb-3">💻 نودهای آنلاین (<?= count($active_nodes) ?>)</h3>
<table class="w-full text-sm"><thead class="bg-gray-100 text-xs uppercase"><tr><th class="text-right p-2">نام</th><th class="text-right p-2">کاربر</th><th class="text-right p-2">CPU</th><th class="text-right p-2">RAM</th><th class="text-right p-2">GPU</th><th class="text-right p-2">ترجیحات</th></tr></thead><tbody>
<?php if (empty($active_nodes)): ?><tr><td colspan="6" class="text-center py-4 text-gray-400">هنوز نودی آنلاین نیست</td></tr>
<?php else: foreach ($active_nodes as $n): ?>
<tr class="border-b"><td class="p-2 font-medium"><?= sanitize($n['node_name']) ?></td><td class="p-2 text-xs"><?= sanitize($n['user_name'] ?? $n['email'] ?? '—') ?></td><td class="p-2 text-xs" dir="ltr"><?= sanitize($n['cpu_model'] ?? '—') ?> (<?= $n['cpu_cores'] ?? '?' ?>c)</td><td class="p-2 text-xs"><?= number_format($n['ram_total_mb'] ?? 0) ?> MB</td><td class="p-2 text-xs" dir="ltr"><?= sanitize($n['gpu_model'] ?? '—') ?></td><td class="p-2 text-xs"><?= sanitize($n['preferred_work_types'] ?? '—') ?></td></tr>
<?php endforeach; endif; ?>
</tbody></table></div>
</main></div></body></html>
