<?php
// ============================================================
// functions.php — توابع اصلی سایت
// ============================================================

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/database.php';

// ===== i18n (multilingual support) =====
$translations = [
    'fa' => [
        'title' => 'پلتفرم ریاضی پارسی',
        'subtitle' => 'به افتخار ریاضیدانان پارسی-اسلامی',
        'dedicated' => 'تقدیم به Jamshid al-Kashi (الکاشی)',
        'home' => 'خانه',
        'series' => 'سری‌ها',
        'ranges' => 'بازه‌ها',
        'magazine' => 'مجله',
        'about' => 'درباره',
        'login_gmail' => 'ورود با Gmail',
        'login_phone' => 'ورود با شماره موبایل',
        'start_factoring' => 'شروع فاکتور کردن',
        'join_network' => 'پیوستن به شبکه',
        'read_magazine' => 'خواندن مجله',
        'contributions' => 'مشارکت‌ها در FactorDB',
        'frontier' => 'فرانتیر پیوسته',
        'series_count' => 'سری‌های ریاضی',
        'articles_count' => 'مقالات مجله',
        'users_count' => 'کاربران',
        'range_complete' => 'کامل شده',
        'range_in_progress' => 'در حال اجرا',
        'no_gaps' => 'بدون شکست',
        'digits' => 'رقم',
        'numbers' => 'عدد',
        'primes' => 'اعداد اول',
        'composites' => 'مرکب فاکتور شده',
        'for_processing' => 'برای پردازش ریاضی و علمی',
        'medical_research' => 'تحقیقات پزشکی و دارویی',
        'volunteer_network' => 'شبکه داوطلبین',
        'secure_platform' => 'پلتفرم امن',
        'motivation' => 'با هم بریم برای جایزه بزرگ',
        'eff_prize' => 'EFF Prize: $150,000 برای عدد اول ۱۰۰ میلیون رقمی',
        'download_software' => 'دانلود نرم‌افزار',
        'admin_panel' => 'پنل مدیریت',
        'copyright' => '© 2026 پلتفرم ریاضی پارسی',
    ],
    'en' => [
        'title' => 'Persian Math Platform',
        'subtitle' => 'Honoring Persian-Islamic mathematicians',
        'dedicated' => 'Dedicated to Jamshid al-Kashi',
        'home' => 'Home',
        'series' => 'Series',
        'ranges' => 'Ranges',
        'magazine' => 'Magazine',
        'about' => 'About',
        'login_gmail' => 'Login with Gmail',
        'login_phone' => 'Login with Phone',
        'start_factoring' => 'Start Factoring',
        'join_network' => 'Join Network',
        'read_magazine' => 'Read Magazine',
        'contributions' => 'FactorDB Contributions',
        'frontier' => 'Continuous Frontier',
        'series_count' => 'Math Series',
        'articles_count' => 'Magazine Articles',
        'users_count' => 'Users',
        'range_complete' => 'Complete',
        'range_in_progress' => 'In Progress',
        'no_gaps' => 'no gaps',
        'digits' => 'digits',
        'numbers' => 'numbers',
        'primes' => 'primes',
        'composites' => 'factored composites',
        'for_processing' => 'For mathematical and scientific processing',
        'medical_research' => 'Medical and pharmaceutical research',
        'volunteer_network' => 'Volunteer Network',
        'secure_platform' => 'Secure Platform',
        'motivation' => 'Let\'s go for the grand prize together',
        'eff_prize' => 'EFF Prize: $150,000 for 100-million-digit prime',
        'download_software' => 'Download Software',
        'admin_panel' => 'Admin Panel',
        'copyright' => '© 2026 Persian Math Platform',
    ],
    'ar' => [
        'title' => 'منصة الرياضيات الفارسية',
        'subtitle' => 'تكريماً للرياضيين الفرس',
        'dedicated' => 'إهداء إلى جمشيد الكاشاني',
        'home' => 'الرئيسية',
        'series' => 'السلاسل',
        'ranges' => 'النطاقات',
        'magazine' => 'المجلة',
        'about' => 'حول',
        'login_gmail' => 'تسجيل الدخول بـ Gmail',
        'login_phone' => 'تسجيل الدخول بالهاتف',
        'start_factoring' => 'ابدأ التحليل',
        'join_network' => 'انضم للشبكة',
        'read_magazine' => 'اقرأ المجلة',
        'contributions' => 'مساهمات FactorDB',
        'frontier' => 'الحد المستمر',
        'series_count' => 'السلاسل الرياضية',
        'articles_count' => 'مقالات المجلة',
        'users_count' => 'المستخدمون',
        'range_complete' => 'مكتمل',
        'range_in_progress' => 'قيد التنفيذ',
        'no_gaps' => 'بدون فجوات',
        'digits' => 'أرقام',
        'numbers' => 'أرقام',
        'primes' => 'أعداد أولية',
        'composites' => 'أعداد مركبة محللة',
        'for_processing' => 'للمعالجة الرياضية والعلمية',
        'medical_research' => 'البحوث الطبية والصيدلانية',
        'volunteer_network' => 'شبكة المتطوعين',
        'secure_platform' => 'منصة آمنة',
        'motivation' => 'لنذهب للجائزة الكبرى معاً',
        'eff_prize' => 'جائزة EFF: 150,000$ للعدد الأولي 100 مليون رقم',
        'download_software' => 'تحميل البرنامج',
        'admin_panel' => 'لوحة الإدارة',
        'copyright' => '© 2026 منصة الرياضيات الفارسية',
    ],
];

