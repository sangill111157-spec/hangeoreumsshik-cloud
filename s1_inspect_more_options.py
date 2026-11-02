# -*- coding: utf-8 -*-
import sys
import json
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

  console.log("Navigating to https://suno.com/song/{song_id}...");
  await page.goto("https://suno.com/song/{song_id}", {{ waitUntil: "domcontentloaded", timeout: 30000 }});
  await page.waitForTimeout(3000);

  // Click 'More options' button
  console.log("Clicking More options...");
  const moreClicked = await page.evaluate(() => {{
    const btns = Array.from(document.querySelectorAll('button'));
    const moreBtn = btns.find(b => (b.innerText || b.getAttribute('aria-label') || '').includes('More options'));
    if (moreBtn) {{
      moreBtn.click();
      return true;
    }}
    return false;
  }});

  await page.waitForTimeout(1500);

  // Inspect menu items
  const menuItems = await page.evaluate(() => {{
    return Array.from(document.querySelectorAll('[role="menuitem"], [role="menu"] button, [role="menu"] a, [class*="menu"] button, [class*="menu"] a, [data-radix-collection-item]')).map(el => ({{
      text: el.innerText.trim(),
      tag: el.tagName,
      href: el.href || ''
    }}));
  }});

  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{
    ok: true,
    moreClicked,
    menuItems
  }}) + '\\n');
}} catch (e) {{
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, err: String(e.message || e) }}) + '\\n');
}} finally {{
  await safeHandOff(currentTask);
}}
"""

res = s1_ego.run_ego_js(js, timeout=45)
print(json.dumps(res, ensure_ascii=False, indent=2))

