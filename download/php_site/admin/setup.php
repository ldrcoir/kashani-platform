<?php
// ============================================================
// admin/setup.php — ساخت اولین ادمین
// ============================================================
require_once __DIR__ . '/../functions.php';
secure_session_start();

$pdo = Database::getInstance();
try { $admin_count = $pdo->query("SELECT COUNT(*) FROM users WHERE role IN ('admin','superadmin')")->fetchColumn(); } catch (Exception $e) { $admin_count = 0; }
if ($admin_count > 0) {
    die(' اولین ادمین قبلاً ساخته شده. <a href="index.php">→ ورود</a>');
}

$error = '';
$success = false;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify($_POST['csrf_token'] ?? '') or die('CSRF invalid');
    $name = sanitize_string($_POST['name'] ?? '', 100);
    $email = sanitize_email($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';
    $password2 = $_POST['password2'] ?? '';
    
    if (!$name || !$email || !$password) $error = 'تمام فیلدها الزامی است';
    elseif (strlen($password) < 8) $error = 'رمز حداقل ۸ کاراکتر';
    elseif ($password !== $password2) $error = 'رمز و تکرار یکسان نیست';
    else {
        try {
            $pdo->exec("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) NULL");
            $stmt = $pdo->prepare("INSERT INTO users (email, name, role, password_hash, language, country) VALUES (?, ?, 'superadmin', ?, 'fa', 'Iran')");
            $stmt->execute([$email, $name, password_hash($password, PASSWORD_BCRYPT)]);
            $success = true;
        } catch (Exception $e) { $error = 'خطا: ' . $e->getMessage(); }
    }
}
?>
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>ساخت ادمین</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
    <style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
</head>
<body class="bg-gradient-to-br from-amber-900 to-orange-900 min-h-screen flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-lg w-full">
        <div class="text-center mb-6">
            <div class="text-6xl mb-2">🎓</div>
            <h1 class="text-2xl font-bold text-gray-800">ساخت اولین ادمین</h1>
        </div>
        <?php if ($success): ?>
        <div class="bg-green-50 border-r-4 border-green-500 text-green-700 p-4 rounded mb-4">
            ✅ ادمین ساخته شد! <a href="index.php" class="underline">ورود</a>
        </div>
        <?php else: ?>
        <?php if ($error): ?><div class="bg-red-50 border-r-4 border-red-500 text-red-700 p-3 rounded mb-4 text-sm"><?= $error ?></div><?php endif; ?>
        <form method="post" class="space-y-4">
            <?= csrf_field() ?>
            <div><label class="block text-sm font-bold mb-1">نام</label><input type="text" name="name" required class="w-full px-4 py-2 border rounded"></div>
            <div><label class="block text-sm font-bold mb-1">ایمیل</label><input type="email" name="email" required class="w-full px-4 py-2 border rounded" dir="ltr"></div>
            <div><label class="block text-sm font-bold mb-1">رمز (حداقل ۸)</label><input type="password" name="password" required minlength="8" class="w-full px-4 py-2 border rounded"></div>
            <div><label class="block text-sm font-bold mb-1">تکرار رمز</label><input type="password" name="password2" required class="w-full px-4 py-2 border rounded"></div>
            <button class="w-full bg-gradient-to-r from-amber-600 to-orange-600 text-white py-3 rounded-lg font-bold">🎓 ساخت ادمین</button>
        </form>
        <?php endif; ?>
    </div>
</body>
</html>
