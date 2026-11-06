# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
# DIRECTIVE_ID: RGON_DIR_NEW_FOUNDATION_152
import json, datetime, os, sys, time, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

# 151호 에러 원인 먼저 로드
err_151 = ""
f151 = BASE / "S1_YOUTUBE_UPLOAD_VERIFIED_151.json"
if f151.exists():
    try:
        err_151 = str(json.loads(f151.read_text(encoding="utf-8")).get("upload_result", {}))[:180]
    except Exception:
        pass

ego.clear_all_spaces_lock()

sh_posix = (BASE / "distrokid_vault_assets" / "NEW_SHORT_01_Oneureun_Yeogikkaji_40s.mp4").resolve().as_posix()

js_fast_upload = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}

  // 현재 Space 3이 이미 한걸음씩 채널 대시보드(사진 FnMBcwuz 확인 완료!)에 있으므로 바로 업로드 모달 열기
  await page.evaluate(() => {{
    const btn = document.querySelector('#create-icon, ytcp-button#create-icon, [aria-label*="만들기"], [aria-label*="Create"]');
    if (btn) btn.click();
  }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 1200));

  await page.evaluate(() => {{
    const items = Array.from(document.querySelectorAll('tp-yt-paper-item, ytcp-text-menu-item, #text-item-0'));
    const upItem = items.find(el => (el.innerText || '').includes('동영상 업로드') || (el.innerText || '').includes('Upload'));
    if (upItem) upItem.click();
  }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 2000));

  const fileInput = await page.$('input[type="file"]');
  let hasFileInput = Boolean(fileInput);
  let fileInjected = false;
  if (fileInput) {{
    await fileInput.setInputFiles('{sh_posix}');
    fileInjected = true;
    await new Promise(r => setTimeout(r, 5000));
  }}

  const statusInfo = await page.evaluate(() => {{
    const tStr = "오늘도 애쓴 당신에게, ‘오늘은 여기까지’ 🍂 #Shorts";
    const dStr = "오늘은 여기까지, 충분히 애쓰셨어요.\\n🎧 정규 1집 《가을과 겨울 사이》 Spotify 전곡 듣기 → https://open.spotify.com/album/44chP2pw8CFr0Z4aPNj4SO\\n🌿 공식 힐링·건강 블로그 → https://connect-ai-shin.blogspot.com/2026/11/1-12-20-15.html\\n\\n#한걸음씩 #오늘은여기까지 #가을과겨울사이 #Shorts";
    const boxes = Array.from(document.querySelectorAll('#textbox'));
    if (boxes.length >= 1) {{
      boxes[0].focus();
      boxes[0].innerText = tStr;
      boxes[0].dispatchEvent(new InputEvent('input', {{ bubbles: true, data: tStr }}));
    }}
    if (boxes.length >= 2) {{
      boxes[1].focus();
      boxes[1].innerText = dStr;
      boxes[1].dispatchEvent(new InputEvent('input', {{ bubbles: true, data: dStr }}));
    }}
    const nk = document.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]');
    if (nk) nk.click();
    const aEl = document.querySelector('a[href*="youtu.be/"], a[href*="/shorts/"]');
    return {{ url: location.href, boxes: boxes.length, video_url: aEl ? aEl.href : '' }};
  }}).catch(e => ({{ err: String(e) }}));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{
    ok: true,
    has_input: hasFileInput,
    injected: fileInjected,
    status: statusInfo
  }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
res_152 = s1_ego.run_ego_js(js_fast_upload, timeout=35)
ego.clear_all_spaces_lock()

(BASE / "S1_YOUTUBE_UPLOAD_FAST_152.json").write_text(json.dumps({
    "directive_id": "RGON_DIR_NEW_FOUNDATION_152",
    "prev_151_diag": err_151,
    "result_152": res_152
}, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_YOUTUBE_UPLOAD_FAST_152.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(152): fast direct upload modal injection on Space 3"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

ego.send_auto_confirm_enter_space0(
    f"확인 (152호 Space3고속업로드:[파일창:{res_152.get('has_input')} / 주입:{res_152.get('injected')} / 상태:{res_152.get('status')} / 에러참고:{res_152.get('error','')[:100]} / 151진단:{err_151[:100]}] | 커밋:{sha})"
)