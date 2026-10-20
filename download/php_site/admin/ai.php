<?php
// admin/ai.php — مدیریت AI (test, generate, statistics)
require_once __DIR__ . '/../functions.php';
secure_session_start();
$user = current_user();
if (!$user || !in_array($user['role'], ['admin', 'superadmin'])) { header('Location: index.php'); exit; }
$pdo = Database::getInstance();

$msg = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify($_POST['csrf_token'] ?? '') or die('🛡️ CSRF');
    $action = $_POST['action'] ?? '';
    if ($action === 'test_ai') {
        $provider = $_POST['provider'] ?? 'zai';
        $api_key = $_POST['api_key'] ?? '';
        $prompt = $_POST['prompt'] ?? 'Hello!';
        $response = test_ai($provider, $api_key, $prompt);
        $msg = "<pre class='text-xs mt-2 bg-gray-100 p-3 rounded' dir='ltr'>" . htmlspecialchars($response) . "</pre>";
    }
}

function test_ai($provider, $api_key, $prompt) {
    if (!$api_key) return 'No API key';
    $api_url = ''; $headers = ['Content-Type: application/json'];
    if ($provider === 'zai') { $api_url = 'https://api.z.ai/api/paas/v4/chat/completions'; $headers[] = 'Authorization: Bearer ' . $api_key; }
    elseif ($provider === 'openai') { $api_url = 'https://api.openai.com/v1/chat/completions'; $headers[] = 'Authorization: Bearer ' . $api_key; }
    else return 'Unknown provider';
    $payload = json_encode(['model' => 'glm-4.6', 'messages' => [['role' => 'user', 'content' => $prompt]], 'max_tokens' => 200]);
    $ch = curl_init($api_url);
    curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_HTTPHEADER => $headers, CURLOPT_POSTFIELDS => $payload, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 30]);
    $r = curl_exec($ch); $http = curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
    $data = json_decode($r, true);
    return $data['choices'][0]['message']['content'] ?? "HTTP $http: $r";
}

$stats = [
    'convs' => $pdo->query("SELECT COUNT(*) FROM ai_conversations")->fetchColumn(),
    'ai_articles' => $pdo->query("SELECT COUNT(*) FROM articles WHERE is_ai = 1")->fetchColumn(),
    'ai_users' => $pdo->query("SELECT COUNT(*) FROM settings WHERE key_name LIKE 'ai_permission_%' AND value = '1'")->fetchColumn(),
];
$settings = Settings::all();
?>
<!DOCTYPE html>
<html lang="fa" dir="rtl"><head>
<meta charset="UTF-8"><title>🤖 AI</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
</head><body class="bg-gray-100 min-h-screen">
<div class="flex">
<aside class="bg-slate-900 text-white w-64 min-h-screen fixed right-0 top-0 bottom-0 p-4 overflow-y-auto">
<div class="mb-6"><h1 class="text-xl font-bold">🔐 پنل مدیریت</h1></div>
<nav class="space-y-1">
<a href="index.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📊 داشبورد</a>
<a href="articles.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📰 مقالات</a>
<a href="lessons.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📚 درس‌ها</a>
<a href="users.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">👥 کاربران</a>
<a href="settings.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">⚙️ تنظیمات</a>
<a href="ai.php" class="block px-3 py-2 rounded text-sm bg-blue-600">🤖 AI</a>
<hr class="my-2 border-slate-700"><a href="../" class="block px-3 py-2 rounded text-sm text-slate-300">🏠 سایت</a>
<a href="logout.php" class="block px-3 py-2 rounded text-sm text-red-300">🚪 خروج</a>
</nav></aside>

<main class="flex-1 mr-64 p-6">
<header class="bg-white rounded-xl shadow-sm p-4 mb-6"><h2 class="text-2xl font-bold">🤖 مدیریت هوش مصنوعی</h2></header>

