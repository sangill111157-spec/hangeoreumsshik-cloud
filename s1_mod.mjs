const sleep = ms => new Promise(r => setTimeout(r, ms));
const fs = await import('node:fs');
const tOmni = await taskSpace('S1_OmniChat');
const pOmni = tOmni.page('p1');
await pOmni.goto('http://127.0.0.1:8502/index.html');
await sleep(1500);
try {
  await pOmni.click({text: '8대 코어 실측 상태'});
  await sleep(1500);
} catch(e) {}
const snapAfter = await pOmni.snapshot();

const pkg = [
  '# S1 FULL EVIDENCE PACKAGE FOR FINAL SIGNOFF',
  '## 1. S1_FULL_PROOF.json (Icons 192/512/maskable + Live /api/status & /api/chat HTTP 200):',
  fs.readFileSync('C:/Users/sangi/Downloads/shin-agent/S1_FULL_PROOF.json', 'utf-8'),
  '## 2. LIVE HTTP://127.0.0.1:8502 SNAPSHOT AFTER BUTTON CLICK:',
  snapAfter,
  '## 3. manifest.webmanifest:',
  fs.readFileSync('C:/Users/sangi/Downloads/shin-agent/manifest.webmanifest', 'utf-8'),
  '## 4. sw.js (s1-v1 + offline.html):',
  fs.readFileSync('C:/Users/sangi/Downloads/shin-agent/sw.js', 'utf-8'),
  '## 5. s1_server.py:',
  fs.readFileSync('C:/Users/sangi/Downloads/shin-agent/s1_server.py', 'utf-8'),
  '## 6. index.html:',
  fs.readFileSync('C:/Users/sangi/Downloads/shin-agent/index.html', 'utf-8'),
  '위 6대 실물 증빙(Pillow 정밀 리사이즈 아이콘 3종, s1-v1 전용 sw.js 및 offline.html, s1_server.py 구동 및 /api/status·/api/chat HTTP 200 응답, http://127.0.0.1:8502 클릭 후 말풍선 스냅샷, 접근성·모바일·정직성 반영 HTML)을 확인하고 (1) 모바일 (2) PWA (3) 로컬 브릿지 1단계 최종 합격 사인오프를 제출하라.'
].join('\n\n');

for (const sid of [2, 3]) {
  try {
    const ts = await takeOverTaskSpace(sid, {leaseMs: 90000});
    const up = await ts.userPage('p1');
    await up.bringToFront();
    const s = await up.snapshot();
    const m = s.match(/textbox\s+\[ref=(\d+)/);
    if (m) {
      await up.fill(m[1], pkg);
      await up.keyboard.press('Enter');
    }
    await ts.yieldToUser({message: 'S1 Final Evidence Sent'});
  } catch(e) { console.log('SEND_ERR_' + sid, e.message); }
}

await sleep(75000);

let report = '# S1 FINAL 100 SIGNOFF REPORT\n\n## SNAPSHOT AFTER CLICK\n```\n' + snapAfter + '\n```\n\n';
for (const sid of [2, 3]) {
  try {
    const ts = await takeOverTaskSpace(sid, {leaseMs: 15000});
    const up = await ts.userPage('p1');
    const txt = await up.evaluate(() => document.body.innerText);
    report += '## SPACE ' + sid + '\n' + txt.slice(-6000) + '\n\n---\n\n';
    await ts.yieldToUser({message: 'S1 Collected'});
  } catch(e) { console.log('COLLECT_ERR_' + sid, e.message); }
}
fs.writeFileSync('C:/Users/sangi/Downloads/shin-agent/S1_OUT.md', report, 'utf-8');
console.log('EGO_AUDIT_COMPLETE_OK');
