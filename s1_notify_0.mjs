
try {
  const t0 = await takeOverTaskSpace(0, {leaseMs: 25000});
  const tabs0 = await t0.tabs();
  for (const tb of tabs0) {
    const info = JSON.stringify(tb).toLowerCase();
    const pg = tb.label ? t0.page(tb.label) : await t0.adopt(tb.page);
    if (info.includes('genspark') || info.includes('르곤') || tabs0.length === 1) {
      await pg.bringToFront();
      const s = await pg.snapshot();
      const m = s.match(/textbox[^\n]*\[ref=(\d+)/);
      if (m) {
        await pg.fill(m[1], '[에고 배달비서관 보고] 0번 우리창 단일화 및 0~16번 고정 창 셋팅(커밋 6914cb4) 완료하여 전달 보고합니다.');
        await pg.keyboard.press('Enter');
        console.log('NOTIFY_SENT_OK');
      }
      break;
    }
  }
  await t0.yieldToUser({message: '보고 완료'});
} catch(e) { console.log('NOTIFY_ERR:', e.message); }
