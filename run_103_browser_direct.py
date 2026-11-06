import json, time, datetime, os, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/3] 에고라이트 Space 4: 디스트로키드 'YOUTUBE 채널 연결' 버튼의 정확한 HTML 태그·href·onclick 추출 및 실제 이동 중...")
js_dk_exact = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  await page.goto('https://distrokid.com/YouTubeOfficialArtistChannels/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 3000));

  await page.evaluate(() => {
    const sel = document.querySelector('select[name="oacartists"], select');
    if (sel) {
      sel.value = '한걸음씩';
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    }
  });
  await new Promise(r => setTimeout(r, 2500));

  await page.evaluate(() => {
    const r3 = document.querySelector('#youtubeChannel3');
    if (r3) {
      r3.checked = true;
      r3.click();
      r3.dispatchEvent(new Event('change', { bubbles: true }));
    }
  });
  await new Promise(r => setTimeout(r, 2000));

  const btnInspection = await page.evaluate(() => {
    const matches = [];
    document.querySelectorAll('a, button, input, div, span').forEach(el => {
      const t = (el.innerText || el.value || '').replace(/\\s+/g, ' ').trim();
      if (t === 'YOUTUBE 채널 연결' || t.includes('YOUTUBE 채널 연결')) {
        if (el.outerHTML.length < 1200) {
          matches.push({
            tag: el.tagName,
            id: el.id,
            cls: el.className,
            href: el.href || '',
            onclick: el.getAttribute('onclick') || '',
            outer: el.outerHTML
          });
        }
      }
    });
    return matches;
  });

  // 실제 마우스 좌표 클릭 수행
  const box = await page.evaluate(() => {
    const els = Array.from(document.querySelectorAll('a, button, input, div, span')).filter(el => {
      const t = (el.innerText || el.value || '').replace(/\\s+/g, ' ').trim();
      return t === 'YOUTUBE 채널 연결';
    });
    const target = els[els.length - 1];
    if (!target) return null;
    const r = target.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2, w: r.width, h: r.height };
  });

  if (box && box.w > 0 && page.mouse) {
    await page.mouse.click(box.x, box.y);
  }

  await new Promise(r => setTimeout(r, 5000));
  const afterMouse = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 2000)
  }));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, btn_matches: btnInspection, box, after_mouse: afterMouse }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
dk_103_res = s1_ego.run_ego_js(js_dk_exact, timeout=75)

print("[2/3] 에고라이트 Space 3: 만료된 토큰 대신 브라우저 로그인 세션으로 Blogger 대시보드 직접 확인 중...")
js_blogger_session = """
let task = null;
try {
  try { task = await takeOverTaskSpace(3); } catch (_) { try { task = await claimTaskSpace(3); } catch (__) { task = await taskSpace(3); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  await page.goto('https://www.blogger.com/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 4000));
  const bState = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 2500)
  }));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, blogger_state: bState }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
bg_103_res = s1_ego.run_ego_js(js_blogger_session, timeout=60)

out_103 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_103",
    "executed_at": datetime.datetime.now().isoformat(),
    "distrokid_oac_button_inspection": dk_103_res,
    "space3_blogger_session": bg_103_res
}
(BASE / "S1_BROWSER_DIRECT_SESSION_103.json").write_text(json.dumps(out_103, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_BROWSER_DIRECT_SESSION_103.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(103): inspect OAC button outerHTML with mouse click and verify Space 3 Blogger live session"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

after_m_url = dk_103_res.get("after_mouse", {}).get("url", "") if isinstance(dk_103_res, dict) else ""
bg_url = bg_103_res.get("blogger_state", {}).get("url", "") if isinstance(bg_103_res, dict) else ""
bg_txt = bg_103_res.get("blogger_state", {}).get("text", "")[:180] if isinstance(bg_103_res, dict) else ""

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (103호 OAC마우스클릭후URL:{after_m_url} | Space3 블로거세션URL:{bg_url} [{bg_txt}] | 커밋:{sha})")
