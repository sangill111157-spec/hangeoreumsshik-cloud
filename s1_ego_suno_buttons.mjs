const task = await takeOverTaskSpace(17);
const page = task.page("p2");

const res = await page.evaluate(async () => {
  const buttons = Array.from(document.querySelectorAll('button')).map((b, i) => ({
    i,
    text: b.innerText ? b.innerText.trim() : '',
    ariaLabel: b.getAttribute('aria-label') || '',
    classes: b.className
  }));
  return buttons;
});

console.log("All buttons:", JSON.stringify(res, null, 2));

