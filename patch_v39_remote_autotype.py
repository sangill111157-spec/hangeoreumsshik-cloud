# -*- coding: utf-8 -*-
"""
patch_v39_remote_autotype.py
--------------------------------------------------------------------------------
1. dashboard/index.html (tab-command & tab-daughters 상단)에
   [📋 스마트폰 복사 명령 ➔ 노트북 안실장에게 1초 직통 쏘기] 스위치 장착
2. window.sendRemoteClipboardToAntigravity JS 함수 탑재
3. dashboard/dream_closet_future_master_app.html 에도 동일 스위치 및 함수 탑재
--------------------------------------------------------------------------------
"""

import sys
from pathlib import Path

BUTTON_HTML = '''<!-- 📲 [스마트폰 원격 복붙 ➔ 노트북 안실장 1초 직통 쏘기] -->
      <div class="mb-3 p-3 bg-gradient-to-r from-purple-950/80 via-indigo-950/80 to-blue-950/80 border border-purple-500/40 rounded-2xl shadow-lg shadow-purple-950/50 flex flex-wrap items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <span class="text-xl">📲</span>
          <div>
            <div class="text-xs font-black text-purple-200 tracking-tight flex items-center gap-1.5">
              <span>스마트폰 원격 복붙 직통 스위치</span>
              <span class="px-1.5 py-0.2 bg-purple-500/30 text-purple-300 rounded text-[10px] font-mono border border-purple-400/30">Zero-Touch 1초</span>
            </div>
            <div class="text-[11px] text-slate-400">스마트폰에서 복사한 르곤이 명령을 노트북 안실장 채팅창에 1초 만에 자동 타건!</div>
          </div>
        </div>
        <button type="button" onclick="sendRemoteClipboardToAntigravity()" class="px-4 py-2 bg-gradient-to-r from-purple-600 via-indigo-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-black text-xs rounded-xl shadow-md active:scale-95 transition-all flex items-center gap-1.5 border border-purple-300/30 cursor-pointer">
          <span>📋 스마트폰 복사 명령 ➔ 노트북 안실장에게 1초 직통 쏘기</span>
        </button>
      </div>'''

JS_CODE = '''
    // 📲 [스마트폰 원격 복붙 ➔ 노트북 안실장 직통 타건]
    window.sendRemoteClipboardToAntigravity = async function() {
      let promptText = '';
      if (navigator.clipboard && navigator.clipboard.readText) {
        try {
          promptText = await navigator.clipboard.readText();
        } catch (e) {
          console.warn('Clipboard readText failed, using prompt:', e);
        }
      }
      if (!promptText || promptText.trim().length === 0) {
        promptText = window.prompt(
          "📱 [스마트폰 복사 ➔ 노트북 안실장 직통 쏘기]\\n\\n스마트폰에서 복사하신 르곤이 명령을 여기에 붙여넣고 [확인]을 누르세요:",
          ""
        );
      }
      if (!promptText || promptText.trim().length === 0) {
        return;
      }
      try {
        const res = await fetch('/api/remote-auto-paste', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: promptText })
        });
        const data = await res.json();
        if (data.success) {
          alert("🎉 [1초 원격 전송 성공!]\\n\\n노트북 안실장 채팅창에 명령이 꽂히고 자동 타건(Ctrl+V + Enter)되었습니다!\\n노트북에서 '띠리링!' 소리가 울렸습니다.");
        } else {
          alert("⚠️ 전송 실패: " + (data.error || '알 수 없는 오류'));
        }
      } catch (err) {
        alert("❌ 노트북 서버 연결 오류: " + err.message);
      }
    };
'''

def patch_index_html():
    idx_path = Path("dashboard/index.html")
    content = idx_path.read_text(encoding="utf-8")

    # 1. tab-command 상단 삽입
    target_cmd = '<div id="tab-command" class="tab-pane p-4 sm:p-6 lg:p-8 space-y-6">'
    if target_cmd in content and 'sendRemoteClipboardToAntigravity' not in content:
        content = content.replace(target_cmd, target_cmd + '\n      ' + BUTTON_HTML, 1)
        print("✅ Added remote button to tab-command")

    # 2. tab-daughters 상단 삽입
    target_d = '<div id="tab-daughters" class="tab-pane hidden p-4 sm:p-6 lg:p-8 space-y-6">'
    if target_d in content and content.count('sendRemoteClipboardToAntigravity') < 2:
        content = content.replace(target_d, target_d + '\n      ' + BUTTON_HTML, 1)
        print("✅ Added remote button to tab-daughters")

    # 3. JS 스크립트 추가
    if 'sendRemoteClipboardToAntigravity =' not in content:
        content = content.replace('</script>\n</body>', JS_CODE + '\n  </script>\n</body>')
        print("✅ Added sendRemoteClipboardToAntigravity JS function")

    idx_path.write_text(content, encoding="utf-8")

def patch_master_app_html():
    app_path = Path("dashboard/dream_closet_future_master_app.html")
    if not app_path.exists():
        return
    content = app_path.read_text(encoding="utf-8")

    # 상단 컨트롤 바 위에 추가
    if 'sendRemoteClipboardToAntigravity' not in content:
        # main 태그 또는 컨테이너 상단에 삽입
        target = '<main class="max-w-4xl mx-auto px-4 py-4 space-y-4">'
        if target in content:
            content = content.replace(target, target + '\n' + BUTTON_HTML, 1)
        elif '<div class="space-y-4">' in content:
            content = content.replace('<div class="space-y-4">', '<div class="space-y-4">\n' + BUTTON_HTML, 1)

        # JS 추가
        content = content.replace('</script>\n</body>', JS_CODE + '\n  </script>\n</body>')
        print("✅ Patched dream_closet_future_master_app.html")

    app_path.write_text(content, encoding="utf-8")

if __name__ == '__main__':
    patch_index_html()
    patch_master_app_html()
    print("🚀 All HTML patches applied successfully!")
