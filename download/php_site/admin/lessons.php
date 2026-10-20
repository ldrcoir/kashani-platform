<?php
// ============================================================
// admin/lessons.php — مدیریت درس‌ها
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
        $description = trim($_POST['description'] ?? '');
        $content = $_POST['content'] ?? '';
        $category = $_POST['category'] ?? 'math';
        $difficulty = $_POST['difficulty'] ?? 'beginner';
        $duration = intval($_POST['duration_minutes'] ?? 30);
        $prerequisites = $_POST['prerequisites'] ?? '';
        $objectives = $_POST['learning_objectives'] ?? '';
        $exercises = $_POST['exercises'] ?? '[]';
        $solution = $_POST['solution_text'] ?? '';
        $video_url = $_POST['video_url'] ?? '';
        $is_published = isset($_POST['is_published']) ? 1 : 0;
        $sort_order = intval($_POST['sort_order'] ?? 0);
        if (empty($slug)) $slug = preg_replace('/[^a-z0-9]+/', '-', strtolower($title)) . '-' . substr(md5(time()), 0, 5);
        
        if ($id) {
            $stmt = $pdo->prepare("UPDATE lessons SET title=?, slug=?, description=?, content=?, category=?, difficulty=?, duration_minutes=?, prerequisites=?, learning_objectives=?, exercises=?, solution_text=?, video_url=?, is_published=?, sort_order=? WHERE id=?");
            $stmt->execute([$title, $slug, $description, $content, $category, $difficulty, $duration, $prerequisites, $objectives, $exercises, $solution, $video_url, $is_published, $sort_order, $id]);
        } else {
            $stmt = $pdo->prepare("INSERT INTO lessons (title, slug, description, content, category, difficulty, duration_minutes, prerequisites, learning_objectives, exercises, solution_text, video_url, is_published, sort_order, author_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)");
            $stmt->execute([$title, $slug, $description, $content, $category, $difficulty, $duration, $prerequisites, $objectives, $exercises, $solution, $video_url, $is_published, $sort_order, $user['id']]);
        }
        header('Location: lessons.php?saved=1'); exit;
    } elseif ($action === 'delete') {
        $id = intval($_POST['id']);
        $pdo->prepare("DELETE FROM lessons WHERE id = ?")->execute([$id]);
        header('Location: lessons.php?deleted=1'); exit;
    } elseif ($action === 'ai_generate') {
        // AI generates lesson
        $topic = trim($_POST['topic'] ?? '');
        $category = $_POST['category'] ?? 'math';
        $difficulty = $_POST['difficulty'] ?? 'beginner';
        if (!$topic) { header('Location: lessons.php?error=empty'); exit; }
        
        $api_key = Settings::get('ai_api_key', '');
        $provider = Settings::get('ai_provider', 'zai');
        $model = Settings::get('ai_model', 'glm-4.6');
        $prompt = "Create a complete educational lesson about '$topic' for $difficulty level in Persian. Output JSON with: title, slug (english), description, content (HTML with h2/h3/p/code tags, max 1500 words), exercises (JSON array of {type:choice/text, question, choices?, answer}), solution_text, learning_objectives. Category: $category. Make exercises educational with 3-5 questions.";
        
        $response = call_ai_for_admin($provider, $api_key, $model, $prompt);
        // Try to parse JSON from response
        if (preg_match('/\{.*\}/s', $response, $m)) {
            $lesson_data = json_decode($m[0], true);
            if ($lesson_data) {
                $stmt = $pdo->prepare("INSERT INTO lessons (title, slug, description, content, category, difficulty, duration_minutes, learning_objectives, exercises, solution_text, is_published, author_id) VALUES (?,?,?,?,?,?,?,?,?,?,1,?)");
                $stmt->execute([
                    $lesson_data['title'] ?? $topic,
                    $lesson_data['slug'] ?? preg_replace('/[^a-z0-9]+/', '-', strtolower($topic)) . '-' . substr(md5(time()), 0, 5),
                    $lesson_data['description'] ?? '',
                    $lesson_data['content'] ?? '',
                    $category, $difficulty, 30,
                    $lesson_data['learning_objectives'] ?? '',
                    json_encode($lesson_data['exercises'] ?? [], JSON_UNESCAPED_UNICODE),
                    $lesson_data['solution_text'] ?? '',
                    $user['id']
                ]);
                header('Location: lessons.php?generated=' . $pdo->lastInsertId()); exit;
            }
        }
        header('Location: lessons.php?ai_error=1'); exit;
    }
}

