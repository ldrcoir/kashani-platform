<?php
// ============================================================
// admin/articles.php — مدیریت مقالات (با AI)
// ============================================================
require_once __DIR__ . '/../functions.php';
secure_session_start();
$user = current_user();
if (!$user || !in_array($user['role'], ['admin', 'superadmin'])) { header('Location: index.php'); exit; }
$pdo = Database::getInstance();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify($_POST['csrf_token'] ?? '') or die('🛡️ CSRF');
    $action = $_POST['action'] ?? '';
    if ($action === 'save') {
        $id = intval($_POST['id'] ?? 0);
        $title = trim($_POST['title'] ?? '');
        $slug = trim($_POST['slug'] ?? '');
        $excerpt = trim($_POST['excerpt'] ?? '');
        $content = $_POST['content'] ?? '';
        $category = $_POST['category'] ?? 'math';
        $tags = $_POST['tags'] ?? '';
        $image_url = $_POST['image_url'] ?? '';
        $is_published = isset($_POST['is_published']) ? 1 : 0;
        $is_ai = isset($_POST['is_ai']) ? 1 : 0;
        if (empty($slug)) $slug = preg_replace('/[^a-z0-9]+/', '-', strtolower($title)) . '-' . substr(md5(time()), 0, 5);
        if ($id) {
            $stmt = $pdo->prepare("UPDATE articles SET title=?, slug=?, excerpt=?, content=?, category=?, tags=?, image_url=?, is_published=?, is_ai=?, author_id=? WHERE id=?");
            $stmt->execute([$title, $slug, $excerpt, $content, $category, $tags, $image_url, $is_published, $is_ai, $user['id'], $id]);
        } else {
            $stmt = $pdo->prepare("INSERT INTO articles (title, slug, excerpt, content, category, tags, image_url, is_published, is_ai, author_id) VALUES (?,?,?,?,?,?,?,?,?,?)");
            $stmt->execute([$title, $slug, $excerpt, $content, $category, $tags, $image_url, $is_published, $is_ai, $user['id']]);
        }
        header('Location: articles.php?saved=1'); exit;
    } elseif ($action === 'delete') {
        $id = intval($_POST['id']);
        $pdo->prepare("DELETE FROM articles WHERE id = ?")->execute([$id]);
        header('Location: articles.php?deleted=1'); exit;
    } elseif ($action === 'ai_generate') {
        $topic = trim($_POST['topic'] ?? '');
        $category = $_POST['category'] ?? 'math';
        if (!$topic) { header('Location: articles.php?error=empty'); exit; }
        $api_key = Settings::get('ai_api_key', '');
        $provider = Settings::get('ai_provider', 'zai');
        $model = Settings::get('ai_model', 'glm-4.6');
        $prompt = "Write an article about '$topic' in Persian. Use HTML tags (h2, p, ul, li, code). Maximum 800 words. Provide a title in <h2>, brief excerpt, and main content with subsections.";
        $response = call_ai_for_admin($provider, $api_key, $model, $prompt);
        if ($response) {
            $stmt = $pdo->prepare("INSERT INTO articles (title, slug, excerpt, content, category, is_published, is_ai, author_id) VALUES (?,?,?,?,?,1,1,?)");
            $stmt->execute([
                $topic, preg_replace('/[^a-z0-9]+/', '-', strtolower($topic)) . '-' . substr(md5(time()), 0, 5),
                mb_substr(strip_tags($response), 0, 200),
                $response, $category, $user['id']
            ]);
            header('Location: articles.php?generated=' . $pdo->lastInsertId()); exit;
        }
        header('Location: articles.php?ai_error=1'); exit;
    }
}

function call_ai_for_admin($provider, $api_key, $model, $prompt) {
    if (!$api_key) return '';
    $api_url = '';
    $headers = ['Content-Type: application/json'];
    if ($provider === 'zai') { $api_url = 'https://api.z.ai/api/paas/v4/chat/completions'; $headers[] = 'Authorization: Bearer ' . $api_key; }
    elseif ($provider === 'openai') { $api_url = 'https://api.openai.com/v1/chat/completions'; $headers[] = 'Authorization: Bearer ' . $api_key; }
    else return '';
    $payload = json_encode(['model' => $model, 'messages' => [['role' => 'user', 'content' => $prompt]], 'max_tokens' => 2000]);
    $ch = curl_init($api_url);
    curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_HTTPHEADER => $headers, CURLOPT_POSTFIELDS => $payload, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 90]);
    $r = curl_exec($ch); curl_close($ch);
    $data = json_decode($r, true);
    return $data['choices'][0]['message']['content'] ?? '';
}

