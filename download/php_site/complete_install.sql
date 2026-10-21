-- ============================================================
-- complete_install.sql — تمام جداول پلتفرم
-- ============================================================
-- این فایل توسط install.php اجرا می‌شود
-- ============================================================

-- ===== Users =====
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NULL,
    name VARCHAR(255),
    phone VARCHAR(20) UNIQUE NULL,
    phone_verified TINYINT DEFAULT 0,
    role ENUM('user','admin','superadmin') DEFAULT 'user',
    credits INT DEFAULT 0,
    avatar VARCHAR(255),
    bio TEXT,
    country VARCHAR(100) DEFAULT 'Iran',
    language VARCHAR(10) DEFAULT 'fa',
    password_hash VARCHAR(255),
    api_key VARCHAR(100) UNIQUE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== Sessions =====
CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    ip VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== Factors =====
CREATE TABLE IF NOT EXISTS factors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    number TEXT NOT NULL,
    digits INT NOT NULL,
    factors TEXT NOT NULL,
    num_factors INT NOT NULL,
    is_prime TINYINT DEFAULT 0,
    source VARCHAR(50) DEFAULT 'manual',
    series VARCHAR(50),
    user_id INT,
    factordb_id VARCHAR(50),
    credited TINYINT DEFAULT 0,
    verified TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_digits (digits),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== Ranges =====
CREATE TABLE IF NOT EXISTS ranges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    start_num BIGINT NOT NULL,
    end_num BIGINT NOT NULL,
    primes_count INT DEFAULT 0,
    composites_count INT DEFAULT 0,
    unfactored_count INT DEFAULT 0,
    is_complete TINYINT DEFAULT 0,
    time_seconds FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== Articles =====
CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    excerpt TEXT,
    content LONGTEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'math',
    tags VARCHAR(500),
    image_url VARCHAR(255),
    author_id INT,
    is_ai TINYINT DEFAULT 0,
    is_published TINYINT DEFAULT 0,
    views INT DEFAULT 0,
    seo_title VARCHAR(255),
    seo_desc TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== Lessons (آموزش) =====
CREATE TABLE IF NOT EXISTS lessons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    content LONGTEXT NOT NULL,
    category ENUM('math','science','medical','pharmacy','physics','computer','general') DEFAULT 'math',
    difficulty ENUM('beginner','intermediate','advanced','expert') DEFAULT 'beginner',
    duration_minutes INT DEFAULT 30,
    prerequisites TEXT,
    learning_objectives TEXT,
    exercises LONGTEXT,
    solution_text LONGTEXT,
    video_url VARCHAR(500),
    is_interactive TINYINT DEFAULT 0,
    interactive_payload LONGTEXT,
    is_published TINYINT DEFAULT 0,
    sort_order INT DEFAULT 0,
    views INT DEFAULT 0,
    completions INT DEFAULT 0,
    rating_avg FLOAT DEFAULT 0,
    rating_count INT DEFAULT 0,
    author_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== Lesson progress =====
