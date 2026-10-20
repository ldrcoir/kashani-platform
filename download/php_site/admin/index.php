<?php
// ============================================================
// admin/index.php — داشبورد پنل ادمین
// ============================================================
require_once __DIR__ . '/../functions.php';
secure_session_start();

$user = current_user();
if (!$user || !in_array($user['role'], ['admin', 'superadmin'])) {
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        csrf_verify($_POST['csrf_token'] ?? '') or die('🛡️ CSRF invalid');
        $email = sanitize_email($_POST['email'] ?? '');
        $password = $_POST['password'] ?? '';
        try {
            $pdo = Database::getInstance();
            $stmt = $pdo->prepare("SELECT * FROM users WHERE email = ? AND role IN ('admin','superadmin')");
            $stmt->execute([$email]);
            $u = $stmt->fetch();
            if ($u && !empty($u['password_hash']) && password_verify($password, $u['password_hash'])) {
                regenerate_session($u['id']);
                audit_log('admin_login', "Email: $email");
                header('Location: index.php'); exit;
            } else { $error = 'ایمیل یا رمز نادرست'; }
        } catch (Exception $e) { $error = 'خطا: ' . $e->getMessage(); }
    }
    ?>
    <!DOCTYPE html>
    <html lang="fa" dir="rtl"><head>
    <meta charset="UTF-8"><title>ورود ادمین</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
    <style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
    </head><body class="bg-gradient-to-br from-slate-900 to-indigo-900 min-h-screen flex items-center justify-center">
        <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
            <div class="text-center mb-6"><div class="text-5xl mb-2">🔐</div><h1 class="text-2xl font-bold">پنل مدیریت</h1></div>
            <?php if (!empty($error)): ?><div class="bg-red-50 border-r-4 border-red-500 text-red-700 p-3 rounded mb-4 text-sm"><?= $error ?></div><?php endif; ?>
            <form method="post" class="space-y-4">
                <?= csrf_field() ?>
                <div><label class="block text-sm font-bold mb-1">ایمیل</label><input type="email" name="email" required class="w-full px-4 py-2 border rounded" dir="ltr"></div>
                <div><label class="block text-sm font-bold mb-1">رمز</label><input type="password" name="password" required class="w-full px-4 py-2 border rounded"></div>
                <button class="w-full bg-blue-600 text-white py-2 rounded">🔓 ورود</button>
            </form>
            <div class="text-center mt-4"><a href="setup.php" class="text-xs text-blue-600">→ ساخت اولین ادمین</a></div>
            <div class="text-center mt-2"><a href="../" class="text-xs text-gray-500">→ سایت</a></div>
        </div>
    </body></html>
    <?php exit;
}

$pdo = Database::getInstance();
try {
    $stats = get_site_stats();
    $user_count = $pdo->query("SELECT COUNT(*) FROM users")->fetchColumn();
    $article_count = $pdo->query("SELECT COUNT(*) FROM articles")->fetchColumn();
    $factor_count = $pdo->query("SELECT COUNT(*) FROM factors")->fetchColumn();
    $lesson_count = $pdo->query("SELECT COUNT(*) FROM lessons")->fetchColumn();
    $series_count = $pdo->query("SELECT COUNT(*) FROM math_series")->fetchColumn();
    $node_count = $pdo->query("SELECT COUNT(*) FROM compute_nodes")->fetchColumn();
    $chat_messages = $pdo->query("SELECT COUNT(*) FROM chat_messages WHERE is_deleted = 0")->fetchColumn();
    $ai_chats = $pdo->query("SELECT COUNT(*) FROM ai_conversations")->fetchColumn();
} catch (Exception $e) {
    $stats = []; $user_count = 0; $article_count = 0; $factor_count = 0; $lesson_count = 0;
    $series_count = 0; $node_count = 0; $chat_messages = 0; $ai_chats = 0;
}
?>
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8"><title>داشبورد</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
    <style>body{font-family:'Vazirmatn',Tahoma,sans-serif}.stat-card{transition:transform 0.2s}.stat-card:hover{transform:translateY(-2px)}</style>
