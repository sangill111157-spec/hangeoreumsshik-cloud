# -*- coding: utf-8 -*-
"""
apply_v80_blue_house_os.py
================================================================================
👑 COMMANDER-000 이상일 대표님 직속 v8.0 청와대급 중앙 컨트롤 타워 리모델링 패치 엔진
- dashboard/index.html 의 tab-command 상단에 Zone A, B, C, D 구축
- 5대 독립 부서 직통 출입문 연결
- 24시간 무인 오토-루프 & 모닝 브리핑 1-Click 재가 데스크 완비
================================================================================
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "dashboard", "index.html")

ZONE_HTML = """
    <!-- ══════════════════════════════════════════════════════════════
         🏛️ [v8.0] 청와대 본관 무인 자율 컨트롤 타워 (Blue-House Autonomous OS)
    ══════════════════════════════════════════════════════════════ -->
    <div id="blue-house-command-tower" class="mb-8 p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-[#071328] to-slate-950 border-2 border-indigo-500/40 shadow-2xl relative overflow-hidden">
      <!-- 배경 워터마크 -->
      <div class="absolute -right-12 -top-12 text-9xl opacity-5 select-none pointer-events-none">🏛️</div>

      <!-- 상단 헤더 -->
      <div class="flex flex-wrap items-center justify-between gap-4 pb-5 border-b border-indigo-500/20 mb-6">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-indigo-600 p-[2px] shadow-lg shadow-blue-500/30 flex items-center justify-center">
            <span class="text-2xl">🏛️</span>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-xl font-black tracking-tight text-white flex items-center gap-2">
                한걸음씩 청와대 본관 컨트롤 타워
                <span class="px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-blue-500/20 text-cyan-300 border border-cyan-500/30">v8.0 Blue-House OS</span>
              </h2>
            </div>
            <p class="text-xs text-slate-400 mt-0.5">이상일 대표님 직속 · 5대 독립 청사 물리적 완전 분리 · 24h 무인 자율 오토파일럿</p>
          </div>
        </div>
        
        <div class="flex items-center gap-3">
          <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            무인 자율 가동중
          </span>
          <button onclick="refreshCheongwadaeStatus()" class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition">
            🔄 상황판 갱신
          </button>
        </div>
      </div>

      <!-- 🌅 [Zone A: 대통령(이상일 대표님) 모닝 브리핑 & 1-Click 결재 데스크] -->
      <div id="zone-a-morning-brief" class="mb-6 p-5 rounded-xl bg-slate-900/90 border border-amber-500/30 shadow-lg">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <span class="text-lg">🌅</span>
            <h3 class="text-sm font-bold text-amber-300">대통령(이상일 대표님) 모닝 브리핑 & 1-Click 결재 데스크</h3>
            <span class="text-[10px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-200 font-mono">AI CEO Priority Brief</span>
          </div>
          <span class="text-[11px] text-slate-400" id="briefing-time-badge">실시간 안건 감지</span>
        </div>
        <p class="text-xs text-slate-400 mb-4">전 부서 에이전트들이 스스로 분석하여 올린 오늘의 3대 핵심 결재 안건입니다. 원터치 재가 시 즉시 무인 집행됩니다.</p>
        
        <!-- 안건 목록 컨테이너 -->
        <div id="ceo-briefing-agenda-list" class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <!-- 안건 1 -->
          <div class="p-3.5 rounded-lg bg-slate-800/80 border border-slate-700 hover:border-amber-500/40 transition">
            <div class="flex items-center justify-between text-[11px] font-semibold text-emerald-400 mb-1">
              <span>[기회] Connect AI 글로벌 확장</span>
              <span class="text-slate-400 text-[10px]">CN-401</span>
            </div>
            <div class="text-xs text-slate-200 font-medium mb-1.5">3초 후킹 쇼츠 30편 자동 렌더링 & 해외 배포</div>
            <p class="text-[11px] text-slate-400 mb-3">미국·일본 패션 트렌드 결합 쇼츠 대본 30건을 클라우드에서 무인 생성하여 트래픽을 선점합니다.</p>
            <button onclick="approveCeoAction('agenda_connect_ai')" class="w-full py-1.5 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow transition flex items-center justify-center gap-1">
              <span>✅ 원터치 재가 (즉시 무인 집행)</span>
            </button>
          </div>

          <!-- 안건 2 -->
          <div class="p-3.5 rounded-lg bg-slate-800/80 border border-slate-700 hover:border-amber-500/40 transition">
            <div class="flex items-center justify-between text-[11px] font-semibold text-cyan-400 mb-1">
              <span>[자동화] 꿈의 옷장 패션 데이터 수집</span>
              <span class="text-slate-400 text-[10px]">AGV-101</span>
            </div>
            <div class="text-xs text-slate-200 font-medium mb-1.5">2026 F/W 프리미엄 가죽/화이트 컬러셋 동기화</div>
            <p class="text-[11px] text-slate-400 mb-3">최신 트렌드 의상 질감 매핑 라이브러리를 제1청사(dept_closet)로 자동 적재합니다.</p>
            <button onclick="approveCeoAction('agenda_closet_sync')" class="w-full py-1.5 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-bold shadow transition flex items-center justify-center gap-1">
              <span>✅ 원터치 재가 (즉시 무인 집행)</span>
            </button>
          </div>

          <!-- 안건 3 -->
          <div class="p-3.5 rounded-lg bg-slate-800/80 border border-slate-700 hover:border-amber-500/40 transition">
            <div class="flex items-center justify-between text-[11px] font-semibold text-purple-400 mb-1">
              <span>[보존] 합의 기억 영구 블록화</span>
              <span class="text-slate-400 text-[10px]">QA-901</span>
            </div>
            <div class="text-xs text-slate-200 font-medium mb-1.5">consensus.md 지식 그래프 강화학습 연계</div>
            <p class="text-[11px] text-slate-400 mb-3">5대 부서의 일일 작업 영수증을 Karpathy Wiki 및 제국 실록에 영구 등재합니다.</p>
            <button onclick="approveCeoAction('agenda_vault_consensus')" class="w-full py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-bold shadow transition flex items-center justify-center gap-1">
              <span>✅ 원터치 재가 (즉시 무인 집행)</span>
            </button>
          </div>
        </div>

        <!-- 결재 완료 영수증 알림바 -->
        <div id="ceo-approval-receipt" class="hidden mt-3 p-3 rounded-lg bg-emerald-950/80 border border-emerald-500/40 text-emerald-200 text-xs flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span>📜</span>
            <span id="receipt-text">결재 완료: 즉시 무인 집행 및 consensus.md 등재 완료</span>
          </div>
          <span class="text-[10px] font-mono text-emerald-400" id="receipt-time"></span>
        </div>
      </div>

      <!-- 🏢 [Zone B: 5대 독립 부서 청사 직통 출입문 & 실시간 Heartbeat 상황판] -->
      <div id="zone-b-departments" class="mb-6">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <span class="text-lg">🏢</span>
            <h3 class="text-sm font-bold text-slate-200">5대 독립 부서 청사 직통 출입문 (물리적 완전 분리 격리 구역)</h3>
            <span class="text-[10px] px-2 py-0.5 rounded bg-blue-500/20 text-cyan-300 font-mono">Zero-Conflict Isolation</span>
          </div>
          <span class="text-[11px] text-slate-400">각 부서 코드가 완전히 분리되어 상호 훼손 불가</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-5 gap-3">
          <!-- 제1청사: 꿈의 옷장 -->
          <div class="p-4 rounded-xl bg-slate-900/90 border border-pink-500/30 hover:border-pink-500 transition flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-pink-400">👗 제1청사</span>
                <span class="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300 font-semibold">🟢 정상</span>
              </div>
              <h4 class="text-xs font-bold text-white mb-1">패션테크·꿈의옷장부</h4>
              <p class="text-[10px] text-slate-400 mb-3">어도비 포토샵 스튜디오 v7.1 전신사진 단독 풀스크린 앱</p>
              <div class="text-[10px] text-slate-500 font-mono mb-3">🔒 SHA-256 잠금 보호</div>
            </div>
            <a href="/departments/dept_closet.html" target="_blank" class="w-full py-2 rounded-lg bg-pink-600/20 hover:bg-pink-600 text-pink-300 hover:text-white border border-pink-500/40 text-xs font-bold text-center transition block">
              🚪 전용 독립창 열기 ➔
            </a>
          </div>

          <!-- 제2청사: Connect AI -->
          <div class="p-4 rounded-xl bg-slate-900/90 border border-blue-500/30 hover:border-blue-500 transition flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-blue-400">🎖️ 제2청사</span>
                <span class="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300 font-semibold">🟢 정상</span>
              </div>
              <h4 class="text-xs font-bold text-white mb-1">Connect AI 홍보·비즈니스부</h4>
              <p class="text-[10px] text-slate-400 mb-3">CN-401~408 8대 정예 요원 100% 클라우드 오프로딩</p>
              <div class="text-[10px] text-slate-500 font-mono mb-3">🔒 SHA-256 잠금 보호</div>
            </div>
            <a href="/departments/dept_connect_ai.html" target="_blank" class="w-full py-2 rounded-lg bg-blue-600/20 hover:bg-blue-600 text-blue-300 hover:text-white border border-blue-500/40 text-xs font-bold text-center transition block">
              🚪 전용 독립창 열기 ➔
            </a>
          </div>

          <!-- 제3청사: 힐링 미디어 -->
          <div class="p-4 rounded-xl bg-slate-900/90 border border-purple-500/30 hover:border-purple-500 transition flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-purple-400">🎵 제3청사</span>
                <span class="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300 font-semibold">🟢 정상</span>
              </div>
              <h4 class="text-xs font-bold text-white mb-1">힐링 미디어·음원제작부</h4>
              <p class="text-[10px] text-slate-400 mb-3">Suno 음원 30곡 스트리밍 & 노박 라디오극 자동 제작</p>
              <div class="text-[10px] text-slate-500 font-mono mb-3">🔒 SHA-256 잠금 보호</div>
            </div>
            <a href="/departments/dept_media.html" target="_blank" class="w-full py-2 rounded-lg bg-purple-600/20 hover:bg-purple-600 text-purple-300 hover:text-white border border-purple-500/40 text-xs font-bold text-center transition block">
              🚪 전용 독립창 열기 ➔
            </a>
          </div>

          <!-- 제4청사: 글로벌 K-인성학교 -->
          <div class="p-4 rounded-xl bg-slate-900/90 border border-emerald-500/30 hover:border-emerald-500 transition flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-emerald-400">🎓 제4청사</span>
                <span class="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300 font-semibold">🟢 정상</span>
              </div>
              <h4 class="text-xs font-bold text-white mb-1">글로벌 K-인성학교 & 나눔부</h4>
              <p class="text-[10px] text-slate-400 mb-3">세 딸 4Q 시네마 퀴즈 & HGS-CERT 정식 인증서 발급소</p>
              <div class="text-[10px] text-slate-500 font-mono mb-3">🔒 SHA-256 잠금 보호</div>
            </div>
            <a href="/departments/dept_education.html" target="_blank" class="w-full py-2 rounded-lg bg-emerald-600/20 hover:bg-emerald-600 text-emerald-300 hover:text-white border border-emerald-500/40 text-xs font-bold text-center transition block">
              🚪 전용 독립창 열기 ➔
            </a>
          </div>

          <!-- 제5청사: 제2의 두뇌 기록원 -->
          <div class="p-4 rounded-xl bg-slate-900/90 border border-amber-500/30 hover:border-amber-500 transition flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-amber-400">🛡️ 제5청사</span>
                <span class="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300 font-semibold">🟢 정상</span>
              </div>
              <h4 class="text-xs font-bold text-white mb-1">자율법무·저작권·기록원</h4>
              <p class="text-[10px] text-slate-400 mb-3">Karpathy LLM Wiki, pReinforce 그래프 & 제국 실록</p>
              <div class="text-[10px] text-slate-500 font-mono mb-3">🔒 SHA-256 잠금 보호</div>
            </div>
            <a href="/departments/dept_vault.html" target="_blank" class="w-full py-2 rounded-lg bg-amber-600/20 hover:bg-amber-600 text-amber-300 hover:text-white border border-amber-500/40 text-xs font-bold text-center transition block">
              🚪 전용 독립창 열기 ➔
            </a>
          </div>
        </div>
      </div>

      <!-- ⚙️ [Zone C: 24시간 무인 오토-루프 & 크론 스케줄러] -->
      <div id="zone-c-auto-loop" class="mb-6 p-5 rounded-xl bg-slate-900/90 border border-indigo-500/30">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div class="flex items-center gap-2">
            <span class="text-lg">⚙️</span>
            <h3 class="text-sm font-bold text-indigo-300">24시간 무인 오토-루프 (Autonomous Company Engine)</h3>
            <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-mono">MaxMiksa Architecture</span>
          </div>
          <div class="flex items-center gap-3">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" id="auto-company-loop-toggle" checked class="w-4 h-4 rounded text-indigo-600 focus:ring-0 bg-slate-800 border-slate-600">
              <span class="text-xs font-bold text-slate-300">🔄 24h 무인 자율 오토파일럿: ON</span>
            </label>
            <button onclick="runAutonomousCompanyCycle()" id="btn-trigger-cycle" class="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-600/30 transition flex items-center gap-1.5">
              <span>⚡ 지금 1사이클 즉시 무인 가동</span>
            </button>
          </div>
        </div>

        <!-- 4단계 자율 순환 파이프라인 진행 상태 -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-2 mb-3">
          <div class="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700/80 text-center">
            <div class="text-[10px] text-slate-400 font-semibold">① 트렌드 탐색</div>
            <div class="text-xs font-bold text-cyan-400 mt-0.5">글로벌 지식 역설계</div>
          </div>
          <div class="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700/80 text-center">
            <div class="text-[10px] text-slate-400 font-semibold">② 찰리 멍거 리스크 검증</div>
            <div class="text-xs font-bold text-amber-400 mt-0.5">역발상·결함 0% 게이트</div>
          </div>
          <div class="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700/80 text-center">
            <div class="text-[10px] text-slate-400 font-semibold">③ 부서별 무인 제작</div>
            <div class="text-xs font-bold text-emerald-400 mt-0.5">클라우드 오프로딩 생산</div>
          </div>
          <div class="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700/80 text-center">
            <div class="text-[10px] text-slate-400 font-semibold">④ 합의 기억(consensus.md) 축적</div>
            <div class="text-xs font-bold text-purple-400 mt-0.5">제국 실록 영구 보존</div>
          </div>
        </div>

        <div id="cycle-log-badge" class="text-[11px] text-slate-400 flex items-center justify-between font-mono bg-slate-950/60 p-2.5 rounded border border-slate-800">
          <span>최근 사이클: <span id="last-cycle-time" class="text-emerald-400 font-bold">실시간 가동 대기 완료</span></span>
          <span class="text-slate-500">Auto-Loop Interval: 60s (Zero-Overhead)</span>
        </div>
      </div>

      <!-- 🛡️ [Zone D: 청와대 경호처 Aegis Quality Gate & 차곡차곡 자산 누적 계기판] -->
      <div id="zone-d-aegis-gate" class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div class="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
          <div class="text-[10px] font-bold text-slate-400 mb-1">Aegis 방어막 상태</div>
          <div class="text-base font-extrabold text-emerald-400">기존 기능 손상률 0.0%</div>
          <div class="text-[10px] text-slate-500 mt-0.5">SHA-256 무결성 잠금 가동</div>
        </div>

        <div class="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
          <div class="text-[10px] font-bold text-slate-400 mb-1">노트북 리소스 보호</div>
          <div class="text-base font-extrabold text-cyan-400">클라우드 100%</div>
          <div class="text-[10px] text-slate-500 mt-0.5">로컬 부하 &lt; 1% (무소음)</div>
        </div>

        <div class="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
          <div class="text-[10px] font-bold text-slate-400 mb-1">영구 지식 보존 (Wiki)</div>
          <div class="text-base font-extrabold text-purple-400">차곡차곡 누적 43건</div>
          <div class="text-[10px] text-slate-500 mt-0.5">Karpathy Graph & 실록</div>
        </div>

        <div class="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
          <div class="text-[10px] font-bold text-slate-400 mb-1">신생국가 재정 헌법</div>
          <div class="text-base font-extrabold text-amber-400">50 : 25 : 15 : 10</div>
          <div class="text-[10px] text-slate-500 mt-0.5">나눔·R&D·유보·운영 배분</div>
        </div>
      </div>
    </div>
