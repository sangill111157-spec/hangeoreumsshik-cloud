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

  // Hook fetch and XMLHttpRequest in page context before clicking!
  await page.evaluate(() => {{
    window.__capturedRequests = [];
    const origFetch = window.fetch;
    window.fetch = async (...args) => {{
      const url = String(args[0]);
      window.__capturedRequests.push({{ type: 'fetch', url }});
      const res = await origFetch(...args);
      try {{
        const clone = res.clone();
        const text = await clone.text();
        window.__capturedRequests.push({{ type: 'fetch-response', url, status: res.status, body: text.slice(0, 500) }});
      }} catch (_) {{}}
      return res;
    }};

    const origOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url) {{
      this._url = url;
      window.__capturedRequests.push({{ type: 'xhr', method, url }});
      origOpen.apply(this, arguments);
    }};
  }});

  // Click More options
  await page.evaluate(() => {{
    const btns = Array.from(document.querySelectorAll('button'));
    const moreBtn = btns.find(b => (b.innerText || b.getAttribute('aria-label') || '').includes('More options'));
    if (moreBtn) moreBtn.click();
  }});
  await page.waitForTimeout(1000);

  // Click Download menuitem
  await page.evaluate(() => {{
    const items = Array.from(document.querySelectorAll('div, button'));
    const dl = items.find(el => el.innerText.trim() === 'Download');
    if (dl) dl.click();
  }});
  await page.waitForTimeout(1500);

  // Click MP3 then Download
  await page.evaluate(() => {{
    const btns = Array.from(document.querySelectorAll('button, div[role="radio"], [role="button"], label'));
    const mp3Btn = btns.find(b => b.innerText.trim() === 'MP3');
    if (mp3Btn) mp3Btn.click();
  }});
  await page.waitForTimeout(500);

  await page.evaluate(() => {{
    const dlActionBtn = Array.from(document.querySelectorAll('button')).find(b => {{
      const text = b.innerText.trim();
      return text === 'Download' && !b.disabled;
    }});
    if (dlActionBtn) dlActionBtn.click();
  }});

  await page.waitForTimeout(3000);

  // Retrieve captured requests
  const captured = await page.evaluate(() => window.__capturedRequests || []);

  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{
    ok: true,
    captured
  }}) + '\\n');
}} catch (e) {{
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, err: String(e.message || e) }}) + '\\n');
}} finally {{
  await safeHandOff(currentTask);
}}
"""

res = s1_ego.run_ego_js(js, timeout=45)
print(json.dumps(res, ensure_ascii=False, indent=2))

