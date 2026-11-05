// S1 Service Worker v2026-v049 (SUN-ONE AON Zero-Paste & Network-First HTML)
const CACHE = 's1-aon-v052-kakao-5tabs';
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
          console.log('[SW-048] Nuking old cache:', k);
          return caches.delete(k);
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url);

  // 1) HTML 페이지 및 내비게이션 요청: 무조건 Network-First (구버전 캐시 즉시 차단!)
  const isHtml = e.request.mode === 'navigate' ||
                 u.pathname.endsWith('.html') ||
                 u.pathname.endsWith('/') ||
                 u.pathname === '';

  if (isHtml || u.pathname.startsWith('/api/') || u.pathname.endsWith('.json') || u.pathname.endsWith('.mp4')) {
    e.respondWith(
      fetch(e.request, { cache: 'no-store' })
        .then(response => {
          if (response && response.status === 200 && isHtml) {
            const clone = response.clone();
            caches.open(CACHE).then(cache => cache.put(e.request, clone));
          }
          return response;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }

  // 2) 정적 이미지 / 아이콘 등 정적 자산: Stale-while-revalidate
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
