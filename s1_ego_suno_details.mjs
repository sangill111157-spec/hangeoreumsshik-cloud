const task = await takeOverTaskSpace(17);
const page = task.page("p2");

const details = await page.evaluate(() => {
  const buttons = Array.from(document.querySelectorAll('button')).slice(12, 35).map((b, idx) => ({
    i: idx + 12,
    text: b.innerText ? b.innerText.trim() : '',
    ariaLabel: b.getAttribute('aria-label') || '',
    classes: b.className,
    parentClass: b.parentElement ? b.parentElement.className : ''
  }));
  return buttons;
});

console.log(JSON.stringify(details, null, 2));

