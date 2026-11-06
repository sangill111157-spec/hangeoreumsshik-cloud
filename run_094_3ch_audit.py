import json, time, datetime, os, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/3] 에고라이트 Space 3: 3대 핵심 유튜브 채널(@한걸음씩-r4i / @Booster_Playlist / @TheCaféHour) 전수 스캔 중...")

js_3ch_audit = """
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

  const targets = [
    { key: "hangeoreumsshik", name: "한걸음씩", handle: "@한걸음씩-r4i", url: "https://www.youtube.com/@%ED%95%9C%EA%B1%B8%EC%9D%8C%EC%94%A9-r4i" },
    { key: "booster_playlist", name: "부스터 플리 | 운동·드라이브 음악", handle: "@Booster_Playlist", url: "https://www.youtube.com/@Booster_Playlist" },
    { key: "the_cafe_hour", name: "The Café Hour", handle: "@TheCaféHour", url: "https://www.youtube.com/@TheCaf%C3%A9Hour" }
  ];

  const results = {};

  for (const ch of targets) {
    const chData = { name: ch.name, handle: ch.handle };

    // 1) /videos 탭 스캔
    await page.goto(ch.url + '/videos', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
    await new Promise(r => setTimeout(r, 4000));
    chData.videos_tab = await page.evaluate(() => {
      const channelIdMatch = (document.body.innerHTML || '').match(/"externalId":"(UC[a-zA-Z0-9_-]{22})"/);
      const cid = channelIdMatch ? channelIdMatch[1] : '';
      const headerTxt = (document.querySelector('#page-header, ytd-tabbed-page-header') || {}).innerText || '';
      const vids = [];
      document.querySelectorAll('ytd-rich-item-renderer, ytd-grid-video-renderer').forEach(el => {
        const titleEl = el.querySelector('#video-title, #video-title-link');
        const metaEl = el.querySelector('#metadata-line');
        const timeEl = el.querySelector('ytd-thumbnail-overlay-time-status-renderer');
        const href = titleEl && titleEl.href ? titleEl.href : (el.querySelector('a#thumbnail') ? el.querySelector('a#thumbnail').href : '');
        const title = titleEl ? (titleEl.innerText || '').trim() : '';
        const meta = metaEl ? (metaEl.innerText || '').replace(/\\s+/g, ' ').trim() : '';
        const duration = timeEl ? (timeEl.innerText || '').trim() : '';
        if (title) vids.push({ title, meta, duration, href });
      });
      const bodyPreview = (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 4000);
      return { channel_id: cid, header: headerTxt.replace(/\\s+/g, ' ').trim(), video_count_detected: vids.length, videos: vids.slice(0, 30), body_preview: bodyPreview };
    });

    // 2) /shorts 탭 스캔
    await page.goto(ch.url + '/shorts', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
    await new Promise(r => setTimeout(r, 3500));
    chData.shorts_tab = await page.evaluate(() => {
      const shorts = [];
      document.querySelectorAll('ytd-rich-item-renderer, ytm-shorts-lockup-view-model, ytd-reel-item-renderer').forEach(el => {
        const txt = (el.innerText || '').replace(/\\s+/g, ' ').trim();
        const a = el.querySelector('a[href*="/shorts/"]');
        if (txt && a) shorts.push({ text: txt.slice(0, 200), href: a.href });
      });
      const bodyPreview = (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 3000);
      return { shorts_count_detected: shorts.length, shorts: shorts.slice(0, 30), body_preview: bodyPreview };
    });

    // 3) /releases (또는 홈 탭) 스캔
    await page.goto(ch.url, { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
    await new Promise(r => setTimeout(r, 3000));
    chData.home_tab = await page.evaluate(() => {
      return { body_preview: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 3500) };
    });

    results[ch.key] = chData;
  }

  // 마지막으로 1번 본진 채널(@한걸음씩-r4i) 화면을 띄워둠
  await page.goto('https://www.youtube.com/@%ED%95%9C%EA%B1%B8%EC%9D%8C%EC%94%A9-r4i/videos', { waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {});

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, channels: results }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""

res = s1_ego.run_ego_js(js_3ch_audit, timeout=180)

out = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_094",
    "audited_at": datetime.datetime.now().isoformat(),
    "three_channels_audit": res
}
out_path = BASE / "S1_YOUTUBE_3CHANNELS_FULL_AUDIT_094.json"
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

# 요약 생성
chs = res.get("channels", {}) if isinstance(res, dict) else {}
sum_list = []
for k, v in chs.items():
    if isinstance(v, dict):
        vt = v.get("videos_tab", {})
        st = v.get("shorts_tab", {})
        cid = vt.get("channel_id", "")
        vc = vt.get("video_count_detected", 0)
        sc = st.get("shorts_count_detected", 0)
        hdr = vt.get("header", "")[:80]
        top_v = vt.get("videos", [{}])[0].get("title", "없음") if vt.get("videos") else "없음"
        sum_list.append(f"[{v.get('name')} ({cid})] 헤더:{hdr} | 롱폼:{vc}개(최신:{top_v[:25]}) | 쇼츠:{sc}개")
sum_txt = " || ".join(sum_list)

print("[2/3] GitHub 원격 저장소에 3대 채널 전수조사 원장(094호) 강제 푸시 중...")
subprocess.run(["git", "add", "-f", "S1_YOUTUBE_3CHANNELS_FULL_AUDIT_094.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(094): full audit of 3 core YouTube channels (videos, shorts, views, channel IDs)"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (094호 3대 유튜브 채널 전수조사 완료! {sum_txt[:550]} | 커밋:{sha})")
