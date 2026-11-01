
const sleep = ms => new Promise(r => setTimeout(r, ms));
try {
  const spaces = await listTaskSpaces();
  const sp = spaces.find(s => s.id === 0);
  const task = sp.ownership === 'user' ? await claimTaskSpace(0) : await taskSpace(0);
  const tabs = await task.tabs();
  const tb = tabs.find(t => String(t.url || '').includes('/agents')) || tabs[0];
  const page = tb.label ? task.page(tb.label) : await task.adopt(tb.page);
  await page.fill('loc=css:textarea[name="query"]', '[에고 배달비서관 6대 안전요건 완비 최종 보고] 비신뢰 탭 차단, 승인 관문, 원장 손상 즉시 정지, 2회 연속 해시 검증, 킬스위치 정지까지 6대 실측 및 삼성 최종 감리 수거 커밋(50fa75e)을 완료하여 보고합니다.');
  await sleep(2500);
  await page.keyboard.press('Enter');
  await sleep(1500);
} catch (e) {}
