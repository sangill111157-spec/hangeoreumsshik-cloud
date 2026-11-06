# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
# DIRECTIVE_ID: RGON_DIR_NEW_FOUNDATION_141
import json, datetime, os, sys, time, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/3] S1_EGO_PROVEN_SKILL_MASTER.py의 clear_all_spaces_lock()을 7개 전체 스페이스(0~6) 해제용으로 영구 업그레이드 중...")
master_p = BASE / "S1_EGO_PROVEN_SKILL_MASTER.py"
if master_p.exists():
    m_txt = master_p.read_text(encoding="utf-8")
    m_txt = m_txt.replace("[0, 1, 2, 3]", "[0, 1, 2, 3, 4, 5, 6]").replace("idx <= 3", "idx <= 6")
    master_p.write_text(m_txt, encoding="utf-8")

js_unlock_all = """
for (let i = 0; i <= 6; i++) {
  try {
    let t = null;
    try { t = await takeOverTaskSpace(i); } catch (_) { try { t = await claimTaskSpace(i); } catch (__) { t = await taskSpace(i); } }
    if (t && typeof t.finish === 'function') await t.finish({ keep: [] });
  } catch (e) {}
}
process.stdout.write('S1EGO_JSON::{"ok":true}');
"""
s1_ego.run_ego_js(js_unlock_all, timeout=20)

print("[2/3] 7번째 창(Space 6: Google Vids)에서 139호 검증 방식으로 우측 'AI 생성 동영상' 패널 클릭 및 프롬프트 타이핑·생성 실행 중...")
prompt_vids = "Photorealistic cinematic scene on a calm late-autumn night, viewed from inside a warm cozy room. A ceramic cup of steaming hot tea rests on a wooden desk beside a rain-kissed window overlooking glowing amber streetlights outside, gentle slow camera push-in, shallow depth of field, no text, no letters, no watermark."

js_vids_native = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(6); }} catch (_) {{ try {{ task = await claimTaskSpace(6); }} catch (__) {{ task = await taskSpace(6); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}

  // 1. 먼저 AI 동영상 클립 생성 / AI 생성 동영상 버튼 좌표 찾아 클릭
  const clickInfo = await page.evaluate(() => {{
    const els = Array.from(document.querySelectorAll('*'));
    const target = els.find(e => {{
      const t = (e.innerText || '').trim();
      return (t === 'AI 동영상 클립 생성' || t === 'AI 생성 동영상' || t === 'AI 동영상 만들기') && e.children.length === 0;
    }});
    if (target) {{
      target.click();
      if (target.parentElement) target.parentElement.click();
      return {{ clicked: true, text: target.innerText }};
    }}
    return {{ clicked: false }};
  }});

  await new Promise(r => setTimeout(r, 2500));

  // 2. 열린 사이드바의 textarea 또는 입력창 포커스
  const inputInfo = await page.evaluate(() => {{
    const tas = Array.from(document.querySelectorAll('textarea, input[type="text"], [contenteditable="true"]'));
    const visibleTas = tas.filter(el => {{
      const rect = el.getBoundingClientRect();
      return rect.width > 30 && rect.height > 15;
    }});
    if (visibleTas.length > 0) {{
      const el = visibleTas[visibleTas.length - 1];
      el.focus();
      el.click();
      return {{ found: true, count: visibleTas.length, tag: el.tagName, placeholder: el.placeholder || el.getAttribute('aria-label') || '' }};
    }}
    return {{ found: false, count: 0 }};
  }});

  let typed = false;
  if (inputInfo && inputInfo.found) {{
    await page.keyboard.press('Control+A').catch(() => {{}});
    await page.keyboard.press('Backspace').catch(() => {{}});
    await page.keyboard.type({json.dumps(prompt_vids)}, {{ delay: 5 }}).catch(() => {{}});
    typed = true;
    await new Promise(r => setTimeout(r, 1200));
  }}

  // 3. 만들기 / 생성 버튼 클릭
  const createClick = await page.evaluate(() => {{
    const btns = Array.from(document.querySelectorAll('button, [role="button"]'));
    const cBtn = btns.find(b => {{
      const t = (b.innerText || b.getAttribute('aria-label') || '').trim();
      const rect = b.getBoundingClientRect();
      return rect.width > 20 && (t === '만들기' || t === '생성' || t.includes('만들기') || t.includes('생성'));
    }});
    if (cBtn && !cBtn.disabled && cBtn.getAttribute('aria-disabled') !== 'true') {{
      cBtn.click();
      return {{ clicked: true, label: (cBtn.innerText || cBtn.getAttribute('aria-label') || '').trim() }};
    }}
    return {{ clicked: false, all_btns: btns.map(b => (b.innerText || b.getAttribute('aria-label') || '').trim()).filter(Boolean).slice(0, 20) }};
  }});

  await new Promise(r => setTimeout(r, 3000));

  const afterTxt = await page.evaluate(() => {{
    return (document.body.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 900);
  }});

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{
    ok: true,
    panel_click: clickInfo,
    input_info: inputInfo,
    typed: typed,
    create_click: createClick,
    after_text: afterTxt
  }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
vids_141 = s1_ego.run_ego_js(js_vids_native, timeout=45)

print("[3/3] 7개 스페이스 잠금 해제 및 Space 0 자동 완료 보고 전송 중...")
s1_ego.run_ego_js(js_unlock_all, timeout=15)

out_141 = BASE / "S1_GOOGLE_VIDS_NATIVE_GEN_141.json"
out_141.write_text(json.dumps({
    "directive_id": "RGON_DIR_NEW_FOUNDATION_141",
    "executed_at": datetime.datetime.now().isoformat(),
    "space6_vids_native": vids_141
}, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_GOOGLE_VIDS_NATIVE_GEN_141.json", "S1_EGO_PROVEN_SKILL_MASTER.py"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(141): upgrade clear_all_spaces_lock to 7 spaces and trigger Google Vids native AI clip generation"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

ego.send_auto_confirm_enter_space0(
    f"확인 (141호 7대스페이스잠금해제업그레이드 & Space6구글빕스:[패널클릭:{vids_141.get('panel_click')} / 입력창:{vids_141.get('input_info')} / 타이핑:{vids_141.get('typed')} / 생성버튼:{vids_141.get('create_click')}] | 화면:{str(vids_141.get('after_text',''))[-240:]} | 커밋:{sha})"
)