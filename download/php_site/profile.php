<?php
require_once __DIR__ . '/functions.php';
secure_session_start();
require_login();
$user = current_user();
$pdo = Database::getInstance();

// Stats
$my_factors = 0; $my_lessons = 0; $my_ai = 0; $my_medals = 0;
try { $s = $pdo->prepare("SELECT COUNT(*) FROM factors WHERE user_id = ?"); $s->execute([$user['id']]); $my_factors = $s->fetchColumn(); } catch(Exception $e) {}
try { $s = $pdo->prepare("SELECT COUNT(*) FROM lesson_progress WHERE user_id = ? AND status='completed'"); $s->execute([$user['id']]); $my_lessons = $s->fetchColumn(); } catch(Exception $e) {}
try { $s = $pdo->prepare("SELECT COUNT(*) FROM ai_conversations WHERE user_id = ?"); $s->execute([$user['id']]); $my_ai = $s->fetchColumn(); } catch(Exception $e) {}
try { $s = $pdo->prepare("SELECT COUNT(*) FROM user_medals WHERE user_id = ?"); $s->execute([$user['id']]); $my_medals = $s->fetchColumn(); } catch(Exception $e) {}

// API key / profile update
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify($_POST['csrf_token'] ?? '') or die('CSRF');
    if (($_POST['action'] ?? '') === 'gen_apikey') {
        $key = 'pmp_' . bin2hex(random_bytes(24));
        $pdo->prepare("UPDATE users SET api_key = ? WHERE id = ?")->execute([$key, $user['id']]);
        header('Location: profile?apikey=' . urlencode($key)); exit;
    } elseif (($_POST['action'] ?? '') === 'update_profile') {
        $name = sanitize_string($_POST['name'] ?? '', 100);
        $bio = sanitize_string($_POST['bio'] ?? '', 500);
        $avatar = sanitize_url($_POST['avatar'] ?? '');
        $pdo->prepare("UPDATE users SET name = ?, bio = ?, avatar = ? WHERE id = ?")->execute([$name, $bio, $avatar, $user['id']]);
        header('Location: profile?saved=1'); exit;
    }
}
$user = current_user();

// Get medals
$medals = [];
try { $s = $pdo->prepare("SELECT m.*, d.icon, d.name, d.color FROM user_medals m LEFT JOIN medal_definitions d ON m.medal_type = d.slug WHERE m.user_id = ?"); $s->execute([$user['id']]); $medals = $s->fetchAll(); } catch(Exception $e) {}

