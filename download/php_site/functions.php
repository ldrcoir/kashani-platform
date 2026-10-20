<?php
// ============================================================
// functions.php — توابع اصلی پلتفرم علمی چندرشته‌ای پارسی
// به افتخار غیاث‌الدین جمشید کاشانی
// ============================================================

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/database.php';

// ===== Settings Manager (all from database) =====
class Settings {
    private static $cache = null;

    public static function load() {
        if (self::$cache !== null) return self::$cache;
        try {
            $pdo = Database::getInstance();
            $stmt = $pdo->query("SELECT key_name, value FROM settings");
            self::$cache = [];
            while ($row = $stmt->fetch()) {
                self::$cache[$row['key_name']] = $row['value'];
            }
        } catch (Exception $e) {
            self::$cache = [];
        }
        return self::$cache;
    }

    public static function get($key, $default = '') {
        $settings = self::load();
        return $settings[$key] ?? $default;
    }

    public static function set($key, $value) {
        $pdo = Database::getInstance();
        $stmt = $pdo->prepare("INSERT INTO settings (key_name, value) VALUES (?,?) ON DUPLICATE KEY UPDATE value = ?");
        $stmt->execute([$key, $value, $value]);
        self::$cache[$key] = $value;
    }

    public static function all() {
        return self::load();
    }
}

// ===== i18n (10 languages) =====
$supported_langs = ['fa', 'en', 'ar', 'fr', 'de', 'es', 'ru', 'zh', 'tr', 'ur'];

