import json, time, datetime, os, re, subprocess, urllib.request
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

print("[1/4] 디스트로키드 S3에서 <가을과 겨울 사이> 정품 앨범 커버 다운로드 및 Space 4에서 타이틀곡(오늘은 여기까지 id=ihIUw) 다운로드 URL 추출 중...")
COVER_URL = "https://s3.amazonaws.com/gather.fandalism.com/800x800%2D12259713%2D%2DFC934BFB%2D150F%2D4894%2DB064A07100CC9BF4%2D%2D0%2D%2D669193%2D%2D%2Ejpg"
cover_path = OUT_DIR / "AW_COVER_800x800.jpg"
try:
    req = urllib.request.Request(COVER_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        cover_path.write_bytes(resp.read())
    print(" -> 정품 앨범 커버 다운로드 완료:", cover_path.stat().st_size, "bytes")
except Exception as e:
    print(" -> 커버 다운로드 참고:", e)

# Space 4에서 Spotify for Artists '한걸음씩' 선택 및 vault/download/?id=ihIUw 의 실제 오디오 데이터(또는 S3 signed URL) 획득
js_dk_s4a_and_audio = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  // 1) Spotify for Artists 페이지에서 '한걸음씩' 선택
  await page.goto('https://distrokid.com/spotify/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 3000));
  const s4aAfter = await page.evaluate(async () => {
    const sel = document.querySelector('select');
    if (sel) {
      const opt = Array.from(sel.options).find(o => o.text.includes('한걸음씩'));
      if (opt) {
        sel.value = opt.value;
        sel.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }
    await new Promise(r => setTimeout(r, 3000));
    const links = Array.from(document.querySelectorAll('a, button, input[type="button"], input[type="submit"]')).map(el => ({
      text: (el.innerText || el.value || '').trim(),
      href: el.href || '',
      onclick: el.getAttribute('onclick') || ''
    })).filter(x => x.text && (x.text.includes('Spotify') || x.text.includes('연결') || x.text.includes('액세스') || x.text.includes('신청') || x.text.includes('계속') || x.href.includes('spotify')));
    return {
      url: location.href,
      text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 2000),
      action_links: links.slice(0, 15)
    };
  });

  // 2) 타이틀곡 #1 '오늘은 여기까지'(ihIUw) 다운로드 URL fetch(redirect URL 확인)
  const audioCheck = await page.evaluate(async () => {
    try {
      const r = await fetch('https://distrokid.com/vault/download/?id=ihIUw', { method: 'HEAD', credentials: 'include', redirect: 'follow' });
      return { ok: r.ok, status: r.status, final_url: r.url, ctype: r.headers.get('content-type') };
    } catch (e) {
      return { ok: false, err: e.message };
    }
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, s4a_after: s4aAfter, audio_check: audioCheck }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
dk_118_res = s1_ego.run_ego_js(js_dk_s4a_and_audio, timeout=65)

print("[2/4] 에고라이트 Space 3: 쇼츠(vSTcyW-K_9Q: 어머니는 꽃이다 쇼츠)에서 '#linked-video-editor-link'(관련 동영상) 클릭 후 풀버전 뮤비 자동 연결 및 저장 중...")
js_connect_related = """
let task = null;
try {
  try { task = await takeOverTaskSpace(3); } catch (_) { try { task = await claimTaskSpace(3); } catch (__) { task = await taskSpace(3); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  await page.goto('https://studio.youtube.com/video/vSTcyW-K_9Q/edit', { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 5000));

  // '#linked-video-editor-link' 클릭하여 관련 동영상 선택 모달 열기
  await page.evaluate(() => {
    const trig = document.querySelector('#linked-video-editor-link, ytcp-shorts-content-links-picker ytcp-text-dropdown-trigger');
    if (trig) trig.click();
  });
  await new Promise(r => setTimeout(r, 3500));

  // 열린 모달 내의 동영상 카드 목록 확인 및 '어머니는 꽃이다'(또는 첫 번째 롱폼) 클릭
  const pickResult = await page.evaluate(() => {
    const cards = Array.from(document.querySelectorAll('ytcp-entity-card, ytcp-video-pick-dialog-contents div[role="button"], .video-list-item, ytcp-ve'));
    const allDialogText = Array.from(document.querySelectorAll('tp-yt-paper-dialog, ytcp-dialog')).map(d => (d.innerText || '').replace(/\\s+/g, ' ').trim()).filter(Boolean);
    // '어머니는 꽃이다' 5:09 롱폼 또는 '빛의 아침' 탐색
    const clickableItems = Array.from(document.querySelectorAll('tp-yt-paper-dialog *, ytcp-dialog *')).filter(el => {
      const t = (el.innerText || '').trim();
      return (t.includes('어머니는 꽃이다') || t.includes('빛의 아침') || t.includes('사냥꾼의 새벽')) && el.getBoundingClientRect().width > 80 && el.getBoundingClientRect().height > 30 && el.getBoundingClientRect().height < 250;
    });
    if (clickableItems.length > 0) {
      clickableItems[clickableItems.length - 1].click();
      return { clicked: true, matched_count: clickableItems.length, dialog_preview: allDialogText.join(' | ').slice(0, 800) };
    }
    return { clicked: false, dialog_preview: allDialogText.join(' | ').slice(0, 800) };
  });

  await new Promise(r => setTimeout(r, 2500));
  const saveAfterRel = await page.evaluate(() => {
    const currentRelText = (document.querySelector('#linked-video-editor-link') || {}).innerText || '';
    const btns = Array.from(document.querySelectorAll('#save-button, ytcp-button#save, ytcp-button, button')).filter(b => (b.innerText || '').trim() === '저장' || (b.innerText || '').trim().toLowerCase() === 'save');
    let saved = false;
    if (btns.length > 0 && !btns[0].hasAttribute('disabled')) {
      btns[0].click();
      saved = true;
    }
    return { current_related_text: currentRelText.replace(/\\s+/g, ' ').trim(), saved };
  });
  await new Promise(r => setTimeout(r, 3000));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, pick_result: pickResult, save_after_rel: saveAfterRel }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
rel_118_res = s1_ego.run_ego_js(js_connect_related, timeout=75)

print("[3/4] 118호 실행 결과 저장 및 원격 GitHub 클린 푸시 중...")
out_118 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_118",
    "executed_at": datetime.datetime.now().isoformat(),
    "cover_downloaded": cover_path.exists(),
    "cover_size_bytes": cover_path.stat().st_size if cover_path.exists() else 0,
    "dk_s4a_and_audio_head": dk_118_res,
    "shorts_related_video_connection": rel_118_res
}
txt_118 = json.dumps(out_118, ensure_ascii=False, indent=2)
txt_118 = re.sub(r"4/0A[a-zA-Z0-9_\-]+", "REDACTED_OAUTH_CODE", txt_118)
(BASE / "S1_RELATED_VIDEO_AND_S4A_118.json").write_text(txt_118, encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_RELATED_VIDEO_AND_S4A_118.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(118): connect Related Video on Shorts, download official album cover, and check Spotify for Artists"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

rel_after = rel_118_res.get("save_after_rel", {}) if isinstance(rel_118_res, dict) else {}
aud_chk = dk_118_res.get("audio_check", {}) if isinstance(dk_118_res, dict) else {}
s4a_txt = dk_118_res.get("s4a_after", {}).get("text", "")[:160] if isinstance(dk_118_res, dict) else ""

print("[4/4] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (118호 쇼츠관련동영상연결:{rel_after} | 정품커버다운:{cover_path.exists()} | 음원URL체크:{aud_chk} | S4A:{s4a_txt} | 커밋:{sha})")
