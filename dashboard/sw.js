// sw.js — clean_ui.py 재생성 (버전 20261019205433)
const VERSION = "rgon-20261019205433";
const LOCAL = /^(127\.0\.0\.1|localhost)$/.test(self.location.hostname);
self.addEventListener("install", e => { self.skipWaiting(); });
self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map(k => caches.delete(k)));
    if (LOCAL) { await self.registration.unregister(); return; }
    await self.clients.claim();
  })());
});