$translations = [
    'fa' => [
        'title' => 'پلتفرم علمی چندرشته‌ای پارسی',
        'subtitle' => 'به افتخار غیاث‌الدین جمشید کاشانی',
        'dedicated' => 'غیاث‌الدین جمشید کاشانی',
        'home' => 'خانه', 'series' => 'سری‌ها', 'ranges' => 'بازه‌ها',
        'magazine' => 'مجله', 'about' => 'درباره', 'lessons' => 'آموزش',
        'login_gmail' => 'ورود با Gmail', 'login_phone' => 'ورود با موبایل',
        'start_factoring' => 'شروع فاکتور کردن', 'join_network' => 'پیوستن به شبکه',
        'read_magazine' => 'مجله', 'chat_intl' => 'چت بین‌المللی',
        'contributions' => 'مشارکت FactorDB', 'frontier' => 'فرانتیر پیوسته',
        'series_count' => 'سری‌های ریاضی', 'users_count' => 'کاربران',
        'range_complete' => 'کامل', 'range_in_progress' => 'در حال اجرا',
        'no_gaps' => 'بدون شکست', 'digits' => 'رقم', 'primes' => 'اعداد اول',
        'composites' => 'مرکب فاکتور شده', 'motivation' => 'با هم بریم برای جایزه بزرگ',
        'eff_prize' => 'EFF Prize: $150,000 برای عدد اول ۱۰۰ میلیون رقمی',
        'admin_panel' => 'پنل مدیریت', 'api_docs' => 'مستندات API',
        'copyright' => '© 2026 — به افتخار کاشانی',
    ],
    'en' => [
        'title' => 'Persian Multidisciplinary Science Platform',
        'subtitle' => 'Dedicated to Ghiyath al-Din Jamshid al-Kashi',
        'dedicated' => 'Ghiyath al-Din al-Kashi',
        'home' => 'Home', 'series' => 'Series', 'ranges' => 'Ranges',
        'magazine' => 'Magazine', 'about' => 'About', 'lessons' => 'Lessons',
        'login_gmail' => 'Login with Gmail', 'login_phone' => 'Login with Phone',
        'start_factoring' => 'Start Factoring', 'join_network' => 'Join Network',
        'read_magazine' => 'Magazine', 'chat_intl' => 'International Chat',
        'contributions' => 'FactorDB Contributions', 'frontier' => 'Continuous Frontier',
        'series_count' => 'Math Series', 'users_count' => 'Users',
        'range_complete' => 'Complete', 'range_in_progress' => 'In Progress',
        'no_gaps' => 'no gaps', 'digits' => 'digits', 'primes' => 'primes',
        'composites' => 'factored', 'motivation' => 'Going for the grand prize',
        'eff_prize' => 'EFF Prize: $150,000 for 100-million-digit prime',
        'admin_panel' => 'Admin Panel', 'api_docs' => 'API Docs',
        'copyright' => '© 2026 — Dedicated to al-Kashi',
    ],
    'ar' => [
        'title' => 'منصة العلوم متعددة التخصصات الفارسية',
        'subtitle' => 'إهداء إلى غياث الدين جمشيد الكاشاني',
        'dedicated' => 'غياث الدين الكاشاني',
        'home' => 'الرئيسية', 'series' => 'السلاسل', 'ranges' => 'النطاقات',
        'magazine' => 'المجلة', 'about' => 'حول', 'lessons' => 'الدروس',
        'login_gmail' => 'Gmail الدخول', 'login_phone' => 'الدخول بالهاتف',
        'start_factoring' => 'ابدأ التحليل', 'join_network' => 'انضم للشبكة',
        'read_magazine' => 'المجلة', 'chat_intl' => 'الدردشة الدولية',
        'contributions' => 'مساهمات FactorDB', 'frontier' => 'الحد المستمر',
        'series_count' => 'السلاسل الرياضية', 'users_count' => 'المستخدمون',
        'range_complete' => 'مكتمل', 'range_in_progress' => 'قيد التنفيذ',
        'no_gaps' => 'بدون فجوات', 'digits' => 'أرقام', 'primes' => 'أولية',
        'composites' => 'محللة', 'motivation' => 'نذهب للجائزة الكبرى',
        'eff_prize' => 'جائزة EFF: 150,000$ للعدد الأولي 100 مليون رقم',
        'admin_panel' => 'لوحة الإدارة', 'api_docs' => 'API',
        'copyright' => '© 2026 — إلى الكاشاني',
    ],
    'fr' => [
        'title' => 'Plateforme Scientifique Pluridisciplinaire Perse',
        'subtitle' => 'Dédiée à Ghiyath al-Din al-Kashi',
        'dedicated' => 'al-Kashi', 'home' => 'Accueil', 'magazine' => 'Magazine',
        'lessons' => 'Leçons', 'chat_intl' => 'Chat International',
        'admin_panel' => 'Panneau Admin', 'copyright' => '© 2026',
    ],
    'de' => [
        'title' => 'Persische Multidisziplinäre Wissenschaftsplattform',
        'subtitle' => 'Gewidmet Ghiyath al-Din al-Kashi',
        'dedicated' => 'al-Kashi', 'home' => 'Startseite', 'magazine' => 'Magazin',
        'lessons' => 'Lektionen', 'chat_intl' => 'Internationaler Chat',
        'admin_panel' => 'Admin', 'copyright' => '© 2026',
    ],
    'es' => [
        'title' => 'Plataforma Científica Multidisciplinaria Persa',
        'subtitle' => 'Dedicada a Ghiyath al-Din al-Kashi',
        'dedicated' => 'al-Kashi', 'home' => 'Inicio', 'magazine' => 'Revista',
        'lessons' => 'Lecciones', 'chat_intl' => 'Chat Internacional',
        'admin_panel' => 'Panel', 'copyright' => '© 2026',
    ],
    'ru' => [
        'title' => 'Персидская Мультидисциплинарная Научная Платформа',
        'subtitle' => 'Посвящается Гият аль-Дин аль-Каши',
        'dedicated' => 'аль-Каши', 'home' => 'Главная', 'magazine' => 'Журнал',
        'lessons' => 'Уроки', 'chat_intl' => 'Международный чат',
        'admin_panel' => 'Админ', 'copyright' => '© 2026',
    ],
    'zh' => [
        'title' => '波斯跨学科科学平台',
        'subtitle' => '献给吉亚斯·丁·贾姆希德·卡尚尼',
        'dedicated' => '卡尚尼', 'home' => '主页', 'magazine' => '杂志',
        'lessons' => '课程', 'chat_intl' => '国际聊天',
        'admin_panel' => '管理面板', 'copyright' => '© 2026',
    ],
    'tr' => [
        'title' => 'Fars Çok Disiplinli Bilim Platformu',
        'subtitle' => 'Gıyâseddin Cemşid el-Kaşi\'ye adanmıştır',
        'dedicated' => 'el-Kaşi', 'home' => 'Ana Sayfa', 'magazine' => 'Dergi',
        'lessons' => 'Dersler', 'chat_intl' => 'Uluslararası Sohbet',
        'admin_panel' => 'Yönetim', 'copyright' => '© 2026',
    ],
    'ur' => [
        'title' => 'فارسی کثیر العلوم سائنسی پلیٹ فارم',
        'subtitle' => 'غیاث الدین جمشید الکاشانی کے نام',
        'dedicated' => 'الکاشانی', 'home' => 'ہوم', 'magazine' => 'میگزین',
        'lessons' => 'اسباق', 'chat_intl' => 'بین الاقوامی چیٹ',
        'admin_panel' => 'ایڈمن', 'copyright' => '© 2026',
    ],
];

