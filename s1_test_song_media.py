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

  console.log("Navigating to song page: https://suno.com/song/{song_id}...");
  await page.goto("https://suno.com/song/{song_id}", {{ waitUntil: "networkidle", timeout: 45000 }});
  await page.waitForTimeout(3000);

  // Check audio elements, video elements, or links
  const mediaInfo = await page.evaluate(() => {{
    const audios = Array.from(document.querySelectorAll('audio')).map(a => a.src);
    const sources = Array.from(document.querySelectorAll('source')).map(s => s.src);
    const links = Array.from(document.querySelectorAll('a')).map(a => ({{ text: a.innerText.trim(), href: a.href }})).filter(x => x.href.includes('audio') || x.href.includes('mp3') || x.href.includes('wav') || x.href.includes('download'));
    
    // Also check Next.js build / React state
    let nextAudio = null;
    try {{
      if (window.__NEXT_DATA__) {{
        const str = JSON.stringify(window.__NEXT_DATA__);
        const matches = str.match(/https?:[^"']+\\.(mp3|wav|ogg|m4a)/gi);
        nextAudio = matches;
      }}
    }} catch (_) {{}}

    return {{ audios, sources, links, nextAudio, title: document.title }};
  }});

  // Click play button to trigger audio stream loading
  console.log("Looking for play button...");
  const playClicked = await page.evaluate(() => {{
    const playBtn = document.querySelector('[aria-label*="Play"], button[aria-label*="play"], [data-testid*="play"]');
    if (playBtn) {{
      playBtn.click();
      return true;
    }}
    return false;
  }});

  await page.waitForTimeout(3000);

  // Check audio element again after play
  const afterPlayAudio = await page.evaluate(() => {{
    return Array.from(document.querySelectorAll('audio')).map(a => a.src);
  }});

  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{
    ok: true,
    mediaInfo,
    playClicked,
    afterPlayAudio
  }}) + '\\n');
}} catch (e) {{
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, err: String(e.message || e) }}) + '\\n');
}} finally {{
  await safeHandOff(currentTask);
}}
"""

res = s1_ego.run_ego_js(js, timeout=60)
print(json.dumps(res, ensure_ascii=False, indent=2))

