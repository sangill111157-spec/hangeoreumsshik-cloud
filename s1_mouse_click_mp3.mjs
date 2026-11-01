const task = await takeOverTaskSpace(17);
const page = task.page("p2");

const pos = await page.evaluate(() => {
  const btn = document.querySelector('#target-mp3-button-v2') || Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('MP3'));
  if (!btn) return null;
  const r = btn.getBoundingClientRect();
  return {
    x: r.x + r.width / 2,
    y: r.y + r.height / 2,
    w: r.width,
    h: r.height,
    visible: r.width > 0 && r.height > 0
  };
});

console.log("MP3 Button Pos:", pos);

if (pos && pos.visible) {
  console.log(`Clicking MP3 with native mouse at (${pos.x}, ${pos.y})...`);
  await page.mouse.click(pos.x, pos.y);
  await new Promise(r => setTimeout(r, 600));

  const after = await page.evaluate(() => {
    const dialog = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal');
    const buttons = Array.from(dialog.querySelectorAll('button'));
    const dl = buttons.find(b => b.innerText.trim() === 'Download');
    const mp3 = buttons.find(b => b.innerText.includes('MP3'));
    return {
      dlDisabled: dl ? dl.disabled : null,
      mp3Classes: mp3 ? mp3.className : ''
    };
  });
  console.log("After native mouse click:", after);

  if (after.dlDisabled === false) {
    console.log("ENABLED! Clicking Download now...");
    const dlPos = await page.evaluate(() => {
      const dialog = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal');
      const buttons = Array.from(dialog.querySelectorAll('button'));
      const dl = buttons.find(b => b.innerText.trim() === 'Download');
      const r = dl.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    });

    const downloadPromise = page.waitForEvent("download", { timeout: 35000 });
    await page.mouse.click(dlPos.x, dlPos.y);

    const download = await downloadPromise;
    const targetPath = "C:/Users/sangi/Downloads/shin-agent/studio_vault/CEO_SUNO_V6_ORIGINALS/04_OFFICIAL_THEME_INST_2_suno_original.mp3";
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
  }
}

