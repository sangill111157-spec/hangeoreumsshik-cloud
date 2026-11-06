# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
# DIRECTIVE_ID: RGON_DIR_NEW_FOUNDATION_154
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

js_open_and_upload = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}

  // 1. 대시보드 화면에서 '동영상 업로드' 또는 '만들기' 버튼의 실제 물리 좌표(x, y) 측정
  const btnCoords = await page.evaluate(() => {{
    const all = Array.from(document.querySelectorAll('ytcp-button, button, a, [role="button"], div, span'));
    const directUp = all.find(e => {{
      const t = (e.innerText || '').trim();
      const r = e.getBoundingClientRect();
      return (t === '동영상 업로드' || t === 'Upload videos') && r.width > 40 && r.height > 20;
    }});
    if (directUp) {{
      const r = directUp.getBoundingClientRect();
      return {{ mode: 'direct_upload_btn', x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2) }};
    }}
    const createBtn = document.querySelector('#create-icon, ytcp-button#create-icon') || all.find(e => {{
      const t = (e.innerText || e.getAttribute('aria-label') || '').trim();
      const r = e.getBoundingClientRect();
      return (t === '만들기' || t === 'Create') && r.width > 30 && r.height > 20;
    }});
    if (createBtn) {{
      const r = createBtn.getBoundingClientRect();
      return {{ mode: 'create_menu_btn', x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2) }};
    }}
    return {{ mode: 'none', url: location.href, text: (document.body.innerText || '').slice(0, 300) }};
  }});

  if (btnCoords.mode === 'direct_upload_btn') {{
    await page.mouse.click(btnCoords.x, btnCoords.y);
    await new Promise(r => setTimeout(r, 2500));
  }} else if (btnCoords.mode === 'create_menu_btn') {{
    await page.mouse.click(btnCoords.x, btnCoords.y);
    await new Promise(r => setTimeout(r, 1200));
    const menuCoord = await page.evaluate(() => {{
      const items = Array.from(document.querySelectorAll('tp-yt-paper-item, ytcp-text-menu-item, #text-item-0'));
      const upItem = items.find(el => (el.innerText || '').includes('동영상 업로드') || (el.innerText || '').includes('Upload'));
      if (upItem) {{
        const r = upItem.getBoundingClientRect();
        return {{ found: true, x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2) }};
      }}
      return {{ found: false }};
    }});
    if (menuCoord && menuCoord.found) {{
      await page.mouse.click(menuCoord.x, menuCoord.y);
      await new Promise(r => setTimeout(r, 2500));
    }}
  }}

  // 2. 일반 DOM 및 Shadow DOM 전체를 뒤져 input[type="file"] 탐색 후 DataTransfer 주입
  const injectRes = await page.evaluate((b64) => {{
    function findFileInput(root) {{
      const direct = root.querySelector('input[type="file"]');
      if (direct) return direct;
      const els = root.querySelectorAll('*');
      for (const el of els) {{
        if (el.shadowRoot) {{
          const found = findFileInput(el.shadowRoot);
          if (found) return found;
        }}
      }}
      return null;
    }}
    const fileInput = findFileInput(document);
    if (!fileInput) {{
      // 드롭존(ytcp-uploads-file-picker) 탐색
      const dropZone = document.querySelector('ytcp-uploads-file-picker, #select-files-button');
      if (!dropZone) return {{ ok: false, reason: 'NO_INPUT_OR_DROPZONE', body: (document.body.innerText || '').slice(0, 300) }};
      const binStr = atob(b64);
      const bytes = new Uint8Array(binStr.length);
      for (let i = 0; i < binStr.length; i++) bytes[i] = binStr.charCodeAt(i);
      const file = new File([bytes], 'NEW_SHORT_01_Oneureun_Yeogikkaji_40s.mp4', {{ type: 'video/mp4' }});
      const dt = new DataTransfer();
      dt.items.add(file);
      const dropEvent = new DragEvent('drop', {{ bubbles: true, cancelable: true, dataTransfer: dt }});
      dropZone.dispatchEvent(dropEvent);
      return {{ ok: true, method: 'dropzone_drag_drop', size_bytes: binStr.length }};
    }}
    const binStr = atob(b64);
    const bytes = new Uint8Array(binStr.length);
    for (let i = 0; i < binStr.length; i++) bytes[i] = binStr.charCodeAt(i);
    const file = new File([bytes], 'NEW_SHORT_01_Oneureun_Yeogikkaji_40s.mp4', {{ type: 'video/mp4' }});
    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;
    fileInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
    fileInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
    return {{ ok: true, method: 'shadow_input_file', size_bytes: binStr.length }};
  }}, {json.dumps(b64_video)});

  await new Promise(r => setTimeout(r, 8000));

  // 3. 제목·설명란·아동용 아님 설정 및 비공개 초안 저장
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
    btn_coords: btnCoords,
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
res_154 = s1_ego.run_ego_js(js_open_and_upload, timeout=60)
ego.clear_all_spaces_lock()

(BASE / "S1_YOUTUBE_SHADOW_UPLOAD_154.json").write_text(json.dumps({
    "directive_id": "RGON_DIR_NEW_FOUNDATION_154",
    "executed_at": datetime.datetime.now().isoformat(),
    "result": res_154
}, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_YOUTUBE_SHADOW_UPLOAD_154.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(154): physical mouse click on Upload button and Shadow DOM / DragEvent file injection"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

ego.send_auto_confirm_enter_space0(
    f"확인 (154호 신곡쇼츠물리클릭업로드! [버튼좌표:{res_154.get('btn_coords')} / 파일주입:{res_154.get('inject')} / 메타데이터:{res_154.get('meta')} / 비공개저장:{res_154.get('save')}] | 커밋:{sha})"
)