# -*- coding: utf-8 -*-
import sys
import json
import pathlib
import s1_ego

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

song_id = "73ba5c00-7d00-43c3-b3c4-28ae873ac59a"

js = s1_ego.EGO_PRELUDE_JS + f"""
let currentTask = null;
try {{
  const task = await getTask(17);
  currentTask = task;
  const tabs = await task.tabs();
  let page = null;
  for (const t of tabs) {{
    const u = (typeof t.url === 'string') ? t.url : (t.url ? t.url.href : '');
    if (u.includes('suno.com')) {{ page = t.page; break; }}
  }}
  if (!page) page = tabs[0].page;

  console.log("Navigating to song page with domcontentloaded...");
  await page.goto("https://suno.com/song/{song_id}", {{ waitUntil: "domcontentloaded", timeout: 30000 }});
  await page.waitForTimeout(3000);

  // Probe API endpoints for this clip using __session token
  const apiProbe = await page.evaluate(async (sid) => {{
    const getCookie = (name) => {{
      const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
      return v ? v[2] : null;
    }};
    const token = getCookie('__session');
    const headers = token ? {{ 'Authorization': `Bearer ${{token}}` }} : {{}};

    const urls = [
      `https://studio-api.prod.suno.com/api/clip/${{sid}}`,
      `https://studio-api.prod.suno.com/api/clips/${{sid}}`,
      `https://studio-api.prod.suno.com/api/song/${{sid}}`,
      `https://studio-api.prod.suno.com/api/songs/${{sid}}`,
      `https://studio-api.prod.suno.com/api/feed/v2?ids=${{sid}}`,
      `https://studio-api.prod.suno.com/api/feed/?ids=${{sid}}`
    ];

    const res = {{}};
    for (const u of urls) {{
      try {{
        const r = await fetch(u, {{ headers }});
        res[u] = {{ status: r.status }};
        if (r.ok) {{
          const data = await r.json();
          res[u].data = data;
        }}
      }} catch (e) {{
        res[u] = {{ error: e.message }};
      }}
    }}
    return res;
  }}, {json.dumps(song_id)});

  // Inspect DOM buttons
  const buttons = await page.evaluate(() => {{
    return Array.from(document.querySelectorAll('button, [role="button"], a')).map(b => ({{
      text: (b.innerText || b.getAttribute('aria-label') || '').trim(),
      tag: b.tagName,
      id: b.id,
      className: b.className.slice(0, 50)
    }})).filter(x => x.text);
  }});

  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{
    ok: true,
    apiProbe,
    buttons: buttons.slice(0, 30)
  }}) + '\\n');
}} catch (e) {{
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, err: String(e.message || e) }}) + '\\n');
}} finally {{
  await safeHandOff(currentTask);
}}
"""

res = s1_ego.run_ego_js(js, timeout=45)
print(json.dumps(res, ensure_ascii=False, indent=2))

