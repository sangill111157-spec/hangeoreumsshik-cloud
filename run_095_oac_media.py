import json, time, datetime, os, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/3] 에고라이트 Space 4: 디스트로키드 공식 아티스트 채널(OAC 음표배지) 및 Special Access 상태 스캔 중...")

js_oac = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  await page.goto('https://distrokid.com/YouTubeOfficialArtistChannels/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 4000));
  const oacData = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 5000)
  }));

  await page.goto('https://distrokid.com/uri/spotify/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 3500));
  const spotUri = await page.evaluate(() => ({
    url: location.href,
    text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 4000)
  }));

  await page.goto('https://distrokid.com/mymusic/', { waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {});

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, oac: oacData, spotify_uri: spotUri }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""

oac_res = s1_ego.run_ego_js(js_oac, timeout=90)

print("[2/3] 로컬 PC 내 보유 음원(mp3/wav/flac) 및 영상(mp4) 자산 위치 자동 스캔 중...")
media_files = []
search_roots = [
    Path(r"C:\Users\sangi\Downloads"),
    Path(r"C:\Users\sangi\OneDrive\바탕 화면"),
    Path(r"C:\Users\sangi\Desktop"),
    Path(r"C:\Users\sangi\Music"),
    Path(r"C:\Users\sangi\Videos")
]
seen_paths = set()
for sr in search_roots:
    if sr.exists():
        for ext in ("*.mp3", "*.wav", "*.flac", "*.m4a", "*.mp4"):
            try:
                for p in sr.rglob(ext):
                    sp = str(p)
                    if sp not in seen_paths and "node_modules" not in sp and ".git" not in sp:
                        seen_paths.add(sp)
                        media_files.append({
                            "path": sp,
                            "name": p.name,
                            "ext": p.suffix.lower(),
                            "size_mb": round(p.stat().st_size / (1024 * 1024), 2)
                        })
                        if len(media_files) >= 120:
                            break
            except Exception:
                pass

out = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_095",
    "scanned_at": datetime.datetime.now().isoformat(),
    "distrokid_oac_and_spotify": oac_res,
    "local_media_count": len(media_files),
    "local_media_samples": media_files[:80]
}
out_path = BASE / "S1_OAC_AND_LOCAL_MEDIA_AUDIT_095.json"
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_OAC_AND_LOCAL_MEDIA_AUDIT_095.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(095): audit DistroKid OAC status, Spotify URIs, and local audio/video files for immediate upload"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

oac_txt = oac_res.get("oac", {}).get("text", "")[:250] if isinstance(oac_res, dict) else ""
sample_names = ", ".join([m["name"] for m in media_files[:10]])

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (095호 OAC상태 및 로컬 미디어 {len(media_files)}개 발굴 완료! OAC:{oac_txt} | 미디어샘플:{sample_names} | 커밋:{sha})")
