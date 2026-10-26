// rgon_smart_edge_dock.js
// 🌊 [상선약수 비움 & 스마트 엣지 도킹 엔진]
// 1) 중복 3종(어사이드, R40/46시냅스배지, 5G터널추적알약) 화면 완전 제거 (비움)
// 2) 핵심 4대 도구(만능소통창, 검열HUD, R47스튜디오, 해상이변신술) 우측 벽 10px 초슬림 막대 은신 + 클릭 등장 + [⇥] 숨기기 + 자유 드래그

(function() {
  function initSmartEdgeDock() {
    if (document.getElementById('rgon-edge-dock-host')) return;

    // 1. 공통 비움 & 엣지 독 CSS 주입
    var style = document.createElement('style');
    style.id = 'rgon-edge-dock-styles';
    style.textContent = `
      /* [1단계: 상선약수 비움] 화면 가리는 중복 플로팅 3종 완전 제거 */
      #rgon-aside-fab,
      #rgon-aside-backdrop,
      #rgon-aside-drawer,
      #rgon-r40-synapse-badge,
      #rgv-float {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
        opacity: 0 !important;
      }

      /* 기존 분산 플로팅 버튼들(소통창FAB, R47배지, 해상토글)은 우측 벽 슬림 바로 통합되어 기본 화면 가림 해제 */
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

      /* 평소 10px 슬림 네온 막대 (호버 시 42px 확장되어 아이콘과 툴팁 노출) */
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
        width: 44px;
        box-shadow: -4px 6px 20px rgba(0, 0, 0, 0.6);
        transform: translateX(-2px);
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
      #edge-tool-muse {
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

      /* [ ⇥ ] 숨기기 버튼 공통 스타일 */
      .rgon-dock-hide-btn {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.4);
        color: #f8fafc;
        border-radius: 8px;
        padding: 2px 7px;
        font-size: 11px;
        font-weight: 800;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 3px;
        transition: all 0.2s ease;
      }
      .rgon-dock-hide-btn:hover {
        background: rgba(244, 63, 94, 0.4);
        border-color: #f43f5e;
        color: #ffffff;
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
      <div id="edge-tool-muse" class="rgon-edge-handle" title="✨ 르곤 만능 소통창 (Omni-Link)" onclick="window.RgonEdgeDock.openMuse()">
        <span class="edge-icon">✨</span>
      </div>
      <div id="edge-tool-hud" class="rgon-edge-handle" title="👑 실전 검열 HUD" onclick="window.RgonEdgeDock.toggleHud()">
        <span class="edge-icon">👑</span>
      </div>
      <div id="edge-tool-r47" class="rgon-edge-handle" title="📊 R47 클릭0번 포토·엑셀 스튜디오" onclick="window.RgonEdgeDock.openR47()">
        <span class="edge-icon">📊</span>
      </div>
      <div id="edge-tool-haesang" class="rgon-edge-handle" title="🎨 해상이의 아온 변신술" onclick="window.RgonEdgeDock.openHaesang()">
        <span class="edge-icon">🎨</span>
      </div>
    `;
    document.body.appendChild(host);

    // 3. 각 창에 드래그 & 숨기기 버튼 바인딩
    setTimeout(bindDockBehaviors, 300);
  }

  // 드래그 앤 드롭 구현 헬퍼
  function makeDraggable(element, handle) {
    if (!element || !handle) return;
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

  function bindDockBehaviors() {
    // 1) 검열 HUD (#rgon-inspect-hud) 드래그 및 [⇥] 버튼
    var hud = document.getElementById('rgon-inspect-hud');
    if (hud) {
      makeDraggable(hud, hud);
      if (!hud.querySelector('.rgon-dock-hide-btn')) {
        var hideBtn = document.createElement('button');
        hideBtn.className = 'rgon-dock-hide-btn';
        hideBtn.innerHTML = '⇥ 숨기기';
        hideBtn.onclick = function(e) {
          e.stopPropagation();
          hud.style.display = 'none';
        };
        hud.insertBefore(hideBtn, hud.firstChild);
      }
    }

    // 2) 해상이 변신술 캡슐 (#aon-morph-capsule) 드래그 및 [⇥] 버튼
    var capsule = document.getElementById('aon-morph-capsule');
    if (capsule) {
      var headerRow = capsule.querySelector('div');
      makeDraggable(capsule, headerRow || capsule);
      if (headerRow && !headerRow.querySelector('.rgon-dock-hide-btn')) {
        var hideBtn = document.createElement('button');
        hideBtn.className = 'rgon-dock-hide-btn';
        hideBtn.innerHTML = '⇥ 숨기기';
        hideBtn.onclick = function(e) {
          e.stopPropagation();
          capsule.style.display = 'none';
        };
        headerRow.appendChild(hideBtn);
      }
    }

    // 3) R47 스튜디오 모달 (#rgon-r47-modal) 내부 카드
    var r47Modal = document.getElementById('rgon-r47-modal');
    if (r47Modal) {
      var r47Card = r47Modal.querySelector('div');
      if (r47Card) makeDraggable(r47Card, r47Card.querySelector('h3') || r47Card);
    }
  }

  // 전역 제어 API
  window.RgonEdgeDock = {
    openMuse: function() {
      if (window.RGMuse && window.RGMuse.openModal) {
        window.RGMuse.openModal();
      } else {
        var fab = document.getElementById('rgmuse-fab');
        if (fab) fab.click();
        else {
          var ov = document.getElementById('rgmuse-overlay');
          if (ov) ov.style.display = 'flex';
        }
      }
    },
    toggleHud: function() {
      var hud = document.getElementById('rgon-inspect-hud');
      if (hud) {
        hud.style.display = (hud.style.display === 'none' ? 'block' : 'none');
      } else {
        if (typeof toggleInspectHUD === 'function') toggleInspectHUD();
      }
    },
    openR47: function() {
      var m = document.getElementById('rgon-r47-modal');
      if (m) m.style.display = 'flex';
      else {
        var b = document.getElementById('rgon-r47-badge');
        if (b) b.click();
      }
    },
    openHaesang: function() {
      var c = document.getElementById('aon-morph-capsule');
      if (c) {
        c.style.display = (c.style.display === 'none' ? 'flex' : 'none');
        if (c.style.display === 'flex' && typeof setHaesangMorph === 'function') {
          setHaesangMorph('orb');
        }
      } else {
        var toggle = document.getElementById('rgon-haesang-toggle');
        if (toggle) toggle.click();
      }
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSmartEdgeDock);
  } else {
    initSmartEdgeDock();
  }
})();
