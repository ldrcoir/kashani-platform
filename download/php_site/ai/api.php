<?php
// ============================================================
// ai/api.php — API برای AI (chat, generate, translate)
// ============================================================
require_once __DIR__ . '/../functions.php';
secure_session_start();

header('Content-Type: application/json; charset=utf-8');
check_rate_limit('ai-api', 30);

$action = $_POST['action'] ?? $_GET['action'] ?? '';

if (!is_logged_in()) { http_response_code(401); echo json_encode(['error' => 'login required']); exit; }
$user = current_user();
if (!can_use_ai()) { http_response_code(403); echo json_encode(['error' => 'AI access required']); exit; }

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify($_POST['csrf_token'] ?? '') or die(json_encode(['error' => 'CSRF invalid']));
}

$pdo = Database::getInstance();

if ($action === 'ai_send') {
    $conv_id = intval($_POST['conv_id'] ?? 0);
    $message = trim($_POST['message'] ?? '');
    
    if (!$message) { echo json_encode(['error' => 'empty message']); exit; }
    if (strlen($message) > 2000) { echo json_encode(['error' => 'message too long']); exit; }
    
    // Get or create conversation
    if ($conv_id) {
        $stmt = $pdo->prepare("SELECT * FROM ai_conversations WHERE id = ? AND user_id = ?");
        $stmt->execute([$conv_id, $user['id']]);
        $conv = $stmt->fetch();
        if (!$conv) { echo json_encode(['error' => 'conversation not found']); exit; }
        $messages = json_decode($conv['messages'], true) ?: [];
    } else {
        // Create new conversation
        $title = mb_substr($message, 0, 50);
        $stmt = $pdo->prepare("INSERT INTO ai_conversations (user_id, title, messages, provider, model) VALUES (?, ?, '[]', ?, ?)");
        $stmt->execute([$user['id'], $title, Settings::get('ai_provider', 'zai'), Settings::get('ai_model', 'glm-4.6')]);
        $conv_id = $pdo->lastInsertId();
        $messages = [];
    }
    
    // Add user message
    $messages[] = ['role' => 'user', 'content' => $message, 'time' => time()];
    
    // Get system prompt
    $system_prompt = Settings::get('ai_system_prompt', "تو یک دستیار علمی هستی. به فارسی پاسخ بده. در زمینه‌ی ریاضی، فیزیک، پزشکی، داروسازی، کامپیوتر و علوم تخصصی. اگر کد لازم است، با markdown بنویس. مختصر و دقیق باش.");
    
    // Build messages for API call
    $api_messages = [['role' => 'system', 'content' => $system_prompt]];
    foreach (array_slice($messages, -10) as $m) {
        $api_messages[] = ['role' => $m['role'], 'content' => $m['content']];
    }
    
    // Call AI provider
    $response = call_ai_provider($api_messages);
    
    if (isset($response['error'])) {
        echo json_encode(['error' => $response['error']]); exit;
    }
    
    $ai_response = $response['content'];
    
    // Add AI message
    $messages[] = ['role' => 'assistant', 'content' => $ai_response, 'time' => time()];
    
    // Save
    $stmt = $pdo->prepare("UPDATE ai_conversations SET messages = ?, updated_at = NOW() WHERE id = ?");
    $stmt->execute([json_encode($messages, JSON_UNESCAPED_UNICODE), $conv_id]);
    
    echo json_encode(['success' => true, 'conv_id' => intval($conv_id), 'response' => $ai_response]);
    exit;
}

if ($action === 'ai_new_conv') {
    $stmt = $pdo->prepare("INSERT INTO ai_conversations (user_id, title, messages, provider, model) VALUES (?, 'گفتگوی جدید', '[]', ?, ?)");
    $stmt->execute([$user['id'], Settings::get('ai_provider', 'zai'), Settings::get('ai_model', 'glm-4.6')]);
    echo json_encode(['success' => true, 'conv_id' => intval($pdo->lastInsertId())]);
    exit;
}

if ($action === 'ai_translate') {
    $text = trim($_POST['text'] ?? '');
    $from = $_POST['from_lang'] ?? 'fa';
    $to = $_POST['to_lang'] ?? 'en';
    
    if (!$text) { echo json_encode(['error' => 'empty text']); exit; }
    
    $prompt = "Translate the following text from $from to $to. Keep technical terms. Only respond with the translation:\n\n$text";
    $api_messages = [
        ['role' => 'system', 'content' => 'You are a professional translator for scientific texts.'],
        ['role' => 'user', 'content' => $prompt]
    ];
    
    $response = call_ai_provider($api_messages);
    if (isset($response['error'])) { echo json_encode(['error' => $response['error']]); exit; }
    
    echo json_encode(['success' => true, 'translation' => $response['content']]);
    exit;
}

