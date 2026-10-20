<?php
// ============================================================
// ai/chat.php — چت با AI دستیار علمی
// ============================================================
require_once __DIR__ . '/../functions.php';
secure_session_start();

require_login();
$user = current_user();

$lang = $_GET['lang'] ?? $_COOKIE['lang'] ?? 'fa';
$dir = in_array($lang, ['fa','ar','ur']) ? 'rtl' : 'ltr';

// Load user's conversations
$pdo = Database::getInstance();
try {
    $conversations = $pdo->prepare("SELECT id, title, provider, model, updated_at FROM ai_conversations WHERE user_id = ? AND is_archived = 0 ORDER BY updated_at DESC LIMIT 20");
    $conversations->execute([$user['id']]);
    $conversations = $conversations->fetchAll();
} catch (Exception $e) { $conversations = []; }

$current_conv_id = intval($_GET['conv'] ?? 0);
$current_conv = null;
$current_messages = [];

if ($current_conv_id) {
    try {
        $stmt = $pdo->prepare("SELECT * FROM ai_conversations WHERE id = ? AND user_id = ?");
        $stmt->execute([$current_conv_id, $user['id']]);
        $current_conv = $stmt->fetch();
        if ($current_conv) {
            $current_messages = json_decode($current_conv['messages'], true) ?: [];
        }
    } catch (Exception $e) {}
}

