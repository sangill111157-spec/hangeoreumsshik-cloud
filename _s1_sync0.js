
const sleep = ms => new Promise(r => setTimeout(r, ms));
const spaces = await listTaskSpaces();
const sp = spaces.find(s => s.id === 0);
if (sp) {
  const task = sp.ownership === 'user' ? await claimTaskSpace(0) : await taskSpace(0);
  const tabs = await task.tabs();
  const tb = tabs.find(t => String(t.url || '').includes('c1647638')) || tabs[0];
  const page = task.page(tb.label || 'p1');
  try { await page.click('text=확인', { timeout: 1500 }); } catch (e) {}
  try { await page.keyboard.press('Escape'); } catch (e) {}
  await sleep(500);
  try { await page.reload(); } catch (e) {}
  await sleep(5000);
  for (let i = 0; i < 8; i++) {
    try { await page.keyboard.press('PageDown'); } catch (e) {}
    await sleep(300);
  }
}
