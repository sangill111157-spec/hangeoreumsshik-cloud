
const fs = await import('node:fs');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const spacesBefore = await listTaskSpaces();
let log = ['# S1 SPACE SETUP REPORT', '## BEFORE:', JSON.stringify(spacesBefore, null, 2)];

// 1. Space 0 (우리창 단일화: Suno 탭은 닫고 르곤 보좌관 탭만 맨 앞으로 활성화)
try {
  const t0 = await takeOverTaskSpace(0, {leaseMs: 30000});
  const tabs0 = await t0.tabs();
  for (const tb of tabs0) {
    const pg = tb.label ? t0.page(tb.label) : await t0.adopt(tb.page);
    const u = pg.url();
    if (u.includes('suno.com') && tabs0.length > 1) {
      try { await pg.close(); } catch(e) {}
    } else if (u.includes('genspark.ai')) {
      try { await pg.bringToFront(); } catch(e) {}
    }
  }
  await t0.yieldToUser({message: '0번 우리창 단일화 완료'});
} catch(e) { log.push('SPACE0_ERR: ' + e.message); }

// 2. 3번 대시보드(S1_03_DASHBOARD) 및 4번 수노(S1_04_SUNO) 등 단일창 개설/정렬
const targets = [
  {name: '3_대시보드', url: 'http://127.0.0.1:8503/index.html'},
  {name: '4_수노', url: 'https://suno.com/me'},
  {name: '5_플레이보드', url: 'https://playboard.co'},
  {name: '6_유튜브_한걸음씩', url: 'https://www.youtube.com/@%ED%95%9C%EA%B1%B8%EC%9D%8C%EC%94%A9-r4i'},
  {name: '7_유튜브_부스터플리', url: 'https://www.youtube.com/@Booster_Playlist'},
  {name: '8_유튜브_카페아워', url: 'https://www.youtube.com/@TheCaf%C3%A9Hour'},
  {name: '16_구글시트', url: 'https://docs.google.com/spreadsheets/'}
];

for (const item of targets) {
  try {
    const ts = await taskSpace(item.name);
    const p1 = ts.page('p1');
    await p1.goto(item.url);
    await sleep(800);
    await ts.yieldToUser({message: item.name + ' 준비 완료'});
  } catch(e) { log.push(item.name + '_ERR: ' + e.message); }
}

const spacesAfter = await listTaskSpaces();
log.push('## AFTER:', JSON.stringify(spacesAfter, null, 2));
fs.writeFileSync('C:/Users/sangi/Downloads/shin-agent/S1_OUT.md', log.join('\n\n'), 'utf-8');
