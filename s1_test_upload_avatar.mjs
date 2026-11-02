let task;
try {
  task = await takeOverTaskSpace(18);
} catch (e) {
  task = await claimTaskSpace(18);
}

try {
  const tabs = await task.tabs();
  let page;
  try {
    page = task.page("p1");
  } catch (e) {
    page = await task.adopt(tabs[0].page, { as: "p1" });
  }

  const avatarPath = "C:/Users/sangi/Downloads/shin-agent/avatar_800x800.png";
  console.log("Setting input file on fileInputs[1] (Avatar):", avatarPath);

  const fileInputs = await page.$$('input[type="file"]');
  console.log("Found file inputs count:", fileInputs.length);

  if (fileInputs.length >= 2) {
    await fileInputs[1].setInputFiles(avatarPath);
    console.log("setInputFiles called on fileInputs[1]!");

    // Wait 2 seconds for dialog
    await page.waitForTimeout(2000);

    // Check if dialog or done-button is visible
    const dialogInfo = await page.evaluate(() => {
      const dialogs = Array.from(document.querySelectorAll('ytcp-dialog, ytcp-profile-image-upload-dialog, [role="dialog"], tp-yt-paper-dialog'));
      const doneBtns = Array.from(document.querySelectorAll('#done-button, button, ytcp-button')).filter(b => {
        const t = (b.innerText || '').trim();
        return b.id === 'done-button' || /완료|Done/i.test(t);
      }).map(b => ({
        id: b.id,
        text: (b.innerText || '').trim(),
        disabled: b.disabled || b.hasAttribute('disabled'),
        visible: b.offsetParent !== null
      }));

      return {
        dialogsCount: dialogs.length,
        dialogTags: dialogs.map(d => d.tagName),
        doneBtns
      };
    });

    console.log("Dialog info after avatar setInputFiles:", JSON.stringify(dialogInfo, null, 2));

    // If done-button exists and visible, click it!
    const doneBtn = await page.$('#done-button:not([disabled])');
    if (doneBtn) {
      console.log("Clicking #done-button...");
      await doneBtn.click();
      await page.waitForTimeout(2000);
      console.log("#done-button clicked!");
    } else {
      console.log("#done-button not ready or not found");
    }
  }

} catch (e) {
  console.error("Upload test error:", e);
} finally {
  await task.handOff();
}

