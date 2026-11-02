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

  // Take screenshot
  await page.screenshot({ path: "C:/Users/sangi/Downloads/shin-agent/studio_debug_avatar_modal.png" });
  console.log("Screenshot saved to studio_debug_avatar_modal.png");

  // Inspect all visible dialogs, buttons, and text
  const state = await page.evaluate(() => {
    const dialogs = Array.from(document.querySelectorAll('ytcp-dialog, [role="dialog"], tp-yt-paper-dialog, ytcp-profile-image-upload-dialog')).map(d => ({
      tag: d.tagName,
      id: d.id,
      className: d.className,
      visible: d.offsetParent !== null,
      text: (d.innerText || '').slice(0, 200).replace(/\n/g, ' ')
    }));

    const btns = Array.from(document.querySelectorAll('button, ytcp-button, [role="button"]')).map(b => ({
      id: b.id,
      text: (b.innerText || '').trim().replace(/\n/g, ' '),
      visible: b.offsetParent !== null,
      disabled: b.disabled || b.hasAttribute('disabled')
    })).filter(b => b.visible && b.text.length > 0);

    return { dialogs, btns, url: location.href };
  });

  console.log("DEBUG STATE:", JSON.stringify(state, null, 2));

} finally {
  await task.handOff();
}

