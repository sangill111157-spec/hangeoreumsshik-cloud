# -*- coding: utf-8 -*-
import sys
import json
import pathlib
import s1_ego

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

screenshot_path = pathlib.Path("studio_vault/CHANNELS/04_US_SUNONE_AON/suno_initial_check.png").resolve().as_posix()

js = s1_ego.EGO_PRELUDE_JS + f"""
let currentTask = null;
try {{
  const task = await getTask(17);
  currentTask = task;
  
  console.log("Checking existing tabs in space 17...");
  const tabs = await task.tabs();
  let page = null;
  
  // Check if a suno tab already exists
  for (const t of tabs) {{
    const u = (typeof t.url === 'string') ? t.url : (t.url ? t.url.href : '');
    if (u.includes('suno.com')) {{
      page = t.page;
      console.log("Found existing suno tab!");
      break;
    }}
  }}
  
  if (!page) {{
    console.log("Creating new tab or navigating to suno.com/me...");
    try {{
      page = await task.newPage();
    }} catch (e) {{
      console.log("newPage not supported or failed, using tabs[0].page:", e.message);
      page = tabs[0].page;
    }}
  }}
  
  console.log("Navigating to https://suno.com/me...");
  await page.goto("https://suno.com/me", {{ waitUntil: "domcontentloaded", timeout: 45000 }});
  await page.waitForTimeout(5000);
  
  const currentUrl = (typeof page.url === 'function') ? page.url() : String(page.url || '');
  const title = await page.title();
  
  await page.screenshot({{ path: {json.dumps(screenshot_path)} }});
  
  const bodySnippet = await page.evaluate(() => {{
    return {{
      url: window.location.href,
      title: document.title,
      text: document.body.innerText.slice(0, 1500),
      buttons: Array.from(document.querySelectorAll('button, a')).map(b => (b.innerText || '').trim()).filter(x => x.length > 0 && x.length < 50).slice(0, 30)
    }};
  }});
  
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{
    ok: true,
    currentUrl,
    title,
    bodySnippet
  }}) + '\\n');
}} catch (e) {{
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, err: String(e.message || e) }}) + '\\n');
}} finally {{
  await safeHandOff(currentTask);
}}
"""

res = s1_ego.run_ego_js(js, timeout=60)
print(json.dumps(res, ensure_ascii=False, indent=2))

