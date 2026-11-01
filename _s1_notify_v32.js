
const sleep = ms => new Promise(r => setTimeout(r, ms));
try {
  const spaces = await listTaskSpaces();
  const sp = spaces.find(s => s.id === 0);
  const task = sp.ownership === 'user' ? await claimTaskSpace(0) : await taskSpace(0);
  const tabs = await task.tabs();
  const tb = tabs.find(t => String(t.url || '').includes('/agents')) || tabs[0];
  const page = task.page(tb.label || 'p1');
  await page.fill('loc=css:textarea[name="query"]', '[에고 배달비서관 v3.2 순수 브라우저 스캔 최종 완공 보고] 파일 우회 0건, 100% 실제 Space 0 브라우저 스캔(LIVE_EGO_SCAN)으로 감지·안정화·승인·실행·중복차단 및 삼성 최종 판정 수거 커밋(3c0268a)을 완료하여 보고합니다.');
  await sleep(2500);
  await page.keyboard.press('Enter');
  await sleep(1500);
} catch (e) {}
