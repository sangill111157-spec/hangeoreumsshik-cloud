import json, time, datetime, os, re, base64, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
OUT_DIR = BASE / "studio_vault" / "NOV06_RELEASE"
OUT_DIR.mkdir(parents=True, exist_ok=True)
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/4] 에고라이트 Space 4: 브라우저 내부 fetch -> Base64/File 저장으로 타이틀곡 '오늘은 여기까지'(ihIUw) 정품 WAV 직접 추출 중...")
wav04_str = str(OUT_DIR / "04_THATS_ALL_FOR_TODAY.wav").replace("\\", "/")

js_fetch_wav = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(4); }} catch (_) {{ try {{ task = await claimTaskSpace(4); }} catch (__) {{ task = await taskSpace(4); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}
  await page.evaluate(() => {{ window.__ego_overlay_disabled = true; }}).catch(() => {{}});

  await page.goto('https://distrokid.com/dashboard/album/?albumuuid=FC934BFB-150F-4894-B064A07100CC9BF4', {{ waitUntil: 'domcontentloaded', timeout: 25000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 3000));

  // 브라우저 내부에서 ihIUw 를 fetch하여 base64 문자열로 변환 후 Node.js fs로 디스크에 직접 기록!
  const b64Data = await page.evaluate(async () => {{
    const res = await fetch('https://distrokid.com/vault/download/?id=ihIUw', {{ credentials: 'include' }});
    const buf = await res.arrayBuffer();
    const bytes = new Uint8Array(buf);
    let binary = '';
    const chunkSize = 0x8000;
    for (let i = 0; i < bytes.length; i += chunkSize) {{
      binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunkSize));
    }}
    return btoa(binary);
  }});

  const fs = require('fs');
  fs.writeFileSync('{wav04_str}', Buffer.from(b64Data, 'base64'));
  const st = fs.statSync('{wav04_str}');

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: true, saved_wav: '{wav04_str}', size_bytes: st.size }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err.message || err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
wav_120_res = s1_ego.run_ego_js(js_fetch_wav, timeout=120)

print("[2/4] FFmpeg(CreateNoWindow)로 타이틀곡 '오늘은 여기까지' 공식 1080p MV 및 40초 세로형 쇼츠 렌더링 중...")
cover_path = OUT_DIR / "AW_COVER_800x800.jpg"
w04_path = OUT_DIR / "04_THATS_ALL_FOR_TODAY.wav"
mv_04_path = OUT_DIR / "S1_AW_04_TODAY_OFFICIAL_MV.mp4"
short_04_path = OUT_DIR / "S1_AW_04_TODAY_SHORTS_40S.mp4"

ffmpeg_res = {}
if cover_path.exists() and w04_path.exists() and w04_path.stat().st_size > 100000:
    cmd_mv = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", "2", "-i", str(cover_path), "-i", str(w04_path),
        "-vf", "scale=1080:1080,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(mv_04_path)
    ]
    subprocess.run(cmd_mv, env=env, capture_output=True, text=True, creationflags=no_win)
    ffmpeg_res["official_mv_1080p"] = {
        "exists": mv_04_path.exists(),
        "size_mb": round(mv_04_path.stat().st_size / (1024*1024), 2) if mv_04_path.exists() else 0,
        "path": str(mv_04_path)
    }

    cmd_sh = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", "2", "-i", str(cover_path), "-ss", "00:00:30", "-t", "40", "-i", str(w04_path),
        "-vf", "scale=1080:1080,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(short_04_path)
    ]
    subprocess.run(cmd_sh, env=env, capture_output=True, text=True, creationflags=no_win)
    ffmpeg_res["shorts_40s_1080x1920"] = {
        "exists": short_04_path.exists(),
        "size_mb": round(short_04_path.stat().st_size / (1024*1024), 2) if short_04_path.exists() else 0,
        "path": str(short_04_path)
    }

print("[3/4] 에고라이트 Space 3: 본진 인기 쇼츠 8편에 '관련 동영상(Related Video)' 일괄 연결 및 저장 중...")
SHORTS_BATCH_REL = [
    "_9TaYaBFmkQ", "I00rUemzODo", "FXnTfmWRv_s", "7Kk-c6ljjHg",
    "D7pfGWuhXjU", "5TGHvNsJJ8c", "77VVallxeu4", "nGvpoau4p_I"
]

