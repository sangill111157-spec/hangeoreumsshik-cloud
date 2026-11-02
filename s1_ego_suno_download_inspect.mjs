const task = await takeOverTaskSpace(17);
const page = task.page("p2");

// Re-open menu first if closed
await page.evaluate(async () => {
  const moreBtns = Array.from(document.querySelectorAll('button[aria-label="More options"]'));
  if (moreBtns.length > 0) moreBtns[0].click();
  await new Promise(r => setTimeout(r, 400));
});

const info = await page.evaluate(async () => {
  // Find all elements containing text Download
  const candidates = Array.from(document.querySelectorAll('*')).filter(el => {
    return el.innerText && el.innerText.trim().startsWith('Download') && el.innerText.trim().length < 30;
  });

  return candidates.map(c => ({
    tagName: c.tagName,
    text: c.innerText.trim(),
    role: c.getAttribute('role'),
    className: c.className,
    parentTag: c.parentElement ? c.parentElement.tagName : '',
    parentRole: c.parentElement ? c.parentElement.getAttribute('role') : '',
    parentClass: c.parentElement ? c.parentElement.className : '',
    dataset: Object.assign({}, c.dataset),
    parentDataset: c.parentElement ? Object.assign({}, c.parentElement.dataset) : {}
  }));
});

console.log("Download Candidates:", JSON.stringify(info, null, 2));

