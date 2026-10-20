<?php
// ============================================================
// api.php — REST API اصلی
// ============================================================
require_once __DIR__ . '/functions.php';
secure_session_start();

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key, X-Node-Token');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') exit(0);

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$path = trim(str_replace('/api', '', $path), '/');

check_rate_limit("api-$path", 60);

$pdo = Database::getInstance();
$action = $_POST['action'] ?? $_GET['action'] ?? $path;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify($_POST['csrf_token'] ?? '') or die(json_encode(['error' => 'CSRF invalid']));
}

// ====== Stats ======
if ($action === 'stats' || $path === 'stats') {
    echo json_encode(get_site_stats()); exit;
}

// ====== Submit factor ======
if ($action === 'factor_submit' || $path === 'factor/submit') {
    $input = json_decode(file_get_contents('php://input'), true) ?: $_POST;
    $n = $input['number'] ?? '';
    $factors = $input['factors'] ?? [];
    if (!$n || !is_array($factors)) { echo json_encode(['error' => 'missing']); exit; }
    $product = 1;
    foreach ($factors as $f) $product = gmp_mul($product, $f);
    if (gmp_cmp($product, $n) !== 0) { echo json_encode(['error' => 'invalid factors']); exit; }
    $result = factordb_submit_factors($n, $factors);
    $credited = $result['result']['credited'] ?? 0;
    $user = current_user();
    $stmt = $pdo->prepare("INSERT INTO factors (number, digits, factors, num_factors, is_prime, source, user_id, credited) VALUES (?,?,?,?,?,?,?,?)");
    $stmt->execute([$n, strlen((string)$n), json_encode($factors), count($factors), count($factors)==1?1:0, 'api', $user['id'] ?? null, $credited]);
    echo json_encode(['success' => true, 'credited' => $credited, 'factordb' => $result]); exit;
}

// ====== Comment on article ======
if ($action === 'comment_article') {
    if (!is_logged_in()) { echo json_encode(['error' => 'login required']); exit; }
    $user = current_user();
    $article_id = intval($_POST['article_id'] ?? 0);
    $content = sanitize_string($_POST['content'] ?? '', 1000);
    if (!$article_id || !$content) { echo json_encode(['error' => 'missing']); exit; }
    $stmt = $pdo->prepare("INSERT INTO comments (article_id, user_id, content, is_approved) VALUES (?, ?, ?, 1)");
    $stmt->execute([$article_id, $user['id'], $content]);
    echo json_encode(['success' => true]); exit;
}

// ====== Comment on lesson ======
if ($action === 'comment_lesson') {
    if (!is_logged_in()) { echo json_encode(['error' => 'login required']); exit; }
    $user = current_user();
    $lesson_id = intval($_POST['lesson_id'] ?? 0);
    $content = sanitize_string($_POST['content'] ?? '', 1000);
    if (!$lesson_id || !$content) { echo json_encode(['error' => 'missing']); exit; }
    $stmt = $pdo->prepare("INSERT INTO comments (lesson_id, user_id, content, is_approved) VALUES (?, ?, ?, 1)");
    $stmt->execute([$lesson_id, $user['id'], $content]);
    echo json_encode(['success' => true]); exit;
}

// ====== Mark lesson complete ======
if ($action === 'lesson_complete') {
    if (!is_logged_in()) { echo json_encode(['error' => 'login required']); exit; }
    $user = current_user();
    $lesson_id = intval($_POST['lesson_id'] ?? 0);
    if (!$lesson_id) { echo json_encode(['error' => 'missing']); exit; }
    $stmt = $pdo->prepare("INSERT INTO lesson_progress (lesson_id, user_id, status, progress_percent, completed_at) VALUES (?, ?, 'completed', 100, NOW()) ON DUPLICATE KEY UPDATE status='completed', progress_percent=100, completed_at=NOW()");
    $stmt->execute([$lesson_id, $user['id']]);
    $pdo->prepare("UPDATE lessons SET completions = completions + 1 WHERE id = ?")->execute([$lesson_id]);
    echo json_encode(['success' => true]); exit;
}

// ====== Get ranges ======
if ($action === 'ranges' || $path === 'ranges') {
    echo json_encode(get_ranges()); exit;
}

// ====== Get series ======
if ($action === 'series' || $path === 'series') {
    echo json_encode(get_math_series()); exit;
}

// ====== Get articles ======
if ($action === 'articles' || $path === 'articles') {
    $limit = min(intval($_GET['limit'] ?? 10), 50);
    echo json_encode(get_articles($limit)); exit;
}

// ====== Get lessons ======
if ($action === 'lessons' || $path === 'lessons') {
    $limit = min(intval($_GET['limit'] ?? 10), 50);
    echo json_encode(get_lessons($limit)); exit;
}

// ====== Get scientists ======
if ($action === 'scientists' || $path === 'scientists') {
    echo json_encode(get_scientists()); exit;
}

// ====== Generate API key ======
if ($action === 'apikey') {
    if (!is_logged_in()) { echo json_encode(['error' => 'login required']); exit; }
    $user = current_user();
    if (!empty($user['api_key'])) { echo json_encode(['api_key' => $user['api_key']]); exit; }
    $key = 'pmp_' . bin2hex(random_bytes(24));
    $pdo->prepare("UPDATE users SET api_key = ? WHERE id = ?")->execute([$key, $user['id']]);
    echo json_encode(['api_key' => $key]); exit;
}

// ====== 404 ======
http_response_code(404);
echo json_encode([
    'error' => 'Endpoint not found',
    'available' => ['stats', 'factor_submit', 'comment_article', 'comment_lesson', 'lesson_complete', 'ranges', 'series', 'articles', 'lessons', 'scientists', 'apikey'],
]);
