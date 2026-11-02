const task = await takeOverTaskSpace(17);
const page = task.page("p2");

const res = await page.evaluate(async () => {
  // Find menuitem with text "Download"
  const allElements = Array.from(document.querySelectorAll('*'));
  const downloadEl = allElements.find(el => {
    return el.children.length === 0 && el.innerText && el.innerText.trim() === 'Download';
  }) || allElements.find(el => el.innerText && el.innerText.trim() === 'Download');

  if (!downloadEl) {
    return { error: "Download element not found" };
  }

  // Inspect the element
  const tag = downloadEl.tagName;
  const role = downloadEl.getAttribute('role');
  const parent = downloadEl.parentElement;

  // Let's trigger mouseenter or click on downloadEl
  downloadEl.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
  downloadEl.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
  downloadEl.click();

  await new Promise(r => setTimeout(r, 600));

  // Check new elements appeared
  const popperTexts = Array.from(document.querySelectorAll('[data-radix-popper-content-wrapper] *, [role="menu"] *, [role="menuitem"]')).map(el => ({
    tag: el.tagName,
    text: el.innerText ? el.innerText.trim().replace(/\n+/g, ' ') : '',
    role: el.getAttribute('role') || '',
    ariaLabel: el.getAttribute('aria-label') || ''
  })).filter(el => el.text.length > 0 && el.text.length < 50);

  return {
    downloadEl: { tag, role, parentTag: parent ? parent.tagName : '' },
    popperTexts: popperTexts.slice(0, 30)
  };
});

console.log("Download result:", JSON.stringify(res, null, 2));

