
const t = await taskSpace(0);
const tbs = await t.tabs();
const target = tbs.find(b => String(b.url).includes('genspark.ai/agents')) || tbs[0];
const p = await t.userPage(target.label);
const msg = '[에고 배달비서관 v3.4 1순위 완전 종결 보고] REAL_DOM_003 원본 멀티라인 파이썬 코드 통째 실행(VERIFIED_EUNOS_2026 3.14.3 win32 출력) 및 삼성 최종 PASS 수거 커밋(2c3c5ff)을 완료하여 보고합니다.';
await p.evaluate((m) => {
  const ta = document.querySelector('textarea');
  if (!ta) return;
  const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
  setter.call(ta, m);
  ta.dispatchEvent(new Event('input', { bubbles: true }));
  ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
}, msg);
