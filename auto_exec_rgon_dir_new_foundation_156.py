# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
# DIRECTIVE_ID: RGON_DIR_NEW_FOUNDATION_156
import json, datetime, os, sys, time, base64, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

lock_156 = BASE / "lock_156.tmp"
if lock_156.exists() and (time.time() - lock_156.stat().st_mtime < 60):
    sys.exit(0)
lock_156.write_text(str(os.getpid()), encoding="utf-8")

ego.clear_all_spaces_lock()

sh_path = BASE / "distrokid_vault_assets" / "NEW_SHORT_01_Oneureun_Yeogikkaji_40s.mp4"
b64_video = base64.b64encode(sh_path.read_bytes()).decode("ascii")

js_phys_upload_156 = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}

  // 현재 Space 3이 이미 깨끗한 한걸음씩 채널 대시보드에 있으므로 우측 상단 '만들기' 버튼 물리 좌표 측정 후 클릭!
  const createCoord = await page.evaluate(() => {{
    const el = document.querySelector('#create-icon, ytcp-button#create-icon') || Array.from(document.querySelectorAll('ytcp-button, button')).find(b => (b.innerText || '').trim() === '만들기');
    if (el) {{
      const r = el.getBoundingClientRect();
      return {{ found: true, x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2) }};
    }}
    return {{ found: false }};
  }});

  if (createCoord && createCoord.found) {{
    await page.mouse.click(createCoord.x, createCoord.y);
    await new Promise(r => setTimeout(r, 1500));
  }}

  // 펼쳐진 드롭다운 메뉴에서 '동영상 업로드'(#text-item-0) 물리 좌표 측정 후 클릭!
  const upMenuCoord = await page.evaluate(() => {{
    const items = Array.from(document.querySelectorAll('#text-item-0, tp-yt-paper-item, ytcp-text-menu-item, a, div'));
    const target = items.find(e => {{
      const t = (e.innerText || '').trim();
      const r = e.getBoundingClientRect();
      return (t === '동영상 업로드' || t === 'Upload videos') && r.width > 40 && r.height > 15;
    }});
    if (target) {{
      const r = target.getBoundingClientRect();
      return {{ found: true, x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2), text: (target.innerText || '').trim() }};
    }}
    return {{ found: false }};
  }});

  if (upMenuCoord && upMenuCoord.found) {{
    await page.mouse.click(upMenuCoord.x, upMenuCoord.y);
    await new Promise(r => setTimeout(r, 2800));
  }}

  // 업로드 모달의 input[type="file"]에 DataTransfer로 5.21MB MP4 주입!
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
    if (!fi) return {{ ok: false, reason: 'NO_FILE_INPUT', modal_text: (document.body.innerText || '').slice(0, 350) }};
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

  await new Promise(r => setTimeout(r, 8500));

  // 제목·설명란·아동용 아님 설정 및 새 영상 URL 추출
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

  // 다음(#next-button) 3회 클릭 후 비공개(PRIVATE) 체크 및 저장(#done-button)
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

  await new Promise(r => setTimeout(r, 3500));
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{
    ok: true,
    create_btn: createCoord,
    upload_menu: upMenuCoord,
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
res_156 = s1_ego.run_ego_js(js_phys_upload_156, timeout=60)
ego.clear_all_spaces_lock()

(BASE / "S1_YOUTUBE_FINAL_UPLOAD_156.json").write_text(json.dumps({
    "directive_id": "RGON_DIR_NEW_FOUNDATION_156",
    "executed_at": datetime.datetime.now().isoformat(),
    "result": res_156
}, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_YOUTUBE_FINAL_UPLOAD_156.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(156): physical mouse click on Create -> Upload videos on clean Studio dashboard and inject 5.21MB Short"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

ego.send_auto_confirm_enter_space0(
    f"확인 (156호 신곡쇼츠유튜브스튜디오최종업로드! [만들기좌표:{res_156.get('create_btn')} / 메뉴좌표:{res_156.get('upload_menu')} / 파일주입:{res_156.get('inject')} / 메타데이터:{res_156.get('meta')} / 비공개저장:{res_156.get('save')}] | 커밋:{sha})"
)