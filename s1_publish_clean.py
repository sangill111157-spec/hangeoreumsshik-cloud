# -*- coding: utf-8 -*-
import sys
import json
import pathlib
import s1_ego

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT_DIR = pathlib.Path(__file__).resolve().parent
SCREENSHOT_AFTER = (ROOT_DIR / "studio_vault" / "CHANNELS" / "04_US_SUNONE_AON" / "live_branding_published_clean.png").resolve().as_posix()
SCREENSHOT_PUBLIC = (ROOT_DIR / "studio_vault" / "CHANNELS" / "04_US_SUNONE_AON" / "live_channel_public_verified.png").resolve().as_posix()

DESCRIPTION_CLEAN = """Welcome to SUN-ONE AON — Where Sound Awakens the Soul and Value Returns to the World.

Rooted in the timeless Eastern philosophy of "Sangseonyaksu" (上善若水: "The highest excellence is like water, benefiting all without contending"), SUN-ONE AON is a global cinematic music sanctuary founded by Sangill Lee.

🌊 33% Global Philanthropy Pledge:
We believe true creative abundance flows outward. 33% of all streaming royalties and licensing revenues are dedicated directly to global humanitarian initiatives and music education for underprivileged youth.

🎵 Musical Universe:
• World-Class Cinematic Orchestral Anthems
• Mindful Acoustic Melodies & Hanok Heritage Harmony
• Midnight Synthwave & Athletic Motivation Beats
• Healing 432Hz Ambient Soundscapes

✨ Label & Official Distribution:
• Official DistroKid Music Label: SUN-ONE AON Records
• Executive Producer: Sangill Lee (이상일)
• Official Handle: @SUN-ONEAON"""

js = s1_ego.EGO_PRELUDE_JS + f"""
let currentTask = null;
try {{
  const task = await getTask(17);
  currentTask = task;
  const tabs = await task.tabs();
  const page = tabs[0].page;

  console.log("Navigating to editing/profile to set clean description and publish...");
  await page.goto("https://studio.youtube.com/channel/UC4C_H80jcXzKV8ldAtmYMog/editing/profile", {{ waitUntil: "networkidle", timeout: 45000 }});
  await page.waitForTimeout(3000);

  // Set concise description under 1000 chars
  const descClean = {json.dumps(DESCRIPTION_CLEAN)};
  await page.evaluate((val) => {{
    const tb = document.querySelector('div#textbox');
    if (tb) {{
      tb.focus();
      tb.innerText = val;
      tb.dispatchEvent(new Event('input', {{ bubbles: true }}));
      tb.dispatchEvent(new Event('change', {{ bubbles: true }}));
    }}
  }}, descClean);

  await page.waitForTimeout(2000);

  // Check character count text
  const charCount = await page.evaluate(() => {{
    const textboxes = Array.from(document.querySelectorAll('*'));
    const counter = textboxes.find(el => el.innerText && /\\d+\\s*\\/\\s*1000/.test(el.innerText));
    return counter ? counter.innerText.trim() : "";
  }});
  console.log("Character counter text:", charCount);

  // Click '게시 (Publish)'
  const publishClicked = await page.evaluate(() => {{
    const btns = Array.from(document.querySelectorAll('button, tp-yt-paper-button, ytcp-button, [role="button"]'));
    const pubBtn = btns.find(b => {{
      const t = (b.innerText || b.getAttribute('aria-label') || '').trim();
      return t === '게시' || t === 'Publish' || b.id === 'publish-button';
    }});
    if (pubBtn) {{
      pubBtn.click();
      return true;
    }}
    return false;
  }});
  console.log("Publish clicked:", publishClicked);

  await page.waitForTimeout(6000);

  // Toast message
  const toastText = await page.evaluate(() => {{
    const el = document.querySelector('ytcp-toast, #toast, [role="status"]');
    return el ? el.innerText.trim() : "";
  }});
  console.log("Toast after publish:", toastText);

  await page.screenshot({{ path: {json.dumps(SCREENSHOT_AFTER)} }});

  // Navigate to public view
  console.log("Navigating to public view...");
  await page.goto("https://www.youtube.com/@SUN-ONEAON", {{ waitUntil: "networkidle", timeout: 30000 }});
  await page.waitForTimeout(3000);
  await page.screenshot({{ path: {json.dumps(SCREENSHOT_PUBLIC)} }});

  const finalPublicTitle = await page.title();

  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{
    ok: true,
    charCount,
    publishClicked,
    toastText,
    finalPublicTitle
  }}) + '\\n');
}} catch (e) {{
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, err: String(e.message || e) }}) + '\\n');
}} finally {{
  await safeHandOff(currentTask);
}}
"""

res = s1_ego.run_ego_js(js, timeout=90)
print(json.dumps(res, ensure_ascii=False, indent=2))
