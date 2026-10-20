<?php
// ============================================================
// sitemap.php — نقشه‌ی سایت پویا برای SEO
// ============================================================
require_once __DIR__ . '/functions.php';
secure_session_start();
header('Content-Type: application/xml; charset=utf-8');

$site_url = Settings::get('site_url', 'https://' . ($_SERVER['HTTP_HOST'] ?? 'platform-oloom.ir'));
$site_url = rtrim($site_url, '/');

$pdo = Database::getInstance();
$urls = [
    ['loc' => $site_url . '/', 'priority' => '1.0', 'changefreq' => 'daily'],
    ['loc' => $site_url . '/factor.php', 'priority' => '0.9', 'changefreq' => 'weekly'],
    ['loc' => $site_url . '/lessons.php', 'priority' => '0.9', 'changefreq' => 'daily'],
    ['loc' => $site_url . '/magazine.php', 'priority' => '0.9', 'changefreq' => 'daily'],
    ['loc' => $site_url . '/scientists.php', 'priority' => '0.8', 'changefreq' => 'weekly'],
    ['loc' => $site_url . '/network.php', 'priority' => '0.7', 'changefreq' => 'daily'],
    ['loc' => $site_url . '/download.php', 'priority' => '0.7', 'changefreq' => 'weekly'],
    ['loc' => $site_url . '/chat.php', 'priority' => '0.6', 'changefreq' => 'always'],
];

// Add published articles
try {
    $articles = $pdo->query("SELECT slug, updated_at FROM articles WHERE is_published = 1 ORDER BY created_at DESC LIMIT 1000")->fetchAll();
    foreach ($articles as $a) {
        $urls[] = ['loc' => $site_url . '/article.php?slug=' . urlencode($a['slug']), 'priority' => '0.7', 'changefreq' => 'weekly', 'lastmod' => date('Y-m-d', strtotime($a['updated_at']))];
    }
} catch (Exception $e) {}

// Add published lessons
try {
    $lessons = $pdo->query("SELECT slug, updated_at FROM lessons WHERE is_published = 1 ORDER BY sort_order LIMIT 500")->fetchAll();
    foreach ($lessons as $l) {
        $urls[] = ['loc' => $site_url . '/lesson.php?slug=' . urlencode($l['slug']), 'priority' => '0.7', 'changefreq' => 'weekly', 'lastmod' => date('Y-m-d', strtotime($l['updated_at']))];
    }
} catch (Exception $e) {}

// Add scientists
try {
    $scientists = $pdo->query("SELECT slug FROM scientists ORDER BY sort_order LIMIT 100")->fetchAll();
    foreach ($scientists as $s) {
        $urls[] = ['loc' => $site_url . '/scientist.php?slug=' . urlencode($s['slug']), 'priority' => '0.6', 'changefreq' => 'monthly'];
    }
} catch (Exception $e) {}

echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<?php foreach ($urls as $u): ?>
    <url>
        <loc><?= htmlspecialchars($u['loc']) ?></loc>
        <?php if (!empty($u['lastmod'])): ?><lastmod><?= $u['lastmod'] ?></lastmod><?php endif; ?>
        <changefreq><?= $u['changefreq'] ?></changefreq>
        <priority><?= $u['priority'] ?></priority>
    </url>
<?php endforeach; ?>
</urlset>
