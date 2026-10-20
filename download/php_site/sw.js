// ============================================================
// sw.js — Service Worker برای PWA
// ============================================================
const CACHE_NAME = 'kashani-platform-v3';
const ASSETS = [
  '/', '/index.php', '/factor.php', '/lessons.php', '/magazine.php',
  '/chat.php', '/scientists.php', '/network.php', '/download.php',
  '/manifest.json',
];

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(ASSETS).catch(_ => {})));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.pathname.startsWith('/api') || url.pathname.startsWith('/admin') || url.pathname.startsWith('/auth')) return;
  if (e.request.mode === 'navigate') {
    e.respondWith(fetch(e.request).then(r => { const c = r.clone(); caches.open(CACHE_NAME).then(c => c.put(e.request, c)); return r; }).catch(() => caches.match(e.request).then(r => r || caches.match('/'))));
    return;
  }
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});

self.addEventListener('push', e => {
  const data = e.data ? e.data.json() : {};
  e.waitUntil(self.registration.showNotification(data.title || '🎓 پلتفرم علمی', {
    body: data.body || 'پیام جدید', icon: '/icon-192.png', tag: data.tag || 'kashani',
  }));
});
