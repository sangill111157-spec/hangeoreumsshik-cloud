
(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const s0 = await takeOverTaskSpace(0);
  const t0 = await s0.tabs();
  if (t0.length > 0) {
    const p = t0[0].page;
    await p.bringToFront();
    await sleep(800);
    await p.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    const draft = await p.evaluate(() => {
      const el = document.querySelector('textarea, div[contenteditable="true"]');
      return el ? (el.value || el.innerText || '').trim() : '';
    });
    if (draft.length === 0) {
      const msg = '[에고 배달비서관 분리 완수 보고] 대표님 지시대로 ① 대시보드(rgon_alpha_chat.html) 단독 스크롤 및 0개 버튼 실클릭 완료(실패 0건), ② 만능 소통창(index.html 순수 복원 + rgon_aside_extension v6.0.0) 단독 0개 버튼 실클릭 완료(실패 0건)로 두 체계를 100% 분리 완결하고 커밋(3195980)까지 완료하여 보고합니다.';
      const inp = p.locator('textarea, div[contenteditable="true"]').first();
      await inp.click();
      await inp.fill(msg);
      await sleep(400);
      await p.keyboard.press('Enter');
    }
  }
})();
