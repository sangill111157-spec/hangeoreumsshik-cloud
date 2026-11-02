# -*- coding: utf-8 -*-
import sys
import json
import time
import s1_ego

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

js = s1_ego.EGO_PRELUDE_JS + """
let currentTask = null;
try {
  const task = await getTask(17);
  currentTask = task;
  const tabs = await task.tabs();
  
  let page = null;
  for (const t of tabs) {
    const u = (typeof t.url === 'string') ? t.url : (t.url ? t.url.href : '');
    if (u.includes('suno.com')) {
      page = t.page;
      break;
    }
  }
  if (!page) page = tabs[0].page;

  console.log("Navigating to https://suno.com/create...");
  await page.goto("https://suno.com/create", { waitUntil: "domcontentloaded", timeout: 45000 });
  await page.waitForTimeout(4000);

  // Scroll down multiple times to load older tracks
  console.log("Scrolling down to load more songs...");
  for (let i = 0; i < 12; i++) {
    await page.evaluate(() => {
      // Find scrollable feed containers or scroll window
      const containers = Array.from(document.querySelectorAll('[data-testid*="feed"], [class*="feed"], [class*="scroll"], [role="feed"], main'));
      for (const c of containers) {
        c.scrollTop += 2000;
      }
      window.scrollBy(0, 2000);
    });
    await page.waitForTimeout(1500);
  }

  // Now extract all songs
  const allSongs = await page.evaluate(() => {
    const songMap = {};
    const links = Array.from(document.querySelectorAll('a[href*="/song/"]'));
    for (const a of links) {
      const href = a.href;
      const songId = href.split('/song/')[1]?.split('?')[0];
      const title = a.innerText.trim();
      if (songId) {
        if (!songMap[songId]) {
          songMap[songId] = { songId, title, href, parentSnippet: '' };
        }
        if (title && !songMap[songId].title) {
          songMap[songId].title = title;
        }
      }
    }

    // Also check all row text and images
    const elements = Array.from(document.querySelectorAll('div, tr, li, [data-testid*="song"]'));
    for (const el of elements) {
      const link = el.querySelector('a[href*="/song/"]');
      if (link) {
        const sid = link.href.split('/song/')[1]?.split('?')[0];
        if (sid && songMap[sid]) {
          const t = (el.innerText || '').slice(0, 250).replace(/\\s+/g, ' ');
          if (t.length > (songMap[sid].parentSnippet || '').length) {
            songMap[sid].parentSnippet = t;
          }
          const img = el.querySelector('img');
          if (img && img.src && !songMap[sid].imgSrc) {
            songMap[sid].imgSrc = img.src;
          }
        }
      }
    }

    return Object.values(songMap);
  });

  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({
    ok: true,
    totalCount: allSongs.length,
    songs: allSongs
  }) + '\\n');
} catch (e) {
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({ ok: false, err: String(e.message || e) }) + '\\n');
} finally {
  await safeHandOff(currentTask);
}
"""

res = s1_ego.run_ego_js(js, timeout=90)
print(json.dumps(res, ensure_ascii=False, indent=2))

