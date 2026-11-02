let task;
try {
  task = await takeOverTaskSpace(18);
} catch (e) {
  task = await claimTaskSpace(18);
}

const page = task.page();

const info = await page.evaluate(() => {
  // 1. All input[type=file]
  const fileInputs = Array.from(document.querySelectorAll('input[type="file"]')).map((fi, idx) => ({
    index: idx,
    id: fi.id,
    name: fi.name,
    accept: fi.accept,
    className: fi.className,
    parentTag: fi.parentElement ? fi.parentElement.tagName : '',
    parentClass: fi.parentElement ? fi.parentElement.className : ''
  }));

  // 2. Buttons matching upload, change, remove, publish
  const allBtns = Array.from(document.querySelectorAll('button, tp-yt-paper-button, ytcp-button, [role="button"]'));
  const btns = allBtns.map((b, idx) => ({
    index: idx,
    tag: b.tagName,
    id: b.id,
    text: (b.innerText || b.getAttribute('aria-label') || '').trim().replace(/\n/g, ' '),
    disabled: b.disabled || b.hasAttribute('disabled')
  })).filter(b => b.text && /업로드|변경|삭제|게시|취소|Upload|Change|Remove|Publish|Cancel/i.test(b.text));

  // 3. Description textbox
  const tb = document.querySelector('div#textbox');
  const descText = tb ? tb.innerText : 'NOT FOUND';

  return {
    url: location.href,
    fileInputs,
    btns,
    descLength: descText.length,
    descSnippet: descText.slice(0, 100)
  };
});

console.log("=== PROBE INFO ===");
console.log(JSON.stringify(info, null, 2));

await task.handOff();
