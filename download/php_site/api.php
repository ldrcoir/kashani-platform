<?php
// ============================================================
// api.php — REST API برای سایت
// ثبت فاکتور، گرفتن credit، استفاده از سایت
// ============================================================

session_start();
require_once __DIR__ . '/functions.php';

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') exit(0);

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$path = trim(str_replace('/api', '', $path), '/');

// API key auth
function get_api_user() {
    $headers = getallheaders();
    $api_key = $headers['X-API-Key'] ?? $headers['x-api-key'] ?? '';
    if (!$api_key) return null;
    $pdo = Database::getInstance();
    $stmt = $pdo->prepare("SELECT * FROM users WHERE api_key = ? AND api_key IS NOT NULL");
    $stmt->execute([$api_key]);
    return $stmt->fetch();
}

// Generate API key for user
function generate_api_key($user_id) {
    $key = 'pmp_' . bin2hex(random_bytes(24));
    $pdo = Database::getInstance();
    $pdo->prepare("UPDATE users SET api_key = ? WHERE id = ?")->execute([$key, $user_id]);
    return $key;
}

// Routes
switch ($path) {
    // ===== Stats =====
    case 'stats':
        echo json_encode(get_site_stats());
        break;

    // ===== FactorDB contributions =====
    case 'contributions':
        echo json_encode(factordb_get_contributions());
        break;

    // ===== Submit factor =====
    case 'factor/submit':
        if ($method !== 'POST') {
            http_response_code(405);
            echo json_encode(['error' => 'Method not allowed']);
            break;
        }
        $input = json_decode(file_get_contents('php://input'), true);
        $n = $input['number'] ?? '';
        $factors = $input['factors'] ?? [];

        if (!$n || !is_array($factors)) {
            http_response_code(400);
            echo json_encode(['error' => 'Missing number or factors']);
            break;
        }

        // Verify factors
        $product = 1;
        foreach ($factors as $f) $product *= $f;
        if ($product != $n) {
            http_response_code(400);
            echo json_encode(['error' => 'Factors do not multiply to number']);
            break;
        }

        // Submit to FactorDB
        $result = factordb_submit_factors($n, $factors);
        $credited = $result['result']['credited'] ?? 0;

        // Save in local DB
        $pdo = Database::getInstance();
        $user = get_api_user();
        $stmt = $pdo->prepare("INSERT INTO factors (number, digits, factors, num_factors, is_prime, source, user_id, credited) VALUES (?,?,?,?,?,?,?,?)");
        $stmt->execute([
            $n, strlen((string)$n), json_encode($factors), count($factors),
            count($factors) == 1 ? 1 : 0, 'api', $user['id'] ?? null, $credited
        ]);

        echo json_encode([
            'success' => true,
            'number' => $n,
            'factors' => $factors,
            'credited' => $credited,
            'factordb_result' => $result,
        ]);
        break;

    // ===== Get ranges =====
    case 'ranges':
        echo json_encode(get_ranges());
        break;

    // ===== Get frontier =====
    case 'frontier':
        echo json_encode(['frontier' => get_frontier()]);
        break;

    // ===== Get math series =====
    case 'series':
        echo json_encode(get_math_series());
        break;

    // ===== Get articles =====
    case 'articles':
        $limit = min(intval($_GET['limit'] ?? 10), 50);
        echo json_encode(get_articles($limit));
        break;

    // ===== Get API key (requires login) =====
    case 'apikey':
        if (!is_logged_in()) {
            http_response_code(401);
            echo json_encode(['error' => 'Login required']);
            break;
        }
        $user = current_user();
        if ($user['api_key']) {
            echo json_encode(['api_key' => $user['api_key']]);
        } else {
            $key = generate_api_key($user['id']);
            echo json_encode(['api_key' => $key]);
        }
        break;

    // ===== Volunteer compute node register =====
    case 'node/register':
        if ($method !== 'POST') {
            http_response_code(405);
            echo json_encode(['error' => 'Method not allowed']);
            break;
        }
        $input = json_decode(file_get_contents('php://input'), true);
        $user = get_api_user();
        if (!$user) {
            http_response_code(401);
            echo json_encode(['error' => 'Invalid API key']);
            break;
        }
        $pdo = Database::getInstance();
        $stmt = $pdo->prepare("INSERT INTO compute_nodes (user_id, node_name, os, cpu_cores, ram_mb, is_active) VALUES (?,?,?,?,?,1)");
        $stmt->execute([
            $user['id'],
            $input['node_name'] ?? 'Unknown',
            $input['os'] ?? php_uname(),
            $input['cpu_cores'] ?? 1,
            $input['ram_mb'] ?? 1024,
        ]);
        $node_id = $pdo->lastInsertId();
        echo json_encode(['success' => true, 'node_id' => $node_id]);
        break;

    // ===== Volunteer compute node heartbeat =====
    case 'node/heartbeat':
        if ($method !== 'POST') {
            http_response_code(405);
            echo json_encode(['error' => 'Method not allowed']);
            break;
        }
        $input = json_decode(file_get_contents('php://input'), true);
        $node_id = $input['node_id'] ?? 0;
        $work_done = $input['work_done'] ?? 0;
        $pdo = Database::getInstance();
        $pdo->prepare("UPDATE compute_nodes SET last_seen = NOW(), total_work = total_work + ?, is_active = 1 WHERE id = ?")
            ->execute([$work_done, $node_id]);
        echo json_encode(['success' => true, 'status' => 'ok']);
        break;

    // ===== AI chat (admin only) =====
    case 'ai/chat':
        if (!can_use_ai()) {
            http_response_code(403);
            echo json_encode(['error' => 'AI access required']);
            break;
        }
        $input = json_decode(file_get_contents('php://input'), true);
        $message = $input['message'] ?? '';
        // Simple response for now — will connect to AI engine later
        echo json_encode([
            'response' => 'AI is being configured. Your message: ' . sanitize($message),
            'timestamp' => date('c'),
        ]);
        break;

    default:
        http_response_code(404);
        echo json_encode([
            'error' => 'Endpoint not found',
            'available_endpoints' => [
                'GET /api/stats',
                'GET /api/contributions',
                'POST /api/factor/submit',
                'GET /api/ranges',
                'GET /api/frontier',
                'GET /api/series',
                'GET /api/articles',
                'GET /api/apikey',
                'POST /api/node/register',
                'POST /api/node/heartbeat',
                'POST /api/ai/chat',
            ]
        ]);
}
