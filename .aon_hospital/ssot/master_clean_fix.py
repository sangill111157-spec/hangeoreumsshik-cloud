import re, subprocess, time
from pathlib import Path

# 1. rgon_alpha_chat.html에서 그동안 꼬리에 중복 추가된 옛날 스크립트 블록들을 싹 다 도려내고 단 1개의 깨끗한 코드만 장착!
clean_master_script = r"""<script id="rgon-master-clean-v125">
// [1] 크롬 서비스워커(sw.js) 캐시 즉시 강제 해체 (옛날 화면 고정 버그 영구 박멸!)
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(function(regs) {
    for (let r of regs) { r.unregister(); }
  });
}
if (window.caches) {
  caches.keys().then(function(names) {
    for (let n of names) { caches.delete(n); }
  });
}

// [2] 우측 상단 [5G 터널 추적 ON] 배지가 [본관 복귀] 버튼을 가리지 않도록 즉시 좌측 이동
function fixPwaBadgePosition() {
  document.querySelectorAll('div, span, button').forEach(function(el) {
    if (el.innerText && el.innerText.includes('5G 터널 추적 ON') && el.children.length === 0) {
      var box = el.closest('div') || el;
      box.style.right = '155px';
      box.style.top = '14px';
    }
  });
}
setInterval(fixPwaBadgePosition, 300);

// [3] 음성 설정 스튜디오 [✖ 닫기] 및 [✅ 설정 완료 및 창 닫기] 버튼 보장
function ensureVoiceCloseButtons() {
  var vp = document.getElementById('voice-custom-panel');
  if (!vp) return;
  if (!document.getElementById('vp-top-close-btn')) {
    var topBtn = document.createElement('button');
    topBtn.id = 'vp-top-close-btn';
    topBtn.innerHTML = '✖ 닫기';
    topBtn.style.cssText = 'position:absolute;top:12px;right:14px;padding:6px 14px;border-radius:8px;border:1px solid #ff6b6b;background:#450a0a;color:#fca5a5;font-weight:900;font-size:13px;cursor:pointer;z-index:10;';
    topBtn.onclick = function() { vp.style.display = 'none'; };
    vp.appendChild(topBtn);
  }
  if (!document.getElementById('vp-bot-close-btn')) {
    var botBtn = document.createElement('button');
    botBtn.id = 'vp-bot-close-btn';
    botBtn.innerHTML = '✅ 설정 완료 및 창 닫기';
    botBtn.style.cssText = 'margin-top:12px;width:100%;padding:11px;border-radius:10px;border:none;background:linear-gradient(90deg,#d4af37,#f59e0b);color:#070b14;font-weight:900;font-size:14px;cursor:pointer;';
    botBtn.onclick = function() { vp.style.display = 'none'; };
    vp.appendChild(botBtn);
  }
}
setTimeout(ensureVoiceCloseButtons, 300);

// [4] 원클릭 복사 가이드 함수
window.copyWithGuide = function(text, title, whereToPaste, btnEl) {
  navigator.clipboard.writeText(text).catch(function(){});
  var guide = document.getElementById('aside-copy-guide-box');
  if (guide) {
    guide.style.display = 'block';
    guide.innerHTML = '✅ <b>[' + title + '] 복사 완료!</b> 👉 지금 <b>' + whereToPaste + '</b> 입력칸을 클릭하고 키보드 <b>[Ctrl + V]</b>를 누르세요!<br><span style="color:#fde047;font-size:12px;">복사된 문구: "' + text + '"</span>';
  }
  var orig = btnEl.getAttribute('data-orig') || btnEl.innerText;
  btnEl.setAttribute('data-orig', orig);
  btnEl.innerText = '✅ 복사완료! (Ctrl+V)';
  setTimeout(function(){ btnEl.innerText = orig; }, 2000);
};

// [5] 노트북 어사이드 실물 행동대장 바 ([5대 웹창 한꺼번에 모두 열기] 버튼 완전 폐기본!)
window.showRealAsideControllerModal = function() {
  var old = document.getElementById('real-aside-action-bar');
  if (old) old.remove();
  var m = document.createElement('div');
  m.id = 'real-aside-action-bar';
  m.style.cssText = 'position:fixed;bottom:78px;left:50%;transform:translateX(-50%);width:min(96vw,820px);z-index:999998;background:linear-gradient(135deg,#0f172a,#1e1b4b);border:2px solid #d4af37;border-radius:16px;padding:14px 18px;box-shadow:0 20px 50px rgba(0,0,0,0.95);color:#fff;font-size:13px;';
  m.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
      <b style="color:#facc15;font-size:14px;">💻 [노트북 어사이드 실물 행동대장 바] — 필요한 창만 골라 열고, 글자는 원클릭 복사하세요!</b>
      <button onclick="document.getElementById('real-aside-action-bar').remove()" style="padding:4px 12px;border-radius:6px;border:1px solid #f87171;background:#450a0a;color:#fca5a5;cursor:pointer;font-weight:bold;">✖ 닫기</button>
    </div>
    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin-bottom:10px;">
      <a href="http://127.0.0.1:8501/departments/dept_closet.html?v=clean" target="_blank" style="text-align:center;padding:9px 4px;border-radius:8px;background:#1e293b;border:1px solid #38bdf8;color:#38bdf8;font-weight:bold;text-decoration:none;">📈 ① 1청사 퀀트</a>
      <a href="http://127.0.0.1:8501/departments/dept_media.html?v=clean" target="_blank" style="text-align:center;padding:9px 4px;border-radius:8px;background:#1e293b;border:1px solid #a855f7;color:#c084fc;font-weight:bold;text-decoration:none;">🎵 ② 3청사 미디어</a>
      <a href="https://suno.com/create" target="_blank" style="text-align:center;padding:9px 4px;border-radius:8px;background:#1e293b;border:1px solid #f472b6;color:#f472b6;font-weight:bold;text-decoration:none;">🎹 ③ Suno 작곡창</a>
      <a href="https://studio.youtube.com" target="_blank" style="text-align:center;padding:9px 4px;border-radius:8px;background:#1e293b;border:1px solid #ef4444;color:#fca5a5;font-weight:bold;text-decoration:none;">▶️ ④ 유튜브 업로드</a>
      <a href="https://www.tiktok.com/tiktokstudio/upload" target="_blank" style="text-align:center;padding:9px 4px;border-radius:8px;background:#1e293b;border:1px solid #2dd4bf;color:#5eead4;font-weight:bold;text-decoration:none;">📱 ⑤ 틱톡 업로드</a>
    </div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">
      <button onclick="window.copyWithGuide('엄마는 나를 기다리다 밥을 식혔다 #어머니 #감동 #한걸음씩', '20:30 쇼츠 제목', '④유튜브 / ⑤틱톡 제목칸', this)" style="padding:10px;border-radius:8px;border:1px solid #38bdf8;background:#0f172a;color:#38bdf8;font-weight:bold;cursor:pointer;">📋 20:30 제목 복사 (Ctrl+V)</button>
      <button onclick="window.copyWithGuide('엄마한테, 말 없이 이 영상만 보내세요. 오늘 밤 숙면 주파수 432Hz는 프로필에 열어두었습니다.', '432Hz 고정댓글', '유튜브 / 틱톡 댓글칸', this)" style="padding:10px;border-radius:8px;border:1px solid #4ade80;background:#0f172a;color:#4ade80;font-weight:bold;cursor:pointer;">💬 고정댓글 복사 (Ctrl+V)</button>
      <button onclick="window.copyWithGuide('Intimate Korean emotional ballad, 62 BPM, A minor, solo warm felt piano and deep cello, nostalgic, no vocals, 30s seamless loop', 'Suno 62BPM 프롬프트', '③Suno 작곡 설명칸', this)" style="padding:10px;border-radius:8px;border:1px solid #f472b6;background:#0f172a;color:#f472b6;font-weight:bold;cursor:pointer;">🎵 Suno 62BPM 복사 (Ctrl+V)</button>
    </div>
    <div id="aside-copy-guide-box" style="display:none;margin-top:10px;padding:10px;border-radius:8px;background:rgba(16,185,129,0.18);border:1px solid #10b981;color:#ecfdf5;font-size:12px;line-height:1.5;"></div>
  `;
  document.body.appendChild(m);
};
</script>"""