</head>
<body class="bg-gray-100 min-h-screen">
<div class="flex">
    <aside class="bg-slate-900 text-white w-64 min-h-screen fixed right-0 top-0 bottom-0 p-4 overflow-y-auto">
        <div class="mb-6"><h1 class="text-xl font-bold">🔐 پنل مدیریت</h1></div>
        <nav class="space-y-1">
            <a href="index.php" class="block px-3 py-2 rounded text-sm bg-blue-600">📊 داشبورد</a>
            <a href="users.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">👥 کاربران</a>
            <a href="articles.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📰 مقالات</a>
            <a href="lessons.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📚 درس‌ها</a>
            <a href="factors.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">🔢 فاکتورها</a>
            <a href="ranges.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📈 بازه‌ها</a>
            <a href="scientists.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">🎓 دانشمندان</a>
            <a href="chat_rooms.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">💬 چت</a>
            <a href="work_queue.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">🚀 توزیع کار</a>
            <a href="nodes.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">💻 نودها</a>
            <a href="games.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">🎮 بازی‌ها</a>
            <a href="medals.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">🏆 مدال‌ها</a>
            <a href="ai.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">🤖 AI</a>
            <a href="settings.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">⚙️ تنظیمات</a>
            <a href="backup.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">💾 پشتیبان</a>
            <hr class="my-2 border-slate-700">
            <a href="../" class="block px-3 py-2 rounded text-sm text-slate-300">🏠 سایت</a>
            <a href="logout.php" class="block px-3 py-2 rounded text-sm text-red-300">🚪 خروج</a>
        </nav>
    </aside>
    
    <main class="flex-1 mr-64 p-6">
        <header class="bg-white rounded-xl shadow-sm p-4 mb-6 flex justify-between">
            <div><h2 class="text-2xl font-bold text-gray-800">📊 داشبورد</h2><p class="text-sm text-gray-500">خوش آمدید <?= sanitize($user['name'] ?? $user['email']) ?></p></div>
            <div class="text-left"><div class="text-xs text-gray-400">امروز</div><div class="font-bold"><?= date('Y-m-d H:i') ?></div></div>
        </header>
        
        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
            <div class="stat-card bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl p-4 shadow"><div class="text-3xl mb-2">👥</div><div class="text-2xl font-bold"><?= number_format($user_count) ?></div><div class="text-xs opacity-80">کاربر</div></div>
            <div class="stat-card bg-gradient-to-br from-amber-500 to-orange-600 text-white rounded-xl p-4 shadow"><div class="text-3xl mb-2">🏆</div><div class="text-2xl font-bold"><?= number_format($stats['contributions'] ?? 0) ?></div><div class="text-xs opacity-80">مشارکت</div></div>
            <div class="stat-card bg-gradient-to-br from-emerald-500 to-green-600 text-white rounded-xl p-4 shadow"><div class="text-3xl mb-2">🔢</div><div class="text-2xl font-bold"><?= number_format($factor_count) ?></div><div class="text-xs opacity-80">فاکتور</div></div>
            <div class="stat-card bg-gradient-to-br from-purple-500 to-pink-600 text-white rounded-xl p-4 shadow"><div class="text-3xl mb-2">📰</div><div class="text-2xl font-bold"><?= number_format($article_count) ?></div><div class="text-xs opacity-80">مقاله</div></div>
            <div class="stat-card bg-gradient-to-br from-cyan-500 to-blue-600 text-white rounded-xl p-4 shadow"><div class="text-3xl mb-2">📚</div><div class="text-2xl font-bold"><?= number_format($lesson_count) ?></div><div class="text-xs opacity-80">درس</div></div>
            <div class="stat-card bg-gradient-to-br from-rose-500 to-red-600 text-white rounded-xl p-4 shadow"><div class="text-3xl mb-2">💬</div><div class="text-2xl font-bold"><?= number_format($chat_messages) ?></div><div class="text-xs opacity-80">پیام</div></div>
            <div class="stat-card bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-xl p-4 shadow"><div class="text-3xl mb-2">🤖</div><div class="text-2xl font-bold"><?= number_format($ai_chats) ?></div><div class="text-xs opacity-80">گفتگو AI</div></div>
            <div class="stat-card bg-gradient-to-br from-yellow-500 to-amber-600 text-white rounded-xl p-4 shadow"><div class="text-3xl mb-2">💻</div><div class="text-2xl font-bold"><?= number_format($node_count) ?></div><div class="text-xs opacity-80">نود</div></div>
        </div>
        
        <div class="bg-white rounded-xl shadow-sm p-5">
            <h3 class="font-bold text-lg mb-3 text-gray-800">⚡ دسترسی سریع</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <a href="articles.php?action=new" class="bg-blue-50 hover:bg-blue-100 p-4 rounded text-center"><div class="text-2xl mb-1">➕</div><div class="text-sm font-medium text-blue-700">مقاله جدید</div></a>
                <a href="lessons.php?action=new" class="bg-emerald-50 hover:bg-emerald-100 p-4 rounded text-center"><div class="text-2xl mb-1">📘</div><div class="text-sm font-medium text-emerald-700">درس جدید</div></a>
                <a href="settings.php" class="bg-purple-50 hover:bg-purple-100 p-4 rounded text-center"><div class="text-2xl mb-1">⚙️</div><div class="text-sm font-medium text-purple-700">تنظیمات</div></a>
                <a href="backup.php" class="bg-amber-50 hover:bg-amber-100 p-4 rounded text-center"><div class="text-2xl mb-1">💾</div><div class="text-sm font-medium text-amber-700">پشتیبان</div></a>
            </div>
        </div>
    </main>
</div>
</body>
</html>
