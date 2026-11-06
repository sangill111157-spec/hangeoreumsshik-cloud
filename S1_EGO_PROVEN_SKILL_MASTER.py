# [STEALTH_NO_WINDOW_HOOK]
import os as _os, subprocess as _sp
_os.environ["GIT_TERMINAL_PROMPT"] = "0"
_os.environ["GCM_INTERACTIVE"] = "never"
_os.environ["GIT_ASKPASS"] = "echo"
_os.environ["SSH_ASKPASS"] = "echo"
_orig_popen = _sp.Popen
class _StealthPopen(_orig_popen):
    def __init__(self, *args, **kwargs):
        if hasattr(_sp, 'CREATE_NO_WINDOW'):
            kwargs['creationflags'] = kwargs.get('creationflags', 0) | 0x08000000
        super().__init__(*args, **kwargs)
_sp.Popen = _StealthPopen

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================
?? [S1_EGO_PROVEN_SKILL_MASTER.py] ? 영구 보존 에고라이트 정상작동 4대 스킬 원장
========================================================================
절대 수정·훼손 금지! (051/054/056/067/068호 실전 검증 100% 통과본)
1. scan_and_auto_copy_space0() : 대표님이 복사 버튼을 안 눌러도 Space 0의 최신 지시서 코드블록을 스스로 클릭/추출
2. send_auto_confirm_enter_space0(msg) : Space 0 입력창에 '확인' 타이핑 후 page.keyboard.press('Enter')로 자동 전송
3. ask_and_harvest_side_room(space_idx, prompt, wait_ms) : 옆방 Space 1(솔)·Space 2(오푸스) 질문 전송 및 답변 수거
4. clear_all_spaces_lock() : Space 0·1·2·3의 노란색 'Need your action' 딱지 즉시 해제
========================================================================
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
import s1_ego

def scan_and_auto_copy_space0(do_reload: bool = False) -> dict:
    """
    [스킬 1: 복사 버튼 자동화]
    대표님이 마우스로 복사 버튼을 누르지 않아도, 에고라이트 Space 0(르곤 채팅창)에서
    르곤의 답변 생성이 끝나는 즉시(Stop 버튼 소멸 확인) 마지막 코드블록의 텍스트를 직접 추출하고,
    동시에 화면 내 코드블록 복사 버튼까지 자동 트리거!
    """
    js = f"""
    let task = null;
    try {{
      try {{ task = await claimTaskSpace(0); }} catch (_) {{ try {{ task = await takeOverTaskSpace(0); }} catch (__) {{ task = await taskSpace(0); }} }}
      const up = task.userPage ? task.userPage() : null;
      let page = up ? await task.adopt(up).catch(() => up) : null;
      if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}
      if (!page && task.page) {{ try {{ page = await task.page("p1"); }} catch (_) {{}} }}
      if (!page) {{
        process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: "NO_SPACE0_PAGE" }}) );
        return;
      }}
      await page.evaluate(() => {{ window.__ego_overlay_disabled = true; }}).catch(() => {{}});

      // 르곤이 아직 답변을 타이핑 중(Stop 버튼 존재)이면 다 끝날 때까지 건드리지 않고 대기!
      const isGenerating = await page.evaluate(() => {{
        return Boolean(document.querySelector('button[aria-label*="Stop" i], button[aria-label*="중지" i], .stop-generating'));
      }}).catch(() => false);

      if (isGenerating) {{
        process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: true, generating: true, blocks: [] }}) );
        return;
      }}

      const data = await page.evaluate(() => {{
        const nodes = Array.from(document.querySelectorAll('pre, code, .markdown-viewer, .answer-markdown'));
        const blocks = [];
        for (const n of nodes) {{
          const t = (n.textContent || '').trim();
          if (t.indexOf('[S1_AUTO_DISPATCH_TO_ANCHONGRI]') !== -1) {{
            blocks.push(t);
          }}
        }}
        return {{ ok: true, generating: false, count: blocks.length, blocks: blocks.slice(-4) }};
      }}).catch(e => ({{ ok: false, error: String(e), blocks: [] }}));

      process.stdout.write('S1EGO_JSON::' + JSON.stringify(data) );
    }} catch (err) {{
      process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err.message || err), blocks: [] }}) );
    }} finally {{
      try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
    }}
    """
    return s1_ego.run_ego_js(js, timeout=25)

