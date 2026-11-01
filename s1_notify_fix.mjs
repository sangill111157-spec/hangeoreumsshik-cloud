
try {
  const t0 = await takeOverTaskSpace(0, {leaseMs: 25000});
  const tabs0 = await t0.tabs();
  for (const tb of tabs0) {
    const pg = tb.label ? t0.page(tb.label) : await t0.adopt(tb.page);
    await pg.bringToFront();
    const s = await pg.snapshot();
    const m = s.match(/textbox[^\n]*\[ref=(\d+)/);
    if (m) {
      await pg.fill(m[1], '[에고 배달비서관 보고] 새로고침 후 모델(GPT-6.1 Sol / Claude Opus 5.5) 유지·재선택 확인 및 클로드 응답 원문 수거, 커밋(bfeff9d)까지 모두 완료하여 보고합니다.');
      await pg.keyboard.press('Enter');
      break;
    }
  }
  await t0.yieldToUser({message: '보고 완료'});
} catch(e) {}
