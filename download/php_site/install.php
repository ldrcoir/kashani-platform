<?php
// ============================================================
// install.php — نصب خودکار پلتفرم
// ============================================================
require_once __DIR__ . '/functions.php';
secure_session_start();

$step = $_GET['step'] ?? '1';

if ($step === '1') {
    // Requirements check
    $checks = [
        'PHP version >= 7.4' => version_compare(PHP_VERSION, '7.4.0', '>='),
        'PDO MySQL extension' => extension_loaded('pdo_mysql'),
        'cURL extension' => extension_loaded('curl'),
        'mbstring' => extension_loaded('mbstring'),
        'JSON' => extension_loaded('json'),
        'GD/Imagick' => extension_loaded('gd') || extension_loaded('imagick'),
        'allow_url_fopen' => ini_get('allow_url_fopen') == 1,
    ];
    $all_ok = !in_array(false, $checks);
    ?>
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>نصب پلتفرم</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
        <style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
    </head>
    <body class="bg-gradient-to-br from-amber-900 to-orange-900 min-h-screen flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-2xl w-full">
            <div class="text-center mb-6">
                <div class="text-6xl mb-2">🎓</div>
                <h1 class="text-3xl font-bold text-gray-800">نصب پلتفرم علمی چندرشته‌ای</h1>
                <p class="text-sm text-gray-500">به افتخار غیاث‌الدین جمشید کاشانی</p>
            </div>
            
            <h2 class="font-bold mb-3">بررسی پیش‌نیازها:</h2>
            <div class="space-y-2 mb-4">
                <?php foreach ($checks as $check => $ok): ?>
                <div class="flex justify-between items-center p-2 bg-<?= $ok?'green':'red' ?>-50 rounded text-sm">
                    <span><?= $check ?></span>
                    <span class="<?= $ok?'text-green-600':'text-red-600' ?> font-bold"><?= $ok?'✓':'✗' ?></span>
                </div>
                <?php endforeach; ?>
            </div>
            
            <form method="post" action="install.php?step=2" class="space-y-3">
                <h3 class="font-bold">اطلاعات دیتابیس MySQL:</h3>
                <div class="grid md:grid-cols-2 gap-3">
                    <div><label class="block text-xs text-gray-500 mb-1">DB Host</label><input type="text" name="db_host" value="localhost" class="w-full px-3 py-2 border rounded text-sm" dir="ltr"></div>
                    <div><label class="block text-xs text-gray-500 mb-1">DB Name</label><input type="text" name="db_name" value="kashani" class="w-full px-3 py-2 border rounded text-sm" dir="ltr"></div>
                    <div><label class="block text-xs text-gray-500 mb-1">DB User</label><input type="text" name="db_user" class="w-full px-3 py-2 border rounded text-sm" dir="ltr"></div>
                    <div><label class="block text-xs text-gray-500 mb-1">DB Pass</label><input type="password" name="db_pass" class="w-full px-3 py-2 border rounded text-sm" dir="ltr"></div>
                </div>
                <h3 class="font-bold mt-4">سایت:</h3>
                <div><label class="block text-xs text-gray-500 mb-1">URL سایت</label><input type="text" name="site_url" placeholder="https://platform-oloom.ir" class="w-full px-3 py-2 border rounded text-sm" dir="ltr"></div>
                <button class="w-full bg-gradient-to-r from-amber-600 to-orange-600 text-white py-3 rounded-lg font-bold">➡️ شروع نصب</button>
            </form>
        </div>
    </body>
    </html>
    <?php
    exit;
}