$edit_id = intval($_GET['id'] ?? 0);
$editing = null;
if ($edit_id) {
    $stmt = $pdo->prepare("SELECT * FROM articles WHERE id = ?"); $stmt->execute([$edit_id]);
    $editing = $stmt->fetch();
}
$articles = $pdo->query("SELECT a.*, u.name as author_name FROM articles a LEFT JOIN users u ON a.author_id = u.id ORDER BY a.created_at DESC")->fetchAll();
?>
<!DOCTYPE html>
<html lang="fa" dir="rtl"><head>
<meta charset="UTF-8"><title>📰 مقالات</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}textarea,input{font-family:inherit}</style>
</head><body class="bg-gray-100 min-h-screen">
<div class="flex">
<aside class="bg-slate-900 text-white w-64 min-h-screen fixed right-0 top-0 bottom-0 p-4 overflow-y-auto">
<div class="mb-6"><h1 class="text-xl font-bold">🔐 پنل مدیریت</h1></div>
<nav class="space-y-1">
<a href="index.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📊 داشبورد</a>
<a href="articles.php" class="block px-3 py-2 rounded text-sm bg-blue-600">📰 مقالات</a>
<a href="lessons.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📚 درس‌ها</a>
<a href="settings.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">⚙️ تنظیمات</a>
<a href="ai.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">🤖 AI</a>
<hr class="my-2 border-slate-700"><a href="../" class="block px-3 py-2 rounded text-sm text-slate-300">🏠 سایت</a>
<a href="logout.php" class="block px-3 py-2 rounded text-sm text-red-300">🚪 خروج</a>
</nav></aside>

<main class="flex-1 mr-64 p-6">
<header class="bg-white rounded-xl shadow-sm p-4 mb-6 flex justify-between">
<div><h2 class="text-2xl font-bold">📰 مقالات (<?= count($articles) ?>)</h2></div>
<div class="flex gap-2">
<a href="?action=new" class="bg-blue-600 text-white px-4 py-2 rounded text-sm">➕ مقاله جدید</a>
<a href="?action=ai" class="bg-purple-600 text-white px-4 py-2 rounded text-sm">🤖 ساخت با AI</a>
</div></header>

<?php if (isset($_GET['saved'])): ?><div class="bg-green-50 border-r-4 border-green-500 text-green-700 p-3 rounded mb-4">✅ ذخیره شد</div><?php endif; ?>
<?php if (isset($_GET['generated'])): ?><div class="bg-purple-50 border-r-4 border-purple-500 text-purple-700 p-3 rounded mb-4">🤖 مقاله توسط AI ساخته شد</div><?php endif; ?>
<?php if (isset($_GET['ai_error'])): ?><div class="bg-red-50 border-r-4 border-red-500 text-red-700 p-3 rounded mb-4">❌ AI نتونست مقاله بسازه</div><?php endif; ?>

<?php if (isset($_GET['action']) && $_GET['action'] === 'ai'): ?>
<div class="bg-white rounded-xl shadow-sm p-5 mb-4">
<h3 class="font-bold text-lg mb-3">🤖 ساخت مقاله با AI</h3>
<form method="post" class="space-y-3">
<?= csrf_field() ?>
<input type="hidden" name="action" value="ai_generate">
<div class="grid md:grid-cols-2 gap-3">
<div><label class="block text-xs text-gray-500 mb-1">موضوع</label><input type="text" name="topic" required placeholder="مثلاً: کشف قضیه‌ی سینوس" class="w-full px-3 py-2 border rounded text-sm"></div>
<div><label class="block text-xs text-gray-500 mb-1">دسته</label><select name="category" class="w-full px-3 py-2 border rounded text-sm"><option value="math">ریاضی</option><option value="physics">فیزیک</option><option value="medical">پزشکی</option><option value="pharmacy">داروسازی</option><option value="computer">کامپیوتر</option><option value="science">علوم</option></select></div>
</div>
<button class="bg-purple-600 text-white px-6 py-2 rounded text-sm">🤖 تولید با AI</button>
</form>
</div>
<?php endif; ?>

