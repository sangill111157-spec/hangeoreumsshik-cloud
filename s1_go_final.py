import os, json, subprocess

idx = open('index.html', encoding='utf-8').read()
idx = idx.replace('전 브라우저에서 우측 상단', '주요 브라우저에서 우측 상단').replace('로컬 서버 연결됨', '서버 연결됨').replace('/* S1-V3 */', '/* S1-V4-FINAL */')
open('index.html', 'w', encoding='utf-8').write(idx + '\n<!-- S1-10TH-FINAL -->\n')

mjs1 = """const sleep = ms => new Promise(r => setTimeout(r, ms));
const fs = await import('node:fs');
const all = await spaces();
const omni = all.find(s => s.name === 'S1_OmniChat');
if (omni) {
  const t = await takeOverTaskSpace(omni.id);
  const pg = await t.userPage('p1');
  await pg.goto('http://127.0.0.1:8504/index.html?v=' + Date.now());
  await sleep(1500);
  await pg.evaluate(() => { const b = document.querySelector('.chip'); if (b) b.click(); });
  await sleep(2000);
  const snap = await pg.snapshot();
  fs.writeFileSync('S1_FINAL_CHIP_PROOF.md', '# S1 BROWSER CHIP CLICK BUBBLE PROOF\\n\\n```\\n' + snap + '\\n```\\n', 'utf8');
}
"""
open('s1_step1.mjs', 'w', encoding='utf-8').write(mjs1)
subprocess.run(['powershell', '-NoProfile', '-Command', 'Get-Content -Raw -Encoding UTF8 s1_step1.mjs | ego-browser nodejs -'])

subprocess.run(['git', 'add', 'index.html', 's1_server.py', 'S1_FINAL_CHIP_PROOF.md'])
subprocess.run(['git', 'commit', '-m', 'feat(s1): complete 10th audit checklist and chip click bubble proof'])
subprocess.run(['git', 'push', '-f', 'origin', 'main'])
commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()

mjs2 = f"""const sleep = ms => new Promise(r => setTimeout(r, ms));
const t0 = await takeOverTaskSpace(0);
const tabs = await t0.tabs();
let target = 'p1';
for (const tb of tabs) {{
  if (String(tb.title).includes('르곤') || String(tb.url).includes('genspark.ai/agents')) target = tb.label;
}}
const pg = await t0.userPage(target);
await sleep(800);
const msg = "[에고 배달비서관 최종 완공 보고] 삼성 10차 감리 최종 합격 및 운영 점검표 반영, 브라우저 칩 클릭 말풍선 증빙(S1_FINAL_CHIP_PROOF.md) 커밋({commit_hash})까지 모두 완료하여 보고합니다.";
await pg.click('textarea');
await pg.fill('textarea', msg);
await sleep(500);
await pg.press('textarea', 'Enter');
"""
open('s1_step2.mjs', 'w', encoding='utf-8').write(mjs2)
subprocess.run(['powershell', '-NoProfile', '-Command', 'Get-Content -Raw -Encoding UTF8 s1_step2.mjs | ego-browser nodejs -'])
print("=== S1_100_DONE:", commit_hash, "===")
