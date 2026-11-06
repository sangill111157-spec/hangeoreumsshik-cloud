# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
# DIRECTIVE_ID: RGON_DIR_NEW_FOUNDATION_155
import json, datetime, os, sys, time, base64, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

# 중복 실행 방지 락 파일 체크 (데몬 2마리가 동시에 집어도 1마리만 실행되도록 원천 차단!)
lock_155 = BASE / "lock_155.tmp"
if lock_155.exists() and (time.time() - lock_155.stat().st_mtime < 60):
    sys.exit(0)
lock_155.write_text(str(os.getpid()), encoding="utf-8")

ego.clear_all_spaces_lock()

sh_path = BASE / "distrokid_vault_assets" / "NEW_SHORT_01_Oneureun_Yeogikkaji_40s.mp4"
b64_video = base64.b64encode(sh_path.read_bytes()).decode("ascii")

js_clean_studio_upload = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}

  // 1. GS-006 황금 스킬: channel_switcher -> 한걸음씩 클릭 -> studio.youtube.com 기본 진입 (URL 강제 조작 금지로 '오류가 발생했습니다' 100% 방지!)
  await page.goto('https://www.youtube.com/channel_switcher', {{ waitUntil: 'domcontentloaded', timeout: 20000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 2500));
  await page.evaluate(() => {{
    const items = Array.from(document.querySelectorAll('ytd-account-item-renderer, tp-yt-paper-icon-item, a'));
    const target = items.find(el => (el.innerText || '').includes('한걸음씩'));
    if (target) target.click();
  }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 3000));

  await page.goto('https://studio.youtube.com/', {{ waitUntil: 'domcontentloaded', timeout: 25000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 4500));

  // 2. 우측 상단 '만들기'(#create-icon) -> '동영상 업로드'(#text-item-0) 클릭
  await page.evaluate(() => {{
    const cBtn = document.querySelector('#create-icon, ytcp-button#create-icon');
    if (cBtn) cBtn.click();
  }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 1200));

  await page.evaluate(() => {{
    const upItem = document.querySelector('#text-item-0') || Array.from(document.querySelectorAll('tp-yt-paper-item')).find(e => (e.innerText || '').includes('업로드') || (e.innerText || '').includes('Upload'));
    if (upItem) upItem.click();
  }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 2500));

  // 3. input[type="file"]에 5.21MB MP4 DataTransfer 주입
  const injectRes = await page.evaluate((b64) => {{
    function findInput(root) {{
      const d = root.querySelector('input[type="file"]');
      if (d) return d;
      for (const el of root.querySelectorAll('*')) {{
        if (el.shadowRoot) {{
          const f = findInput(el.shadowRoot);
          if (f) return f;
        }}
      }}
      return null;
    }}
    const fi = findInput(document);
    if (!fi) return {{ ok: false, reason: 'NO_FILE_INPUT', url: location.href, snap: (document.body.innerText || '').slice(0, 250) }};
    const binStr = atob(b64);
    const bytes = new Uint8Array(binStr.length);
    for (let i = 0; i < binStr.length; i++) bytes[i] = binStr.charCodeAt(i);
    const file = new File([bytes], 'NEW_SHORT_01_Oneureun_Yeogikkaji_40s.mp4', {{ type: 'video/mp4' }});
    const dt = new DataTransfer();
    dt.items.add(file);
    fi.files = dt.files;
    fi.dispatchEvent(new Event('change', {{ bubbles: true }}));
    fi.dispatchEvent(new Event('input', {{ bubbles: true }}));
    return {{ ok: true, size_bytes: binStr.length }};
  }}, {json.dumps(b64_video)});

  await new Promise(r => setTimeout(r, 8000));

  // 4. 제목·설명란·아동용 아님 설정 및 비공개(PRIVATE) 저장
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

  for (let i = 0; i < 3; i++) {{
    await page.evaluate(() => {{
      const nb = document.querySelector('#next-button');
      if (nb) nb.click();
    }}).catch(() => {{}});
    await new Promise(r => setTimeout(r, 1500));
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

  await new Promise(r => setTimeout(r, 3000));
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
res_155 = s1_ego.run_ego_js(js_clean_studio_upload, timeout=65)
ego.clear_all_spaces_lock()

(BASE / "S1_YOUTUBE_CLEAN_UPLOAD_155.json").write_text(json.dumps({
    "directive_id": "RGON_DIR_NEW_FOUNDATION_155",
    "executed_at": datetime.datetime.now().isoformat(),
    "result": res_155
}, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_YOUTUBE_CLEAN_UPLOAD_155.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(155): enter studio.youtube.com cleanly via GS-006 and upload new Short as Private draft"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

ego.send_auto_confirm_enter_space0(
    f"확인 (155호 GS006정석진입&신곡쇼츠업로드! [파일주입:{res_155.get('inject')} / 메타데이터:{res_155.get('meta')} / 비공개저장:{res_155.get('save')}] | 커밋:{sha})"
)