function t($key, $lang = 'fa') {
    global $translations;
    return $translations[$lang][$key] ?? $translations['fa'][$key] ?? $key;
}

// ===== FactorDB API =====
function factordb_get_contributions() {
    $token = Settings::get('factordb_token', '');
    if (!$token) return ['total' => 0, 'largest_digits' => 0];
    $payload = json_encode([
        'jsonrpc' => '2.0', 'id' => 1, 'method' => 'contributions',
        'params' => ['limit' => 5]
    ]);
    $ch = curl_init(FACTORDB_API);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json', 'X-Fdb-User-Token: ' . $token],
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
    $token = Settings::get('factordb_token', '');
    if (!$token) return ['error' => 'No token'];
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
        CURLOPT_HTTPHEADER => ['Content-Type: application/json', 'X-Fdb-User-Token: ' . $token],
        CURLOPT_POSTFIELDS => $payload,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 30,
    ]);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response, true);
}

// ===== Security helpers =====
function generate_token($length = 32) {
    return bin2hex(random_bytes($length));
}

function sanitize($input) {
    return htmlspecialchars(trim($input ?? ''), ENT_QUOTES, 'UTF-8');
}

function sanitize_int($v, $def = 0) {
    $r = filter_var($v, FILTER_VALIDATE_INT);
    return $r === false ? $def : $r;
}

function sanitize_email($v) {
    return filter_var($v, FILTER_VALIDATE_EMAIL) ?: '';
}

function sanitize_url($v) {
    return filter_var($v, FILTER_VALIDATE_URL) ?: '';
}

function sanitize_string($v, $max_len = 1000) {
    $v = trim($v ?? '');
    if (strlen($v) > $max_len) $v = substr($v, 0, $max_len);
    return htmlspecialchars($v, ENT_QUOTES, 'UTF-8');
}

function sanitize_html($html, $allowed = '<p><br><b><i><strong><em><a><ul><ol><li><code><pre><h2><h3><h4><img><blockquote><span><div><table><tr><td><th><math><mi><mo><mn><msup><msub><mfrac>') {
    $html = preg_replace('/\bon\w+\s*=\s*["\'][^"\']*["\']/i', '', $html);
    $html = preg_replace('/javascript:/i', '', $html);
    $html = preg_replace('/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/i', '', $html);
    $html = preg_replace('/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/i', '', $html);
    return strip_tags($html, $allowed);
}

function get_client_ip() {
    return $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
}

