
const sleep = ms => new Promise(r => setTimeout(r, ms));
try {
  const spaces = await listTaskSpaces();
  const sp = spaces.find(s => s.id === 0);
  const task = sp.ownership === 'user' ? await claimTaskSpace(0) : await taskSpace(0);
  const tabs = await task.tabs();
  const tb = tabs.find(t => String(t.url || '').includes('/agents')) || tabs[0];
  const page = tb.label ? task.page(tb.label) : await task.adopt(tb.page);
  await page.fill('loc=css:textarea[name="query"]', '[에고 배달비서관 대표님 허락 기반 v3.3 최종 완공 보고] 르곤 보좌관의 명령(REAL_DOM_002) 감지 -> 5회 대기(HOLD) -> 대표님 직접 허락(Enter) -> 격리 실행(rc=0, stdout 3줄) -> 실행 커밋(e1f8aa8) 및 삼성 최종 판정 수거 커밋(531246d)까지 완료하여 보고합니다.');
  await sleep(2500);
  await page.keyboard.press('Enter');
  await sleep(1500);
} catch (e) {}
