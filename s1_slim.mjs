
const fs = await import('node:fs');
const sleep = ms => new Promise(r => setTimeout(r, ms));
let log = ['# S1 LIGHTWEIGHT SPACES & SMART REPORT'];

// 1. 당장 안 쓰는 무거운 창(5~16번) 닫아서 노트북 메모리 경량화
const heavyNames = ['5_플레이보드', '6_유튜브_한걸음씩', '7_유튜브_부스터플리', '8_유튜브_카페아워', '16_구글시트'];
for (const nm of heavyNames) {
  try {
    const ts = await taskSpace(nm);
    await ts.finish({keep: []});
    log.push('CLOSED_HEAVY_SPACE: ' + nm);
  } catch(e) { log.push('CLOSE_SKIP_' + nm + ': ' + e.message); }
}

// 2. 3_대시보드 창에 S1 만능소통창(http://127.0.0.1:8503/index.html) 정확히 띄우기 (새 페이지 생성 대응)
try {
  const td = await taskSpace('3_대시보드');
  const tabsD = await td.tabs();
  let pd = null;
  if (tabsD.length > 0) {
    const t0 = tabsD[0];
    pd = t0.label ? td.page(t0.label) : await td.adopt(t0.page);
  } else {
    pd = await td.newPage();
  }
  await pd.goto('http://127.0.0.1:8503/index.html');
  await sleep(1000);
  log.push('DASHBOARD_READY: ' + (await pd.url()));
} catch(e) { log.push('DASHBOARD_ERR: ' + e.message); }

const afterSpaces = await listTaskSpaces();
log.push('## ACTIVE SPACES (LIGHTWEIGHT 0~4):', JSON.stringify(afterSpaces, null, 2));
fs.writeFileSync('C:/Users/sangi/Downloads/shin-agent/S1_OUT.md', log.join('\n\n'), 'utf-8');
