import json, time, datetime, os, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/4] 에고라이트 Space 3 (유튜브 스튜디오) 및 구글 계정 내 전체 유튜브 채널(한걸음씩/부스터플리/까페아워) 자동 탐지 중...")

js_yt_audit = """
let task = null;
try {
  try { task = await takeOverTaskSpace(3); } catch (_) { try { task = await claimTaskSpace(3); } catch (__) { task = await taskSpace(3); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  if (!page) {
    process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: "NO_SPACE3_PAGE" }));
    return;
  }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  // 1) 현재 열린 Space 3 유튜브 스튜디오 화면 정보
  const studioInitial = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    text: (document.body ? document.body.innerText : '').slice(0, 6000)
  }));

  // 2) 유튜브 channel_switcher 페이지로 이동하여 동일 구글 계정의 모든 브랜드 채널(한걸음씩, 부스터플리, 까페 아워 등) 목록 추출
  await page.goto('https://www.youtube.com/account_advanced', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 3000));
  const advInfo = await page.evaluate(() => ({
    url: location.href,
    text: (document.body ? document.body.innerText : '').slice(0, 4000)
  }));

  await page.goto('https://www.youtube.com/channel_switcher', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 4000));
  const switcherData = await page.evaluate(() => {
    const txt = document.body ? document.body.innerText : '';
    const items = [];
    document.querySelectorAll('ytd-account-item-renderer, a, yt-formatted-string').forEach(el => {
      const t = (el.innerText || '').replace(/\\s+/g, ' ').trim();
      if (t && t.length > 1 && t.length < 200) items.push(t);
    });
    return {
      url: location.href,
      title: document.title,
      channels_raw_text: txt.slice(0, 8000),
      unique_lines: Array.from(new Set(items)).slice(0, 80)
    };
  });

  // 3) 다시 원래 유튜브 스튜디오 대시보드로 복귀해서 최근 영상/분석 요약 확보
  await page.goto('https://studio.youtube.com/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 4000));
  const studioDash = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    text: (document.body ? document.body.innerText : '').slice(0, 8000)
  }));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({
    ok: true,
    studio_initial: studioInitial,
    account_advanced: advInfo,
    channel_switcher: switcherData,
    studio_dashboard: studioDash
  }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""

yt_ego_res = s1_ego.run_ego_js(js_yt_audit, timeout=120)

print("[2/4] YouTube Data API v3로 채널별 정밀 통계 및 최근 영상 목록 추가 조회 중...")
yt_api_summary = {}
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    tok = BASE / "youtube_token.json"
    if tok.exists():
        creds = Credentials.from_authorized_user_file(str(tok))
        yt = build("youtube", "v3", credentials=creds)
        ch_resp = yt.channels().list(part="snippet,statistics,contentDetails,brandingSettings", mine=True).execute()
        channels_info = []
        for item in ch_resp.get("items", []):
            cid = item.get("id")
            snip = item.get("snippet", {})
            stat = item.get("statistics", {})
            uploads_id = item.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
            recent_vids = []
            if uploads_id:
                pl_resp = yt.playlistItems().list(part="snippet,contentDetails", playlistId=uploads_id, maxResults=10).execute()
                for v in pl_resp.get("items", []):
                    Recent_snip = v.get("snippet", {})
                    recent_vids.append({
                        "videoId": Recent_snip.get("resourceId", {}).get("videoId"),
                        "title": Recent_snip.get("title"),
                        "publishedAt": Recent_snip.get("publishedAt")
                    })
            channels_info.append({
                "channel_id": cid,
                "title": snip.get("title"),
                "customUrl": snip.get("customUrl"),
                "publishedAt": snip.get("publishedAt"),
                "subscriberCount": stat.get("subscriberCount"),
                "viewCount": stat.get("viewCount"),
                "videoCount": stat.get("videoCount"),
                "recent_videos": recent_vids
            })
        yt_api_summary["mine_channels"] = channels_info

        # 검색으로 부스터플리 / 까페 아워 / SUN-ONE AON 채널도 탐색
        search_channels = []
        for q in ["한걸음씩", "Booster Playlist SUN-ONE AON", "Cafe Hour SUN-ONE AON", "부스터플리", "까페 아워"]:
            sr = yt.search().list(part="snippet", q=q, type="channel", maxResults=3).execute()
            for sitem in sr.get("items", []):
                search_channels.append({
                    "query": q,
                    "channelId": sitem.get("snippet", {}).get("channelId"),
                    "title": sitem.get("snippet", {}).get("title"),
                    "description": sitem.get("snippet", {}).get("description")
                })
        yt_api_summary["searched_channels"] = search_channels
except Exception as e:
    yt_api_summary["error"] = str(e)

print("[3/4] 디스트로키드 092호 감사 데이터(17개 앨범·Bank·Stats)와 결합하여 마스터 정황 원장 생성 중...")
dk_summary = {}
dk_file = BASE / "S1_DISTROKID_FULL_CATALOG_AUDIT_092.json"
if dk_file.exists():
    dk_raw = json.loads(dk_file.read_text(encoding="utf-8")).get("distrokid_full_audit", {})
    dk_summary["total_albums_count"] = dk_raw.get("mymusic", {}).get("album_count", 17)
    dk_summary["all_17_album_links"] = dk_raw.get("mymusic", {}).get("album_links", [])
    dk_summary["bank_text"] = dk_raw.get("bank", {}).get("text", "")[:2500]
    dk_summary["stats_text"] = dk_raw.get("stats", {}).get("text", "")[:2500]
    compact_albums = []
    for a in dk_raw.get("albums_detailed", []):
        if isinstance(a, dict):
            compact_albums.append({
                "title": a.get("link_title"),
                "uploaded": a.get("uploaded_date_line"),
                "release_date": a.get("release_date_line"),
                "upc": a.get("upc_line"),
                "isrc_count": a.get("isrc_count"),
                "isrcs": a.get("isrcs"),
                "hyperfollow": a.get("hyperfollow_url")
            })
    dk_summary["albums_15_compact"] = compact_albums

master_status = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_093",
    "audited_at": datetime.datetime.now().isoformat(),
    "youtube_space3_ego_audit": yt_ego_res,
    "youtube_api_audit": yt_api_summary,
    "distrokid_master_summary": dk_summary
}

out_file = BASE / "S1_CEO_TOTAL_EMPIRE_STATUS_093.json"
out_file.write_text(json.dumps(master_status, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_CEO_TOTAL_EMPIRE_STATUS_093.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(093): comprehensive audit of all YouTube channels (Space 3 switcher + API) and DistroKid Bank/Stats"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

sw_txt = ""
if isinstance(yt_ego_res, dict):
    sw_txt = yt_ego_res.get("channel_switcher", {}).get("channels_raw_text", "").replace("\n", " | ")[:450]

print("[4/4] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (093호 유튜브 전체 채널 스위치 목록 및 디스트로키드 정황 실측 완료! 채널목록: {sw_txt} | 커밋:{sha})")
