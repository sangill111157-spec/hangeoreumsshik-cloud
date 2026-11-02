// S1 Service Worker v2026-zeropaste-v7 (SUN-ONE AON Zero-Paste & Dual Bridge)
const CACHE = 's1-v2026-deliverable-review-v10-clean';
const ASSETS = [
  './',
  './index.html',
  './rgon_alpha_chat.html',
  './manifest.webmanifest',
  './manifest.json',
  './icon-192.png?v=2026s1max',
  './icon-512.png?v=2026s1max',
  './icon-512-maskable.png?v=2026s1max',
  './apple-touch-icon.png?v=2026s1max',
  './favicon.ico',
  './icon-192.png',
  './icon-512.png',
  './icon-512-maskable.png',
  './apple-touch-icon.png'
];

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE).then(cache => {
      return cache.addAll(ASSETS).catch(err => console.warn('Cache addAll warning:', err));
    })
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(k => k !== CACHE).map(k => {
          console.log('[SW] Deleting old cache:', k);
          return caches.delete(k);
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url);

  // Network-first for dynamic API / live JSON
  if (u.pathname.startsWith('/api/') || u.pathname.endsWith('.json')) {
    e.respondWith(
      fetch(e.request, { cache: 'no-store' }).catch(() => caches.match(e.request))
    );
    return;
  }

  // Stale-while-revalidate for html and assets
  e.respondWith(
    caches.match(e.request).then(cached => {
      const networked = fetch(e.request).then(response => {
        if (response && response.status === 200 && response.type === 'basic') {
          const clone = response.clone();
          caches.open(CACHE).then(cache => cache.put(e.request, clone));
        }
        return response;
      }).catch(() => cached);

      return cached || networked;
    })
  );
});
