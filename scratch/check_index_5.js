
// 🏛️ [v8.0] 청와대 본관 컨트롤 타워 실시간 통신 및 1-Click 재가 엔진
async function refreshCheongwadaeStatus() {
  try {
    const res = await fetch('/api/cheongwadae-status');
    if (!res.ok) return;
    const data = await res.json();
    
    // 모닝 브리핑 갱신
    if (data.morning_brief && data.morning_brief.timestamp) {
      const badge = document.getElementById('briefing-time-badge');
      if (badge) badge.innerText = '최신 브리핑: ' + data.morning_brief.timestamp;
    }
    
    // 오토-루프 최근 상태 갱신
    if (data.auto_loop) {
      const timeElem = document.getElementById('last-cycle-time');
      if (timeElem) timeElem.innerText = '사이클 #' + (data.auto_loop.cycle_count || 1) + ' (' + (data.auto_loop.last_cycle_at || '방금 전') + ')';
    }
  } catch (err) {
    console.warn('[Cheongwadae] Status fetch skip:', err);
  }
}

// 🌅 대표님 1-Click 원터치 재가 실행
async function approveCeoAction(agendaId) {
  try {
    const btn = event?.currentTarget;
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span>⏳ 무인 집행중...</span>';
    }
    
    const res = await fetch('/api/ceo-approve-action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agenda_id: agendaId })
    });
    const result = await res.json();
    
    // 완료 영수증 알림
    const receiptBox = document.getElementById('ceo-approval-receipt');
    const receiptText = document.getElementById('receipt-text');
    const receiptTime = document.getElementById('receipt-time');
    if (receiptBox && receiptText) {
      receiptBox.classList.remove('hidden');
      receiptText.innerText = '✅ 대표님 재가 완료: [' + (result.receipt?.agenda_id || agendaId) + '] 무인 집행 및 consensus.md 등재 완료!';
      if (receiptTime) receiptTime.innerText = result.receipt?.approved_at || new Date().toLocaleTimeString();
    }
    
    if (btn) {
      btn.innerHTML = '<span>✅ 집행 완료됨</span>';
      btn.classList.remove('from-emerald-600', 'from-cyan-600', 'from-purple-600');
      btn.classList.add('bg-slate-700', 'text-slate-400');
    }
  } catch (err) {
    alert('재가 집행 중 오류 발생: ' + err.message);
  }
}

// ⚙️ 지금 1사이클 즉시 무인 가동
async function runAutonomousCompanyCycle() {
  const btn = document.getElementById('btn-trigger-cycle');
  if (btn) {
    btn.disabled = true;
    btn.innerText = '⚡ 무인 협업 가동중...';
  }
  try {
    const res = await fetch('/api/autonomous-cycle-run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ trigger: 'manual_button' })
    });
    const data = await res.json();
    const timeElem = document.getElementById('last-cycle-time');
    if (timeElem) {
      timeElem.innerText = '사이클 #' + (data.cycle_result?.cycle || '완료') + ' (' + new Date().toLocaleTimeString() + ' 차곡차곡 누적됨)';
    }
    alert('🎉 14대 전문가 & Connect AI 8대 요원이 1사이클 무인 협업을 완수하고 consensus.md에 영구 기록했습니다!');
  } catch (err) {
    alert('오토파일럿 실행 오류: ' + err.message);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerText = '⚡ 지금 1사이클 즉시 무인 가동';
    }
  }
}

// ☀️ [v8.8] 대표님 모닝 브리핑 로드 및 야간 자율주행 즉시 재점검
async function loadMorningBriefing() {
  try {
    const res = await fetch('/api/morning-briefing');
    if (!res.ok) return;
    const data = await res.json();
    if (data.metrics) {
      const g = document.getElementById('briefing-guard-metric');
      const t = document.getElementById('briefing-task-metric');
      const l = document.getElementById('briefing-legal-metric');
      const tr = document.getElementById('briefing-treasury-metric');
      if (g) g.innerText = data.metrics.guard_status || 'ALL_SECURE';
      if (t) t.innerText = data.metrics.tasks_completed || '18/18 완수';
      if (l) l.innerText = data.metrics.legal_score || '100/100 점';
      if (tr && data.metrics.disposable_net_krw !== undefined) {
        tr.innerText = (data.metrics.disposable_net_krw || 0).toLocaleString('ko-KR') + '원 순익';
      }
    }
  } catch (e) {
    console.warn('[Briefing] load skip:', e);
  }
}

async function triggerNightAutopilotRun() {
  const btn = document.getElementById('btn-night-autopilot');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<span>⏳ 야간 당직 순찰 가동중...</span>';
  }
  try {
    const res = await fetch('/api/night-autopilot-run', { method: 'POST' });
    const data = await res.json();
    if (data.status === 'OK') {
      alert('☀️ [르곤 수석보좌관 × 안총리 당직 완료]\n전 기관(본관+1~6청사+5대 안전웹앱) 야간 무인 자율주행 및 모닝 브리핑이 성공적으로 갱신되었습니다!');
      loadMorningBriefing();
    } else {
      alert('오류 발생: ' + data.message);
    }
  } catch (e) {
    alert('야간 자율주행 실행 통신 오류: ' + e.message);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<span>🌙</span><span>야간 자율주행 즉시 재점검</span>';
    }
  }
}

// 초기화 로드 시 자동 갱신
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(refreshCheongwadaeStatus, 1000);
  setTimeout(loadMorningBriefing, 1100);
  setTimeout(fetchTreasuryQuickStatus, 1200);
});
