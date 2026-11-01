
try {
  const t0 = await takeOverTaskSpace(0, {leaseMs: 25000});
  const tabs0 = await t0.tabs();
  for (const tb of tabs0) {
    if (String(tb.url).includes('genspark.ai')) {
      const pg = tb.label ? t0.page(tb.label) : await t0.adopt(tb.page);
      await pg.bringToFront();
      const s = await pg.snapshot();
      const m = s.match(/textbox[^\n]*\[ref=(\d+)/);
      if (m) {
        await pg.fill(m[1], '[에고 배달비서관 보고] Space 2(GPT)·Space 3(Claude) 삼성 급선무 순위 선정 회담 수거 및 GitHub 커밋(3cef227) 완료하여 전달 보고합니다.');
        await pg.keyboard.press('Enter');
      }
      break;
    }
  }
  await t0.yieldToUser({message: '보고 완료'});
} catch(e) { console.log('NOTIFY_ERR:', e.message); }