<?php if (isset($_GET['action']) || $editing): ?>
<div class="bg-white rounded-xl shadow-sm p-5 mb-4">
<h3 class="font-bold text-lg mb-3"><?= $editing ? '✏️ ویرایش' : '➕ مقاله جدید' ?></h3>
<form method="post" class="space-y-3">
<?= csrf_field() ?>
<input type="hidden" name="action" value="save">
<input type="hidden" name="id" value="<?= $editing['id'] ?? 0 ?>">
<div class="grid md:grid-cols-2 gap-3">
<div><label class="block text-xs text-gray-500 mb-1">عنوان</label><input type="text" name="title" required value="<?= sanitize($editing['title'] ?? '') ?>" class="w-full px-3 py-2 border rounded text-sm"></div>
<div><label class="block text-xs text-gray-500 mb-1">slug</label><input type="text" name="slug" value="<?= sanitize($editing['slug'] ?? '') ?>" placeholder="auto" class="w-full px-3 py-2 border rounded text-sm font-mono" dir="ltr"></div>
</div>
<div><label class="block text-xs text-gray-500 mb-1">خلاصه</label><textarea name="excerpt" rows="2" class="w-full px-3 py-2 border rounded text-sm"><?= sanitize($editing['excerpt'] ?? '') ?></textarea></div>
<div><label class="block text-xs text-gray-500 mb-1">محتوا (HTML)</label><textarea name="content" rows="15" required class="w-full px-3 py-2 border rounded text-sm font-mono" dir="ltr"><?= htmlspecialchars($editing['content'] ?? '') ?></textarea></div>
<div class="grid md:grid-cols-3 gap-3">
<div><label class="block text-xs text-gray-500 mb-1">دسته</label><select name="category" class="w-full px-3 py-2 border rounded text-sm"><option value="math" <?= ($editing['category'] ?? '')=='math'?'selected':'' ?>>ریاضی</option><option value="physics" <?= ($editing['category'] ?? '')=='physics'?'selected':'' ?>>فیزیک</option><option value="medical" <?= ($editing['category'] ?? '')=='medical'?'selected':'' ?>>پزشکی</option><option value="pharmacy" <?= ($editing['category'] ?? '')=='pharmacy'?'selected':'' ?>>داروسازی</option><option value="computer" <?= ($editing['category'] ?? '')=='computer'?'selected':'' ?>>کامپیوتر</option></select></div>
<div><label class="block text-xs text-gray-500 mb-1">برچسب‌ها</label><input type="text" name="tags" value="<?= sanitize($editing['tags'] ?? '') ?>" class="w-full px-3 py-2 border rounded text-sm"></div>
<div><label class="block text-xs text-gray-500 mb-1">URL تصویر</label><input type="text" name="image_url" value="<?= sanitize($editing['image_url'] ?? '') ?>" class="w-full px-3 py-2 border rounded text-sm" dir="ltr"></div>
</div>
<div class="flex gap-4">
<label class="flex items-center gap-2"><input type="checkbox" name="is_published" <?= ($editing['is_published'] ?? 0)?'checked':'' ?> class="w-5 h-5"><span>منتشرشده</span></label>
<label class="flex items-center gap-2"><input type="checkbox" name="is_ai" <?= ($editing['is_ai'] ?? 0)?'checked':'' ?> class="w-5 h-5"><span>تولیدشده با AI</span></label>
</div>
<button class="bg-blue-600 text-white px-6 py-2 rounded text-sm">💾 ذخیره</button>
</form>
</div>
<?php endif; ?>

<div class="bg-white rounded-xl shadow-sm overflow-x-auto">
<table class="w-full text-sm"><thead class="bg-gray-100 text-xs uppercase"><tr>
<th class="text-right p-3">#</th><th class="text-right p-3">عنوان</th><th class="text-right p-3">دسته</th><th class="text-right p-3">نویسنده</th><th class="text-right p-3">بازدید</th><th class="text-right p-3">وضعیت</th><th class="text-right p-3">عملیات</th>
</tr></thead><tbody>
<?php if (empty($articles)): ?><tr><td colspan="7" class="text-center py-6 text-gray-400">مقاله‌ای ساخته نشده</td></tr>
<?php else: foreach ($articles as $a): ?>
<tr class="border-b hover:bg-gray-50">
<td class="p-3 text-xs text-gray-400"><?= $a['id'] ?></td>
<td class="p-3 font-medium"><?= sanitize($a['title']) ?><?php if ($a['is_ai']): ?> <span class="text-xs bg-purple-100 text-purple-700 px-1 rounded">AI</span><?php endif; ?></td>
<td class="p-3 text-xs"><?= sanitize($a['category']) ?></td>
<td class="p-3 text-xs"><?= sanitize($a['author_name'] ?? '—') ?></td>
<td class="p-3 text-xs"><?= number_format($a['views']) ?></td>
<td class="p-3"><span class="px-2 py-1 rounded text-xs <?= $a['is_published']?'bg-green-100 text-green-700':'bg-yellow-100 text-yellow-700' ?>"><?= $a['is_published']?'منتشر':'پیش‌نویس' ?></span></td>
<td class="p-3 flex gap-2">
<a href="?id=<?= $a['id'] ?>" class="text-blue-600 text-xs">✏️</a>
<form method="post" onsubmit="return confirm('حذف؟')" class="inline"><input type="hidden" name="csrf_token" value="<?= csrf_token() ?>"><input type="hidden" name="action" value="delete"><input type="hidden" name="id" value="<?= $a['id'] ?>"><button class="text-red-600 text-xs">🗑️</button></form>
</td></tr>
<?php endforeach; endif; ?>
</tbody></table></div>
</main></div></body></html>
