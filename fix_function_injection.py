# -*- coding: utf-8 -*-
"""
fix_function_injection.py
--------------------------------------------------------------------------------
dashboard/index.html의 마지막 <script> 태그 내부에
sendRemoteClipboardToAntigravity 함수를 확실하게 주입합니다.
--------------------------------------------------------------------------------
"""

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

JS_CODE = '''
    // 📲 [스마트폰 원격 복붙 ➔ 노트북 안실장 직통 타건]
    async function sendRemoteClipboardToAntigravity() {
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
    }
    window.sendRemoteClipboardToAntigravity = sendRemoteClipboardToAntigravity;
'''

def apply_fix():
    idx_path = Path("dashboard/index.html")
    content = idx_path.read_text(encoding="utf-8")

    if "function sendRemoteClipboardToAntigravity" not in content:
        # 마지막 </script> 찾기
        idx = content.rfind("</script>")
        if idx != -1:
            content = content[:idx] + JS_CODE + "\n  " + content[idx:]
            idx_path.write_text(content, encoding="utf-8")
            print("✅ Successfully injected sendRemoteClipboardToAntigravity into dashboard/index.html")
        else:
            print("❌ </script> tag not found")
    else:
        print("ℹ️ Already injected")

    # dream_closet_future_master_app.html 확인
    app_path = Path("dashboard/dream_closet_future_master_app.html")
    if app_path.exists():
        app_content = app_path.read_text(encoding="utf-8")
        if "function sendRemoteClipboardToAntigravity" not in app_content:
            idx = app_content.rfind("</script>")
            if idx != -1:
                app_content = app_content[:idx] + JS_CODE + "\n  " + app_content[idx:]
                app_path.write_text(app_content, encoding="utf-8")
                print("✅ Successfully injected into dream_closet_future_master_app.html")

if __name__ == "__main__":
    apply_fix()