function t($key, $lang = 'fa') {
    global $translations;
    return $translations[$lang][$key] ?? $translations['fa'][$key] ?? $key;
}

// ===== FactorDB API =====
function factordb_get_contributions() {
    $payload = json_encode([
        'jsonrpc' => '2.0', 'id' => 1, 'method' => 'contributions',
        'params' => ['limit' => 5]
    ]);
    $ch = curl_init(FACTORDB_API);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => [
            'Content-Type: application/json',
            'X-Fdb-User-Token: ' . FACTORDB_TOKEN
        ],
        CURLOPT_POSTFIELDS => $payload,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 15,
    ]);
    $response = curl_exec($ch);
    curl_close($ch);
    $data = json_decode($response, true);
    return $data['result'] ?? ['total' => 0, 'largest_digits' => 0];
}

function factordb_submit_factors($n, $factors) {
    $payload = json_encode([
        'jsonrpc' => '2.0', 'id' => 1, 'method' => 'report_factors',
        'params' => [
            'target' => ['expr' => (string)$n],
            'factors' => array_map('strval', $factors),
            'credit' => true
        ]
    ]);
    $ch = curl_init(FACTORDB_API);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => [
            'Content-Type: application/json',
            'X-Fdb-User-Token: ' . FACTORDB_TOKEN
        ],
        CURLOPT_POSTFIELDS => $payload,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 30,
    ]);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response, true);
}

// ===== Security =====
function generate_token($length = 32) {
    return bin2hex(random_bytes($length));
}

function sanitize($input) {
    return htmlspecialchars(trim($input), ENT_QUOTES, 'UTF-8');
}

function get_client_ip() {
    return $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
}

// ===== User management =====
function is_logged_in() {
    return isset($_SESSION['user_id']);
}

function current_user() {
    if (!is_logged_in()) return null;
    $pdo = Database::getInstance();
    $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
    $stmt->execute([$_SESSION['user_id']]);
    return $stmt->fetch();
}

function require_login() {
    if (!is_logged_in()) {
        header('Location: /login.php');
        exit;
    }
}

function require_admin() {
    $user = current_user();
    if (!$user || $user['role'] !== 'admin') {
        http_response_code(403);
        die('Admin access required');
    }
}

// ===== Math series =====
function get_math_series() {
    $pdo = Database::getInstance();
    return $pdo->query("SELECT * FROM math_series ORDER BY sort_order")->fetchAll();
}

// ===== Range data =====
function get_ranges() {
    $pdo = Database::getInstance();
    return $pdo->query("SELECT * FROM ranges ORDER BY start_num")->fetchAll();
}

function get_frontier() {
    $pdo = Database::getInstance();
    $stmt = $pdo->query("SELECT MAX(end_num) as frontier FROM ranges WHERE is_complete = 1");
    $result = $stmt->fetch();
    return $result['frontier'] ?? 200000000;
}

// ===== Articles =====
function get_articles($limit = 10, $published_only = true) {
    $pdo = Database::getInstance();
    $sql = "SELECT * FROM articles";
    if ($published_only) $sql .= " WHERE is_published = 1";
    $sql .= " ORDER BY created_at DESC LIMIT ?";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$limit]);
    return $stmt->fetchAll();
}

// ===== Stats =====
function get_site_stats() {
    $pdo = Database::getInstance();
    $users = $pdo->query("SELECT COUNT(*) FROM users")->fetchColumn();
    $articles = $pdo->query("SELECT COUNT(*) FROM articles WHERE is_published = 1")->fetchColumn();
    $factors = $pdo->query("SELECT COUNT(*) FROM factors")->fetchColumn();
    $series = $pdo->query("SELECT COUNT(*) FROM math_series")->fetchColumn();

    // Get FactorDB contributions (cached)
    $cache_file = CACHE_DIR . 'factordb_stats.json';
    $contributions = 0;
    $largest = 0;
    if (file_exists($cache_file) && time() - filemtime($cache_file) < 300) {
        $data = json_decode(file_get_contents($cache_file), true);
        $contributions = $data['total'] ?? 0;
        $largest = $data['largest_digits'] ?? 0;
    } else {
        $data = factordb_get_contributions();
        $contributions = $data['total'] ?? 0;
        $largest = $data['largest_digits'] ?? 0;
        file_put_contents($cache_file, json_encode($data));
    }

    return [
        'users' => $users,
        'articles' => $articles,
        'factors' => $factors,
        'series' => $series,
        'contributions' => $contributions,
        'largest_factor' => $largest,
        'frontier' => get_frontier(),
    ];
}

// ===== SEO =====
function seo_meta($title, $description, $image = null, $url = null) {
    $html = "<title>" . sanitize($title) . "</title>\n";
    $html .= "<meta name='description' content='" . sanitize($description) . "'>\n";
    $html .= "<meta property='og:title' content='" . sanitize($title) . "'>\n";
    $html .= "<meta property='og:description' content='" . sanitize($description) . "'>\n";
    if ($image) $html .= "<meta property='og:image' content='" . sanitize($image) . "'>\n";
    if ($url) $html .= "<meta property='og:url' content='" . sanitize($url) . "'>\n";
    $html .= "<meta name='twitter:card' content='summary_large_image'>\n";
    $html .= "<meta name='twitter:title' content='" . sanitize($title) . "'>\n";
    $html .= "<meta name='twitter:description' content='" . sanitize($description) . "'>\n";
    return $html;
}
