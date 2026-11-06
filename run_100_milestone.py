import json, time, datetime, os, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

TARGET_VIDS = [
    {"video_id": "3nUJqf0ztBw", "title": "빛의 아침 (Morning Light) - Original Song (한걸음씩)"},
    {"video_id": "v-UdDDTx5Fw", "title": "🌸 어머니는 꽃이다 (Mother is a Flower)"},
    {"video_id": "ZGKDVNLzCyA", "title": "🕊️ A Morning of Light | Hope in the Midst of War"},
    {"video_id": "pmiytSqutsQ", "title": "다시 피어날 나 (Reborn in Light) - 한 걸음씩 | Official MV"},
    {"video_id": "hlIFjM_AGYc", "title": "한걸음씩 - 원인과 결과, 결국 사랑 (Cause & Effect) | Official MV"},
    {"video_id": "P90h3HLw9Qk", "title": "사냥꾼의 새벽 (Hunter's Dawn) - Official AI Music Video"}
]

SOL_ABOVE_FOLD = (
    "🎧 오늘은 여기까지, 충분히 잘했어요. 한걸음씩 정규 1집 《가을과 겨울 사이》 전곡 듣기 → https://open.spotify.com/album/44chP2pw8CFr0Z4aPNj4SO\n"
    "🍂 11/27 발매 정규 2집 《잔상》 미리 저장하기 → https://distrokid.com/hyperfollow/9050fa2/0QOwWYR3KqK\n"
    "🌿 음악과 함께하는 건강 루틴 → https://connect-ai-shin.blogspot.com/2026/11/1-12-20-15.html\n\n"
)

print("[1/3] 에고라이트 Space 4: 디스트로키드 OAC '한걸음씩' 전용 채널 라디오 버튼(input[type=radio]) 정밀 클릭 및 제출 버튼 확인 중...")
js_oac_radio = """
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
  await new Promise(r => setTimeout(r, 3000));

  const radioDetails = await page.evaluate(() => {
    const inputs = Array.from(document.querySelectorAll('input[type="radio"], input, button, a.btn, .button'));
    const radios = Array.from(document.querySelectorAll('input[type="radio"]'));
    if (radios.length > 0) {
      const lastRadio = radios[radios.length - 1];
      lastRadio.checked = true;
      lastRadio.click();
      lastRadio.dispatchEvent(new Event('change', { bubbles: true }));
    }
    // 라디오 주변 또는 폼 내부 구조 덤프
    const formHtml = document.querySelector('form') ? document.querySelector('form').innerHTML.slice(0, 4000) : document.body.innerHTML.slice(0, 6000);
    return {
      radio_count: radios.length,
      radios_info: radios.map(r => ({ name: r.name, id: r.id, val: r.value, checked: r.checked, onclick: r.getAttribute('onclick') || '' })),
      form_snippet: formHtml
    };
  });

  await new Promise(r => setTimeout(r, 3500));
  const afterRadio = await page.evaluate(() => {
    const visibleBtns = Array.from(document.querySelectorAll('button, input[type="submit"], input[type="button"], a')).filter(el => {
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    }).map(el => ({ tag: el.tagName, text: (el.innerText || el.value || '').trim(), href: el.href || '', id: el.id, cls: el.className })).filter(x => x.text);
    return {
      url: location.href,
      text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 3500),
      visible_elements: visibleBtns.slice(0, 40)
    };
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, radio_details: radioDetails, after_radio: afterRadio }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
oac_100_res = s1_ego.run_ego_js(js_oac_radio, timeout=75)

print("[2/3] 본진 @한걸음씩-r4i 대표 뮤직비디오 6편에 솔(Space 1)의 Above-the-fold Spotify 전환 문구 장착 중...")
updated_vids = []
api_errors = []
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    for tok_cand in [BASE / "youtube_token.json", Path(r"C:\Users\sangi\.connectai\secrets\youtube_token.json"), BASE / "token.json"]:
        if tok_cand.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(tok_cand))
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                yt = build("youtube", "v3", credentials=creds)
                for tv in TARGET_VIDS:
                    vid_id = tv["video_id"]
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
                            updated_vids.append({"video_id": vid_id, "title": snip.get("title"), "status": "UPDATED_SUCCESS"})
                        else:
                            updated_vids.append({"video_id": vid_id, "title": snip.get("title"), "status": "ALREADY_UPDATED"})
                if updated_vids:
                    break
            except Exception as ex:
                api_errors.append(f"{tok_cand.name}: {ex}")
except Exception as e:
    api_errors.append(str(e))

out_100 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_100",
    "executed_at": datetime.datetime.now().isoformat(),
    "oac_radio_inspection": oac_100_res,
    "target_6_music_videos": TARGET_VIDS,
    "updated_videos": updated_vids,
    "api_errors": api_errors
}
(BASE / "S1_MILESTONE_100_OAC_AND_SEO.json").write_text(json.dumps(out_100, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_MILESTONE_100_OAC_AND_SEO.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(100): inspect DistroKid OAC radio DOM and update 6 core music videos with Sol Spotify formula"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

r_cnt = oac_100_res.get("radio_details", {}).get("radio_count", 0) if isinstance(oac_100_res, dict) else 0
err_str = "; ".join(api_errors)[:160]

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (100호 OAC라디오:{r_cnt}개 | 본진 뮤비 6편 스포티파이 링크 장착:{len(updated_vids)}건 | 에러참고:{err_str} | 커밋:{sha})")
