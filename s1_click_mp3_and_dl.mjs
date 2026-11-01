const task = await takeOverTaskSpace(17);
const page = task.page("p2");

console.log("Checking dialog and clicking MP3...");
const before = await page.evaluate(() => {
  const dialog = document.querySelector('[role="dialog"]');
  if (!dialog) return { error: "No dialog" };
  const buttons = Array.from(dialog.querySelectorAll('button'));
  const mp3 = buttons.find(b => b.innerText.trim() === 'MP3');
  if (mp3) {
    mp3.id = "target-mp3-button";
    return { foundMp3: true, id: mp3.id };
  }
  return { foundMp3: false };
});

console.log("Before click:", before);

// Click MP3 button
await page.click("#target-mp3-button");
await new Promise(r => setTimeout(r, 600));

// Check Download button state
const after = await page.evaluate(() => {
  const dialog = document.querySelector('[role="dialog"]');
  const buttons = Array.from(dialog.querySelectorAll('button'));
  const dl = buttons.find(b => b.innerText.trim() === 'Download');
  if (dl) {
    dl.id = "target-dl-button";
    return { foundDl: true, disabled: dl.disabled };
  }
  return { foundDl: false };
});

console.log("After MP3 click:", after);

if (!after.disabled) {
  console.log("Download button is enabled! Arming download promise...");
  const downloadPromise = page.waitForEvent("download", { timeout: 35000 });
  
  await page.click("#target-dl-button");
  console.log("Clicked Download! Waiting for download event...");
  
  const download = await downloadPromise;
  const targetPath = "C:/Users/sangi/Downloads/shin-agent/studio_vault/CEO_SUNO_V6_ORIGINALS/03_OFFICIAL_THEME_INST_1_suno_original.mp3";
  console.log("DOWNLOAD EVENT RECEIVED!", {
    url: download.url(),
    suggestedFilename: download.suggestedFilename()
  });
  await download.saveAs(targetPath);
  console.log("Saved Song 3 to:", targetPath);

  // Cover image fetch
  const songId = "6edfa20f-da7c-466e-b9bb-07554f2358d5";
  const coverUrl = `https://cdn2.suno.ai/image_${songId}.jpeg`;
  const coverPath = "C:/Users/sangi/Downloads/shin-agent/studio_vault/CEO_SUNO_V6_ORIGINALS/03_OFFICIAL_THEME_INST_1_cover.jpeg";
  try {
    await page.fetch(coverUrl, { saveAs: coverPath });
    console.log("Cover saved:", coverPath);
  } catch (e) {
    console.log("Cover note:", e.message);
  }
}

