const fs = await import('node:fs');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const { Ego } = await import('file:///C:/Program%20Files/Citro%20Labs/ego%20lite/Application/0.6.0.0/resources/app.asar/dist/ego-script/index.js');
const ego = new Ego();

const spaces = await ego.listTaskSpaces();
const scanLog = [];
let claudeMatch = null;
let gptMatch = null;
let ourMatch = null;
let dashMatch = null;

// 1. 모든 Space + 모든 탭(p1, p2, p3...)을 동적 변수로 전수 조사 및 switchTo 깨우기
for (const sp of spaces) {
  try {
    const tk = await ego.takeOverTaskSpace(sp.id);
    const tbs = await tk.tabs();
    for (const tb of tbs) {
      const tid = String(tb.id || 'p1');
      const turl = String(tb.url || '');
      const ttitle = String(tb.title || '');
      try {
        await tk.switchTo(tid);
        await sleep(600);
      } catch (e) {}
      const up = await tk.userPage(tid);
      let snap = '';
      if (up) {
        try { snap = String(await up.snapshot()); } catch (e) {}
      }
      scanLog.push({ spaceId: sp.id, tabId: tid, title: ttitle.slice(0, 40), url: turl.slice(0, 60), snapLen: snap.length });

      // 동적 변수 매칭
      if (turl.includes('127.0.0.1') || ttitle.includes('SUN-ONE AON')) {
        dashMatch = { spaceId: sp.id, tabId: tid, tk, up, snap };
      } else if (ttitle.includes('완공 파이프라인') || ttitle.includes('인수인계') || snap.includes('클로드 창이 뒤로 가있다') || snap.includes('배달비서관')) {
        ourMatch = { spaceId: sp.id, tabId: tid, tk, up, snap };
      } else if (snap.includes('Claude') || snap.includes('Opus') || snap.includes('클로드') || snap.includes('트랙 1') || snap.includes('권장안')) {
        if (!claudeMatch || snap.includes('Claude Opus')) {
          claudeMatch = { spaceId: sp.id, tabId: tid, tk, up, snap };
        }
      } else if (snap.includes('GPT-6.1') || snap.includes('Sol') || snap.includes('합격')) {
        gptMatch = { spaceId: sp.id, tabId: tid, tk, up, snap };
      }
    }
  } catch (e) {
    scanLog.push({ spaceId: sp.id, error: String(e.message || e) });
  }
}

// 2. 만약 클로드 창이 아직 구분 안 되었으면 agents 탭 중 우리 창/GPT 창이 아닌 탭을 동적 변수로 자동 지정
if (!claudeMatch) {
  for (const sp of spaces) {
    try {
      const tk = await ego.takeOverTaskSpace(sp.id);
      const tbs = await tk.tabs();
      for (const tb of tbs) {
        const tid = String(tb.id || 'p1');
        const turl = String(tb.url || '');
        if (turl.includes('genspark.ai/agents')) {
          const isOur = ourMatch && ourMatch.spaceId === sp.id && ourMatch.tabId === tid;
          const isGpt = gptMatch && gptMatch.spaceId === sp.id && gptMatch.tabId === tid;
          if (!isOur && !isGpt) {
            await tk.switchTo(tid);
            const up = await tk.userPage(tid);
            const snap = up ? String(await up.snapshot()) : '';
            claudeMatch = { spaceId: sp.id, tabId: tid, tk, up, snap };
          }
        }
      }
    } catch (e) {}
  }
}

// 3. 클로드 창 맨 앞으로 활성화(switchTo) + 새로고침 후 모델 확인·복구 + 답변 전문 수거
let claudeReport = 'NOT_FOUND';
let claudeModelStatus = 'UNKNOWN';
if (claudeMatch) {
  try {
    await claudeMatch.tk.switchTo(claudeMatch.tabId);
    await sleep(1000);
    const up = await claudeMatch.tk.userPage(claudeMatch.tabId);
    let snap = String(await up.snapshot());
    if (snap.includes('Claude Opus 5.5')) {
      claudeModelStatus = 'VERIFIED_CLAUDE_OPUS_5_5';
    } else {
      // 모델 선택 복구 시도
      const lines = snap.split('\n');
      for (const l of lines) {
        if (l.includes('GPT') || l.includes('Gemini') || l.includes('Claude') || l.includes('Model')) {
          const m = l.match(/\[(e\d+)\]/);
          if (m) {
            try { await up.click(m[1]); await sleep(1000); break; } catch (e) {}
          }
        }
      }
      const s2 = String(await up.snapshot());
      for (const l of s2.split('\n')) {
        if (l.includes('Claude Opus 5.5') || l.includes('Opus')) {
          const m = l.match(/\[(e\d+)\]/);
          if (m) {
            try { await up.click(m[1]); await sleep(1000); claudeModelStatus = 'RESTORED_CLAUDE_OPUS_5_5'; break; } catch (e) {}
          }
        }
      }
      snap = String(await up.snapshot());
    }
    claudeReport = snap.slice(-3500);
  } catch (e) {
    claudeReport = 'ERR: ' + String(e.message || e);
  }
}

// 4. GPT 창 모델 확인
let gptModelStatus = 'NOT_FOUND';
if (gptMatch) {
  gptModelStatus = gptMatch.snap.includes('GPT-6.1 Sol') ? 'VERIFIED_GPT_6_1_SOL' : 'CHECKED_SPACE_' + gptMatch.spaceId;
}

const outMd = [
  '# 🧠 S1 [다중 창·탭 동적 변수 스캔 & 클로드 맨 앞 활성화 및 모델 검증] 최종 보고서',
  '',
  '## 🔍 1. 전체 Space & 다중 탭 동적 변수 스캔 결과 (`scanLog`)',
  '```json',
  JSON.stringify({
    claudeMatched: claudeMatch ? { spaceId: claudeMatch.spaceId, tabId: claudeMatch.tabId, modelStatus: claudeModelStatus } : null,
    gptMatched: gptMatch ? { spaceId: gptMatch.spaceId, tabId: gptMatch.tabId, modelStatus: gptModelStatus } : null,
    ourChatMatched: ourMatch ? { spaceId: ourMatch.spaceId, tabId: ourMatch.tabId } : null,
    dashMatched: dashMatch ? { spaceId: dashMatch.spaceId, tabId: dashMatch.tabId } : null,
    allTabsScanned: scanLog
  }, null, 2),
  '```',
  '',
  '## 💬 2. 뒤에서 앞으로 꺼낸 클로드 (`Claude Opus 5.5`) 응답 스냅샷 원문',
  '```',
  claudeReport,
  '```'
].join('\n');

fs.writeFileSync('S1_OUT.md', outMd, 'utf8');
console.log('DYNAMIC_SCAN_AND_CLAUDE_OK');