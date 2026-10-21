<?php
// ============================================================
// chat.php — چت بین‌المللی (WebSocket client)
// ============================================================
require_once __DIR__ . '/functions.php';
secure_session_start();
$lang = $_GET['lang'] ?? $_COOKIE['lang'] ?? 'fa';
$dir = in_array($lang, ['fa','ar','ur']) ? 'rtl' : 'ltr';
$user = current_user();
$jwt_token = '';
if ($user) { $jwt_token = generate_jwt($user['id'], $user['email']); }
$chat_server_url = Settings::get('chat_server_url', (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off' ? 'wss' : 'ws') . '://' . ($_SERVER['HTTP_HOST'] ?? 'localhost') . ':8080');
$pdo = Database::getInstance();
try { $rooms = $pdo->query("SELECT id, name, name_en, name_ar, category, icon FROM chat_rooms WHERE is_active = 1 ORDER BY category, name")->fetchAll(); } catch (Exception $e) { $rooms = []; }
?>
<!DOCTYPE html>
<html lang="<?= $lang ?>" dir="<?= $dir ?>">
<head>
<meta charset="UTF-8">
    <link rel="canonical" href="<?= site_url() ?>/chat.php">

<title>💬 چت بین‌المللی</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.min.js"></script>
<style>
body{font-family:'Vazirmatn',Tahoma,sans-serif;height:100vh;overflow:hidden}
.chat-msg{padding:8px 12px;border-radius:8px;margin:4px 0}
.chat-own{background:#dbeafe}
.chat-msg:hover{background:#f9fafb}
.online-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#10b981}
</style>
</head>
<body class="bg-gray-100 flex flex-col">
<header class="bg-white shadow-sm px-4 py-2 flex justify-between items-center flex-shrink-0">
    <div class="flex items-center gap-3"><span class="text-2xl">💬</span><h1 class="text-lg font-bold">چت بین‌المللی</h1></div>
    <div class="flex items-center gap-2">
        <span id="conn-status" class="px-2 py-1 rounded text-xs bg-red-100 text-red-700">🔴 متصل نشده</span>
        <a href="index.php" class="px-3 py-1 bg-gray-100 rounded text-sm">🏠</a>
    </div>
</header>

<?php if (!$user): ?>
<div class="flex-1 flex items-center justify-center">
    <div class="bg-white rounded-xl shadow p-8 max-w-md text-center">
        <div class="text-5xl mb-3">🔐</div>
        <h2 class="text-xl font-bold mb-2">برای چت باید وارد شوید</h2>
        <a href="auth/phone.php" class="inline-block bg-emerald-600 text-white px-4 py-2 rounded text-sm">📱 ورود</a>
    </div>
</div>
<?php else: ?>

<div class="flex-1 flex overflow-hidden">
    <aside class="bg-white w-64 border-l flex-shrink-0 overflow-y-auto">
        <div class="p-3 border-b"><h2 class="font-bold text-sm text-gray-700 mb-2">📂 روم‌ها</h2></div>
        <div id="rooms-list" class="space-y-1 p-2">
            <?php if (empty($rooms)): ?><p class="text-xs text-gray-400 text-center">رومی نیست</p>
            <?php else: foreach ($rooms as $r): ?>
            <div onclick="joinRoom(<?= $r['id'] ?>)" class="cursor-pointer p-2 rounded hover:bg-blue-50 flex items-center gap-2" id="room-<?= $r['id'] ?>">
                <span class="text-xl"><?= $r['icon'] ?? '💬' ?></span>
                <div class="flex-1 min-w-0">
                    <div class="font-medium text-sm truncate"><?= sanitize($lang=='fa' ? $r['name'] : ($lang=='ar' ? ($r['name_ar'] ?? $r['name_en']) : $r['name_en'])) ?></div>
                    <div class="text-xs text-gray-400"><?= $r['category'] ?></div>
                </div>
            </div>
            <?php endforeach; endif; ?>
        </div>
    </aside>
    
    <main class="flex-1 flex flex-col">
        <div id="room-header" class="bg-white border-b px-4 py-2 flex items-center justify-between">
            <div class="flex items-center gap-2">
                <span id="room-icon" class="text-2xl">💬</span>
                <h2 id="room-title" class="font-bold text-gray-800">روم را انتخاب کنید</h2>
            </div>
        </div>
        <div id="messages" class="flex-1 overflow-y-auto p-3 bg-gray-50"></div>
        <form id="msg-form" class="bg-white border-t p-3 flex gap-2">
            <button type="button" id="latex-toggle" class="px-2 py-1 bg-purple-100 text-purple-700 rounded text-sm" title="LaTeX">∑</button>
            <button type="button" id="voice-btn" class="px-2 py-1 bg-red-100 text-red-700 rounded text-sm" title="چت صوتی">🎤</button>
            <textarea id="msg-input" placeholder="پیام بنویسید... (Enter ارسال)" class="flex-1 px-3 py-2 border rounded text-sm" rows="1" maxlength="500"></textarea>
            <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded text-sm">📤</button>
        </form>
        <div id="voice-status" class="hidden px-4 py-1 text-sm text-red-600 bg-red-50">🔴 در حال ضبط صدا... (دوباره کلیک برای توقف)</div>
    </main>
</div>

<script>
const TOKEN = '<?= $jwt_token ?>';
const WS_URL = '<?= $chat_server_url ?>';
const CURRENT_USER = {id: <?= intval($user['id']) ?>, name: <?= json_encode($user['name'] ?? $user['email']) ?>};
let ws = null, currentRoomId = null, typingTimer = null;

function connect() {
    ws = new WebSocket(WS_URL + '?token=' + encodeURIComponent(TOKEN));
    ws.onopen = () => { document.getElementById('conn-status').className = 'px-2 py-1 rounded text-xs bg-green-100 text-green-700'; document.getElementById('conn-status').textContent = '🟢 متصل'; };
    ws.onmessage = (e) => { handleMessage(JSON.parse(e.data)); };
    ws.onclose = () => { document.getElementById('conn-status').className = 'px-2 py-1 rounded text-xs bg-red-100 text-red-700'; document.getElementById('conn-status').textContent = '🔴 قطع'; setTimeout(connect, 3000); };
    ws.onerror = (e) => console.error(e);
}

function handleMessage(d) {
    switch (d.type) {
        case 'connected': console.log('Connected'); break;
        case 'room_joined': currentRoomId = d.room.id;
            document.getElementById('room-icon').textContent = d.room.icon || '💬';
            document.getElementById('room-title').textContent = d.room.name_fa || d.room.name_en || d.room.name;
            document.getElementById('messages').innerHTML = '';
            if (d.recentMessages) d.recentMessages.forEach(m => renderMessage(m));
            if (window.MathJax) MathJax.typesetPromise();
            break;
        case 'message': renderMessage(d); if (window.MathJax) MathJax.typesetPromise(); break;
        case 'user_joined': showSysMsg(d.name + ' وارد شد'); break;
        case 'user_left': showSysMsg(d.name + ' خارج شد'); break;
        case 'typing': if (d.userId != CURRENT_USER.id) { /* show typing */ } break;
        case 'error': alert('خطا: ' + d.message); break;
    }
}

function escapeHtml(s) { return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function renderMessage(m) {
    const div = document.getElementById('messages');
    const isOwn = m.userId == CURRENT_USER.id;
    const time = new Date(m.timestamp * 1000).toLocaleTimeString('fa-IR', {hour: '2-digit', minute: '2-digit'});
    const name = isOwn ? 'شما' : (m.name || 'کاربر');
    let content = escapeHtml(m.content);
    if (m.msgType === 'latex' || m.content.match(/\\\(.*\\\)/)) content = content;
    const el = document.createElement('div');
    el.className = 'chat-msg ' + (isOwn ? 'chat-own' : '');
    el.innerHTML = '<div class="flex items-baseline gap-2 mb-1"><span class="font-medium text-xs ' + (isOwn?'text-blue-700':'text-gray-700') + '">' + escapeHtml(name) + '</span><span class="text-xs text-gray-400">' + time + '</span></div><div class="text-sm">' + content + '</div>';
    div.appendChild(el);
    div.scrollTop = div.scrollHeight;
}

function showSysMsg(t) {
    const div = document.getElementById('messages');
    const el = document.createElement('div');
    el.className = 'text-center text-xs text-gray-400 py-1';
    el.textContent = t;
    div.appendChild(el);
    div.scrollTop = div.scrollHeight;
}

function joinRoom(id) {
    if (!ws || ws.readyState !== WebSocket.OPEN) { alert('اتصال برقرار نیست'); return; }
    document.querySelectorAll('[id^="room-"]').forEach(el => el.classList.remove('bg-blue-100'));
    document.getElementById('room-' + id).classList.add('bg-blue-100');
    ws.send(JSON.stringify({type: 'join_room', payload: {roomId: id}}));
}

document.getElementById('msg-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const input = document.getElementById('msg-input');
    const content = input.value.trim();
    if (!content || !currentRoomId || !ws) return;
    const msgType = (content.includes('\\(') || content.includes('$$')) ? 'latex' : 'text';
    ws.send(JSON.stringify({type: 'send_message', payload: {roomId: currentRoomId, content, type: msgType}}));
    input.value = '';
});

document.getElementById('msg-input').addEventListener('input', () => {
    if (currentRoomId && ws) ws.send(JSON.stringify({type: 'typing', payload: {roomId: currentRoomId}}));
});

document.getElementById('msg-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); document.getElementById('msg-form').dispatchEvent(new Event('submit')); }
});

// ====== Voice Chat (Web Speech API) ======
let recognition = null;
let isRecording = false;

const voiceBtn = document.getElementById('voice-btn');
const voiceStatus = document.getElementById('voice-status');

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SR();
    recognition.lang = 'fa-IR';
    recognition.continuous = true;
    recognition.interimResults = true;
    
    recognition.onresult = (e) => {
        let transcript = '';
        for (let i = e.resultIndex; i < e.results.length; i++) {
            transcript += e.results[i][0].transcript;
        }
        document.getElementById('msg-input').value = transcript;
    };
    
    recognition.onerror = (e) => { console.log('Voice error:', e.error); };
    recognition.onend = () => {
        isRecording = false;
        voiceBtn.classList.remove('bg-red-600', 'text-white');
        voiceBtn.classList.add('bg-red-100', 'text-red-700');
        voiceStatus.classList.add('hidden');
    };
    
    voiceBtn.addEventListener('click', () => {
        if (isRecording) {
            recognition.stop();
        } else {
            recognition.lang = document.getElementById('voice-lang')?.value || 'fa-IR';
            recognition.start();
            isRecording = true;
            voiceBtn.classList.remove('bg-red-100', 'text-red-700');
            voiceBtn.classList.add('bg-red-600', 'text-white');
            voiceStatus.classList.remove('hidden');
        }
    });
} else {
    voiceBtn.style.opacity = '0.5';
    voiceBtn.title = 'مرورگر شما از چت صوتی پشتیبانی نمی‌کند';
}

// ====== Text-to-Speech (خواندن پیام‌های دریافتی) ======
function speakMessage(text) {
    if (!('speechSynthesis' in window)) return;
    // حذف HTML tags
    const clean = text.replace(/<[^>]*>/g, '').replace(/\\[()\\]/g, '');
    if (clean.length > 200) return; // فقط پیام‌های کوتاه
    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.lang = 'fa-IR';
    utterance.rate = 1.0;
    speechSynthesis.speak(utterance);
}

connect();
</script>
<?php endif; ?>
</body>
</html>
