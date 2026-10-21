-- themes.sql — تم‌های قابل انتخاب از پنل ادمین
INSERT INTO themes (name, slug, primary_color, accent_color, bg_color, text_color, font_family, is_dark, is_rtl_friendly, is_active) VALUES
('بنفش مدرن', 'purple-modern', '#7c3aed', '#06b6d4', '#f8fafc', '#1e293b', 'Vazirmatn, sans-serif', 0, 1, 0),
('آبی اقیانوسی', 'ocean-blue', '#0ea5e9', '#8b5cf6', '#f0f9ff', '#0c4a6e', 'Vazirmatn, sans-serif', 0, 1, 0),
('سبز جنگلی', 'forest-green', '#16a34a', '#f59e0b', '#f0fdf4', '#14532d', 'Vazirmatn, sans-serif', 0, 1, 0),
('نارنجی گرم', 'warm-orange', '#ea580c', '#7c3aed', '#fff7ed', '#7c2d12', 'Vazirmatn, sans-serif', 0, 1, 0),
('طلایی سلطنتی', 'royal-gold', '#d97706', '#1e40af', '#fffbeb', '#78350f', 'Vazirmatn, sans-serif', 0, 1, 0),
('قرمز یاقوتی', 'ruby-red', '#dc2626', '#f59e0b', '#fef2f2', '#7f1d1d', 'Vazirmatn, sans-serif', 0, 1, 0),
('تیره مدرن', 'dark-modern', '#818cf8', '#34d399', '#0f172a', '#e2e8f0', 'Vazirmatn, sans-serif', 1, 1, 0),
('تیره بنفش', 'dark-purple', '#a78bfa', '#f472b6', '#1e1b29', '#e9d5ff', 'Vazirmatn, sans-serif', 1, 1, 0),
('تیره سبز', 'dark-green', '#4ade80', '#fbbf24', '#0a1a0f', '#d1fae5', 'Vazirmatn, sans-serif', 1, 1, 0),
('تیره آبی', 'dark-blue', '#60a5fa', '#f9a8d4', '#0c1929', '#bfdbfe', 'Vazirmatn, sans-serif', 1, 1, 0)
ON DUPLICATE KEY UPDATE name=VALUES(name);
