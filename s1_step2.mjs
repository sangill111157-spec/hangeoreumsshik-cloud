const sleep = ms => new Promise(r => setTimeout(r, ms));
const t0 = await takeOverTaskSpace(0);
const tabs = await t0.tabs();
let target = 'p1';
for (const tb of tabs) {
  if (String(tb.title).includes('르곤') || String(tb.url).includes('genspark.ai/agents')) target = tb.label;
}
const pg = await t0.userPage(target);
await sleep(800);
const msg = "[에고 배달비서관 최종 완공 보고] 삼성 10차 감리 최종 합격 및 운영 점검표 반영, 브라우저 칩 클릭 말풍선 증빙(S1_FINAL_CHIP_PROOF.md) 커밋(309549e)까지 모두 완료하여 보고합니다.";
await pg.click('textarea');
await pg.fill('textarea', msg);
await sleep(500);
await pg.press('textarea', 'Enter');
