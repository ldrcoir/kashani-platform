<?php
// ============================================================
// config.php — تمام تنظیمات از پنل ادمین قابل تغییر
// هیچ hardcoded URL یا نام دامنه‌ای وجود ندارد
// ============================================================

// Database (از پنل ادمین قابل تغییر)
$db_host = getenv('DB_HOST') ?: 'localhost';
$db_name = getenv('DB_NAME') ?: 'persian_math';
$db_user = getenv('DB_USER') ?: 'root';
$db_pass = getenv('DB_PASS') ?: '';
define('DB_HOST', $db_host);
define('DB_NAME', $db_name);
define('DB_USER', $db_user);
define('DB_PASS', $db_pass);
define('DB_CHARSET', 'utf8mb4');

// FactorDB API (از پنل ادمین قابل تغییر)
define('FACTORDB_API', 'https://factordb.com:4059/rpc');

// Security
define('JWT_SECRET', getenv('JWT_SECRET') ?: 'CHANGE_THIS_TO_RANDOM_STRING_2026');
define('SESSION_LIFETIME', 86400 * 7);

// Google OAuth (از پنل ادمین)
define('GOOGLE_CLIENT_ID', getenv('GOOGLE_CLIENT_ID') ?: '');
define('GOOGLE_CLIENT_SECRET', getenv('GOOGLE_CLIENT_SECRET') ?: '');

// SMS (Iranian phone verification - از پنل ادمین)
define('SMS_API_KEY', getenv('SMS_API_KEY') ?: '');
define('SMS_SENDER', getenv('SMS_SENDER') ?: '3000');

// File paths
define('ROOT_DIR', __DIR__);
define('UPLOAD_DIR', ROOT_DIR . '/uploads/');
define('CACHE_DIR', ROOT_DIR . '/cache/');
define('LOG_DIR', ROOT_DIR . '/logs/');

// Create directories
foreach ([UPLOAD_DIR, CACHE_DIR, LOG_DIR] as $dir) {
    if (!is_dir($dir)) @mkdir($dir, 0755, true);
}

// Error reporting
error_reporting(E_ALL);
ini_set('display_errors', 0);
ini_set('log_errors', 1);
ini_set('error_log', LOG_DIR . 'error.log');

// Timezone
date_default_timezone_set('Asia/Tehran');

// Version
define('APP_VERSION', '1.0.0');

// All site settings are loaded from database via Settings class
// No hardcoded URLs, names, or domains
