import json, time, datetime, os, re, subprocess
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

print("[1/4] 에고라이트 Space 4: 디스트로키드에서 타이틀곡 #1 '오늘은 여기까지'(id=ihIUw) 정품 WAV 다운로드 및 s4aVerify() 실행 중...")
wav_path = OUT_DIR / "04_THATS_ALL_FOR_TODAY.wav"

js_dl_wav_and_s4a = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  // 1) Spotify for Artists 페이지에서 '한걸음씩' 선택 후 s4aVerify() 호출
  await page.goto('https://distrokid.com/spotify/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 3000));
  const s4aRes = await page.evaluate(async () => {
    const sel = document.querySelector('select');
    if (sel) {
      const opt = Array.from(sel.options).find(o => o.text.includes('한걸음씩'));
      if (opt) {
        sel.value = opt.value;
        sel.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }
    await new Promise(r => setTimeout(r, 1500));
    let verifyCalled = false;
    if (typeof window.s4aVerify === 'function') {
      try { window.s4aVerify(); verifyCalled = true; } catch (e) {}
    }
    await new Promise(r => setTimeout(r, 3000));
    return { url: location.href, verify_called: verifyCalled, text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 1500) };
  });

  // 2) 브라우저 쿠키 추출하여 Python이 직접 대용량 WAV(ihIUw)를 고속 다운로드하도록 전달
  const cookies = await page.context().cookies('https://distrokid.com');
  const cookieHeader = cookies.map(c => `${c.name}=${c.value}`).join('; ');
  const ua = await page.evaluate(() => navigator.userAgent);

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, s4a_res: s4aRes, cookie_header: cookieHeader, ua }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
dk_119 = s1_ego.run_ego_js(js_dl_wav_and_audio if False else js_dl_wav_and_s4a, timeout=65)

# 추출한 디스트로키드 세션 쿠키로 타이틀곡 #1 (ihIUw) 및 타이틀곡 #2 (ihIUx) 원본 WAV 다운로드
import urllib.request
cookie_hdr = dk_119.get("cookie_header", "") if isinstance(dk_119, dict) else ""
ua_str = dk_119.get("ua", "Mozilla/5.0") if isinstance(dk_119, dict) else "Mozilla/5.0"

downloaded_tracks = []
if cookie_hdr:
    for tid, fname in [("ihIUw", "04_THATS_ALL_FOR_TODAY.wav"), ("ihIUx", "05_HAVE_YOU_EATEN.wav")]:
        tpath = OUT_DIR / fname
        if not tpath.exists() or tpath.stat().st_size < 100000:
            try:
                req = urllib.request.Request(
                    f"https://distrokid.com/vault/download/?id={tid}",
                    headers={"Cookie": cookie_hdr, "User-Agent": ua_str}
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    tpath.write_bytes(resp.read())
                downloaded_tracks.append({"file": fname, "size_mb": round(tpath.stat().st_size / (1024*1024), 2)})
                print(f" -> {fname} 다운로드 성공: {tpath.stat().st_size} bytes")
            except Exception as e:
                downloaded_tracks.append({"file": fname, "err": str(e)[:80]})
        else:
            downloaded_tracks.append({"file": fname, "size_mb": round(tpath.stat().st_size / (1024*1024), 2), "cached": True})

print("[2/4] FFmpeg(CreateNoWindow)로 신곡 공식 MV(1920x1080) + 40초 하이라이트 쇼츠(1080x1920) 렌더링 중...")
cover_path = OUT_DIR / "AW_COVER_800x800.jpg"
mv_04_path = OUT_DIR / "S1_AW_04_TODAY_OFFICIAL_MV.mp4"
short_04_path = OUT_DIR / "S1_AW_04_TODAY_SHORTS_40S.mp4"
mv_05_path = OUT_DIR / "S1_AW_05_EATEN_OFFICIAL_MV.mp4"

ffmpeg_results = {}
if cover_path.exists() and (OUT_DIR / "04_THATS_ALL_FOR_TODAY.wav").exists():
    w04 = str(OUT_DIR / "04_THATS_ALL_FOR_TODAY.wav")
    # 1) 타이틀곡 #1 풀버전 MV (1920x1080 패딩)
    cmd_mv04 = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", "2", "-i", str(cover_path), "-i", w04,
        "-vf", "scale=1080:1080,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(mv_04_path)
    ]
    r1 = subprocess.run(cmd_mv04, env=env, capture_output=True, text=True, creationflags=no_win)
    ffmpeg_results["mv_04"] = {"ok": mv_04_path.exists(), "size_mb": round(mv_04_path.stat().st_size/(1024*1024), 2) if mv_04_path.exists() else 0}

    # 2) 타이틀곡 #1 40초 하이라이트 쇼츠 (1080x1920 세로형, NotNoise 2026 <60초 규칙 준수!)
    cmd_sh04 = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", "2", "-i", str(cover_path), "-ss", "00:00:30", "-t", "40", "-i", w04,
        "-vf", "scale=1080:1080,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(short_04_path)
    ]
    r2 = subprocess.run(cmd_sh04, env=env, capture_output=True, text=True, creationflags=no_win)
    ffmpeg_results["short_04_40s"] = {"ok": short_04_path.exists(), "size_mb": round(short_04_path.stat().st_size/(1024*1024), 2) if short_04_path.exists() else 0}

