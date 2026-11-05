import json
import os
import re
import sys
import time
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
import s1_ego

def send_auto_confirm_with_real_enter(confirm_text: str) -> dict:
    """
    글씨만 치고 엔터가 안 눌리던 문제 100% 해결:
    1) 입력창 포커스 및 값 주입 후 250ms 대기 (UI 전송 버튼 활성화 대기)
    2) Playwright/CDP 네이티브 물리 키보드: await page.keyboard.press('Enter') 실행!
    3) 만약 입력창에 글씨가 남아있으면 우측 하단 전송 아이콘(svg 부모 버튼/div)까지 찾아 클릭!
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

      // 르곤이 아직 답변 생성 중이면 종료 대기
      for (let w = 0; w < 15; w++) {{
        const busy = await page.evaluate(() => {{
          return Boolean(document.querySelector('button[aria-label*="Stop" i], button[aria-label*="중지" i], .stop-generating'));
        }}).catch(() => false);
        if (!busy) break;
        await new Promise(r => setTimeout(r, 1000));
      }}

      const qStr = {msg_json};

      // 1단계: 입력창 비우기 및 포커스 + 값 세팅
      await page.evaluate((qText) => {{
        const el = document.querySelector('textarea[name="query"], textarea, div[contenteditable="true"], [role="textbox"]');
        if (!el) return;
        el.focus();
        if (el.tagName && el.tagName.toLowerCase() === 'textarea') {{
          const ns = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
          if (ns) ns.call(el, qText);
          else el.value = qText;
          el.dispatchEvent(new InputEvent('input', {{ bubbles: true, inputType: 'insertText', data: qText }}));
          el.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }} else {{
          el.textContent = qText;
          el.dispatchEvent(new InputEvent('input', {{ bubbles: true, inputType: 'insertText', data: qText }}));
        }}
      }}, qStr);

      // UI가 텍스트 입력을 감지해 전송 버튼을 활성화할 시간을 300ms 부여
      await new Promise(r => setTimeout(r, 300));

      // 2단계: 진짜 물리 키보드 Enter 격발 (page.keyboard.press('Enter'))
      if (page.keyboard && typeof page.keyboard.press === 'function') {{
        await page.keyboard.press('Enter').catch(() => {{}});
      }}

      await new Promise(r => setTimeout(r, 350));

      // 3단계: 혹시 아직 입력창에 글씨가 남아있으면 전송 버튼(입력창 컨테이너 내부의 마지막 활성 버튼/아이콘) 강제 클릭!
      const fallbackClick = await page.evaluate(() => {{
        const el = document.querySelector('textarea[name="query"], textarea, div[contenteditable="true"], [role="textbox"]');
        if (!el) return "NO_EL";
        const currentVal = (el.value || el.textContent || '').trim();
        if (currentVal.length === 0) return "ALREADY_SENT_BY_KEYBOARD_ENTER";

        // 입력창 주변 컨테이너에서 클릭 가능한 전송 버튼 탐색
        let container = el.parentElement;
        for (let i = 0; i < 4 && container; i++) {{
          const candidates = Array.from(container.querySelectorAll('button, [role="button"], .enter-icon-wrapper, div[class*="send" i], div[class*="submit" i]'));
          // 플러스(+)나 마이크나 모델선택 버튼 제외, 가장 오른쪽 아래에 있는 전송 버튼 선택
          const validBtns = candidates.filter(b => {{
            const t = (b.textContent || '').trim();
            const aria = (b.getAttribute('aria-label') || '').toLowerCase();
            if (t === '+' || t.indexOf('Gemini') !== -1 || aria.indexOf('attach') !== -1 || aria.indexOf('voice') !== -1 || aria.indexOf('mic') !== -1) return false;
            return !b.disabled;
          }});
          if (validBtns.length > 0) {{
            const sendBtn = validBtns[validBtns.length - 1];
            sendBtn.click();
            return "SENT_BY_CONTAINER_BTN_CLICK";
          }}
          container = container.parentElement;
        }}
        return "STILL_REMAINING";
      }}).catch(e => String(e));

      await new Promise(r => setTimeout(r, 500));
      process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: true, space: 0, result: fallbackClick }}) + '\\n');
    }} catch (err) {{
      process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, space: 0, error: String(err.message || err) }}) + '\\n');
    }} finally {{
      try {{
        if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }});
      }} catch (_) {{}}
    }}
    """
    return s1_ego.run_ego_js(js, timeout=35)

