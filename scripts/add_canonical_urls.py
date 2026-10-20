#!/usr/bin/env python3
"""
🔧 افزودن canonical URL و JSON-LD به همه‌ی صفحات عمومی سایت
"""
import os
import re

PAGES = [
    '/home/z/my-project/download/php_site/factor.php',
    '/home/z/my-project/download/php_site/lessons.php',
    '/home/z/my-project/download/php_site/magazine.php',
    '/home/z/my-project/download/php_site/scientists.php',
    '/home/z/my-project/download/php_site/network.php',
    '/home/z/my-project/download/php_site/download.php',
    '/home/z/my-project/download/php_site/chat.php',
    '/home/z/my-project/download/php_site/article.php',
    '/home/z/my-project/download/php_site/lesson.php',
    '/home/z/my-project/download/php_site/scientist.php',
]

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find <head> section
    head_match = re.search(r'<head>(.*?)</head>', content, re.DOTALL)
    if not head_match:
        print(f"  ⚠️ {os.path.basename(path)}: no <head>")
        return False
    
    head = head_match.group(1)
    
    # Check if canonical already exists
    if 'rel="canonical"' in head:
        print(f"  ✓ {os.path.basename(path)}: already has canonical")
        return False
    
    # Determine page slug for canonical
    filename = os.path.basename(path)
    if filename == 'article.php':
        canonical = "<?= site_url() ?>/article.php?slug=<?= urlencode(\$article['slug']) ?>"
    elif filename == 'lesson.php':
        canonical = "<?= site_url() ?>/lesson.php?slug=<?= urlencode(\$lesson['slug']) ?>"
    elif filename == 'scientist.php':
        canonical = "<?= site_url() ?>/scientist.php?slug=<?= urlencode(\$s['slug']) ?>"
    else:
        canonical = f"<?= site_url() ?>/{filename}"
    
    # Add canonical link after <meta charset>
    canonical_html = f'\n    <link rel="canonical" href="{canonical}">\n'
    
    # Insert after first meta tag
    new_head = re.sub(
        r'(<meta charset="UTF-8">)',
        r'\1' + canonical_html,
        head,
        count=1
    )
    
    new_content = content.replace(head, new_head, 1)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✅ {filename}: canonical added")
    return True

def main():
    print("🔧 افزودن canonical URL به صفحات:")
    count = 0
    for path in PAGES:
        if os.path.exists(path):
            if process_file(path):
                count += 1
    print(f"\n📊 Total: {count} files updated")

if __name__ == '__main__':
    main()