if ($action === 'ai_generate_article') {
    if (!in_array($user['role'], ['admin', 'superadmin'])) {
        echo json_encode(['error' => 'admin only']); exit;
    }
    $topic = trim($_POST['topic'] ?? '');
    $lang = $_POST['lang'] ?? 'fa';
    if (!$topic) { echo json_encode(['error' => 'empty topic']); exit; }
    
    $prompt = "Write an article about '$topic' in $lang language. Include title (HTML h2), excerpt (p), main content with sections. Use HTML tags. Maximum 800 words.";
    $api_messages = [
        ['role' => 'system', 'content' => 'You are a professional science writer.'],
        ['role' => 'user', 'content' => $prompt]
    ];
    
    $response = call_ai_provider($api_messages);
    if (isset($response['error'])) { echo json_encode(['error' => $response['error']]); exit; }
    
    echo json_encode(['success' => true, 'article' => $response['content']]);
    exit;
}

echo json_encode(['error' => 'unknown action']);

// ====== AI provider ======
function call_ai_provider($messages) {
    $provider = Settings::get('ai_provider', 'zai');
    $api_key = Settings::get('ai_api_key', '');
    $model = Settings::get('ai_model', 'glm-4.6');
    $max_tokens = intval(Settings::get('ai_max_tokens', '1000'));
    $temperature = floatval(Settings::get('ai_temperature', '0.7'));
    
    if (!$api_key) return ['error' => 'AI API key not configured'];
    
    if ($provider === 'zai') {
        return call_zai($api_key, $model, $messages, $max_tokens, $temperature);
    } elseif ($provider === 'openai') {
        return call_openai($api_key, $model, $messages, $max_tokens, $temperature);
    } elseif ($provider === 'claude') {
        return call_claude($api_key, $model, $messages, $max_tokens, $temperature);
    } elseif ($provider === 'gemini') {
        return call_gemini($api_key, $model, $messages, $max_tokens, $temperature);
    }
    return ['error' => 'unknown provider: ' . $provider];
}

function call_zai($api_key, $model, $messages, $max_tokens, $temperature) {
    $payload = json_encode([
        'model' => $model,
        'messages' => $messages,
        'max_tokens' => $max_tokens,
        'temperature' => $temperature,
    ]);
    
    $ch = curl_init('https://api.z.ai/api/paas/v4/chat/completions');
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => [
            'Content-Type: application/json',
            'Authorization: Bearer ' . $api_key,
        ],
        CURLOPT_POSTFIELDS => $payload,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 60,
    ]);
    $response = curl_exec($ch);
    $http = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($http !== 200) return ['error' => 'Z.ai HTTP ' . $http . ': ' . $response];
    
    $data = json_decode($response, true);
    return ['content' => $data['choices'][0]['message']['content'] ?? ''];
}

function call_openai($api_key, $model, $messages, $max_tokens, $temperature) {
    $payload = json_encode([
        'model' => $model,
        'messages' => $messages,
        'max_tokens' => $max_tokens,
        'temperature' => $temperature,
    ]);
    
    $ch = curl_init('https://api.openai.com/v1/chat/completions');
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => [
            'Content-Type: application/json',
            'Authorization: Bearer ' . $api_key,
        ],
        CURLOPT_POSTFIELDS => $payload,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 60,
    ]);
    $response = curl_exec($ch);
    $http = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($http !== 200) return ['error' => 'OpenAI HTTP ' . $http];
    $data = json_decode($response, true);
    return ['content' => $data['choices'][0]['message']['content'] ?? ''];
}

function call_claude($api_key, $model, $messages, $max_tokens, $temperature) {
    $system_msg = '';
    $user_msgs = [];
    foreach ($messages as $m) {
        if ($m['role'] === 'system') $system_msg = $m['content'];
        else $user_msgs[] = $m;
    }
    
    $payload = json_encode([
        'model' => $model,
        'max_tokens' => $max_tokens,
        'system' => $system_msg,
        'messages' => $user_msgs,
    ]);
    
    $ch = curl_init('https://api.anthropic.com/v1/messages');
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => [
            'Content-Type: application/json',
            'x-api-key: ' . $api_key,
            'anthropic-version: 2023-06-01',
        ],
        CURLOPT_POSTFIELDS => $payload,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 60,
    ]);
    $response = curl_exec($ch);
    $http = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($http !== 200) return ['error' => 'Claude HTTP ' . $http];
    $data = json_decode($response, true);
    return ['content' => $data['content'][0]['text'] ?? ''];
}

function call_gemini($api_key, $model, $messages, $max_tokens, $temperature) {
    $contents = [];
    $system_msg = '';
    foreach ($messages as $m) {
        if ($m['role'] === 'system') { $system_msg = $m['content']; continue; }
        $role = $m['role'] === 'assistant' ? 'model' : 'user';
        $contents[] = ['role' => $role, 'parts' => [['text' => $m['content']]]];
    }
    
    $url = "https://generativelanguage.googleapis.com/v1beta/models/$model:generateContent?key=" . $api_key;
    $payload = json_encode([
        'contents' => $contents,
        'systemInstruction' => ['parts' => [['text' => $system_msg]]],
        'generationConfig' => ['maxOutputTokens' => $max_tokens, 'temperature' => $temperature],
    ]);
    
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_POSTFIELDS => $payload,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 60,
    ]);
    $response = curl_exec($ch);
    $http = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($http !== 200) return ['error' => 'Gemini HTTP ' . $http];
    $data = json_decode($response, true);
    return ['content' => $data['candidates'][0]['content']['parts'][0]['text'] ?? ''];
}
