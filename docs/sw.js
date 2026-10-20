// SHIN service worker: v5 cache reset worker (build v5-20261020154003)
const BUILD = 'v5-20261020154003';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map((k) => caches.delete(k)));
    await self.clients.claim();
    const clients = await self.clients.matchAll({ type: 'window' });
    clients.forEach((c) => c.postMessage({ type: 'SHIN_SW_RESET', build: BUILD }));
  })());
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (req.headers.has('range')) return;
  if (url.pathname.includes('/ingredients_basket/')) return;
  if (/\.(mp4|webm|mp3|wav|m4a|ogg|jpg|jpeg|png|webp|gif|json)$/i.test(url.pathname)) return;
  if (req.mode === 'navigate' || /\.html?$/i.test(url.pathname)) {
    event.respondWith(fetch(req, { cache: 'no-store' }).catch(() => caches.match(req)));
  }
});
