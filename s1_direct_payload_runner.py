import json
import os
import sys
import time
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
import s1_ego

def send_auto_confirm_to_space0(confirm_text: str) -> dict:
    """
    056호에서 100% 검증된 s1_ego.run_ego_js 방식으로
    에고라이트 Space 0 (현재 르곤 채팅창)의 입력창에 '확인' 메시지를 자동 타이핑 후 전송 클릭!
    전송 직후 task.finish({ keep: [] })로 노란 딱지까지 완벽 제거!
    """
    msg_json = json.dumps(confirm_text, ensure_ascii=False)
    js = f"""
    let task = null;
    try {{
      try {{
        task = await takeOverTaskSpace(0);
      }} catch (_) {{
        try {{
          task = await claimTaskSpace(0);
        }} catch (__) {{
          task = await taskSpace(0);
        }}
      }}
      let page = null;
      const up = task.userPage ? task.userPage() : null;
      if (up) {{
        try {{ page = await task.adopt(up); }} catch (_) {{ page = up; }}
      }}
      if (!page && task.pages) {{
        const pages = await task.pages();
        if (pages && pages.length) page = pages[0];
      }}
      if (!page && task.page) {{
        try {{ page = await task.page("p1"); }} catch (_) {{}}
      }}
      if (!page) {{
        process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, error: "NO_SPACE0_PAGE" }}) + '\\n');
        return;
      }}

      await page.evaluate(() => {{ window.__ego_overlay_disabled = true; }}).catch(() => {{}});

      // 만약 르곤이 아직 답변 생성 중(Stop 버튼 존재)이면 끝날 때까지 최대 15초 대기
      for (let w = 0; w < 15; w++) {{
        const busy = await page.evaluate(() => {{
          return Boolean(document.querySelector('button[aria-label*="Stop" i], button[aria-label*="중지" i], .stop-generating'));
        }}).catch(() => false);
        if (!busy) break;
        await new Promise(r => setTimeout(r, 1000));
      }}

      const qStr = {msg_json};
      const sendResult = await page.evaluate((qText) => {{
        const el = document.querySelector('textarea[name="query"], textarea, div[contenteditable="true"], [role="textbox"]');
        if (!el) return {{ sent: false, reason: "NO_INPUT_BOX" }};
        el.focus();
        if (el.tagName && el.tagName.toLowerCase() === 'textarea') {{
          const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
          if (nativeSetter) nativeSetter.call(el, qText);
          else el.value = qText;
          el.dispatchEvent(new Event('input', {{ bubbles: true }}));
          el.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }} else {{
          el.textContent = qText;
          el.dispatchEvent(new InputEvent('input', {{ bubbles: true, data: qText }}));
        }}
        const btns = Array.from(document.querySelectorAll('button[type="submit"], button[aria-label*="send" i], button[aria-label*="전송" i], button[data-testid*="send" i], .enter-icon-wrapper, [class*="send-btn"]'));
        const activeBtn = btns.find(b => !b.disabled);
        if (activeBtn) {{
          activeBtn.click();
          return {{ sent: true, method: "button_click" }};
        }}
        el.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }}));
        return {{ sent: true, method: "enter_key" }};
      }}, qStr).catch(e => ({{ sent: false, error: String(e) }}));

      await new Promise(r => setTimeout(r, 600));
      process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: true, space: 0, send_result: sendResult }}) + '\\n');
    }} catch (err) {{
      process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, space: 0, error: String(err.message || err) }}) + '\\n');
    }} finally {{
      try {{
        if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }});
      }} catch (_) {{}}
    }}
    """
    return s1_ego.run_ego_js(js, timeout=35)

def upgrade_bridge_daemon_with_auto_confirm():
    bp = BASE / "s1_rgon_to_anchongri_bridge.py"
    if not bp.exists():
        return
    txt = bp.read_text(encoding="utf-8", errors="replace")

    helper_fn = '''
def send_auto_confirm_to_space0(directive_id: str):
    """임무 완료 및 GitHub 푸시 직후 에고라이트 Space 0에 자동으로 '확인' 메시지를 타이핑·전송"""
    try:
        import s1_ego
        head_sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=BASE, text=True).strip()
        msg = f"확인 (자동수거·임무완료: {directive_id} · 커밋 {head_sha})"
        msg_json = json.dumps(msg, ensure_ascii=False)
        js = f"""
        let task = null;
        try {{
          try {{ task = await takeOverTaskSpace(0); }} catch (_) {{ try {{ task = await claimTaskSpace(0); }} catch (__) {{ task = await taskSpace(0); }} }}
          const up = task.userPage ? task.userPage() : null;
          let page = up ? await task.adopt(up).catch(() => up) : null;
          if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}
          if (!page) return;
          const qText = {msg_json};
          await page.evaluate((t) => {{
            const el = document.querySelector('textarea[name="query"], textarea, div[contenteditable="true"], [role="textbox"]');
            if (!el) return;
            el.focus();
            if (el.tagName && el.tagName.toLowerCase() === 'textarea') {{
              const ns = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
              if (ns) ns.call(el, t); else el.value = t;
              el.dispatchEvent(new Event('input', {{ bubbles: true }}));
              el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }} else {{
              el.textContent = t;
              el.dispatchEvent(new InputEvent('input', {{ bubbles: true, data: t }}));
            }}
            const btns = Array.from(document.querySelectorAll('button[type="submit"], button[aria-label*="send" i], button[aria-label*="전송" i], .enter-icon-wrapper'));
            const ab = btns.find(b => !b.disabled);
            if (ab) ab.click();
            else el.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }}));
          }}, qText);
          await new Promise(r => setTimeout(r, 500));
        }} catch (_) {{}} finally {{
          try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
        }}
        """
        s1_ego.run_ego_js(js, timeout=30)
        print(f"[AUTO-CONFIRM] Sent automatic '확인' to Space 0 for {directive_id}", flush=True)
    except Exception as e:
        print(f"[AUTO-CONFIRM] Error: {e}", flush=True)
'''

    if "def send_auto_confirm_to_space0(" not in txt:
        txt = txt.replace("def auto_execute_directive_trigger(", helper_fn + "\ndef auto_execute_directive_trigger(", 1)

    # git push 직후 send_auto_confirm_to_space0(directive_id) 호출 연결
    target_line = 'subprocess.run(["git", "push", "origin", "main"], cwd=BASE, check=False)'
    replacement_line = (
        'subprocess.run(["git", "push", "origin", "main"], cwd=BASE, check=False)\n'
        '                send_auto_confirm_to_space0(directive_id)'
    )
    if "send_auto_confirm_to_space0(directive_id)" not in txt and target_line in txt:
        txt = txt.replace(target_line, replacement_line, 1)

    bp.write_text(txt, encoding="utf-8")

def main():
    upgrade_bridge_daemon_with_auto_confirm()

    subprocess.run([sys.executable, "s1_qm_structure_linter.py"], cwd=str(BASE))
    subprocess.run(["git", "add", "s1_rgon_to_anchongri_bridge.py"], cwd=str(BASE))
    subprocess.run(["git", "commit", "-m", "feat(066): automate Space 0 '확인' confirmation message after directive execution"], cwd=str(BASE))
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE))

    head_sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), text=True).strip()

    # 지금 즉시 Space 0 (르곤 채팅창)에 첫 무인 자동 '확인' 메시지 발사!
    res = send_auto_confirm_to_space0(f"확인 (066호 무인 자동 확인 엔진 개통 완료! 최신 커밋: {head_sha})")
    print("[066-AUTO-CONFIRM-RESULT]", res)

if __name__ == "__main__":
    main()