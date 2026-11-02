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
download_dir = pathlib.Path("studio_vault/CEO_SUNO_V6_ORIGINALS").resolve().as_posix()

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

  // Set download behavior in CDP
  console.log("Setting CDP download behavior to:", {json.dumps(download_dir)});
  await page.cdp('Page.setDownloadBehavior', {{
    behavior: 'allow',
    downloadPath: {json.dumps(download_dir)}
  }});

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

  // Click Download menuitem
  await page.evaluate(() => {{
    const items = Array.from(document.querySelectorAll('div, button'));
    const dl = items.find(el => el.innerText.trim() === 'Download');
    if (dl) dl.click();
  }});
  await page.waitForTimeout(1500);

  // In the modal, select WAV or MP3 and click Download
  const modalClickResult = await page.evaluate(() => {{
    const btns = Array.from(document.querySelectorAll('button, div[role="radio"], [role="button"], label'));
    // Find MP3 or WAV button
    const mp3Btn = btns.find(b => b.innerText.trim() === 'MP3' || b.innerText.trim() === 'WAV');
    if (mp3Btn) {{
      mp3Btn.click();
    }}
    // Find the final Download action button inside the modal
    const dlActionBtn = Array.from(document.querySelectorAll('button')).find(b => {{
      const text = b.innerText.trim();
      return text === 'Download' && !b.disabled;
    }});
    if (dlActionBtn) {{
      dlActionBtn.click();
      return {{ mp3Clicked: !!mp3Btn, dlClicked: true }};
    }}
    return {{ mp3Clicked: !!mp3Btn, dlClicked: false }};
  }});

  console.log("Modal click result:", modalClickResult);
  // Wait 10 seconds for download to complete
  await page.waitForTimeout(10000);

  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{
    ok: true,
    modalClickResult
  }}) + '\\n');
}} catch (e) {{
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, err: String(e.message || e) }}) + '\\n');
}} finally {{
  await safeHandOff(currentTask);
}}
"""

res = s1_ego.run_ego_js(js, timeout=60)
print(json.dumps(res, ensure_ascii=False, indent=2))

