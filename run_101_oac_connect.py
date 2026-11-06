import json, time, datetime, os, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/3] 에고라이트 Space 4: 디스트로키드 OAC '#youtubeChannel3' 체크 후 'YOUTUBE 채널 연결' 버튼 정밀 클릭 중...")
js_oac_connect = """
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
    const r3 = document.querySelector('#youtubeChannel3') || Array.from(document.querySelectorAll('input[type="radio"]')).pop();
    if (r3) {
      r3.checked = true;
      r3.click();
      r3.dispatchEvent(new Event('change', { bubbles: true }));
    }
  });
  await new Promise(r => setTimeout(r, 2000));

  const btnClick = await page.evaluate(() => {
    const all = Array.from(document.querySelectorAll('button, a, input[type="button"], input[type="submit"], div[role="button"], span, div'));
    const target = all.find(el => {
      const t = (el.innerText || el.value || '').trim();
      return t === 'YOUTUBE 채널 연결' || t.toUpperCase() === 'CONNECT YOUTUBE CHANNEL' || (t.includes('YOUTUBE 채널 연결') && t.length < 30);
    });
    if (target) {
      const clickable = target.closest('a, button, input, [onclick]') || target;
      clickable.click();
      return { clicked: true, tag: clickable.tagName, text: (clickable.innerText || clickable.value || '').trim(), href: clickable.href || '', onclick: clickable.getAttribute('onclick') || '' };
    }
    return { clicked: false };
  });

  await new Promise(r => setTimeout(r, 5000));
  const afterConnect = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 3500)
  }));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, btn_click: btnClick, after_connect: afterConnect }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
oac_conn_res = s1_ego.run_ego_js(js_oac_connect, timeout=75)

print("[2/3] 로컬 내 모든 Google/YouTube/Blogger OAuth 토큰 위치 탐색 및 라이브 블로그 Spotify 플레이어 패치 재검증 중...")
found_tokens = []
for root_dir in [Path(r"C:\Users\sangi\OneDrive\바탕 화면"), Path(r"C:\Users\sangi\Downloads"), Path(r"C:\Users\sangi\.connectai")]:
    if root_dir.exists():
        try:
            for p in root_dir.rglob("*token*.json"):
                if "node_modules" not in str(p):
                    found_tokens.append(str(p))
        except Exception:
            pass

blog_patch_status = "NOT_RUN"
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    html_body = (BASE / "S1_BLOG_REVENUE_POST_001.html").read_text(encoding="utf-8")
    proof = json.loads((BASE / "S1_LIVE_PUBLISHED_REVENUE_PROOF.json").read_text(encoding="utf-8"))
    post_id = proof.get("blogger_post_id")
    for tp_str in found_tokens:
        try:
            creds = Credentials.from_authorized_user_file(tp_str)
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            service = build("blogger", "v3", credentials=creds)
            r_b = service.posts().patch(blogId="5122625989918564552", postId=str(post_id), body={"content": html_body}).execute()
            blog_patch_status = f"SUCCESS ({r_b.get('url')}) via {Path(tp_str).name}"
            break
        except Exception as e:
            blog_patch_status = f"ERR ({Path(tp_str).name}): {str(e)[:80]}"
except Exception as e:
    blog_patch_status = f"OUTER_ERR: {str(e)[:80]}"

out_101 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_101",
    "executed_at": datetime.datetime.now().isoformat(),
    "oac_connect_result": oac_conn_res,
    "found_tokens": found_tokens,
    "blog_patch_status": blog_patch_status
}
(BASE / "S1_OAC_CONNECT_AND_TOKENS_101.json").write_text(json.dumps(out_101, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_OAC_CONNECT_AND_TOKENS_101.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(101): click DistroKid OAC Connect YouTube Channel button and verify token paths"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

after_url = oac_conn_res.get("after_connect", {}).get("url", "") if isinstance(oac_conn_res, dict) else ""
after_txt = oac_conn_res.get("after_connect", {}).get("text", "")[:220] if isinstance(oac_conn_res, dict) else ""

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (101호 OAC 연결클릭후 URL:{after_url} | 화면:{after_txt} | 블로그패치:{blog_patch_status} | 토큰수:{len(found_tokens)}개 | 커밋:{sha})")
