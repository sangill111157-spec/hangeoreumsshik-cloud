import sys
import json
import s1_ego

js = """
let task;
try { task = await takeOverTaskSpace(18); } catch(e) { task = await claimTaskSpace(18); }
try {
  const tabs = await task.tabs();
  let page;
  try { page = task.page('p1'); } catch(e) { page = await task.adopt(tabs[0].page, { as: 'p1' }); }

  const sections = await page.evaluate(() => {
    // 1. Profile Picture section
    const picSection = document.querySelector('ytcp-profile-image-upload')?.closest('section, div[class*="section"]') || document.querySelector('#profile-image-section');
    const picText = picSection ? picSection.innerText.replace(/\\n/g, ' ') : 'NOT_FOUND';

    // 2. Banner section
    const banSection = document.querySelector('ytcp-banner-upload-instructions')?.closest('section, div[class*="section"]') || document.querySelector('#banner-section');
    const banText = banSection ? banSection.innerText.replace(/\\n/g, ' ') : 'NOT_FOUND';

    // 3. Watermark section
    const wmSection = document.querySelector('ytcp-video-watermark-upload')?.closest('section, div[class*="section"]') || document.querySelector('#watermark-section');
    const wmText = wmSection ? wmSection.innerText.replace(/\\n/g, ' ') : 'NOT_FOUND';

    return {
      profile_section: picText,
      banner_section: banText,
      watermark_section: wmText
    };
  });

  process.stdout.write("SECTION_DETAILS::" + JSON.stringify(sections, null, 2) + "\\n");
} finally {
  await task.handOff();
}
"""

ret = s1_ego.run_ego_js(js)
print(ret.get("stdout"))
print(ret.get("stderr"))

