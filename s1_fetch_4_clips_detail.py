# -*- coding: utf-8 -*-
import sys
import json
import urllib.request
import pathlib
import s1_ego

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

song_ids = [
    "73ba5c00-7d00-43c3-b3c4-28ae873ac59a", # 희망의 등불
    "e32fa822-6672-4392-aafc-c9760fc7b406", # 희망의 바다
    "6edfa20f-da7c-466e-b9bb-07554f2358d5", # Official Theme #1
    "3a056c44-93bf-4d49-8396-23db04e71fcb"  # Official Theme #2
]

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

  const clipDetails = await page.evaluate(async (ids) => {{
    const getCookie = (name) => {{
      const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
      return v ? v[2] : null;
    }};
    const token = getCookie('__session');
    const headers = token ? {{ 'Authorization': `Bearer ${{token}}` }} : {{}};

    const results = [];
    for (const sid of ids) {{
      const u = `https://studio-api.prod.suno.com/api/clip/${{sid}}`;
      try {{
        const r = await fetch(u, {{ headers }});
        if (r.ok) {{
          const data = await r.json();
          results.push(data);
        }} else {{
          results.push({{ id: sid, error: `HTTP ${{r.status}}` }});
        }}
      }} catch (e) {{
        results.push({{ id: sid, error: e.message }});
      }}
    }}
    return results;
  }}, {json.dumps(song_ids)});

  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: true, clipDetails }}) + '\\n');
}} catch (e) {{
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, err: String(e.message || e) }}) + '\\n');
}} finally {{
  await safeHandOff(currentTask);
}}
"""

res = s1_ego.run_ego_js(js, timeout=45)
print(json.dumps(res, ensure_ascii=False, indent=2))