CREATE TABLE IF NOT EXISTS lesson_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lesson_id INT NOT NULL,
    user_id INT NOT NULL,
    status ENUM('not_started','in_progress','completed') DEFAULT 'not_started',
    progress_percent INT DEFAULT 0,
    time_spent_seconds INT DEFAULT 0,
    last_exercise_answer TEXT,
    score INT DEFAULT 0,
    completed_at TIMESTAMP NULL,
    UNIQUE KEY (lesson_id, user_id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== Comments =====
CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    article_id INT,
    lesson_id INT,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    is_approved TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== Settings =====
CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    key_name VARCHAR(100) UNIQUE NOT NULL,
    value TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== Math series =====
CREATE TABLE IF NOT EXISTS math_series (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    name_ar VARCHAR(100),
    mathematician VARCHAR(200),
    mathematician_en VARCHAR(200),
    century INT,
    born_year INT,
    died_year INT,
    description TEXT,
    description_en TEXT,
    oeis_ref VARCHAR(50),
    formula TEXT,
    color VARCHAR(50),
    icon VARCHAR(50),
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== Compute nodes =====
CREATE TABLE IF NOT EXISTS compute_nodes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    node_name VARCHAR(100),
    os VARCHAR(50),
    cpu_cores INT,
    ram_mb INT,
    total_work BIGINT DEFAULT 0,
    total_credit INT DEFAULT 0,
    last_seen TIMESTAMP NULL,
    is_active TINYINT DEFAULT 0,
    assigned_token_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== Scientists =====
CREATE TABLE IF NOT EXISTS scientists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name_fa VARCHAR(200) NOT NULL,
    name_en VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200),
    full_name_fa TEXT,
    full_name_en TEXT,
    field VARCHAR(100),
    century INT,
    born_year INT,
    died_year INT,
    born_place VARCHAR(200),
    died_place VARCHAR(200),
    bio_fa LONGTEXT,
    bio_en LONGTEXT,
    bio_ar LONGTEXT,
    achievements_fa TEXT,
    achievements_en TEXT,
    works_fa TEXT,
    works_en TEXT,
    image_url VARCHAR(500),
    wikipedia_url VARCHAR(500),
    oeis_ref VARCHAR(50),
    icon VARCHAR(50),
    color VARCHAR(50),
    sort_order INT DEFAULT 0,
    is_featured TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== Chat rooms =====
CREATE TABLE IF NOT EXISTS chat_rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    name_ar VARCHAR(200),
    category ENUM('math','science','medical','pharmacy','physics','computer','general','custom') DEFAULT 'general',
    description TEXT,
    icon VARCHAR(50) DEFAULT '💬',
    owner_id INT,
    is_public TINYINT DEFAULT 1,
    is_active TINYINT DEFAULT 1,
    max_users INT DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    type ENUM('text','latex','file','image','system') DEFAULT 'text',
    is_pinned TINYINT DEFAULT 0,
    is_deleted TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES chat_rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_room_created (room_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS chat_private (
    id INT AUTO_INCREMENT PRIMARY KEY,
    from_user_id INT NOT NULL,
    to_user_id INT NOT NULL,
    content TEXT NOT NULL,
    is_read TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (to_user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS chat_room_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    user_id INT NOT NULL,
    role ENUM('member','moderator','admin') DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (room_id, user_id),
    FOREIGN KEY (room_id) REFERENCES chat_rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== Work distribution =====
CREATE TABLE IF NOT EXISTS work_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    description TEXT,
    icon VARCHAR(50) DEFAULT '🔬',
    color VARCHAR(50) DEFAULT 'blue',
    category ENUM('math','science','medical','pharmacy','physics','computer','general') DEFAULT 'general',
    min_cpu_cores INT DEFAULT 1,
    min_ram_mb INT DEFAULT 256,
    min_disk_mb INT DEFAULT 0,
    min_gpu_vram_mb INT DEFAULT 0,
    requires_gpu TINYINT DEFAULT 0,
    requires_avx TINYINT DEFAULT 0,
    requires_internet TINYINT DEFAULT 1,
    estimated_time_seconds INT DEFAULT 60,
    credit_per_task INT DEFAULT 1,
    priority INT DEFAULT 100,
    is_active TINYINT DEFAULT 1,
    requires_review TINYINT DEFAULT 0,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS work_queue (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    work_type_id INT NOT NULL,
    payload LONGTEXT NOT NULL,
    priority INT DEFAULT 100,
    status ENUM('pending','assigned','running','completed','failed','cancelled','pending_review') DEFAULT 'pending',
    assigned_node_id INT NULL,
    assigned_at TIMESTAMP NULL,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    result LONGTEXT NULL,
    error_message TEXT,
    attempts INT DEFAULT 0,
    max_attempts INT DEFAULT 3,
    credit_awarded INT DEFAULT 0,
    time_taken_seconds FLOAT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_type_id) REFERENCES work_types(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_node_id) REFERENCES compute_nodes(id) ON DELETE SET NULL,
    INDEX idx_status (status),
    INDEX idx_assigned_node (assigned_node_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS node_specs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    node_id INT NOT NULL UNIQUE,
    cpu_model VARCHAR(200),
    cpu_cores INT,
    cpu_threads INT,
    cpu_freq_mhz INT,
    cpu_benchmark INT,
    ram_total_mb INT,
    ram_available_mb INT,
    disk_total_gb INT,
    disk_free_gb INT,
    disk_type ENUM('hdd','ssd','nvme','unknown') DEFAULT 'unknown',
    gpu_model VARCHAR(200),
    gpu_vram_mb INT,
    gpu_cuda TINYINT DEFAULT 0,
    os_name VARCHAR(100),
    os_version VARCHAR(100),
    arch VARCHAR(50),
    internet_speed_mbps INT,
    is_online TINYINT DEFAULT 0,
    preferred_work_types TEXT,
    blocked_work_types TEXT,
    max_concurrent_tasks INT DEFAULT 1,
    max_hours_per_day INT DEFAULT 24,
    last_benchmark_at TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES compute_nodes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS node_stats_daily (
    id INT AUTO_INCREMENT PRIMARY KEY,
    node_id INT NOT NULL,
    stat_date DATE NOT NULL,
    work_type_id INT,
    tasks_completed INT DEFAULT 0,
    tasks_failed INT DEFAULT 0,
    credit_earned INT DEFAULT 0,
    work_seconds INT DEFAULT 0,
    UNIQUE KEY (node_id, stat_date, work_type_id),
    FOREIGN KEY (node_id) REFERENCES compute_nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (work_type_id) REFERENCES work_types(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== Games & medals =====
CREATE TABLE IF NOT EXISTS games (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    name_ar VARCHAR(100),
    description TEXT,
    icon VARCHAR(50) DEFAULT '🎮',
    color VARCHAR(50) DEFAULT 'blue',
    category ENUM('prime','factor','sinus','pattern','daily','general') DEFAULT 'general',
    is_active TINYINT DEFAULT 1,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS daily_challenge (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challenge_date DATE UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    title_en VARCHAR(200),
    description TEXT,
    description_en TEXT,
    answer TEXT NOT NULL,
    difficulty ENUM('easy','medium','hard','expert') DEFAULT 'medium',
    category VARCHAR(50) DEFAULT 'math',
    participants_count INT DEFAULT 0,
    winners_count INT DEFAULT 0,
    is_published TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS daily_challenge_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challenge_id INT NOT NULL,
    user_id INT NOT NULL,
    answer TEXT NOT NULL,
    is_correct TINYINT DEFAULT 0,
    time_taken_seconds INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (challenge_id) REFERENCES daily_challenge(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS medal_definitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    description TEXT,
    icon VARCHAR(50) DEFAULT '🏆',
    color VARCHAR(50) DEFAULT 'amber',
    requirement_type ENUM('count','specific','streak','daily','special') DEFAULT 'count',
    requirement_value INT DEFAULT 1,
    is_active TINYINT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS user_medals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    medal_type VARCHAR(50) NOT NULL,
    description TEXT,
    challenge_id INT NULL,
    game_id VARCHAR(50) NULL,
    awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (user_id, medal_type),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS game_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    game_name VARCHAR(50) NOT NULL,
    score INT NOT NULL DEFAULT 0,
    level INT DEFAULT 1,
    duration_seconds INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== AI conversations =====
CREATE TABLE IF NOT EXISTS ai_conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255),
    provider VARCHAR(50) DEFAULT 'zai',
    model VARCHAR(100),
    messages LONGTEXT NOT NULL,
    is_archived TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== Themes =====
CREATE TABLE IF NOT EXISTS themes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    primary_color VARCHAR(20) DEFAULT '#3b82f6',
    accent_color VARCHAR(20) DEFAULT '#10b981',
    bg_color VARCHAR(20) DEFAULT '#ffffff',
    text_color VARCHAR(20) DEFAULT '#1f2937',
    font_family VARCHAR(200) DEFAULT 'Vazirmatn, Tahoma, sans-serif',
    is_dark TINYINT DEFAULT 0,
    is_rtl_friendly TINYINT DEFAULT 1,
    is_active TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- پیش‌فرض‌ها
-- ============================================================

INSERT INTO math_series (name, name_en, name_ar, mathematician, mathematician_en, century, born_year, died_year, description, description_en, oeis_ref, formula, color, icon, sort_order) VALUES
('کاشانی', 'Science', 'الكاشاني', 'جمشید کاشانی', 'Jamshid al-Kashi', 15, 1380, 1429, 'اعشار π و سینوس', 'Digits of π and sine', null, 'floor(10^p × sin(π/p))', 'amber', '🔢', 1),
('خیام', 'Khayyam', 'الخيام', 'عمر خیام', 'Omar Khayyam', 11, 1048, 1131, 'مثلث خیام', 'Khayyam triangle', 'A007318', 'C(n,k) mod 2', 'emerald', '📐', 2),
('بیرونی', 'Biruni', 'البيروني', 'ابوریحان بیرونی', 'al-Biruni', 10, 973, 1048, 'فاصله‌های اول', 'Prime gaps', 'A005250', null, 'blue', '🌍', 3),
('کرجی', 'Karaji', 'الكرجي', 'ابوبکر کرجی', 'al-Karaji', 10, 953, 1029, 'اعداد مثلثی', 'Triangular numbers', 'A000217', 'n(n+1)/2', 'purple', '🔺', 4),
('خوارزمی', 'Khwarizmi', 'الخوارزمي', 'محمد خوارزمی', 'al-Khwarizmi', 9, 780, 850, 'جبر', 'Algebra', 'A007917', null, 'rose', '📝', 5),
('طوسی', 'Tusi', 'الطوسي', 'نصیرالدین طوسی', 'Nasir al-Din al-Tusi', 13, 1201, 1274, 'زوج‌های اول', 'Twin primes', 'A001359', null, 'cyan', '♊', 6)
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO scientists (slug, name_fa, name_en, name_ar, full_name_fa, full_name_en, field, century, born_year, died_year, born_place, died_place, bio_fa, bio_en, icon, color, sort_order, is_featured) VALUES
('science', 'جمشید کاشانی', 'Jamshid al-Kashi', 'جمشيد الكاشاني', 'غیاث‌الدین جمشید مسعود کاشانی', 'Ghiyath al-Din Jamshid al-Kashi', 'ریاضی و ستاره‌شناسی', 15, 1380, 1429, 'کاشان', 'سمرقند', 'ریاضیدان و ستاره‌شناس پارسی که π را تا ۱۶ رقم محاسبه کرد', 'Persian mathematician who calculated pi to 16 digits', '🔢', 'amber', 1, 1),
('khayyam', 'عمر خیام', 'Omar Khayyam', 'عمر الخيام', 'غیاث‌الدین عمر خیام نیشابوری', 'Omar Khayyam', 'ریاضی و شعر', 11, 1048, 1131, 'نیشابور', 'نیشابور', 'ریاضیدان و شاعر', 'Mathematician and poet', '📐', 'emerald', 2, 1),
('biruni', 'ابوریحان بیرونی', 'Al-Biruni', 'البيروني', 'ابوریحان بیرونی', 'Al-Biruni', 'همه‌ی علوم', 10, 973, 1048, 'خوارزم', 'غزنی', 'دانشمند پارسی', 'Persian polymath', '🌍', 'blue', 3, 1),
('khwarizmi', 'محمد خوارزمی', 'Al-Khwarizmi', 'الخوارزمي', 'محمد خوارزمی', 'Al-Khwarizmi', 'ریاضی', 9, 780, 850, 'خوارزم', 'بغداد', 'پدر جبر', 'Father of algebra', '📝', 'rose', 4, 1),
('ibn-sina', 'ابن‌سینا', 'Avicenna', 'ابن سينا', 'ابوعلی حسین بن‌سینا', 'Avicenna', 'پزشکی و فلسفه', 10, 980, 1037, 'بخارا', 'همدان', 'پدر پزشکی مدرن', 'Father of modern medicine', '⚕️', 'green', 7, 1),
('razi', 'زکریا رازی', 'Al-Razi', 'الرازي', 'ابوبکر رازی', 'Al-Razi', 'پزشکی و شیمی', 9, 865, 925, 'ری', 'ری', 'پزشک و شیمی‌دان', 'Physician and chemist', '🔬', 'red', 8, 1)
ON DUPLICATE KEY UPDATE name_fa=VALUES(name_fa);

INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES
('چت عمومی', 'General', 'عام', 'general', 'گفتگوی عمومی', '💬'),
('ریاضی', 'Math', 'رياضيات', 'math', 'بحث ریاضی', '🔢'),
('فیزیک', 'Physics', 'فيزياء', 'physics', 'بحث فیزیک', '⚛️'),
('پزشکی', 'Medical', 'طب', 'medical', 'بحث پزشکی', '🏥'),
('داروسازی', 'Pharmacy', 'صيدلة', 'pharmacy', 'بحث داروسازی', '💊'),
('کامپیوتر', 'Computer', 'حاسوب', 'computer', 'بحث کامپیوتر', '💻'),
('علوم پایه', 'Science', 'علوم', 'science', 'علوم پایه', '🔬'),
('آموزش', 'Education', 'تعليم', 'general', 'بحث آموزشی', '📚'),
('هوش مصنوعی', 'AI', 'ذكاء', 'computer', 'بحث AI', '🤖')
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO work_types (slug, name, name_en, description, icon, color, category, min_cpu_cores, min_ram_mb, estimated_time_seconds, credit_per_task, priority, sort_order) VALUES
('factor_small', 'فاکتور کوچک', 'Factor small', 'اعداد ۲۰-۴۰ رقم', '🔢', 'blue', 'math', 1, 256, 5, 1, 50, 1),
('factor_medium', 'فاکتور متوسط', 'Factor medium', 'اعداد ۴۰-۶۰ رقم', '🔢', 'blue', 'math', 2, 512, 30, 2, 40, 2),
('factor_large', 'فاکتور بزرگ', 'Factor large', 'اعداد ۶۰-۸۰ رقم', '🔢', 'indigo', 'math', 4, 1024, 120, 5, 30, 3),
('prime_hunt', 'شکار اول', 'Prime hunt', 'پیدا کردن اعداد اول', '⭐', 'amber', 'math', 2, 512, 60, 3, 35, 4),
('mersenne_check', 'بررسی مرسن', 'Mersenne', 'تست مرسن', '⭐', 'amber', 'math', 4, 2048, 300, 10, 20, 5),
('protein_folding', 'پروتئین', 'Protein', 'شبیه‌سازی پروتئین', '🧬', 'rose', 'medical', 4, 4096, 600, 20, 15, 10),
('drug_screening', 'دارو', 'Drug', 'غربالگری دارویی', '💊', 'emerald', 'pharmacy', 4, 4096, 900, 25, 12, 11),
('sequence_alignment', 'DNA', 'DNA', 'ترازبندی DNA', '🧬', 'rose', 'medical', 2, 1024, 60, 3, 45, 12),
('particle_sim', 'ذرات', 'Particles', 'شبیه‌سازی ذرات', '⚛️', 'purple', 'physics', 4, 4096, 600, 15, 25, 20),
('orbit_calc', 'مدار', 'Orbit', 'محاسبه‌ی مدار', '🪐', 'purple', 'physics', 2, 1024, 120, 5, 35, 21),
('ml_training', 'ML', 'ML training', 'آموزش ML', '🤖', 'cyan', 'computer', 4, 8192, 3600, 50, 10, 30),
('crypto_test', 'کریپتو', 'Crypto', 'تست رمزنگاری', '🔐', 'cyan', 'computer', 2, 1024, 60, 3, 40, 31),
('data_analysis', 'تحلیل داده', 'Data analysis', 'تحلیل داده', '📊', 'amber', 'science', 2, 2048, 300, 8, 30, 40),
('benchmark', 'بنچمارک', 'Benchmark', 'تست سرعت', '⚡', 'gray', 'general', 1, 256, 30, 0, 100, 100)
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO games (slug, name, name_en, icon, color, category, sort_order) VALUES
('prime_hunt', 'شکار اعداد اول', 'Prime Hunt', '🎯', 'blue', 'prime', 1),
('factor_master', 'فاکتورزن', 'Factor Master', '🔢', 'emerald', 'factor', 2),
('sinus_finder', 'سینوس‌یاب', 'Sine Finder', '📐', 'purple', 'sinus', 3),
('pattern_finder', 'کاشف الگو', 'Pattern Finder', '🔍', 'amber', 'pattern', 4),
('daily_quiz', 'مسابقه روزانه', 'Daily Quiz', '📅', 'rose', 'daily', 5)
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO medal_definitions (slug, name, name_en, description, icon, color, requirement_type, requirement_value) VALUES
('first_factor', 'اولین فاکتور', 'First Factor', 'اولین فاکتور', '🎯', 'blue', 'count', 1),
('factor_10', 'فاکتورزن تازه‌کار', 'Novice', '۱۰ فاکتور', '🥉', 'amber', 'count', 10),
('factor_100', 'فاکتورزن حرفه‌ای', 'Expert', '۱۰۰ فاکتور', '🥈', 'emerald', 'count', 100),
('factor_1000', 'استاد فاکتور', 'Master', '۱۰۰۰ فاکتور', '🥇', 'purple', 'count', 1000),
('chat_helper', 'کمک‌رسان', 'Helper', '۱۰۰ پیام چت', '💬', 'blue', 'count', 100),
('first_login', 'اولین ورود', 'First Login', 'اولین ورود', '👋', 'yellow', 'count', 1)
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO themes (name, slug, primary_color, accent_color, bg_color, text_color, font_family, is_dark, is_rtl_friendly, is_active) VALUES
('پیش‌فرض روشن', 'default-light', '#3b82f6', '#10b981', '#ffffff', '#1f2937', 'Vazirmatn, Tahoma, sans-serif', 0, 1, 1),
('تیره', 'dark', '#60a5fa', '#34d399', '#0f172a', '#e2e8f0', 'Vazirmatn, Tahoma, sans-serif', 1, 1, 0),
('علمی', 'scientific', '#0891b2', '#f59e0b', '#f8fafc', '#0f172a', 'Vazirmatn, Tahoma, sans-serif', 0, 1, 0),
('گرم', 'warm', '#dc2626', '#f59e0b', '#fff7ed', '#7c2d12', 'Vazirmatn, Tahoma, sans-serif', 0, 1, 0)
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO settings (key_name, value) VALUES
('site_title_fa', 'پلتفرم علمی چندرشته‌ای پارسی'),
('site_title_en', 'Persian Multidisciplinary Science Platform'),
('site_title_ar', 'منصة العلوم متعددة التخصصات الفارسية'),
('site_subtitle_fa', 'به افتخار غیاث‌الدین جمشید کاشانی'),
('dedicated_to', 'غیاث‌الدین جمشید کاشانی'),
('language_default', 'fa'),
('timezone', 'Asia/Tehran'),
('factordb_token', ''),
('factordb_api', 'https://factordb.com:4059/rpc'),
('chat_enabled', '1'),
('games_enabled', '1'),
('ai_enabled', '1'),
('magazine_enabled', '1'),
('volunteer_enabled', '1'),
('registration_open', '1'),
('chat_max_message_length', '500'),
('chat_rate_limit', '10'),
('ai_provider', 'zai'),
('ai_model', 'glm-4.6'),
('ai_max_tokens', '1000'),
('ai_temperature', '0.7'),
('max_login_attempts', '5'),
('session_lifetime', '604800'),
('jwt_secret', REPLACE(UUID(),'-',''))
ON DUPLICATE KEY UPDATE value=VALUES(value);

-- Insert default ranges
INSERT INTO ranges (start_num, end_num, primes_count, composites_count, is_complete) VALUES
(1, 100000, 9592, 90407, 1),
(1, 1000000, 78498, 921501, 1),
(1, 10000000, 664579, 9335420, 1),
(1, 100000000, 5761455, 94238544, 1),
(1, 200000000, 5317482, 94682519, 1)
ON DUPLICATE KEY UPDATE is_complete=VALUES(is_complete);

-- ============================================================
-- دانشمندان بین‌المللی
-- ============================================================
INSERT INTO scientists (slug, name_fa, name_en, name_ar, full_name_fa, full_name_en, field, century, born_year, died_year, born_place, died_place, bio_fa, bio_en, icon, color, sort_order, is_featured) VALUES
('euclid', 'اقلیدس', 'Euclid', 'إقليدس', 'اقلیدس اسکندرانی', 'Euclid of Alexandria', 'هندسه', -3, -300, -265, 'اسکندریه', 'اسکندریه', 'پدر هندسه — کتاب اصول', 'Father of geometry — Elements', '📐', 'blue', 20, 1),
('archimedes', 'ارشمیدس', 'Archimedes', 'أرخميدس', 'ارشمیدس', 'Archimedes of Syracuse', 'فیزیک و ریاضی', -3, -287, -212, 'سیراکوز', 'سیراکوز', 'ریاضیدان و فیزیک‌دان — قانون شناور', 'Mathematician and physicist — buoyancy', '⚖️', 'amber', 21, 1),
('pythagoras', 'فیثاغورس', 'Pythagoras', 'فيثاغورس', 'فیثاغورس', 'Pythagoras of Samos', 'ریاضی', -6, -570, -495, 'ساموس', 'متاپنتوم', 'قضیه‌ی فیثاغورس', 'Pythagorean theorem', '📐', 'green', 22, 1),
('newton', 'اسحاق نیوتن', 'Isaac Newton', 'إسحاق نيوتن', 'سیر اسحاق نیوتن', 'Sir Isaac Newton', 'فیزیک و ریاضی', 17, 1643, 1727, 'لینکولن‌شایر', 'لندن', 'قوانین حرکت و جاذبه — حساب دیفرانسیل', 'Laws of motion and gravity — calculus', '🍎', 'red', 23, 1),
('euler', 'لئونارد اویلر', 'Leonhard Euler', 'ليونارد أويلر', 'لئونارد اویلر', 'Leonhard Euler', 'ریاضی', 18, 1707, 1783, 'بازل', 'سنت‌پترزبورگ', 'پربازده‌ترین ریاضیدان تاریخ — فرمول e^(iπ)+1=0', 'Most prolific mathematician — Euler formula', '∑', 'indigo', 24, 1),
('gauss', 'کارل فریدریش گاوس', 'Carl Friedrich Gauss', 'كارل فريدريش غاوس', 'کارل فریدریش گاوس', 'Carl Friedrich Gauss', 'ریاضی', 18, 1777, 1855, 'براونشوایگ', 'گوتینگن', 'شاهزاده‌ی ریاضیدانان — نظریه‌ی اعداد', 'Prince of mathematicians — number theory', '🔢', 'purple', 25, 1),
('riemann', 'برنارد ریمان', 'Bernhard Riemann', 'برنارد ريمان', 'برنارد ریمان', 'Bernhard Riemann', 'ریاضی', 19, 1826, 1866, 'هانوفر', 'سلبیا', 'هندسه‌ی ریمانی — فرضیه‌ی ریمان', 'Riemannian geometry — Riemann hypothesis', '📐', 'cyan', 26, 1),
('ramanujan', 'سرینواسا رامانوجان', 'Srinivasa Ramanujan', 'سرينيفاسا رامانوجان', 'سرینواسا رامانوجان', 'Srinivasa Ramanujan', 'ریاضی', 19, 1887, 1920, 'ایرود', 'چنای', 'نابغه‌ی هندی — اعداد خاص رامانوجان', 'Indian genius — Ramanujan numbers', '🔢', 'amber', 27, 1),
('tesla', 'نیکولا تسلا', 'Nikola Tesla', 'نيكولا تسلا', 'نیکولا تسلا', 'Nikola Tesla', 'فیزیک و مهندسی', 19, 1856, 1943, 'اسمیلجان', 'نیویورک', 'مخترع برق متناوب — کویل تسلا', 'AC electricity inventor — Tesla coil', '⚡', 'blue', 28, 1),
('curie', 'ماری کوری', 'Marie Curie', 'ماري كوري', 'ماریا اسکودوفسکا کوری', 'Marie Curie', 'فیزیک و شیمی', 19, 1867, 1934, 'ورشو', 'پاریس', 'نخستین برنده‌ی دو جایزه‌ی نوبل — رادیوم', 'First double Nobel winner — radium', '☢️', 'rose', 29, 1),
('einstein', 'آلبرت انیشتین', 'Albert Einstein', 'ألبرت أينشتاين', 'آلبرت انیشتین', 'Albert Einstein', 'فیزیک', 19, 1879, 1955, 'اولم', 'پریسنتون', 'نسبیت عام و خاص — E=mc²', 'General and special relativity', '⚛️', 'indigo', 30, 1),
('turing', 'آلن تورینگ', 'Alan Turing', 'آلان تورينغ', 'آلن ماتیسون تورینگ', 'Alan Turing', 'کامپیوتر', 20, 1912, 1954, 'لندن', 'وینسلتون', 'پدر علم کامپیوتر — ماشین تورینگ', 'Father of computer science — Turing machine', '💻', 'cyan', 31, 1),
('darwin', 'چارلز داروین', 'Charles Darwin', 'تشارلز داروين', 'چارلز داروین', 'Charles Darwin', 'زیست‌شناسی', 19, 1809, 1882, 'شروزبری', 'داون', 'نظریه‌ی تکامل — انتخاب طبیعی', 'Evolution theory — natural selection', '🧬', 'green', 32, 1),
('maxwell', 'جیمز کلرک ماکسول', 'James Clerk Maxwell', 'جيمس كليرك ماكسويل', 'جیمز کلرک ماکسول', 'James Clerk Maxwell', 'فیزیک', 19, 1831, 1879, 'ادینبرگ', 'کمبریج', 'معادلات ماکسول — الکترومغناطیس', 'Maxwell equations — electromagnetism', '📡', 'blue', 33, 1),
('nobel', 'آلفرد نوبل', 'Alfred Nobel', 'ألفريد نوبل', 'آلفرد برنارد نوبل', 'Alfred Nobel', 'شیمی', 19, 1833, 1896, 'استکهلم', 'سنریمو', 'مخترع دینامیت — بنیان‌گذار جایزه‌ی نوبل', 'Dynamite inventor — Nobel Prize founder', '🧪', 'amber', 34, 0),
('fibonacci', 'لئوناردو فیبوناچی', 'Leonardo Fibonacci', 'ليوناردو فيبوناتشي', 'لئوناردو پیزانو فیبوناچی', 'Leonardo Fibonacci', 'ریاضی', 12, 1170, 1250, 'پیزا', 'پیزا', 'دنباله‌ی فیبوناچی — اعداد هندی-عربی در اروپا', 'Fibonacci sequence — brought Hindu-Arabic numerals', '🔢', 'emerald', 35, 1),
('galileo', 'گالیله', 'Galileo Galilei', 'غاليليو غاليلي', 'گالیله گالیله', 'Galileo Galilei', 'فیزیک و ستاره‌شناسی', 16, 1564, 1642, 'پیزا', 'آرچتری', 'پدر علم فیزیک — تلسکوپ — حرکت زمین', 'Father of physics — telescope — heliocentrism', '🔭', 'amber', 36, 1),
('bohr', 'نیلز بوهر', 'Niels Bohr', 'نيلز بوهر', 'نیلز هنریک داوید بوهر', 'Niels Bohr', 'فیزیک', 19, 1885, 1962, 'کپنهاگ', 'کپنهاگ', 'مدل اتم بوهر — مکانیک کوانتومی', 'Bohr model — quantum mechanics', '⚛️', 'blue', 37, 0),
('shannon', 'کلود شانون', 'Claude Shannon', 'كلود شانون', 'کلود الوود شانون', 'Claude Shannon', 'کامپیوتر', 20, 1916, 2001, 'پتوسکی', 'مفورد', 'پدر نظریه‌ی اطلاعات — بیت', 'Father of information theory — bit', '💾', 'cyan', 38, 0)
ON DUPLICATE KEY UPDATE name_fa=VALUES(name_fa);

-- More scientists (batch 3)
INSERT INTO scientists (slug, name_fa, name_en, name_ar, full_name_fa, full_name_en, field, century, born_year, died_year, born_place, died_place, bio_fa, bio_en, icon, color, sort_order, is_featured) VALUES
('faraday', 'مایکل فارادی', 'Michael Faraday', 'مايكل فاراداي', 'مایکل فارادی', 'Michael Faraday', 'فیزیک و شیمی', 18, 1791, 1867, 'لندن', 'لندن', 'الکترومغناطیس — موتور الکتریکی', 'Electromagnetism — electric motor', '⚡', 'amber', 60, 1),
('ampere', 'آمپر', 'André-Marie Ampère', 'أندري-ماري أمبير', 'آندره-ماری آمپر', 'André-Marie Ampère', 'فیزیک', 18, 1775, 1836, 'لیون', 'مارسی', 'پدر الکترودینامیک — واحد آمپر', 'Father of electrodynamics', '⚡', 'blue', 61, 0),
('volt', 'الساندرو ولتا', 'Alessandro Volta', 'أليساندرو فولتا', 'الساندرو جوزپه آنتونیو آناستاسیو ولتا', 'Alessandro Volta', 'فیزیک', 18, 1745, 1827, 'کومو', 'کومو', 'اختراع باتری — پیل ولتایی', 'Invented battery — voltaic pile', '🔋', 'emerald', 62, 0),
('ohm', 'گئورگ اهم', 'Georg Ohm', 'غيورغ أوم', 'گئورگ سیمون اهم', 'Georg Ohm', 'فیزیک', 18, 1789, 1854, 'ارلانگن', 'مونیخ', 'قانون اهم — V=IR', 'Ohm law — V=IR', '🔌', 'cyan', 63, 0),
('mendel', 'گریگور مندل', 'Gregor Mendel', 'غريغور مندل', 'گریگور یوهان مندل', 'Gregor Mendel', 'زیست‌شناسی', 19, 1822, 1884, 'هاینزندورف', 'برنو', 'پدر ژنتیک — قوانین مندل', 'Father of genetics — Mendel laws', '🧬', 'green', 64, 1),
('linnaeus', 'کارل لینه', 'Carl Linnaeus', 'كارل لينيوس', 'کارل لینه', 'Carl Linnaeus', 'زیست‌شناسی', 18, 1707, 1778, 'اسمولند', 'اولاستاد', 'پدر تاکسونومی — نام‌گذاری دوجنسی', 'Father of taxonomy — binomial nomenclature', '🌿', 'emerald', 65, 0),
('hubble', 'ادوین هابل', 'Edwin Hubble', 'إدوين هابل', 'ادوین پاول هابل', 'Edwin Hubble', 'ستاره‌شناسی', 20, 1889, 1953, 'مارسفیلد', 'سن‌مارینو', 'انبساط جهان — کهکشان‌های دور', 'Expanding universe — distant galaxies', '🌌', 'indigo', 66, 1),
('sagan', 'کارل ساگان', 'Carl Sagan', 'كارل ساجان', 'کارل ادوارد ساگان', 'Carl Sagan', 'ستاره‌شناسی', 20, 1934, 1996, 'نیویورک', 'سیاتل', 'ستاره‌شناس — Cosmos — جستجوی هوش فرازمینی', 'Astronomer — Cosmos — SETI', '🌠', 'blue', 67, 1),
('tesla-nikola', 'نیکولا تسلا', 'Nikola Tesla', 'نيكولا تسلا', 'نیکولا تسلا', 'Nikola Tesla', 'فیزیک و مهندسی', 19, 1856, 1943, 'اسمیلجان', 'نیویورک', 'برق متناوب — کویل تسلا — انتقال بی‌سیم', 'AC electricity — Tesla coil — wireless', '⚡', 'cyan', 68, 1),
('pascal', 'بلز پاسکال', 'Blaise Pascal', 'بليز باسكال', 'بلز پاسکال', 'Blaise Pascal', 'ریاضی و فیزیک', 17, 1623, 1662, 'کلرمون', 'پاریس', 'مثلث پاسکال — فشار — ماشین حساب', 'Pascal triangle — pressure — calculator', '📐', 'blue', 69, 1),
('fermat', 'پیر فرما', 'Pierre de Fermat', 'بيير دي فيرما', 'پیر دو فرما', 'Pierre de Fermat', 'ریاضی', 17, 1607, 1665, 'بومون', 'کاستر', 'قضیه‌ی بزرگ فرما — نظریه‌ی اعداد', 'Fermat last theorem — number theory', '🔢', 'amber', 70, 1),
('leibniz', 'گوتفرید لایب‌نیتس', 'Gottfried Leibniz', 'غوتفريد لايبنيتس', 'گوتفرید ویلهلم لایب‌نیتس', 'Gottfried Leibniz', 'ریاضی و فلسفه', 17, 1646, 1716, 'لایپزیگ', 'هانوفر', 'حساب دیفرانسیل — منطق ریاضی', 'Calculus — mathematical logic', '∫', 'purple', 71, 1),
('descartes', 'رنه دکارت', 'René Descartes', 'رينيه ديكارت', 'رنه دکارت', 'René Descartes', 'ریاضی و فلسفه', 17, 1596, 1650, 'لاهه', 'استکهلم', 'سیستم مختصات دکارتی — تفکر، هست', 'Cartesian coordinates — I think therefore I am', '📊', 'indigo', 72, 1),
('napier', 'جان نپر', 'John Napier', 'جون نابير', 'جان نپر', 'John Napier', 'ریاضی', 16, 1550, 1617, 'ادینبرگ', 'ادینبرگ', 'اختراع لگاریتم — استخوان نپر', 'Invented logarithms — Napier bones', '📐', 'emerald', 73, 0),
('abel', 'نیلز هنریک آبل', 'Niels Henrik Abel', 'نيلز هنريك أبيل', 'نیلز هنریک آبل', 'Niels Henrik Abel', 'ریاضی', 19, 1802, 1829, 'فیندا', 'فرولند', 'گروه‌های آبل — معادلات درجه ۵', 'Abelian groups — quintic equations', '∑', 'blue', 74, 0),
('galois', 'اواریست گالوا', 'Évariste Galois', 'إيفاريست غالوا', 'اواریست گالوا', 'Évariste Galois', 'ریاضی', 19, 1811, 1832, 'بور-لا-رین', 'پاریس', 'نظریه‌ی گالوا — گروه‌ها — مرگ در ۲۰ سالگی', 'Galois theory — groups — died at 20', '∑', 'rose', 75, 1),
('weierstrass', 'کارل وایرشتراس', 'Karl Weierstrass', 'كارل فايرشتراس', 'کارل تئودور ویلهلم وایرشتراس', 'Karl Weierstrass', 'ریاضی', 19, 1815, 1897, 'اوفنبرگ', 'برلین', 'پدر تحلیل مدرن — تابع ε-δ', 'Father of modern analysis', '∫', 'cyan', 76, 0),
('riemann-bernhard', 'برنارد ریمان', 'Bernhard Riemann', 'برنارد ريمان', 'گئورگ فردریش برنارد ریمان', 'Bernhard Riemann', 'ریاضی', 19, 1826, 1866, 'هانوفر', 'سلبیا', 'هندسه‌ی ریمانی — فرضیه‌ی ریمان — انتگرال ریمان', 'Riemannian geometry — hypothesis', '📐', 'purple', 77, 1),
('hadamard', 'ژاک آدامار', 'Jacques Hadamard', 'جاك هادامار', 'ژاک سالومون آدامار', 'Jacques Hadamard', 'ریاضی', 19, 1865, 1963, 'ورسای', 'پاریس', 'قضیه‌ی عدد اول — ماتریس آدامار', 'Prime number theorem — Hadamard matrix', '🔢', 'amber', 78, 0),
('selberg', 'آتل سلبرگ', 'Atle Selberg', 'آتلي سيلبرغ', 'آتل سلبرگ', 'Atle Selberg', 'ریاضی', 20, 1917, 2007, 'لانگرود', 'پریسنتون', 'قضیه‌ی عدد اول — اثر سلبرگ', 'Prime number theorem — Selberg trace', '🔢', 'blue', 79, 0),
('erdos', 'پل اردیش', 'Paul Erdős', 'بول إيرديش', 'پل اردیش', 'Paul Erdős', 'ریاضی', 20, 1913, 1996, 'بوداپست', 'ورشو', 'پربازده‌ترین ریاضیدان — عدد اردیش', 'Most prolific — Erdős number', '🔢', 'rose', 80, 1),
('wiles', 'اندرو وایلز', 'Andrew Wiles', 'أندرو ويلز', 'سر اندرو جان وایلز', 'Andrew Wiles', 'ریاضی', 20, 1953, null, 'کمبریج', null, 'اثبات قضیه‌ی بزرگ فرما — ۳۵۸ سال بعد', 'Proved Fermat last theorem', '✓', 'indigo', 81, 1),
('perl', 'لری وال', 'Larry Wall', 'لاري وال', 'لری وال', 'Larry Wall', 'کامپیوتر', 20, 1954, null, 'لس‌آنجلس', null, 'سازنده‌ی Perl — زبان برنامه‌نویسی', 'Creator of Perl', '💻', 'purple', 82, 0),
('torvalds', 'لینوس توروالدز', 'Linus Torvalds', 'لينوس تورفالدس', 'لینوس بندیکت توروالدز', 'Linus Torvalds', 'کامپیوتر', 20, 1969, null, 'هلسینکی', null, 'سازنده‌ی Linux و Git', 'Creator of Linux and Git', '🐧', 'cyan', 83, 1)
ON DUPLICATE KEY UPDATE name_fa=VALUES(name_fa);

-- More scientists (batch 4) — target 80+
INSERT INTO scientists (slug, name_fa, name_en, name_ar, full_name_fa, full_name_en, field, century, born_year, died_year, born_place, died_place, bio_fa, bio_en, icon, color, sort_order, is_featured) VALUES
('bardeen', 'جان باردین', 'John Bardeen', 'جون باردين', 'جان باردین', 'John Bardeen', 'فیزیک', 20, 1908, 1991, 'مدیسون', 'باستون', 'تنها دو بار جایزه‌ی نوبل در فیزیک — ترانزیستور', 'Only double Nobel in physics — transistor', '⚡', 'blue', 84, 1),
('shockley', 'ویلیام شاکلی', 'William Shockley', 'ويليام شوكلي', 'ویلیام برادفورد شاکلی', 'William Shockley', 'فیزیک', 20, 1910, 1989, 'لندن', 'استنفورد', 'اختراع ترانزیستور — جایزه‌ی نوبل', 'Invented transistor — Nobel Prize', '💻', 'cyan', 85, 0),
('brattain', 'والتر براتین', 'Walter Brattain', 'والتر براتين', 'والتر هاوزر براتین', 'Walter Brattain', 'فیزیک', 20, 1902, 1987, 'شیامین', 'سیاتل', 'ترانزیستور — جایزه‌ی نوبل', 'Transistor — Nobel Prize', '💻', 'amber', 86, 0),
('mozart', 'موتسارت', 'Wolfgang Mozart', 'موتسارت', 'یوهان کریزوستوم ولفگانگ آمادئوس موتسارت', 'Wolfgang Amadeus Mozart', 'موسیقی', 18, 1756, 1791, 'سالزبورگ', 'وین', 'نابغه‌ی موسیقی — ۶۰۰+ اثر', 'Music genius — 600+ works', '🎵', 'rose', 87, 0),
('beethoven', 'بتهوون', 'Ludwig Beethoven', 'بيتهوفن', 'لودویگ فان بتهوون', 'Ludwig van Beethoven', 'موسیقی', 18, 1770, 1827, 'بن', 'وین', 'نابغه‌ی موسیقی — ناشنوا شد ولی ساخت', 'Music genius — composed when deaf', '🎵', 'indigo', 88, 0),
('einstein-albert', 'آلبرت انیشتین', 'Albert Einstein', 'ألبرت أينشتاين', 'آلبرت انیشتین', 'Albert Einstein', 'فیزیک', 19, 1879, 1955, 'اولم', 'پریسنتون', 'نسبیت — E=mc² — جایزه‌ی نوبل', 'Relativity — E=mc² — Nobel', '⚛️', 'indigo', 89, 1),
('bohr-niels', 'نیلز بوهر', 'Niels Bohr', 'نيلز بوهر', 'نیلز هنریک داوید بوهر', 'Niels Bohr', 'فیزیک', 19, 1885, 1962, 'کپنهاگ', 'کپنهاگ', 'مدل اتم بوهر — مکانیک کوانتومی — نوبل', 'Bohr model — quantum mechanics — Nobel', '⚛️', 'blue', 90, 1),
('heisenberg-w', 'ورنر هایزنبرگ', 'Werner Heisenberg', 'فيرنر هايزنبرغ', 'ورنر کارل هایزنبرگ', 'Werner Heisenberg', 'فیزیک', 20, 1901, 1976, 'وورتسبورگ', 'مونیخ', 'اصل عدم قطعیت — نوبل', 'Uncertainty principle — Nobel', '⚛️', 'cyan', 91, 0),
('schrodinger-e', 'اروین شرودینگر', 'Erwin Schrödinger', 'إروين شرودنغر', 'اروین شرودینگر', 'Erwin Schrödinger', 'فیزیک', 19, 1887, 1961, 'وین', 'وین', 'معادله شرودینگر — گربه شرودینگر — نوبل', 'Schrödinger equation — cat — Nobel', '🐈', 'purple', 92, 0),
('pauli', 'ولفگانگ پاولی', 'Wolfgang Pauli', 'فولفغانغ باولي', 'ولفگانگ ارنست پاولی', 'Wolfgang Pauli', 'فیزیک', 20, 1900, 1958, 'وین', 'زوریخ', 'اصل طرد پاولی — نوبل', 'Pauli exclusion principle — Nobel', '⚛️', 'amber', 93, 0),
('debroglie', 'لوئی دوبروی', 'Louis de Broglie', 'لويس دي بروغلي', 'لوئی ویکتور پیر رایمون دوبروی', 'Louis de Broglie', 'فیزیک', 19, 1892, 1987, 'دیپ', 'لووشه', 'موج-ذره — طول موج دوبروی — نوبل', 'Wave-particle — de Broglie wavelength — Nobel', '🌊', 'blue', 94, 0),
('born', 'ماکس بورن', 'Max Born', 'ماكس بورن', 'ماکس بورن', 'Max Born', 'فیزیک', 19, 1882, 1970, 'برسلاو', 'گوتینگن', 'تفسیر احتمالی کوانتوم — نوبل', 'Probabilistic quantum interpretation — Nobel', '⚛️', 'cyan', 95, 0),
('lander', 'رابرت لند', 'Robert Lander', 'روبرت لند', 'رابرت لند', 'Robert Lander', 'شیمی', 19, 1903, 1973, 'سانی', 'ریچموند', 'تحلیل گرمایی — تکنیک‌های آزمایشگاهی', 'Thermal analysis — lab techniques', '🧪', 'amber', 96, 0),
('pare', 'امبروز پاره', 'Ambroise Paré', 'أمبرواز باري', 'امبروز پاره', 'Ambroise Paré', 'پزشکی', 16, 1510, 1590, 'لاوال', 'پاریس', 'پدر جراحی مدرن — بندآرteri', 'Father of modern surgery', '⚕️', 'green', 97, 0),
('vesalius', 'وسالیوس', 'Andreas Vesalius', 'أندرياس فيساليوس', 'آندریاس وسالیوس', 'Andreas Vesalius', 'پزشکی', 16, 1514, 1564, 'برکسل', 'زاکنته', 'پدر آناتومی مدرن', 'Father of modern anatomy', '🫀', 'rose', 98, 0),
('harvey', 'ویلیام هاروی', 'William Harvey', 'ويليام هارفي', 'ویلیام هاروی', 'William Harvey', 'پزشکی', 16, 1578, 1657, 'فولکستون', 'لندن', 'کشف گردش خون', 'Discovered blood circulation', '🫀', 'red', 99, 1)
ON DUPLICATE KEY UPDATE name_fa=VALUES(name_fa);
