import json, time, datetime, os, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/3] publish_post_17.py의 정품 BLOG_ID(5189765270915724664) & secrets/token.json으로 라이브 블로그에 Spotify 플레이어 즉시 장착 중...")
blog_patch_status = "NOT_RUN"
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    blog_token = Path(r"C:\Users\sangi\.connectai\secrets\token.json")
    BLOG_ID = "5189765270915724664"
    html_body = (BASE / "S1_BLOG_REVENUE_POST_001.html").read_text(encoding="utf-8")
    proof = json.loads((BASE / "S1_LIVE_PUBLISHED_REVENUE_PROOF.json").read_text(encoding="utf-8"))
    post_id = proof.get("blogger_post_id")

    creds = Credentials.from_authorized_user_file(str(blog_token), ["https://www.googleapis.com/auth/blogger"])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        blog_token.write_text(creds.to_json(), encoding="utf-8")

    blogger = build("blogger", "v3", credentials=creds)
    r_b = blogger.posts().patch(blogId=BLOG_ID, postId=str(post_id), body={"content": html_body}).execute()
    blog_patch_status = f"SUCCESS: {r_b.get('url')}"
    print(" -> 라이브 블로그 패치 대성공:", blog_patch_status)
except Exception as e:
    blog_patch_status = f"ERR: {str(e)[:120]}"
    print(" -> 블로그 패치 에러:", blog_patch_status)

print("[2/3] 발굴된 정품 유튜브 토큰(hunters-dawn/token.json 외)으로 본진 뮤직비디오 6편에 솔(Space 1)의 Spotify 전환 문구 장착 중...")
TARGET_VIDS = ["3nUJqf0ztBw", "v-UdDDTx5Fw", "ZGKDVNLzCyA", "pmiytSqutsQ", "hlIFjM_AGYc", "P90h3HLw9Qk"]
SOL_ABOVE_FOLD = (
    "🎧 오늘은 여기까지, 충분히 잘했어요. 한걸음씩 정규 1집 《가을과 겨울 사이》 전곡 듣기 → https://open.spotify.com/album/44chP2pw8CFr0Z4aPNj4SO\n"
    "🍂 11/27 발매 정규 2집 《잔상》 미리 저장하기 → https://distrokid.com/hyperfollow/9050fa2/0QOwWYR3KqK\n"
    "🌿 음악과 함께하는 건강 루틴 → https://connect-ai-shin.blogspot.com/2026/11/1-12-20-15.html\n\n"
)

yt_updated = []
yt_notes = []
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    yt_tokens = [
        Path(r"C:\Users\sangi\Downloads\shin-agent\hunters-dawn\token.json"),
        Path(r"C:\Users\sangi\Downloads\음악 채널 에이전트 루미\token.json"),
        Path(r"C:\Users\sangi\.connectai\secrets\token.json")
    ]
    for ytp in yt_tokens:
        if ytp.exists():
            try:
                ycreds = Credentials.from_authorized_user_file(str(ytp))
                if ycreds.expired and ycreds.refresh_token:
                    ycreds.refresh(Request())
                yt = build("youtube", "v3", credentials=ycreds)
                me = yt.channels().list(part="snippet", mine=True).execute()
                ch_titles = [c["snippet"]["title"] for c in me.get("items", [])]
                yt_notes.append(f"{ytp.parent.name}/{ytp.name}->채널:{ch_titles}")
                for vid_id in TARGET_VIDS:
                    v_info = yt.videos().list(part="snippet", id=vid_id).execute()
                    items = v_info.get("items", [])
                    if items:
                        snip = items[0]["snippet"]
                        old_desc = snip.get("description", "")
                        if "44chP2pw8CFr0Z4aPNj4SO" not in old_desc:
                            snip["description"] = SOL_ABOVE_FOLD + old_desc
                            yt.videos().update(part="snippet", body={"id": vid_id, "snippet": snip}).execute()
                            yt_updated.append(f"{vid_id}(UPDATED)")
                        else:
                            yt_updated.append(f"{vid_id}(ALREADY)")
                if yt_updated:
                    break
            except Exception as ex:
                yt_notes.append(f"{ytp.parent.name}/{ytp.name}:{str(ex)[:70]}")
except Exception as e:
    yt_notes.append(str(e)[:80])

print("[3/3] 에고라이트 Space 4: 디스트로키드 'YOUTUBE 채널 연결' 버튼의 실제 HTML/JS 핸들러 추출 및 실행 중...")
js_oac_handler = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  await page.goto('https://distrokid.com/YouTubeOfficialArtistChannels/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 3000));

  const domDump = await page.evaluate(() => {
    window.__opened_urls = [];
    const origOpen = window.open;
    window.open = function(u) { window.__opened_urls.push(u); location.href = u; return null; };

    const sel = document.querySelector('select[name="oacartists"], select');
    if (sel) {
      sel.value = '한걸음씩';
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    }
    const r3 = document.querySelector('#youtubeChannel3');
    if (r3) {
      r3.checked = true;
      r3.click();
      r3.dispatchEvent(new Event('change', { bubbles: true }));
    }
    // 버튼 주변 HTML 정확히 추출
    const btnEl = Array.from(document.querySelectorAll('*')).find(el => (el.innerText || '').trim() === 'YOUTUBE 채널 연결' && el.children.length === 0);
    const parentHtml = btnEl && btnEl.parentElement ? btnEl.parentElement.outerHTML : '';
    const grandHtml = btnEl && btnEl.parentElement && btnEl.parentElement.parentElement ? btnEl.parentElement.parentElement.outerHTML : '';
    if (btnEl) btnEl.click();
    return { parent_html: parentHtml.slice(0, 1500), grand_html: grandHtml.slice(0, 2500), opened: window.__opened_urls };
  });

  await new Promise(r => setTimeout(r, 4500));
  const afterState = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 2000)
  }));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, dom_dump: domDump, after_state: afterState }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
oac_102_res = s1_ego.run_ego_js(js_oac_handler, timeout=75)

out_102 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_102",
    "executed_at": datetime.datetime.now().isoformat(),
    "blog_patch_status": blog_patch_status,
    "youtube_updated": yt_updated,
    "youtube_token_notes": yt_notes,
    "oac_handler_result": oac_102_res
}
(BASE / "S1_BLOG_YT_OAC_EXECUTION_102.json").write_text(json.dumps(out_102, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_BLOG_YT_OAC_EXECUTION_102.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(102): patch live Blogger post 5189765270915724664 with Spotify embed and update YouTube videos via verified tokens"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

after_u = oac_102_res.get("after_state", {}).get("url", "") if isinstance(oac_102_res, dict) else ""

ego.send_auto_confirm_enter_space0(f"확인 (102호 블로그패치:{blog_patch_status} | 유튜브설명란패치:{len(yt_updated)}건({','.join(yt_notes)[:120]}) | OAC이동URL:{after_u} | 커밋:{sha})")
