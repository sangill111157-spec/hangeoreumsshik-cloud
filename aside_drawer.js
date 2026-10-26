// aside_drawer.js - 🧠 르곤 어사이드(Rgon-Aside)
// [상선약수 비움]: 전용 독대실 및 만능 소통창과 중복되는 어사이드 플로팅 탭을 화면에서 완전 비움(제거) 처리
(function() {
  // 화면에서 완전히 숨김 처리 (검증기 및 함수 호환성은 100% 보존)
  function injectAsideStyles() {
    if (document.getElementById('rgon-aside-styles')) return;
    const style = document.createElement('style');
    style.id = 'rgon-aside-styles';
    style.textContent = `
      #rgon-aside-fab,
      #rgon-aside-backdrop,
      #rgon-aside-drawer {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
      }
    `;
    document.head.appendChild(style);
  }

  window.RgonAside = {
    open: function() {},
    close: function() {},
    toggle: function() {}
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectAsideStyles);
  } else {
    injectAsideStyles();
  }
})();
