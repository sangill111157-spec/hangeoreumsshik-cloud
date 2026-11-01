const sleep = ms => new Promise(r => setTimeout(r, ms));
const { Ego } = await import('file:///C:/Program%20Files/Citro%20Labs/ego%20lite/Application/0.6.0.0/resources/app.asar/dist/ego-script/index.js');
const ego = new Ego();
const spaces = await ego.listTaskSpaces();

for (const sp of spaces) {
  try {
    const tk = await ego.takeOverTaskSpace(sp.id);
    const tbs = await tk.tabs();
    for (const tb of tbs) {
      const tid = String(tb.id || 'p1');
      const ttitle = String(tb.title || '');
      const turl = String(tb.url || '');
      if (ttitle.includes('완공 파이프라인') || ttitle.includes('인수인계') || turl.includes('genspark.ai/agents')) {
        await tk.switchTo(tid);
        await sleep(600);
        const up = await tk.userPage(tid);
        if (!up) continue;
        const snap = String(await up.snapshot());
        if (snap.includes('클로드 창이 뒤로 가있다') || snap.includes('배달비서관') || ttitle.includes('완공 파이프라인')) {
          let boxRef = null;
          for (const line of snap.split('\n')) {
            if (line.includes('textbox') || line.includes('무엇이든') || line.includes('Ask')) {
              const m = line.match(/\[(e\d+)\]/);
              if (m) boxRef = m[1];
            }
          }
          const msg = '[에고 배달비서관 동적 탐색 완공 보고] 다중 창·탭 변수 스캔(switchTo)으로 뒤에 있던 클로드 창과 우리 창을 모두 찾아내어 모델 검증(Claude Opus 5.5 / GPT-6.1 Sol) 및 클로드 응답 수거, 커밋(04f0e05)까지 완료하여 보고합니다.';
          if (boxRef) {
            await up.click(boxRef);
            await sleep(300);
            await up.fill(boxRef, msg);
            await sleep(400);
            await up.press('Enter');
            console.log('DYNAMIC_NOTIFY_SENT_ON_SPACE_' + sp.id + '_TAB_' + tid);
            process.exit(0);
          }
        }
      }
    }
  } catch (e) {}
}