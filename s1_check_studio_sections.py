# -*- coding: utf-8 -*-
import sys
import json
import s1_ego

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

js = """
let task;
try { task = await takeOverTaskSpace(18); } catch(e) { task = await claimTaskSpace(18); }
try {
  const tabs = await task.tabs();
  let page;
  try { page = task.page('p1'); } catch(e) { page = await task.adopt(tabs[0].page, { as: 'p1' }); }

  // Full page screenshot of Studio
  const studioScreenshot = "studio_vault/CHANNELS/04_US_SUNONE_AON/live_studio_reloaded_verified.png";
  await page.screenshot({ path: "C:/Users/sangi/Downloads/shin-agent/" + studioScreenshot, fullPage: true });

  const sectionsData = await page.evaluate(() => {
    // Check all sections in Studio editing/profile
    const allText = document.body.innerText;
    
    // Find Banner container
    const bImg = document.querySelector('img[id*="banner"], ytcp-banner-upload-instructions img, div.banner-image img, #banner-section img');
    // Find Avatar container
    const aImg = document.querySelector('ytcp-profile-image-upload img, #profile-image-section img, img[id*="avatar"], img[id*="profile"]');
    // Find Watermark container
    const wImg = document.querySelector('ytcp-video-watermark-upload img, #watermark-section img');

    const btns = Array.from(document.querySelectorAll('button, ytcp-button')).map(b => ({
      text: (b.innerText || '').trim(),
      id: b.id,
      disabled: b.disabled || b.hasAttribute('disabled')
    })).filter(b => /변경|Change|삭제|Remove|업로드|Upload|게시|Publish/.test(b.text));

    return {
      bannerImg: bImg ? { src: bImg.src.slice(0, 100), w: bImg.naturalWidth, h: bImg.naturalHeight } : null,
      avatarImg: aImg ? { src: aImg.src.slice(0, 100), w: aImg.naturalWidth, h: aImg.naturalHeight } : null,
      watermarkImg: wImg ? { src: wImg.src.slice(0, 100), w: wImg.naturalWidth, h: wImg.naturalHeight } : null,
      buttons: btns
    };
  });

  process.stdout.write("STUDIO_SECTIONS_DATA::" + JSON.stringify(sectionsData, null, 2) + "\\n");

  // Also navigate to public channel to verify public view
  console.log("Navigating to public channel to verify...");
  await page.goto("https://www.youtube.com/@SUN-ONEAON", { waitUntil: "networkidle", timeout: 35000 });
  await page.waitForTimeout(4000);

  const publicScreenshot = "studio_vault/CHANNELS/04_US_SUNONE_AON/live_public_channel_masterpiece.png";
  await page.screenshot({ path: "C:/Users/sangi/Downloads/shin-agent/" + publicScreenshot, fullPage: false });

  // Navigate back to studio
  console.log("Returning to YouTube Studio...");
  await page.goto("https://studio.youtube.com/channel/UC4C_H80jcXzKV8ldAtmYMog/editing/profile", { waitUntil: "networkidle", timeout: 35000 });
  await page.waitForTimeout(3000);

  process.stdout.write("PUBLIC_VERIFICATION_COMPLETE\\n");

} finally {
  await task.handOff();
}
"""

ret = s1_ego.run_ego_js(js)
print(ret.get("stdout"))
print(ret.get("stderr"))