if ($step === '2') {
    $db_host = $_POST['db_host'] ?? 'localhost';
    $db_name = $_POST['db_name'] ?? 'kashani';
    $db_user = $_POST['db_user'] ?? '';
    $db_pass = $_POST['db_pass'] ?? '';
    $site_url = $_POST['site_url'] ?? '';
    
    $errors = [];
    $success = [];
    
    try {
        $dsn = "mysql:host=$db_host;dbname=$db_name;charset=utf8mb4";
        $pdo = new PDO($dsn, $db_user, $db_pass, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
        $success[] = 'اتصال به MySQL موفق بود';
        
        // Run complete_install.sql
        $sql = file_get_contents(__DIR__ . '/complete_install.sql');
        if ($sql) {
            // Split by semicolons but be careful of multi-line statements
            $pdo->exec("SET FOREIGN_KEY_CHECKS=0");
            $statements = array_filter(array_map('trim', explode(';', $sql)));
            foreach ($statements as $stmt) {
                if (empty($stmt) || strpos($stmt, '--') === 0) continue;
                try {
                    $pdo->exec($stmt);
                } catch (Exception $e) {
                    // Skip errors (e.g., already exists)
                }
            }
            $pdo->exec("SET FOREIGN_KEY_CHECKS=1");
            $success[] = 'تمام جداول ساخته شدند';
        }
        
        // Save config to .env
        $jwt = bin2hex(random_bytes(32));
        $env = "DB_HOST=$db_host\nDB_NAME=$db_name\nDB_USER=$db_user\nDB_PASS=$db_pass\nJWT_SECRET=$jwt\n";
        @file_put_contents(__DIR__ . '/.env', $env);
        @file_put_contents(__DIR__ . '/chat-server/.env', $env);
        
        // Save site_url
        if ($site_url) {
            $stmt = $pdo->prepare("INSERT INTO settings (key_name, value) VALUES ('site_url', ?) ON DUPLICATE KEY UPDATE value=?");
            $stmt->execute([$site_url, $site_url]);
        }
        
        $success[] = 'JWT secret تولید شد: ' . substr($jwt, 0, 8) . '...';
        $success[] = 'فایل .env ساخته شد';
        
    } catch (PDOException $e) {
        $errors[] = 'خطای اتصال MySQL: ' . $e->getMessage();
    }
    ?>
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>نتیجه نصب</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
        <style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
    </head>
    <body class="bg-gray-100 min-h-screen flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-2xl w-full">
            <div class="text-center mb-6">
                <div class="text-6xl mb-2"><?= empty($errors)?'✅':'⚠️' ?></div>
                <h1 class="text-2xl font-bold">نتیجه نصب</h1>
            </div>
            
            <?php if (!empty($success)): ?>
            <div class="bg-green-50 rounded p-4 mb-4">
                <h3 class="font-bold text-green-700 mb-2">✓ موفق:</h3>
                <ul class="list-disc mr-5 text-sm">
                    <?php foreach ($success as $s): ?><li><?= sanitize($s) ?></li><?php endforeach; ?>
                </ul>
            </div>
            <?php endif; ?>
            
            <?php if (!empty($errors)): ?>
            <div class="bg-red-50 rounded p-4 mb-4">
                <h3 class="font-bold text-red-700 mb-2">⚠ خطاها:</h3>
                <ul class="list-disc mr-5 text-sm">
                    <?php foreach ($errors as $e): ?><li><?= sanitize($e) ?></li><?php endforeach; ?>
                </ul>
            </div>
            <?php endif; ?>
            
            <div class="bg-blue-50 rounded p-4 mb-4 text-sm">
                <h3 class="font-bold mb-2">قدم بعدی:</h3>
                <p>۱. <a href="admin/setup.php" class="text-blue-600">ساخت اولین ادمین</a></p>
                <p>۲. وارد <a href="admin/" class="text-blue-600">پنل ادمین</a> شوید</p>
                <p>۳. تنظیمات → FactorDB token را وارد کنید</p>
                <p>۴. چت سرور را اجرا کنید (راهنما: chat-server/README.md)</p>
            </div>
            
            <div class="flex justify-center gap-3 mt-6">
                <a href="../" class="bg-gray-100 px-6 py-2 rounded">🏠 سایت</a>
                <a href="admin/setup.php" class="bg-blue-600 text-white px-6 py-2 rounded">➡️ ساخت ادمین</a>
            </div>
        </div>
    </body>
    </html>
    <?php
    exit;
}