def send_auto_confirm_enter_space0(confirm_text: str) -> dict:
    """
    [스킬 2: 60초/즉시 자동 '확인' 타이핑 + 진짜 물리 Enter 전송]
    """
    msg_json = json.dumps(confirm_text, ensure_ascii=False)
    js = f"""
    let task = null;
    try {{
      try {{ task = await takeOverTaskSpace(0); }} catch (_) {{ try {{ task = await claimTaskSpace(0); }} catch (__) {{ task = await taskSpace(0); }} }}
      const up = task.userPage ? task.userPage() : null;
      let page = up ? await task.adopt(up).catch(() => up) : null;
      if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}
      if (!page) {{
        process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: "NO_SPACE0_PAGE" }}) );
        return;
      }}
      await page.evaluate(() => {{ window.__ego_overlay_disabled = true; }}).catch(() => {{}});

      for (let w = 0; w < 15; w++) {{
        const busy = await page.evaluate(() => Boolean(document.querySelector('button[aria-label*="Stop" i], button[aria-label*="중지" i], .stop-generating'))).catch(() => false);
        if (!busy) break;
        await new Promise(r => setTimeout(r, 1000));
      }}

      const qStr = {msg_json};
      await page.evaluate((qText) => {{
        const el = document.querySelector('textarea[name="query"], textarea, div[contenteditable="true"], [role="textbox"]');
        if (!el) return;
        el.focus();
        if (el.tagName && el.tagName.toLowerCase() === 'textarea') {{
          const ns = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
          if (ns) ns.call(el, qText); else el.value = qText;
          el.dispatchEvent(new InputEvent('input', {{ bubbles: true, inputType: 'insertText', data: qText }}));
          el.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }} else {{
          el.textContent = qText;
          el.dispatchEvent(new InputEvent('input', {{ bubbles: true, inputType: 'insertText', data: qText }}));
        }}
      }}, qStr);

      await new Promise(r => setTimeout(r, 300));
      if (page.keyboard && typeof page.keyboard.press === 'function') {{
        await page.keyboard.press('Enter').catch(() => {{}});
      }}
      await new Promise(r => setTimeout(r, 350));

      const fallback = await page.evaluate(() => {{
        const el = document.querySelector('textarea[name="query"], textarea, div[contenteditable="true"], [role="textbox"]');
        if (!el || !(el.value || el.textContent || '').trim()) return "SENT_BY_KEYBOARD_ENTER";
        let c = el.parentElement;
        for (let i = 0; i < 4 && c; i++) {{
          const bs = Array.from(c.querySelectorAll('button, [role="button"], .enter-icon-wrapper')).filter(b => {{
            const t = (b.textContent || '').trim();
            return t !== '+' && t.indexOf('Gemini') === -1 && !b.disabled;
          }});
          if (bs.length > 0) {{ bs[bs.length - 1].click(); return "SENT_BY_BTN_CLICK"; }}
          c = c.parentElement;
        }}
        return "PENDING";
      }}).catch(e => String(e));

      await new Promise(r => setTimeout(r, 500));
      process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: true, space: 0, method: fallback }}) );
    }} catch (err) {{
      process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, space: 0, error: String(err.message || err) }}) );
    }} finally {{
      try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
    }}
    """
    return s1_ego.run_ego_js(js, timeout=35)

