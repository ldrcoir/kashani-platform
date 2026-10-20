<?php
// ============================================================
// admin/settings.php — تنظیمات کامل پلتفرم
// ============================================================
require_once __DIR__ . '/../functions.php';
secure_session_start();
$user = current_user();
if (!$user || !in_array($user['role'], ['admin', 'superadmin'])) { header('Location: index.php'); exit; }

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify($_POST['csrf_token'] ?? '') or die('🛡️ CSRF');
    $section = $_POST['section'] ?? '';
    
    if ($section === 'site_info') {
        foreach (['fa','en','ar','fr','de','es','ru','zh','tr','ur'] as $l) {
            Settings::set("site_title_$l", $_POST["title_$l"] ?? '');
            Settings::set("site_subtitle_$l", $_POST["subtitle_$l"] ?? '');
        }
        Settings::set('dedicated_to', $_POST['dedicated_to'] ?? '');
        Settings::set('site_url', $_POST['site_url'] ?? '');
        Settings::set('language_default', $_POST['language_default'] ?? 'fa');
        Settings::set('timezone', $_POST['timezone'] ?? 'Asia/Tehran');
    } elseif ($section === 'factordb') {
        Settings::set('factordb_token', $_POST['factordb_token'] ?? '');
        Settings::set('factordb_api', $_POST['factordb_api'] ?? 'https://factordb.com:4059/rpc');
    } elseif ($section === 'auth') {
        Settings::set('google_client_id', $_POST['google_client_id'] ?? '');
        Settings::set('google_client_secret', $_POST['google_client_secret'] ?? '');
        Settings::set('sms_api_key', $_POST['sms_api_key'] ?? '');
        Settings::set('sms_sender', $_POST['sms_sender'] ?? '3000');
    } elseif ($section === 'security') {
        Settings::set('max_login_attempts', $_POST['max_login_attempts'] ?? '5');
        Settings::set('session_lifetime', $_POST['session_lifetime'] ?? '604800');
    } elseif ($section === 'features') {
        Settings::set('magazine_enabled', isset($_POST['magazine_enabled']) ? '1' : '0');
        Settings::set('volunteer_enabled', isset($_POST['volunteer_enabled']) ? '1' : '0');
        Settings::set('chat_enabled', isset($_POST['chat_enabled']) ? '1' : '0');
        Settings::set('games_enabled', isset($_POST['games_enabled']) ? '1' : '0');
        Settings::set('ai_enabled', isset($_POST['ai_enabled']) ? '1' : '0');
        Settings::set('registration_open', isset($_POST['registration_open']) ? '1' : '0');
    } elseif ($section === 'chat') {
        Settings::set('chat_server_url', $_POST['chat_server_url'] ?? '');
        Settings::set('chat_max_message_length', $_POST['chat_max_message_length'] ?? '500');
        Settings::set('chat_rate_limit', $_POST['chat_rate_limit'] ?? '10');
        Settings::set('chat_allow_latex', isset($_POST['chat_allow_latex']) ? '1' : '0');
    } elseif ($section === 'ai_config') {
        Settings::set('ai_provider', $_POST['ai_provider'] ?? 'zai');
        Settings::set('ai_api_key', $_POST['ai_api_key'] ?? '');
        Settings::set('ai_model', $_POST['ai_model'] ?? 'glm-4.6');
        Settings::set('ai_max_tokens', $_POST['ai_max_tokens'] ?? '1000');
        Settings::set('ai_temperature', $_POST['ai_temperature'] ?? '0.7');
        Settings::set('ai_system_prompt', $_POST['ai_system_prompt'] ?? 'تو یک دستیار علمی هستی. به فارسی پاسخ بده. در زمینه‌ی ریاضی، فیزیک، پزشکی، داروسازی، کامپیوتر. مختصر و دقیق باش.');
    } elseif ($section === 'maintenance') {
        Settings::set('maintenance_mode', isset($_POST['maintenance_mode']) ? '1' : '0');
        Settings::set('maintenance_message', $_POST['maintenance_message'] ?? 'در حال به‌روزرسانی');
    }
    audit_log('settings_update', "Section: $section");
    header('Location: settings.php?saved=1'); exit;
}

