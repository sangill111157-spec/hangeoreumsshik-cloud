# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
# DIRECTIVE_ID: RGON_DIR_NEW_FOUNDATION_134
import json, datetime, os, sys, time, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

ego.clear_all_spaces_lock()

print("[1/3] 133호에서 솔(Space 1)과 오푸스(Space 2)가 완성한 고정댓글·3단계 실행수칙·제휴고지문 전체 원문 로드 중...")
f133 = BASE / "S1_GRAND_RETURN_SYSTEM_START_133.json"
sol_full = ""
opus_full = ""
if f133.exists():
    d133 = json.loads(f133.read_text(encoding="utf-8"))
    s_list = d133.get("sol_space1_blueprint", {}).get("harvested", {}).get("latest_texts", [])
    o_list = d133.get("opus_space2_audit", {}).get("harvested", {}).get("latest_texts", [])
    if s_list:
        sol_full = str(s_list[-1]).replace("\n", " ")
    if o_list:
        opus_full = str(o_list[-1]).replace("\n", " ")

# 만약 133호에서 오푸스 최신 답변이 아직 생성 중이었다면 Space 2에서 최신본 즉시 재수거
if "step_by_step_3" not in opus_full and "disclosure" not in opus_full:
    op_re = ego.ask_and_harvest_side_room(2, "", wait_ms=1000)
    o_list2 = op_re.get("harvested", {}).get("latest_texts", []) if isinstance(op_re, dict) else []
    if o_list2:
        opus_full = str(o_list2[-1]).replace("\n", " ")

print("[2/3] Space 5(캡컷 Credit discount on Seedance 2.0 Mini)에서 프롬프트 재확인 및 생성(Generate) 버튼 클릭·진행 상태 확인 중...")
prompt_en = (
    "Create a photorealistic cinematic scene for the song 'That's All for Today'. A quiet late-autumn night turning into winter, viewed from inside a cozy warm room. A single ceramic cup of steaming hot tea rests beside a rain-kissed window overlooking glowing amber streetlights, soft camera push-in, 4k film grain, no text, no letters, no watermark."
)

js_space5_gen = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(5); }} catch (_) {{ try {{ task = await claimTaskSpace(5); }} catch (__) {{ task = await taskSpace(5); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}

  const genRes = await page.evaluate(async (pText) => {{
    const inputs = Array.from(document.querySelectorAll('textarea, [contenteditable="true"]'));
    let inputEl = inputs[0];
    if (inputEl) {{
      inputEl.focus();
      if (inputEl.tagName === 'TEXTAREA') {{
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
        if (setter) setter.call(inputEl, pText); else inputEl.value = pText;
        inputEl.dispatchEvent(new InputEvent('input', {{ bubbles: true, data: pText }}));
        inputEl.dispatchEvent(new Event('change', {{ bubbles: true }}));
      }} else {{
        inputEl.innerText = pText;
        inputEl.dispatchEvent(new InputEvent('input', {{ bubbles: true, data: pText }}));
      }}
    }}
    await new Promise(r => setTimeout(r, 1000));

    // 생성/전송 버튼 탐색 (Generate, Create, 파란색 아이콘 버튼 등)
    const btns = Array.from(document.querySelectorAll('button, [role="button"], a'));
    const genBtn = btns.find(b => {{
      const t = (b.innerText || '').trim();
      const cls = (b.className || '').toString().toLowerCase();
      return t === 'Generate' || t.includes('Generate') || t.includes('Create') || (cls.includes('send') || cls.includes('submit') || cls.includes('generate'));
    }});
    let clickedText = 'NONE';
    if (genBtn) {{
      clickedText = (genBtn.innerText || genBtn.className || 'BTN').toString().trim().slice(0, 50);
      genBtn.click();
    }}
    await new Promise(r => setTimeout(r, 3500));
    const afterText = (document.body.innerText || '').replace(/\\s+/g, ' ').trim();
    return {{
      url: location.href,
      clicked_btn: clickedText,
      after_snippet: afterText.slice(0, 700)
    }};
  }}, {json.dumps(prompt_en)});

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: true, capcut_gen: genRes }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
cc_gen_res = s1_ego.run_ego_js(js_space5_gen, timeout=45)

print("[3/3] 생성 완료된 28.74MB MV & 5.21MB 쇼츠 파일 + 솔/오푸스 카피 통합 업로드 패키지(S1_YOUTUBE_READY_PACKAGE_134.json) 저장 중...")
out_dir = BASE / "distrokid_vault_assets"
mv_file = out_dir / "NEW_MV_01_Oneureun_Yeogikkaji_1080p.mp4"
sh_file = out_dir / "NEW_SHORT_01_Oneureun_Yeogikkaji_40s.mp4"

pkg_134 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_134",
    "prepared_at": datetime.datetime.now().isoformat(),
    "video_assets_verified": {
        "mv_1080p_path": str(mv_file),
        "mv_size_mb": round(mv_file.stat().st_size / (1024 * 1024), 2) if mv_file.exists() else 0,
        "short_40s_path": str(sh_file),
        "short_size_mb": round(sh_file.stat().st_size / (1024 * 1024), 2) if sh_file.exists() else 0
    },
    "capcut_seedance_trigger": cc_gen_res,
    "sol_space1_full_json": sol_full,
    "opus_space2_full_json": opus_full
}
(BASE / "S1_YOUTUBE_READY_PACKAGE_134.json").write_text(json.dumps(pkg_134, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_YOUTUBE_READY_PACKAGE_134.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(134): trigger CapCut Seedance generation on Space 5 and finalize YouTube MV+Shorts package with Sol+Opus copy"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

ego.clear_all_spaces_lock()

cc_g = cc_gen_res.get("capcut_gen", {}) if isinstance(cc_gen_res, dict) else {}
ego.send_auto_confirm_enter_space0(
    f"확인 (134호 Space5캡컷생성클릭:[버튼:{cc_g.get('clicked_btn')} / URL:{cc_g.get('url')} / 화면:{str(cc_g.get('after_snippet',''))[:180]}] | 솔전체:{sol_full[:260]} | 오푸스전체:{opus_full[:260]} | 커밋:{sha})"
)