function call_ai_for_admin($provider, $api_key, $model, $prompt) {
    if (!$api_key) return '';
    $messages = [['role' => 'user', 'content' => $prompt]];
    $api_url = '';
    $headers = ['Content-Type: application/json'];
    if ($provider === 'zai') { $api_url = 'https://api.z.ai/api/paas/v4/chat/completions'; $headers[] = 'Authorization: Bearer ' . $api_key; }
    elseif ($provider === 'openai') { $api_url = 'https://api.openai.com/v1/chat/completions'; $headers[] = 'Authorization: Bearer ' . $api_key; }
    else return '';
    
    $payload = json_encode(['model' => $model, 'messages' => $messages, 'max_tokens' => 4000]);
    $ch = curl_init($api_url);
    curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_HTTPHEADER => $headers, CURLOPT_POSTFIELDS => $payload, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 120]);
    $r = curl_exec($ch); curl_close($ch);
    $data = json_decode($r, true);
    return $data['choices'][0]['message']['content'] ?? '';
}

$edit_id = intval($_GET['id'] ?? 0);
$editing = null;
if ($edit_id) {
    $stmt = $pdo->prepare("SELECT * FROM lessons WHERE id = ?"); $stmt->execute([$edit_id]);
    $editing = $stmt->fetch();
}
$lessons = $pdo->query("SELECT * FROM lessons ORDER BY sort_order, created_at DESC")->fetchAll();
?>
<!DOCTYPE html>
<html lang="fa" dir="rtl"><head>
<meta charset="UTF-8"><title>📚 مدیریت درس‌ها</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}textarea,input{font-family:inherit}</style>
</head><body class="bg-gray-100 min-h-screen">
<div class="flex">
<aside class="bg-slate-900 text-white w-64 min-h-screen fixed right-0 top-0 bottom-0 p-4 overflow-y-auto">
<div class="mb-6"><h1 class="text-xl font-bold">🔐 پنل مدیریت</h1></div>
<nav class="space-y-1">
<a href="index.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📊 داشبورد</a>
<a href="lessons.php" class="block px-3 py-2 rounded text-sm bg-blue-600">📚 درس‌ها</a>
<a href="articles.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">📰 مقالات</a>
<a href="settings.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">⚙️ تنظیمات</a>
<a href="ai.php" class="block px-3 py-2 rounded text-sm hover:bg-blue-600">🤖 AI</a>
<hr class="my-2 border-slate-700"><a href="../" class="block px-3 py-2 rounded text-sm text-slate-300">🏠 سایت</a>
<a href="logout.php" class="block px-3 py-2 rounded text-sm text-red-300">🚪 خروج</a>
</nav></aside>

<main class="flex-1 mr-64 p-6">
<header class="bg-white rounded-xl shadow-sm p-4 mb-6 flex justify-between">
<div><h2 class="text-2xl font-bold">📚 مدیریت درس‌ها (<?= count($lessons) ?>)</h2></div>
<div class="flex gap-2">
<a href="?action=new" class="bg-blue-600 text-white px-4 py-2 rounded text-sm">➕ درس جدید</a>
<a href="?action=ai" class="bg-purple-600 text-white px-4 py-2 rounded text-sm">🤖 ساخت با AI</a>
</div></header>

<?php if (isset($_GET['saved'])): ?><div class="bg-green-50 border-r-4 border-green-500 text-green-700 p-3 rounded mb-4">✅ ذخیره شد</div><?php endif; ?>
<?php if (isset($_GET['generated'])): ?><div class="bg-purple-50 border-r-4 border-purple-500 text-purple-700 p-3 rounded mb-4">🤖 درس توسط AI ساخته شد (ID: <?= intval($_GET['generated']) ?>)</div><?php endif; ?>
<?php if (isset($_GET['ai_error'])): ?><div class="bg-red-50 border-r-4 border-red-500 text-red-700 p-3 rounded mb-4">❌ AI نتونست درس بسازه</div><?php endif; ?>

