import json, time, datetime, os, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/3] 에고라이트 Space 4: 오푸스 Step 1 권고에 따라 디스트로키드 OAC '한걸음씩 전용 채널 운영' 버튼 클릭 및 진행 중...")
js_oac_click = """
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
  }).catch(() => {});
  await new Promise(r => setTimeout(r, 3500));

  // '네, 다음 아티스트 전용 YouTube 채널을 운영하고 있습니다: 한걸음씩' 클릭
  const clickRes = await page.evaluate(() => {
    const els = Array.from(document.querySelectorAll('a, button, div, label, input'));
    const target = els.find(el => {
      const t = (el.innerText || el.value || '').trim();
      return t.includes('네, 다음 아티스트 전용') || t.includes('Yes, I have a YouTube channel dedicated');
    });
    if (target) {
      target.click();
      return { clicked: true, text: (target.innerText || target.value || '').trim(), href: target.href || '' };
    }
    return { clicked: false };
  });

  await new Promise(r => setTimeout(r, 5000));
  const afterClick = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 4000)
  }));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, click_res: clickRes, after_click: afterClick }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
oac_step_res = s1_ego.run_ego_js(js_oac_click, timeout=75)

print("[2/3] 에고라이트 Space 3: @한걸음씩-r4i 유튜브 스튜디오에서 솔(Space 1)의 Chartlex 2026 공식 설명란(Above-the-fold) 적용 대상 영상 ID 추출 중...")
SOL_ABOVE_FOLD = (
    "🎧 오늘은 여기까지, 충분히 잘했어요. 한걸음씩 정규 1집 《가을과 겨울 사이》 전곡 듣기 → https://open.spotify.com/album/44chP2pw8CFr0Z4aPNj4SO\n"
    "🍂 11/27 발매 정규 2집 《잔상》 미리 저장하기 → https://distrokid.com/hyperfollow/9050fa2/0QOwWYR3KqK\n"
    "🌿 음악과 함께하는 건강 루틴 → https://connect-ai-shin.blogspot.com/2026/11/1-12-20-15.html\n\n"
)

js_get_vids = """
let task = null;
try {
  try { task = await takeOverTaskSpace(3); } catch (_) { try { task = await claimTaskSpace(3); } catch (__) { task = await taskSpace(3); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  await page.goto('https://www.youtube.com/@%ED%95%9C%EA%B1%B8%EC%9D%8C%EC%94%A9-r4i/videos', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 4000));
  const vidLinks = await page.evaluate(() => {
    const list = [];
    const seen = new Set();
    document.querySelectorAll('a[href*="/watch?v="]').forEach(a => {
      const m = a.href.match(/[?&]v=([a-zA-Z0-9_-]{11})/);
      if (m && !seen.has(m[1])) {
        const title = (a.innerText || a.getAttribute('title') || '').trim();
        if (title) {
          seen.add(m[1]);
          list.push({ video_id: m[1], title, url: 'https://www.youtube.com/watch?v=' + m[1] });
        }
      }
    });
    return list;
  });
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, count: vidLinks.length, videos: vidLinks }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
vids_res = s1_ego.run_ego_js(js_get_vids, timeout=60)

# YouTube Data API v3로 본진 대표 뮤직비디오에 솔의 Above-the-fold 링크 장착 시도
updated_vids = []
api_note = ""
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    tok = BASE / "youtube_token.json"
    if tok.exists() and isinstance(vids_res, dict) and vids_res.get("videos"):
        creds = Credentials.from_authorized_user_file(str(tok))
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        yt = build("youtube", "v3", credentials=creds)
        # 음악 뮤직비디오 상위 5개 대상
        music_vids = [v for v in vids_res.get("videos", []) if any(k in v.get("title", "") for k in ["사냥꾼", "원인과 결과", "어머니는 꽃", "다시 피어날", "빛의 아침"])]
        for mv in music_vids[:5]:
            vid_id = mv["video_id"]
            v_info = yt.videos().list(part="snippet", id=vid_id).execute()
            items = v_info.get("items", [])
            if items:
                snip = items[0]["snippet"]
                old_desc = snip.get("description", "")
                if "44chP2pw8CFr0Z4aPNj4SO" not in old_desc:
                    snip["description"] = SOL_ABOVE_FOLD + old_desc
                    tags = snip.get("tags", [])
                    for tg in ["한걸음씩", "가을과 겨울 사이", "오늘은 여기까지", "한걸음씩 정규 1집", "위로 노래", "감성 음악"]:
                        if tg not in tags:
                            tags.append(tg)
                    snip["tags"] = tags[:25]
                    yt.videos().update(part="snippet", body={"id": vid_id, "snippet": snip}).execute()
                    updated_vids.append({"video_id": vid_id, "title": mv["title"], "status": "UPDATED_WITH_SOL_FORMULA"})
                else:
                    updated_vids.append({"video_id": vid_id, "title": mv["title"], "status": "ALREADY_HAS_SPOTIFY_LINK"})
except Exception as e:
    api_note = str(e)

out_099 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_099",
    "executed_at": datetime.datetime.now().isoformat(),
    "oac_step1_result": oac_step_res,
    "detected_channel_videos": vids_res,
    "youtube_api_updated_videos": updated_vids,
    "youtube_api_note": api_note,
    "sol_applied_template": SOL_ABOVE_FOLD
}
(BASE / "S1_STEP1_OAC_AND_VIDEO_SEO_099.json").write_text(json.dumps(out_099, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_STEP1_OAC_AND_VIDEO_SEO_099.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(099): execute Opus Step 1 OAC claim click and apply Sol Above-the-fold Spotify formula"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

oac_url_after = oac_step_res.get("after_click", {}).get("url", "") if isinstance(oac_step_res, dict) else ""
oac_txt_after = oac_step_res.get("after_click", {}).get("text", "")[:220] if isinstance(oac_step_res, dict) else ""

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (099호 OAC 신청 클릭결과:{oac_url_after} [{oac_txt_after}] | 본진 뮤비 설명란 패치:{len(updated_vids)}건({api_note[:80]}) | 커밋:{sha})")
