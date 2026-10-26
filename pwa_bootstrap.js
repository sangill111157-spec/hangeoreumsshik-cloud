/* RGON_LOCAL_SW_GUARD_START */
(function(){
  if(/^(127\.0\.0\.1|localhost)$/.test(location.hostname) && "serviceWorker" in navigator){
    var fake={update:function(){},unregister:function(){return Promise.resolve(true);},addEventListener:function(){},installing:null,waiting:null,active:null};
    try{ navigator.serviceWorker.register=function(){ return Promise.resolve(fake); }; }catch(e){}
  }
})();
/* RGON_LOCAL_SW_GUARD_END */
// pwa_bootstrap.js - 청와대 AI 중앙 컨트롤타워 PWA 부트스트랩 및 터널 자동 추적 브릿지
(function() {
  'use strict';

  let deferredPrompt = null;
  let activeTunnelUrl = null;

  // 1. 서비스 워커 등록
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js')
        .then((reg) => {
          console.log('[PWA] 서비스 워커 등록 성공:', reg.scope);
        })
        .catch((err) => {
          console.warn('[PWA] 서비스 워커 등록 건너뜀 또는 실패:', err);
        });
    });
  }

  // 2. 스마트폰 앱 설치 프롬프트 감지
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    updatePwaBadge(true);
  });

  window.addEventListener('appinstalled', () => {
    console.log('[PWA] 스마트폰 홈 화면 앱 설치 완료!');
    deferredPrompt = null;
    updatePwaBadge(false, true);
  });

  // 3. UI 플로팅/헤더 PWA & 터널 상태 배지 주입
  function injectPwaUI() {
    if (document.getElementById('rgon-pwa-bridge-bar')) return;

    const isChatPage = window.location.pathname.toLowerCase().includes('rgon_alpha_chat');
    const bar = document.createElement('div');
    bar.id = 'rgon-pwa-bridge-bar';
    bar.style.cssText = isChatPage ? `
      position: fixed;
      top: 14px;
      right: 145px;
      bottom: auto;
      z-index: 99999;
      display: none !important;
      align-items: center;
      gap: 6px;
      background: rgba(7, 11, 20, 0.92);
      border: 1px solid #d4af37;
      border-radius: 16px;
      padding: 4px 10px;
      font-size: 10px;
      color: #e6edf3;
      box-shadow: 0 2px 12px rgba(0,0,0,0.6);
      backdrop-filter: blur(8px);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    ` : `
      position: fixed;
      bottom: 12px;
      right: 145px;
      z-index: 99999;
      display: none !important;
      align-items: center;
      gap: 8px;
      background: rgba(7, 11, 20, 0.92);
      border: 1px solid #d4af37;
      border-radius: 24px;
      padding: 6px 14px;
      font-size: 11px;
      color: #e6edf3;
      box-shadow: 0 4px 20px rgba(0,0,0,0.6);
      backdrop-filter: blur(8px);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;

    bar.innerHTML = `
      <span id="pwa-tunnel-indicator" style="display:inline-flex; align-items:center; gap:4px; color:#22c55e;">
        <span style="width:8px; height:8px; border-radius:50%; background:#22c55e; box-shadow:0 0 8px #22c55e;"></span>
        <span>5G 터널 추적 ON</span>
      </span>
      <button id="pwa-install-btn" style="
        background: linear-gradient(135deg, #d4af37, #aa820a);
        color: #070b14;
        border: none;
        border-radius: 12px;
        padding: 4px 10px;
        font-weight: 700;
        cursor: pointer;
        font-size: 11px;
        display: none;
      ">📲 앱 설치</button>
    `;

    document.body.appendChild(bar);

    const installBtn = document.getElementById('pwa-install-btn');
    installBtn.addEventListener('click', async () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log('[PWA] 설치 선택 결과:', outcome);
        deferredPrompt = null;
        installBtn.style.display = 'none';
      } else {
        alert('홈 화면에 추가하거나 브라우저 메뉴에서 [앱 설치]를 선택하실 수 있습니다.');
      }
    });
  }

  function updatePwaBadge(canInstall, isInstalled) {
    const installBtn = document.getElementById('pwa-install-btn');
    if (!installBtn) return;
    if (canInstall) {
      installBtn.style.display = 'inline-block';
    } else if (isInstalled) {
      installBtn.style.display = 'none';
      const ind = document.getElementById('pwa-tunnel-indicator');
      if (ind) ind.innerHTML += ' <span style="color:#d4af37;">(PWA 실행중)</span>';
    }
  }

  // 4. 무중단 터널 브릿지 감시자 (30초 주기 폴링)
  async function monitorTunnelBridge() {
    try {
      const res = await fetch('/tunnel_bridge.json?_t=' + Date.now(), { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        const liveUrl = data.active_url || data.tunnel_url;
        if (liveUrl) {
          activeTunnelUrl = liveUrl;
          const currentOrigin = window.location.origin;
          // 만약 현재 origin이 trycloudflare 호스트이고 새 터널과 도메인이 달라졌다면 무중단 재접속 안내
          if (currentOrigin.includes('trycloudflare.com') && !liveUrl.includes(window.location.hostname)) {
            console.warn('[PWA Bridge] 터널 주소 갱신 감지! 새 터널:', liveUrl);
            const banner = document.getElementById('pwa-tunnel-indicator');
            if (banner) {
              banner.innerHTML = `<a href="${liveUrl + window.location.pathname}" style="color:#f59e0b; text-decoration:underline;">새 터널로 이동</a>`;
            }
          }
        }
      }
    } catch (e) {
      // 오프라인이거나 일시적 통신 단절
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      injectPwaUI();
      monitorTunnelBridge();
      setInterval(monitorTunnelBridge, 30000);
    });
  } else {
    injectPwaUI();
    monitorTunnelBridge();
    setInterval(monitorTunnelBridge, 30000);
  }
})();

/* RGON_STEP2_BEGIN */
;(function () {
  'use strict';
  if (window.__RGON_STEP2_TUNNEL__) { return; }
  window.__RGON_STEP2_TUNNEL__ = true;

  var RE = /5G\s*\ud130\ub110\s*\ucd94\uc801/;
  var STYLE_ID = 'rgon-step2-tunnel-style';
  var CSS = '.rgon-tunnel-badge{white-space:nowrap !important;width:max-content !important;max-width:90vw !important;word-break:keep-all !important;overflow-wrap:normal !important;writing-mode:horizontal-tb !important;box-sizing:border-box !important;}' +
    '@media (max-width:768px){html.rgon-dokdae-page .rgon-tunnel-badge{position:fixed !important;top:auto !important;left:auto !important;right:6px !important;bottom:6px !important;transform:none !important;margin:0 !important;padding:2px 7px !important;font-size:10px !important;line-height:1.25 !important;opacity:0.72 !important;pointer-events:none !important;z-index:40 !important;}}';

  function isDokdae() {
    try { return /rgon_alpha_chat/i.test(location.pathname) || !!document.getElementById('dokdae-feed'); }
    catch (e) { return false; }
  }
  function norm(el) { return (el.textContent || '').replace(/\s+/g, ' ').trim(); }
  function ensureStyle() {
    if (document.getElementById(STYLE_ID)) { return; }
    var host = document.head || document.documentElement;
    if (!host) { return; }
    var st = document.createElement('style');
    st.id = STYLE_ID;
    st.textContent = CSS;
    host.appendChild(st);
  }
  function tag(el) {
    var base = norm(el);
    var cur = el;
    var n = 0;
    while (cur && cur !== document.body && cur !== document.documentElement && n < 4) {
      if (n > 0 && norm(cur) !== base) { break; }
      cur.classList.add('rgon-tunnel-badge');
      cur = cur.parentElement;
      n++;
    }
  }
  function tagNode(node) {
    var el = node.parentElement;
    if (!el || el.classList.contains('rgon-tunnel-badge')) { return; }
    if (norm(el).length > 80) {
      var sp = document.createElement('span');
      node.parentNode.insertBefore(sp, node);
      sp.appendChild(node);
      el = sp;
    }
    tag(el);
  }
  function scan() {
    if (!document.body) { return; }
    ensureStyle();
    if (isDokdae()) { document.documentElement.classList.add('rgon-dokdae-page'); }
    var w;
    try {
      w = document.createTreeWalker(document.body, 5, { acceptNode: function (n) {
        if (n.nodeType === 1) {
          var t = n.tagName;
          if (t === 'SCRIPT' || t === 'STYLE' || t === 'NOSCRIPT' || t === 'TEXTAREA' || n.id === 'dokdae-feed') { return 2; }
          return 3;
        }
        var v = n.nodeValue;
        return (v && v.length < 100 && RE.test(v)) ? 1 : 3;
      } });
    } catch (e) { return; }
    var hits = [];
    var node;
    while ((node = w.nextNode())) { hits.push(node); }
    hits.forEach(tagNode);
  }

  var timer = null;
  function sched() {
    if (timer) { return; }
    timer = setTimeout(function () {
      timer = null;
      try { scan(); } catch (e) {}
    }, 350);
  }
  function boot() {
    try { scan(); } catch (e) {}
    setTimeout(function () { try { scan(); } catch (e) {} }, 600);
    setTimeout(function () { try { scan(); } catch (e) {} }, 1800);
    var n = 0;
    var iv = setInterval(function () {
      try { scan(); } catch (e) {}
      if (++n >= 20) { clearInterval(iv); }
    }, 3000);
    try {
      var mo = new MutationObserver(sched);
      mo.observe(document.body, { childList: true, subtree: true });
    } catch (e) {}
  }
  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', boot); }
  else { boot(); }
})();
/* RGON_STEP2_END */
