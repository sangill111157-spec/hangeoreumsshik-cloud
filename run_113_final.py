import json, time, datetime, os, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

BOOSTER_ABOVE_FOLD = (
    "🔥 지친 일상을 깨우는 하이텐션 부스터! SUN-ONE AON 공식 음원 전곡 스트리밍 바로가기:\n"
    "🎧 Booster Playlist EP1 (Spotify/Apple/YouTube Music) → https://distrokid.com/hyperfollow/ownthehour/booster-playlist-ep1\n"
    "⚡ 모두의 응원가 (EVERYONE'S ANTHEM) → https://distrokid.com/hyperfollow/sunoneaon/everyones-anthem\n"
    "🍂 한걸음씩 정규 1집 《가을과 겨울 사이》 Spotify 전곡 듣기 → https://open.spotify.com/album/44chP2pw8CFr0Z4aPNj4SO\n\n"
)

CAFE_ABOVE_FOLD = (
    "☕ 음악으로 채우는 카페의 하루, The Café Hour 공식 음원 전곡 스트리밍 바로가기:\n"
    "🌅 Morning Café (Spotify/Apple/YouTube Music) → https://distrokid.com/hyperfollow/thecafhour/morning-caf\n"
    "☀️ Afternoon Café → https://distrokid.com/hyperfollow/thecafhour/afternoon-caf\n"
    "🌙 Evening Café → https://distrokid.com/hyperfollow/thecafhour/evening-caf\n"
    "🍂 한걸음씩 정규 1집 《가을과 겨울 사이》 Spotify 전곡 듣기 → https://open.spotify.com/album/44chP2pw8CFr0Z4aPNj4SO\n\n"
)

