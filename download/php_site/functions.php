<?php
// ============================================================
// functions.php — توابع اصلی سایت
// تمام تنظیمات از دیتابیس خوانده می‌شوند (پنل ادمین قابل تغییر)
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

// ===== Site info (all from database) =====
function site_title($lang = 'fa') {
    return Settings::get("site_title_$lang", Settings::get("site_title_fa", "Math Platform"));
}
function site_subtitle($lang = 'fa') {
    return Settings::get("site_subtitle_$lang", "");
}
function site_dedicated() {
    return Settings::get("dedicated_to", "");
}
function site_url() {
    return Settings::get("site_url", "https://" . ($_SERVER['HTTP_HOST'] ?? 'localhost'));
}
function factordb_token() {
    return Settings::get("factordb_token", "");
}

// ===== i18n (multilingual — more languages) =====
$supported_langs = ['fa', 'en', 'ar', 'fr', 'de', 'es', 'ru', 'zh', 'tr', 'ur'];

$translations = [
    'fa' => [
        'title' => site_title('fa'),
        'subtitle' => site_subtitle('fa'),
        'dedicated' => site_dedicated(),
        'home' => 'خانه', 'series' => 'سری‌ها', 'ranges' => 'بازه‌ها',
        'magazine' => 'مجله', 'about' => 'درباره',
        'login_gmail' => 'ورود با Gmail', 'login_phone' => 'ورود با شماره موبایل',
        'start_factoring' => 'شروع فاکتور کردن', 'join_network' => 'پیوستن به شبکه',
        'read_magazine' => 'خواندن مجله', 'contributions' => 'مشارکت‌ها در FactorDB',
        'frontier' => 'فرانتیر پیوسته', 'series_count' => 'سری‌های ریاضی',
        'articles_count' => 'مقالات مجله', 'users_count' => 'کاربران',
        'range_complete' => 'کامل شده', 'range_in_progress' => 'در حال اجرا',
        'no_gaps' => 'بدون شکست', 'digits' => 'رقم', 'numbers' => 'عدد',
        'primes' => 'اعداد اول', 'composites' => 'مرکب فاکتور شده',
        'for_processing' => 'برای پردازش ریاضی و علمی',
        'medical_research' => 'تحقیقات پزشکی و دارویی',
        'volunteer_network' => 'شبکه داوطلبین', 'secure_platform' => 'پلتفرم امن',
        'motivation' => 'با هم بریم برای جایزه بزرگ',
        'eff_prize' => 'EFF Prize: $150,000 برای عدد اول ۱۰۰ میلیون رقمی',
        'download_software' => 'دانلود نرم‌افزار', 'admin_panel' => 'پنل مدیریت',
        'api_docs' => 'مستندات API', 'copyright' => '© 2026 ' . site_title('fa'),
        'powered_by' => 'قدرت گرفته از',
    ],
    'en' => [
        'title' => site_title('en'), 'subtitle' => site_subtitle('en'),
        'dedicated' => site_dedicated(),
        'home' => 'Home', 'series' => 'Series', 'ranges' => 'Ranges',
        'magazine' => 'Magazine', 'about' => 'About',
        'login_gmail' => 'Login with Gmail', 'login_phone' => 'Login with Phone',
        'start_factoring' => 'Start Factoring', 'join_network' => 'Join Network',
        'read_magazine' => 'Read Magazine', 'contributions' => 'FactorDB Contributions',
        'frontier' => 'Continuous Frontier', 'series_count' => 'Math Series',
        'articles_count' => 'Magazine Articles', 'users_count' => 'Users',
        'range_complete' => 'Complete', 'range_in_progress' => 'In Progress',
        'no_gaps' => 'no gaps', 'digits' => 'digits', 'numbers' => 'numbers',
        'primes' => 'primes', 'composites' => 'factored composites',
        'for_processing' => 'For mathematical and scientific processing',
        'medical_research' => 'Medical and pharmaceutical research',
        'volunteer_network' => 'Volunteer Network', 'secure_platform' => 'Secure Platform',
        'motivation' => 'Let\'s go for the grand prize together',
        'eff_prize' => 'EFF Prize: $150,000 for 100-million-digit prime',
        'download_software' => 'Download Software', 'admin_panel' => 'Admin Panel',
        'api_docs' => 'API Documentation', 'copyright' => '© 2026 ' . site_title('en'),
        'powered_by' => 'Powered by',
    ],
    'ar' => [
        'title' => site_title('ar'), 'subtitle' => site_subtitle('ar'),
        'dedicated' => site_dedicated(),
        'home' => 'الرئيسية', 'series' => 'السلاسل', 'ranges' => 'النطاقات',
        'magazine' => 'المجلة', 'about' => 'حول',
        'login_gmail' => 'تسجيل الدخول بـ Gmail', 'login_phone' => 'تسجيل الدخول بالهاتف',
        'start_factoring' => 'ابدأ التحليل', 'join_network' => 'انضم للشبكة',
        'read_magazine' => 'اقرأ المجلة', 'contributions' => 'مساهمات FactorDB',
        'frontier' => 'الحد المستمر', 'series_count' => 'السلاسل الرياضية',
        'articles_count' => 'مقالات المجلة', 'users_count' => 'المستخدمون',
        'range_complete' => 'مكتمل', 'range_in_progress' => 'قيد التنفيذ',
        'no_gaps' => 'بدون فجوات', 'digits' => 'أرقام', 'numbers' => 'أرقام',
        'primes' => 'أعداد أولية', 'composites' => 'أعداد مركبة محللة',
        'for_processing' => 'للمعالجة الرياضية والعلمية',
        'medical_research' => 'البحوث الطبية والصيدلانية',
        'volunteer_network' => 'شبكة المتطوعين', 'secure_platform' => 'منصة آمنة',
        'motivation' => 'لنذهب للجائزة الكبرى معاً',
        'eff_prize' => 'جائزة EFF: 150,000$ للعدد الأولي 100 مليون رقم',
        'download_software' => 'تحميل البرنامج', 'admin_panel' => 'لوحة الإدارة',
        'api_docs' => 'وثائق API', 'copyright' => '© 2026 ' . site_title('ar'),
        'powered_by' => 'مدعوم من',
    ],
    // Additional languages can be added from admin panel
    'fr' => [
        'title' => 'Plateforme Mathématique Perse', 'home' => 'Accueil',
        'series' => 'Séries', 'ranges' => 'Plages', 'magazine' => 'Magazine',
        'about' => 'À propos', 'login_gmail' => 'Connexion avec Gmail',
        'login_phone' => 'Connexion par téléphone', 'start_factoring' => 'Commencer',
        'join_network' => 'Rejoindre', 'read_magazine' => 'Lire le magazine',
        'contributions' => 'Contributions FactorDB', 'frontier' => 'Frontière continue',
        'series_count' => 'Séries mathématiques', 'articles_count' => 'Articles',
        'users_count' => 'Utilisateurs', 'motivation' => 'Allons chercher le grand prix',
        'eff_prize' => 'Prix EFF: $150,000', 'download_software' => 'Télécharger',
        'admin_panel' => 'Panneau d\'administration', 'api_docs' => 'Documentation API',
        'copyright' => '© 2026 Plateforme Mathématique Perse', 'powered_by' => 'Propulsé par',
    ],
    'de' => [
        'title' => 'Persische Mathematik-Plattform', 'home' => 'Startseite',
        'series' => 'Reihen', 'ranges' => 'Bereiche', 'magazine' => 'Magazin',
        'about' => 'Über', 'login_gmail' => 'Mit Gmail anmelden',
        'login_phone' => 'Mit Telefon anmelden', 'start_factoring' => 'Faktorisieren starten',
        'join_network' => 'Netzwerk beitreten', 'read_magazine' => 'Magazin lesen',
        'contributions' => 'FactorDB Beiträge', 'frontier' => 'Fortlaufende Grenze',
        'motivation' => 'Gemeinsam zum großen Preis', 'eff_prize' => 'EFF Preis: $150.000',
        'admin_panel' => 'Admin-Panel', 'api_docs' => 'API-Dokumentation',
        'copyright' => '© 2026 Persische Mathematik-Plattform', 'powered_by' => 'Unterstützt von',
    ],
    'tr' => [
        'title' => 'Fars Matematik Platformu', 'home' => 'Ana Sayfa',
        'series' => 'Seriler', 'ranges' => 'Aralıklar', 'magazine' => 'Dergi',
        'about' => 'Hakkında', 'login_gmail' => 'Gmail ile giriş',
        'login_phone' => 'Telefon ile giriş', 'start_factoring' => 'Faktörizasyon başlat',
        'join_network' => 'Ağa katıl', 'read_magazine' => 'Dergi oku',
        'contributions' => 'FactorDB Katkıları', 'frontier' => 'Sürekli Sınır',
        'motivation' => 'Büyük ödül için birlikte gidelim', 'eff_prize' => 'EFF Ödülü: $150.000',
        'admin_panel' => 'Yönetim Paneli', 'api_docs' => 'API Belgeleri',
        'copyright' => '© 2026 Fars Matematik Platformu', 'powered_by' => 'Gücüyle',
    ],
    'ur' => [
        'title' => 'فارسی ریاضی پلیٹ فارم', 'home' => 'ہوم',
        'series' => 'سیریز', 'ranges' => 'رینجز', 'magazine' => 'میگزین',
        'about' => 'بارے میں', 'login_gmail' => 'Gmail سے لاگ ان',
        'login_phone' => 'فون سے لاگ ان', 'start_factoring' => 'فیکٹرنگ شروع کریں',
        'join_network' => 'نیٹ ورک میں شامل ہوں', 'read_magazine' => 'میگزین پڑھیں',
        'contributions' => 'FactorDB تعاون', 'frontier' => 'مسلسل سرحد',
        'motivation' => 'بڑے انعام کے لیے ساتھ چلیں', 'eff_prize' => 'EFF انعام: $150,000',
        'admin_panel' => 'ایڈمن پینل', 'api_docs' => 'API دستاویزات',
        'copyright' => '© 2026 فارسی ریاضی پلیٹ فارم', 'powered_by' => 'پاورڈ بائی',
    ],
];

