const task = await takeOverTaskSpace(17);
const page = task.page("p2");

console.log("Finding and clicking MP3 button on Song 4...");

for (let attempt = 1; attempt <= 5; attempt++) {
  console.log(`Attempt ${attempt}: Clicking MP3...`);
  
  await page.evaluate(() => {
    const dialog = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal');
    if (!dialog) return;
    const buttons = Array.from(dialog.querySelectorAll('button'));
    const mp3 = buttons.find(b => b.innerText.includes('MP3'));
    if (mp3) {
      mp3.id = "target-mp3-button-v2";
      // Also trigger click directly in DOM
      mp3.click();
    }
  });

  try {
    await page.click("#target-mp3-button-v2");
  } catch (e) {
    console.log("page.click notice:", e.message);
  }

  await new Promise(r => setTimeout(r, 1000));

  const status = await page.evaluate(() => {
    const dialog = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal');
    if (!dialog) return { found: false };
    const buttons = Array.from(dialog.querySelectorAll('button'));
    const dl = buttons.find(b => b.innerText.trim() === 'Download');
    const mp3 = buttons.find(b => b.innerText.includes('MP3'));
    return {
      found: true,
      dlDisabled: dl ? dl.disabled : null,
      mp3Classes: mp3 ? mp3.className : ''
    };
  });

  console.log("Status after attempt:", status);
  if (status.dlDisabled === false) {
    console.log("Download button is ENABLED!");
    break;
  }
}

// Now Download
console.log("Arming download event listener...");
const downloadPromise = page.waitForEvent("download", { timeout: 35000 });

await page.evaluate(() => {
  const dialog = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal');
  const buttons = Array.from(dialog.querySelectorAll('button'));
  const dl = buttons.find(b => b.innerText.trim() === 'Download');
  if (dl) dl.id = "target-dl-button-v2";
});

console.log("Clicking Download button...");
await page.click("#target-dl-button-v2");

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
const songId = "3a056c44-93bf-4d49-8396-23db04e71fcb";
const coverUrl = `https://cdn2.suno.ai/image_${songId}.jpeg`;
const coverPath = "C:/Users/sangi/Downloads/shin-agent/studio_vault/CEO_SUNO_V6_ORIGINALS/04_OFFICIAL_THEME_INST_2_cover.jpeg";
try {
  await page.fetch(coverUrl, { saveAs: coverPath });
  console.log("Cover saved:", coverPath);
} catch (e) {
  console.log("Cover note:", e.message);
}
console.log("Song 4 completely done!");

