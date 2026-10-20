<?php
// ============================================================
// auth/phone.php — ورود با موبایل (SMS)
// ============================================================
require_once __DIR__ . '/../functions.php';
secure_session_start();

$step = $_GET['step'] ?? '1';
$phone = $_SESSION['pending_phone'] ?? '';
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify($_POST['csrf_token'] ?? '') or die('🛡️ CSRF invalid');
    
    if ($step === '1') {
        $phone = trim($_POST['phone'] ?? '');
        if (!preg_match('/^09\d{9}$/', $phone)) {
            $error = 'شماره باید 09xxxxxxxxx باشد';
        } else {
            $code = str_pad(random_int(0, 9999), 4, '0', STR_PAD_LEFT);
            $_SESSION['pending_phone'] = $phone;
            $_SESSION['phone_code'] = $code;
            $_SESSION['phone_code_expires'] = time() + 120;
            
            // Send SMS (if API configured)
            $sms_key = Settings::get('sms_api_key', '');
            if ($sms_key) {
                // Real SMS sending
            } else {
                $error = "⚠️ SMS API تنظیم نشده. کد تست: $code";
            }
            header('Location: phone.php?step=2'); exit;
        }
    } elseif ($step === '2') {
        $input_code = trim($_POST['code'] ?? '');
        $stored = $_SESSION['phone_code'] ?? '';
        $expires = $_SESSION['phone_code_expires'] ?? 0;
        
        if (time() > $expires) {
            $error = 'کد منقضی شده. دوباره کد بگیرید.';
            session_unset();
        } elseif ($input_code !== $stored) {
            $error = 'کد اشتباه';
        } else {
            $pdo = Database::getInstance();
            $stmt = $pdo->prepare("SELECT * FROM users WHERE phone = ?");
            $stmt->execute([$phone]);
            $u = $stmt->fetch();
            if (!$u) {
                $pdo->prepare("INSERT INTO users (phone, name, phone_verified, language, country) VALUES (?, ?, 1, 'fa', 'Iran')")
                    ->execute([$phone, 'کاربر ' . substr($phone, -4)]);
                $uid = $pdo->lastInsertId();
            } else {
                $uid = $u['id'];
                $pdo->prepare("UPDATE users SET phone_verified = 1 WHERE id = ?")->execute([$uid]);
            }
            regenerate_session($uid);
            header('Location: /'); exit;
        }
    }
}
?>
<!DOCTYPE html>
<html lang="fa" dir="rtl"><head>
<meta charset="UTF-8"><title>ورود با موبایل</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<style>body{font-family:'Vazirmatn',Tahoma,sans-serif}</style>
</head><body class="bg-gradient-to-br from-emerald-900 to-green-900 min-h-screen flex items-center justify-center p-4">
<div class="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
<div class="text-center mb-6"><div class="text-6xl mb-2">📱</div><h1 class="text-2xl font-bold">ورود با موبایل</h1></div>
<?php if ($error): ?><div class="bg-yellow-50 border-r-4 border-yellow-500 text-yellow-700 p-3 rounded mb-4 text-sm"><?= $error ?></div><?php endif; ?>
<?php if ($step === '1'): ?>
<form method="post" action="?step=1" class="space-y-4">
    <?= csrf_field() ?>
    <div><label class="block text-sm font-bold mb-1">شماره موبایل</label><input type="tel" name="phone" required pattern="09\d{9}" placeholder="09121234567" class="w-full px-4 py-3 border rounded-lg text-lg font-mono" dir="ltr"></div>
    <button class="w-full bg-gradient-to-r from-emerald-600 to-green-600 text-white py-3 rounded-lg font-bold">📲 ارسال کد</button>
</form>
<?php else: ?>
<form method="post" action="?step=2" class="space-y-4">
    <?= csrf_field() ?>
    <div class="text-center mb-2"><p class="text-sm">کد ارسال شده به:</p><p class="font-bold font-mono" dir="ltr"><?= sanitize($phone) ?></p></div>
    <div><label class="block text-sm font-bold mb-1">کد تایید</label><input type="text" name="code" required pattern="\d{4}" maxlength="4" placeholder="0000" class="w-full px-4 py-3 border rounded-lg text-3xl font-mono text-center" dir="ltr"></div>
    <button class="w-full bg-gradient-to-r from-emerald-600 to-green-600 text-white py-3 rounded-lg font-bold">✓ تایید</button>
    <a href="phone.php?step=1" class="block text-center text-sm text-gray-500">→ ارسال مجدد</a>
</form>
<?php endif; ?>
<div class="mt-6 text-center"><a href="../" class="text-xs text-gray-400">→ سایت</a></div>
</div>
</body></html>
