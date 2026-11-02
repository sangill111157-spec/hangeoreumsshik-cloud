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
  let task;
  try {
    task = await takeOverTaskSpace(18);
  } catch (e) {
    task = await claimTaskSpace(18);
  }
  currentTask = task;
  const tabs = await task.tabs();
  const page = tabs[0].page;

  const info = await page.evaluate(() => {
    // 1. All input[type=file]
    const fileInputs = Array.from(document.querySelectorAll('input[type="file"]')).map((fi, idx) => ({
      index: idx,
      id: fi.id,
      name: fi.name,
      accept: fi.accept,
      className: fi.className,
      parentElement: fi.parentElement ? fi.parentElement.tagName + '.' + fi.parentElement.className : ''
    }));

    // 2. Buttons matching upload, change, remove, publish
    const allBtns = Array.from(document.querySelectorAll('button, tp-yt-paper-button, ytcp-button, [role="button"]'));
    const btns = allBtns.map((b, idx) => ({
      index: idx,
      tag: b.tagName,
      id: b.id,
      text: (b.innerText || b.getAttribute('aria-label') || '').trim().replace(/\\n/g, ' '),
      disabled: b.disabled || b.hasAttribute('disabled')
    })).filter(b => b.text && /업로드|변경|삭제|게시|취소|Upload|Change|Remove|Publish|Cancel/i.test(b.text));

    // 3. Sections
    const sections = Array.from(document.querySelectorAll('.section, section, [id*="section"], [class*="section"]')).map(s => ({
      id: s.id,
      className: s.className,
      textPreview: (s.innerText || '').slice(0, 60).replace(/\\n/g, ' ')
    }));

    // 4. Description
    const tb = document.querySelector('div#textbox');
    const descLen = tb ? tb.innerText.length : -1;

    return {
      url: location.href,
      fileInputs,
      btns,
      sectionsCount: sections.length,
      descLength: descLen
    };
  });

  console.log("=== STUDIO PROBE RESULT ===");
  console.log(JSON.stringify(info, null, 2));
} catch (e) {
  console.error("Probe error:", e);
} finally {
  await safeHandOff(currentTask);
}
"""

ret = s1_ego.run_ego_js(js)
print(ret.get("stdout"))
print(ret.get("stderr"))

