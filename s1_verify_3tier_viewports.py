import os, sys, json, subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent
MJS_PATH = BASE / "_ego_tmp" / "test_viewports.mjs"
MJS_PATH.parent.mkdir(exist_ok=True)

mjs_code = """
import fs from 'node:fs';

(async () => {
  let task;
  try {
    task = await taskSpace("s1_viewport_test");
  } catch (e) {
    task = await takeOverTaskSpace("s1_viewport_test");
  }

  const results = [];
  try {
    const page = await task.newPage();
    const viewports = [
      { name: "desktop_1440", width: 1440, height: 900, mobile: false },
      { name: "tablet_768", width: 768, height: 1024, mobile: false },
      { name: "mobile_390", width: 390, height: 844, mobile: true }
    ];

    for (const vp of viewports) {
      await page.cdp("Emulation.setDeviceMetricsOverride", {
        width: vp.width,
        height: vp.height,
        deviceScaleFactor: 2,
        mobile: vp.mobile
      });

      await page.goto("http://127.0.0.1:8504/index.html");
      await page.waitForTimeout(600);

      const check = await page.evaluate(() => {
        const docWidth = document.documentElement.clientWidth;
        const scrollWidth = document.documentElement.scrollWidth;
        const bodyScrollWidth = document.body.scrollWidth;
        const hasHOverflow = scrollWidth > docWidth || bodyScrollWidth > docWidth;
        const anatomy = document.getElementById("anatomy-panel");
        const hasAnatomy = !!anatomy;
        const marble = document.querySelector(".marble-bead");
        const hasMarble = !!marble;

        return {
          viewportWidth: window.innerWidth,
          clientWidth: docWidth,
          scrollWidth: scrollWidth,
          bodyScrollWidth: bodyScrollWidth,
          horizontalOverflow: hasHOverflow,
          hasAnatomyPanel: hasAnatomy,
          hasMarbleAnimation: hasMarble
        };
      });

      results.push({
        viewport: vp,
        check: check,
        status: (!check.horizontalOverflow && check.hasAnatomyPanel && check.hasMarbleAnimation) ? "PASS" : "FAIL"
      });
    }

    // Reset emulation and close page
    await page.cdp("Emulation.clearDeviceMetricsOverride", {});
    await page.close();
    await task.finish({ keep: [] });
    process.stdout.write(JSON.stringify({ ok: true, results: results }));
  } catch (err) {
    process.stdout.write(JSON.stringify({ ok: false, error: err.message }));
  } finally {
    try { await task.handOff(); } catch(e) {}
  }
})();
"""

MJS_PATH.write_text(mjs_code, encoding="utf-8")
file_url = MJS_PATH.as_uri()

res = subprocess.run(
    ["ego-browser", "nodejs", "-e", f"await import('{file_url}')"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    timeout=35
)

combined = (res.stdout + "\n" + res.stderr).strip()

data = None
for line in combined.splitlines():
    line = line.strip()
    if line.startswith("{") and line.endswith("}"):
        try:
            data = json.loads(line)
            break
        except Exception:
            pass

if data:
    print(json.dumps(data, ensure_ascii=False, indent=2))
    # Write proof to file
    with open("S1_3TIER_VIEWPORTS_VERIFICATION_PROOF.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[SUCCESS] Successfully saved S1_3TIER_VIEWPORTS_VERIFICATION_PROOF.json")
else:
    print("RAW OUTPUT:", combined)

