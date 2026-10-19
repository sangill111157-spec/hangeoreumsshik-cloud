from pathlib import Path

inject_js = r"""
(function(){
  function enhanceVoiceModalClose() {
    var vp = document.getElementById('voice-custom-panel');
    if (!vp || document.getElementById('vp-top-close-btn')) return;

    // 1. 우측 상단 큼직한 [✖ 닫기] 버튼 주입
    var topClose = document.createElement('button');
    topClose.id = 'vp-top-close-btn';
    topClose.innerHTML = '✖ 닫기';
    topClose.style.cssText = 'position:absolute;top:12px;right:14px;padding:6px 14px;border-radius:8px;border:1px solid #ff6b6b;background:#450a0a;color:#fca5a5;font-weight:900;font-size:13px;cursor:pointer;z-index:10;';
    topClose.onclick = function() { vp.style.display = 'none'; };
    vp.appendChild(topClose);

    // 2. 하단 [✅ 설정 완료 및 닫기] 버튼 주입
    var botClose = document.createElement('button');
    botClose.id = 'vp-bot-close-btn';
    botClose.innerHTML = '✅ 설정 완료 및 창 닫기';
    botClose.style.cssText = 'margin-top:12px;width:100%;padding:11px;border-radius:10px;border:none;background:linear-gradient(90deg,#d4af37,#f59e0b);color:#070b14;font-weight:900;font-size:14px;cursor:pointer;box-shadow:0 4px 14px rgba(212,175,55,0.4);';
    botClose.onclick = function() { vp.style.display = 'none'; };
    vp.appendChild(botClose);
  }

  // ESC 키 누르면 즉시 닫기 & 패널 바깥 영역 클릭 시 닫기
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      var vp = document.getElementById('voice-custom-panel');
      if (vp) vp.style.display = 'none';
    }
  });
  document.addEventListener('mousedown', function(e) {
    var vp = document.getElementById('voice-custom-panel');
    var btn = document.getElementById('voice-settings-toggle-btn');
    if (vp && vp.style.display === 'block' && !vp.contains(e.target) && (!btn || !btn.contains(e.target))) {
      vp.style.display = 'none';
    }
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhanceVoiceModalClose);
  } else {
    enhanceVoiceModalClose();
  }
  setTimeout(enhanceVoiceModalClose, 500);
})();

window.openRealMultiTabsNow = function() {
  const urls = [
    'http://127.0.0.1:8501/departments/dept_closet.html',
    'http://127.0.0.1:8501/departments/dept_media.html',
    'https://suno.com/create',
    'https://studio.youtube.com',
    'https://www.tiktok.com/tiktokstudio/upload'
  ];
  urls.forEach((u, idx) => { setTimeout(() => window.open(u, '_blank'), idx * 250); });
};
window.showRealAsideControllerModal = function() {
  let m = document.getElementById('real-aside-action-bar');
  if (!m) {
    m = document.createElement('div');
    m.id = 'real-aside-action-bar';
    m.style.cssText = 'position:fixed;bottom:78px;left:50%;transform:translateX(-50%);width:min(95vw,760px);z-index:999998;background:linear-gradient(135deg,#0f172a,#1e1b4b);border:2px solid #d4af37;border-radius:14px;padding:12px 16px;box-shadow:0 15px 40px rgba(0,0,0,0.9);color:#fff;font-size:13px;';
    m.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <b style="color:#facc15;">💻 [노트북 어사이드 실물 행동대장 바] — 클립보드 자동 복사 완료!</b>
        <button onclick="document.getElementById('real-aside-action-bar').style.display='none'" style="padding:4px 10px;border-radius:6px;border:1px solid #f87171;background:#450a0a;color:#fca5a5;cursor:pointer;font-weight:bold;">✖ 닫기</button>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <button onclick="window.openRealMultiTabsNow()" style="flex:1;padding:9px;border-radius:8px;border:none;background:linear-gradient(90deg,#d4af37,#f59e0b);color:#000;font-weight:900;cursor:pointer;">🌐 1. 노트북에 5대 작업 웹창(퀀트·Suno·유튜브·틱톡) 지금 실제로 열기</button>
        <button onclick="navigator.clipboard.writeText('엄마는 나를 기다리다 밥을 식혔다 #어머니 #감동 #한걸음씩');alert('쇼츠 제목 복사 완료! Ctrl+V 하세요!');" style="padding:9px 12px;border-radius:8px;border:1px solid #38bdf8;background:#0f172a;color:#38bdf8;font-weight:bold;cursor:pointer;">📋 20:30 제목 복사</button>
        <button onclick="navigator.clipboard.writeText('엄마한테, 말 없이 이 영상만 보내세요. 오늘 밤 숙면 주파수 432Hz는 프로필에 열어두었습니다.');alert('432Hz 고정댓글 복사 완료!');" style="padding:9px 12px;border-radius:8px;border:1px solid #4ade80;background:#0f172a;color:#4ade80;font-weight:bold;cursor:pointer;">💬 고정댓글 복사</button>
      </div>
    `;
    document.body.appendChild(m);
  }
  m.style.display = 'block';
};
"""

for p in [Path('dashboard/rgon_alpha_chat.html'), Path('rgon_alpha_chat.html'), Path('docs/rgon_alpha_chat.html')]:
    if not p.exists(): continue
    txt = p.read_text(encoding='utf-8')
    if 'enhanceVoiceModalClose' not in txt:
        txt = txt.replace('</body>', '<script>' + inject_js + '</script>\n</body>')
        txt = txt.replace('id="all-in-one-omni-btn"', 'id="all-in-one-omni-btn" onclick="if(window.showRealAsideControllerModal)window.showRealAsideControllerModal();"')
        p.write_text(txt, encoding='utf-8')

print("CLOSE BUTTON & REAL MULTITAB PATCH COMPLETE!")
