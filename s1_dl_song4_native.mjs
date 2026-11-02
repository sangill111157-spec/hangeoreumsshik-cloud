import fs from 'node:fs/promises';

const task = await takeOverTaskSpace(17);
const page = task.page("p2");

const songId = "3a056c44-93bf-4d49-8396-23db04e71fcb";
const songUrl = `https://suno.com/song/${songId}`;

console.log(`Navigating to ${songUrl}...`);
await page.goto(songUrl, { waitUntil: 'load', timeout: 30000 });
await new Promise(r => setTimeout(r, 2500));

// Open menu
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
  if (moreBtns.length > 0) {
    moreBtns[0].id = "suno-more-options-btn";
  }
});

await page.click("#suno-more-options-btn");
await new Promise(r => setTimeout(r, 600));

// Mark Download item in menu
await page.evaluate(() => {
  const menuItems = Array.from(document.querySelectorAll('[role="menuitem"]'));
  const dlItem = menuItems.find(el => el.innerText && el.innerText.trim() === 'Download');
  if (dlItem) {
    dlItem.id = "suno-menu-dl-item";
  }
});

await page.click("#suno-menu-dl-item");
await new Promise(r => setTimeout(r, 1000));

// Arm download listener
console.log("Setting up download promise...");
const downloadPromise = page.waitForEvent("download", { timeout: 35000 });

// Mark MP3 button and Download button in dialog
await page.evaluate(() => {
  const dialog = document.querySelector('[role="dialog"]');
  if (!dialog) return;
  const buttons = Array.from(dialog.querySelectorAll('button'));
  const mp3Btn = buttons.find(b => b.innerText && b.innerText.trim() === 'MP3');
  if (mp3Btn) mp3Btn.id = "suno-dialog-mp3-btn";
  const dlBtn = buttons.find(b => b.innerText && b.innerText.trim() === 'Download');
  if (dlBtn) dlBtn.id = "suno-dialog-dl-btn";
});

// Click MP3 if needed
try {
  await page.click("#suno-dialog-mp3-btn");
  await new Promise(r => setTimeout(r, 400));
} catch (e) {
  console.log("MP3 button already active or skipped:", e.message);
}

// Click Download button natively
console.log("Clicking Download button natively...");
await page.click("#suno-dialog-dl-btn");

console.log("Waiting for download event...");
const download = await downloadPromise;

const targetPath = "C:/Users/sangi/Downloads/shin-agent/studio_vault/CEO_SUNO_V6_ORIGINALS/04_OFFICIAL_THEME_INST_2_suno_original.mp3";
console.log("DOWNLOAD EVENT RECEIVED!", {
  url: download.url(),
  suggestedFilename: download.suggestedFilename()
});

await download.saveAs(targetPath);
console.log("Saved Song 4 to:", targetPath);

// Cover image fetch
const coverUrl = `https://cdn2.suno.ai/image_${songId}.jpeg`;
const coverPath = "C:/Users/sangi/Downloads/shin-agent/studio_vault/CEO_SUNO_V6_ORIGINALS/04_OFFICIAL_THEME_INST_2_cover.jpeg";
try {
  await page.fetch(coverUrl, { saveAs: coverPath });
  console.log("Cover saved:", coverPath);
} catch (e) {
  console.log("Cover note:", e.message);
}

