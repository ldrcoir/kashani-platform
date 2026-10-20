<?php
// ============================================================
// lesson.php — نمایش یک درس با تمرین تعاملی
// ============================================================
require_once __DIR__ . '/functions.php';
secure_session_start();

$lang = $_GET['lang'] ?? $_COOKIE['lang'] ?? 'fa';
$dir = in_array($lang, ['fa','ar','ur']) ? 'rtl' : 'ltr';

$slug = $_GET['slug'] ?? '';
if (!$slug) { header('Location: lessons.php'); exit; }

$pdo = Database::getInstance();
$stmt = $pdo->prepare("SELECT * FROM lessons WHERE slug = ? AND is_published = 1");
$stmt->execute([$slug]);
$lesson = $stmt->fetch();

if (!$lesson) {
    http_response_code(404);
    die('<h1>۴۰۴ — درس یافت نشد</h1><p><a href="lessons.php">→ بازگشت</a></p>');
}

// Increment views
$pdo->prepare("UPDATE lessons SET views = views + 1 WHERE id = ?")->execute([$lesson['id']]);

// Get user progress
$user = current_user();
$progress = null;
if ($user) {
    $stmt = $pdo->prepare("SELECT * FROM lesson_progress WHERE lesson_id = ? AND user_id = ?");
    $stmt->execute([$lesson['id'], $user['id']]);
    $progress = $stmt->fetch();
}

// Parse exercises from lesson (JSON)
$exercises = json_decode($lesson['exercises'] ?? '[]', true) ?: [];
$categories = [
    'math' => ['label' => 'ریاضی', 'icon' => '🔢'],
    'physics' => ['label' => 'فیزیک', 'icon' => '⚛️'],
    'medical' => ['label' => 'پزشکی', 'icon' => '⚕️'],
    'pharmacy' => ['label' => 'داروسازی', 'icon' => '💊'],
    'computer' => ['label' => 'کامپیوتر', 'icon' => '💻'],
    'science' => ['label' => 'علوم', 'icon' => '🔬'],
    'general' => ['label' => 'عمومی', 'icon' => '📚'],
];
$cat = $categories[$lesson['category']] ?? $categories['general'];

