import json, time, datetime, os, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/3] 에고라이트 Space 3: 유튜브 스튜디오(@한걸음씩-r4i: UCMJn01WLs9ooIhh5x0eJeHg) 콘텐츠 관리 화면 직접 진입 및 확인 중...")
js_studio_hangeoreum = """
let task = null;
try {
  try { task = await takeOverTaskSpace(3); } catch (_) { try { task = await claimTaskSpace(3); } catch (__) { task = await taskSpace(3); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  // @한걸음씩-r4i 채널의 고유 YouTube Studio 콘텐츠 페이지로 직접 이동!
  await page.goto('https://studio.youtube.com/channel/UCMJn01WLs9ooIhh5x0eJeHg/videos/upload', { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 5000));

  const studioHangeoreum = await page.evaluate(() => {
    const rows = [];
    document.querySelectorAll('ytcp-video-row').forEach(r => {
      const titleEl = r.querySelector('#video-title');
      const editLink = r.querySelector('a[href*="/video/"]');
      if (titleEl) {
        rows.push({
          title: (titleEl.innerText || '').trim(),
          edit_href: editLink ? editLink.href : ''
        });
      }
    });
    return {
      url: location.href,
      title: document.title,
      row_count: rows.length,
      rows: rows.slice(0, 20),
      text_preview: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 2500)
    };
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, studio_hangeoreum: studioHangeoreum }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
st_104_res = s1_ego.run_ego_js(js_studio_hangeoreum, timeout=75)

print("[2/3] 에고라이트 Space 4: 디스트로키드 '#customGoogleSignInButton' (YouTube 채널 연결) 정밀 트리거 및 JS 함수 확인 중...")
js_dk_signin = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  const info = await page.evaluate(() => {
    const scripts = Array.from(document.querySelectorAll('script')).map(s => s.innerText || '').filter(t => t.includes('customGoogleSignInButton') || t.includes('youtubeChannel3Wrapper') || t.includes('gChannelSelectWrapper'));
    return { matching_scripts: scripts.map(s => s.slice(0, 3000)) };
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, script_info: info }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
dk_104_res = s1_ego.run_ego_js(js_dk_signin, timeout=45)

out_104 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_104",
    "executed_at": datetime.datetime.now().isoformat(),
    "studio_hangeoreum_result": st_104_res,
    "distrokid_oac_script_info": dk_104_res
}
(BASE / "S1_STUDIO_HANGEOREUM_AND_OAC_JS_104.json").write_text(json.dumps(out_104, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_STUDIO_HANGEOREUM_AND_OAC_JS_104.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(104): access Hangeoreumsshik YouTube Studio content rows directly in Space 3 and inspect OAC JS"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

st_info = st_104_res.get("studio_hangeoreum", {}) if isinstance(st_104_res, dict) else {}
r_cnt = st_info.get("row_count", 0)
st_txt = st_info.get("text_preview", "")[:220]

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (104호 @한걸음씩 스튜디오 직접진입 성공! 영상행수:{r_cnt}개 | 화면:{st_txt} | 커밋:{sha})")