<div class="grid grid-cols-3 gap-4 mb-6">
<div class="bg-white rounded-xl p-4 shadow text-center"><div class="text-3xl font-bold text-purple-600"><?= $stats['convs'] ?></div><div class="text-xs text-gray-500">گفتگوها</div></div>
<div class="bg-white rounded-xl p-4 shadow text-center"><div class="text-3xl font-bold text-blue-600"><?= $stats['ai_articles'] ?></div><div class="text-xs text-gray-500">مقالات AI</div></div>
<div class="bg-white rounded-xl p-4 shadow text-center"><div class="text-3xl font-bold text-emerald-600"><?= $stats['ai_users'] ?></div><div class="text-xs text-gray-500">کاربران با AI</div></div>
</div>

<div class="bg-white rounded-xl shadow p-5 mb-4">
<h3 class="font-bold text-lg mb-3">🔬 تست اتصال AI</h3>
<form method="post" class="space-y-3">
<?= csrf_field() ?>
<div class="grid md:grid-cols-2 gap-3">
<div><label class="block text-xs text-gray-500 mb-1">Provider</label><select name="provider" class="w-full px-3 py-2 border rounded text-sm"><option value="zai" <?= ($settings['ai_provider'] ?? '')=='zai'?'selected':'' ?>>Z.ai GLM</option><option value="openai" <?= ($settings['ai_provider'] ?? '')=='openai'?'selected':'' ?>>OpenAI</option></select></div>
<div><label class="block text-xs text-gray-500 mb-1">API Key</label><input type="password" name="api_key" value="<?= sanitize($settings['ai_api_key'] ?? '') ?>" class="w-full px-3 py-2 border rounded text-sm font-mono"></div>
</div>
<div><label class="block text-xs text-gray-500 mb-1">Prompt</label><textarea name="prompt" rows="3" class="w-full px-3 py-2 border rounded text-sm">سلام! خودت رو معرفی کن.</textarea></div>
<button class="bg-purple-600 text-white px-6 py-2 rounded text-sm">🧪 تست</button>
</form>
<?php if ($msg): ?><div class="mt-4"><?= $msg ?></div><?php endif; ?>
</div>

<div class="bg-white rounded-xl shadow p-5 mb-4">
<h3 class="font-bold text-lg mb-3">📚 ساخت محتوا با AI</h3>
<div class="grid grid-cols-2 gap-3">
<a href="articles.php?action=ai" class="bg-purple-100 hover:bg-purple-200 p-4 rounded text-center"><div class="text-3xl mb-2">📰</div><div class="font-bold text-purple-700">ساخت مقاله</div></a>
<a href="lessons.php?action=ai" class="bg-emerald-100 hover:bg-emerald-200 p-4 rounded text-center"><div class="text-3xl mb-2">📚</div><div class="font-bold text-emerald-700">ساخت درس</div></a>
</div>
</div>

<div class="bg-white rounded-xl shadow p-5">
<h3 class="font-bold text-lg mb-3">📖 مستندات</h3>
<div class="text-sm text-gray-600">
<p><strong>API Providers پشتیبانی‌شده:</strong></p>
<ul class="list-disc mr-5 mt-2 space-y-1">
<li><strong>Z.ai GLM-4.6</strong>: <a href="https://z.ai" class="text-blue-600" target="_blank">z.ai</a> — توصیه‌شده برای ایرانی‌ها</li>
<li><strong>OpenAI GPT-4</strong>: <a href="https://platform.openai.com" class="text-blue-600" target="_blank">platform.openai.com</a></li>
<li><strong>Anthropic Claude</strong>: <a href="https://anthropic.com" class="text-blue-600" target="_blank">anthropic.com</a></li>
</ul>
<p class="mt-3">برای فعال‌سازی:</p>
<ol class="list-decimal mr-5 mt-2 space-y-1">
<li>به <a href="settings.php" class="text-blue-600">تنظیمات</a> بروید</li>
<li>قسمت AI — provider و API key را وارد کنید</li>
<li>تست کنید (با این صفحه)</li>
<li>به کاربران AI access بدهید (از <a href="users.php" class="text-blue-600">کاربران</a>)</li>
</ol>
</div>
</div>
</main></div></body></html>