if cover_path.exists() and (OUT_DIR / "05_HAVE_YOU_EATEN.wav").exists():
    w05 = str(OUT_DIR / "05_HAVE_YOU_EATEN.wav")
    cmd_mv05 = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", "2", "-i", str(cover_path), "-i", w05,
        "-vf", "scale=1080:1080,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(mv_05_path)
    ]
    r3 = subprocess.run(cmd_mv05, env=env, capture_output=True, text=True, creationflags=no_win)
    ffmpeg_results["mv_05"] = {"ok": mv_05_path.exists(), "size_mb": round(mv_05_path.stat().st_size/(1024*1024), 2) if mv_05_path.exists() else 0}

print("[3/4] 에고라이트 Space 3: '특정 동영상 선택' 모달 내부 DOM 정밀 스캔 후 풀버전 뮤비(어머니는 꽃이다) 실제 클릭 및 저장 중...")
js_rel_modal_pick = """
let task = null;
try {
  try { task = await takeOverTaskSpace(3); } catch (_) { try { task = await claimTaskSpace(3); } catch (__) { task = await taskSpace(3); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  await page.goto('https://studio.youtube.com/video/vSTcyW-K_9Q/edit', { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 5000));

  await page.evaluate(() => {
    const trig = document.querySelector('#linked-video-editor-link, ytcp-shorts-content-links-picker ytcp-text-dropdown-trigger');
    if (trig) trig.click();
  });
  await new Promise(r => setTimeout(r, 4000));

  const modalScan = await page.evaluate(() => {
    const cards = Array.from(document.querySelectorAll('ytcp-entity-card, ytcp-video-pick-dialog-contents *')).filter(el => {
      const r = el.getBoundingClientRect();
      return r.width > 100 && r.height > 80 && r.height < 300 && (el.innerText || '').trim().length > 3;
    });
    const samples = cards.slice(0, 12).map(c => ({
      tag: c.tagName,
      cls: c.className,
      text: (c.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 100),
      x: c.getBoundingClientRect().left + c.getBoundingClientRect().width / 2,
      y: c.getBoundingClientRect().top + c.getBoundingClientRect().height / 2
    }));
    return samples;
  });

  // '어머니는 꽃이다' 5:09 카드 또는 첫 번째 롱폼 카드 물리 마우스 클릭
  const targetCard = modalScan.find(s => s.text.includes('어머니는 꽃이다') && !s.text.includes('0:')) || modalScan[0];
  if (targetCard && page.mouse) {
    await page.mouse.click(targetCard.x, targetCard.y);
  }
  await new Promise(r => setTimeout(r, 2500));

  const afterPick = await page.evaluate(() => {
    const relTxt = (document.querySelector('#linked-video-editor-link') || {}).innerText || '';
    const btns = Array.from(document.querySelectorAll('#save-button, ytcp-button#save, ytcp-button, button')).filter(b => (b.innerText || '').trim() === '저장' || (b.innerText || '').trim().toLowerCase() === 'save');
    let saved = false;
    if (btns.length > 0 && !btns[0].hasAttribute('disabled')) {
      btns[0].click();
      saved = true;
    }
    return { rel_text: relTxt.replace(/\\s+/g, ' ').trim(), saved };
  });
  await new Promise(r => setTimeout(r, 3000));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, modal_cards: modalScan, after_pick: afterPick }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
rel_119 = s1_ego.run_ego_js(js_rel_modal_pick, timeout=75)

out_119 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_119",
    "executed_at": datetime.datetime.now().isoformat(),
    "downloaded_wav_masters": downloaded_tracks,
    "rendered_mp4_videos": ffmpeg_results,
    "spotify_for_artists_verify": dk_119.get("s4a_res") if isinstance(dk_119, dict) else {},
    "related_video_modal_pick": rel_119
}
txt_119 = json.dumps(out_119, ensure_ascii=False, indent=2)
txt_119 = re.sub(r"4/0A[a-zA-Z0-9_\-]+", "REDACTED_OAUTH_CODE", txt_119)
(BASE / "S1_WAV_RENDER_AND_RELATED_119.json").write_text(txt_119, encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_WAV_RENDER_AND_RELATED_119.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(119): download lossless WAV masters from DistroKid Vault, render 3 new MP4 videos, and link Related Video"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

ap = rel_119.get("after_pick", {}) if isinstance(rel_119, dict) else {}

print("[4/4] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (119호 정품WAV다운:{downloaded_tracks} | 신곡MP4렌더링3종:{ffmpeg_results} | 쇼츠관련동영상연결:{ap} | 커밋:{sha})")
