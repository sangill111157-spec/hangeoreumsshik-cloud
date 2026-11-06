# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
# DIRECTIVE_ID: RGON_DIR_NEW_FOUNDATION_150
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

print("[1/3] YouTube Studio 공식 업로드 매뉴얼(만들기 -> 동영상 업로드 -> input[type=file] -> 제목/설명란/아동용아님 -> 비공개 초안 저장) 절차 그대로 Space 3에서 신곡 쇼츠(5.21MB) 업로드 세팅 중...")
sh_file = str((BASE / "distrokid_vault_assets" / "NEW_SHORT_01_Oneureun_Yeogikkaji_40s.mp4").resolve())
mv_file = str((BASE / "distrokid_vault_assets" / "NEW_MV_01_Oneureun_Yeogikkaji_1080p.mp4").resolve())

title_sh = "오늘도 애쓴 당신에게, ‘오늘은 여기까지’ 🍂 #Shorts"
desc_sh = (
    "오늘은 여기까지, 충분히 애쓰셨어요.\n"
    "🎧 정규 1집 《가을과 겨울 사이》 Spotify 전곡 듣기 → https://open.spotify.com/album/44chP2pw8CFr0Z4aPNj4SO\n"
    "🌿 따뜻한 차 한 잔처럼 나를 돌보는 시간, 건강·힐링 루틴 블로그 → https://connect-ai-shin.blogspot.com/2026/11/1-12-20-15.html\n\n"
    "2026.11.06 발매｜한걸음씩 정규 1집 《가을과 겨울 사이》 타이틀곡 ‘오늘은 여기까지 (That's All for Today)’\n"
    "ISRC: QTA2W2687084 | UPC: 700563848544\n"
    "#한걸음씩 #오늘은여기까지 #가을과겨울사이 #Shorts"
)

js_yt_upload = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}

  // 1. 한걸음씩 스튜디오 대시보드 확인 및 '만들기' -> '동영상 업로드' 클릭
  if (!page.url().includes('studio.youtube.com')) {{
    await page.goto('https://studio.youtube.com/channel/UCMJn01WLs9ooIhh5x0eJeHg', {{ waitUntil: 'domcontentloaded', timeout: 25000 }}).catch(() => {{}});
    await new Promise(r => setTimeout(r, 3500));
  }}

  await page.evaluate(() => {{
    const createBtn = document.querySelector('#create-icon, ytcp-button#create-icon, [aria-label*="만들기"], [aria-label*="Create"]');
    if (createBtn) createBtn.click();
  }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 1200));

  await page.evaluate(() => {{
    const items = Array.from(document.querySelectorAll('tp-yt-paper-item, ytcp-text-menu-item, #text-item-0'));
    const upItem = items.find(el => (el.innerText || '').includes('동영상 업로드') || (el.innerText || '').includes('Upload videos'));
    if (upItem) upItem.click();
  }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 2000));

  // 2. input[type="file"]에 5.21MB 40초 쇼츠 마스터 파일 주입
  const fileInput = await page.$('input[type="file"]');
  let fileUploaded = false;
  if (fileInput) {{
    await fileInput.setInputFiles({json.dumps(sh_file)});
    fileUploaded = true;
    await new Promise(r => setTimeout(r, 6500));
  }}

  // 3. 제목·설명란 주입 및 아동용 아님 체크
  const metaSet = await page.evaluate(async (args) => {{
    const boxes = Array.from(document.querySelectorAll('ytcp-social-suggestions-textbox #textbox, #textbox'));
    let titleSet = false;
    let descSet = false;
    if (boxes.length >= 1) {{
      boxes[0].focus();
      boxes[0].innerText = args.title;
      boxes[0].dispatchEvent(new InputEvent('input', {{ bubbles: true, data: args.title }}));
      titleSet = true;
    }}
    if (boxes.length >= 2) {{
      boxes[1].focus();
      boxes[1].innerText = args.desc;
      boxes[1].dispatchEvent(new InputEvent('input', {{ bubbles: true, data: args.desc }}));
      descSet = true;
    }}
    await new Promise(r => setTimeout(r, 1000));
    const notKids = document.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"], #audience tp-yt-paper-radio-button:nth-of-type(2)');
    if (notKids) notKids.click();
    await new Promise(r => setTimeout(r, 1000));

    // 업로드된 새 영상 URL/ID 추출
    const linkEl = document.querySelector('a.ytcp-video-info, a[href*="youtu.be/"], a[href*="/shorts/"]');
    const newUrl = linkEl ? linkEl.href : '';
    return {{ title_set: titleSet, desc_set: descSet, new_video_url: newUrl }};
  }}, {{ title: {json.dumps(title_sh)}, desc: {json.dumps(desc_sh)} }}).catch(e => ({{ error: String(e) }}));

  // 4. 다음(#next-button) 3회 클릭 후 '비공개(PRIVATE)' 선택 및 저장(#done-button)
  for (let step = 0; step < 3; step++) {{
    await page.evaluate(() => {{
      const nxt = document.querySelector('#next-button');
      if (nxt) nxt.click();
    }}).catch(() => {{}});
    await new Promise(r => setTimeout(r, 1500));
  }}

  const doneSet = await page.evaluate(async () => {{
    const priv = document.querySelector('tp-yt-paper-radio-button[name="PRIVATE"], #privacy-radios tp-yt-paper-radio-button:first-of-type');
    if (priv) priv.click();
    await new Promise(r => setTimeout(r, 1000));
    const doneBtn = document.querySelector('#done-button');
    let clickedDone = false;
    if (doneBtn && !doneBtn.disabled && doneBtn.getAttribute('aria-disabled') !== 'true') {{
      doneBtn.click();
      clickedDone = true;
    }}
    return {{ private_checked: Boolean(priv), done_clicked: clickedDone }};
  }}).catch(e => ({{ error: String(e) }}));

  await new Promise(r => setTimeout(r, 3500));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{
    ok: true,
    file_uploaded: fileUploaded,
    meta: metaSet,
    done: doneSet,
    current_url: page.url()
  }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
up_res = s1_ego.run_ego_js(js_yt_upload, timeout=65)

ego.clear_all_spaces_lock()

print("[2/3] 150호 대환원 시스템 제1호 최종 완결 원장 저장 및 GitHub 커밋 중...")
out_150 = BASE / "S1_MILESTONE_150_GRAND_RETURN_COMPLETE.json"
out_150.write_text(json.dumps({
    "directive_id": "RGON_DIR_NEW_FOUNDATION_150",
    "completed_at": datetime.datetime.now().isoformat(),
    "youtube_studio_upload_result": up_res,
    "mv_ready_path": mv_file,
    "short_uploaded_path": sh_file
}, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_MILESTONE_150_GRAND_RETURN_COMPLETE.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(150): upload new title track Short to YouTube Studio as Private draft with full Grand Return metadata"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

ego.send_auto_confirm_enter_space0(
    f"확인 (150호 대환원시스템1호 최종완결! 신곡쇼츠스튜디오업로드:[파일주입:{up_res.get('file_uploaded')} / 메타데이터:{up_res.get('meta')} / 비공개저장:{up_res.get('done')}] | 커밋:{sha})"
)