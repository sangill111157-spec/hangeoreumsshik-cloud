# -*- coding: utf-8 -*-
import sys
import json
import s1_ego

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

js = s1_ego.EGO_PRELUDE_JS + """
let currentTask = null;
try {
  const task = await getTask(17);
  currentTask = task;
  const tabs = await task.tabs();
  const page = tabs[0].page;
  
  const details = await page.evaluate(() => {
    const fileInputs = Array.from(document.querySelectorAll('input[type="file"]')).map((el, idx) => {
      let p = el.parentElement;
      let text = '';
      for (let i = 0; i < 5 && p; i++) {
        text += ' ' + (p.innerText || '');
        p = p.parentElement;
      }
      return {
        index: idx,
        id: el.id,
        accept: el.accept,
        parentText: text.slice(0, 300).replace(/\\s+/g, ' ')
      };
    });
    
    const textareas = Array.from(document.querySelectorAll('textarea, [contenteditable="true"]')).map(el => ({
      tag: el.tagName,
      id: el.id,
      placeholder: el.placeholder || el.getAttribute('aria-label') || '',
      value: (el.value || el.innerText || '').slice(0, 100)
    }));
    
    return { fileInputs, textareas };
  });
  
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({ ok: true, details }) + '\\n');
} catch (e) {
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({ ok: false, err: String(e.message || e) }) + '\\n');
} finally {
  await safeHandOff(currentTask);
}
"""

res = s1_ego.run_ego_js(js, timeout=30)
print(json.dumps(res, ensure_ascii=False, indent=2))
