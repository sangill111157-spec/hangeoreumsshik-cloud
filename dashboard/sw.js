// sw.js - 청와대 AI 중앙 컨트롤타워 서비스 워커 (Claude Opus 5.5 무중단 브릿지)
const CACHE_NAME = 'cheongwadae-pwa-v12.0';
const OFFLINE_URL = '/offline.html';

const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/rgon_alpha_chat.html',
  '/offline.html',
  '/manifest.webmanifest',
  '/pwa_bootstrap.js',
  '/departments/dept_closet.html',
  '/departments/dept_connect_ai.html',
  '/departments/dept_media.html',
  '/tunnel_bridge.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] PWA 캐시 자산 사전 설치 중...');
      return cache.addAll(ASSETS_TO_CACHE).catch((err) => {
        console.warn('[SW] 일부 정적 자산 사전 캐싱 건너뜀:', err);
      });
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[SW] 구버전 캐시 정리:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Network-First 전략 with Offline / Tunnel fallback
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // POST 요청은 캐싱 불가, 네트워크 그대로 수행
  if (request.method !== 'GET') {
    return;
  }

  // API 요청 처리: 네트워크 우선, 실패 시 클라이언트가 tunnel_bridge.json을 통해 자동 재시도하도록 503 반환
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).catch(async (error) => {
        console.warn('[SW] API 요청 실패 (터널 교체 중일 수 있음):', url.pathname);
        return new Response(JSON.stringify({
          error: "TUNNEL_TRANSITION_OR_OFFLINE",
          message: "터널 주소 전환 또는 네트워크 재연결 중입니다. 브릿지 자동 추적 중...",
          status: 503
        }), {
          status: 503,
          headers: { 'Content-Type': 'application/json; charset=utf-8' }
        });
      })
    );
    return;
  }

  // 일반 HTML/JS/CSS 자산: Network First -> Cache Fallback -> Offline Page
  event.respondWith(
    fetch(request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseToCache);
          });
        }
        return networkResponse;
      })
      .catch(async () => {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
          return cachedResponse;
        }
        // HTML 페이지 탐색 요청인 경우 offline.html 반환
        if (request.mode === 'navigate' || (request.headers.get('accept') && request.headers.get('accept').includes('text/html'))) {
          return caches.match(OFFLINE_URL);
        }
        return new Response('Network unavailable', { status: 503, statusText: 'Service Unavailable' });
      })
  );
});
