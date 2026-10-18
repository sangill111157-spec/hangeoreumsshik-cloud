// aside_drawer.js - 🧠 르곤 어사이드(Rgon-Aside) 우측 슬라이드 지휘 서랍 공통 모듈
// [v11.3-RGON-ASIDE-AGENTIC-BROWSER-ABSORPTION]
// 100% 한글 UI · 모바일 360px 시야 가림 0% · Vault 보안 자동 연동 · 유료 구독료 0원

(function() {
  // 현재 페이지 식별자 추출
  function detectCurrentPage() {
    const p = window.location.pathname.toLowerCase();
    if (p.includes('dept_closet')) return 'dept_closet';
    if (p.includes('dept_connect_ai')) return 'dept_connect_ai';
    if (p.includes('dept_media')) return 'dept_media';
    if (p.includes('dept_education')) return 'dept_education';
    if (p.includes('dept_vault')) return 'dept_vault';
    if (p.includes('dept_treasury')) return 'dept_treasury';
    return 'command_main';
  }

  // CSS 스타일 주입
  function injectAsideStyles() {
    if (document.getElementById('rgon-aside-styles')) return;
    const style = document.createElement('style');
    style.id = 'rgon-aside-styles';
    style.textContent = `
      #rgon-aside-fab {
        position: fixed;
        right: 0;
        top: 45%;
        transform: translateY(-50%);
        z-index: 9998;
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.95), rgba(217, 119, 6, 0.95));
        color: #ffffff;
        font-weight: 800;
        font-size: 12px;
        padding: 10px 10px 10px 14px;
        border-radius: 20px 0 0 20px;
        box-shadow: -2px 4px 16px rgba(245, 158, 11, 0.4), 0 0 0 1px rgba(254, 243, 199, 0.3);
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 5px;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        user-select: none;
      }
      #rgon-aside-fab:hover {
        padding-left: 18px;
        background: linear-gradient(135deg, #f59e0b, #b45309);
        box-shadow: -4px 6px 20px rgba(245, 158, 11, 0.6);
      }
      #rgon-aside-backdrop {
        position: fixed;
        inset: 0;
        background: rgba(3, 7, 18, 0.6);
        backdrop-filter: blur(4px);
        z-index: 9998;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
      }
      #rgon-aside-backdrop.active {
        opacity: 1;
        pointer-events: auto;
      }
      #rgon-aside-drawer {
        position: fixed;
        top: 0;
        right: -100%;
        width: 100%;
        max-width: 410px;
        height: 100vh;
        background: linear-gradient(180deg, rgba(11, 19, 43, 0.97) 0%, rgba(3, 7, 18, 0.98) 100%);
        border-left: 1px solid rgba(245, 158, 11, 0.3);
        box-shadow: -10px 0 35px rgba(0, 0, 0, 0.7);
        z-index: 9999;
        display: flex;
        flex-direction: column;
        transition: right 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        overflow: hidden;
      }
      #rgon-aside-drawer.active {
        right: 0;
      }
      .aside-scrollbar::-webkit-scrollbar {
        width: 5px;
      }
      .aside-scrollbar::-webkit-scrollbar-thumb {
        background: rgba(245, 158, 11, 0.3);
        border-radius: 4px;
      }
    `;
    document.head.appendChild(style);
  }

  // DOM 마크업 주입
  function injectAsideDOM() {
    if (document.getElementById('rgon-aside-fab')) return;

    // 플로팅 호출 버튼
    const fab = document.createElement('div');
    fab.id = 'rgon-aside-fab';
    fab.innerHTML = '<span>🧠</span><span>어사이드</span>';
    fab.title = '🧠 르곤 어사이드 AI 브라우저 부관 열기';
    fab.onclick = toggleAsideDrawer;

    // 백드롭
    const backdrop = document.createElement('div');
    backdrop.id = 'rgon-aside-backdrop';
    backdrop.onclick = closeAsideDrawer;

    // 슬라이드 서랍 본체
    const drawer = document.createElement('aside');
    drawer.id = 'rgon-aside-drawer';
    drawer.innerHTML = `
      <!-- 헤더 -->
      <div style="padding: 16px 18px; border-bottom: 1px solid rgba(245, 158, 11, 0.25); background: rgba(15, 23, 42, 0.8); display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 20px;">🧠</span>
          <div>
            <div style="font-weight: 800; font-size: 14px; color: #f8fafc; letter-spacing: -0.02em;">르곤 어사이드 (Rgon-Aside)</div>
            <div style="font-size: 11px; color: #fbbf24; display: flex; align-items: center; gap: 4px;">
              <span style="width: 6px; height: 6px; border-radius: 50%; background: #10b981; display: inline-block;"></span>
              <span>Vault 보안 가동 (마스킹 100%)</span>
            </div>
          </div>
        </div>
        <button id="btn-aside-close" onclick="window.closeAsideDrawer()" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #cbd5e1; border-radius: 8px; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 13px;">✕</button>
      </div>

      <!-- 본문 스크롤 영역 -->
      <div class="aside-scrollbar" style="flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 14px;">
        
        <!-- 섹션 1: 현재 화면 문맥 X-Ray 카드 -->
        <div style="padding: 12px; border-radius: 12px; background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(59, 130, 246, 0.3);">
          <div style="font-size: 11px; color: #60a5fa; font-weight: 700; margin-bottom: 4px; display: flex; align-items: center; justify-content: space-between;">
            <span>🔍 현재 화면 X-Ray 자동 브리핑</span>
            <span id="aside-xray-dept-tag" style="padding: 2px 6px; border-radius: 4px; background: #1e3a8a; color: #bfdbfe; font-size: 10px;">감지중</span>
          </div>
          <div id="aside-xray-title" style="font-weight: 700; font-size: 13px; color: #ffffff; margin-bottom: 4px;">화면을 분석하고 있습니다...</div>
          <div id="aside-xray-summary" style="font-size: 11px; color: #94a3b8; line-height: 1.4;">잠시만 기다려주세요.</div>
        </div>

        <!-- 섹션 2: 원터치 에이전트 액션 칩 4종 -->
        <div style="display: flex; flex-direction: column; gap: 6px;">
          <div style="font-size: 11px; font-weight: 700; color: #f59e0b; margin-left: 2px;">⚡ 원터치 어사이드 에이전트 출격</div>
          
          <button onclick="window.triggerAsideAction('MULTI_7_CHANNEL_AUTOFILL')" style="width: 100%; text-align: left; padding: 10px 12px; border-radius: 10px; background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.25)); border: 1px solid rgba(245, 158, 11, 0.4); color: #fef3c7; font-size: 12px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
            <span>🚀 7대 채널(유튜브3·틱톡·SNS) 서브에이전트 동시 자동채움</span>
            <span>➔</span>
          </button>

          <button onclick="window.triggerAsideAction('CONTEXT_XRAY')" style="width: 100%; text-align: left; padding: 10px 12px; border-radius: 10px; background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.35); color: #dbeafe; font-size: 12px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
            <span>🔍 현재 화면 정밀 엑스레이 요약 & 텔레그램 보고</span>
            <span>➔</span>
          </button>

          <button onclick="window.triggerAsideAction('INSTANT_SYNERGY_BOOST')" style="width: 100%; text-align: left; padding: 10px 12px; border-radius: 10px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35); color: #d1fae5; font-size: 12px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
            <span>🤝 현 청사 ➔ 전 기관 즉시 바통터치(릴레이) 발동</span>
            <span>➔</span>
          </button>

          <button onclick="window.triggerAsideAction('VIEW_ARTIFACTS')" style="width: 100%; text-align: left; padding: 10px 12px; border-radius: 10px; background: rgba(139, 92, 246, 0.15); border: 1px solid rgba(139, 92, 246, 0.35); color: #ede9fe; font-size: 12px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
            <span>📂 로컬 메모리 & 아티팩트 작업 영수증 열람</span>
            <span>➔</span>
          </button>
        </div>

        <!-- 섹션 3: 자연어 지시창 -->
        <div style="padding: 12px; border-radius: 12px; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(148, 163, 184, 0.2); display: flex; flex-direction: column; gap: 8px;">
          <div style="font-size: 11px; font-weight: 700; color: #cbd5e1;">💬 말로 시키는 자연어 지시창</div>
          <input id="aside-prompt-input" type="text" placeholder="여기에 시키실 일을 입력하면 즉시 실행합니다..." style="width: 100%; padding: 8px 10px; border-radius: 8px; background: rgba(3, 7, 18, 0.8); border: 1px solid rgba(148, 163, 184, 0.3); color: #ffffff; font-size: 11px; outline: none; box-sizing: border-box;" />
          <button id="btn-aside-prompt-run" onclick="window.runAsidePromptCommand()" style="width: 100%; padding: 8px; border-radius: 8px; background: linear-gradient(135deg, #0284c7, #2563eb); border: none; color: #ffffff; font-weight: 700; font-size: 11px; cursor: pointer;">
            ⚡ 즉시 실행 (자율 에이전트 가동)
          </button>
        </div>

        <!-- 섹션 4: 실시간 작동 결과 & 7대 채널 카드 출력창 -->
        <div id="aside-results-box" style="display: flex; flex-direction: column; gap: 8px;">
          <div style="font-size: 11px; font-weight: 700; color: #94a3b8;">📱 서브 에이전트 7대 채널 자동 채움 카드</div>
          <div id="aside-channels-list" style="display: flex; flex-direction: column; gap: 6px; font-size: 11px;">
            <div style="padding: 10px; border-radius: 8px; background: rgba(30, 41, 59, 0.4); color: #94a3b8; text-align: center;">
              상단의 [🚀 7대 채널 동시 자동채움] 버튼을 누르면 7기 서브에이전트가 즉시 카드를 펼칩니다.
            </div>
          </div>
        </div>

      </div>

      <!-- 하단 상태 푸터 -->
      <div style="padding: 10px 14px; border-top: 1px solid rgba(255, 255, 255, 0.08); background: rgba(3, 7, 18, 0.9); font-size: 10px; color: #64748b; display: flex; justify-content: space-between; align-items: center;">
        <span>청와대 AI OS v11.3 Aside</span>
        <span style="color: #10b981;">● 실전금고 0원 불변</span>
      </div>
    `;

    document.body.appendChild(backdrop);
    document.body.appendChild(drawer);
    document.body.appendChild(fab);
  }

  // 서랍 열기/닫기
  function toggleAsideDrawer() {
    const drawer = document.getElementById('rgon_aside_drawer') || document.getElementById('rgon-aside-drawer');
    const backdrop = document.getElementById('rgon-aside-backdrop');
    if (!drawer) return;
    const isOpen = drawer.classList.contains('active');
    if (isOpen) {
      closeAsideDrawer();
    } else {
      openAsideDrawer();
    }
  }
  window.toggleAsideDrawer = toggleAsideDrawer;

  function openAsideDrawer() {
    const drawer = document.getElementById('rgon-aside-drawer');
    const backdrop = document.getElementById('rgon-aside-backdrop');
    if (drawer) drawer.classList.add('active');
    if (backdrop) backdrop.classList.add('active');
    loadAsideStatus();
  }
  window.openAsideDrawer = openAsideDrawer;

  function closeAsideDrawer() {
    const drawer = document.getElementById('rgon-aside-drawer');
    const backdrop = document.getElementById('rgon-aside-backdrop');
    if (drawer) drawer.classList.remove('active');
    if (backdrop) backdrop.classList.remove('active');
  }
  window.closeAsideDrawer = closeAsideDrawer;

  // 상태 로드 및 X-Ray 바인딩
  async function loadAsideStatus() {
    try {
      const pageId = detectCurrentPage();
      const res = await fetch('/api/aside-status?page=' + pageId + '&t=' + Date.now());
      if (!res.ok) return;
      const data = await res.json();
      const ctx = data.context_xray;
      if (ctx) {
        const tag = document.getElementById('aside-xray-dept-tag');
        const title = document.getElementById('aside-xray-title');
        const summary = document.getElementById('aside-xray-summary');
        if (tag) tag.innerText = ctx.dept_id || 'MAIN';
        if (title) title.innerText = ctx.name || '화면 감지 완료';
        if (summary) summary.innerText = ctx.summary || '';
      }
    } catch (e) {
      console.warn('Aside status load error:', e);
    }
  }
  window.loadAsideStatus = loadAsideStatus;

  // 원터치 액션 트리거
  async function triggerAsideAction(mode) {
    const pageId = detectCurrentPage();
    const btnClose = document.getElementById('btn-aside-close');
    const channelsBox = document.getElementById('aside-channels-list');
    
    if (channelsBox) {
      channelsBox.innerHTML = '<div style="padding: 12px; color: #fbbf24; text-align: center; font-weight: 700;">⏳ 르곤 어사이드 서브 에이전트 동시 작업 중...</div>';
    }

    try {
      const res = await fetch('/api/aside-execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: mode, page_id: pageId })
      });
      const data = await res.json();
      const payload = data.data || data;

      if (payload.sub_agents_results && channelsBox) {
        renderChannelsResults(payload.sub_agents_results, payload.receipt_id, payload.artifact_filename);
      }

      alert(`🧠 [르곤 어사이드 작업 완수!]\n\n• 영수증: ${payload.receipt_id}\n• 실행 모드: ${mode}\n• 출격 에이전트: ${payload.sub_agents_count || 7}기 전원 완료\n• 대표님 스마트폰 텔레그램 발송 완료!`);
    } catch (err) {
      alert('어사이드 실행 오류: ' + err.message);
    }
  }
  window.triggerAsideAction = triggerAsideAction;

  // 자연어 프롬프트 실행
  async function runAsidePromptCommand() {
    const input = document.getElementById('aside-prompt-input');
    const val = input ? input.value.trim() : '';
    if (!val) {
      alert('어사이드 에이전트에게 내리실 지시를 입력해주세요.');
      return;
    }
    const pageId = detectCurrentPage();
    try {
      const res = await fetch('/api/aside-execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: 'CUSTOM_VOICE_COMMAND', page_id: pageId, prompt: val })
      });
      const data = await res.json();
      const payload = data.data || data;
      if (payload.sub_agents_results) {
        renderChannelsResults(payload.sub_agents_results, payload.receipt_id, payload.artifact_filename);
      }
      alert(`⚡ [어사이드 지시 완수!]\n\n• 명령: ${val}\n• 영수증: ${payload.receipt_id}\n• 결과가 서랍에 펼쳐졌습니다.`);
      if (input) input.value = '';
    } catch (e) {
      alert('어사이드 지시 실행 오류: ' + e.message);
    }
  }
  window.runAsidePromptCommand = runAsidePromptCommand;

  // 7대 채널 결과 렌더링
  function renderChannelsResults(channels, receiptId, artifactName) {
    const box = document.getElementById('aside-channels-list');
    if (!box) return;

    let html = `
      <div style="padding: 6px 8px; border-radius: 6px; background: rgba(16, 185, 129, 0.2); border: 1px solid rgba(16, 185, 129, 0.4); color: #a7f3d0; font-weight: 700; margin-bottom: 4px;">
        ✅ 영수증: ${receiptId} (${channels.length}기 출격 완료)
      </div>
    `;

    channels.forEach(ch => {
      const p = ch.autofill_payload || {};
      const intentBtn = p.threads_intent_url ? `
        <a href="${p.threads_intent_url}" target="_blank" style="display: inline-block; padding: 4px 8px; border-radius: 6px; background: #22c55e; color: #ffffff; font-weight: 700; text-decoration: none; font-size: 10px; margin-top: 4px;">
          🚀 스레드 원터치 즉시 포스팅 ➔
        </a>
      ` : '';

      html += `
        <div style="padding: 8px 10px; border-radius: 8px; background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(245, 158, 11, 0.3);">
          <div style="font-weight: 700; color: #fbbf24; display: flex; justify-content: space-between;">
            <span>${ch.channel_name}</span>
            <span style="font-size: 10px; color: #10b981;">자동채움 완료</span>
          </div>
          <div style="color: #f1f5f9; font-weight: 600; margin-top: 2px;">${p.title || ''}</div>
          <div style="color: #94a3b8; font-size: 10px; margin-top: 2px;">${(p.body || '').substring(0, 50)}...</div>
          ${intentBtn}
        </div>
      `;
    });

    box.innerHTML = html;
  }

  // 초기화
  function initAsideDrawer() {
    injectAsideStyles();
    injectAsideDOM();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAsideDrawer);
  } else {
    initAsideDrawer();
  }
})();
