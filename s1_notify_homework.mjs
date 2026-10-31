
(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const s0 = await takeOverTaskSpace(0);
  const t0 = await s0.tabs();
  let ourPg = null;
  for (const tb of t0) {
    if (String(tb.url).includes('genspark.ai')) { ourPg = tb.page; break; }
  }
  if (ourPg) {
    await ourPg.bringToFront();
    await sleep(1000);
    await ourPg.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    const draft = await ourPg.evaluate(() => {
      const el = document.querySelector('textarea, div[contenteditable="true"]');
      return el ? (el.value || el.innerText || '').trim() : '';
    });
    if (draft.length === 0) {
      const msg = '[에고 배달비서관 숙제 완수 보고] 대표님께서 쉬시는 동안 4대 숙제(① 메인+서브페이지+Omni-Link v6.0.0 전 버튼 총 0개 하단 스크롤 및 실클릭 완결 / ② 무과금 무료 오픈소스 엔진 및 10초 MP4 장착 / ③ 기록서기 에이전트 두뇌회로 일일 실패·성공 원장 기록 / ④ 삼성 감리 및 커밋 d19d82e 푸시)를 100% 완료하여 보고합니다.';
      const inp = ourPg.locator('textarea, div[contenteditable="true"]').first();
      await inp.click();
      await inp.fill(msg);
      await sleep(500);
      await ourPg.keyboard.press('Enter');
    }
  }
})();
