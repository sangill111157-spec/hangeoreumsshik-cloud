(function() {
  if (document.getElementById('rgon-real-aside-ext-root')) return;
  const root = document.createElement('div');
  root.id = 'rgon-real-aside-ext-root';
  root.innerHTML = `
    <div id="rgon-ext-tab" style="position:fixed;bottom:140px;right:0;z-index:2147483647;background:linear-gradient(135deg,#d4af37,#b8860b);color:#070b14;font-weight:900;font-size:12px;padding:10px 12px;border-radius:12px 0 0 12px;cursor:pointer;box-shadow:0 6px 20px rgba(0,0,0,0.6);font-family:sans-serif;">
      👑 르곤-어사이드
    </div>
    <div id="rgon-ext-drawer" style="display:none;position:fixed;top:60px;right:12px;width:330px;z-index:2147483647;background:#0a101f;color:#fff;border:2px solid #d4af37;border-radius:16px;padding:16px;box-shadow:0 20px 50px rgba(0,0,0,0.9);font-family:sans-serif;">
      <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #2a3b5c;padding-bottom:10px;margin-bottom:12px;">
        <b style="color:#d4af37;font-size:14px;">👑 르곤-어사이드 실물 행동대장</b>
        <span id="rgon-ext-close" style="cursor:pointer;color:#ff6b6b;font-weight:bold;padding:2px 6px;">✖ 닫기</span>
      </div>
      <div style="font-size:12px;color:#94a3b8;margin-bottom:10px;">현재 사이트 입력칸에 원클릭으로 자동 타이핑 및 복사합니다:</div>
      <button id="rgon-btn-1" style="width:100%;margin-bottom:8px;padding:10px;border-radius:8px;border:none;background:#1e293b;color:#38bdf8;font-weight:bold;cursor:pointer;text-align:left;">📋 1. [20:30 어머니 쇼츠] 제목+태그 자동꽂기</button>
      <button id="rgon-btn-2" style="width:100%;margin-bottom:8px;padding:10px;border-radius:8px;border:none;background:#1e293b;color:#4ade80;font-weight:bold;cursor:pointer;text-align:left;">💬 2. [432Hz 고정댓글] 입력칸에 자동꽂기</button>
      <button id="rgon-btn-3" style="width:100%;margin-bottom:8px;padding:10px;border-radius:8px;border:none;background:#1e293b;color:#f472b6;font-weight:bold;cursor:pointer;text-align:left;">🎵 3. [Suno 62BPM 발라드] 프롬프트 꽂기</button>
      <button id="rgon-btn-4" style="width:100%;margin-bottom:8px;padding:10px;border-radius:8px;border:none;background:#1e293b;color:#facc15;font-weight:bold;cursor:pointer;text-align:left;">☕ 4. [22:10 카페 로파이 78BPM] 프롬프트 꽂기</button>
      <button id="rgon-btn-5" style="width:100%;padding:10px;border-radius:8px;border:none;background:linear-gradient(90deg,#d4af37,#f59e0b);color:#000;font-weight:900;cursor:pointer;">🏛️ 1:1 전담 독대실 새 탭 열기</button>
      <div id="rgon-ext-status" style="margin-top:10px;font-size:12px;color:#4ade80;font-weight:bold;min-height:18px;"></div>
    </div>
  `;
  document.body.appendChild(root);

  const tab = document.getElementById('rgon-ext-tab');
  const drawer = document.getElementById('rgon-ext-drawer');
  const status = document.getElementById('rgon-ext-status');
  tab.onclick = () => { drawer.style.display = drawer.style.display === 'block' ? 'none' : 'block'; };
  document.getElementById('rgon-ext-close').onclick = () => { drawer.style.display = 'none'; };

  function autoFillAndCopy(text, label) {
    navigator.clipboard.writeText(text).catch(()=>{});
    const el = document.activeElement;
    let filled = false;
    if (el && (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT')) {
      el.value = text;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      filled = true;
    } else {
      const target = document.querySelector('textarea, [contenteditable="true"], input[type="text"]');
      if (target) {
        if (target.isContentEditable) target.innerText = text;
        else target.value = text;
        target.dispatchEvent(new Event('input', { bubbles: true }));
        filled = true;
      }
    }
    status.innerText = filled ? `✅ [${label}] 입력칸 자동주입 & 클립보드 복사 완료!` : `✅ [${label}] 클립보드 복사 완료! (Ctrl+V 하세요)`;
  }

  document.getElementById('rgon-btn-1').onclick = () => autoFillAndCopy("엄마는 나를 기다리다 밥을 식혔다 #어머니 #감동 #한걸음씩 #효도 #눈물", "20:30 쇼츠 제목");
  document.getElementById('rgon-btn-2').onclick = () => autoFillAndCopy("엄마한테, 말 없이 이 영상만 보내세요. 오늘 밤 숙면 주파수 432Hz는 프로필에 열어두었습니다.", "고정 댓글");
  document.getElementById('rgon-btn-3').onclick = () => autoFillAndCopy("Intimate Korean emotional ballad, 62 BPM, A minor, solo warm felt piano and deep cello, nostalgic, no vocals, 30s seamless loop", "Suno 62BPM");
  document.getElementById('rgon-btn-4').onclick = () => autoFillAndCopy("Seoul rainy night cafe lo-fi jazz, 78 BPM, warm Rhodes electric piano, subtle vinyl crackle and gentle rain ambiance, 24s loop", "Suno 78BPM");
  document.getElementById('rgon-btn-5').onclick = () => window.open("http://127.0.0.1:8501/rgon_alpha_chat.html", "_blank");
})();