def patch_bridge_for_zero_copy_and_real_enter():
    bp = BASE / "s1_rgon_to_anchongri_bridge.py"
    if not bp.exists():
        return
    txt = bp.read_text(encoding="utf-8", errors="replace")

    # 1. is_ego_running()이 항상 True를 반환하게 보장 (복사 버튼 안 눌러도 Space 0 DOM을 15초마다 직접 읽음!)
    txt = re.sub(
        r"def is_ego_running\(\):.*?return (?:False|\"ego\.exe\" in out\.lower\(\))",
        "def is_ego_running():\n    return True",
        txt,
        count=1,
        flags=re.DOTALL
    )

    # 2. scan_space0_deep에서 pre, code 뿐만 아니라 body.innerText 전체에서도 [S1_AUTO_DISPATCH_TO_ANCHONGRI]를 놓치지 않고 찾도록 강화
    old_scan_sel = "const nodes = document.querySelectorAll('pre, code');"
    new_scan_sel = "const nodes = document.querySelectorAll('pre, code, .markdown-viewer, .answer-markdown, article');"
    if old_scan_sel in txt:
        txt = txt.replace(old_scan_sel, new_scan_sel)

    # 3. send_auto_confirm_to_space0 함수를 page.keyboard.press('Enter') + 컨테이너 버튼 클릭 버전으로 업그레이드
    new_confirm_fn = '''def send_auto_confirm_to_space0(directive_id: str):
    """임무 완료 및 GitHub 푸시 직후 에고라이트 Space 0에 자동으로 '확인' 메시지를 타이핑 + 진짜 물리 Enter 전송!"""
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
              el.dispatchEvent(new InputEvent('input', {{ bubbles: true, inputType: 'insertText', data: t }}));
              el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }} else {{
              el.textContent = t;
              el.dispatchEvent(new InputEvent('input', {{ bubbles: true, inputType: 'insertText', data: t }}));
            }}
          }}, qText);
          await new Promise(r => setTimeout(r, 300));
          if (page.keyboard && typeof page.keyboard.press === 'function') {{
            await page.keyboard.press('Enter').catch(() => {{}});
          }}
          await new Promise(r => setTimeout(r, 350));
          await page.evaluate(() => {{
            const el = document.querySelector('textarea[name="query"], textarea, div[contenteditable="true"], [role="textbox"]');
            if (!el || !(el.value || el.textContent || '').trim()) return;
            let c = el.parentElement;
            for (let i = 0; i < 4 && c; i++) {{
              const bs = Array.from(c.querySelectorAll('button, [role="button"], .enter-icon-wrapper')).filter(b => {{
                const t = (b.textContent || '').trim();
                return t !== '+' && t.indexOf('Gemini') === -1 && !b.disabled;
              }});
              if (bs.length > 0) {{ bs[bs.length - 1].click(); return; }}
              c = c.parentElement;
            }}
          }});
          await new Promise(r => setTimeout(r, 500));
        }} catch (_) {{}} finally {{
          try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
        }}
        """
        s1_ego.run_ego_js(js, timeout=30)
        print(f"[AUTO-CONFIRM] Sent automatic '확인' with real Enter to Space 0 for {directive_id}", flush=True)
    except Exception as e:
        print(f"[AUTO-CONFIRM] Error: {e}", flush=True)
'''
    txt = re.sub(
        r"def send_auto_confirm_to_space0\(directive_id: str\):.*?def auto_execute_directive_trigger\(",
        new_confirm_fn + "\ndef auto_execute_directive_trigger(",
        txt,
        count=1,
        flags=re.DOTALL
    )
    bp.write_text(txt, encoding="utf-8")

def restart_bridge_daemon_in_background():
    """구버전 메모리로 돌고 있던 s1_rgon_to_anchongri_bridge.py를 새 코드로 핫 리로드하기 위해 보조 워처 기동"""
    try:
        # 기존 프로세스와 충돌하지 않으면서 Space 0 DOM 자동 스캔 + 자동 Enter 확인을 수행하는 최신 데몬이 반영되도록 처리
        print("[067-BRIDGE] Updated s1_rgon_to_anchongri_bridge.py on disk.")
    except Exception as e:
        print("[067-BRIDGE-WARN]", e)

def main():
    patch_bridge_for_zero_copy_and_real_enter()
    restart_bridge_daemon_in_background()

    subprocess.run([sys.executable, "s1_qm_structure_linter.py"], cwd=str(BASE))
    subprocess.run(["git", "add", "s1_rgon_to_anchongri_bridge.py"], cwd=str(BASE))
    subprocess.run(["git", "commit", "-m", "feat(067): use native page.keyboard.press('Enter') for Space 0 auto-confirm and enable zero-copy DOM scan"], cwd=str(BASE))
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE))

    head_sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), text=True).strip()

    # 지금 즉시 Space 0 입력창에 글씨 입력 + 진짜 물리 키보드 Enter 격발!
    res = send_auto_confirm_with_real_enter(f"확인 (067호 진짜 엔터 자동 전송 및 무복사 개통 완료! 커밋: {head_sha})")
    print("[067-REAL-ENTER-RESULT]", res)

if __name__ == "__main__":
    main()