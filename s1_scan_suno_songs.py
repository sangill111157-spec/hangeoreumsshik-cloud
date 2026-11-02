# -*- coding: utf-8 -*-
import sys
import json
import pathlib
import s1_ego

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

screenshot_path = pathlib.Path("studio_vault/CHANNELS/04_US_SUNONE_AON/suno_songs_scan.png").resolve().as_posix()

js = s1_ego.EGO_PRELUDE_JS + f"""
let currentTask = null;
try {{
  const task = await getTask(17);
  currentTask = task;
  const tabs = await task.tabs();
  
  // Find suno tab
  let page = null;
  for (const t of tabs) {{
    const u = (typeof t.url === 'string') ? t.url : (t.url ? t.url.href : '');
    if (u.includes('suno.com')) {{
      page = t.page;
      break;
    }}
  }}
  if (!page) page = tabs[0].page;

  // Scan current page (/me)
  const songsMe = await page.evaluate(() => {{
    const songLinks = Array.from(document.querySelectorAll('a[href*="/song/"]')).map(a => ({{
      title: a.innerText.trim(),
      href: a.href,
      songId: a.href.split('/song/')[1]?.split('?')[0] || ''
    }}));
    
    // Also scan row elements
    const rows = Array.from(document.querySelectorAll('[data-testid*="song"], tr, [role="row"], li')).map(r => {{
      const text = (r.innerText || '').slice(0, 300);
      const link = r.querySelector('a[href*="/song/"]');
      const audio = r.querySelector('audio');
      const img = r.querySelector('img');
      return {{
        text: text.replace(/\\s+/g, ' '),
        link: link ? link.href : '',
        audioSrc: audio ? audio.src : '',
        imgSrc: img ? img.src : ''
      }};
    }}).filter(x => x.text && (x.text.includes('SUN') || x.text.includes('희망') || x.text.includes('썬원') || x.text.includes('Official')));

    return {{ songLinks, matchedRows: rows }};
  }});

  // Now also check /create
  console.log("Navigating to https://suno.com/create to scan recent generations...");
  await page.goto("https://suno.com/create", {{ waitUntil: "domcontentloaded", timeout: 45000 }});
  await page.waitForTimeout(6000);

  await page.screenshot({{ path: {json.dumps(screenshot_path)} }});

  const songsCreate = await page.evaluate(() => {{
    const songLinks = Array.from(document.querySelectorAll('a[href*="/song/"]')).map(a => ({{
      title: a.innerText.trim(),
      href: a.href,
      songId: a.href.split('/song/')[1]?.split('?')[0] || ''
    }}));

    // Scan all text blocks or cards on create page
    const cards = Array.from(document.querySelectorAll('div, tr, li')).map(el => {{
      const t = (el.innerText || '').trim();
      const link = el.querySelector('a[href*="/song/"]');
      const audio = el.querySelector('audio');
      const img = el.querySelector('img');
      return {{
        text: t.slice(0, 300).replace(/\\s+/g, ' '),
        href: link ? link.href : '',
        audioSrc: audio ? audio.src : '',
        imgSrc: img ? img.src : ''
      }};
    }}).filter(x => x.text && (x.text.includes('희망의 등불') || x.text.includes('희망의 바다') || x.text.includes('SUN-ONE AON Official Theme') || x.text.includes('썬원 에이온')));

    // Unique by text
    const uniqueCards = [];
    const seen = new Set();
    for (const c of cards) {{
      const k = c.text.slice(0, 60);
      if (!seen.has(k)) {{
        seen.add(k);
        uniqueCards.push(c);
      }}
    }}

    return {{ songLinks, uniqueCards }};
  }});

  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{
    ok: true,
    songsMe,
    songsCreate
  }}) + '\\n');
}} catch (e) {{
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, err: String(e.message || e) }}) + '\\n');
}} finally {{
  await safeHandOff(currentTask);
}}
"""

res = s1_ego.run_ego_js(js, timeout=90)
print(json.dumps(res, ensure_ascii=False, indent=2))

