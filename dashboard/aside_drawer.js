/* [RGON-SHADOW-OPEN-START] */
;(function () {
  try {
    if (typeof Element === 'undefined' || !Element.prototype.attachShadow) return;
    if (Element.prototype.__rgonShadowPatched) return;
    var orig = Element.prototype.attachShadow;
    Object.defineProperty(Element.prototype, '__rgonShadowPatched', { value: true });
    Element.prototype.attachShadow = function (init) {
      var opts = Object.assign({}, init || {}, { mode: 'open' });
      return orig.call(this, opts);
    };
  } catch (e) {}
})();
/* [RGON-SHADOW-OPEN-END] */
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
      #rgon-aside-fab.chat-compact {
        top: auto; bottom: 92px !important;
        transform: none !important;
        font-size: 11px !important;
        padding: 6px 10px !important;
        opacity: 0.85 !important;
        border-radius: 12px 0 0 12px !important;
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
    if (window.location.pathname.toLowerCase().includes('rgon_alpha_chat')) {
      fab.classList.add('chat-compact');
    }
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
            <div style="font-size: 11px; color: #a5b4fc; display: flex; align-items: center; gap: 4px; margin-top: 2px;">
              <span style="width: 6px; height: 6px; border-radius: 50%; background: #6366f1; display: inline-block;"></span>
              <span style="font-weight: 700;">🛰️ 대시보드 총괄: 르곤-알파(RGON-ALPHA) 상주 중</span>
            </div>
          </div>
        </div>
        <div style="display:flex; align-items:center; gap:6px;">
          <button id="btn-aside-header-alpha-chat" onclick="window.goToAlphaChat()" title="1:1 독대실 바로가기" style="background: rgba(245,158,11,0.2); border: 1px solid rgba(245,158,11,0.4); color: #fef08a; border-radius: 8px; padding: 4px 8px; cursor: pointer; font-size: 11px; font-weight: 700; display: flex; align-items: center; gap: 4px;">
            <span>💬</span><span>독대실</span>
          </button>
          <button id="btn-aside-close" onclick="window.closeAsideDrawer()" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #cbd5e1; border-radius: 8px; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 13px;">✕</button>
        </div>
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

        <!-- 섹션 2: 원터치 에이전트 액션 칩 5종 -->
        <div style="display: flex; flex-direction: column; gap: 6px;">
          <!-- 💻 [v12.2] 노트북 6대 멀티탭 워크스페이스 일괄 가동 -->
          <button id="btn-aside-multitab-allinone" onclick="window.triggerAsideAllInOneMultitab()" style="width: 100%; text-align: left; padding: 11px 12px; border-radius: 10px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.25), rgba(5, 150, 105, 0.35)); border: 1.5px solid rgba(16, 185, 129, 0.6); color: #a7f3d0; font-size: 12px; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);">
            <span style="display:flex; align-items:center; gap:6px;">
              <span>💻</span>
              <span>노트북 6대 멀티탭 워크스페이스 일괄 가동</span>
            </span>
            <span style="background:rgba(16, 185, 129, 0.3); padding:2px 8px; border-radius:12px; font-size:10px; color:#fff;">올인원 ➔</span>
          </button>

          <!-- 👑 르곤-알파 1:1 전담 독대실 바로가기 -->
          <button id="btn-aside-goto-alpha-chat" onclick="window.goToAlphaChat()" style="width: 100%; text-align: left; padding: 11px 12px; border-radius: 10px; background: linear-gradient(135deg, rgba(245, 158, 11, 0.25), rgba(217, 119, 6, 0.35)); border: 1.5px solid rgba(245, 158, 11, 0.6); color: #fef08a; font-size: 12px; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 12px rgba(245,158,11,0.2);">
            <span style="display:flex; align-items:center; gap:6px;">
              <span>💬</span>
              <span>👑 대표님 ⇄ 🛰️ 르곤-알파 1:1 독대실</span>
            </span>
            <span style="background:rgba(245,158,11,0.3); padding:2px 8px; border-radius:12px; font-size:10px; color:#fff;">직통 ➔</span>
          </button>

          <button onclick="window.triggerAlphaFromAside()" style="width: 100%; text-align: left; padding: 10px 12px; border-radius: 10px; background: linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(79, 70, 229, 0.35)); border: 1px solid rgba(99, 102, 241, 0.5); color: #e0e7ff; font-size: 12px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
            <span>🛰️ 르곤-알파 전 기관 통합 순찰·명령</span>
            <span>➔</span>
          </button>
          
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

  // 👑 대표님 ⇄ 르곤-알파 1:1 독대실 바로가기
  function goToAlphaChat() {
    const p = window.location.pathname.toLowerCase();
    if (p.includes('/departments/')) {
      window.location.href = '../rgon_alpha_chat.html';
    } else if (p.includes('/dashboard/')) {
      window.location.href = 'rgon_alpha_chat.html';
    } else {
      window.location.href = 'rgon_alpha_chat.html';
    }
  }
  window.goToAlphaChat = goToAlphaChat;

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

  // 💻 [v12.2] 노트북 6대 멀티탭 워크스페이스 일괄 가동
  window.triggerAsideAllInOneMultitab = async function() {
    const listEl = document.getElementById('aside-channels-list');
    if (listEl) {
      listEl.innerHTML = `
        <div style="padding: 12px; border-radius: 8px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); text-align: center; color: #a7f3d0; font-size: 11px;">
          <div style="font-weight: 700; margin-bottom: 4px;">💻 6대 멀티탭 워크스페이스 동시 집행 중...</div>
          <div style="font-size: 10px; color: #6ee7b7;">1청사 퀀트 ➔ 6청사 트레저리 작업 분배 및 동기화 진행 중</div>
        </div>
      `;
    }

    try {
      const res = await fetch('/api/aside-all-in-one-execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command_text: '어사이드 서랍 6대 멀티탭 일괄 가동' })
      });
      const data = await res.json();
      if (data && data.success) {
        renderMultitabStatusBoard(data);
      } else {
        if (listEl) listEl.innerHTML = `<div style="padding:10px; color:#f87171;">멀티탭 실행 응답 오류</div>`;
      }
    } catch (err) {
      console.warn('어사이드 멀티탭 실행 예외:', err);
    }
  };

  function renderMultitabStatusBoard(data) {
    const listEl = document.getElementById('aside-channels-list');
    if (!listEl) return;

    const plan = data.multitab_execution_plan || [];
    let html = `
      <div style="padding: 8px 10px; border-radius: 8px; background: rgba(16, 185, 129, 0.2); border: 1px solid rgba(16, 185, 129, 0.5); color: #a7f3d0; font-weight: 800; font-size: 11px; margin-bottom: 6px;">
        💻 노트북 6대 멀티탭 올인원 완수 (${data.receipt_id || ''})
      </div>
    `;

    plan.forEach(item => {
      html += `
        <div style="padding: 8px 10px; border-radius: 8px; background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(16, 185, 129, 0.35); font-size: 11px;">
          <div style="font-weight: 700; color: #fef08a; display: flex; justify-content: space-between;">
            <span>탭 ${item.tab_index}: ${item.dept}</span>
            <span style="font-size: 10px; color: #34d399;">100% 정상</span>
          </div>
          <div style="color: #e2e8f0; font-size: 11px; margin-top: 2px;">${item.target}</div>
        </div>
      `;
    });

    listEl.innerHTML = html;
  }

  // 🛰️ [v11.4] 어사이드 서랍 내부에서 르곤-알파 호출 함수
  window.triggerAlphaFromAside = async function() {
    try {
      const res = await fetch('/api/rgon-alpha-command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: 'ALPHA_FULL_PATROL' })
      });
      const data = await res.json();
      const payload = data.data || data;
      alert(`🛰️ [르곤-알파 전 기관 통합 자가순찰 완료!]\n\n• 영수증: ${payload.receipt_id || '#ALPHA-PATROL-OK'}\n• 르곤-알파 브리핑: ${payload.briefing || '전 기관 이상 무'}\n• 대표님 스마트폰 텔레그램 발송 완료!`);
      if (typeof window.loadRgonAlphaStatus === 'function') {
        window.loadRgonAlphaStatus();
      }
    } catch (e) {
      alert('르곤-알파 순찰 호출 실패: ' + e.message);
    }
  };

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