function t($key, $lang = 'fa') {
    global $translations;
    return $translations[$lang][$key] ?? $translations['fa'][$key] ?? $key;
}

// ===== FactorDB API =====
function factordb_get_contributions() {
    $token = factordb_token();
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
    $token = factordb_token();
    if (!$token) return ['error' => 'No FactorDB token'];
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
function csrf_token() {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = generate_token(16);
    }
    return $_SESSION['csrf_token'];
}
function csrf_verify($token) {
    return !empty($_SESSION['csrf_token']) && hash_equals($_SESSION['csrf_token'], $token);
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
        header('Location: /login');
        exit;
    }
}
function require_admin() {
    $user = current_user();
    if (!$user || !in_array($user['role'], ['admin', 'superadmin'])) {
        http_response_code(403);
        die('Access denied');
    }
}

// ===== AI permissions (admin can grant AI access) =====
function can_use_ai() {
    $user = current_user();
    if (!$user) return false;
    if (in_array($user['role'], ['admin', 'superadmin'])) return true;
    // Check if user has ai_permission in settings
    return Settings::get("ai_permission_{$user['id']}", '0') === '1';
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
    $html .= "<meta property='og:title' content='" . sanitize($title) . "'>\n";
    $html .= "<meta property='og:description' content='" . sanitize($description) . "'>\n";
    if ($image) $html .= "<meta property='og:image' content='" . sanitize($image) . "'>\n";
    if ($url) $html .= "<meta property='og:url' content='" . sanitize($url) . "'>\n";
    $html .= "<meta name='twitter:card' content='summary_large_image'>\n";
    return $html;
}
