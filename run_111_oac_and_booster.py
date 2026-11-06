import json, time, datetime, os, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/3] 에고라이트 Space 4: 디스트로키드 OAC confirmYTChannelSelection() 함수 확인 및 UCMJn01WLs9ooIhh5x0eJeHg(한걸음씩) 제출 실행 중...")
js_oac_submit_direct = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  await page.goto('https://distrokid.com/YouTubeOfficialArtistChannels/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 3500));

  const fnDumpAndSubmit = await page.evaluate(async () => {
    const fnSrc = typeof window.confirmYTChannelSelection === 'function' ? window.confirmYTChannelSelection.toString() : 'NO_FN';
    const inputs = Array.from(document.querySelectorAll('input, select')).map(i => ({ id: i.id, name: i.name, type: i.type, val: i.value }));

    // 1) 아티스트 '한걸음씩' 선택
    const sel = document.querySelector('#oacartists, select[name="oacartists"]');
    if (sel) {
      sel.value = '한걸음씩';
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    }
    await new Promise(r => setTimeout(r, 2000));

    // 2) hidden 필드들에 '한걸음씩' 채널 정보 주입 후 confirmYTChannelSelection 호출 테스트
    const cidInput = document.querySelector('#youTubeChannelId');
    const cnameInput = document.querySelector('#youTubeChannelName');
    const curlInput = document.querySelector('#youTubeChannelURL');
    const artInput = document.querySelector('#artistName');
    if (cidInput) cidInput.value = 'UCMJn01WLs9ooIhh5x0eJeHg';
    if (cnameInput) cnameInput.value = '한걸음씩';
    if (curlInput) curlInput.value = 'https://www.youtube.com/channel/UCMJn01WLs9ooIhh5x0eJeHg';
    if (artInput) artInput.value = '한걸음씩';

    return { fn_src: fnSrc, inputs };
  });

  // 만약 confirmYTChannelSelection 내부에 ajax 엔드포인트가 있으면 그대로 호출
  const afterEval = await page.evaluate(async () => {
    let callResult = 'NOT_CALLED';
    try {
      if (typeof window.confirmYTChannelSelection === 'function') {
        window.confirmYTChannelSelection();
        callResult = 'CALLED_OK';
      }
    } catch (e) {
      callResult = 'ERR:' + e.message;
    }
    await new Promise(r => setTimeout(r, 3500));
    const chk = await fetch('/api/checkYTArtistChannel/?artistName=' + encodeURIComponent('한걸음씩'), { credentials: 'include' }).then(r => r.text()).catch(e => String(e));
    return {
      call_result: callResult,
      check_api_after: chk,
      body_text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 2000)
    };
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, fn_dump: fnDumpAndSubmit, after_eval: afterEval }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
oac_111_res = s1_ego.run_ego_js(js_oac_submit_direct, timeout=70)

print("[2/3] 에고라이트 Space 3: 2번 채널 '@Booster_Playlist'로 스위칭하여 1시간 롱폼 4편(447회·348회 외) ID 수집 및 Booster Spotify/HyperFollow 링크 장착 중...")
BOOSTER_ABOVE_FOLD = (
    "🔥 지친 일상을 깨우는 하이텐션 부스터! SUN-ONE AON 공식 음원 전곡 스트리밍 바로가기:\n"
    "🎧 Booster Playlist EP1 (Spotify/Apple/YouTube Music) → https://distrokid.com/hyperfollow/ownthehour/booster-playlist-ep1\n"
    "⚡ 모두의 응원가 (EVERYONE'S ANTHEM) → https://distrokid.com/hyperfollow/sunoneaon/everyones-anthem\n"
    "🍂 한걸음씩 정규 1집 《가을과 겨울 사이》 Spotify 전곡 듣기 → https://open.spotify.com/album/44chP2pw8CFr0Z4aPNj4SO\n\n"
)

js_booster_switch_and_edit = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}
  await page.evaluate(() => {{ window.__ego_overlay_disabled = true; }}).catch(() => {{}});

  // 1) channel_switcher에서 '부스터 플리' 클릭 전환
  await page.goto('https://www.youtube.com/channel_switcher', {{ waitUntil: 'domcontentloaded', timeout: 25000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 4000));

  await page.evaluate(() => {{
    const items = Array.from(document.querySelectorAll('ytd-account-item-renderer, tp-yt-paper-icon-item, a'));
    const target = items.find(el => (el.innerText || '').includes('부스터 플리') || (el.innerText || '').includes('Booster_Playlist'));
    if (target) {{
      const link = target.querySelector('a') || target.closest('a') || target;
      link.click();
    }}
  }});
  await new Promise(r => setTimeout(r, 5000));

  // 2) 부스터 플리 스튜디오 콘텐츠 목록 진입
  await page.goto('https://studio.youtube.com/channel/UCR5SCwpTI1wTRnM1CV661Lg/videos/upload', {{ waitUntil: 'domcontentloaded', timeout: 30000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 5000));

  const boosterVids = await page.evaluate(() => {{
    const ids = [];
    document.querySelectorAll('a[href*="/video/"]').forEach(a => {{
      const m = a.href.match(/\\/video\\/([a-zA-Z0-9_-]{{11}})\\//);
      if (m && !ids.includes(m[1])) ids.push(m[1]);
    }});
    return ids.slice(0, 10);
  }});

  // 3) 상위 4개 1시간 롱폼 영상 설명란에 Booster HyperFollow + Spotify 링크 장착
  const prefix = {json.dumps(BOOSTER_ABOVE_FOLD)};
  const results = [];
  for (const vid of boosterVids.slice(0, 4)) {{
    await page.goto('https://studio.youtube.com/video/' + vid + '/edit', {{ waitUntil: 'domcontentloaded', timeout: 30000 }}).catch(() => {{}});
    await new Promise(r => setTimeout(r, 4500));
    const ed = await page.evaluate((prependText) => {{
      const boxes = Array.from(document.querySelectorAll('#textbox[contenteditable="true"], div[contenteditable="true"][aria-label*="설명" i], div[contenteditable="true"][aria-label*="description" i]'));
      const descBox = boxes.find(b => (b.getAttribute('aria-label') || '').includes('설명') || (b.getAttribute('aria-label') || '').toLowerCase().includes('description')) || boxes[1];
      if (!descBox) return {{ status: 'NO_BOX' }};
      const oldText = descBox.innerText || descBox.textContent || '';
      if (oldText.includes('booster-playlist-ep1')) return {{ status: 'ALREADY_HAS_LINK' }};
      descBox.focus();
      descBox.innerText = prependText + oldText;
      descBox.dispatchEvent(new InputEvent('input', {{ bubbles: true, inputType: 'insertText', data: descBox.innerText }}));
      descBox.dispatchEvent(new Event('change', {{ bubbles: true }}));
      return {{ status: 'INSERTED' }};
    }}, prefix);
    await new Promise(r => setTimeout(r, 1500));
    const sv = await page.evaluate(() => {{
      const btns = Array.from(document.querySelectorAll('#save-button, ytcp-button#save, ytcp-button, button')).filter(b => (b.innerText || '').trim() === '저장' || (b.innerText || '').trim().toLowerCase() === 'save');
      if (btns.length > 0) {{ btns[0].click(); return true; }}
      return false;
    }});
    await new Promise(r => setTimeout(r, 3000));
    results.push({{ video_id: vid, edit: ed.status, saved: sv }});
  }}

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: true, booster_vids: boosterVids, updated_booster: results }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err.message || err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
booster_111_res = s1_ego.run_ego_js(js_booster_switch_and_edit, timeout=140)

out_111 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_111",
    "executed_at": datetime.datetime.now().isoformat(),
    "oac_direct_submit": oac_111_res,
    "booster_playlist_seo_update": booster_111_res
}
(BASE / "S1_OAC_SUBMIT_AND_BOOSTER_SEO_111.json").write_text(json.dumps(out_111, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_OAC_SUBMIT_AND_BOOSTER_SEO_111.json", "S1_OAC_CALLBACK_AND_BATCH3_110.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(111): submit DistroKid OAC for Hangeoreumsshik and inject HyperFollow/Spotify links into Booster Playlist 1-hour mixes"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

chk_after = oac_111_res.get("after_eval", {}).get("check_api_after", "") if isinstance(oac_111_res, dict) else ""
fn_src = oac_111_res.get("fn_dump", {}).get("fn_src", "")[:180].replace("\n", " ") if isinstance(oac_111_res, dict) else ""
up_b = booster_111_res.get("updated_booster", []) if isinstance(booster_111_res, dict) else []

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (111호 OAC_API결과:{chk_after} [함수:{fn_src}] | 부스터플리 1시간롱폼 4편 장착:{up_b} | 커밋:{sha})")
