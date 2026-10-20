<?php
// profile.php — پروفایل کاربر
require_once __DIR__ . '/functions.php';
secure_session_start();
require_login();
$user = current_user();
$pdo = Database::getInstance();

// آمار کاربر
$my_factors = $pdo->prepare("SELECT COUNT(*) FROM factors WHERE user_id = ?");
$my_factors->execute([$user['id']]);
$my_factors = $my_factors->fetchColumn();

$my_lessons_completed = $pdo->prepare("SELECT COUNT(*) FROM lesson_progress WHERE user_id = ? AND status = 'completed'");
$my_lessons_completed->execute([$user['id']]);
$my_lessons_completed = $my_lessons_completed->fetchColumn();

$my_ai_chats = $pdo->prepare("SELECT COUNT(*) FROM ai_conversations WHERE user_id = ?");
$my_ai_chats->execute([$user['id']]);
$my_ai_chats = $my_ai_chats->fetchColumn();

// Generate API key
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify($_POST['csrf_token'] ?? '') or die('🛡️ CSRF');
    if (($_POST['action'] ?? '') === 'gen_apikey') {
        $key = 'pmp_' . bin2hex(random_bytes(24));
        $pdo->prepare("UPDATE users SET api_key = ? WHERE id = ?")->execute([$key, $user['id']]);
        header('Location: profile.php?apikey=' . urlencode($key)); exit;
    }
}
$user = current_user();
?>
<!DOCTYPE html>
<html lang="fa" dir="rtl"><head>
<meta charset="UTF-8"><title>👤 پروفایل</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
</head><body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-4xl mx-auto px-4 py-3 flex justify-between">
        <div class="flex items-center gap-3"><span class="text-3xl">👤</span><h1 class="text-xl font-bold">پروفایل</h1></div>
        <a href="index.php" class="px-4 py-2 bg-gray-100 rounded text-sm">🏠 خانه</a>
    </div>
</header>

<div class="max-w-4xl mx-auto p-4">
    <div class="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-6 mb-6 text-center">
        <div class="text-6xl mb-3"><?= $user['avatar'] ?? '👤' ?></div>
        <h2 class="text-2xl font-bold"><?= sanitize($user['name'] ?? $user['email']) ?></h2>
        <p class="text-sm text-gray-500"><?= sanitize($user['email'] ?? '—') ?></p>
        <p class="text-xs text-gray-400 mt-1">کشور: <?= sanitize($user['country']) ?> • زبان: <?= sanitize($user['language']) ?></p>
    </div>
    
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-xl p-4 shadow text-center"><div class="text-3xl font-bold text-amber-600"><?= number_format($user['credits']) ?></div><div class="text-xs text-gray-500">credit</div></div>
        <div class="bg-white rounded-xl p-4 shadow text-center"><div class="text-3xl font-bold text-blue-600"><?= $my_factors ?></div><div class="text-xs text-gray-500">فاکتورها</div></div>
        <div class="bg-white rounded-xl p-4 shadow text-center"><div class="text-3xl font-bold text-emerald-600"><?= $my_lessons_completed ?></div><div class="text-xs text-gray-500">درس‌های تکمیل‌شده</div></div>
        <div class="bg-white rounded-xl p-4 shadow text-center"><div class="text-3xl font-bold text-purple-600"><?= $my_ai_chats ?></div><div class="text-xs text-gray-500">گفتگوهای AI</div></div>
    </div>
    
    <div class="bg-white rounded-xl shadow p-5 mb-4">
        <h3 class="font-bold text-lg mb-3">🔑 API Key</h3>
        <p class="text-sm text-gray-500 mb-3">برای استفاده از volunteer-client یا API نیاز به API key دارید.</p>
        <?php if ($user['api_key']): ?>
        <code class="block bg-gray-100 p-3 rounded text-sm font-mono" dir="ltr"><?= sanitize($user['api_key']) ?></code>
        <?php else: ?>
        <form method="post"><?= csrf_field() ?><input type="hidden" name="action" value="gen_apikey"><button class="bg-blue-600 text-white px-4 py-2 rounded text-sm">🔑 ساخت API Key</button></form>
        <?php endif; ?>
        <?php if (isset($_GET['apikey'])): ?>
        <div class="mt-2 bg-yellow-50 border-r-4 border-yellow-500 p-3 rounded text-sm">API key شما: <code class="font-mono" dir="ltr"><?= sanitize($_GET['apikey']) ?></code></div>
        <?php endif; ?>
    </div>
    
    <div class="bg-white rounded-xl shadow p-5">
        <h3 class="font-bold text-lg mb-3">🚀 مشارکت علمی</h3>
        <p class="text-sm text-gray-600 mb-3">برای مشارکت در پردازش‌های علمی:</p>
        <ol class="list-decimal mr-5 space-y-1 text-sm">
            <li><a href="download.php" class="text-blue-600">نرم‌افزار داوطلبین</a> را دانلود کنید</li>
            <li>با API key بالا لاگین کنید</li>
            <li>نرم‌افزار خودکار به سرور متصل می‌شود و کار می‌گیرد</li>
            <li>credit جمع می‌کنید</li>
        </ol>
    </div>
</div>
</body></html>
