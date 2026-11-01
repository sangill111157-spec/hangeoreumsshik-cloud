import path from 'node:path';

const task = await takeOverTaskSpace(17);
const page = task.page("p2");

console.log("Starting Suno download test for Song 1...");

// Check current dialog or open it
const res = await page.evaluate(async () => {
  const dialog = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal, [aria-modal="true"]');
  if (!dialog) {
    // Open menu
    const moreBtns = Array.from(document.querySelectorAll('button[aria-label="More options"]'));
    if (moreBtns.length > 0) moreBtns[0].click();
    await new Promise(r => setTimeout(r, 400));
    
    // Find Download menu item
    const dlItem = Array.from(document.querySelectorAll('[role="menuitem"]')).find(el => el.innerText && el.innerText.trim() === 'Download');
    if (dlItem) dlItem.click();
    await new Promise(r => setTimeout(r, 600));
  }

  // Find WAV button in dialog
  const dialogNow = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal, [aria-modal="true"]');
  if (!dialogNow) return { error: "No dialog found" };

  const buttons = Array.from(dialogNow.querySelectorAll('button'));
  const wavBtn = buttons.find(b => b.innerText && b.innerText.trim() === 'WAV');
  const mp3Btn = buttons.find(b => b.innerText && b.innerText.trim() === 'MP3');
  const dlBtn = buttons.find(b => b.innerText && b.innerText.trim() === 'Download');

  return {
    hasWav: !!wavBtn,
    hasMp3: !!mp3Btn,
    hasDl: !!dlBtn
  };
});

console.log("Evaluation check:", res);

// Now let's arm waitForEvent('download')
console.log("Arming download event listener...");
const downloadPromise = page.waitForEvent("download", { timeout: 30000 });

// Select WAV button in dialog, then click Download
await page.evaluate(() => {
  const dialog = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal, [aria-modal="true"]');
  const buttons = Array.from(dialog.querySelectorAll('button'));
  const wavBtn = buttons.find(b => b.innerText && b.innerText.trim() === 'WAV');
  if (wavBtn) wavBtn.click();
});

await new Promise(r => setTimeout(r, 500));

// Click Download button
await page.evaluate(() => {
  const dialog = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal, [aria-modal="true"]');
  const buttons = Array.from(dialog.querySelectorAll('button'));
  const dlBtn = buttons.find(b => b.innerText && b.innerText.trim() === 'Download');
  if (dlBtn) dlBtn.click();
});

console.log("Waiting for download event...");
const download = await downloadPromise;

const targetPath = "C:/Users/sangi/Downloads/shin-agent/studio_vault/CEO_SUNO_V6_ORIGINALS/01_BEACON_OF_HOPE_suno_original.wav";
console.log("Download event received!", {
  url: download.url(),
  suggestedFilename: download.suggestedFilename()
});

await download.saveAs(targetPath);
console.log("Successfully saved download to:", targetPath);

