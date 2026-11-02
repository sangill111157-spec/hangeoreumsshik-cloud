const task = await takeOverTaskSpace(17);
const page = task.page("p2");

const res = await page.evaluate(async () => {
  // Find all button[aria-label="More options"]
  const moreBtns = Array.from(document.querySelectorAll('button[aria-label="More options"]'));
  if (moreBtns.length === 0) return { error: "No More options button found" };

  // Click the first one (i=16)
  moreBtns[0].click();

  // Wait 500ms
  await new Promise(r => setTimeout(r, 500));

  // Find all popover / menu items
  const menuElements = Array.from(document.querySelectorAll('[role="menu"] *, [role="menuitem"], [role="presentation"] *, [data-radix-popper-content-wrapper] *'));
  const texts = menuElements.map(el => el.innerText ? el.innerText.trim() : '').filter(t => t.length > 0);
  
  // Also check all buttons visible now
  const allCurrentBtns = Array.from(document.querySelectorAll('button')).map(b => b.innerText ? b.innerText.trim() : b.getAttribute('aria-label') || '').filter(t => t.length > 0);

  return {
    clicked: true,
    menuTexts: Array.from(new Set(texts)),
    buttonTexts: Array.from(new Set(allCurrentBtns))
  };
});

console.log("Result:", JSON.stringify(res, null, 2));

