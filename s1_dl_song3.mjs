import fs from 'node:fs/promises';

const task = await takeOverTaskSpace(17);
const page = task.page("p2");

const songId = "6edfa20f-da7c-466e-b9bb-07554f2358d5";
const songUrl = `https://suno.com/song/${songId}`;

console.log(`Navigating to ${songUrl}...`);
await page.goto(songUrl, { waitUntil: 'load', timeout: 30000 });
await new Promise(r => setTimeout(r, 2500));

// Open menu and click Download
console.log("Opening Download modal...");
await page.evaluate(async () => {
  const existingDialog = document.querySelector('[role="dialog"]');
  if (existingDialog) {
    const closeBtn = existingDialog.querySelector('button[aria-label="Close"]');
    if (closeBtn) {
      closeBtn.click();
      await new Promise(r => setTimeout(r, 400));
    }
  }

  const moreBtns = Array.from(document.querySelectorAll('button[aria-label="More options"]'));
  if (moreBtns.length > 0) moreBtns[0].click();
  await new Promise(r => setTimeout(r, 500));

  const dlItem = Array.from(document.querySelectorAll('[role="menuitem"]')).find(
    el => el.innerText && el.innerText.trim() === 'Download'
  );
  if (dlItem) dlItem.click();
  await new Promise(r => setTimeout(r, 800));
});

console.log("Arming download event listener...");
const downloadPromise = page.waitForEvent("download", { timeout: 45000 });

// Click MP3 then Download
await page.evaluate(async () => {
  const dialog = document.querySelector('[role="dialog"]');
  if (!dialog) return;
  const buttons = Array.from(dialog.querySelectorAll('button'));
  const mp3Btn = buttons.find(b => b.innerText && b.innerText.trim() === 'MP3');
  if (mp3Btn) mp3Btn.click();
  await new Promise(r => setTimeout(r, 400));

  const dlBtn = buttons.find(b => b.innerText && b.innerText.trim() === 'Download');
  if (dlBtn) dlBtn.click();
});

console.log("Waiting for download event...");
const download = await downloadPromise;

const targetPath = "C:/Users/sangi/Downloads/shin-agent/studio_vault/CEO_SUNO_V6_ORIGINALS/03_OFFICIAL_THEME_INST_1_suno_original.mp3";
console.log("Download event received!", {
  url: download.url(),
  suggestedFilename: download.suggestedFilename()
});

await download.saveAs(targetPath);
console.log("Successfully saved Song 3 to:", targetPath);

// Cover fetch
const coverUrl = `https://cdn2.suno.ai/image_${songId}.jpeg`;
const coverPath = "C:/Users/sangi/Downloads/shin-agent/studio_vault/CEO_SUNO_V6_ORIGINALS/03_OFFICIAL_THEME_INST_1_cover.jpeg";
try {
  await page.fetch(coverUrl, { saveAs: coverPath });
  console.log("Cover saved:", coverPath);
} catch (e) {
  console.log("Cover note:", e.message);
}

