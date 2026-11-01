
const sleep = ms => new Promise(r => setTimeout(r, ms));
const spaces = await listTaskSpaces();
const sp = spaces.find(s => s.id === 0);
const task = sp.ownership === 'user' ? await claimTaskSpace(0) : await taskSpace(0);
const tabs = await task.tabs();
const tb = tabs.find(t => String(t.url || '').includes('genspark.ai')) || tabs[0];
const page = tb.label ? task.page(tb.label) : await task.adopt(tb.page);
try {
  await page.fill('loc=css:textarea[name="query"]', '[에고 배달비서관 5시간 제한 자동 대기·재개 및 4대 증빙 완공 보고] 22:22 쿼터 해제 시각 자동 대기(Auto-Resume) 후 4대 증빙 제출·수거·커밋(e6a616b)까지 완료하여 보고합니다.');
  await sleep(2500);
  await page.keyboard.press('Enter');
  await sleep(1500);
} catch (e) {}
