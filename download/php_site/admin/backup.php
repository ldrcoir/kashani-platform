<?php
// admin/backup.php
require_once __DIR__ . '/../functions.php';
secure_session_start();
$user = current_user();
if (!$user || !in_array($user['role'], ['admin', 'superadmin'])) { header('Location: index.php'); exit; }
$msg = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify($_POST['csrf_token'] ?? '') or die('🛡️ CSRF');
    $action = $_POST['action'] ?? '';
    if ($action === 'create_backup') {
        $backup_dir = ROOT_DIR . '/backups/';
        if (!is_dir($backup_dir)) @mkdir($backup_dir, 0755, true);
        $filename = 'backup_' . date('Y-m-d_H-i-s') . '.sql';
        $filepath = $backup_dir . $filename;
        try {
            $pdo = Database::getInstance();
            $tables = $pdo->query("SHOW TABLES")->fetchAll(PDO::FETCH_COLUMN);
            $sql = "-- Kashani Platform Backup\n-- Date: " . date('Y-m-d H:i:s') . "\n\n";
            foreach ($tables as $table) {
                $sql .= "DROP TABLE IF EXISTS `$table`;\n";
                $create = $pdo->query("SHOW CREATE TABLE `$table`")->fetch();
                $sql .= $create['Create Table'] . ";\n\n";
                $rows = $pdo->query("SELECT * FROM `$table`");
                $count = 0;
                while ($row = $rows->fetch(PDO::FETCH_ASSOC)) {
                    $values = array_map(fn($v) => $v === null ? 'NULL' : $pdo->quote($v), array_values($row));
                    $sql .= "INSERT INTO `$table` VALUES (" . implode(',', $values) . ");\n";
                    $count++;
                }
                $sql .= "-- $count rows\n\n";
            }
            file_put_contents($filepath, $sql);
            $msg = "✅ پشتیبان ساخته شد: $filename (" . round(filesize($filepath)/1024) . " KB)";
        } catch (Exception $e) {
            $msg = "❌ خطا: " . $e->getMessage();
        }
    }
}
$backup_dir = ROOT_DIR . '/backups/';
$backups = is_dir($backup_dir) ? array_diff(scandir($backup_dir), ['.','..']) : [];
$backups = array_filter($backups, fn($f) => preg_match('/\.sql$/', $f));
rsort($backups);
?>
<!DOCTYPE html>
<html lang="fa" dir="rtl"><head>
<meta charset="UTF-8"><title>💾 پشتیبان</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
</head><body class="bg-gray-100 min-h-screen">
<div class="flex">
<aside class="bg-slate-900 text-white w-64 min-h-screen fixed right-0 top-0 bottom-0 p-4 overflow-y-auto">
<div class="mb-6"><h1 class="text-xl font-bold">🔐 پنل مدیریت</h1></div>
<nav class="space-y-1">
<a href="index.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📊 داشبورد</a>
<a href="settings.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">⚙️ تنظیمات</a>
<a href="backup.php" class="block px-3 py-2 rounded text-sm bg-blue-600">💾 پشتیبان</a>
<hr class="my-2 border-slate-700"><a href="../" class="block px-3 py-2 rounded text-sm text-slate-300">🏠 سایت</a>
<a href="logout.php" class="block px-3 py-2 rounded text-sm text-red-300">🚪 خروج</a>
</nav></aside>

<main class="flex-1 mr-64 p-6">
<header class="bg-white rounded-xl shadow-sm p-4 mb-6"><h2 class="text-2xl font-bold">💾 پشتیبان‌گیری</h2></header>

<?php if ($msg): ?><div class="bg-blue-50 border-r-4 border-blue-500 p-3 rounded mb-4 text-sm"><?= $msg ?></div><?php endif; ?>

<div class="bg-white rounded-xl shadow p-5 mb-4">
<h3 class="font-bold text-lg mb-3">➕ ساخت پشتیبان</h3>
<form method="post"><?= csrf_field() ?><input type="hidden" name="action" value="create_backup"><button class="bg-blue-600 text-white px-6 py-2 rounded text-sm">💾 ساخت پشتیبان</button></form>
</div>

<div class="bg-white rounded-xl shadow p-5">
<h3 class="font-bold text-lg mb-3">📁 پشتیبان‌ها (<?= count($backups) ?>)</h3>
<?php if (empty($backups)): ?><p class="text-gray-400">هنوز پشتیبانی ساخته نشده</p>
<?php else: ?>
<table class="w-full text-sm"><thead class="bg-gray-100 text-xs uppercase"><tr><th class="text-right p-2">نام فایل</th><th class="text-right p-2">حجم</th><th class="text-right p-2">تاریخ</th></tr></thead><tbody>
<?php foreach ($backups as $b): 
$filepath = $backup_dir . $b;
$size = filesize($filepath);
$size_str = $size > 1024*1024 ? round($size/1024/1024, 1) . ' MB' : round($size/1024) . ' KB'; ?>
<tr class="border-b"><td class="p-2 font-mono text-xs" dir="ltr"><?= sanitize($b) ?></td><td class="p-2 text-xs"><?= $size_str ?></td><td class="p-2 text-xs text-gray-400"><?= date('Y/m/d H:i', filemtime($filepath)) ?></td></tr>
<?php endforeach; ?>
</tbody></table>
<?php endif; ?>
</div>
</main></div></body></html>
