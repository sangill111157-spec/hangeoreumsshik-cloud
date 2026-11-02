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

  // Track network requests
  const requests = [];
  const responses = [];

  // Enable CDP Network
  await page.cdp('Network.enable');

  console.log("Navigating to https://suno.com/song/{song_id}...");
  await page.goto("https://suno.com/song/{song_id}", {{ waitUntil: "domcontentloaded", timeout: 30000 }});
  await page.waitForTimeout(3000);

  // Click More options
  await page.evaluate(() => {{
    const btns = Array.from(document.querySelectorAll('button'));
    const moreBtn = btns.find(b => (b.innerText || b.getAttribute('aria-label') || '').includes('More options'));
    if (moreBtn) moreBtn.click();
  }});
  await page.waitForTimeout(1000);

  // Click Download
  console.log("Clicking Download and observing network...");
  await page.evaluate(() => {{
    const items = Array.from(document.querySelectorAll('div, button'));
    const dl = items.find(el => el.innerText.trim() === 'Download');
    if (dl) dl.click();
  }});

  await page.waitForTimeout(1500);

  // Inspect any new modal or popover that opened
  const popovers = await page.evaluate(() => {{
    return Array.from(document.querySelectorAll('[role="dialog"], [data-radix-popper-content-wrapper], [role="menu"]')).map(el => ({{
      text: el.innerText.slice(0, 500).replace(/\\s+/g, ' '),
      buttons: Array.from(el.querySelectorAll('button, a')).map(b => ({{ text: b.innerText.trim(), href: b.href || '' }}))
    }}));
  }});

  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{
    ok: true,
    popovers
  }}) + '\\n');
}} catch (e) {{
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, err: String(e.message || e) }}) + '\\n');
}} finally {{{{
  await safeHandOff(currentTask);
}}}}
"""

res = s1_ego.run_ego_js(js, timeout=45)
print(json.dumps(res, ensure_ascii=False, indent=2))

