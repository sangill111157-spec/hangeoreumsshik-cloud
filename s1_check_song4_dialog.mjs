const task = await takeOverTaskSpace(17);
const page = task.page("p2");

const info = await page.evaluate(() => {
  const dialog = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal, [aria-modal="true"]');
  if (!dialog) return { hasDialog: false };
  const btns = Array.from(dialog.querySelectorAll('button')).map((b, i) => ({
    i,
    text: b.innerText.trim(),
    disabled: b.disabled,
    classes: b.className
  }));
  return {
    hasDialog: true,
    text: dialog.innerText.replace(/\n+/g, ' | '),
    btns
  };
});

console.log("Song 4 dialog info:", JSON.stringify(info, null, 2));