<?php if (isset($_GET['action']) && $_GET['action'] === 'ai'): ?>
<div class="bg-white rounded-xl shadow-sm p-5 mb-4">
<h3 class="font-bold text-lg mb-3">🤖 ساخت درس با AI</h3>
<form method="post" class="space-y-3">
<?= csrf_field() ?>
<input type="hidden" name="action" value="ai_generate">
<div class="grid md:grid-cols-3 gap-3">
<div><label class="block text-xs text-gray-500 mb-1">موضوع درس</label><input type="text" name="topic" required placeholder="مثلاً: مقدمه‌ای بر رمزنگاری RSA" class="w-full px-3 py-2 border rounded text-sm"></div>
<div><label class="block text-xs text-gray-500 mb-1">دسته</label><select name="category" class="w-full px-3 py-2 border rounded text-sm"><option value="math">ریاضی</option><option value="physics">فیزیک</option><option value="medical">پزشکی</option><option value="pharmacy">داروسازی</option><option value="computer">کامپیوتر</option><option value="science">علوم</option></select></div>
<div><label class="block text-xs text-gray-500 mb-1">سطح</label><select name="difficulty" class="w-full px-3 py-2 border rounded text-sm"><option value="beginner">مقدماتی</option><option value="intermediate">متوسط</option><option value="advanced">پیشرفته</option><option value="expert">خبره</option></select></div>
</div>
<button class="bg-purple-600 text-white px-6 py-2 rounded text-sm">🤖 تولید با AI</button>
</form>
</div>
<?php endif; ?>

<?php if (isset($_GET['action']) || $editing): ?>
<div class="bg-white rounded-xl shadow-sm p-5 mb-4">
<h3 class="font-bold text-lg mb-3"><?= $editing ? '✏️ ویرایش' : '➕ درس جدید' ?></h3>
<form method="post" class="space-y-3">
<?= csrf_field() ?>
<input type="hidden" name="action" value="save">
<input type="hidden" name="id" value="<?= $editing['id'] ?? 0 ?>">
<div class="grid md:grid-cols-2 gap-3">
<div><label class="block text-xs text-gray-500 mb-1">عنوان</label><input type="text" name="title" required value="<?= sanitize($editing['title'] ?? '') ?>" class="w-full px-3 py-2 border rounded text-sm"></div>
<div><label class="block text-xs text-gray-500 mb-1">slug</label><input type="text" name="slug" value="<?= sanitize($editing['slug'] ?? '') ?>" placeholder="auto" class="w-full px-3 py-2 border rounded text-sm font-mono" dir="ltr"></div>
</div>
<div><label class="block text-xs text-gray-500 mb-1">توضیح</label><textarea name="description" rows="2" class="w-full px-3 py-2 border rounded text-sm"><?= sanitize($editing['description'] ?? '') ?></textarea></div>
<div><label class="block text-xs text-gray-500 mb-1">محتوا (HTML با LaTeX)</label><textarea name="content" rows="15" required class="w-full px-3 py-2 border rounded text-sm font-mono" dir="ltr"><?= htmlspecialchars($editing['content'] ?? '') ?></textarea></div>
<div class="grid md:grid-cols-4 gap-3">
<div><label class="block text-xs text-gray-500 mb-1">دسته</label><select name="category" class="w-full px-3 py-2 border rounded text-sm"><option value="math" <?= ($editing['category'] ?? '')=='math'?'selected':'' ?>>ریاضی</option><option value="physics" <?= ($editing['category'] ?? '')=='physics'?'selected':'' ?>>فیزیک</option><option value="medical" <?= ($editing['category'] ?? '')=='medical'?'selected':'' ?>>پزشکی</option><option value="pharmacy" <?= ($editing['category'] ?? '')=='pharmacy'?'selected':'' ?>>داروسازی</option><option value="computer" <?= ($editing['category'] ?? '')=='computer'?'selected':'' ?>>کامپیوتر</option><option value="science" <?= ($editing['category'] ?? '')=='science'?'selected':'' ?>>علوم</option></select></div>
<div><label class="block text-xs text-gray-500 mb-1">سطح</label><select name="difficulty" class="w-full px-3 py-2 border rounded text-sm"><option value="beginner" <?= ($editing['difficulty'] ?? '')=='beginner'?'selected':'' ?>>مقدماتی</option><option value="intermediate" <?= ($editing['difficulty'] ?? '')=='intermediate'?'selected':'' ?>>متوسط</option><option value="advanced" <?= ($editing['difficulty'] ?? '')=='advanced'?'selected':'' ?>>پیشرفته</option><option value="expert" <?= ($editing['difficulty'] ?? '')=='expert'?'selected':'' ?>>خبره</option></select></div>
<div><label class="block text-xs text-gray-500 mb-1">مدت (دقیقه)</label><input type="number" name="duration_minutes" value="<?= $editing['duration_minutes'] ?? 30 ?>" class="w-full px-3 py-2 border rounded text-sm"></div>
<div><label class="block text-xs text-gray-500 mb-1">ترتیب</label><input type="number" name="sort_order" value="<?= $editing['sort_order'] ?? 0 ?>" class="w-full px-3 py-2 border rounded text-sm"></div>
</div>
<div><label class="block text-xs text-gray-500 mb-1">پیش‌نیازها</label><input type="text" name="prerequisites" value="<?= sanitize($editing['prerequisites'] ?? '') ?>" class="w-full px-3 py-2 border rounded text-sm"></div>
<div><label class="block text-xs text-gray-500 mb-1">اهداف آموزشی</label><input type="text" name="learning_objectives" value="<?= sanitize($editing['learning_objectives'] ?? '') ?>" class="w-full px-3 py-2 border rounded text-sm"></div>
<div><label class="block text-xs text-gray-500 mb-1">تمرین‌ها (JSON)</label><textarea name="exercises" rows="5" class="w-full px-3 py-2 border rounded text-sm font-mono" dir="ltr"><?= sanitize($editing['exercises'] ?? '[]') ?></textarea></div>
<div><label class="block text-xs text-gray-500 mb-1">راهنمایی / پاسخ</label><textarea name="solution_text" rows="3" class="w-full px-3 py-2 border rounded text-sm"><?= sanitize($editing['solution_text'] ?? '') ?></textarea></div>
<div><label class="block text-xs text-gray-500 mb-1">URL ویدیو (اختیاری)</label><input type="text" name="video_url" value="<?= sanitize($editing['video_url'] ?? '') ?>" class="w-full px-3 py-2 border rounded text-sm" dir="ltr"></div>
<label class="flex items-center gap-2"><input type="checkbox" name="is_published" <?= ($editing['is_published'] ?? 0)?'checked':'' ?> class="w-5 h-5"><span>منتشرشده</span></label>
<button class="bg-blue-600 text-white px-6 py-2 rounded text-sm">💾 ذخیره</button>
</form>
</div>
<?php endif; ?>

