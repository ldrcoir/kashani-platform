<?php
// config.php — تنظیمات (از env vars یا .env)
$db_host = getenv('DB_HOST') ?: 'localhost';
$db_name = getenv('DB_NAME') ?: 'science';
$db_user = getenv('DB_USER') ?: 'root';
$db_pass = getenv('DB_PASS') ?: '';
// Load .env if exists
$env_file = __DIR__ . '/.env';
if (file_exists($env_file)) {
    foreach (file($env_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
        if (strpos($line, '#') === 0) continue;
        if (strpos($line, '=') === false) continue;
        list($k, $v) = explode('=', $line, 2);
        $k = trim($k); $v = trim($v);
        if (getenv($k) === false) putenv("$k=$v");
        if (!isset($_ENV[$k])) $_ENV[$k] = $v;
        $$k = $v;
    }
}
define('DB_HOST', getenv('DB_HOST') ?: $db_host);
define('DB_NAME', getenv('DB_NAME') ?: $db_name);
define('DB_USER', getenv('DB_USER') ?: $db_user);
define('DB_PASS', getenv('DB_PASS') ?: $db_pass);
define('DB_CHARSET', 'utf8mb4');

define('FACTORDB_API', getenv('FACTORDB_API') ?: 'https://factordb.com:4059/rpc');
define('JWT_SECRET', getenv('JWT_SECRET') ?: bin2hex(random_bytes(32)));
define('SESSION_LIFETIME', 86400 * 7);

define('ROOT_DIR', __DIR__);
define('UPLOAD_DIR', ROOT_DIR . '/uploads/');
define('CACHE_DIR', ROOT_DIR . '/cache/');
define('LOG_DIR', ROOT_DIR . '/logs/');

foreach ([UPLOAD_DIR, CACHE_DIR, LOG_DIR] as $dir) {
    if (!is_dir($dir)) @mkdir($dir, 0755, true);
}

error_reporting(E_ALL);
ini_set('display_errors', 0);
ini_set('log_errors', 1);
ini_set('error_log', LOG_DIR . 'error.log');

date_default_timezone_set('Asia/Tehran');
define('APP_VERSION', '2.0.0');
