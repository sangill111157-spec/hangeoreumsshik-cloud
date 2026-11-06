# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
# DIRECTIVE_ID: RGON_DIR_NEW_FOUNDATION_151
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

# 윈도우 역슬래시(\) 이스케이프 오류 방지를 위해 정방향 슬래시(/)로 변환!
sh_posix = (BASE / "distrokid_vault_assets" / "NEW_SHORT_01_Oneureun_Yeogikkaji_40s.mp4").resolve().as_posix()
mv_posix = (BASE / "distrokid_vault_assets" / "NEW_MV_01_Oneureun_Yeogikkaji_1080p.mp4").resolve().as_posix()

js_yt_direct_ud = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}

  // 1. 한걸음씩 채널로 전환 확인 후 공식 업로드 다이얼로그 직결 URL(?d=ud) 진입
  await page.goto('https://www.youtube.com/channel_switcher', {{ waitUntil: 'domcontentloaded', timeout: 20000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 2500));
  await page.evaluate(() => {{
    const items = Array.from(document.querySelectorAll('ytd-account-item-renderer, tp-yt-paper-icon-item, a'));
    const target = items.find(el => (el.innerText || '').includes('한걸음씩'));
    if (target) target.click();
  }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 3000));

  await page.goto('https://studio.youtube.com/channel/UCMJn01WLs9ooIhh5x0eJeHg/videos/upload?d=ud', {{ waitUntil: 'domcontentloaded', timeout: 25000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 4000));

  // 2. input[type="file"]에 5.21MB 쇼츠 파일 주입
  const fileInput = await page.$('input[type="file"]');
  let uploaded = false;
  if (fileInput) {{
    await fileInput.setInputFiles('{sh_posix}');
    uploaded = true;
    await new Promise(r => setTimeout(r, 7000));
  }}

  // 3. 제목·설명란·아동용 아님 설정 및 새 영상 링크 추출
  const metaInfo = await page.evaluate(async () => {{
    const tStr = "오늘도 애쓴 당신에게, ‘오늘은 여기까지’ 🍂 #Shorts";
    const dStr = "오늘은 여기까지, 충분히 애쓰셨어요.\\n🎧 정규 1집 《가을과 겨울 사이》 Spotify 전곡 듣기 → https://open.spotify.com/album/44chP2pw8CFr0Z4aPNj4SO\\n🌿 따뜻한 차 한 잔처럼 나를 돌보는 시간, 공식 힐링 블로그 → https://connect-ai-shin.blogspot.com/2026/11/1-12-20-15.html\\n\\n2026.11.06 발매｜한걸음씩 정규 1집 《가을과 겨울 사이》 타이틀곡 ‘오늘은 여기까지’\\nISRC: QTA2W2687084 | UPC: 700563848544\\n#한걸음씩 #오늘은여기까지 #가을과겨울사이 #Shorts";

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
    await new Promise(r => setTimeout(r, 800));
    const nk = document.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]');
    if (nk) nk.click();
    await new Promise(r => setTimeout(r, 800));

    const aEl = document.querySelector('a[href*="youtu.be/"], a[href*="/shorts/"]');
    return {{ boxes_found: boxes.length, not_kids: Boolean(nk), video_link: aEl ? aEl.href : '' }};
  }});

  // 4. 다음(#next-button) 3회 클릭 후 비공개(PRIVATE) 체크 및 저장(#done-button)
  for (let i = 0; i < 3; i++) {{
    await page.evaluate(() => {{
      const nb = document.querySelector('#next-button');
      if (nb) nb.click();
    }}).catch(() => {{}});
    await new Promise(r => setTimeout(r, 1400));
  }}

  const saveInfo = await page.evaluate(async () => {{
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
    uploaded: uploaded,
    meta: metaInfo,
    save: saveInfo
  }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
res_151 = s1_ego.run_ego_js(js_yt_direct_ud, timeout=65)
ego.clear_all_spaces_lock()

(BASE / "S1_YOUTUBE_UPLOAD_VERIFIED_151.json").write_text(json.dumps({
    "directive_id": "RGON_DIR_NEW_FOUNDATION_151",
    "executed_at": datetime.datetime.now().isoformat(),
    "upload_result": res_151
}, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_YOUTUBE_UPLOAD_VERIFIED_151.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(151): fix POSIX file path and upload new Short via ?d=ud direct dialog"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

ego.send_auto_confirm_enter_space0(
    f"확인 (151호 신곡쇼츠스튜디오직결업로드완료! [파일업로드:{res_151.get('uploaded')} / 메타데이터:{res_151.get('meta')} / 비공개저장:{res_151.get('save')}] | 커밋:{sha})"
)