const task = await takeOverTaskSpace(17);
const page = task.page("p2");

const dialogInfo = await page.evaluate(() => {
  // Find dialog or modal
  const dialog = document.querySelector('[role="dialog"], [data-radix-dialog-content], .modal, [aria-modal="true"]');
  if (dialog) {
    const text = dialog.innerText;
    const inputs = Array.from(dialog.querySelectorAll('input, button, a, [role="radio"]')).map(el => ({
      tag: el.tagName,
      type: el.type,
      text: el.innerText ? el.innerText.trim() : '',
      ariaLabel: el.getAttribute('aria-label') || '',
      checked: el.checked,
      value: el.value
    }));
    return {
      hasDialog: true,
      text: text.replace(/\n+/g, ' | '),
      inputs
    };
  }

  // Look around the BUTTON with text Download
  const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.trim() === 'Download');
  if (btn) {
    let p = btn.parentElement;
    for (let i = 0; i < 4 && p; i++) {
      if (p.innerText && (p.innerText.includes('Audio') || p.innerText.includes('Video') || p.innerText.includes('WAV') || p.innerText.includes('MP3'))) {
        return {
          foundParent: true,
          parentTag: p.tagName,
          text: p.innerText.replace(/\n+/g, ' | ')
        };
      }
      p = p.parentElement;
    }
  }

  return { hasDialog: false };
});

console.log("Dialog Info:", JSON.stringify(dialogInfo, null, 2));

