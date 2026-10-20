from pathlib import Path
import re

clean_bar_js = r'''
window.showRealAsideControllerModal = function() {
  let m = document.getElementById('real-aside-action-bar');
  if (m) m.remove();
  m = document.createElement('div');
  m.id = 'real-aside-action-bar';
  m.style.cssText = 'position:fixed;bottom:78px;left:50%;transform:translateX(-50%);width:min(96vw,820px);z-index:999998;background:linear-gradient(135deg,#0f172a,#1e1b4b);border:2px solid #d4af37;border-radius:16px;padding:14px 18px;box-shadow:0 20px 50px rgba(0,0,0,0.95);color:#fff;font-size:13px;';
  m.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
      <b style="color:#facc15;font-size:14px;">💻 [노트북 어사이드 실물 행동대장 바] — 필요한 창만 골라 열고, 글자는 원클릭 복사하세요!</b>
      <button onclick="document.getElementById('real-aside-action-bar').style.display='none'" style="padding:4px 12px;border-radius:6px;border:1px solid #f87171;background:#450a0a;color:#fca5a5;cursor:pointer;font-weight:bold;">✖ 닫기</button>
    </div>
    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin-bottom:10px;">
      <a href="http://127.0.0.1:8501/departments/dept_closet.html" target="_blank" style="text-align:center;padding:9px 4px;border-radius:8px;background:#1e293b;border:1px solid #38bdf8;color:#38bdf8;font-weight:bold;text-decoration:none;">📈 ① 1청사 퀀트</a>
      <a href="http://127.0.0.1:8501/departments/dept_media.html" target="_blank" style="text-align:center;padding:9px 4px;border-radius:8px;background:#1e293b;border:1px solid #a855f7;color:#c084fc;font-weight:bold;text-decoration:none;">🎵 ② 3청사 미디어</a>
      <a href="https://suno.com/create" target="_blank" style="text-align:center;padding:9px 4px;border-radius:8px;background:#1e293b;border:1px solid #f472b6;color:#f472b6;font-weight:bold;text-decoration:none;">🎹 ③ Suno 작곡창</a>
      <a href="https://studio.youtube.com" target="_blank" style="text-align:center;padding:9px 4px;border-radius:8px;background:#1e293b;border:1px solid #ef4444;color:#fca5a5;font-weight:bold;text-decoration:none;">▶️ ④ 유튜브 업로드</a>
      <a href="https://www.tiktok.com/tiktokstudio/upload" target="_blank" style="text-align:center;padding:9px 4px;border-radius:8px;background:#1e293b;border:1px solid #2dd4bf;color:#5eead4;font-weight:bold;text-decoration:none;">📱 ⑤ 틱톡 업로드</a>
    </div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">
      <button onclick="window.copyWithGuide('엄마는 나를 기다리다 밥을 식혔다 #어머니 #감동 #한걸음씩', '20:30 쇼츠 제목', '④유튜브 / ⑤틱톡 제목칸', this)" style="padding:10px;border-radius:8px;border:1px solid #38bdf8;background:#0f172a;color:#38bdf8;font-weight:bold;cursor:pointer;">📋 20:30 제목 복사 (Ctrl+V)</button>
      <button onclick="window.copyWithGuide('엄마한테, 말 없이 이 영상만 보내세요. 오늘 밤 숙면 주파수 432Hz는 프로필에 열어두었습니다.', '432Hz 고정댓글', '유튜브 / 틱톡 댓글칸', this)" style="padding:10px;border-radius:8px;border:1px solid #4ade80;background:#0f172a;color:#4ade80;font-weight:bold;cursor:pointer;">💬 고정댓글 복사 (Ctrl+V)</button>
      <button onclick="window.copyWithGuide('Intimate Korean emotional ballad, 62 BPM, A minor, solo warm felt piano and deep cello, nostalgic, no vocals, 30s seamless loop', 'Suno 62BPM 프롬프트', '③Suno 작곡 설명칸', this)" style="padding:10px;border-radius:8px;border:1px solid #f472b6;background:#0f172a;color:#f472b6;font-weight:bold;cursor:pointer;">🎵 Suno 62BPM 복사 (Ctrl+V)</button>
    </div>
    <div id="aside-copy-guide-box" style="display:none;margin-top:10px;padding:10px;border-radius:8px;background:rgba(16,185,129,0.15);border:1px solid #10b981;color:#ecfdf5;font-size:12px;line-height:1.5;"></div>
  `;
  document.body.appendChild(m);
};
'''

for p in [Path('dashboard/rgon_alpha_chat.html'), Path('rgon_alpha_chat.html'), Path('docs/rgon_alpha_chat.html')]:
    if not p.exists(): continue
    txt = p.read_text(encoding='utf-8')
    txt = txt.replace('</body>', '<script>' + clean_bar_js + '</script>\n</body>')
    p.write_text(txt, encoding='utf-8')

print('FAST PATCH 8 (REMOVED BULK OPEN BTN) COMPLETE!')
