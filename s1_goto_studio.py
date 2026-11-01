# -*- coding: utf-8 -*-
import sys
import json
import pathlib
import s1_ego

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

screenshot_path = pathlib.Path("studio_vault/CHANNELS/04_US_SUNONE_AON/live_studio_customization.png").resolve().as_posix()

js = s1_ego.EGO_PRELUDE_JS + f"""
let currentTask = null;
try {{
  const task = await getTask(17);
  currentTask = task;
  const tabs = await task.tabs();
  const page = tabs[0].page;
  
  // Go to customization branding tab directly
  console.log("Navigating to YouTube Studio customization...");
  await page.goto("https://studio.youtube.com/channel/UC4C_H80jcXzKV8ldAtmYMog/editing/profile", {{ waitUntil: "networkidle", timeout: 45000 }});
  
  await page.waitForTimeout(3000);
  const currentUrl = page.url();
  const currentTitle = await page.title();
  
  await page.screenshot({{ path: {json.dumps(screenshot_path)} }});
  
  const pageData = await page.evaluate(() => {{
    return {{
      buttons: Array.from(document.querySelectorAll('button, tp-yt-paper-button, [role="button"]')).map(b => ({{
        text: (b.innerText || b.getAttribute('aria-label') || '').trim(),
        id: b.id || '',
        tag: b.tagName
      }})).filter(x => x.text),
      inputs: Array.from(document.querySelectorAll('input, textarea')).map(i => ({{
        type: i.type,
        id: i.id,
        name: i.name,
        placeholder: i.placeholder || '',
        value: i.value ? i.value.slice(0, 100) : ''
      }})),
      tabs: Array.from(document.querySelectorAll('[role="tab"]')).map(t => t.innerText.trim()),
      bodySnippet: document.body.innerText.slice(0, 1000)
    }};
  }});
  
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{
    ok: true,
    url: currentUrl,
    title: currentTitle,
    tabs: pageData.tabs,
    buttons: pageData.buttons.slice(0, 30),
    inputs: pageData.inputs,
    bodySnippet: pageData.bodySnippet.slice(0, 500)
  }}) + '\\n');
}} catch (e) {{
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, err: String(e.message || e) }}) + '\\n');
}} finally {{
  await safeHandOff(currentTask);
}}
"""

res = s1_ego.run_ego_js(js, timeout=60)
print(json.dumps(res, ensure_ascii=False, indent=2))
