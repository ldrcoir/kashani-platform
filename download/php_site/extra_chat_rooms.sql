-- Additional chat rooms
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('چت عمومی', 'General', 'عام', 'general', 'گفتگوی عمومی', '💬') ON DUPLICATE KEY UPDATE name=VALUES(name);
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('ریاضی', 'Math', 'رياضيات', 'math', 'بحث ریاضی', '🔢') ON DUPLICATE KEY UPDATE name=VALUES(name);
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('فیزیک', 'Physics', 'فيزياء', 'physics', 'بحث فیزیک', '⚛️') ON DUPLICATE KEY UPDATE name=VALUES(name);
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('پزشکی', 'Medical', 'طب', 'medical', 'بحث پزشکی', '🏥') ON DUPLICATE KEY UPDATE name=VALUES(name);
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('داروسازی', 'Pharmacy', 'صيدلة', 'pharmacy', 'بحث داروسازی', '💊') ON DUPLICATE KEY UPDATE name=VALUES(name);
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('کامپیوتر', 'Computer', 'حاسوب', 'computer', 'بحث کامپیوتر', '💻') ON DUPLICATE KEY UPDATE name=VALUES(name);
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('علوم پایه', 'Science', 'علوم', 'science', 'علوم پایه', '🔬') ON DUPLICATE KEY UPDATE name=VALUES(name);
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('آموزش', 'Education', 'تعليم', 'general', 'بحث آموزشی', '📚') ON DUPLICATE KEY UPDATE name=VALUES(name);
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('هوش مصنوعی', 'AI', 'ذكاء', 'computer', 'بحث AI', '🤖') ON DUPLICATE KEY UPDATE name=VALUES(name);
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('فلسفه', 'Philosophy', 'فلسفة', 'general', 'بحث فلسفی', '🧠') ON DUPLICATE KEY UPDATE name=VALUES(name);
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('موسیقی', 'Music', 'موسيقى', 'general', 'بحث موسیقی', '🎵') ON DUPLICATE KEY UPDATE name=VALUES(name);
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('شیمی', 'Chemistry', 'كيمياء', 'science', 'بحث شیمی', '🧪') ON DUPLICATE KEY UPDATE name=VALUES(name);
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('زیست‌شناسی', 'Biology', 'أحياء', 'science', 'بحث زیست', '🧬') ON DUPLICATE KEY UPDATE name=VALUES(name);
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('ستاره‌شناسی', 'Astronomy', 'فلك', 'physics', 'بحث ستاره‌شناسی', '🌌') ON DUPLICATE KEY UPDATE name=VALUES(name);
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('تاریخ', 'History', 'تاريخ', 'general', 'بحث تاریخی', '📜') ON DUPLICATE KEY UPDATE name=VALUES(name);
INSERT INTO chat_rooms (name, name_en, name_ar, category, description, icon) VALUES ('ادبیات', 'Literature', 'أدب', 'general', 'بحث ادبی', '📖') ON DUPLICATE KEY UPDATE name=VALUES(name);
