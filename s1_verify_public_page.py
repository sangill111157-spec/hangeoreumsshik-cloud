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

  const data = await page.evaluate(() => {
    return {
      title: document.title,
      url: window.location.href,
      handle: (document.querySelector('#channel-handle, yt-formatted-string#channel-handle') || {}).innerText || '',
      channelHeader: (document.querySelector('yt-page-header-renderer, #channel-header') || {}).innerText || '',
      avatarSrc: (document.querySelector('yt-avatar-shape img, #channel-header img') || {}).src || '',
      bannerSrc: (document.querySelector('#banner img, ytd-channel-banner-renderer img') || {}).src || '',
      aboutSnippet: document.body.innerText.slice(0, 1000)
    };
  });

  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({ ok: true, data }) + '\\n');
} catch (e) {
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({ ok: false, err: String(e.message || e) }) + '\\n');
} finally {
  await safeHandOff(currentTask);
}
"""

res = s1_ego.run_ego_js(js, timeout=30)
print(json.dumps(res, ensure_ascii=False, indent=2))