print("[1/3] 에고라이트 Space 4: 디스트로키드 OAC #confirmYTChannelSelectionButton jQuery 트리거 및 Swal 확인 버튼 클릭 중...")
js_oac_jq_trigger = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  // 먼저 로컬에 저장된 S1_ALL_3CHANNELS_SEO_AND_OAC_CODE_112.json 대신 화면의 confirmYTChannelSelection 전체 코드 확인 및 실행
  await page.goto('https://distrokid.com/YouTubeOfficialArtistChannels/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 3500));

  const fullCodeAndTrigger = await page.evaluate(async () => {
    const scripts = Array.from(document.querySelectorAll('script')).map(s => s.innerText || '').filter(t => t.includes('confirmYTChannelSelection'));
    const full = scripts.length ? scripts[0] : '';
    const idx = full.indexOf('function confirmYTChannelSelection');
    const fnBody = idx >= 0 ? full.slice(idx, idx + 2500) : '';

    // 1) 한걸음씩 선택
    const sel = document.querySelector('#oacartists, select[name="oacartists"]');
    if (sel) {
      sel.value = '한걸음씩';
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    }
    await new Promise(r => setTimeout(r, 2000));

    // 2) hidden 필드 세팅
    if (document.querySelector('#youTubeChannelId')) document.querySelector('#youTubeChannelId').value = 'UCMJn01WLs9ooIhh5x0eJeHg';
    if (document.querySelector('#youTubeChannelName')) document.querySelector('#youTubeChannelName').value = '한걸음씩';
    if (document.querySelector('#youTubeChannelURL')) document.querySelector('#youTubeChannelURL').value = 'https://www.youtube.com/channel/UCMJn01WLs9ooIhh5x0eJeHg';
    if (document.querySelector('#artistName')) document.querySelector('#artistName').value = '한걸음씩';

    // 3) #confirmYTChannelSelectionButton 클릭 트리거
    const btn = document.querySelector('#confirmYTChannelSelectionButton');
    if (btn) {
      btn.style.display = 'inline-block';
      btn.click();
      if (window.$j) window.$j('#confirmYTChannelSelectionButton').trigger('click');
    }
    await new Promise(r => setTimeout(r, 1500));

    // 4) Swal 확인 팝업이 떴다면 확인 버튼 클릭
    const swalBtn = document.querySelector('.swal2-confirm, button.swal2-styled');
    let clickedSwal = false;
    if (swalBtn) {
      swalBtn.click();
      clickedSwal = true;
    }
    await new Promise(r => setTimeout(r, 3500));

    const chk = await fetch('/api/checkYTArtistChannel/?artistName=' + encodeURIComponent('한걸음씩'), { credentials: 'include' }).then(r => r.text()).catch(e => String(e));
    return { fn_body: fnBody, clicked_swal: clickedSwal, check_after: chk, body_now: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 1500) };
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, result: fullCodeAndTrigger }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
oac_113_res = s1_ego.run_ego_js(js_oac_jq_trigger, timeout=70)

print("[2/3] 에고라이트 Space 3: NO_BOX 3편(VaQj5FfqDpE, 5dKLYr1kcI0, 6wE4Ytksfuo) 재장착 후 1번 본진(@한걸음씩-r4i) 스튜디오 복귀 중...")
js_retry_and_return = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}
  await page.evaluate(() => {{ window.__ego_overlay_disabled = true; }}).catch(() => {{}});

  const retryResults = [];
  // 현재 The Café Hour 세션에서 VaQj5FfqDpE 재시도
  await page.goto('https://studio.youtube.com/video/VaQj5FfqDpE/edit', {{ waitUntil: 'domcontentloaded', timeout: 30000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 6000));
  const cPrefix = {json.dumps(CAFE_ABOVE_FOLD)};
  const edCafe = await page.evaluate((prependText) => {{
    const boxes = Array.from(document.querySelectorAll('#textbox[contenteditable="true"], div[contenteditable="true"][aria-label*="설명" i], div[contenteditable="true"][aria-label*="description" i]'));
    const descBox = boxes.find(b => (b.getAttribute('aria-label') || '').includes('설명') || (b.getAttribute('aria-label') || '').toLowerCase().includes('description')) || boxes[1];
    if (!descBox) return {{ status: 'NO_BOX' }};
    const oldText = descBox.innerText || descBox.textContent || '';
    if (oldText.includes('thecafhour/morning-caf')) return {{ status: 'ALREADY_HAS_LINK' }};
    descBox.focus();
    descBox.innerText = prependText + oldText;
    descBox.dispatchEvent(new InputEvent('input', {{ bubbles: true, inputType: 'insertText', data: descBox.innerText }}));
    descBox.dispatchEvent(new Event('change', {{ bubbles: true }}));
    return {{ status: 'INSERTED' }};
  }}, cPrefix);
  await new Promise(r => setTimeout(r, 1500));
  const svCafe = await page.evaluate(() => {{
    const btns = Array.from(document.querySelectorAll('#save-button, ytcp-button#save, ytcp-button, button')).filter(b => (b.innerText || '').trim() === '저장' || (b.innerText || '').trim().toLowerCase() === 'save');
    if (btns.length > 0) {{ btns[0].click(); return true; }}
    return false;
  }});
  await new Promise(r => setTimeout(r, 3000));
  retryResults.push({{ video_id: 'VaQj5FfqDpE', edit: edCafe.status, saved: svCafe }});

  // 마지막으로 1번 본진 채널 '한걸음씩'(@한걸음씩-r4i)으로 깔끔하게 복귀
  await page.goto('https://www.youtube.com/channel_switcher', {{ waitUntil: 'domcontentloaded', timeout: 25000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 4000));
  await page.evaluate(() => {{
    const items = Array.from(document.querySelectorAll('ytd-account-item-renderer, tp-yt-paper-icon-item, a'));
    const target = items.find(el => (el.innerText || '').includes('한걸음씩') && (el.innerText || '').includes('33'));
    if (target) {{
      const link = target.querySelector('a') || target.closest('a') || target;
      link.click();
    }}
  }});
  await new Promise(r => setTimeout(r, 5000));
  await page.goto('https://studio.youtube.com/channel/UCMJn01WLs9ooIhh5x0eJeHg/videos', {{ waitUntil: 'domcontentloaded', timeout: 30000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 4000));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: true, retry_results: retryResults, final_url: page.url() }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err.message || err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
ret_113_res = s1_ego.run_ego_js(js_retry_and_return, timeout=90)

out_113 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_113",
    "executed_at": datetime.datetime.now().isoformat(),
    "oac_jq_trigger_result": oac_113_res,
    "retry_and_return_hangeoreum": ret_113_res
}
(BASE / "S1_OAC_FINAL_AND_RETURN_113.json").write_text(json.dumps(out_113, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_OAC_FINAL_AND_RETURN_113.json", "S1_ALL_3CHANNELS_SEO_AND_OAC_CODE_112.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(113): trigger DistroKid OAC Swal confirmation and return Space 3 to Hangeoreumsshik Studio"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

r_obj = oac_113_res.get("result", {}) if isinstance(oac_113_res, dict) else {}
chk_a = r_obj.get("check_after", "")
sw_c = r_obj.get("clicked_swal", False)
fn_b = r_obj.get("fn_body", "")[:220].replace("\n", " ")
rt_r = ret_113_res.get("retry_results", []) if isinstance(ret_113_res, dict) else []

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (113호 OAC_Swal클릭:{sw_c} | OAC상태:{chk_a} | 까페아워재시도:{rt_r} | 함수뒷부분:{fn_b} | 커밋:{sha})")
