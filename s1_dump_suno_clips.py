# -*- coding: utf-8 -*-
import sys
import json
import pathlib
import s1_ego

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT_DIR = pathlib.Path(__file__).resolve().parent
SAVE_DIR = ROOT_DIR / "studio_vault" / "CEO_SUNO_V6_ORIGINALS"
SAVE_DIR.mkdir(parents=True, exist_ok=True)
SAVE_JSON = (SAVE_DIR / "suno_clips_raw.json").resolve().as_posix()

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

  const feedData = await page.evaluate(async () => {{
    const getCookie = (name) => {{
      const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
      return v ? v[2] : null;
    }};
    const token = getCookie('__session');
    if (!token) return {{ error: "No __session cookie found" }};

    const allClips = [];
    for (let p = 0; p < 8; p++) {{
      const url = `https://studio-api.prod.suno.com/api/feed/v2?page=${{p}}`;
      const res = await fetch(url, {{
        headers: {{ 'Authorization': `Bearer ${{token}}` }}
      }});
      if (res.ok) {{
        const json = await res.json();
        const clips = json.clips || [];
        if (clips.length === 0) break;
        for (const c of clips) {{
          allClips.push(c);
        }}
      }} else {{
        break;
      }}
    }}
    return {{ ok: true, totalClips: allClips.length, clips: allClips }};
  }});

  // Write file via node fs
  const fs = await import('node:fs');
  fs.writeFileSync({json.dumps(SAVE_JSON)}, JSON.stringify(feedData, null, 2), 'utf8');

  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: true, count: feedData.totalClips, path: {json.dumps(SAVE_JSON)} }}) + '\\n');
}} catch (e) {{
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, err: String(e.message || e) }}) + '\\n');
}} finally {{
  await safeHandOff(currentTask);
}}
"""

res = s1_ego.run_ego_js(js, timeout=45)
print(json.dumps(res, ensure_ascii=False, indent=2))