$settings = Settings::all();
?>
<!DOCTYPE html>
<html lang="fa" dir="rtl"><head>
<meta charset="UTF-8"><title>تنظیمات</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}textarea,input{font-family:inherit}</style>
</head><body class="bg-gray-100 min-h-screen">
<div class="flex">
    <aside class="bg-slate-900 text-white w-64 min-h-screen fixed right-0 top-0 bottom-0 p-4 overflow-y-auto">
        <div class="mb-6"><h1 class="text-xl font-bold">🔐 پنل مدیریت</h1></div>
        <nav class="space-y-1">
            <a href="index.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📊 داشبورد</a>
            <a href="users.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">👥 کاربران</a>
            <a href="articles.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📰 مقالات</a>
            <a href="lessons.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📚 درس‌ها</a>
            <a href="settings.php" class="block px-3 py-2 rounded text-sm bg-blue-600">⚙️ تنظیمات</a>
            <a href="ai.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">🤖 AI</a>
            <a href="backup.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">💾 پشتیبان</a>
            <hr class="my-2 border-slate-700">
            <a href="../" class="block px-3 py-2 rounded text-sm text-slate-300">🏠 سایت</a>
            <a href="logout.php" class="block px-3 py-2 rounded text-sm text-red-300">🚪 خروج</a>
        </nav>
    </aside>
    
    <main class="flex-1 mr-64 p-6">
        <header class="bg-white rounded-xl shadow-sm p-4 mb-6"><h2 class="text-2xl font-bold">⚙️ تنظیمات پلتفرم</h2></header>
        
        <?php if (isset($_GET['saved'])): ?><div class="bg-green-50 border-r-4 border-green-500 text-green-700 p-3 rounded mb-4">✅ ذخیره شد</div><?php endif; ?>
        
        <!-- FactorDB -->
        <div class="bg-white rounded-xl shadow-sm p-5 mb-4">
            <h3 class="font-bold text-lg mb-3">🎯 FactorDB API</h3>
            <form method="post" class="space-y-3">
                <?= csrf_field() ?>
                <input type="hidden" name="section" value="factordb">
                <div><label class="block text-xs text-gray-500 mb-1">FactorDB Token</label><input type="text" name="factordb_token" value="<?= sanitize($settings['factordb_token'] ?? '') ?>" class="w-full px-3 py-2 border rounded text-sm font-mono"></div>
                <div><label class="block text-xs text-gray-500 mb-1">FactorDB API URL</label><input type="text" name="factordb_api" value="<?= sanitize($settings['factordb_api'] ?? 'https://factordb.com:4059/rpc') ?>" class="w-full px-3 py-2 border rounded text-sm font-mono"></div>
                <button class="bg-blue-600 text-white px-6 py-2 rounded text-sm">💾 ذخیره</button>
            </form>
        </div>
        
        <!-- Features -->
        <div class="bg-white rounded-xl shadow-sm p-5 mb-4">
            <h3 class="font-bold text-lg mb-3">✨ قابلیت‌های سایت</h3>
            <form method="post" class="space-y-3">
                <?= csrf_field() ?>
                <input type="hidden" name="section" value="features">
                <div class="grid md:grid-cols-2 gap-3 text-sm">
                    <?php $features = ['magazine_enabled'=>'📰 مجله','volunteer_enabled'=>'👥 شبکه داوطلبین','chat_enabled'=>'💬 چت','games_enabled'=>'🎮 بازی‌ها','ai_enabled'=>'🤖 هوش مصنوعی','registration_open'=>'📝 ثبت‌نام باز'];
                    foreach ($features as $k => $label): ?>
                    <label class="flex items-center gap-2 p-2 border rounded"><input type="checkbox" name="<?= $k ?>" <?= ($settings[$k] ?? '1')==='1'?'checked':'' ?> class="w-5 h-5"><span><?= $label ?></span></label>
                    <?php endforeach; ?>
                </div>
                <button class="bg-blue-600 text-white px-6 py-2 rounded text-sm">💾 ذخیره</button>
            </form>
        </div>
        
        <!-- AI Config -->
        <div class="bg-white rounded-xl shadow-sm p-5 mb-4">
            <h3 class="font-bold text-lg mb-3">🤖 هوش مصنوعی</h3>
            <form method="post" class="space-y-3">
                <?= csrf_field() ?>
                <input type="hidden" name="section" value="ai_config">
                <div class="grid md:grid-cols-2 gap-3">
                    <div><label class="block text-xs text-gray-500 mb-1">Provider</label><select name="ai_provider" class="w-full px-3 py-2 border rounded text-sm">
                        <option value="zai" <?= ($settings['ai_provider'] ?? '')=='zai'?'selected':'' ?>>Z.ai GLM</option>
                        <option value="openai" <?= ($settings['ai_provider'] ?? '')=='openai'?'selected':'' ?>>OpenAI GPT</option>
                        <option value="claude" <?= ($settings['ai_provider'] ?? '')=='claude'?'selected':'' ?>>Anthropic Claude</option>
                        <option value="gemini" <?= ($settings['ai_provider'] ?? '')=='gemini'?'selected':'' ?>>Google Gemini</option>
                    </select></div>
                    <div><label class="block text-xs text-gray-500 mb-1">Model</label><input type="text" name="ai_model" value="<?= sanitize($settings['ai_model'] ?? 'glm-4.6') ?>" class="w-full px-3 py-2 border rounded text-sm"></div>
                    <div><label class="block text-xs text-gray-500 mb-1">API Key</label><input type="password" name="ai_api_key" value="<?= sanitize($settings['ai_api_key'] ?? '') ?>" class="w-full px-3 py-2 border rounded text-sm font-mono"></div>
                    <div><label class="block text-xs text-gray-500 mb-1">Max Tokens</label><input type="number" name="ai_max_tokens" value="<?= sanitize($settings['ai_max_tokens'] ?? '1000') ?>" class="w-full px-3 py-2 border rounded text-sm"></div>
                    <div><label class="block text-xs text-gray-500 mb-1">Temperature</label><input type="number" step="0.1" name="ai_temperature" value="<?= sanitize($settings['ai_temperature'] ?? '0.7') ?>" class="w-full px-3 py-2 border rounded text-sm"></div>
                </div>
                <div><label class="block text-xs text-gray-500 mb-1">System Prompt</label><textarea name="ai_system_prompt" rows="3" class="w-full px-3 py-2 border rounded text-sm"><?= sanitize($settings['ai_system_prompt'] ?? '') ?></textarea></div>
                <button class="bg-blue-600 text-white px-6 py-2 rounded text-sm">💾 ذخیره</button>
            </form>
        </div>
        
        <!-- Site info -->
        <div class="bg-white rounded-xl shadow-sm p-5 mb-4">
            <h3 class="font-bold text-lg mb-3">🌐 اطلاعات سایت</h3>
            <form method="post" class="space-y-3">
                <?= csrf_field() ?>
                <input type="hidden" name="section" value="site_info">
                <div class="grid md:grid-cols-2 gap-3">
                    <?php foreach (['fa'=>'فارسی','en'=>'English','ar'=>'العربية'] as $code => $name): ?>
                    <div class="border rounded p-2">
                        <div class="font-bold text-sm mb-1"><?= $name ?></div>
                        <input type="text" name="title_<?= $code ?>" value="<?= sanitize($settings["site_title_$code"] ?? '') ?>" placeholder="عنوان" class="w-full px-2 py-1 border rounded text-sm mb-1">
                        <input type="text" name="subtitle_<?= $code ?>" value="<?= sanitize($settings["site_subtitle_$code"] ?? '') ?>" placeholder="زیرعنوان" class="w-full px-2 py-1 border rounded text-sm">
                    </div>
                    <?php endforeach; ?>
                </div>
                <div class="grid md:grid-cols-3 gap-3">
                    <div><label class="block text-xs text-gray-500 mb-1">به افتخار</label><input type="text" name="dedicated_to" value="<?= sanitize($settings['dedicated_to'] ?? '') ?>" class="w-full px-3 py-2 border rounded text-sm"></div>
                    <div><label class="block text-xs text-gray-500 mb-1">URL سایت</label><input type="text" name="site_url" value="<?= sanitize($settings['site_url'] ?? '') ?>" class="w-full px-3 py-2 border rounded text-sm" dir="ltr"></div>
                    <div><label class="block text-xs text-gray-500 mb-1">زبان پیش‌فرض</label><select name="language_default" class="w-full px-3 py-2 border rounded text-sm">
                        <?php foreach (['fa'=>'فارسی','en'=>'English','ar'=>'العربية','fr'=>'Français','de'=>'Deutsch','es'=>'Español','ru'=>'Русский','zh'=>'中文','tr'=>'Türkçe','ur'=>'اردو'] as $code=>$n): ?>
                        <option value="<?= $code ?>" <?= $settings['language_default']==$code?'selected':'' ?>><?= $n ?></option>
                        <?php endforeach; ?>
                    </select></div>
                </div>
                <button class="bg-blue-600 text-white px-6 py-2 rounded text-sm">💾 ذخیره</button>
            </form>
        </div>
        
        <!-- Chat -->
        <div class="bg-white rounded-xl shadow-sm p-5 mb-4">
            <h3 class="font-bold text-lg mb-3">💬 چت</h3>
            <form method="post" class="space-y-3">
                <?= csrf_field() ?>
                <input type="hidden" name="section" value="chat">
                <div><label class="block text-xs text-gray-500 mb-1">URL سرور چت (WebSocket)</label><input type="text" name="chat_server_url" value="<?= sanitize($settings['chat_server_url'] ?? '') ?>" placeholder="wss://example.com:8080" class="w-full px-3 py-2 border rounded text-sm font-mono"></div>
                <div class="grid md:grid-cols-2 gap-3">
                    <div><label class="block text-xs text-gray-500 mb-1">حداکثر طول پیام</label><input type="number" name="chat_max_message_length" value="<?= sanitize($settings['chat_max_message_length'] ?? '500') ?>" class="w-full px-3 py-2 border rounded text-sm"></div>
                    <div><label class="block text-xs text-gray-500 mb-1">نرخ پیام (پیام/دقیقه)</label><input type="number" name="chat_rate_limit" value="<?= sanitize($settings['chat_rate_limit'] ?? '10') ?>" class="w-full px-3 py-2 border rounded text-sm"></div>
                </div>
                <label class="flex items-center gap-2"><input type="checkbox" name="chat_allow_latex" <?= ($settings['chat_allow_latex'] ?? '1')==='1'?'checked':'' ?> class="w-5 h-5"><span>اجازه LaTeX</span></label>
                <button class="bg-blue-600 text-white px-6 py-2 rounded text-sm">💾 ذخیره</button>
            </form>
        </div>
    </main>
</div>
</body></html>
