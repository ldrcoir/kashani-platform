<?php
// ============================================================
// admin/users.php — مدیریت کاربران
// ============================================================
require_once __DIR__ . '/../functions.php';
secure_session_start();
$user = current_user();
if (!$user || !in_array($user['role'], ['admin', 'superadmin'])) { header('Location: index.php'); exit; }
$pdo = Database::getInstance();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify($_POST['csrf_token'] ?? '') or die('🛡️ CSRF');
    $action = $_POST['action'] ?? '';
    $id = intval($_POST['id'] ?? 0);
    if ($action === 'update_role' && $id) {
        $role = $_POST['role'] ?? 'user';
        if (in_array($role, ['user','admin','superadmin'])) {
            $pdo->prepare("UPDATE users SET role = ? WHERE id = ?")->execute([$role, $id]);
            audit_log('user_role_change', "User: $id, Role: $role");
        }
    } elseif ($action === 'delete' && $id && $user['role'] === 'superadmin' && $id != $user['id']) {
        $pdo->prepare("DELETE FROM users WHERE id = ?")->execute([$id]);
        audit_log('user_delete', "User: $id");
    } elseif ($action === 'update_credits' && $id) {
        $credits = intval($_POST['credits'] ?? 0);
        $pdo->prepare("UPDATE users SET credits = ? WHERE id = ?")->execute([$credits, $id]);
    } elseif ($action === 'toggle_ai' && $id) {
        $current = Settings::get("ai_permission_$id", '0');
        Settings::set("ai_permission_$id", $current === '1' ? '0' : '1');
    }
    header('Location: users.php'); exit;
}

$search = $_GET['search'] ?? '';
$role_filter = $_GET['role'] ?? '';
$where = []; $params = [];
if ($search) { $where[] = "(name LIKE ? OR email LIKE ?)"; $params[] = "%$search%"; $params[] = "%$search%"; }
if ($role_filter) { $where[] = "role = ?"; $params[] = $role_filter; }
$where_sql = $where ? 'WHERE ' . implode(' AND ', $where) : '';
$total = $pdo->prepare("SELECT COUNT(*) FROM users $where_sql"); $total->execute($params); $total = $total->fetchColumn();
$stmt = $pdo->prepare("SELECT * FROM users $where_sql ORDER BY created_at DESC LIMIT 50"); $stmt->execute($params);
$users = $stmt->fetchAll();
?>
<!DOCTYPE html>
<html lang="fa" dir="rtl"><head>
<meta charset="UTF-8"><title>👥 کاربران</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
</head><body class="bg-gray-100 min-h-screen">
<div class="flex">
<aside class="bg-slate-900 text-white w-64 min-h-screen fixed right-0 top-0 bottom-0 p-4 overflow-y-auto">
<div class="mb-6"><h1 class="text-xl font-bold">🔐 پنل مدیریت</h1></div>
<nav class="space-y-1">
<a href="index.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📊 داشبورد</a>
<a href="users.php" class="block px-3 py-2 rounded text-sm bg-blue-600">👥 کاربران</a>
<a href="articles.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📰 مقالات</a>
<a href="lessons.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📚 درس‌ها</a>
<a href="settings.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">⚙️ تنظیمات</a>
<hr class="my-2 border-slate-700"><a href="../" class="block px-3 py-2 rounded text-sm text-slate-300">🏠 سایت</a>
<a href="logout.php" class="block px-3 py-2 rounded text-sm text-red-300">🚪 خروج</a>
</nav></aside>

<main class="flex-1 mr-64 p-6">
<header class="bg-white rounded-xl shadow-sm p-4 mb-6"><h2 class="text-2xl font-bold">👥 کاربران (<?= $total ?>)</h2></header>

<form method="get" class="bg-white rounded-xl shadow-sm p-4 mb-4 flex gap-3">
<div><label class="block text-xs text-gray-500 mb-1">جستجو</label><input type="text" name="search" value="<?= sanitize($search) ?>" class="px-3 py-2 border rounded text-sm"></div>
<div><label class="block text-xs text-gray-500 mb-1">نقش</label><select name="role" class="px-3 py-2 border rounded text-sm"><option value="">همه</option><option value="user" <?= $role_filter=='user'?'selected':'' ?>>کاربر</option><option value="admin" <?= $role_filter=='admin'?'selected':'' ?>>ادمین</option><option value="superadmin" <?= $role_filter=='superadmin'?'selected':'' ?>>مدیر کل</option></select></div>
<button class="bg-blue-600 text-white px-4 py-2 rounded text-sm">🔍</button>
</form>

<div class="bg-white rounded-xl shadow-sm overflow-x-auto">
<table class="w-full text-sm"><thead class="bg-gray-100 text-xs uppercase"><tr>
<th class="text-right p-2">#</th><th class="text-right p-2">نام/ایمیل</th><th class="text-right p-2">کشور</th><th class="text-right p-2">نقش</th><th class="text-right p-2">credits</th><th class="text-right p-2">AI</th><th class="text-right p-3">عملیات</th>
</tr></thead><tbody>
<?php foreach ($users as $u): ?>
<tr class="border-b hover:bg-gray-50">
<td class="p-2 text-xs text-gray-400"><?= $u['id'] ?></td>
<td class="p-2"><div class="font-medium"><?= sanitize($u['name'] ?? '(بدون نام)') ?></div><div class="text-xs text-gray-400"><?= sanitize($u['email'] ?? '—') ?></div></td>
<td class="p-2 text-xs"><?= sanitize($u['country'] ?? '—') ?></td>
<td class="p-2">
<form method="post" class="inline"><?= csrf_field() ?><input type="hidden" name="action" value="update_role"><input type="hidden" name="id" value="<?= $u['id'] ?>"><select name="role" onchange="this.form.submit()" class="text-xs px-2 py-1 border rounded"><option value="user" <?= $u['role']=='user'?'selected':'' ?>>کاربر</option><option value="admin" <?= $u['role']=='admin'?'selected':'' ?>>ادمین</option><option value="superadmin" <?= $u['role']=='superadmin'?'selected':'' ?>>مدیر کل</option></select></form>
</td>
<td class="p-2">
<form method="post" class="inline"><?= csrf_field() ?><input type="hidden" name="action" value="update_credits"><input type="hidden" name="id" value="<?= $u['id'] ?>"><input type="number" name="credits" value="<?= $u['credits'] ?>" onchange="this.form.submit()" class="w-20 text-xs px-2 py-1 border rounded"></form>
</td>
<td class="p-2 text-center">
<form method="post"><?= csrf_field() ?><input type="hidden" name="action" value="toggle_ai"><input type="hidden" name="id" value="<?= $u['id'] ?>"><button class="px-2 py-1 rounded text-xs <?= Settings::get("ai_permission_{$u['id']}", '0')==='1'?'bg-green-100 text-green-700':'bg-gray-100 text-gray-500' ?>"><?= Settings::get("ai_permission_{$u['id']}", '0')==='1'?'✓ فعال':'غیرفعال' ?></button></form>
</td>
<td class="p-2">
<?php if ($user['role'] === 'superadmin' && $u['id'] != $user['id']): ?>
<form method="post" onsubmit="return confirm('حذف؟')" class="inline"><?= csrf_field() ?><input type="hidden" name="action" value="delete"><input type="hidden" name="id" value="<?= $u['id'] ?>"><button class="text-red-600 text-xs">🗑️</button></form>
<?php endif; ?>
</td></tr>
<?php endforeach; ?>
</tbody></table></div>
</main></div></body></html>
