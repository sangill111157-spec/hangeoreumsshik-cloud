
const sleep = ms => new Promise(r => setTimeout(r, ms));
try {
  const t0 = await taskSpace(0);
  const tabs0 = await t0.tabs();
  let pg = null;
  for (const tb of tabs0) {
    if (JSON.stringify(tb).toLowerCase().includes('genspark') || tabs0.length === 1) {
      pg = tb.label ? t0.page(tb.label) : await t0.adopt(tb.page);
      break;
    }
  }
  if (pg) {
    // (1) 먼저 입력창이 보이는지 스냅샷 점검, 안 보이면 안전하게 reload 후 대기
    let snap = await pg.snapshot();
    if (!snap.includes('textbox')) {
      await pg.reload();
      await sleep(4000);
      snap = await pg.snapshot();
    }
    // (2) 대표님 타이핑 중이거나 AI 답변 중이면 최대 3회(15초) 예절 대기
    for (let waitTry = 0; waitTry < 3; waitTry++) {
      const busy = await pg.evaluate(() => {
        const el = document.querySelector('textarea, input[type="text"], [contenteditable="true"]');
        const val = el ? (el.value || el.innerText || '').trim() : '';
        return val.length > 0;
      });
      if (!busy) break;
      console.log('USER_TYPING_WAIT...');
      await sleep(5000);
    }
    // (3) 최신 ref 번호를 다시 찍어서 정확히 입력 후 Enter
    snap = await pg.snapshot();
    const m = snap.match(/textbox[^\n]*\[ref=(\d+)/);
    if (m) {
      await pg.fill(m[1], '[에고 배달비서관 보고] 불필요한 무거운 창(5~16번)을 닫아 노트북 경량화(0~4번 핵심창 유지) 및 3번 대시보드 연결, 커밋(3d34923)까지 완료하여 전달 보고합니다.');
      await sleep(500);
      await pg.keyboard.press('Enter');
      console.log('POLITE_NOTIFY_SUCCESS');
    } else {
      console.log('TEXTBOX_NOT_FOUND_IN_SNAP');
    }
  }
} catch(e) { console.log('POLITE_NOTIFY_ERR:', e.message); }
