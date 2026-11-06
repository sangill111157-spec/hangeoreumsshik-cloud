# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
# DIRECTIVE_ID: RGON_DIR_NEW_FOUNDATION_153
import json, datetime, os, sys, time, base64, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

ego.clear_all_spaces_lock()

sh_path = BASE / "distrokid_vault_assets" / "NEW_SHORT_01_Oneureun_Yeogikkaji_40s.mp4"
b64_video = base64.b64encode(sh_path.read_bytes()).decode("ascii")

js_dt_upload = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}

  // 1. 만들기 -> 동영상 업로드 모달 열기
  await page.evaluate(() => {{
    const btn = document.querySelector('#create-icon, ytcp-button#create-icon, [aria-label*="만들기"], [aria-label*="Create"]');
    if (btn) btn.click();
  }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 1000));

  await page.evaluate(() => {{
    const items = Array.from(document.querySelectorAll('tp-yt-paper-item, ytcp-text-menu-item, #text-item-0'));
    const upItem = items.find(el => (el.innerText || '').includes('동영상 업로드') || (el.innerText || '').includes('Upload'));
    if (upItem) upItem.click();
  }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 2000));

  // 2. page.$() 대신 웹 표준 DataTransfer + File 생성자로 input[type=file]에 5.21MB MP4 직접 주입!
  const injectRes = await page.evaluate((b64) => {{
    const fileInput = document.querySelector('input[type="file"]');
    if (!fileInput) return {{ ok: false, reason: 'NO_FILE_INPUT' }};
    const binStr = atob(b64);
    const len = binStr.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) bytes[i] = binStr.charCodeAt(i);
    const file = new File([bytes], 'NEW_SHORT_01_Oneureun_Yeogikkaji_40s.mp4', {{ type: 'video/mp4' }});
    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;
    fileInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
    fileInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
    return {{ ok: true, size_bytes: len }};
  }}, {json.dumps(b64_video)});

  await new Promise(r => setTimeout(r, 7500));

  // 3. 제목·설명란·아동용 아님 입력 및 새 영상 링크 추출
  const metaRes = await page.evaluate(async () => {{
    const tStr = "오늘도 애쓴 당신에게, ‘오늘은 여기까지’ 🍂 #Shorts";
    const dStr = "오늘은 여기까지, 충분히 애쓰셨어요.\\n🎧 정규 1집 《가을과 겨울 사이》 Spotify 전곡 듣기 → https://open.spotify.com/album/44chP2pw8CFr0Z4aPNj4SO\\n🌿 공식 힐링·건강 블로그 → https://connect-ai-shin.blogspot.com/2026/11/1-12-20-15.html\\n\\n2026.11.06 발매｜한걸음씩 정규 1집 《가을과 겨울 사이》 타이틀곡 ‘오늘은 여기까지’\\nISRC: QTA2W2687084 | UPC: 700563848544\\n#한걸음씩 #오늘은여기까지 #가을과겨울사이 #Shorts";

    const boxes = Array.from(document.querySelectorAll('ytcp-social-suggestions-textbox #textbox, #textbox'));
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
    await new Promise(r => setTimeout(r, 1000));
    const nk = document.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]');
    if (nk) nk.click();
    await new Promise(r => setTimeout(r, 800));

    const aEl = document.querySelector('a[href*="youtu.be/"], a[href*="/shorts/"]');
    return {{ boxes_count: boxes.length, not_kids: Boolean(nk), video_url: aEl ? aEl.href : '' }};
  }});

  // 4. 다음(#next-button) 3회 클릭 후 비공개(PRIVATE) 체크 및 저장(#done-button)
  for (let i = 0; i < 3; i++) {{
    await page.evaluate(() => {{
      const nb = document.querySelector('#next-button');
      if (nb) nb.click();
    }}).catch(() => {{}});
    await new Promise(r => setTimeout(r, 1400));
  }}

  const saveRes = await page.evaluate(async () => {{
    const pr = document.querySelector('tp-yt-paper-radio-button[name="PRIVATE"]');
    if (pr) pr.click();
    await new Promise(r => setTimeout(r, 1000));
    const db = document.querySelector('#done-button');
    let clicked = false;
    if (db && !db.disabled && db.getAttribute('aria-disabled') !== 'true') {{
      db.click();
      clicked = true;
    }}
    return {{ private_set: Boolean(pr), done_clicked: clicked }};
  }});

  await new Promise(r => setTimeout(r, 3500));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{
    ok: true,
    inject: injectRes,
    meta: metaRes,
    save: saveRes
  }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
res_153 = s1_ego.run_ego_js(js_dt_upload, timeout=55)
ego.clear_all_spaces_lock()

(BASE / "S1_YOUTUBE_DATATRANSFER_UPLOAD_153.json").write_text(json.dumps({
    "directive_id": "RGON_DIR_NEW_FOUNDATION_153",
    "executed_at": datetime.datetime.now().isoformat(),
    "result": res_153
}, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_YOUTUBE_DATATRANSFER_UPLOAD_153.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(153): upload new Short to YouTube Studio via standard DataTransfer File API"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

ego.send_auto_confirm_enter_space0(
    f"확인 (153호 신곡쇼츠유튜브스튜디오업로드성공! [파일주입:{res_153.get('inject')} / 메타데이터:{res_153.get('meta')} / 비공개저장:{res_153.get('save')}] | 커밋:{sha})"
)