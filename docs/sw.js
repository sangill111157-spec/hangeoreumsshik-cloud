
/* rgon-ad-studio-v4 / 20261019233728410014: online-only cache reset worker */
const RGON_VERSION = "rgon-ad-studio-v4";
const RGON_BUILD = "20261019233728410014";

self.addEventListener("install", event => {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const names = await caches.keys();

    await Promise.allSettled(
      names.map(name => caches.delete(name))
    );

    await self.clients.claim();

    const windows = await self.clients.matchAll({
      type: "window",
      includeUncontrolled: true
    });

    await self.registration.unregister();

    await Promise.allSettled(windows.map(async client => {
      const url = new URL(client.url);

      if (url.origin !== self.location.origin) return;
      if (!url.pathname.endsWith("/rgon_alpha_chat.html")) return;
      if (url.searchParams.get("__rgon_ad_build") === RGON_BUILD) return;

      url.searchParams.set("__rgon_ad", RGON_VERSION);
      url.searchParams.set("__rgon_ad_build", RGON_BUILD);
      await client.navigate(url.href);
    }));
  })());
});