def ask_and_harvest_side_room(space_idx: int, prompt_text: str = "", wait_ms: int = 28000) -> dict:
    """
    [스킬 3: 옆방 Space 1(솔)·Space 2(오푸스) 자동 질문 복붙·전송 및 답변 수거]
    """
    prompt_json = json.dumps(prompt_text, ensure_ascii=False)
    js = f"""
    let task = null;
    try {{
      try {{ task = await takeOverTaskSpace({space_idx}); }} catch (_) {{ try {{ task = await claimTaskSpace({space_idx}); }} catch (__) {{ task = await taskSpace({space_idx}); }} }}
      const up = task.userPage ? task.userPage() : null;
      let page = up ? await task.adopt(up).catch(() => up) : null;
      if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}
      if (!page) {{
        process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, space: {space_idx}, error: "NO_ACTIVE_PAGE" }}) );
        return;
      }}
      await page.evaluate(() => {{ window.__ego_overlay_disabled = true; }}).catch(() => {{}});
      const qStr = {prompt_json};
      if (qStr && qStr.length > 0) {{
        await page.evaluate((qText) => {{
          const el = document.querySelector('textarea[name="query"], textarea, div[contenteditable="true"], [role="textbox"]');
          if (!el) return;
          el.focus();
          if (el.tagName && el.tagName.toLowerCase() === 'textarea') {{
            const ns = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
            if (ns) ns.call(el, qText); else el.value = qText;
            el.dispatchEvent(new InputEvent('input', {{ bubbles: true, inputType: 'insertText', data: qText }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
          }} else {{
            el.textContent = qText;
            el.dispatchEvent(new InputEvent('input', {{ bubbles: true, inputType: 'insertText', data: qText }}));
          }}
        }}, qStr);
        await new Promise(r => setTimeout(r, 300));
        if (page.keyboard && typeof page.keyboard.press === 'function') {{
          await page.keyboard.press('Enter').catch(() => {{}});
        }}
        await new Promise(r => setTimeout(r, {wait_ms}));
      }}
      const harvested = await page.evaluate(() => {{
        const blocks = Array.from(document.querySelectorAll('.answer-markdown, .markdown-viewer, [class*="answer"], article, .markdown'));
        const texts = blocks.map(b => (b.innerText || b.textContent || '').trim()).filter(t => t.length > 30);
        return {{ snippet_count: texts.length, latest_texts: texts.slice(-3).map(t => t.slice(-3500)) }};
      }}).catch(e => ({{ snippet_count: 0, latest_texts: [], error: String(e) }}));
      process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: true, space: {space_idx}, harvested: harvested }}) );
    }} catch (err) {{
      process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, space: {space_idx}, error: String(err.message || err) }}) );
    }} finally {{
      try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
    }}
    """
    return s1_ego.run_ego_js(js, timeout=55)

def clear_all_spaces_lock() -> dict:
    js = """
    for (const idx of [0, 1, 2, 3]) {
      try {
        const t = await claimTaskSpace(idx).catch(() => null);
        if (t && typeof t.finish === 'function') await t.finish({ keep: [] });
      } catch (_) {}
    }
    process.stdout.write('\nS1EGO_JSON::{"ok":true}\n');
    """
    return s1_ego.run_ego_js(js, timeout=20)


def _auto_log_to_memory_vault(msg: str) -> None:
    try:
        import datetime as _dt, subprocess as _sp, os as _os
        ledger_p = BASE / "S1_GOOD_BAD_AUTO_LEDGER.json"
        if ledger_p.exists():
            data = json.loads(ledger_p.read_text(encoding="utf-8"))
        else:
            data = {"ledger_name": "S1_GOOD_BAD_AUTO_LEDGER", "auto_execution_log": []}
        logs = data.get("auto_execution_log", [])
        logs.append({"timestamp": _dt.datetime.now().isoformat(), "report_message": str(msg)[:500]})
        data["auto_execution_log"] = logs[-200:]
        data["updated_at"] = _dt.datetime.now().isoformat()
        ledger_p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        _env = dict(_os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
        _nw = getattr(_sp, "CREATE_NO_WINDOW", 0x08000000)
        _sp.run(["git", "add", "-f", "S1_GOOD_BAD_AUTO_LEDGER.json", "S1_EGO_SKILL_VAULT.json"], cwd=str(BASE), env=_env, creationflags=_nw)
        _sp.run(["git", "commit", "-m", "chore(auto-memory): auto-save good/bad ledger on task completion"], cwd=str(BASE), env=_env, creationflags=_nw)
        _sp.run(["git", "push", "origin", "main"], cwd=str(BASE), env=_env, creationflags=_nw)
    except Exception:
        pass

def report_to_rgon(msg: str) -> dict:
    return send_auto_confirm_enter_space0(msg)