// Get comments
$comments = [];
try {
    $stmt = $pdo->prepare("SELECT c.*, u.name as user_name FROM comments c JOIN users u ON c.user_id = u.id WHERE c.lesson_id = ? AND c.is_approved = 1 ORDER BY c.created_at");
    $stmt->execute([$lesson['id']]);
    $comments = $stmt->fetchAll();
} catch (Exception $e) {}
?>
<!DOCTYPE html>
<html lang="<?= $lang ?>" dir="<?= $dir ?>">
<head>
    <meta charset="UTF-8">
    <link rel="canonical" href="<?= site_url() ?>/lesson.php?slug=<?= urlencode($lesson['slug']) ?>">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📚 <?= sanitize($lesson['title']) ?></title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.min.js"></script>
    <style>
        body{font-family:'Vazirmatn',Tahoma,sans-serif}
        .lesson-content p{margin-bottom:1em;line-height:1.8}
        .lesson-content h2{font-weight:bold;font-size:1.5em;margin-top:1.5em;margin-bottom:0.5em}
        .lesson-content h3{font-weight:bold;font-size:1.25em;margin-top:1em}
        .lesson-content code{background:#f3f4f6;padding:2px 4px;border-radius:3px;direction:ltr}
        .lesson-content pre{background:#1e293b;color:#e2e8f0;padding:1em;border-radius:8px;direction:ltr;overflow-x:auto}
        .lesson-content ul,.lesson-content ol{margin-right:1.5em}
        .exercise-card{border:1px solid #e5e7eb;border-radius:8px;padding:1em;margin:1em 0}
        .exercise-card.correct{background:#f0fdf4;border-color:#86efac}
        .exercise-card.wrong{background:#fef2f2;border-color:#fca5a5}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">

<header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-4xl mx-auto px-4 py-3 flex justify-between">
        <a href="lessons.php" class="text-sm text-gray-600">← بازگشت به درس‌ها</a>
        <a href="index.php" class="text-sm text-gray-600">🏠 خانه</a>
    </div>
</header>

<article class="max-w-4xl mx-auto p-4">
    <!-- Header -->
    <div class="bg-gradient-to-br from-<?= $cat['icon']=='⚛️'?'purple':($cat['icon']=='🔢'?'blue':'emerald') ?>-50 to-<?= $cat['icon']=='⚛️'?'purple':($cat['icon']=='🔢'?'blue':'emerald') ?>-100 rounded-2xl p-6 mb-6">
        <div class="flex items-center gap-3 mb-2">
            <span class="text-4xl"><?= $cat['icon'] ?></span>
            <div>
                <span class="text-xs bg-white px-2 py-1 rounded"><?= $cat['label'] ?></span>
                <span class="text-xs bg-white px-2 py-1 rounded mr-1">⏱️ <?= $lesson['duration_minutes'] ?> دقیقه</span>
            </div>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2"><?= sanitize($lesson['title']) ?></h1>
        <p class="text-gray-600"><?= sanitize($lesson['description']) ?></p>
    </div>
    
    <!-- Learning objectives -->
    <?php if ($lesson['learning_objectives']): ?>
    <div class="bg-blue-50 rounded-xl p-4 mb-4">
        <h3 class="font-bold mb-2 text-blue-700">🎯 اهداف آموزشی</h3>
        <div class="text-sm text-gray-700"><?= $lesson['learning_objectives'] ?></div>
    </div>
    <?php endif; ?>
    
    <!-- Prerequisites -->
    <?php if ($lesson['prerequisites']): ?>
    <div class="bg-amber-50 rounded-xl p-4 mb-4">
        <h3 class="font-bold mb-2 text-amber-700">📋 پیش‌نیازها</h3>
        <div class="text-sm text-gray-700"><?= $lesson['prerequisites'] ?></div>
    </div>
    <?php endif; ?>
    
    <!-- Video -->
    <?php if ($lesson['video_url']): ?>
    <div class="bg-black rounded-xl overflow-hidden mb-4">
        <video src="<?= sanitize($lesson['video_url']) ?>" controls class="w-full"></video>
    </div>
    <?php endif; ?>
    
    <!-- Main content -->
    <div class="bg-white rounded-xl shadow p-6 mb-4">
        <h2 class="text-xl font-bold mb-4 text-gray-800">📖 محتوای درس</h2>
        <div class="lesson-content prose max-w-none">
            <?= sanitize_html($lesson['content']) ?>
        </div>
    </div>
    
    <!-- Exercises -->
    <?php if (!empty($exercises)): ?>
    <div class="bg-white rounded-xl shadow p-6 mb-4">
        <h2 class="text-xl font-bold mb-4 text-gray-800">✍️ تمرین‌ها (<?= count($exercises) ?>)</h2>
        <?php if (!$user): ?>
        <div class="bg-yellow-50 border-r-4 border-yellow-500 p-3 rounded mb-3 text-sm">
            ⚠️ برای پاسخ به تمرین‌ها باید <a href="auth/phone.php" class="text-blue-600 underline">وارد شوید</a>
        </div>
        <?php endif; ?>
        
        <?php foreach ($exercises as $i => $ex): 
            $type = $ex['type'] ?? 'text';
            $question = $ex['question'] ?? '';
            $answer = $ex['answer'] ?? '';
            $choices = $ex['choices'] ?? [];
        ?>
        <div class="exercise-card" id="ex-<?= $i ?>">
            <h4 class="font-bold mb-2">سوال <?= $i+1 ?></h4>
            <p class="mb-3 text-gray-700"><?= sanitize($question) ?></p>
            
            <?php if ($type === 'choice' && !empty($choices)): ?>
            <div class="space-y-1">
                <?php foreach ($choices as $j => $choice): ?>
                <button onclick="checkChoice(<?= $i ?>, '<?= htmlspecialchars($choice, ENT_QUOTES) ?>', '<?= htmlspecialchars($answer, ENT_QUOTES) ?>')" 
                    class="block w-full text-right p-2 border rounded hover:bg-blue-50 text-sm">
                    <?= sanitize($choice) ?>
                </button>
                <?php endforeach; ?>
            </div>
            <?php else: ?>
            <div class="flex gap-2">
                <input type="text" id="answer-<?= $i ?>" placeholder="پاسخ شما" class="flex-1 px-3 py-2 border rounded text-sm" <?= $user?'':'disabled' ?>>
                <button onclick="checkText(<?= $i ?>, '<?= htmlspecialchars($answer, ENT_QUOTES) ?>')" class="bg-blue-600 text-white px-4 py-2 rounded text-sm" <?= $user?'':'disabled' ?>>بررسی</button>
            </div>
            <?php endif; ?>
            
            <div id="result-<?= $i ?>" class="mt-2 text-sm"></div>
        </div>
        <?php endforeach; ?>
    </div>
    <?php endif; ?>
    
    <!-- Solution -->
    <?php if ($lesson['solution_text']): ?>
    <div class="bg-emerald-50 rounded-xl p-4 mb-4">
        <h3 class="font-bold mb-2 text-emerald-700">💡 راهنمایی / پاسخ</h3>
        <div class="text-sm text-gray-700"><?= sanitize_html($lesson['solution_text']) ?></div>
    </div>
    <?php endif; ?>
    
    <!-- Mark complete -->
    <?php if ($user): ?>
    <div class="bg-white rounded-xl shadow p-4 mb-4 text-center">
        <?php if ($progress && $progress['status'] === 'completed'): ?>
        <div class="bg-green-100 text-green-700 p-3 rounded">✅ این درس را تکمیل کرده‌اید</div>
        <?php else: ?>
        <button onclick="markComplete(<?= $lesson['id'] ?>)" class="bg-emerald-600 text-white px-6 py-2 rounded">✓ این درس را به اتمام رساندم</button>
        <?php endif; ?>
    </div>
    <?php endif; ?>
    
    <!-- Comments -->
    <div class="bg-white rounded-xl shadow p-5">
        <h2 class="font-bold text-lg mb-3 text-gray-800">💬 نظرات (<?= count($comments) ?>)</h2>
        <?php if (empty($comments)): ?>
        <p class="text-sm text-gray-400 mb-3">اولین نظر را ثبت کنید</p>
        <?php else: foreach ($comments as $c): ?>
        <div class="border-r-2 border-gray-200 pr-3 py-2">
            <div class="font-medium text-sm"><?= sanitize($c['user_name']) ?> <span class="text-xs text-gray-400"><?= date('Y/m/d', strtotime($c['created_at'])) ?></span></div>
            <div class="text-sm text-gray-700"><?= sanitize($c['content']) ?></div>
        </div>
        <?php endforeach; endif; ?>
        
        <?php if ($user): ?>
        <form method="post" action="api.php" class="mt-3">
            <input type="hidden" name="action" value="comment_lesson">
            <input type="hidden" name="csrf_token" value="<?= csrf_token() ?>">
            <input type="hidden" name="lesson_id" value="<?= $lesson['id'] ?>">
            <textarea name="content" rows="2" placeholder="نظر شما..." class="w-full px-3 py-2 border rounded text-sm" required></textarea>
            <button class="mt-2 bg-blue-600 text-white px-4 py-1 rounded text-sm">ارسال</button>
        </form>
        <?php endif; ?>
    </div>
</article>

<script>
function checkChoice(i, choice, answer) {
    const card = document.getElementById('ex-' + i);
    const result = document.getElementById('result-' + i);
    if (choice === answer) {
        card.classList.add('correct'); card.classList.remove('wrong');
        result.innerHTML = '<span class="text-green-600">✓ درست!</span>';
    } else {
        card.classList.add('wrong'); card.classList.remove('correct');
        result.innerHTML = '<span class="text-red-600">✗ نادرست. پاسخ درست: ' + answer + '</span>';
    }
}

function checkText(i, answer) {
    const input = document.getElementById('answer-' + i);
    const card = document.getElementById('ex-' + i);
    const result = document.getElementById('result-' + i);
    const user_answer = input.value.trim();
    if (!user_answer) { alert('پاسخ بنویسید'); return; }
    // Normalize: lower, no spaces
    if (user_answer.toLowerCase().replace(/\s/g,'') === answer.toLowerCase().replace(/\s/g,'')) {
        card.classList.add('correct'); card.classList.remove('wrong');
        result.innerHTML = '<span class="text-green-600">✓ درست!</span>';
    } else {
        card.classList.add('wrong'); card.classList.remove('correct');
        result.innerHTML = '<span class="text-red-600">✗ نادرست. پاسخ درست: ' + answer + '</span>';
    }
}

async function markComplete(lessonId) {
    const formData = new FormData();
    formData.append('action', 'lesson_complete');
    formData.append('csrf_token', '<?= csrf_token() ?>');
    formData.append('lesson_id', lessonId);
    const r = await fetch('api.php', {method: 'POST', body: formData}).then(r => r.json());
    if (r.success) { alert('✅ تبریک! درس تکمیل شد.'); location.reload(); }
    else { alert('خطا: ' + (r.error || 'unknown')); }
}
</script>

</body>
</html>