// Get AI provider info
$ai_provider = Settings::get('ai_provider', 'zai');
$ai_model = Settings::get('ai_model', 'glm-4.6');
?>
<!DOCTYPE html>
<html lang="<?= $lang ?>" dir="<?= $dir ?>">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI دستیار علمی</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.0.6/purify.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.min.js"></script>
    <style>
        body{font-family:'Vazirmatn',Tahoma,sans-serif}
        .msg-user{background:#dbeafe;border-radius:12px 12px 4px 12px;padding:10px 14px;margin:8px 0;max-width:80%;margin-right:auto}
        .msg-ai{background:#f1f5f9;border-radius:12px 12px 12px 4px;padding:10px 14px;margin:8px 0;max-width:80%}
        .msg-ai pre{background:#1e293b;color:#e2e8f0;padding:8px;border-radius:6px;overflow-x:auto;font-family:monospace;direction:ltr}
        .msg-ai code{background:#e2e8f0;padding:2px 4px;border-radius:3px;font-family:monospace;direction:ltr}
        .typing{animation:pulse 1s infinite}
        @keyframes pulse{0%,100%{opacity:0.5}50%{opacity:1}}
    </style>
</head>
<body class="bg-gray-100 min-h-screen h-screen overflow-hidden flex flex-col">

<header class="bg-white shadow-sm px-4 py-2 flex justify-between items-center flex-shrink-0">
    <div class="flex items-center gap-3">
        <span class="text-2xl">🤖</span>
        <div><h1 class="text-lg font-bold text-gray-800">AI دستیار علمی</h1><p class="text-xs text-gray-500">پلتفرم علمی — به افتخار کاشانی</p></div>
    </div>
    <div class="flex items-center gap-2">
        <span class="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded"><?= $ai_provider ?> • <?= $ai_model ?></span>
        <a href="../" class="text-sm text-gray-600">🏠 خانه</a>
    </div>
</header>

<div class="flex-1 flex overflow-hidden">
    <!-- Sidebar: conversations -->
    <aside class="bg-white w-64 border-l flex-shrink-0 overflow-y-auto">
        <div class="p-3 border-b"><button onclick="newConversation()" class="w-full bg-emerald-600 text-white px-3 py-2 rounded text-sm">➕ گفتگوی جدید</button></div>
        <div class="p-2 space-y-1">
            <?php if (empty($conversations)): ?>
            <p class="text-xs text-gray-400 text-center p-3">هنوز گفتگویی ندارید</p>
            <?php else: foreach ($conversations as $c): ?>
            <a href="?conv=<?= $c['id'] ?>" class="block p-2 rounded hover:bg-gray-100 text-sm <?= $current_conv_id==$c['id']?'bg-blue-100':'' ?>">
                <div class="font-medium truncate"><?= sanitize($c['title'] ?? 'بدون عنوان') ?></div>
                <div class="text-xs text-gray-400"><?= date('Y/m/d H:i', strtotime($c['updated_at'])) ?></div>
            </a>
            <?php endforeach; endif; ?>
        </div>
    </aside>
    
    <!-- Chat area -->
    <main class="flex-1 flex flex-col">
        <div id="messages" class="flex-1 overflow-y-auto p-4 bg-gray-50">
            <?php if (empty($current_messages)): ?>
            <div class="text-center py-12 text-gray-400">
                <div class="text-6xl mb-3">🤖</div>
                <p class="text-lg">سوال خود را بپرسید</p>
                <p class="text-sm mt-2">ریاضی، فیزیک، پزشکی، داروسازی، کامپیوتر</p>
                <div class="mt-6 grid grid-cols-2 gap-2 max-w-md mx-auto text-sm">
                    <button onclick="usePrompt('قضیه‌ی سینوس را توضیح بده')" class="p-2 bg-white rounded hover:bg-blue-50">📐 قضیه‌ی سینوس</button>
                    <button onclick="usePrompt('اعداد اول چه هستند؟')" class="p-2 bg-white rounded hover:bg-blue-50">🔢 اعداد اول</button>
                    <button onclick="usePrompt('پروتئین فولدینگ چیست؟')" class="p-2 bg-white rounded hover:bg-blue-50">🧬 پروتئین فولدینگ</button>
                    <button onclick="usePrompt('الگوریتم ضرب نخی را بنویس')" class="p-2 bg-white rounded hover:bg-blue-50">🔢 الگوریتم فاکتور</button>
                </div>
            </div>
            <?php else: foreach ($current_messages as $m): ?>
            <div class="<?= $m['role']=='user'?'msg-user':'msg-ai' ?>">
                <div class="text-xs text-gray-500 mb-1"><?= $m['role']=='user'?'👤 شما':'🤖 AI' ?></div>
                <div id="msg-<?= md5($m['content']) ?>" class="text-sm"></div>
            </div>
            <script>
                (function() {
                    const content = <?= json_encode($m['content']) ?>;
                    let html;
                    try { html = marked.parse(content); } catch (e) { html = content.replace(/</g,'&lt;'); }
                    document.getElementById('msg-<?= md5($m['content']) ?>').innerHTML = DOMPurify.sanitize(html);
                })();
            </script>
            <?php endforeach; endif; ?>
        </div>
        
        <div id="typing" class="hidden px-4 py-2 text-sm text-gray-500 typing">🤖 در حال تایپ...</div>
        
        <form id="chat-form" class="bg-white border-t p-3 flex gap-2">
            <textarea id="input" placeholder="سوال بنویسید... (Enter ارسال، Shift+Enter خط جدید)" rows="2" class="flex-1 px-3 py-2 border rounded text-sm" maxlength="2000"></textarea>
            <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded text-sm">📤 ارسال</button>
        </form>
    </main>
</div>

<script>
const CSRF = '<?= csrf_token() ?>';
const CONV_ID = <?= $current_conv_id ?>;
let currentConvId = CONV_ID;

function usePrompt(text) {
    document.getElementById('input').value = text;
    document.getElementById('input').focus();
}

async function newConversation() {
    if (!confirm('شروع گفتگوی جدید؟')) return;
    const result = await fetch('api.php', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: 'action=ai_new_conv&csrf_token=' + CSRF
    }).then(r => r.json());
    if (result.success) {
        window.location.href = '?conv=' + result.conv_id;
    }
}

document.getElementById('chat-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('input');
    const text = input.value.trim();
    if (!text) return;
    
    // Show user message immediately
    const msgsDiv = document.getElementById('messages');
    const userMsg = document.createElement('div');
    userMsg.className = 'msg-user';
    userMsg.innerHTML = '<div class="text-xs text-gray-500 mb-1">👤 شما</div><div class="text-sm"></div>';
    userMsg.querySelector('.text-sm').textContent = text;
    msgsDiv.appendChild(userMsg);
    input.value = '';
    input.disabled = true;
    
    // Show typing
    document.getElementById('typing').classList.remove('hidden');
    msgsDiv.scrollTop = msgsDiv.scrollHeight;
    
    try {
        const formData = new FormData();
        formData.append('action', 'ai_send');
        formData.append('csrf_token', CSRF);
        formData.append('conv_id', currentConvId);
        formData.append('message', text);
        
        const result = await fetch('api.php', {method: 'POST', body: formData}).then(r => r.json());
        
        document.getElementById('typing').classList.add('hidden');
        
        if (result.error) {
            alert('خطا: ' + result.error);
        } else {
            if (result.conv_id && !currentConvId) {
                currentConvId = result.conv_id;
                history.replaceState(null, '', '?conv=' + currentConvId);
            }
            // Show AI response
            const aiMsg = document.createElement('div');
            aiMsg.className = 'msg-ai';
            aiMsg.innerHTML = '<div class="text-xs text-gray-500 mb-1">🤖 AI</div><div class="text-sm"></div>';
            const bodyDiv = aiMsg.querySelector('.text-sm');
            let html;
            try { html = marked.parse(result.response); } catch (e) { html = result.response.replace(/</g,'&lt;'); }
            bodyDiv.innerHTML = DOMPurify.sanitize(html);
            msgsDiv.appendChild(aiMsg);
            if (window.MathJax) MathJax.typesetPromise();
            msgsDiv.scrollTop = msgsDiv.scrollHeight;
        }
    } catch (err) {
        alert('خطای شبکه: ' + err.message);
    }
    
    input.disabled = false;
    input.focus();
});

document.getElementById('input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        document.getElementById('chat-form').dispatchEvent(new Event('submit'));
    }
});
</script>

</body>
</html>