/* [RGON-4BTN-V12-START] step12 자동 생성 블록 - 수동 편집 금지 */
;(function () {
  'use strict';
  if (typeof window === 'undefined' || typeof document === 'undefined') return;
  if (window.__RGON_4BTN_V12__) return;
  window.__RGON_4BTN_V12__ = true;

  var MARK = 'data-rgon-v12';
  var CODE_SEL = 'textarea, pre, code, [contenteditable="true"]';
  var CARD_SEL = '[class*="card" i], [class*="item" i], [class*="result" i], [data-card], article, li, details';

  function txt(el) { return ((el && (el.innerText || el.textContent)) || '').replace(/\s+/g, ' ').trim(); }
  function ours(b) { return b.hasAttribute(MARK) || !!b.closest('[' + MARK + ']'); }
  function isSave(b) { return !ours(b) && txt(b).indexOf('shin-agent 저장') !== -1; }
  function isQueue(b) { return !ours(b) && txt(b).indexOf('안총리') !== -1; }
  function is(b) { var t = txt(b); return !ours(b) && t.indexOf('복사') !== -1 && t.indexOf('흡수') === -1; }
  function isTopAbsorb(b) {
    var t = txt(b);
    return !ours(b) && (t.indexOf('이 탭 코드 흡수') !== -1 || t.indexOf('화면 텍스트 흡수') !== -1);
  }

  /* ---------- DOM 탐색 (open shadow root 포함) ---------- */
  var observed = new WeakSet();
  function roots() {
    var out = [document];
    (function walk(r) {
      var all = r.querySelectorAll('*');
      for (var i = 0; i < all.length; i++) {
        if (all[i].shadowRoot) { out.push(all[i].shadowRoot); walk(all[i].shadowRoot); }
      }
    })(document);
    return out;
  }
  function buttons(pred) {
    var res = [];
    roots().forEach(function (r) {
      r.querySelectorAll('button, [role="button"]').forEach(function (b) { if (pred(b)) res.push(b); });
    });
    return res;
  }
  function css(el, obj) { for (var k in obj) el.style.setProperty(k, obj[k], 'important'); }

  var BTN_CSS = {
    'overflow': 'visible', 'text-overflow': 'clip', 'white-space': 'normal',
    'word-break': 'keep-all', 'overflow-wrap': 'anywhere',
    'padding': '7px 10px', 'font-size': '12px', 'line-height': '1.3',
    'min-width': '0', 'max-width': 'none', 'width': '100%', 'height': 'auto',
    'min-height': '32px', 'box-sizing': 'border-box', 'text-align': 'center'
  };
  function styleBtn(b) {
    css(b, BTN_CSS);
    b.querySelectorAll('*').forEach(function (c) {
      css(c, { 'overflow': 'visible', 'text-overflow': 'clip', 'white-space': 'normal', 'max-width': 'none' });
    });
  }

  /* ---------- 카드 컨테이너 찾기 ---------- */
  function countSaves(el, saves) { var n = 0; saves.forEach(function (s) { if (el.contains(s)) n++; }); return n; }
  function hasTop(el, tops) { return tops.some(function (t) { return el.contains(t); }); }
  function findCard(btn, saves, tops) {
    var A = null, el = btn.parentElement, depth = 0;
    while (el && el !== document.body && el !== document.documentElement && depth < 8) {
      if (countSaves(el, saves) > 1 || hasTop(el, tops)) break;
      if (el.querySelector(CODE_SEL)) { A = el; break; }
      el = el.parentElement; depth++;
    }
    var C = btn.closest(CARD_SEL);
    if (C && C !== document.body && countSaves(C, saves) === 1 && !hasTop(C, tops) &&
        (!A || C.contains(A))) return C;
    return A || btn.parentElement;
  }

  /* ---------- 지우기 동작 ---------- */
  function setVal(f, v) {
    var proto = f.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    var d = Object.getOwnPropertyDescriptor(proto, 'value');
    if (d && d.set) d.set.call(f, v); else f.value = v;
    f.dispatchEvent(new Event('input', { bubbles: true }));
    f.dispatchEvent(new Event('change', { bubbles: true }));
  }
  function clearFields(scope) {
    scope.querySelectorAll('textarea, input[type="text"], input[type="search"], input:not([type])')
      .forEach(function (f) { if (!ours(f)) setVal(f, ''); });
    scope.querySelectorAll('pre').forEach(function (p) { p.textContent = ''; });
    scope.querySelectorAll('code').forEach(function (c) { if (!c.closest('pre')) c.textContent = ''; });
    scope.querySelectorAll('[contenteditable="true"]').forEach(function (c) { c.textContent = ''; });
  }
  function hideCard(card) {
    clearFields(card);
    css(card, { 'display': 'none' });
    card.setAttribute('data-rgon-v12-hidden', '1');
    card.__rgonV12Snap = txt(card);
  }
  function toast(msg) {
    try {
      var t = document.createElement('div');
      t.setAttribute(MARK, 'toast');
      t.textContent = msg;
      css(t, { 'position': 'fixed', 'left': '50%', 'bottom': '18px', 'transform': 'translateX(-50%)',
        'background': '#222', 'color': '#fff', 'padding': '8px 14px', 'border-radius': '8px',
        'font-size': '12px', 'z-index': '2147483647', 'opacity': '0.95' });
      document.body.appendChild(t);
      setTimeout(function () { t.remove(); }, 1600);
    } catch (e) {}
  }
  function clearAll(ask) {
    if (ask && !window.confirm('흡수창의 모든 카드와 입력창을 비울까요?')) return;
    var saves = buttons(isSave), tops = buttons(isTopAbsorb);
    saves.forEach(function (s) { hideCard(findCard(s, saves, tops)); });
    roots().forEach(function (r) {
      r.querySelectorAll('textarea').forEach(function (f) { if (!ours(f)) setVal(f, ''); });
    });
    try {
      var keys = window.RGON_V12_STORAGE_KEYS;  /* 필요 시 저장소 키 배열 지정 */
      if (Array.isArray(keys) && keys.length && window.chrome && chrome.storage && chrome.storage.local) {
        chrome.storage.local.remove(keys);
      }
    } catch (e) {}
    try { window.dispatchEvent(new CustomEvent('rgon:clear-all')); } catch (e) {}
    toast('🗑️ 흡수창을 모두 비웠습니다');
  }

  function makeBtn(label, kind, onClick) {
    var b = document.createElement('button');
    b.type = 'button';
    b.setAttribute(MARK, kind);
    b.textContent = label;
    b.title = label;
    styleBtn(b);
    css(b, { 'cursor': 'pointer', 'border-radius': '6px', 'border': '1px solid rgba(127,127,127,.35)',
      'background': kind === 'all' || kind === 'top' ? '#fdecec' : '#f3f4f6', 'color': '#222' });
    b.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); onClick(b); });
    return b;
  }

  /* ---------- 카드별 버튼 배치 ---------- */
  function ensureRow(saveBtn) {
    var row = saveBtn.parentElement;
    if (!row) return null;
    if (row.hasAttribute(MARK) && row.getAttribute(MARK) === 'btnrow') return row;
    var nonBtn = Array.prototype.filter.call(row.children, function (c) {
      return !(c.matches('button, [role="button"]'));
    }).length;
    if (row.querySelector('textarea, pre, code, input, select') || nonBtn > 2) {
      var wrap = document.createElement('div');
      wrap.setAttribute(MARK, 'btnrow');
      row.insertBefore(wrap, saveBtn);
      Array.prototype.slice.call(row.children).forEach(function (c) {
        if (c !== wrap && c.matches && c.matches('button, [role="button"]') &&
            (is(c) || isSave(c) || isQueue(c))) wrap.appendChild(c);
      });
      row = wrap;
    }
    return row;
  }
  function decorate(saveBtn, saves, tops) {
    var row = ensureRow(saveBtn);
    if (!row) return;
    css(row, { 'display': 'grid', 'grid-template-columns': 'repeat(auto-fit, minmax(96px, 1fr))',
      'gap': '6px', 'width': '100%', 'overflow': 'visible', 'flex': '1 1 100%',
      'min-width': '0', 'box-sizing': 'border-box', 'grid-column': '1 / -1' });
    var p = row.parentElement;
    if (p && getComputedStyle(p).display.indexOf('flex') !== -1) css(p, { 'flex-wrap': 'wrap' });
    Array.prototype.forEach.call(row.querySelectorAll('button, [role="button"]'), styleBtn);

    var next = row.nextElementSibling;
    if (next && next.getAttribute(MARK) === 'row') return;
    var er = document.createElement('div');
    er.setAttribute(MARK, 'row');
    css(er, { 'display': 'grid', 'grid-template-columns': '1fr 1fr', 'gap': '6px', 'width': '100%',
      'margin-top': '6px', 'grid-column': '1 / -1', 'flex': '1 1 100%', 'box-sizing': 'border-box' });
    er.appendChild(makeBtn('🧹 이 카드 지우기', 'one', function () {
      var s = buttons(isSave), t = buttons(isTopAbsorb);
      hideCard(findCard(saveBtn, s, t));
      toast('🧹 카드를 지웠습니다');
    }));
    er.appendChild(makeBtn('🗑️ 전체 카드 지우기', 'all', function () { clearAll(true); }));
    row.insertAdjacentElement('afterend', er);
  }

  function decorateTop(tops) {
    var seen = new Set();
    tops.forEach(function (b) {
      var p = b.parentElement;
      if (!p || seen.has(p)) return;
      seen.add(p);
      if (p.querySelector('[' + MARK + '="top"]')) return;
      var last = tops.filter(function (x) { return x.parentElement === p; }).pop() || b;
      var nb = makeBtn('🗑️ 흡수창 전체 비우기', 'top', function () { clearAll(true); });
      css(nb, { 'width': 'auto' });
      last.insertAdjacentElement('afterend', nb);
      if (getComputedStyle(p).display.indexOf('flex') !== -1) css(p, { 'flex-wrap': 'wrap', 'gap': '6px' });
    });
  }

  function unhideIfRefilled() {
    roots().forEach(function (r) {
      r.querySelectorAll('[data-rgon-v12-hidden="1"]').forEach(function (c) {
        var now = txt(c);
        if (now && now !== c.__rgonV12Snap) {
          c.style.removeProperty('display');
          c.removeAttribute('data-rgon-v12-hidden');
        }
      });
    });
  }

  function scan() {
    try {
      var saves = buttons(isSave), tops = buttons(isTopAbsorb);
      saves.forEach(function (s) { decorate(s, saves, tops); });   /* 모든 카드 반복 */
      if (tops.length) decorateTop(tops);
      unhideIfRefilled();
      roots().forEach(observe);
    } catch (e) { console.warn('[RGON-V12]', e); }
  }

  var timer = null;
  function schedule() { clearTimeout(timer); timer = setTimeout(scan, 200); }
  function observe(r) {
    if (observed.has(r)) return;
    observed.add(r);
    new MutationObserver(schedule).observe(r === document ? document.documentElement : r,
      { childList: true, subtree: true, characterData: true });
  }

  window.RGON_V12 = { scan: scan, clearAll: clearAll };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', scan);
  else scan();
})();
/* [RGON-4BTN-V12-END] */
