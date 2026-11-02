const task = await takeOverTaskSpace(17);
const page = task.page("p2");

const info = await page.evaluate(() => {
  const dialog = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal, [aria-modal="true"]');
  const moreBtns = Array.from(document.querySelectorAll('button[aria-label="More options"]')).map((b, i) => ({
    i,
    text: b.innerText,
    ariaLabel: b.getAttribute('aria-label'),
    classes: b.className
  }));

  return {
    url: window.location.href,
    title: document.title,
    hasDialog: !!dialog,
    dialogText: dialog ? dialog.innerText.replace(/\n+/g, ' | ') : null,
    moreBtnsCount: moreBtns.length,
    buttonsCount: document.querySelectorAll('button').length
  };
});

console.log("Current page state:", JSON.stringify(info, null, 2));

