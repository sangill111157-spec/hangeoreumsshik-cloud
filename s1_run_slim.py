import subprocess

ego_slim_and_report = """
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
fs.writeFileSync('C:/Users/sangi/Downloads/shin-agent/S1_OUT.md', log.join('\\n\\n'), 'utf-8');
"""
open('s1_slim.mjs', 'w', encoding='utf-8').write(ego_slim_and_report)
subprocess.run('cmd /c ego-browser nodejs < s1_slim.mjs', shell=True)

subprocess.run('git add -f S1_OUT.md && git commit -m "S1-Lightweight-0to4" && git push -f origin main', shell=True)
chash = subprocess.getoutput('git rev-parse --short HEAD').strip()

# 3. [배달비서관 예절·충돌방지 & 스마트 동기화 보고] 0번 우리창(p3) 상태 점검 후 안전 입력 및 Enter
polite_notify = f"""
const sleep = ms => new Promise(r => setTimeout(r, ms));
try {{
  const t0 = await taskSpace(0);
  const tabs0 = await t0.tabs();
  let pg = null;
  for (const tb of tabs0) {{
    if (JSON.stringify(tb).toLowerCase().includes('genspark') || tabs0.length === 1) {{
      pg = tb.label ? t0.page(tb.label) : await t0.adopt(tb.page);
      break;
    }}
  }}
  if (pg) {{
    // (1) 먼저 입력창이 보이는지 스냅샷 점검, 안 보이면 안전하게 reload 후 대기
    let snap = await pg.snapshot();
    if (!snap.includes('textbox')) {{
      await pg.reload();
      await sleep(4000);
      snap = await pg.snapshot();
    }}
    // (2) 대표님 타이핑 중이거나 AI 답변 중이면 최대 3회(15초) 예절 대기
    for (let waitTry = 0; waitTry < 3; waitTry++) {{
      const busy = await pg.evaluate(() => {{
        const el = document.querySelector('textarea, input[type="text"], [contenteditable="true"]');
        const val = el ? (el.value || el.innerText || '').trim() : '';
        return val.length > 0;
      }});
      if (!busy) break;
      console.log('USER_TYPING_WAIT...');
      await sleep(5000);
    }}
    // (3) 최신 ref 번호를 다시 찍어서 정확히 입력 후 Enter
    snap = await pg.snapshot();
    const m = snap.match(/textbox[^\\n]*\\[ref=(\\d+)/);
    if (m) {{
      await pg.fill(m[1], '[에고 배달비서관 보고] 불필요한 무거운 창(5~16번)을 닫아 노트북 경량화(0~4번 핵심창 유지) 및 3번 대시보드 연결, 커밋({chash})까지 완료하여 전달 보고합니다.');
      await sleep(500);
      await pg.keyboard.press('Enter');
      console.log('POLITE_NOTIFY_SUCCESS');
    }} else {{
      console.log('TEXTBOX_NOT_FOUND_IN_SNAP');
    }}
  }}
}} catch(e) {{ console.log('POLITE_NOTIFY_ERR:', e.message); }}
"""
open('s1_polite_notify.mjs', 'w', encoding='utf-8').write(polite_notify)
subprocess.run('cmd /c ego-browser nodejs < s1_polite_notify.mjs', shell=True)
print('=== S1_SLIM_AND_POLITE_NOTIFY_DONE: ' + chash + ' ===')
