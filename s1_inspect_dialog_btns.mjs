const task = await takeOverTaskSpace(17);
const page = task.page("p2");

const dialogBtns = await page.evaluate(() => {
  const dialog = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal, [aria-modal="true"]');
  if (!dialog) return { error: "No dialog" };
  const buttons = Array.from(dialog.querySelectorAll('button')).map((b, i) => ({
    i,
    text: b.innerText.trim(),
    classes: b.className,
    disabled: b.disabled,
    dataset: Object.assign({}, b.dataset)
  }));
  return buttons;
});

console.log("Dialog buttons:", JSON.stringify(dialogBtns, null, 2));

