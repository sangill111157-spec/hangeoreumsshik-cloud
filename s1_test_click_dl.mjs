const task = await takeOverTaskSpace(17);
const page = task.page("p2");

console.log("Setting up download promise...");
const downloadPromise = page.waitForEvent("download", { timeout: 30000 });

console.log("Clicking Download button with page.click...");
// Button 6 is inside dialog: 'button.hxc-btn-variant-primary' or selector
const clicked = await page.evaluate(() => {
  const dialog = document.querySelector('[role="dialog"]');
  if (!dialog) return { error: "no dialog" };
  const buttons = Array.from(dialog.querySelectorAll('button'));
  const dlBtn = buttons.find(b => b.innerText && b.innerText.trim() === 'Download');
  if (dlBtn) {
    dlBtn.id = "suno-dl-btn-target";
    return { found: true };
  }
  return { found: false };
});

console.log("Marked button:", clicked);
await page.click("#suno-dl-btn-target");
console.log("Clicked! Waiting for download event...");

try {
  const download = await downloadPromise;
  console.log("DOWNLOAD EVENT RECEIVED!", {
    url: download.url(),
    suggestedFilename: download.suggestedFilename()
  });
  const savePath = "C:/Users/sangi/Downloads/shin-agent/studio_vault/CEO_SUNO_V6_ORIGINALS/02_OCEAN_OF_HOPE_suno_original.mp3";
  await download.saveAs(savePath);
  console.log("Saved to:", savePath);
} catch (e) {
  console.log("Download event wait error:", e.message);
  
  // Inspect dialog text again to see if status changed
  const state = await page.evaluate(() => {
    const dialog = document.querySelector('[role="dialog"]');
    return dialog ? dialog.innerText.replace(/\n+/g, ' | ') : 'none';
  });
  console.log("Dialog state after click:", state);
}

