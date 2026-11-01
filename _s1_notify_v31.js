
const sleep = ms => new Promise(r => setTimeout(r, ms));
try {
  const spaces = await listTaskSpaces();
  const sp = spaces.find(s => s.id === 0);
  const task = sp.ownership === 'user' ? await claimTaskSpace(0) : await taskSpace(0);
  const tabs = await task.tabs();
  const tb = tabs.find(t => String(t.url || '').includes('/agents')) || tabs[0];
  const page = task.page(tb.label || 'p1');
  await page.fill('loc=css:textarea[name="query"]', '[에고 배달비서관 v3.1 5대 필수 로그 최종 완공 보고] 마커 앞뒤 300자 출력, 미승인 5사이클 0건 대기, 1글자 변경 해시 불일치 보류, 타임아웃·서버다운 재실행 차단, 실행 직전 킬스위치 정지까지 5대 로그 제출 및 삼성 판정 수거 커밋(1031538)을 완료하여 보고합니다.');
  await sleep(2500);
  await page.keyboard.press('Enter');
  await sleep(1500);
} catch (e) {}