// ===== CSRF =====
function csrf_token() {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

function csrf_field() {
    return '<input type="hidden" name="csrf_token" value="' . csrf_token() . '">';
}

function csrf_verify($token) {
    if (empty($token) || empty($_SESSION['csrf_token'])) return false;
    return hash_equals($_SESSION['csrf_token'], $token);
}

// ===== Session security =====
function secure_session_start() {
    if (session_status() === PHP_SESSION_NONE) {
        session_set_cookie_params([
            'lifetime' => 86400 * 7,
            'path' => '/',
            'httponly' => true,
            'samesite' => 'Strict',
        ]);
        if (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') {
            session_set_cookie_params(['secure' => true]);
        }
        session_start();
    }
}

function regenerate_session($user_id) {
    session_regenerate_id(true);
    $_SESSION['user_id'] = $user_id;
    $_SESSION['login_time'] = time();
    $_SESSION['ip_address'] = get_client_ip();
    $_SESSION['user_agent'] = $_SERVER['HTTP_USER_AGENT'] ?? '';
}

// ===== Security headers =====
function send_security_headers() {
    if (headers_sent()) return;
    header('X-Content-Type-Options: nosniff');
    header('X-Frame-Options: SAMEORIGIN');
    header('X-XSS-Protection: 1; mode=block');
    header('Referrer-Policy: strict-origin-when-cross-origin');
    header('Permissions-Policy: geolocation=(), microphone=(), camera=()');
    header("Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; img-src 'self' data: https:; connect-src 'self' wss: https:; font-src 'self' data: cdn.jsdelivr.net");
}

// ===== Rate limiting =====
function check_rate_limit($key, $max_per_minute = 60) {
    $ip = get_client_ip();
    $cache_file = CACHE_DIR . md5("rate_limit_{$key}_{$ip}") . '.json';
    $now = time();
    $data = ['requests' => []];
    if (file_exists($cache_file)) {
        $data = json_decode(file_get_contents($cache_file), true) ?: ['requests' => []];
    }
    $data['requests'] = array_filter($data['requests'], fn($t) => $now - $t < 60);
    if (count($data['requests']) >= $max_per_minute) {
        http_response_code(429);
        header('Retry-After: 60');
        die(json_encode(['error' => 'Rate limited']));
    }
    $data['requests'][] = $now;
    file_put_contents($cache_file, json_encode($data));
}

// ===== Audit log =====
function audit_log($action, $details = '') {
    try {
        $pdo = Database::getInstance();
        $user = current_user();
        $pdo->exec("CREATE TABLE IF NOT EXISTS audit_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT, action VARCHAR(100), details TEXT,
            ip VARCHAR(45), user_agent TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )");
        $stmt = $pdo->prepare("INSERT INTO audit_log (user_id, action, details, ip, user_agent) VALUES (?, ?, ?, ?, ?)");
        $stmt->execute([
            $user['id'] ?? null, $action, $details, get_client_ip(),
            $_SERVER['HTTP_USER_AGENT'] ?? ''
        ]);
    } catch (Exception $e) {}
}

// ===== User management =====
function is_logged_in() {
    return isset($_SESSION['user_id']);
}

function current_user() {
    if (!is_logged_in()) return null;
    try {
        $pdo = Database::getInstance();
        $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
        $stmt->execute([$_SESSION['user_id']]);
        return $stmt->fetch();
    } catch (Exception $e) { return null; }
}

function require_login() {
    if (!is_logged_in()) { header('Location: /auth/phone.php'); exit; }
}

function require_admin() {
    $user = current_user();
    if (!$user || !in_array($user['role'], ['admin', 'superadmin'])) {
        http_response_code(403);
        die('Access denied');
    }
}

function can_use_ai() {
    $user = current_user();
    if (!$user) return false;
    if (in_array($user['role'], ['admin', 'superadmin'])) return true;
    return Settings::get("ai_permission_{$user['id']}", '0') === '1';
}

// ===== Site info =====
function site_title($lang = 'fa') {
    return Settings::get("site_title_$lang", Settings::get('site_title_fa', 'پلتفرم علمی چندرشته‌ای پارسی'));
}
function site_url() {
    return Settings::get('site_url', "https://" . ($_SERVER['HTTP_HOST'] ?? 'localhost'));
}
function factordb_token() {
    return Settings::get('factordb_token', '');
}

// ===== Data queries =====
function get_math_series() {
    try {
        $pdo = Database::getInstance();
        return $pdo->query("SELECT * FROM math_series ORDER BY sort_order")->fetchAll();
    } catch (Exception $e) { return []; }
}

function get_ranges() {
    try {
        $pdo = Database::getInstance();
        return $pdo->query("SELECT * FROM ranges ORDER BY start_num")->fetchAll();
    } catch (Exception $e) { return []; }
}

function get_frontier() {
    try {
        $pdo = Database::getInstance();
        $stmt = $pdo->query("SELECT MAX(end_num) as frontier FROM ranges WHERE is_complete = 1");
        return $stmt->fetch()['frontier'] ?? 200000000;
    } catch (Exception $e) { return 200000000; }
}

function get_articles($limit = 10, $published_only = true) {
    try {
        $pdo = Database::getInstance();
        $sql = "SELECT a.*, u.name as author_name FROM articles a LEFT JOIN users u ON a.author_id = u.id";
        if ($published_only) $sql .= " WHERE a.is_published = 1";
        $sql .= " ORDER BY a.created_at DESC LIMIT ?";
        $stmt = $pdo->prepare($sql);
        $stmt->execute([$limit]);
        return $stmt->fetchAll();
    } catch (Exception $e) { return []; }
}

function get_lessons($limit = 10, $published_only = true) {
    try {
        $pdo = Database::getInstance();
        $sql = "SELECT * FROM lessons";
        if ($published_only) $sql .= " WHERE is_published = 1";
        $sql .= " ORDER BY sort_order, created_at DESC LIMIT ?";
        $stmt = $pdo->prepare($sql);
        $stmt->execute([$limit]);
        return $stmt->fetchAll();
    } catch (Exception $e) { return []; }
}

function get_scientists() {
    try {
        $pdo = Database::getInstance();
        return $pdo->query("SELECT * FROM scientists ORDER BY sort_order, century")->fetchAll();
    } catch (Exception $e) { return []; }
}

function get_site_stats() {
    $pdo = Database::getInstance();
    $users = 0; $articles = 0; $factors = 0; $series = 0;
    try { $users = $pdo->query("SELECT COUNT(*) FROM users")->fetchColumn(); } catch (Exception $e) {}
    try { $articles = $pdo->query("SELECT COUNT(*) FROM articles WHERE is_published = 1")->fetchColumn(); } catch (Exception $e) {}
    try { $factors = $pdo->query("SELECT COUNT(*) FROM factors")->fetchColumn(); } catch (Exception $e) {}
    try { $series = $pdo->query("SELECT COUNT(*) FROM math_series")->fetchColumn(); } catch (Exception $e) {}

    $cache_file = CACHE_DIR . 'factordb_stats.json';
    $contributions = 0; $largest = 0;
    if (file_exists($cache_file) && time() - filemtime($cache_file) < 300) {
        $data = json_decode(file_get_contents($cache_file), true);
        $contributions = $data['total'] ?? 0;
        $largest = $data['largest_digits'] ?? 0;
    } else {
        $data = factordb_get_contributions();
        $contributions = $data['total'] ?? 0;
        $largest = $data['largest_digits'] ?? 0;
        @file_put_contents($cache_file, json_encode($data));
    }

    return [
        'users' => $users, 'articles' => $articles, 'factors' => $factors,
        'series' => $series, 'contributions' => $contributions,
        'largest_factor' => $largest, 'frontier' => get_frontier(),
    ];
}

// ===== SEO =====
function seo_meta($title, $description, $image = null, $url = null) {
    $html = "<title>" . sanitize($title) . "</title>\n";
    $html .= "<meta name='description' content='" . sanitize($description) . "'>\n";
    $html .= "<meta name='keywords' content='ریاضی, فیزیک, پزشکی, داروسازی, کامپیوتر, علوم, اعداد اول, فاکتور, علم, پژوهش, کاشانی, jamshid al-kashi, persian science, multidisciplinary'>\n";
    $html .= "<meta property='og:title' content='" . sanitize($title) . "'>\n";
    $html .= "<meta property='og:description' content='" . sanitize($description) . "'>\n";
    $html .= "<meta property='og:type' content='website'>\n";
    $html .= "<meta property='og:locale' content='fa_IR'>\n";
    if ($image) $html .= "<meta property='og:image' content='" . sanitize($image) . "'>\n";
    if ($url) $html .= "<meta property='og:url' content='" . sanitize($url) . "'>\n";
    $html .= "<meta name='twitter:card' content='summary_large_image'>\n";
    $html .= "<meta name='twitter:title' content='" . sanitize($title) . "'>\n";
    $html .= "<meta name='twitter:description' content='" . sanitize($description) . "'>\n";
    return $html;
}

// JSON-LD structured data (rich snippets)
function seo_jsonld_article($title, $description, $url, $image = null, $author = null, $datePublished = null) {
    $data = [
        '@context' => 'https://schema.org',
        '@type' => 'Article',
        'headline' => $title,
        'description' => $description,
        'url' => $url,
        'inLanguage' => 'fa-IR',
        'author' => ['@type' => 'Person', 'name' => $author ?: 'پلتفرم علمی پارسی'],
        'publisher' => [
            '@type' => 'Organization',
            'name' => 'پلتفرم علمی چندرشته‌ای پارسی',
            'description' => 'به افتخار غیاث‌الدین جمشید کاشانی',
        ],
    ];
    if ($image) $data['image'] = $image;
    if ($datePublished) $data['datePublished'] = $datePublished;
    return '<script type="application/ld+json">' . json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</script>';
}

function seo_jsonld_website() {
    $data = [
        '@context' => 'https://schema.org',
        '@type' => 'WebSite',
        'name' => 'پلتفرم علمی چندرشته‌ای پارسی',
        'alternateName' => 'Persian Multidisciplinary Science Platform',
        'url' => site_url(),
        'description' => 'پلتفرم بین‌المللی علوم: ریاضی، فیزیک، پزشکی، داروسازی، کامپیوتر — به افتخار غیاث‌الدین جمشید کاشانی',
        'inLanguage' => ['fa-IR', 'en', 'ar', 'fr', 'de', 'es', 'ru', 'zh', 'tr', 'ur'],
        'potentialAction' => [
            '@type' => 'SearchAction',
            'target' => site_url() . '/magazine.php?search={search_term_string}',
            'query-input' => 'required name=search_term_string',
        ],
    ];
    return '<script type="application/ld+json">' . json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</script>';
}

function seo_jsonld_lesson($title, $description, $url, $difficulty, $duration_min) {
    $data = [
        '@context' => 'https://schema.org',
        '@type' => 'LearningResource',
        'name' => $title,
        'description' => $description,
        'url' => $url,
        'inLanguage' => 'fa-IR',
        'learningResourceType' => 'Lesson',
        'educationalLevel' => $difficulty,
        'timeRequired' => 'PT' . $duration_min . 'M',
        'provider' => [
            '@type' => 'Organization',
            'name' => 'پلتفرم علمی چندرشته‌ای پارسی',
            'url' => site_url(),
        ],
    ];
    return '<script type="application/ld+json">' . json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</script>';
}

// ===== JWT helper =====
function base64url_encode($data) {
    return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
}
function base64url_decode($data) {
    return base64_decode(strtr($data, '-_', '+/'));
}
function generate_jwt($user_id, $email, $ttl = 86400) {
    $header = base64url_encode(json_encode(['typ' => 'JWT', 'alg' => 'HS256']));
    $payload = base64url_encode(json_encode([
        'userId' => $user_id, 'email' => $email,
        'iat' => time(), 'exp' => time() + $ttl,
    ]));
    $sig = base64url_encode(hash_hmac('sha256', "$header.$payload", JWT_SECRET, true));
    return "$header.$payload.$sig";
}

// Send security headers on every request
send_security_headers();
