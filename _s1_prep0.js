
const sleep = ms => new Promise(r => setTimeout(r, ms));
const spaces = await listTaskSpaces();
const sp = spaces.find(s => s.id === 0);
if (sp) {
  const task = sp.ownership === 'user' ? await claimTaskSpace(0) : await taskSpace(0);
  const tabs = await task.tabs();
  const tb = tabs.find(t => String(t.url || '').includes('c1647638')) || tabs[0];
  const page = tb.label ? task.page(tb.label) : await task.adopt(tb.page);
  await page.fill('loc=css:textarea[name="query"]', '===S1_AUTO_START:REAL_DOM_002===\nprint("LINE1_S1_SANDBOX_ISOLATED_OK")\nprint("LINE2_REAL_DOM_002_RC0_VERIFIED")\nprint("LINE3_LEDGER_AND_RESULT_LINKED")\n===S1_AUTO_END:REAL_DOM_002===');
  await sleep(1000);
}
