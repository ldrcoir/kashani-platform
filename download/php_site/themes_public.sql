-- ============================================================
-- themes_public.sql — تم‌های قابل انتخاب توسط عموم کاربران
-- ============================================================
-- کاربران می‌توانند تم سایت را خودشان انتخاب کنند

CREATE TABLE IF NOT EXISTS user_theme_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    theme_slug VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (user_id, theme_slug),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10 themes available for all users
INSERT INTO themes (name, slug, primary_color, accent_color, bg_color, text_color, font_family, is_dark, is_rtl_friendly, is_active) VALUES
('Indigo Modern', 'indigo-modern', '#4f46e5', '#06b6d4', '#f8fafc', '#1e293b', 'Vazirmatn, sans-serif', 0, 1, 1),
('Purple Dream', 'purple-dream', '#7c3aed', '#ec4899', '#faf5ff', '#4c1d95', 'Vazirmatn, sans-serif', 0, 1, 1),
('Ocean Blue', 'ocean-blue', '#0ea5e9', '#8b5cf6', '#f0f9ff', '#0c4a6e', 'Vazirmatn, sans-serif', 0, 1, 1),
('Forest Green', 'forest-green', '#16a34a', '#f59e0b', '#f0fdf4', '#14532d', 'Vazirmatn, sans-serif', 0, 1, 1),
('Warm Orange', 'warm-orange', '#ea580c', '#7c3aed', '#fff7ed', '#7c2d12', 'Vazirmatn, sans-serif', 0, 1, 1),
('Dark Modern', 'dark-modern', '#818cf8', '#34d399', '#0f172a', '#e2e8f0', 'Vazirmatn, sans-serif', 1, 1, 1),
('Dark Purple', 'dark-purple', '#a78bfa', '#f472b6', '#1e1b29', '#e9d5ff', 'Vazirmatn, sans-serif', 1, 1, 1),
('Dark Green', 'dark-green', '#4ade80', '#fbbf24', '#0a1a0f', '#d1fae5', 'Vazirmatn, sans-serif', 1, 1, 1),
('Dark Ocean', 'dark-ocean', '#60a5fa', '#f9a8d4', '#0c1929', '#bfdbfe', 'Vazirmatn, sans-serif', 1, 1, 1),
('Dark Rose', 'dark-rose', '#fb7185', '#c084fc', '#1c1115', '#fecdd3', 'Vazirmatn, sans-serif', 1, 1, 1)
ON DUPLICATE KEY UPDATE name=VALUES(name);
