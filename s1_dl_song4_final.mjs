import fs from 'node:fs/promises';

const task = await takeOverTaskSpace(17);
const page = task.page("p2");

const songId = "3a056c44-93bf-4d49-8396-23db04e71fcb";
const songUrl = `https://suno.com/song/${songId}`;

console.log(`Navigating to ${songUrl}...`);
await page.goto(songUrl, { waitUntil: 'load', timeout: 30000 });
await new Promise(r => setTimeout(r, 2500));

// Close any open dialog and click More options
console.log("Opening More options menu...");
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

// Click Download in menu
await page.evaluate(() => {
  const menuItems = Array.from(document.querySelectorAll('[role="menuitem"]'));
  const dlItem = menuItems.find(el => el.innerText && el.innerText.trim() === 'Download');
  if (dlItem) dlItem.id = "suno-menu-dl-item";
});

await page.click("#suno-menu-dl-item");
await new Promise(r => setTimeout(r, 1000));

// Mark MP3 button in dialog
await page.evaluate(() => {
  const dialog = document.querySelector('[role="dialog"]');
  if (!dialog) return;
  const buttons = Array.from(dialog.querySelectorAll('button'));
  const mp3 = buttons.find(b => b.innerText.trim() === 'MP3');
  if (mp3) mp3.id = "target-mp3-button";
});

// Click MP3 button natively
console.log("Clicking MP3 button...");
await page.click("#target-mp3-button");
await new Promise(r => setTimeout(r, 600));

// Mark Download button in dialog
const dlState = await page.evaluate(() => {
  const dialog = document.querySelector('[role="dialog"]');
  if (!dialog) return { found: false };
  const buttons = Array.from(dialog.querySelectorAll('button'));
  const dl = buttons.find(b => b.innerText.trim() === 'Download');
  if (dl) {
    dl.id = "target-dl-button";
    return { found: true, disabled: dl.disabled };
  }
  return { found: false };
});

console.log("Download button state:", dlState);

if (!dlState.disabled) {
  console.log("Arming download event listener...");
  const downloadPromise = page.waitForEvent("download", { timeout: 35000 });

  console.log("Clicking Download button natively...");
  await page.click("#target-dl-button");

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
}

// Hand off Space 17 safely
console.log("Handing off Space 17 back to user...");
await task.handOff();
console.log("All done!");