<div class="bg-white rounded-xl shadow-sm overflow-x-auto">
<table class="w-full text-sm"><thead class="bg-gray-100 text-xs uppercase"><tr>
<th class="text-right p-3">#</th><th class="text-right p-3">عنوان</th><th class="text-right p-3">دسته</th><th class="text-right p-3">سطح</th><th class="text-right p-3">مدت</th><th class="text-right p-3">بازدید</th><th class="text-right p-3">تکمیل</th><th class="text-right p-3">وضعیت</th><th class="text-right p-3">عملیات</th>
</tr></thead><tbody>
<?php if (empty($lessons)): ?><tr><td colspan="9" class="text-center py-6 text-gray-400">هنوز درسی ساخته نشده</td></tr>
<?php else: foreach ($lessons as $l): ?>
<tr class="border-b hover:bg-gray-50">
<td class="p-3 text-xs text-gray-400"><?= $l['id'] ?></td>
<td class="p-3 font-medium"><?= sanitize($l['title']) ?></td>
<td class="p-3 text-xs"><?= sanitize($l['category']) ?></td>
<td class="p-3 text-xs"><?= sanitize($l['difficulty']) ?></td>
<td class="p-3 text-xs"><?= $l['duration_minutes'] ?> دقیقه</td>
<td class="p-3 text-xs"><?= number_format($l['views']) ?></td>
<td class="p-3 text-xs text-emerald-600"><?= number_format($l['completions']) ?></td>
<td class="p-3"><span class="px-2 py-1 rounded text-xs <?= $l['is_published']?'bg-green-100 text-green-700':'bg-yellow-100 text-yellow-700' ?>"><?= $l['is_published']?'منتشر':'پیش‌نویس' ?></span></td>
<td class="p-3 flex gap-2">
<a href="?id=<?= $l['id'] ?>" class="text-blue-600 text-xs">✏️</a>
<form method="post" onsubmit="return confirm('حذف؟')" class="inline"><input type="hidden" name="csrf_token" value="<?= csrf_token() ?>"><input type="hidden" name="action" value="delete"><input type="hidden" name="id" value="<?= $l['id'] ?>"><button class="text-red-600 text-xs">🗑️</button></form>
</td></tr>
<?php endforeach; endif; ?>
</tbody></table></div>
</main></div></body></html>
