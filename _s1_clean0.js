
const spaces = await listTaskSpaces();
const sp = spaces.find(s => s.id === 0);
if (sp) {
  const task = sp.ownership === 'user' ? await claimTaskSpace(0) : await taskSpace(0);
  const tabs = await task.tabs();
  const tb = tabs.find(t => String(t.url || '').includes('c1647638')) || tabs[0];
  const page = tb.label ? task.page(tb.label) : await task.adopt(tb.page);
  try { await page.fill('loc=css:textarea[name="query"]', ''); } catch (e) {}
}
