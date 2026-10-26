/**
 * rgon_button_bot_runtime.js — 제29기관 전 페이지·전 버튼 자동화 봇 런타임
 * v11.52-AON-PAGE-BUTTON-BOT · 항체 R1~R53 · 스킬 49개
 * [본문 가림 0% 엄수] 상시 플로팅 알약 0개 · Alt+B 단축키 또는 온디맨드 호출 시에만 봇 편성 모드 토글
 */
(function() {
  'use strict';
  if (window.__RGON_BUTTON_BOT_RUNTIME__) return;
  window.__RGON_BUTTON_BOT_RUNTIME__ = true;

  var isBotModeActive = false;
  var overlayBadgeId = 'rgon-bot-mode-indicator';

  function toast(msg) {
    var t = document.getElementById('rgon-bot-toast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'rgon-bot-toast';
      t.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);z-index:999999;background:rgba(15,23,42,0.95);border:1px solid #38bdf8;color:#f8fafc;padding:8px 16px;border-radius:12px;font-size:12px;font-weight:bold;box-shadow:0 10px 30px rgba(0,0,0,0.6);pointer-events:none;transition:opacity 0.2s;';
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.opacity = '1';
    clearTimeout(t._timer);
    t._timer = setTimeout(function() {
      t.style.opacity = '0';
    }, 2400);
  }

  function toggleBotMode() {
    isBotModeActive = !isBotModeActive;
    var buttons = document.querySelectorAll('button, a[role="button"], .btn');

    if (isBotModeActive) {
      buttons.forEach(function(b, idx) {
        if (!b.getAttribute('data-bot-tagged')) {
          b.setAttribute('data-bot-tagged', 'true');
          b.style.outline = '1.5px dashed rgba(56, 189, 248, 0.7)';
          b.style.outlineOffset = '2px';
        }
      });
      toast('🤖 [제29기관 봇 편성 모드 ON] 원하는 버튼을 클릭하면 Button-Bot으로 즉시 자율 실행됩니다 (Alt+B 해제)');
    } else {
      buttons.forEach(function(b) {
        b.removeAttribute('data-bot-tagged');
        b.style.outline = '';
        b.style.outlineOffset = '';
      });
      toast('🤖 [봇 편성 모드 OFF] 표준 인터랙션 모드로 복귀했습니다');
    }
  }

  // Alt+B 단축키 등록
  document.addEventListener('keydown', function(e) {
    if (e.altKey && (e.key === 'b' || e.key === 'B')) {
      e.preventDefault();
      toggleBotMode();
    }
  });

  window.toggleBotOverlayMode = toggleBotMode;
  window.RGON_BOT_RUNTIME = {
    version: 'v11.52-AON-PAGE-BUTTON-BOT',
    antibody: 'R1~R53',
    organ: 29,
    toggleBotMode: toggleBotMode,
    isBotModeActive: function() { return isBotModeActive; }
  };
})();