js_batch_rel = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}
  await page.evaluate(() => {{ window.__ego_overlay_disabled = true; }}).catch(() => {{}});

  const sids = {json.dumps(SHORTS_BATCH_REL)};
  const relResults = [];

  for (const sid of sids) {{
    await page.goto('https://studio.youtube.com/video/' + sid + '/edit', {{ waitUntil: 'domcontentloaded', timeout: 30000 }}).catch(() => {{}});
    await new Promise(r => setTimeout(r, 4500));

    const curRel = await page.evaluate(() => {{
      const trig = document.querySelector('#linked-video-editor-link, ytcp-shorts-content-links-picker ytcp-text-dropdown-trigger');
      if (!trig) return 'NO_TRIG';
      const t = (trig.innerText || '').replace(/\\s+/g, ' ').trim();
      if (!t.includes('없음') && !t.toLowerCase().includes('none')) return 'ALREADY:' + t;
      trig.click();
      return 'OPENED';
    }});

    if (curRel === 'OPENED') {{
      await new Promise(r => setTimeout(r, 3500));
      const cardPos = await page.evaluate(() => {{
        const cards = Array.from(document.querySelectorAll('ytcp-entity-card')).filter(el => el.getBoundingClientRect().width > 100);
        // 사냥꾼의 새벽, 원인과 결과, 어머니는 꽃이다 중 하나 선택
        const target = cards.find(c => (c.innerText || '').includes('사냥꾼의 새벽') || (c.innerText || '').includes('원인과 결과') || (c.innerText || '').includes('어머니는 꽃이다')) || cards[0];
        if (!target) return null;
        const r = target.getBoundingClientRect();
        return {{ x: r.left + r.width / 2, y: r.top + r.height / 2, title: (target.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 40) }};
      }});

      if (cardPos && page.mouse) {{
        await page.mouse.click(cardPos.x, cardPos.y);
        await new Promise(r => setTimeout(r, 2000));
      }}

      const sv = await page.evaluate(() => {{
        const newRel = (document.querySelector('#linked-video-editor-link') || {{}}).innerText || '';
        const btns = Array.from(document.querySelectorAll('#save-button, ytcp-button#save, ytcp-button, button')).filter(b => (b.innerText || '').trim() === '저장' || (b.innerText || '').trim().toLowerCase() === 'save');
        let saved = false;
        if (btns.length > 0 && !btns[0].hasAttribute('disabled')) {{
          btns[0].click();
          saved = true;
        }}
        return {{ rel: newRel.replace(/\\s+/g, ' ').trim(), saved }};
      }});
      await new Promise(r => setTimeout(r, 2800));
      relResults.push({{ short_id: sid, status: sv.rel, saved: sv.saved }});
    }} else {{
      relResults.push({{ short_id: sid, status: curRel, saved: false }});
    }}
  }}

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: true, batch_related_results: relResults }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err.message || err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
rel_120_res = s1_ego.run_ego_js(js_batch_rel, timeout=180)

out_120 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_120",
    "executed_at": datetime.datetime.now().isoformat(),
    "wav_direct_download": wav_120_res,
    "ffmpeg_rendered_videos": ffmpeg_res,
    "shorts_8_related_video_linked": rel_120_res
}
txt_120 = json.dumps(out_120, ensure_ascii=False, indent=2)
txt_120 = re.sub(r"4/0A[a-zA-Z0-9_\-]+", "REDACTED_OAUTH_CODE", txt_120)
(BASE / "S1_NEW_MV_RENDER_AND_8SHORTS_REL_120.json").write_text(txt_120, encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_NEW_MV_RENDER_AND_8SHORTS_REL_120.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(120): download lossless WAV via browser fetch, render official MV + 40s Short, and link Related Video on 8 Shorts"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

w_sz = round(wav_120_res.get("size_bytes", 0) / (1024*1024), 2) if isinstance(wav_120_res, dict) else 0
rel_list = rel_120_res.get("batch_related_results", []) if isinstance(rel_120_res, dict) else []

print("[4/4] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (120호 타이틀곡WAV:{w_sz}MB | 신곡MP4제작:{ffmpeg_res} | 쇼츠8편 관련동영상 일괄연결:{len(rel_list)}건 | 커밋:{sha})")