// Get recent activity
$recent = [];
try { $s = $pdo->prepare("SELECT * FROM factors WHERE user_id = ? ORDER BY created_at DESC LIMIT 10"); $s->execute([$user['id']]); $recent = $s->fetchAll(); } catch(Exception $e) {}
?>
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="canonical" href="<?= site_url() ?>/profile">
<title>👤 پنل کاربری</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>
body{font-family:'Vazirmatn',sans-serif;background:#f1f5f9}
.card{transition:all 0.25s;border-radius:16px}
.card:hover{box-shadow:0 12px 28px rgba(0,0,0,0.08)}
.profile-header{background:linear-gradient(135deg,#4f46e5,#7c3aed,#06b6d4);border-radius:20px}
.avatar-circle{width:80px;height:80px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2rem;background:rgba(255,255,255,0.2);border:3px solid rgba(255,255,255,0.3)}
</style>
</head>
<body class="min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50">
<div class="max-w-4xl mx-auto px-4 py-2 flex justify-between items-center">
<div class="flex items-center gap-2"><span class="text-2xl">👤</span><span class="font-bold text-sm">پنل کاربری</span></div>
<a href="/" class="text-xs text-gray-500">🏠 خانه</a>
</div>
</header>

<div class="max-w-4xl mx-auto p-4">
<!-- Profile Header -->
<div class="profile-header p-6 text-white text-center mb-4">
<div class="avatar-circle mx-auto mb-3">
<?php if ($user['avatar']): ?>
<img src="<?= sanitize($user['avatar']) ?>" class="w-full h-full rounded-full object-cover">
<?php else: ?>
👤
<?php endif; ?>
</div>
<h2 class="text-xl font-bold"><?= sanitize($user['name'] ?? $user['email']) ?></h2>
<p class="text-sm opacity-80"><?= sanitize($user['email'] ?? '') ?></p>
<?php if ($user['bio']): ?><p class="text-sm opacity-70 mt-2 max-w-md mx-auto"><?= sanitize($user['bio']) ?></p><?php endif; ?>
<div class="mt-3 flex justify-center gap-2 text-xs">
<span class="px-3 py-1 rounded-full bg-white/20"><?= sanitize($user['country'] ?? 'Iran') ?></span>
<span class="px-3 py-1 rounded-full bg-white/20"><?= sanitize($user['language'] ?? 'fa') ?></span>
<?php if (in_array($user['role'], ['admin','superadmin'])): ?>
<span class="px-3 py-1 rounded-full bg-amber-500/40">🔐 <?= $user['role'] ?></span>
<?php endif; ?>
</div>
</div>

<!-- Stats Grid -->
<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
<div class="card bg-white p-4 text-center shadow-sm">
<div class="text-2xl mb-1">🏆</div>
<div class="text-3xl font-bold text-amber-600"><?= number_format($user['credits']) ?></div>
<div class="text-xs text-gray-500">credit</div>
</div>
<div class="card bg-white p-4 text-center shadow-sm">
<div class="text-2xl mb-1">🔢</div>
<div class="text-3xl font-bold text-blue-600"><?= $my_factors ?></div>
<div class="text-xs text-gray-500">فاکتور</div>
</div>
<div class="card bg-white p-4 text-center shadow-sm">
<div class="text-2xl mb-1">📚</div>
<div class="text-3xl font-bold text-emerald-600"><?= $my_lessons ?></div>
<div class="text-xs text-gray-500">درس</div>
</div>
<div class="card bg-white p-4 text-center shadow-sm">
<div class="text-2xl mb-1">🏅</div>
<div class="text-3xl font-bold text-purple-600"><?= $my_medals ?></div>
<div class="text-xs text-gray-500">مدال</div>
</div>
</div>

<!-- Notifications -->
<?php if (isset($_GET['apikey'])): ?>
<div class="bg-yellow-50 border-r-4 border-yellow-500 p-3 rounded mb-4 text-sm">🔑 API key: <code class="font-mono break-all" dir="ltr"><?= sanitize($_GET['apikey']) ?></code></div>
<?php endif; ?>
<?php if (isset($_GET['saved'])): ?>
<div class="bg-green-50 border-r-4 border-green-500 p-3 rounded mb-4 text-sm">✅ ذخیره شد</div>
<?php endif; ?>

<!-- Two columns -->
<div class="grid md:grid-cols-2 gap-4">
<!-- Left: Edit + API -->
<div class="space-y-4">
<div class="card bg-white shadow-sm p-5">
<h3 class="font-bold mb-3">📝 ویرایش پروفایل</h3>
<form method="post" class="space-y-3">
<?= csrf_field() ?>
<input type="hidden" name="action" value="update_profile">
<div><label class="block text-xs text-gray-500 mb-1">نام نمایشی</label><input type="text" name="name" value="<?= sanitize($user['name'] ?? '') ?>" class="w-full px-3 py-2 border rounded-lg text-sm"></div>
<div><label class="block text-xs text-gray-500 mb-1">بیوگرافی</label><textarea name="bio" rows="2" class="w-full px-3 py-2 border rounded-lg text-sm"><?= sanitize($user['bio'] ?? '') ?></textarea></div>
<div><label class="block text-xs text-gray-500 mb-1">آواتار (URL — عکس، انیمیشن، آواتار)</label><input type="text" name="avatar" value="<?= sanitize($user['avatar'] ?? '') ?>" placeholder="https://..." class="w-full px-3 py-2 border rounded-lg text-sm" dir="ltr"></div>
<button class="bg-indigo-600 text-white px-6 py-2 rounded-lg text-sm">💾 ذخیره</button>
</form>
</div>

<div class="card bg-white shadow-sm p-5">
<h3 class="font-bold mb-3">🔑 API Key</h3>
<p class="text-xs text-gray-500 mb-2">برای اتصال نرم‌افزار دسکتاپ/اندروید</p>
<?php if ($user['api_key']): ?>
<code class="block bg-gray-100 p-3 rounded-lg text-xs font-mono break-all" dir="ltr"><?= sanitize($user['api_key']) ?></code>
<?php else: ?>
<form method="post"><?= csrf_field() ?><input type="hidden" name="action" value="gen_apikey"><button class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">🔑 ساخت</button></form>
<?php endif; ?>
</div>
</div>

<!-- Right: Medals + Activity -->
<div class="space-y-4">
<div class="card bg-white shadow-sm p-5">
<h3 class="font-bold mb-3">🏆 مدال‌ها (<?= $my_medals ?>)</h3>
<?php if (empty($medals)): ?>
<p class="text-sm text-gray-400">هنوز مدالی ندارید. با فعالیت مدال جمع کنید!</p>
<?php else: ?>
<div class="flex flex-wrap gap-2">
<?php foreach ($medals as $m): ?>
<span class="px-3 py-2 rounded-xl text-xs bg-<?= $m['color'] ?? 'amber' ?>-100 text-<?= $m['color'] ?? 'amber' ?>-700 flex items-center gap-1">
<span class="text-lg"><?= $m['icon'] ?? '🏆' ?></span> <?= sanitize($m['name'] ?? 'مدال') ?>
</span>
<?php endforeach; ?>
</div>
<?php endif; ?>
</div>

<div class="card bg-white shadow-sm p-5">
<h3 class="font-bold mb-3">📊 فعالیت اخیر</h3>
<?php if (empty($recent)): ?>
<p class="text-sm text-gray-400">فعالیتی ثبت نشده</p>
<?php else: ?>
<div class="space-y-2">
<?php foreach ($recent as $r): ?>
<div class="text-xs border-r-2 border-gray-200 pr-2 py-1">
<div class="font-mono text-gray-600" dir="ltr"><?= substr($r['number'], 0, 40) ?>... (<?= $r['digits'] ?> رقم)</div>
<div class="text-gray-400"><?= $r['credited'] ? '+' . $r['credited'] . ' credit' : '' ?> • <?= date('Y/m/d', strtotime($r['created_at'])) ?></div>
</div>
<?php endforeach; ?>
</div>
<?php endif; ?>
</div>

<div class="card bg-white shadow-sm p-5">
<h3 class="font-bold mb-3">📈 خلاصه</h3>
<div class="space-y-1 text-sm">
<div class="flex justify-between"><span>🏅 Credit کل:</span><span class="font-bold"><?= number_format($user['credits']) ?></span></div>
<div class="flex justify-between"><span>🔢 فاکتور:</span><span class="font-bold"><?= $my_factors ?></span></div>
<div class="flex justify-between"><span>📚 درس:</span><span class="font-bold"><?= $my_lessons ?></span></div>
<div class="flex justify-between"><span>🤖 گفتگوی AI:</span><span class="font-bold"><?= $my_ai ?></span></div>
<div class="flex justify-between"><span>🏅 مدال:</span><span class="font-bold"><?= $my_medals ?></span></div>
</div>
</div>
</div>
</div>
</div>
</body>
</html>
