import json, time, datetime, os, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/3] 에고라이트 Space 3: youtube.com/channel_switcher 에서 '한걸음씩(@한걸음씩-r4i)' 실제 클릭 전환 후 YouTube Studio 진입 중...")
js_switch_to_hangeoreum = """
let task = null;
try {
  try { task = await takeOverTaskSpace(3); } catch (_) { try { task = await claimTaskSpace(3); } catch (__) { task = await taskSpace(3); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  await page.goto('https://www.youtube.com/channel_switcher', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 4000));

  const switchClick = await page.evaluate(() => {
    const items = Array.from(document.querySelectorAll('ytd-account-item-renderer, tp-yt-paper-icon-item, a'));
    const target = items.find(el => {
      const t = (el.innerText || '').replace(/\\s+/g, ' ').trim();
      return t.includes('한걸음씩') && t.includes('33');
    });
    if (target) {
      const link = target.querySelector('a') || target.closest('a') || target;
      link.click();
      return { clicked: true, text: (target.innerText || '').replace(/\\s+/g, ' ').trim(), href: link.href || '' };
    }
    return { clicked: false };
  });

  await new Promise(r => setTimeout(r, 5000));
  await page.goto('https://studio.youtube.com/', { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 5000));

  const studioNow = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 2500)
  }));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, switch_click: switchClick, studio_now: studioNow }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
sw_105_res = s1_ego.run_ego_js(js_switch_to_hangeoreum, timeout=75)

print("[2/3] 에고라이트 Space 4: 디스트로키드 내부 API(/api/checkYTArtistChannel/)로 '한걸음씩' OAC 신청 상태 직접 조회 중...")
js_dk_check_api = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  const apiCheck = await page.evaluate(async () => {
    const r1 = await fetch('/api/checkYTArtistChannel/?artistName=' + encodeURIComponent('한걸음씩'), { credentials: 'include' }).then(r => r.text()).catch(e => String(e));
    const r2 = await fetch('/api/checkYTArtistChannel/?artistName=' + encodeURIComponent('SUN-ONE AON'), { credentials: 'include' }).then(r => r.text()).catch(e => String(e));
    return { hangeoreumsshik: r1, sun_one_aon: r2 };
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, api_check: apiCheck }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
dk_api_105 = s1_ego.run_ego_js(js_dk_check_api, timeout=45)

out_105 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_105",
    "executed_at": datetime.datetime.now().isoformat(),
    "space3_channel_switch_and_studio": sw_105_res,
    "space4_distrokid_oac_api_check": dk_api_105
}
(BASE / "S1_SWITCH_HANGEOREUM_AND_OAC_API_105.json").write_text(json.dumps(out_105, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_SWITCH_HANGEOREUM_AND_OAC_API_105.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(105): switch YouTube session to Hangeoreumsshik and query DistroKid checkYTArtistChannel API"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

st_url = sw_105_res.get("studio_now", {}).get("url", "") if isinstance(sw_105_res, dict) else ""
st_txt = sw_105_res.get("studio_now", {}).get("text", "")[:220] if isinstance(sw_105_res, dict) else ""
dk_chk = dk_api_105.get("api_check", {}) if isinstance(dk_api_105, dict) else {}

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (105호 @한걸음씩 채널스위치후 스튜디오URL:{st_url} [{st_txt}] | 디스트로키드OAC_API:{dk_chk} | 커밋:{sha})")
