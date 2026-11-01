# -*- coding: utf-8 -*-
import sys
import json
import pathlib
import s1_ego

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

screenshot_path = pathlib.Path("studio_vault/CHANNELS/04_US_SUNONE_AON/live_channel_before.png").resolve().as_posix()

js = s1_ego.EGO_PRELUDE_JS + f"""
let currentTask = null;
try {{
  const task = await getTask(17);
  currentTask = task;
  const tabs = await task.tabs();
  const page = tabs[0].page;
  const currentUrl = page.url();
  const currentTitle = await page.title();
  
  await page.screenshot({{ path: {json.dumps(screenshot_path)} }});
  
  const accountInfo = await page.evaluate(() => {{
    return {{
      bodyText: document.body.innerText.slice(0, 1500),
      links: Array.from(document.querySelectorAll('a')).map(a => ({{ text: a.innerText.trim(), href: a.href }})).filter(x => x.text || x.href.includes('studio') || x.href.includes('channel'))
    }};
  }});
  
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{
    ok: true,
    url: currentUrl,
    title: currentTitle,
    links: accountInfo.links.slice(0, 20),
    bodySnippet: accountInfo.bodyText.slice(0, 500)
  }}) + '\\n');
}} catch (e) {{
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, err: String(e.message || e) }}) + '\\n');
}} finally {{
  await safeHandOff(currentTask);
}}
"""

res = s1_ego.run_ego_js(js, timeout=30)
print(json.dumps(res, ensure_ascii=False, indent=2))
