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
    if (u.includes('suno.com')) {
      page = t.page;
      break;
    }
  }
  if (!page) page = tabs[0].page;

  console.log("Probing Suno internal API from page context...");
  const apiResult = await page.evaluate(async () => {
    const results = {};
    
    // Try common Suno endpoints with user credentials
    const endpoints = [
      '/api/feed/v2?page=0',
      '/api/feed/v2?page=1',
      '/api/feed/?page=0',
      '/api/feed/?page=1',
      'https://studio-api.suno.ai/api/feed/v2?page=0',
      'https://studio-api.suno.ai/api/feed/v2?page=1',
      'https://studio-api.prod.suno.com/api/feed/v2?page=0'
    ];
    
    for (const ep of endpoints) {
      try {
        const r = await fetch(ep, { credentials: 'include' });
        if (r.ok) {
          const data = await r.json();
          results[ep] = {
            status: r.status,
            clips_count: (data.clips || data || []).length,
            clips: (data.clips || data || []).map(c => ({
              id: c.id,
              title: c.title,
              audio_url: c.audio_url,
              image_url: c.image_url,
              image_large_url: c.image_large_url,
              model_name: c.model_name,
              metadata: {
                prompt: (c.metadata?.prompt || '').slice(0, 100),
                tags: c.metadata?.tags || '',
                duration: c.metadata?.duration || 0
              },
              created_at: c.created_at
            }))
          };
        } else {
          results[ep] = { status: r.status };
        }
      } catch (e) {
        results[ep] = { error: e.message };
      }
    }
    
    return results;
  });

  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({
    ok: true,
    apiResult
  }) + '\\n');
} catch (e) {
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({ ok: false, err: String(e.message || e) }) + '\\n');
} finally {
  await safeHandOff(currentTask);
}
"""

res = s1_ego.run_ego_js(js, timeout=45)
print(json.dumps(res, ensure_ascii=False, indent=2))

