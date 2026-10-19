import shutil
from pathlib import Path

for p in [Path('dashboard/rgon_alpha_chat.html'), Path('rgon_alpha_chat.html'), Path('docs/rgon_alpha_chat.html')]:
    if not p.exists(): continue
    txt = p.read_text(encoding='utf-8')
    # 1. voice-custom-panel을 화면 최상단 중앙 팝업으로 강제 변환
    txt = txt.replace('id="voice-custom-panel"', 'id="voice-custom-panel" style="display:none; position:fixed; top:120px; left:50%; transform:translateX(-50%); width:min(92vw,620px); z-index:999999; background:#0b1326; border:2px solid #d4af37; border-radius:16px; padding:18px; box-shadow:0 25px 60px rgba(0,0,0,0.95);"')
    # 2. 버튼에 직접 인라인 onclick 장착
    txt = txt.replace('id="voice-settings-toggle-btn"', 'id="voice-settings-toggle-btn" onclick="var vp=document.getElementById(\'voice-custom-panel\'); if(vp){vp.style.display=(vp.style.display===\'block\'?\'none\':\'block\'); if(window.populateVoiceActors)window.populateVoiceActors();}"')
    p.write_text(txt, encoding='utf-8')

for p in [Path('pwa_bootstrap.js'), Path('dashboard/pwa_bootstrap.js'), Path('docs/pwa_bootstrap.js')]:
    if not p.exists(): continue
    txt = p.read_text(encoding='utf-8')
    txt = txt.replace('right: 76px', 'right: 140px').replace('top: 10px', 'top: 14px')
    p.write_text(txt, encoding='utf-8')

for p in [Path('aside_drawer.js'), Path('dashboard/aside_drawer.js'), Path('docs/aside_drawer.js')]:
    if not p.exists(): continue
    txt = p.read_text(encoding='utf-8')
    txt = txt.replace('top: 68px', 'top: auto; bottom: 92px')
    p.write_text(txt, encoding='utf-8')

print('FAST PATCH 1 COMPLETE!')
