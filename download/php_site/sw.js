// ============================================================
// sw.js — Service Worker برای PWA (نسخه‌ی پیشرفته)
// ============================================================
const CACHE_NAME = 'kashani-platform-v4';
const STATIC_CACHE = 'kashani-static-v4';
const RUNTIME_CACHE = 'kashani-runtime-v4';

const STATIC_ASSETS = [
  '/',
  '/index.php',
  '/factor.php',
  '/lessons.php',
  '/magazine.php',
  '/scientists.php',
  '/network.php',
  '/download.php',
  '/manifest.json',
  'https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css',
  'https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css',
];

// Install: pre-cache static assets
self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(STATIC_CACHE).then(c => c.addAll(STATIC_ASSETS).catch(err => {
      console.log('Cache partial fail:', err);
    }))
  );
});

// Activate: clean old caches
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(k => ![STATIC_CACHE, RUNTIME_CACHE].includes(k))
             .map(k => caches.delete(k))
      );
    })
  );
  self.clients.claim();
});

// Fetch strategy: network-first for navigation, cache-first for static, runtime cache for API
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  
  // Skip API and admin (must always be fresh)
  if (url.pathname.startsWith('/api') || url.pathname.startsWith('/admin') ||
      url.pathname.startsWith('/auth') || url.pathname.startsWith('/ai')) {
    return;
  }
  
  // Navigation (HTML): network-first with cache fallback
  if (e.request.mode === 'navigate') {
    e.respondWith(
      fetch(e.request)
        .then(response => {
          // Cache a copy
          const clone = response.clone();
          caches.open(RUNTIME_CACHE).then(c => c.put(e.request, clone));
          return response;
        })
        .catch(() => {
          // Fallback to cache, then to home
          return caches.match(e.request).then(r => r || caches.match('/'));
        })
    );
    return;
  }
  
  // Static assets from CDN: cache-first
  if (url.hostname !== location.hostname) {
    e.respondWith(
      caches.match(e.request).then(cached => {
        return cached || fetch(e.request).then(resp => {
          if (resp.status === 200) {
            const clone = resp.clone();
            caches.open(RUNTIME_CACHE).then(c => c.put(e.request, clone));
          }
          return resp;
        });
      })
    );
    return;
  }
  
  // Same-origin static assets: stale-while-revalidate
  e.respondWith(
    caches.match(e.request).then(cached => {
      const fetchPromise = fetch(e.request).then(resp => {
        if (resp.status === 200) {
          const clone = resp.clone();
          caches.open(RUNTIME_CACHE).then(c => c.put(e.request, clone));
        }
        return resp;
      }).catch(() => cached);
      return cached || fetchPromise;
    })
  );
});

// Push notifications
self.addEventListener('push', e => {
  const data = e.data ? e.data.json() : {};
  e.waitUntil(
    self.registration.showNotification(data.title || '🎓 پلتفرم علمی پارسی', {
      body: data.body || 'پیام جدیدی دارید',
      icon: '/icon-192.png',
      badge: '/icon-192.png',
      tag: data.tag || 'kashani',
      data: { url: data.url || '/' },
      vibrate: [100, 50, 100],
    })
  );
});

// Notification click
self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(
    clients.openWindow(e.notification.data.url || '/')
  );
});

// Background sync (offline support)
self.addEventListener('sync', e => {
  if (e.tag === 'sync-factor-submits') {
    e.waitUntil(syncFactorSubmits());
  }
});

async function syncFactorSubmits() {
  // TODO: send queued factor submissions when back online
  console.log('[SW] Syncing queued submissions...');
}

// Periodic sync (Chrome only)
self.addEventListener('periodicsync', e => {
  if (e.tag === 'check-for-work') {
    e.waitUntil(checkForWork());
  }
});

async function checkForWork() {
  // Check for new work in background
  console.log('[SW] Checking for new work...');
}
