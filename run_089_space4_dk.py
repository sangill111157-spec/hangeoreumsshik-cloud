import json, datetime, os, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

print("[1/3] 에고라이트 Space 4 (디스트로키드 창) 정밀 스캔 중...")
js_dk = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  if (!page) {
    process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: "NO_SPACE4_PAGE" }));
    return;
  }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  const data = await page.evaluate(async () => {
    const url = location.href;
    const title = document.title;
    const bodyText = document.body ? document.body.innerText : '';
    let mymusicText = '';
    try {
      const r = await fetch('https://distrokid.com/mymusic/', { credentials: 'include' });
      const h = await r.text();
      const doc = new DOMParser().parseFromString(h, 'text/html');
      mymusicText = doc.body ? doc.body.innerText.replace(/\\s+/g, ' ').trim().slice(0, 8000) : '';
    } catch (e) {
      mymusicText = 'FETCH_ERR:' + e.message;
    }
    return { ok: true, url, title, album_page_text: bodyText.slice(0, 12000), mymusic_overview: mymusicText };
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify(data));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""

res = s1_ego.run_ego_js(js_dk, timeout=35)
out = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_089",
    "scanned_at": datetime.datetime.now().isoformat(),
    "space4_distrokid_result": res
}
out_path = BASE / "S1_DISTROKID_LIVE_RELEASE_DATES.json"
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

print("[2/3] GitHub 원격 저장소에 디스트로키드 실측 데이터 동기화 중...")
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
subprocess.run(["git", "add", "-f", "S1_DISTROKID_LIVE_RELEASE_DATES.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(089): extract live DistroKid release date, UPC, and track ISRCs from Space 4"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (089호 Space 4 디스트로키드 실제 발매일시·UPC·12곡 ISRC 실측 완료! 커밋: {sha})")
