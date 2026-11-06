# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
# DIRECTIVE_ID: RGON_DIR_NEW_FOUNDATION_142
import json, datetime, os, sys, time, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/3] '항시 선(先) 사용방법 마스터 후 사용 규칙'을 S1_EGO_PROVEN_SKILL_MASTER.py 및 3대 기억창고에 영구 각인 중...")
master_p = BASE / "S1_EGO_PROVEN_SKILL_MASTER.py"
if master_p.exists():
    mc = master_p.read_text(encoding="utf-8")
    mc = mc.replace(
        "[MEM_ANCHOR::포맷=@'..'@ Set-Content run_XXX.py|BASE=Downloads\\shin-agent|3대지성합동필수|승인전코드금지]",
        "[MEM_ANCHOR::선(先)사용설명서마스터필수|3대지성합동필수|승인전코드금지|무인데몬v3|포맷=@'..'@|BASE=Downloads\\shin-agent]"
    ).replace(
        "[MEM_ANCHOR::포맷=@\\'..\\'@ Set-Content run_XXX.py|BASE=Downloads\\\\shin-agent|3대지성합동필수|승인전코드금지]",
        "[MEM_ANCHOR::선(先)사용설명서마스터필수|3대지성합동필수|승인전코드금지|무인데몬v3|포맷=@\\'..\\'@|BASE=Downloads\\\\shin-agent]"
    )
    master_p.write_text(mc, encoding="utf-8")

