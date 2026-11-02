import fs from 'node:fs/promises';
import path from 'node:path';

const songs = [
  {
    id: "73ba5c00-7d00-43c3-b3c4-28ae873ac59a",
    num: "01",
    tag: "01_BEACON_OF_HOPE",
    title: "썬원 에이온 - 희망의 등불 (SUN-ONE AON)",
    expectedDuration: 158.0
  },
  {
    id: "e32fa822-6672-4392-aafc-c9760fc7b406",
    num: "02",
    tag: "02_OCEAN_OF_HOPE",
    title: "썬원 에이온 - 희망의 바다 (SUN-ONE AON)",
    expectedDuration: 139.8
  },
  {
    id: "6edfa20f-da7c-466e-b9bb-07554f2358d5",
    num: "03",
    tag: "03_OFFICIAL_THEME_INST_1",
    title: "SUN-ONE AON Official Theme (Instrumental) #1",
    expectedDuration: 202.36
  },
  {
    id: "3a056c44-93bf-4d49-8396-23db04e71fcb",
    num: "04",
    tag: "04_OFFICIAL_THEME_INST_2",
    title: "SUN-ONE AON Official Theme (Instrumental) #2",
    expectedDuration: 178.8
  }
];

const targetDir = "C:/Users/sangi/Downloads/shin-agent/studio_vault/CEO_SUNO_V6_ORIGINALS";
await fs.mkdir(targetDir, { recursive: true });

let task = null;
for (let retry = 0; retry < 5; retry++) {
  try {
    task = await takeOverTaskSpace(17);
    break;
  } catch (e) {
    console.log(`takeOverTaskSpace retry ${retry + 1}/5 due to:`, e.message);
    await new Promise(r => setTimeout(r, 2000));
  }
}
if (!task) {
  throw new Error("Failed to take over task space 17 after retries");
}
const page = task.page("p2");

const results = [];

for (const s of songs) {
  console.log(`\n========================================`);
  console.log(`[SONG ${s.num}] Processing: ${s.title} (${s.id})`);
  console.log(`========================================`);

  const songUrl = `https://suno.com/song/${s.id}`;
  console.log(`Navigating to ${songUrl}...`);
  await page.goto(songUrl, { waitUntil: 'load', timeout: 30000 });

  // Wait 3 seconds for UI to render
  await new Promise(r => setTimeout(r, 3000));

  // Step 1: Open More options and click Download
  console.log("Opening Download modal via DOM...");
  const opened = await page.evaluate(async () => {
    // If a dialog is already open, close it or check it
    const existingDialog = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal, [aria-modal="true"]');
    if (existingDialog) {
      const closeBtn = existingDialog.querySelector('button[aria-label="Close"]');
      if (closeBtn) {
        closeBtn.click();
        await new Promise(r => setTimeout(r, 500));
      }
    }

    // Find the More options button for this song (usually button index 16 in toolbar)
    const moreBtns = Array.from(document.querySelectorAll('button[aria-label="More options"]'));
    if (moreBtns.length === 0) return { error: "No More options button found" };

    moreBtns[0].click();
    await new Promise(r => setTimeout(r, 600));

    // Find Download menu item
    const menuItems = Array.from(document.querySelectorAll('[role="menuitem"]'));
    const dlItem = menuItems.find(el => el.innerText && el.innerText.trim() === 'Download');
    if (!dlItem) {
      // Try searching text
      const fallback = Array.from(document.querySelectorAll('*')).find(el => el.innerText && el.innerText.trim() === 'Download' && el.getAttribute('role') === 'menuitem');
      if (fallback) {
        fallback.click();
        await new Promise(r => setTimeout(r, 800));
        return { ok: true, method: 'fallback_menuitem' };
      }
      return { error: "Download menu item not found" };
    }

    dlItem.click();
    await new Promise(r => setTimeout(r, 800));
    return { ok: true, method: 'menuitem' };
  });

  console.log("Modal open result:", opened);

  if (opened.error) {
    console.error(`Failed to open Download modal for ${s.id}:`, opened.error);
    results.push({ ...s, success: false, error: opened.error });
    continue;
  }

  // Step 2: Arm download event
  console.log("Arming download event listener...");
  const downloadPromise = page.waitForEvent("download", { timeout: 45000 });

  // Step 3: Click format button (MP3 or WAV) and Download button
  await page.evaluate(async () => {
    const dialog = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal, [aria-modal="true"]');
    if (!dialog) return;
    const buttons = Array.from(dialog.querySelectorAll('button'));
    // Prefer MP3 for universal compatibility, or WAV
    const mp3Btn = buttons.find(b => b.innerText && b.innerText.trim() === 'MP3');
    if (mp3Btn) mp3Btn.click();
    await new Promise(r => setTimeout(r, 400));

    const dlBtn = buttons.find(b => b.innerText && b.innerText.trim() === 'Download');
    if (dlBtn) dlBtn.click();
  });

  console.log("Waiting for Suno download event...");
  try {
    const download = await downloadPromise;
    const filename = `${s.num}_${s.tag}_suno_original.mp3`;
    const savePath = path.join(targetDir, filename).replace(/\\/g, '/');
    console.log(`Download event received! url=${download.url()}, suggestedFilename=${download.suggestedFilename()}`);
    await download.saveAs(savePath);
    console.log(`Saved to ${savePath}`);

    // Also download cover image if available
    const coverUrl = `https://cdn2.suno.ai/image_${s.id}.jpeg`;
    const coverPath = path.join(targetDir, `${s.num}_${s.tag}_cover.jpeg`).replace(/\\/g, '/');
    try {
      await page.fetch(coverUrl, { saveAs: coverPath });
      console.log(`Cover saved to ${coverPath}`);
    } catch (ce) {
      console.warn(`Cover fetch note: ${ce.message}`);
    }

    results.push({
      ...s,
      success: true,
      audioPath: savePath,
      coverPath,
      suggestedFilename: download.suggestedFilename()
    });
  } catch (err) {
    console.error(`Download failed for ${s.id}:`, err);
    results.push({ ...s, success: false, error: err.message });
  }

  // Small delay between songs
  await new Promise(r => setTimeout(r, 2000));
}

// Hand off space 17 back to user
await task.handOff();

console.log("\n========================================");
console.log("ALL DOWNLOADS COMPLETE SUMMARY:");
console.log(JSON.stringify(results, null, 2));
console.log("========================================");

await fs.writeFile(
  path.join(targetDir, "download_results.json"),
  JSON.stringify(results, null, 2),
  'utf-8'
);
