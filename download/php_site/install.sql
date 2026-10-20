-- ============================================================
-- install.sql — MySQL database setup for cPanel
-- Run this in phpMyAdmin or cPanel > MySQL Databases
-- ============================================================

CREATE DATABASE IF NOT EXISTS persian_math CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE persian_math;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    phone VARCHAR(20),
    phone_verified TINYINT DEFAULT 0,
    role ENUM('user','admin','superadmin') DEFAULT 'user',
    credits INT DEFAULT 0,
    avatar VARCHAR(255),
    bio TEXT,
    country VARCHAR(100) DEFAULT 'Iran',
    language VARCHAR(10) DEFAULT 'fa',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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

CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    title_en VARCHAR(500),
    title_ar VARCHAR(500),
    slug VARCHAR(255) UNIQUE NOT NULL,
    excerpt TEXT,
    content LONGTEXT NOT NULL,
    content_en LONGTEXT,
    content_ar LONGTEXT,
    image_url VARCHAR(255),
    category VARCHAR(50) DEFAULT 'math',
    tags VARCHAR(500),
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

CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    article_id INT,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    is_approved TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    key_name VARCHAR(100) UNIQUE NOT NULL,
    value TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default math series
INSERT INTO math_series (name, name_en, name_ar, mathematician, mathematician_en, century, born_year, died_year, description, description_en, oeis_ref, formula, color, icon, sort_order) VALUES
('کاشانی', 'Kashani', 'الكاشاني', 'Jamshid al-Kashi', 'Ghiyath al-Din Jamshid al-Kashi', 15, 1380, 1429, 'اعشار π و سینوس', 'Digits of π and sine theorem', NULL, 'floor(10^p × sin(π/p))', 'amber', '🔢', 1),
('خیام', 'Khayyam', 'الخيام', 'Omar Khayyam', 'Omar Khayyam', 11, 1048, 1131, 'مثلث خیام', 'Khayyam triangle', 'A007318', 'C(n,k) mod 2', 'emerald', '📐', 2),
('بیرونی', 'Biruni', 'البيروني', 'Abu Rayhan al-Biruni', 'al-Biruni', 10, 973, 1048, 'فاصله‌های اول', 'Prime gaps', 'A005250', NULL, 'blue', '🌍', 3),
('کرجی', 'Karaji', 'الكرجي', 'Abu Bakr al-Karaji', 'al-Karaji', 10, 953, 1029, 'اعداد مثلثی', 'Triangular numbers', 'A000217', 'n(n+1)/2', 'purple', '🔺', 4),
('خوارزمی', 'Khwarizmi', 'الخوارزمي', 'Muhammad al-Khwarizmi', 'al-Khwarizmi', 9, 780, 850, 'جبر', 'Algebra', 'A007917', NULL, 'rose', '📝', 5),
('طوسی', 'Tusi', 'الطوسي', 'Nasir al-Din al-Tusi', 'al-Tusi', 13, 1201, 1274, 'زوج‌های اول', 'Twin primes', 'A001359', NULL, 'cyan', '♊', 6),
('سلطانی', 'Soltani', 'السلطاني', 'Golden Age of Islamic Science', 'Islamic Golden Age', NULL, NULL, NULL, 'اعداد کامل', 'Perfect numbers', 'A000396', '2^(p-1) × (2^p - 1)', 'yellow', '⭐', 7);

-- Insert default settings
INSERT INTO settings (key_name, value) VALUES
('site_title_fa', 'پلتفرم ریاضی پارسی'),
('site_title_en', 'Persian Math Platform'),
('site_title_ar', 'منصة الرياضيات الفارسية'),
('dedicated_to', 'به افتخار Jamshid al-Kashi (الکاشی)'),
('language_default', 'fa'),
('magazine_enabled', '1'),
('volunteer_enabled', '1'),
('factordb_token', '6ddb5c17a56f920f3ee459e99036bd57');

-- Insert admin user (change password after install!)
INSERT INTO users (email, name, role, language) VALUES
('admin@persian-math.ir', 'Admin', 'superadmin', 'fa');