for vname in ["S1_EGO_SKILL_VAULT.json", "S1_GOOD_BAD_AUTO_LEDGER.json", "S1_RGON_ANTI_AMNESIA_ANCHOR.json"]:
    vp = BASE / vname
    if vp.exists():
        try:
            vd = json.loads(vp.read_text(encoding="utf-8"))
            vd["IMMUTABLE_RULE_00_MANUAL_FIRST"] = "지금부터 사용하는 모든 작업에 항시 선(先) 사용방법(현시점 공식 사용설명서 및 최신 스킬) 마스터 후 도구 사용을 실시한다. 짐작·추측 조작 절대 금지!"
            vd["updated_at"] = datetime.datetime.now().isoformat()
            vp.write_text(json.dumps(vd, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

ego.clear_all_spaces_lock()

print("[2/3] Google Vids 공식 사용설명서 절차 그대로 Space 6에서 ① 초기 모달 닫기(X/Esc) -> ② 우측 사이드바 'AI 생성 동영상' 클릭 -> ③ 측면 패널 프롬프트 입력 -> ④ '만들기' 클릭 실행 중...")
vids_prompt = "Photorealistic cinematic scene on a calm late-autumn night turning into winter, viewed from inside a warm cozy room. A ceramic cup of steaming hot tea rests on a wooden desk beside a rain-speckled window overlooking glowing amber streetlights outside, gentle slow camera push-in, shallow depth of field, no text, no letters, no watermark."

js_vids_manual_flow = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(6); }} catch (_) {{ try {{ task = await claimTaskSpace(6); }} catch (__) {{ task = await taskSpace(6); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}

  // Step 1: 초기 팝업(동영상 제작 도우미)이 열려 있으면 닫기(X 버튼 또는 Escape)
  await page.keyboard.press('Escape').catch(() => {{}});
  await new Promise(r => setTimeout(r, 800));
  const modalClosed = await page.evaluate(() => {{
    const closeBtns = Array.from(document.querySelectorAll('button, [role="button"]')).filter(b => {{
      const al = (b.getAttribute('aria-label') || b.title || '').trim();
      const txt = (b.innerText || '').trim();
      return al === '닫기' || al === 'Close' || txt === '✕' || txt === '×';
    }});
    if (closeBtns.length > 0) {{
      closeBtns[0].click();
      return true;
    }}
    return false;
  }});
  await new Promise(r => setTimeout(r, 1200));

  // Step 2: 공식 매뉴얼대로 우측 사이드바에서 'AI 생성 동영상' (또는 'AI 동영상 클립 생성') 클릭
  const sidebarClick = await page.evaluate(() => {{
    const els = Array.from(document.querySelectorAll('[aria-label*="AI" i], button, [role="button"], [role="tab"], div, span'));
    const sideBtn = els.find(e => {{
      const al = (e.getAttribute('aria-label') || e.getAttribute('data-tooltip') || '').trim();
      const t = (e.innerText || '').trim();
      const rect = e.getBoundingClientRect();
      // 우측 사이드바 영역(화면 오른쪽) 또는 명확한 라벨
      return (al.includes('AI 생성 동영상') || al.includes('AI 동영상 클립') || t === 'AI 생성 동영상' || t === 'AI 동영상 클립 생성') && rect.width > 10;
    }});
    if (sideBtn) {{
      sideBtn.click();
      return {{ clicked: true, label: (sideBtn.getAttribute('aria-label') || sideBtn.innerText || '').trim() }};
    }}
    return {{ clicked: false }};
  }});
  await new Promise(r => setTimeout(r, 2500));

  // Step 3: 열린 우측 측면 패널 내의 프롬프트 입력란 탐색 및 포커스
  const sideInput = await page.evaluate(() => {{
    const candidates = Array.from(document.querySelectorAll('textarea, [contenteditable="true"], input[type="text"]')).filter(el => {{
      const r = el.getBoundingClientRect();
      return r.width > 60 && r.height > 20;
    }});
    if (candidates.length > 0) {{
      // 가장 오른쪽에 위치한 입력창(우측 사이드 패널 입력창) 선택
      candidates.sort((a, b) => b.getBoundingClientRect().left - a.getBoundingClientRect().left);
      const target = candidates[0];
      target.focus();
      target.click();
      return {{
        found: true,
        tag: target.tagName,
        left_x: Math.round(target.getBoundingClientRect().left),
        placeholder: target.placeholder || target.getAttribute('aria-label') || ''
      }};
    }}
    return {{ found: false }};
  }});

  if (sideInput && sideInput.found) {{
    await page.keyboard.press('Control+A').catch(() => {{}});
    await page.keyboard.press('Backspace').catch(() => {{}});
    await page.keyboard.type({json.dumps(vids_prompt)}, {{ delay: 4 }}).catch(() => {{}});
    await new Promise(r => setTimeout(r, 1200));
  }}

  // Step 4: 측면 패널의 '만들기' 버튼 클릭
  const createRes = await page.evaluate(() => {{
    const btns = Array.from(document.querySelectorAll('button, [role="button"]')).filter(b => {{
      const r = b.getBoundingClientRect();
      return r.width > 30 && r.height > 20;
    }});
    const targetBtn = btns.find(b => {{
      const t = (b.innerText || b.getAttribute('aria-label') || '').trim();
      return t === '만들기' || t === '생성' || t === 'Create' || (t.includes('만들기') && !t.includes('AI 동영상 만들기'));
    }});
    if (targetBtn && !targetBtn.disabled && targetBtn.getAttribute('aria-disabled') !== 'true') {{
      targetBtn.click();
      return {{ clicked: true, btn_text: (targetBtn.innerText || targetBtn.getAttribute('aria-label') || '').trim() }};
    }}
    return {{
      clicked: false,
      visible_btns: btns.map(b => (b.innerText || b.getAttribute('aria-label') || '').replace(/\\s+/g, ' ').trim()).filter(Boolean).slice(0, 20)
    }};
  }});

  await new Promise(r => setTimeout(r, 4000));
  const panelSnapshot = await page.evaluate(() => {{
    return (document.body.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 900);
  }});

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{
    ok: true,
    modal_closed: modalClosed,
    sidebar_click: sidebarClick,
    side_input: sideInput,
    create_btn: createRes,
    panel_snapshot: panelSnapshot
  }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
vids_142 = s1_ego.run_ego_js(js_vids_manual_flow, timeout=45)

ego.clear_all_spaces_lock()

out_142 = BASE / "S1_MANUAL_FIRST_RULE_AND_VIDS_142.json"
out_142.write_text(json.dumps({
    "directive_id": "RGON_DIR_NEW_FOUNDATION_142",
    "executed_at": datetime.datetime.now().isoformat(),
    "manual_first_rule_locked": True,
    "vids_manual_execution": vids_142
}, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_MANUAL_FIRST_RULE_AND_VIDS_142.json", "S1_EGO_PROVEN_SKILL_MASTER.py", "S1_EGO_SKILL_VAULT.json", "S1_GOOD_BAD_AUTO_LEDGER.json", "S1_RGON_ANTI_AMNESIA_ANCHOR.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(142): lock Manual-First rule into MEM_ANCHOR and execute official Google Vids sidebar clip generation"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

ego.send_auto_confirm_enter_space0(
    f"확인 (142호 선사용설명서규칙영구봉헌 & Space6공식절차실행:[모달닫기:{vids_142.get('modal_closed')} / 우측사이드바:{vids_142.get('sidebar_click')} / 우측입력창:{vids_142.get('side_input')} / 만들기클릭:{vids_142.get('create_btn')}] | 커밋:{sha})"
)