# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
# DIRECTIVE_ID: RGON_DIR_NEW_FOUNDATION_140
import json, datetime, os, sys, time, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/3] Space 0~6 전체 잠금 해제 중...")
ego.clear_all_spaces_lock()

print("[2/3] 7번째 창(Space 6: Google Vids)에서 우측 'AI 생성 동영상 / AI 동영상 클립 생성' 패널을 열고 솔의 '오늘은 여기까지' 시네마틱 프롬프트 입력 및 무료 생성 트리거 중...")
vids_prompt = (
    "Photorealistic cinematic scene for a calm late-autumn night turning into winter, viewed from inside a warm cozy room. A single ceramic mug of steaming hot tea rests on a wooden desk beside a rain-speckled window overlooking soft glowing amber streetlights outside, gentle camera push-in, shallow depth of field, no text, no letters, no watermark."
)

js_space6_vids = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(6); }} catch (_) {{ try {{ task = await claimTaskSpace(6); }} catch (__) {{ task = await taskSpace(6); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}

  const res = await page.evaluate(async (pText) => {{
    // 1. 초기 모달('AI 동영상 만들기' / 닫기 X 버튼)이나 우측 'AI 생성 동영상' 버튼 탐색
    const allEls = Array.from(document.querySelectorAll('button, [role="button"], div, span'));
    const aiClipBtn = allEls.find(e => {{
      const t = (e.innerText || '').trim();
      return t === 'AI 동영상 클립 생성' || t === 'AI 생성 동영상' || t.includes('AI 생성 동');
    }});
    if (aiClipBtn) {{
      aiClipBtn.click();
      await new Promise(r => setTimeout(r, 2000));
    }}

    // 2. 화면 내 모든 입력창(textarea, input, contenteditable) 탐색 및 프롬프트 주입
    const inputs = Array.from(document.querySelectorAll('textarea, input[type="text"], [contenteditable="true"]'))
      .filter(el => el.offsetParent !== null);
    let filled = false;
    let targetInfo = 'NONE';
    if (inputs.length > 0) {{
      const target = inputs[inputs.length - 1];
      targetInfo = target.tagName + ':' + (target.placeholder || target.getAttribute('aria-label') || '');
      target.focus();
      if (target.tagName === 'TEXTAREA' || target.tagName === 'INPUT') {{
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set || Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
        if (setter) setter.call(target, pText); else target.value = pText;
        target.dispatchEvent(new InputEvent('input', {{ bubbles: true, data: pText }}));
        target.dispatchEvent(new Event('change', {{ bubbles: true }}));
        filled = true;
      }} else {{
        target.innerText = pText;
        target.dispatchEvent(new InputEvent('input', {{ bubbles: true, data: pText }}));
        filled = true;
      }}
    }}
    await new Promise(r => setTimeout(r, 1200));

    // 3. '만들기' / '생성' / 'Create' / 'Generate' 버튼 탐색 및 클릭
    const btns = Array.from(document.querySelectorAll('button, [role="button"]')).filter(b => b.offsetParent !== null);
    const createBtn = btns.find(b => {{
      const t = (b.innerText || b.getAttribute('aria-label') || '').trim();
      return t === '만들기' || t === '생성' || t === 'Create' || t.includes('만들기') || t.includes('클립 생성');
    }});
    let clickedCreate = 'NONE';
    if (createBtn && !createBtn.disabled && createBtn.getAttribute('aria-disabled') !== 'true') {{
      clickedCreate = (createBtn.innerText || createBtn.getAttribute('aria-label') || 'BTN').trim();
      createBtn.click();
      await new Promise(r => setTimeout(r, 3500));
    }}

    const visibleBtns = btns.map(b => (b.innerText || b.getAttribute('aria-label') || '').replace(/\\s+/g, ' ').trim()).filter(t => t.length > 0 && t.length < 50);
    const bodyTxt = (document.body.innerText || '').replace(/\\s+/g, ' ').trim();

    return {{
      url: location.href,
      input_found: targetInfo,
      prompt_filled: filled,
      clicked_create: clickedCreate,
      visible_buttons: Array.from(new Set(visibleBtns)).slice(0, 25),
      body_sample: bodyTxt.slice(0, 700)
    }};
  }}, {json.dumps(vids_prompt)});

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: true, vids: res }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
vids_res = s1_ego.run_ego_js(js_space6_vids, timeout=45)

print("[3/3] Google Vids(Space 6) 실측 및 생성 결과를 저장하고 Space 0 자동 완료 보고 전송 중...")
out_140 = BASE / "S1_GOOGLE_VIDS_FREE_GEN_140.json"
out_140.write_text(json.dumps({
    "directive_id": "RGON_DIR_NEW_FOUNDATION_140",
    "executed_at": datetime.datetime.now().isoformat(),
    "space6_google_vids_result": vids_res
}, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_GOOGLE_VIDS_FREE_GEN_140.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(140): trigger free AI video clip generation on Space 6 Google Vids using Sol cinematic prompt"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

ego.clear_all_spaces_lock()

v_info = vids_res.get("vids", {}) if isinstance(vids_res, dict) else {}
ego.send_auto_confirm_enter_space0(
    f"확인 (140호 Space6구글빕스 무료AI클립생성:[입력창:{v_info.get('input_found')} / 주입:{v_info.get('prompt_filled')} / 생성클릭:{v_info.get('clicked_create')}] | 노출버튼:{v_info.get('visible_buttons',[])[:12]} | 화면:{str(v_info.get('body_sample',''))[:180]} | 커밋:{sha})"
)