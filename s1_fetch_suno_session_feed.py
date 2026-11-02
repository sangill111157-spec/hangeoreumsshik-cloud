# -*- coding: utf-8 -*-
import sys
import json
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
    if (u.includes('suno.com')) { page = t.page; break; }
  }
  if (!page) page = tabs[0].page;

  const feedData = await page.evaluate(async () => {
    try {
      // Extract __session cookie
      const getCookie = (name) => {
        const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
        return v ? v[2] : null;
      };
      const token = getCookie('__session');
      if (!token) return { error: "No __session cookie found" };

      // Query feed v2 pages 0 to 4
      const allClips = [];
      for (let p = 0; p < 6; p++) {
        const url = `https://studio-api.prod.suno.com/api/feed/v2?page=${p}`;
        const res = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (res.ok) {
          const json = await res.json();
          const clips = json.clips || [];
          if (clips.length === 0) break;
          for (const c of clips) {
            allClips.push({
              id: c.id,
              title: c.title,
              audio_url: c.audio_url,
              image_url: c.image_url,
              image_large_url: c.image_large_url,
              duration: c.metadata?.duration || 0,
              prompt: c.metadata?.prompt || '',
              tags: c.metadata?.tags || '',
              model_name: c.model_name,
              created_at: c.created_at
            });
          }
        } else {
          return { error: `HTTP ${res.status} on page ${p}` };
        }
      }

      return { ok: true, totalClips: allClips.length, clips: allClips };
    } catch (e) {
      return { error: e.message };
    }
  });

  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify(feedData) + '\\n');
} catch (e) {
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({ ok: false, err: String(e.message || e) }) + '\\n');
} finally {
  await safeHandOff(currentTask);
}
"""

res = s1_ego.run_ego_js(js, timeout=45)
print(json.dumps(res, ensure_ascii=False, indent=2))

