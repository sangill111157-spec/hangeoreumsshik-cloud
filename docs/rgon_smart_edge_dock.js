// rgon_smart_edge_dock.js
// 🌊 [상선약수 비움 & 스마트 엣지 도킹 엔진 - 실전 정밀 직결판]
// 1) 화면 가리는 3대 알약(르곤만능소통창, 실전검열HUD, 5G터널추적) 및 중복 플로팅 100% 은신 (비움)
// 2) 우측 4대 슬림 막대(✨ 소통창, 👑 검열HUD, 📊 R47스튜디오, 🎨 해상변신술) 정밀 직결
// 3) 텍스트 기반 전수 스캔 실시간 가디언 탑재

(function() {
  function initSmartEdgeDock() {
    if (document.getElementById('rgon-edge-dock-host')) return;

    // 1. 공통 비움 & 엣지 독 CSS 주입
    var style = document.createElement('style');
    style.id = 'rgon-edge-dock-styles';
    style.textContent = `
      /* [1단계: 상선약수 비움 & 3대 알약 100% 은신] 화면 가리는 요소 원천 차단 */
      #rgon-aside-fab,
      #rgon-aside-backdrop,
      #rgon-aside-drawer,
      #rgon-r40-synapse-badge,
      #rgv-float,
      #rgon-pwa-bridge-bar,
      #rgon-agentation-hud,
      #rgon-hud-pill,
      #rgon-inspect-hud,
      #rgmuse-fab,
      #rgon-r47-badge,
      #rgon-haesang-toggle {
        display: none !important;
      }

      /* [2단계: 우측 끝 초슬림 엣지 도킹 바 컨테이너] */
      #rgon-edge-dock-host {
        position: fixed;
        right: 0;
        top: 24%;
        z-index: 2147483640;
        display: flex;
        flex-direction: column;
        gap: 12px;
        pointer-events: auto;
        user-select: none;
      }

      /* 평소 10px 슬림 네온 막대 (호버 시 44px 확장되어 아이콘과 툴팁 노출) */
      .rgon-edge-handle {
        width: 10px;
        height: 48px;
        border-radius: 12px 0 0 12px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        padding-left: 8px;
        overflow: hidden;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: -2px 4px 14px rgba(0, 0, 0, 0.4);
        position: relative;
        white-space: nowrap;
      }
      .rgon-edge-handle:hover {
        width: 46px;
        box-shadow: -4px 6px 20px rgba(0, 0, 0, 0.6);
        transform: translateX(-2px);
      }
      /* 스마트폰 모바일 터치 히트박스 (투명 엄지 터치 영역 24px) */
      .rgon-edge-handle::before {
        content: "";
        position: absolute;
        top: -6px;
        bottom: -6px;
        left: -18px;
        right: 0;
        min-width: 28px;
        pointer-events: auto;
      }
      @media (max-width: 768px) {
        #rgon-aside-drawer, #rgon-agentation-hud, #rgon-hud-pill, .rgon-popup-panel {
          max-width: 92vw !important;
          width: min(92vw, 380px) !important;
        }
      }
      .rgon-edge-handle .edge-icon {
        font-size: 16px;
        opacity: 0.35;
        transition: opacity 0.2s ease, transform 0.2s ease;
      }
      .rgon-edge-handle:hover .edge-icon {
        opacity: 1;
        transform: scale(1.15);
      }

      /* 4대 도구별 고유 네온 테마 */
      #edge-tool-omni {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.85), rgba(14, 165, 233, 0.9));
        border: 1px solid rgba(125, 211, 252, 0.7);
        border-right: none;
      }
      #edge-tool-hud {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.85), rgba(217, 119, 6, 0.9));
        border: 1px solid rgba(253, 230, 138, 0.7);
        border-right: none;
      }
      #edge-tool-r47 {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.85), rgba(126, 34, 206, 0.9));
        border: 1px solid rgba(216, 180, 254, 0.7);
        border-right: none;
      }
      #edge-tool-haesang {
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.85), rgba(225, 29, 72, 0.9));
        border: 1px solid rgba(254, 205, 211, 0.7);
        border-right: none;
      }

      /* [ ⇥ 숨기기 ] 버튼 공통 고품질 스타일 */
      .rgon-dock-hide-btn {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(148, 163, 184, 0.5) !important;
        color: #f8fafc !important;
        border-radius: 8px !important;
        padding: 3px 8px !important;
        font-size: 11px !important;
        font-weight: 800 !important;
        cursor: pointer !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 3px !important;
        transition: all 0.2s ease !important;
        outline: none !important;
      }
      .rgon-dock-hide-btn:hover {
        background: rgba(244, 63, 94, 0.6) !important;
        border-color: #f43f5e !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
      }

      /* 드래그 핸들 커서 스타일 */
      .rgon-draggable-header {
        cursor: move !important;
      }
    `;
    document.head.appendChild(style);

    // 2. 우측 벽 슬림 막대 호스트 DOM 생성
    var host = document.createElement('div');
    host.id = 'rgon-edge-dock-host';

    host.innerHTML = `
      <div id="edge-tool-omni" class="rgon-edge-handle" title="✨ 르곤 만능 소통창 (Omni-Link)" onclick="window.RgonEdgeDock.toggleOmniLink()">
        <span class="edge-icon">✨</span>
      </div>
      <div id="edge-tool-hud" class="rgon-edge-handle" title="👑 실전 검열 HUD" onclick="window.RgonEdgeDock.toggleHud()">
        <span class="edge-icon">👑</span>
      </div>
      <div id="edge-tool-r47" class="rgon-edge-handle" title="📊 제23기관 포토·카드뉴스 & 엑셀 스튜디오" onclick="window.RgonEdgeDock.openR47()">
        <span class="edge-icon">📊</span>
      </div>
      <div id="edge-tool-haesang" class="rgon-edge-handle" title="🎨 해상이의 아온 변신술" onclick="window.RgonEdgeDock.openHaesang()">
        <span class="edge-icon">🎨</span>
      </div>
    `;
    document.body.appendChild(host);

    // 3. 주기적 텍스트 기반 전수 스캔 및 버튼 바인딩
    setInterval(sweepRoguePillsAndBind, 500);
    sweepRoguePillsAndBind();
  }

  // 드래그 앤 드롭 구현 헬퍼
  function makeDraggable(element, handle) {
    if (!element || !handle || element.__rgon_draggable) return;
    element.__rgon_draggable = true;
    handle.classList.add('rgon-draggable-header');

    var isDown = false;
    var startX = 0, startY = 0;
    var elemX = 0, elemY = 0;

    handle.addEventListener('mousedown', function(e) {
      if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' || e.target.tagName === 'INPUT') return;
      isDown = true;
      var rect = element.getBoundingClientRect();
      startX = e.clientX;
      startY = e.clientY;
      elemX = rect.left;
      elemY = rect.top;
      e.preventDefault();
    });

    window.addEventListener('mousemove', function(e) {
      if (!isDown) return;
      var dx = e.clientX - startX;
      var dy = e.clientY - startY;
      element.style.position = 'fixed';
      element.style.left = (elemX + dx) + 'px';
      element.style.top = (elemY + dy) + 'px';
      element.style.right = 'auto';
      element.style.bottom = 'auto';
      element.style.transform = 'none';
    });

    window.addEventListener('mouseup', function() {
      isDown = false;
    });
  }

  // [핵심 가디언] 실제 텍스트 및 Shadow DOM 스캔하여 불량 알약 전수 은닉 & 닫기 버튼 단일화
  function sweepRoguePillsAndBind() {
    // A) 1번: ✨ 르곤 만능 소통창 Shadow Root 내부 탐색 및 배지 은닉
    var omniHost = document.getElementById('rgon-omni-host');
    if (omniHost && omniHost.shadowRoot) {
      var badge = omniHost.shadowRoot.getElementById('badge');
      if (badge) {
        badge.style.setProperty('display', 'none', 'important');
      }
    }

    // B) 3번: 최하단 🟢 5G 터널 추적 ON 알약 (#rgon-pwa-bridge-bar 또는 텍스트 포함 요소) 은닉
    var pwaBar = document.getElementById('rgon-pwa-bridge-bar');
    if (pwaBar) {
      pwaBar.style.setProperty('display', 'none', 'important');
    }

    // C) 2번: 👑 실전 검열 HUD (#rgon-agentation-hud) 제어 및 숨기기 버튼 장착
    var hud = document.getElementById('rgon-agentation-hud') || document.getElementById('rgon-inspect-hud');
    if (hud) {
      if (!window.__rgon_hud_user_opened) {
        hud.style.setProperty('display', 'none', 'important');
      }
      makeDraggable(hud, hud);
      if (!hud.querySelector('.rgon-hud-top-hide')) {
        var hideBtn = document.createElement('button');
        hideBtn.className = 'rgon-dock-hide-btn rgon-hud-top-hide';
        hideBtn.innerHTML = '⇥ 숨기기';
        hideBtn.style.marginRight = '8px';
        hideBtn.onclick = function(e) {
          e.stopPropagation();
          window.__rgon_hud_user_opened = false;
          hud.style.setProperty('display', 'none', 'important');
        };
        var firstRow = hud.querySelector('div');
        if (firstRow) firstRow.insertBefore(hideBtn, firstRow.firstChild);
      }
    }

    // D) 4번: 해상이의 아온 변신술 (#aon-morph-capsule) 닫기 버튼 단일화 (겹치는 ✕ 제거)
    var capsule = document.getElementById('aon-morph-capsule');
    if (capsule) {
      var headerRow = capsule.querySelector('div');
      if (headerRow) {
        makeDraggable(capsule, headerRow);
        // 기존의 작은 ✕ 글자 버튼 숨김
        var oldClose = headerRow.querySelector('button[onclick*="toggleHaesangWidget"]');
        if (oldClose && !oldClose.classList.contains('rgon-dock-hide-btn')) {
          oldClose.style.display = 'none';
        }
        // 새로운 [ ⇥ 숨기기 ] 버튼 하나만 유지
        if (!headerRow.querySelector('.rgon-haesang-dock-hide')) {
          var hideBtn = document.createElement('button');
          hideBtn.className = 'rgon-dock-hide-btn rgon-haesang-dock-hide';
          hideBtn.innerHTML = '⇥ 숨기기';
          hideBtn.onclick = function(e) {
            e.stopPropagation();
            capsule.style.display = 'none';
          };
          headerRow.appendChild(hideBtn);
        }
      }
    }

    // E) 제23기관 스튜디오 모달 (#rgon-r47-modal) 상단 [ ⇥ 숨기기 ] 버튼 및 여백 축소
    var r47Modal = document.getElementById('rgon-r47-modal');
    if (r47Modal) {
      var card = r47Modal.querySelector('div');
      if (card) {
        card.style.margin = '3vh auto';
        card.style.padding = '14px 18px';
        card.style.maxWidth = '680px';
        makeDraggable(card, card.querySelector('div') || card);
        var topRow = card.querySelector('div');
        if (topRow && !topRow.querySelector('.rgon-r47-dock-hide')) {
          // 기존 ✕는 작게 남아있을 수 있으므로 깔끔한 [ ⇥ 숨기기 ] 버튼 추가
          var r47Hide = document.createElement('button');
          r47Hide.className = 'rgon-dock-hide-btn rgon-r47-dock-hide';
          r47Hide.innerHTML = '⇥ 숨기기';
          r47Hide.style.marginLeft = '10px';
          r47Hide.onclick = function() {
            r47Modal.style.display = 'none';
          };
          var oldX = topRow.querySelector('#rgon-r47-x');
          if (oldX) oldX.style.display = 'none';
          topRow.appendChild(r47Hide);
        }
      }
    }

    // F) 뮤즈 오버레이 (#rgmuse-overlay) [ ⇥ 숨기기 / ✕ 닫기 ] 장착
    var museOverlay = document.getElementById('rgmuse-overlay');
    if (museOverlay) {
      var museCard = museOverlay.querySelector('div');
      if (museCard && !museCard.querySelector('.rgon-muse-dock-hide')) {
        var museHide = document.createElement('button');
        museHide.className = 'rgon-dock-hide-btn rgon-muse-dock-hide';
        museHide.innerHTML = '⇥ 숨기기';
        museHide.style.position = 'absolute';
        museHide.style.top = '12px';
        museHide.style.right = '12px';
        museHide.onclick = function() {
          museOverlay.style.display = 'none';
        };
        museCard.style.position = 'relative';
        museCard.appendChild(museHide);
      }
    }

    // G) 텍스트 전수 검색: 혹시라도 남아 있는 텍스트 기반 rogue 요소 숨김
    document.querySelectorAll('div, span, button').forEach(function(el) {
      if (el.id === 'rgon-edge-dock-host' || el.closest('#rgon-edge-dock-host')) return;
      var txt = (el.innerText || el.textContent || '').trim();
      if (txt === '5G 터널 추적 ON' || txt.indexOf('5G 터널 추적 ON') !== -1) {
        var target = el.closest('#rgon-pwa-bridge-bar') || el;
        target.style.setProperty('display', 'none', 'important');
      }
    });
  }

  // 전역 제어 API (슬림 막대 클릭 액션 직결)
  window.RgonEdgeDock = {
    // 1번 파란색 막대: ✨ 진짜 르곤 만능 소통창 (Omni-Link) 토글!
    toggleOmniLink: function() {
      // 1) Shadow Root 내부의 #panel 탐색
      var host = document.getElementById('rgon-omni-host');
      if (host && host.shadowRoot) {
        var panel = host.shadowRoot.getElementById('panel');
        if (panel) {
          panel.classList.toggle('open');
          return;
        }
      }
      // 2) 일반 DOM 패널 탐색
      var p = document.getElementById('panel') || document.getElementById('rgon-omni-panel');
      if (p) {
        p.classList.toggle('open');
        return;
      }
      // 3) 확장 프로그램 백업 트리거
      if (window.__RGON_OMNI_TOGGLE__) {
        window.__RGON_OMNI_TOGGLE__();
        return;
      }
      // 4) 보좌관 뮤즈 보드
      if (window.RGMuse && window.RGMuse.openModal) {
        window.RGMuse.openModal();
      } else {
        var ov = document.getElementById('rgmuse-overlay');
        if (ov) ov.style.display = (ov.style.display === 'none' ? 'flex' : 'none');
      }
    },

    // 2번 주황색 막대: 👑 실전 검열 HUD 토글!
    toggleHud: function() {
      var hud = document.getElementById('rgon-agentation-hud') || document.getElementById('rgon-inspect-hud');
      if (hud) {
        var isHidden = (window.getComputedStyle(hud).display === 'none' || hud.style.display === 'none');
        if (isHidden) {
          window.__rgon_hud_user_opened = true;
          hud.style.setProperty('display', 'block', 'important');
          // 최소화 상태면 버튼 트리거로 펼치기 시도
          var expandBtn = hud.querySelector('#rgon-hud-expand');
          if (expandBtn) expandBtn.click();
        } else {
          window.__rgon_hud_user_opened = false;
          hud.style.setProperty('display', 'none', 'important');
        }
      } else {
        if (typeof toggleInspectHUD === 'function') toggleInspectHUD();
      }
    },

    // 3번 보라색 막대: 📊 제23기관 포토·카드뉴스 & 엑셀 스튜디오
    openR47: function() {
      var m = document.getElementById('rgon-r47-modal');
      if (m) {
        var isHidden = (m.style.display === 'none');
        m.style.display = isHidden ? 'flex' : 'none';
        if (m.style.display === 'flex') {
          var card = m.querySelector('div');
          if (card) {
            card.style.margin = '3vh auto';
            card.style.padding = '14px 18px';
            card.style.maxWidth = '680px';
          }
        }
      } else {
        var b = document.getElementById('rgon-r47-badge');
        if (b) b.click();
      }
    },

    // 4번 분홍색 막대: 🎨 해상이의 아온 변신술
    openHaesang: function() {
      var c = document.getElementById('aon-morph-capsule');
      if (c) {
        var isHidden = (c.style.display === 'none');
        c.style.display = isHidden ? 'flex' : 'none';
        if (isHidden && typeof setHaesangMorph === 'function') {
          setHaesangMorph('orb');
        }
      } else {
        var toggle = document.getElementById('rgon-haesang-toggle');
        if (toggle) toggle.click();
      }
    }
  };

  // 호환용 레거시 별칭
  window.RgonEdgeDock.openMuse = window.RgonEdgeDock.toggleOmniLink;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSmartEdgeDock);
  } else {
    initSmartEdgeDock();
  }
})();
