import os, subprocess
from pathlib import Path

# 1. rgon_alpha_chat.html의 triggerAllInOneOmni에 실제 멀티탭 팝업 컨트롤러 & 클립보드 실제 복사 장착
modal_js = r"""
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
        <b style="color:#facc15;">💻 [노트북 어사이드 실물 행동대장 바] — 클립보드에 오늘 쇼츠 패키지 자동 복사 완료!</b>
        <span onclick="this.parentElement.parentElement.style.display='none'" style="cursor:pointer;color:#f87171;font-weight:bold;">✖ 닫기</span>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <button onclick="window.openRealMultiTabsNow()" style="flex:1;padding:9px;border-radius:8px;border:none;background:linear-gradient(90deg,#d4af37,#f59e0b);color:#000;font-weight:900;cursor:pointer;">🌐 1. 노트북에 5대 작업 웹창(퀀트·Suno·유튜브·틱톡) 지금 실제로 열기</button>
        <button onclick="navigator.clipboard.writeText('엄마는 나를 기다리다 밥을 식혔다 #어머니 #감동 #한걸음씩');alert('쇼츠 제목 복사 완료! 유튜브/틱톡 창에서 Ctrl+V 하세요!');" style="padding:9px 12px;border-radius:8px;border:1px solid #38bdf8;background:#0f172a;color:#38bdf8;font-weight:bold;cursor:pointer;">📋 20:30 제목 복사</button>
        <button onclick="navigator.clipboard.writeText('엄마한테, 말 없이 이 영상만 보내세요. 오늘 밤 숙면 주파수 432Hz는 프로필에 열어두었습니다.');alert('432Hz 고정댓글 복사 완료!');" style="padding:9px 12px;border-radius:8px;border:1px solid #4ade80;background:#0f172a;color:#4ade80;font-weight:bold;cursor:pointer;">💬 고정댓글 복사</button>
        <button onclick="navigator.clipboard.writeText('Intimate Korean emotional ballad, 62 BPM, A minor, solo warm felt piano and deep cello, nostalgic, no vocals, 30s seamless loop');alert('Suno 62BPM 프롬프트 복사 완료!');" style="padding:9px 12px;border-radius:8px;border:1px solid #f472b6;background:#0f172a;color:#f472b6;font-weight:bold;cursor:pointer;">🎵 Suno 62BPM 복사</button>
      </div>
    `;
    document.body.appendChild(m);
  }
  m.style.display = 'block';
  navigator.clipboard.writeText('엄마는 나를 기다리다 밥을 식혔다 #어머니 #감동 #한걸음씩\n\n[고정댓글]: 엄마한테, 말 없이 이 영상만 보내세요. 오늘 밤 숙면 주파수 432Hz는 프로필에 열어두었습니다.').catch(()=>{});
};
"""

for p in [Path('dashboard/rgon_alpha_chat.html'), Path('rgon_alpha_chat.html'), Path('docs/rgon_alpha_chat.html')]:
    if not p.exists(): continue
    txt = p.read_text(encoding='utf-8')
    if 'showRealAsideControllerModal' not in txt:
        txt = txt.replace('</script>\n</body>', modal_js + '\n</script>\n</body>')
        txt = txt.replace('id="all-in-one-omni-btn"', 'id="all-in-one-omni-btn" onclick="if(window.showRealAsideControllerModal)window.showRealAsideControllerModal();"')
        p.write_text(txt, encoding='utf-8')

# 2. 윈도우 클립보드에 오늘 자 골든타임 패키지 실제 장전 및 확장프로그램 폴더 탐색기 자동 팝업
clip_text = "엄마는 나를 기다리다 밥을 식혔다 #어머니 #감동 #한걸음씩\n[고정댓글] 엄마한테, 말 없이 이 영상만 보내세요. 오늘 밤 숙면 주파수 432Hz는 프로필에 열어두었습니다."
subprocess.run(['powershell', '-Command', f'Set-Clipboard -Value "{clip_text}"'], check=False)

ext_path = Path('rgon_aside_extension').resolve()
os.startfile(str(ext_path))
print("FAST PATCH 3 COMPLETE! Opened folder:", ext_path)
