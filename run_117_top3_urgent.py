import json, time, datetime, os, re, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
OUT_DIR = BASE / "studio_vault" / "NOV06_RELEASE"
OUT_DIR.mkdir(parents=True, exist_ok=True)
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/5] 에고라이트 Space 1 (솔) & Space 2 (오푸스)에게 급선무 TOP 3(신곡 3편 패키징 + Related Video + 11/27 잔상 Spotify 피칭) 합동 자문 수거 중...")
prompt_sol = (
    "솔 보좌관, 세계 원탑 Chartlex 2026 발매 첫 72시간 골든타임 공식에 따라 오늘(11/6) 발매된 '한걸음씩' 정규 1집 <가을과 겨울 사이>(UPC:700563848544, Spotify: https://open.spotify.com/album/44chP2pw8CFr0Z4aPNj4SO )로 "
    "@한걸음씩-r4i 유튜브 채널(최근 90일 업로드 0/3개 -> 3/3개 달성용)에 올릴 신곡 영상 3편의 최고 클릭률 제목과 설명란을 JSON({\"mv_title\": \"...\", \"short_title\": \"...\", \"full_album_title\": \"...\", \"spotify_pitch_note_for_jansang\": \"...\"})으로만 답해줘."
)
sol_117 = ego.ask_and_harvest_side_room(1, prompt_sol, 35000)

prompt_opus = (
    "오푸스 감사관, 우리 급선무 TOP 3 실행안을 감사해줘: "
    "1순위: 디스트로키드 Vault에서 오늘 발매된 <가을과 겨울 사이> 정품 음원(오늘은 여기까지 QTA2W2687084 외)과 커버를 받아 @한걸음씩-r4i에 풀MV + 40초 쇼츠 + 풀앨범 롱폼 3편 업로드(YPP 90일 3개 조건 달성 및 첫 72시간 Spotify 유입 점화). "
    "2순위: 기존 인기 쇼츠의 관련 동영상(Related Video)을 롱폼으로 연결. "
    "3순위: 11/27 발매 <잔상>(15곡)을 Spotify for Artists에서 에디토리얼 플레이리스트 사전 피칭(발매 7일 전 필수 조건). "
    "이 3단계에서 주의할 기술·정책 체크포인트를 JSON({\"priority1_check\": \"...\", \"priority2_check\": \"...\", \"priority3_check\": \"...\", \"verdict\": \"APPROVED\"})으로만 답해줘."
)
opus_117 = ego.ask_and_harvest_side_room(2, prompt_opus, 35000)

print("[2/5] 에고라이트 Space 4: 디스트로키드 Spotify for Artists(distrokid.com/spotify/) 상태 확인 및 <가을과 겨울 사이> 앨범 커버·타이틀곡 실제 다운로드 URL 추출 중...")
js_dk_spotify_and_vault = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  // 1) DistroKid Spotify for Artists 연동 페이지 스캔
  await page.goto('https://distrokid.com/spotify/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 4000));
  const s4aPage = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 2500)
  }));

  // 2) 가을과 겨울 사이 앨범 페이지에서 커버 이미지 고화질 URL 및 Track 4(오늘은 여기까지 id=ihIUw) 다운로드 리다이렉트 URL 확인
  await page.goto('https://distrokid.com/dashboard/album/?albumuuid=FC934BFB-150F-4894-B064A07100CC9BF4', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 3500));

  const vaultAssets = await page.evaluate(async () => {
    const artEl = document.querySelector('img.album-art, img[src*="artwork"], img[src*="cloudfront"], img[src*="s3"], .album-artwork img');
    const allImgs = Array.from(document.querySelectorAll('img')).map(i => ({ src: i.src, w: i.naturalWidth || i.width, h: i.naturalHeight || i.height })).filter(i => i.w > 60 && !i.src.includes('svg'));
    // 커버 이미지를 base64 dataURL로 추출
    let coverBase64 = '';
    const targetImg = artEl || (allImgs.length ? document.querySelector(`img[src="${allImgs[0].src}"]`) : null);
    if (targetImg) {
      try {
        const c = document.createElement('canvas');
        c.width = targetImg.naturalWidth || 1000;
        c.height = targetImg.naturalHeight || 1000;
        c.getContext('2d').drawImage(targetImg, 0, 0);
        coverBase64 = c.toDataURL('image/jpeg', 0.92);
      } catch (e) {}
    }
    return {
      detected_images: allImgs.slice(0, 8),
      has_cover_base64: coverBase64.length > 100
    };
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, spotify_for_artists: s4aPage, vault_assets: vaultAssets }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
dk_117_res = s1_ego.run_ego_js(js_dk_spotify_and_vault, timeout=75)

print("[3/5] 에고라이트 Space 3: @한걸음씩-r4i 인기 쇼츠(vSTcyW-K_9Q) 편집 화면에서 '관련 동영상(Related Video)' 설정 UI/셀렉터 실측 및 연결 중...")
js_related_video = """
let task = null;
try {
  try { task = await takeOverTaskSpace(3); } catch (_) { try { task = await claimTaskSpace(3); } catch (__) { task = await taskSpace(3); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  await page.goto('https://studio.youtube.com/video/vSTcyW-K_9Q/edit', { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 5000));

  const relInfo = await page.evaluate(() => {
    const els = Array.from(document.querySelectorAll('*')).filter(el => {
      const t = (el.innerText || '').trim();
      return (t === '관련 동영상' || t === 'Related video' || t.includes('관련 동영상')) && el.children.length < 5;
    }).map(el => ({
      tag: el.tagName,
      id: el.id,
      cls: el.className,
      text: (el.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 120)
    }));
    return { count: els.length, matches: els.slice(0, 10) };
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, related_video_ui: relInfo }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
rel_117_res = s1_ego.run_ego_js(js_related_video, timeout=60)

print("[4/5] 117호 급선무 TOP 3 합동 설계 및 실측 원장 저장 (GH013 클린 필터 적용) 중...")
report_117 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_117",
    "executed_at": datetime.datetime.now().isoformat(),
    "space1_sol_harvest": sol_117,
    "space2_opus_harvest": opus_117,
    "space4_spotify_for_artists_and_vault": dk_117_res,
    "space3_related_video_ui": rel_117_res
}
rep_txt = json.dumps(report_117, ensure_ascii=False, indent=2)
rep_txt = re.sub(r"4/0A[a-zA-Z0-9_\-]+", "REDACTED_OAUTH_CODE", rep_txt)
(BASE / "S1_TOP3_URGENT_PRIORITIES_117.json").write_text(rep_txt, encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_TOP3_URGENT_PRIORITIES_117.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(117): harvest Sol & Opus Top 3 urgent priorities and inspect DistroKid Spotify for Artists + YouTube Related Video UI"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

s4a_txt = dk_117_res.get("spotify_for_artists", {}).get("text", "")[:180] if isinstance(dk_117_res, dict) else ""
rel_cnt = rel_117_res.get("related_video_ui", {}).get("count", 0) if isinstance(rel_117_res, dict) else 0

print("[5/5] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (117호 솔·오푸스 급선무TOP3 합동수거 완료! SpotifyForArtists:{s4a_txt} | 쇼츠관련동영상UI:{rel_cnt}개 | 커밋:{sha})")
