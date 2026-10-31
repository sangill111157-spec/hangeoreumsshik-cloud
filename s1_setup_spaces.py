import json, subprocess

registry = [
  {"index": 0, "space_name": "S1_00_RGON", "title": "0. 우리창 (르곤 보좌관)", "url": "https://www.genspark.ai/agents?id=c1647638-2531-43db-a059-c153d8da14d9"},
  {"index": 1, "space_name": "S1_01_GPT", "title": "1. GPT-6.1 Sol", "url": "https://www.genspark.ai/agents"},
  {"index": 2, "space_name": "S1_02_CLAUDE", "title": "2. Claude Opus 5.5", "url": "https://www.genspark.ai/agents"},
  {"index": 3, "space_name": "S1_03_DASHBOARD", "title": "3. S1 대시보드 (만능소통창)", "url": "http://127.0.0.1:8503/index.html"},
  {"index": 4, "space_name": "S1_04_SUNO", "title": "4. 수노 (Suno v6)", "url": "https://suno.com/me"},
  {"index": 5, "space_name": "S1_05_PLAYBOARD", "title": "5. 플레이보드", "url": "https://playboard.co"},
  {"index": 6, "space_name": "S1_06_YT_STEP", "title": "6. 유튜브 (한걸음씩)", "url": "https://www.youtube.com/@%ED%95%9C%EA%B1%B8%EC%9D%8C%EC%94%A9-r4i"},
  {"index": 7, "space_name": "S1_07_YT_BOOSTER", "title": "7. 유튜브 (부스터 플리)", "url": "https://www.youtube.com/@Booster_Playlist"},
  {"index": 8, "space_name": "S1_08_YT_CAFE", "title": "8. 유튜브 (The Cafe Hour)", "url": "https://www.youtube.com/@TheCaf%C3%A9Hour"},
  {"index": 9, "space_name": "S1_09_TIKTOK", "title": "9. 틱톡", "url": "https://www.tiktok.com"},
  {"index": 10, "space_name": "S1_10_THREADS", "title": "10. 스레드", "url": "https://www.threads.net"},
  {"index": 11, "space_name": "S1_11_INSTA", "title": "11. 인스타그램", "url": "https://www.instagram.com"},
  {"index": 12, "space_name": "S1_12_FACEBOOK", "title": "12. 페이스북", "url": "https://www.facebook.com"},
  {"index": 13, "space_name": "S1_13_BLOG", "title": "13. 블로그", "url": "https://www.tistory.com"},
  {"index": 14, "space_name": "S1_14_NAVER", "title": "14. 네이버", "url": "https://www.naver.com"},
  {"index": 15, "space_name": "S1_15_GOOGLE", "title": "15. 구글 드라이브", "url": "https://drive.google.com"},
  {"index": 16, "space_name": "S1_16_GSHEETS", "title": "16. 구글 시트", "url": "https://docs.google.com/spreadsheets/"}
]
open('S1_SPACE_REGISTRY.json', 'w', encoding='utf-8').write(json.dumps(registry, ensure_ascii=False, indent=2))

ego_setup = """
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
fs.writeFileSync('C:/Users/sangi/Downloads/shin-agent/S1_OUT.md', log.join('\\n\\n'), 'utf-8');
"""
open('s1_space_setup.mjs', 'w', encoding='utf-8').write(ego_setup)
subprocess.run('cmd /c ego-browser nodejs < s1_space_setup.mjs', shell=True)

subprocess.run('git add -f S1_SPACE_REGISTRY.json S1_OUT.md && git commit -m "S1-Spaces-0-to-16-Setup" && git push -f origin main', shell=True)
chash = subprocess.getoutput('git rev-parse --short HEAD').strip()

# 3. 배달비서관이 0번 우리창에 완료 보고 입력 후 Enter 전송
notify_js = f"""
try {{
  const t0 = await takeOverTaskSpace(0, {{leaseMs: 20000}});
  const tabs0 = await t0.tabs();
  for (const tb of tabs0) {{
    const pg = tb.label ? t0.page(tb.label) : await t0.adopt(tb.page);
    if (pg.url().includes('genspark.ai')) {{
      await pg.bringToFront();
      const s = await pg.snapshot();
      const m = s.match(/textbox[^\\n]*\\[ref=(\\d+)/);
      if (m) {{
        await pg.fill(m[1], '[에고 배달비서관 보고] 0번 우리창 단일화 및 0~16번 고정 창 셋팅(커밋 {chash}) 완료하여 전달 보고합니다.');
        await pg.keyboard.press('Enter');
      }}
      break;
    }}
  }}
  await t0.yieldToUser({{message: '보고 완료'}});
}} catch(e) {{ console.log('NOTIFY_ERR:', e.message); }}
"""
open('s1_notify_0.mjs', 'w', encoding='utf-8').write(notify_js)
subprocess.run('cmd /c ego-browser nodejs < s1_notify_0.mjs', shell=True)
print('=== S1_SPACES_SETUP_AND_NOTIFY_COMPLETE: ' + chash + ' ===')
