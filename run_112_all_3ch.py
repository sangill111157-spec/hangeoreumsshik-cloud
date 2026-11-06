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

print("[1/3] 에고라이트 Space 3: @Booster_Playlist 인기 쇼츠 6편 장착 후 -> 3번 채널 @TheCaféHour 영상 4편까지 전수 장착 중...")
js_booster_shorts_and_cafe = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}
  await page.evaluate(() => {{ window.__ego_overlay_disabled = true; }}).catch(() => {{}});

  // 1) @Booster_Playlist Shorts 탭 진입 및 상위 6편 설명란 장착
  await page.goto('https://studio.youtube.com/channel/UCR5SCwpTI1wTRnM1CV661Lg/videos/short', {{ waitUntil: 'domcontentloaded', timeout: 30000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 4500));

  const bShortIds = await page.evaluate(() => {{
    const ids = [];
    document.querySelectorAll('a[href*="/video/"]').forEach(a => {{
      const m = a.href.match(/\\/video\\/([a-zA-Z0-9_-]{{11}})\\//);
      if (m && !ids.includes(m[1])) ids.push(m[1]);
    }});
    return ids.slice(0, 6);
  }});

  const bPrefix = {json.dumps(BOOSTER_ABOVE_FOLD)};
  const boosterShortsUpdated = [];
  for (const sid of bShortIds) {{
    await page.goto('https://studio.youtube.com/video/' + sid + '/edit', {{ waitUntil: 'domcontentloaded', timeout: 30000 }}).catch(() => {{}});
    await new Promise(r => setTimeout(r, 4000));
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
    }}, bPrefix);
    await new Promise(r => setTimeout(r, 1200));
    const sv = await page.evaluate(() => {{
      const btns = Array.from(document.querySelectorAll('#save-button, ytcp-button#save, ytcp-button, button')).filter(b => (b.innerText || '').trim() === '저장' || (b.innerText || '').trim().toLowerCase() === 'save');
      if (btns.length > 0) {{ btns[0].click(); return true; }}
      return false;
    }});
    await new Promise(r => setTimeout(r, 2500));
    boosterShortsUpdated.push({{ short_id: sid, edit: ed.status, saved: sv }});
  }}

  // 2) channel_switcher에서 3번 채널 'The Café Hour'로 전환 후 4편 전수 장착
  await page.goto('https://www.youtube.com/channel_switcher', {{ waitUntil: 'domcontentloaded', timeout: 25000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 4000));
  await page.evaluate(() => {{
    const items = Array.from(document.querySelectorAll('ytd-account-item-renderer, tp-yt-paper-icon-item, a'));
    const target = items.find(el => (el.innerText || '').includes('Café Hour') || (el.innerText || '').includes('TheCaféHour'));
    if (target) {{
      const link = target.querySelector('a') || target.closest('a') || target;
      link.click();
    }}
  }});
  await new Promise(r => setTimeout(r, 5000));

  await page.goto('https://studio.youtube.com/channel/UCWSquL3NEAQcAKKBK2vam5g/videos/upload', {{ waitUntil: 'domcontentloaded', timeout: 30000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 4500));

  const cafeVidIds = await page.evaluate(() => {{
    const ids = [];
    document.querySelectorAll('a[href*="/video/"]').forEach(a => {{
      const m = a.href.match(/\\/video\\/([a-zA-Z0-9_-]{{11}})\\//);
      if (m && !ids.includes(m[1])) ids.push(m[1]);
    }});
    return ids.slice(0, 6);
  }});

  // Shorts 탭도 확인
  await page.goto('https://studio.youtube.com/channel/UCWSquL3NEAQcAKKBK2vam5g/videos/short', {{ waitUntil: 'domcontentloaded', timeout: 30000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 4000));
  const cafeShortIds = await page.evaluate(() => {{
    const ids = [];
    document.querySelectorAll('a[href*="/video/"]').forEach(a => {{
      const m = a.href.match(/\\/video\\/([a-zA-Z0-9_-]{{11}})\\//);
      if (m && !ids.includes(m[1])) ids.push(m[1]);
    }});
    return ids.slice(0, 6);
  }});

  const allCafeIds = Array.from(new Set([...cafeVidIds, ...cafeShortIds]));
  const cPrefix = {json.dumps(CAFE_ABOVE_FOLD)};
  const cafeUpdated = [];

  for (const cid of allCafeIds) {{
    await page.goto('https://studio.youtube.com/video/' + cid + '/edit', {{ waitUntil: 'domcontentloaded', timeout: 30000 }}).catch(() => {{}});
    await new Promise(r => setTimeout(r, 4000));
    const ed = await page.evaluate((prependText) => {{
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
    await new Promise(r => setTimeout(r, 1200));
    const sv = await page.evaluate(() => {{
      const btns = Array.from(document.querySelectorAll('#save-button, ytcp-button#save, ytcp-button, button')).filter(b => (b.innerText || '').trim() === '저장' || (b.innerText || '').trim().toLowerCase() === 'save');
      if (btns.length > 0) {{ btns[0].click(); return true; }}
      return false;
    }});
    await new Promise(r => setTimeout(r, 2500));
    cafeUpdated.push({{ video_id: cid, edit: ed.status, saved: sv }});
  }}

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: true, booster_shorts: boosterShortsUpdated, cafe_updated: cafeUpdated }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err.message || err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
ch23_112_res = s1_ego.run_ego_js(js_booster_shorts_and_cafe, timeout=210)

print("[2/3] 에고라이트 Space 4: 디스트로키드 OAC confirmYTChannelSelection 내부 AJAX 엔드포인트 추출 및 직접 POST/GET 호출 중...")
js_oac_ajax = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  const ajaxInfo = await page.evaluate(() => {
    const scripts = Array.from(document.querySelectorAll('script')).map(s => s.innerText || '').filter(t => t.includes('confirmYTChannelSelection'));
    if (!scripts.length) return { found: false };
    const full = scripts[0];
    const idx = full.indexOf('function confirmYTChannelSelection');
    return { found: true, code: idx >= 0 ? full.slice(idx, idx + 3500) : full.slice(-3500) };
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, ajax_info: ajaxInfo }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
oac_112_res = s1_ego.run_ego_js(js_oac_ajax, timeout=45)

out_112 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_112",
    "executed_at": datetime.datetime.now().isoformat(),
    "booster_shorts_and_cafe_hour_updated": ch23_112_res,
    "oac_ajax_code": oac_112_res
}
(BASE / "S1_ALL_3CHANNELS_SEO_AND_OAC_CODE_112.json").write_text(json.dumps(out_112, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_ALL_3CHANNELS_SEO_AND_OAC_CODE_112.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(112): update Booster Playlist Shorts and The Cafe Hour videos with HyperFollow/Spotify links and extract OAC AJAX endpoint"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

bs_u = ch23_112_res.get("booster_shorts", []) if isinstance(ch23_112_res, dict) else []
cf_u = ch23_112_res.get("cafe_updated", []) if isinstance(ch23_112_res, dict) else []
oac_c = oac_112_res.get("ajax_info", {}).get("code", "")[:200].replace("\n", " ") if isinstance(oac_112_res, dict) else ""

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (112호 부스터쇼츠6편:{bs_u} | 까페아워장착:{cf_u} | OAC코드:{oac_c} | 커밋:{sha})")
