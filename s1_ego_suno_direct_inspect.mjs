const task = await takeOverTaskSpace(17);
const page = task.page("p2");

// Click the button with aria-label="More actions"
console.log("Clicking More actions button...");
await page.click('button[aria-label="More actions"]');

// Wait 1 second and check what menu items appeared
await new Promise(r => setTimeout(r, 1000));

const menuItems = await page.evaluate(() => {
  // Check dropdown / popover / menu items
  const items = Array.from(document.querySelectorAll('[role="menuitem"], [role="option"], [data-radix-collection-item], button, a')).map(el => ({
    tag: el.tagName,
    text: el.innerText ? el.innerText.trim().replace(/\n+/g, ' ') : '',
    role: el.getAttribute('role') || '',
    ariaLabel: el.getAttribute('aria-label') || '',
    classes: el.className
  })).filter(el => 
    el.text.toLowerCase().includes('download') || 
    el.text.includes('다운로드') ||
    el.text.toLowerCase().includes('audio') ||
    el.text.toLowerCase().includes('video') ||
    el.text.toLowerCase().includes('wav') ||
    el.text.toLowerCase().includes('mp3') ||
    el.text.toLowerCase().includes('create') ||
    el.text.toLowerCase().includes('reuse') ||
    el.text.toLowerCase().includes('share')
  );
  return items;
});

console.log("Menu Items:", JSON.stringify(menuItems, null, 2));
