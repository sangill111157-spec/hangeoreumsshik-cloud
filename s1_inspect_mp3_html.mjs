const task = await takeOverTaskSpace(17);
const page = task.page("p2");

const html = await page.evaluate(() => {
  const dialog = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal');
  if (!dialog) return "No dialog";
  const buttons = Array.from(dialog.querySelectorAll('button'));
  const mp3 = buttons.find(b => b.innerText.includes('MP3'));
  return {
    mp3OuterHTML: mp3 ? mp3.outerHTML : null,
    wavOuterHTML: buttons.find(b => b.innerText.includes('WAV'))?.outerHTML,
    allButtonsCount: buttons.length,
    rect: mp3 ? mp3.getBoundingClientRect() : null
  };
});

console.log("MP3 button details:", JSON.stringify(html, null, 2));

