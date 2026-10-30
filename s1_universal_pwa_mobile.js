(function(){
  if(window.__S1_UNIVERSAL_PWA__)return; window.__S1_UNIVERSAL_PWA__=true;
  var deferredPrompt=null;
  window.addEventListener("beforeinstallprompt",function(e){e.preventDefault();deferredPrompt=e;var b=document.getElementById("s1-pwa-install-btn");if(b)b.style.display="inline-flex";});
  function injectPwaTags(){
    if(!document.querySelector("link[rel=\"manifest\"]")){var l=document.createElement("link");l.rel="manifest";l.href="./manifest.webmanifest";document.head.appendChild(l);}
    if(!document.querySelector("meta[name=\"apple-mobile-web-app-capable\"]")){var m=document.createElement("meta");m.name="apple-mobile-web-app-capable";m.content="yes";document.head.appendChild(m);}
    if("serviceWorker" in navigator){navigator.serviceWorker.register("./sw.js").catch(function(){});}
  }
  function mountS1MobileBar(){
    if(document.getElementById("s1-universal-mobile-bar"))return;
    var css=document.createElement("style");
    css.textContent="@media (max-width:768px){body,html{max-width:100vw!important;overflow-x:hidden!important;-webkit-text-size-adjust:100%!important;} #hq-comm-form{padding-bottom:env(safe-area-inset-bottom,8px)!important;position:sticky!important;bottom:0!important;z-index:999999!important;background:rgba(15,23,42,0.98)!important;}} #s1-universal-mobile-bar{position:sticky;top:0;z-index:2147483640;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px;padding:8px 12px;background:linear-gradient(90deg,#0f172a,#1e1b4b,#064e3b);border-bottom:1px solid #38bdf8;color:#f8fafc;font-size:12px;font-family:system-ui,sans-serif;} .s1-ubtn{background:rgba(56,189,248,0.2);border:1px solid #38bdf8;color:#fff;padding:5px 10px;border-radius:8px;font-size:11.5px;font-weight:700;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;gap:4px;} .s1-ubtn:active{transform:scale(0.96);}";
    document.head.appendChild(css);
    var bar=document.createElement("div"); bar.id="s1-universal-mobile-bar";
    bar.innerHTML="<div>☀️ <b>S1 중앙컨트롤타워</b> · 8대코어 & V3검증 ON</div><div style=\"display:flex;gap:6px;align-items:center;\"><a class=\"s1-ubtn\" href=\"./index.html\">��️ 타워본관</a><a class=\"s1-ubtn\" href=\"./rgon_alpha_chat.html\">�� 만능소통창</a><button type=\"button\" id=\"s1-pwa-install-btn\" class=\"s1-ubtn\" style=\"background:linear-gradient(135deg,#10b981,#059669);border-color:#34d399;\">�� 앱 설치</button></div>";
    document.body.insertBefore(bar,document.body.firstChild);
    document.getElementById("s1-pwa-install-btn").onclick=function(){
      if(deferredPrompt){deferredPrompt.prompt();deferredPrompt.userChoice.then(function(){deferredPrompt=null;});}
      else{alert("�� [전 브라우저 설치 안내]\n• 크롬/엣지/에고라이트: 주소창 우측 [앱 설치] 아이콘 클릭\n• 삼성인터넷/크롬(모바일): 메뉴(⋮) ➔ [홈 화면에 추가]\n• 아이폰(Safari): 하단 공유(⬆️) ➔ [홈 화면에 추가]를 누르시면 즉시 독립 앱으로 설치됩니다!");}
    };
  }
  if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",function(){injectPwaTags();mountS1MobileBar();});}else{injectPwaTags();mountS1MobileBar();}
})();