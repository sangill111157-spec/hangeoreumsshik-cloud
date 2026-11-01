import subprocess

agenda = """[S1 제국 삼성(TOP 3 AI) 긴급 의사결정 안건: 다음 단계 급선무 순위 선정]
현재 S1 만능소통창(index.html, s1_server.py, sw.js s1-v1, manifest, 아이콘 3종, 킬스위치 연동, JSONL 원장)의 10차 감리 종결 및 ego(lite) 0~16번 고정 번호표(0:우리창, 1:GPT, 2:클로드, 3:대시보드, 4:수노, 5:플레이보드, 6:유튜브 @한걸음씩-r4i, 7:유튜브 @Booster_Playlist, 8:유튜브 @TheCaféHour, 9~15:SNS/포털, 16:구글시트) 편제가 완료되었다.

이제 다음 단계로 즉시 착수해야 할 [급선무 1순위 ~ 5순위]를 아래 후보군과 현재 우리의 자산을 기준으로 냉정하고 실용적으로 확정하여 제출하라:
- 후보 A: s1_zero_paste_daemon.py 2단계(URL 고유 에이전트 ID 고정 매핑 및 무복붙 데몬 완전 정착) + 만능소통창(/api/chat)의 안전한 화이트리스트 실행(Allowlist Action: 상태조회/킬스위치/렌더실행) 연결
- 후보 B: 4번 수노(Suno v6) 및 로컬 오디오/이미지 재고를 활용한 3대 유튜브 채널(6번 @한걸음씩-r4i, 7번 @Booster_Playlist, 8번 @TheCaféHour) 중 제1호 파일럿 영상 로컬 렌더링(48kHz Stereo, -16 LUFS, -1.5 dBTP V3 검산) 및 실물 완공
- 후보 C: Tailscale Serve 연동을 통한 대표님 스마트폰 실기기 LTE 접속 및 PWA 설치 완결
- 후보 D: 16번 구글 시트(5대 마스터 원장) 및 구글 드라이브(G:\\) 자동 동기화 연동

각 순위별로 (1) 선정 이유, (2) 구체적 실행 순서, (3) 완료 판정 기준(DoD)을 명확히 제시하라."""

open('s1_agenda.txt', 'w', encoding='utf-8').write(agenda)

mjs_council = """
const fs = await import('node:fs');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const promptText = fs.readFileSync('C:/Users/sangi/Downloads/shin-agent/s1_agenda.txt', 'utf-8');

for (const sid of [2, 3]) {
  try {
    const ts = await takeOverTaskSpace(sid, {leaseMs: 90000});
    const tabs = await ts.tabs();
    for (const tb of tabs) {
      const pg = tb.label ? ts.page(tb.label) : await ts.adopt(tb.page);
      if (String(tb.url).includes('genspark.ai/agents')) {
        await pg.bringToFront();
        const s = await pg.snapshot();
        const m = s.match(/textbox[^\\n]*\\[ref=(\\d+)/);
        if (m) {
          await pg.fill(m[1], promptText);
          await pg.keyboard.press('Enter');
        }
        break;
      }
    }
    await ts.yieldToUser({message: '급선무 순위 선정 안건 상정 완료'});
  } catch(e) { console.log('SEND_ERR_' + sid, e.message); }
}

await sleep(75000);

let report = '# S1 TRIUMVIRATE NEXT PRIORITY COUNCIL REPORT\\n\\n';
for (const sid of [2, 3]) {
  try {
    const ts = await takeOverTaskSpace(sid, {leaseMs: 20000});
    const tabs = await ts.tabs();
    for (const tb of tabs) {
      const pg = tb.label ? ts.page(tb.label) : await ts.adopt(tb.page);
      if (String(tb.url).includes('genspark.ai/agents')) {
        await pg.bringToFront();
        let txt = '';
        try {
          txt = await pg.evaluate(() => document.body.innerText);
        } catch(e) {
          txt = await pg.snapshot();
        }
        report += '## SPACE ' + sid + ' (' + (sid===2?'GPT-6.1 Sol':'Claude Opus 5.5') + ')\\n' + txt.slice(-6500) + '\\n\\n---\\n\\n';
        break;
      }
    }
    await ts.yieldToUser({message: '수거 완료'});
  } catch(e) { report += '## SPACE ' + sid + ' ERR: ' + e.message + '\\n\\n'; }
}

fs.writeFileSync('C:/Users/sangi/Downloads/shin-agent/S1_NEXT_PRIORITY_COUNCIL.md', report, 'utf-8');
fs.writeFileSync('C:/Users/sangi/Downloads/shin-agent/S1_OUT.md', report, 'utf-8');
"""
open('s1_priority_council.mjs', 'w', encoding='utf-8').write(mjs_council)
subprocess.run('cmd /c ego-browser nodejs < s1_priority_council.mjs', shell=True)

subprocess.run('git add -f S1_NEXT_PRIORITY_COUNCIL.md S1_OUT.md && git commit -m "S1-Next-Priority-Council" && git push -f origin main', shell=True)
chash = subprocess.getoutput('git rev-parse --short HEAD').strip()

notify_js = f"""
try {{
  const t0 = await takeOverTaskSpace(0, {{leaseMs: 25000}});
  const tabs0 = await t0.tabs();
  for (const tb of tabs0) {{
    if (String(tb.url).includes('genspark.ai')) {{
      const pg = tb.label ? t0.page(tb.label) : await t0.adopt(tb.page);
      await pg.bringToFront();
      const s = await pg.snapshot();
      const m = s.match(/textbox[^\\n]*\\[ref=(\\d+)/);
      if (m) {{
        await pg.fill(m[1], '[에고 배달비서관 보고] Space 2(GPT)·Space 3(Claude) 삼성 급선무 순위 선정 회담 수거 및 GitHub 커밋({chash}) 완료하여 전달 보고합니다.');
        await pg.keyboard.press('Enter');
      }}
      break;
    }}
  }}
  await t0.yieldToUser({{message: '보고 완료'}});
}} catch(e) {{ console.log('NOTIFY_ERR:', e.message); }}
"""
open('s1_notify_priority.mjs', 'w', encoding='utf-8').write(notify_js)
subprocess.run('cmd /c ego-browser nodejs < s1_notify_priority.mjs', shell=True)
print('=== S1_PRIORITY_COUNCIL_COMPLETE: ' + chash + ' ===')