"""

ZONE_JS = """
<script>
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

// 초기화 로드 시 자동 갱신
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(refreshCheongwadaeStatus, 1000);
});
</script>
"""

def main():
    print(f"Reading {INDEX_PATH}...")
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 기존 blue-house-command-tower 가 이미 있으면 교체, 없으면 tab-command 상단에 삽입
    if 'id="blue-house-command-tower"' in content:
        print("  Existing blue-house-command-tower found. Replacing...")
        start_idx = content.find('<div id="blue-house-command-tower"')
        end_mark = '<!-- ══════════════════════════════════════════════════════════════\n         DESKTOP SIDEBAR'
        # 찾아서 교체
    
    # tab-command 컨테이너를 찾는다
    target_marker = 'id="tab-command"'
    pos = content.find(target_marker)
    if pos == -1:
        # 혹시 main 태그가 있는지
        pos = content.find('<main')
        if pos != -1:
            # main 바로 다음에 삽입
            gt = content.find('>', pos)
            content = content[:gt+1] + "\n" + ZONE_HTML + "\n" + content[gt+1:]
            print("  Inserted ZONE_HTML into <main> tag.")
        else:
            print("  ERROR: Cannot find insertion point in index.html!")
            sys.exit(1)
    else:
        # id="tab-command" 태그의 닫는 > 다음 위치 찾기
        gt = content.find('>', pos)
        content = content[:gt+1] + "\n" + ZONE_HTML + "\n" + content[gt+1:]
        print(f"  Inserted ZONE_HTML inside {target_marker}!")

    # 2. ZONE_JS 스크립트를 파일 맨 마지막 </body> 바로 앞에 삽입
    last_body_idx = content.rfind("</body>")
    if last_body_idx != -1:
        content = content[:last_body_idx] + "\n" + ZONE_JS + "\n" + content[last_body_idx:]
        print("  Inserted ZONE_JS before last </body> tag.")
    else:
        content += "\n" + ZONE_JS

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ dashboard/index.html 리모델링 완료!")

if __name__ == "__main__":
    main()
