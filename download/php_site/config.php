<?php
// ============================================================
// config.php — تنظیمات اصلی سایت
// پلتفرم ریاضی پارسی — به افتخار Jamshid al-Kashi (الکاشی)
// ============================================================

// Database (MySQL — cPanel compatible)
define('DB_HOST', 'localhost');
define('DB_NAME', 'persian_math');
define('DB_USER', 'root');
define('DB_PASS', '');
define('DB_CHARSET', 'utf8mb4');

// FactorDB API
define('FACTORDB_API', 'https://factordb.com:4059/rpc');
define('FACTORDB_TOKEN', '6ddb5c17a56f920f3ee459e99036bd57');

// Site settings
define('SITE_NAME', 'پلتفرم ریاضی پارسی');
define('SITE_NAME_EN', 'Persian Math Platform');
define('SITE_DEDICATED', 'به افتخار Jamshid al-Kashi (الکاشی)');
define('SITE_URL', 'https://persian-math.ir');
define('SITE_VERSION', '1.0.0');

// Languages
define('LANGUAGES', json_encode(['fa', 'en', 'ar']));

// Security
define('JWT_SECRET', 'CHANGE_THIS_TO_RANDOM_STRING');
define('SESSION_LIFETIME', 86400 * 7); // 7 days

// Google OAuth
define('GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID');
define('GOOGLE_CLIENT_SECRET', 'YOUR_GOOGLE_CLIENT_SECRET');
define('GOOGLE_REDIRECT', SITE_URL . '/auth/google-callback.php');

// SMS (Iranian phone verification)
define('SMS_API_KEY', 'YOUR_SMS_API_KEY');
define('SMS_SENDER', '3000');

// File paths
define('UPLOAD_DIR', __DIR__ . '/uploads/');
define('CACHE_DIR', __DIR__ . '/cache/');

// Error reporting (disable in production)
error_reporting(E_ALL);
ini_set('display_errors', 0);
ini_set('log_errors', 1);
ini_set('error_log', __DIR__ . '/error.log');

// Timezone
date_default_timezone_set('Asia/Tehran');

// Create directories
foreach ([UPLOAD_DIR, CACHE_DIR] as $dir) {
    if (!is_dir($dir)) mkdir($dir, 0755, true);
}