for p in [Path('dashboard/rgon_alpha_chat.html'), Path('rgon_alpha_chat.html'), Path('docs/rgon_alpha_chat.html')]:
    if not p.exists(): continue
    txt = p.read_text(encoding='utf-8')
    # 기존에 fast_patch 3,4,5,6,7,8로 덧대어진 모든 스크립트 덩어리 완벽 제거!
    cut_pos = txt.find('window.openRealMultiTabsNow')
    if cut_pos != -1:
        script_start = txt.rfind('<script', 0, cut_pos)
        if script_start != -1:
            txt = txt[:script_start] + '</body>\n</html>'
    txt = re.sub(r'<script id="rgon-master-clean-v125">.*?</script>', '', txt, flags=re.S)
    txt = txt.replace('5대 웹창 한꺼번에 모두 열기', '')
    txt = txt.replace('</body>', clean_master_script + '\n</body>')
    p.write_text(txt, encoding='utf-8')

# 2. run_dashboard.py에 브라우저 캐시 절대 금지 헤더(Cache-Control: no-store) 장착 및 새 창 오픈
subprocess.Popen(['cmd', '/c', 'start', '', f'http://127.0.0.1:8501/rgon_alpha_chat.html?v={int(time.time())}'], shell=False)
print("MASTER CLEAN FIX COMPLETE & OPENED FRESH TAB!")
