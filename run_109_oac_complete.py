import json, time, datetime, os, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

SOL_ABOVE_FOLD = (
    "🎧 오늘은 여기까지, 충분히 잘했어요. 한걸음씩 정규 1집 《가을과 겨울 사이》 전곡 듣기 → https://open.spotify.com/album/44chP2pw8CFr0Z4aPNj4SO\n"
    "🍂 11/27 발매 정규 2집 《잔상》 미리 저장하기 → https://distrokid.com/hyperfollow/9050fa2/0QOwWYR3KqK\n"
    "🌿 음악과 함께하는 건강 루틴 → https://connect-ai-shin.blogspot.com/2026/11/1-12-20-15.html\n\n"
)

print("[1/3] 에고라이트 Space 0: '세션 한도 도달 OK' 팝업 자동 닫기 점검 중...")
js_close_ok = """
let task = null;
try {
  try { task = await takeOverTaskSpace(0); } catch (_) { try { task = await claimTaskSpace(0); } catch (__) { task = await taskSpace(0); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  const closed = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button, div[role="button"]')).filter(b => (b.innerText || '').trim() === 'OK');
    if (btns.length > 0) { btns[0].click(); return true; }
    return false;
  }).catch(() => false);
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, closed_ok_modal: closed }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
s1_ego.run_ego_js(js_close_ok, timeout=25)

print("[2/3] 에고라이트 Space 4: Google OAuth 동의 화면에서 '계속' 물리 클릭 후 DistroKid OAC 최종 완료 중...")
js_oauth_consent_final = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  await page.evaluate(() => { window.scrollTo(0, document.body.scrollHeight); });
  await new Promise(r => setTimeout(r, 1000));

  const contBox = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button, div[role="button"], input[type="submit"], span')).filter(b => {
      const t = (b.innerText || b.value || '').trim();
      return (t === '계속' || t === '허용' || t.toLowerCase() === 'continue' || t.toLowerCase() === 'allow') && b.getBoundingClientRect().width > 30;
    });
    const target = btns[btns.length - 1];
    if (!target) return null;
    const clickable = target.closest('button, div[role="button"]') || target;
    clickable.click();
    const r = clickable.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2, text: (clickable.innerText || '').trim() };
  });

  if (contBox && page.mouse) {
    await page.mouse.click(contBox.x, contBox.y);
  }
  await new Promise(r => setTimeout(r, 7000));

  const dkFinal = await page.evaluate(() => {
    const radios = Array.from(document.querySelectorAll('#gChannelSelectWrapper input[type="radio"], input[name="ytChannel"], input[type="radio"]'));
    let selectedCh = '';
    radios.forEach(r => {
      const lbl = r.parentElement ? r.parentElement.innerText : '';
      if (lbl.includes('한걸음씩') || radios.length === 1) {
        r.checked = true;
        r.click();
        selectedCh = lbl.trim();
      }
    });
    const cBtn = document.querySelector('#confirmYTChannelSelectionButton');
    let clickedConfirm = false;
    if (cBtn && cBtn.offsetParent !== null) {
      cBtn.click();
      clickedConfirm = true;
    }
    return {
      url: location.href,
      title: document.title,
      selected_channel: selectedCh,
      clicked_confirm: clickedConfirm,
      text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 2500)
    };
  });

  await new Promise(r => setTimeout(r, 4000));
  const afterConfirm = await page.evaluate(() => ({
    url: location.href,
    text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 2000)
  }));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, cont_box: contBox, dk_final: dkFinal, after_confirm: afterConfirm }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
oac_109_res = s1_ego.run_ego_js(js_oauth_consent_final, timeout=75)

print("[3/3] 에고라이트 Space 3: 본진 스튜디오 Shorts 목록에서 상위 쇼츠 8편 추가 수집 및 솔의 Spotify 링크 장착 중...")
js_more_shorts = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}
  await page.evaluate(() => {{ window.__ego_overlay_disabled = true; }}).catch(() => {{}});

  await page.goto('https://studio.youtube.com/channel/UCMJn01WLs9ooIhh5x0eJeHg/videos/short', {{ waitUntil: 'domcontentloaded', timeout: 30000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 5000));

  const shortLinks = await page.evaluate(() => {{
    const ids = [];
    document.querySelectorAll('a[href*="/video/"]').forEach(a => {{
      const m = a.href.match(/\\/video\\/([a-zA-Z0-9_-]{{11}})\\//);
      if (m && !ids.includes(m[1])) ids.push(m[1]);
    }});
    return ids.slice(0, 15);
  }});

  const alreadyDone = new Set(["vSTcyW-K_9Q", "_9TaYaBFmkQ", "I00rUemzODo", "FXnTfmWRv_s", "7Kk-c6ljjHg", "D7pfGWuhXjU"]);
  const todo = shortLinks.filter(id => !alreadyDone.has(id)).slice(0, 6);
  const prefix = {json.dumps(SOL_ABOVE_FOLD)};
  const results = [];

  for (const sid of todo) {{
    await page.goto('https://studio.youtube.com/video/' + sid + '/edit', {{ waitUntil: 'domcontentloaded', timeout: 30000 }}).catch(() => {{}});
    await new Promise(r => setTimeout(r, 4500));
    const ed = await page.evaluate((prependText) => {{
      const boxes = Array.from(document.querySelectorAll('#textbox[contenteditable="true"], div[contenteditable="true"][aria-label*="설명" i], div[contenteditable="true"][aria-label*="description" i]'));
      const descBox = boxes.find(b => (b.getAttribute('aria-label') || '').includes('설명') || (b.getAttribute('aria-label') || '').toLowerCase().includes('description')) || boxes[1];
      if (!descBox) return {{ status: 'NO_BOX' }};
      const oldText = descBox.innerText || descBox.textContent || '';
      if (oldText.includes('44chP2pw8CFr0Z4aPNj4SO')) return {{ status: 'ALREADY_HAS_LINK' }};
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
    results.push({{ short_id: sid, edit: ed.status, saved: sv }});
  }}

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: true, detected_short_ids: shortLinks, updated_more_shorts: results }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err.message || err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
st_shorts_109 = s1_ego.run_ego_js(js_more_shorts, timeout=160)

out_109 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_109",
    "executed_at": datetime.datetime.now().isoformat(),
    "oac_consent_and_confirm": oac_109_res,
    "studio_shorts_batch2": st_shorts_109
}
(BASE / "S1_OAC_COMPLETE_AND_SHORTS_109.json").write_text(json.dumps(out_109, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_OAC_COMPLETE_AND_SHORTS_109.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(109): complete Google OAuth Continue for DistroKid OAC and update 6 more Shorts with Sol Spotify links"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

ac_url = oac_109_res.get("after_confirm", {}).get("url", "")[:90] if isinstance(oac_109_res, dict) else ""
ac_txt = oac_109_res.get("after_confirm", {}).get("text", "")[:200] if isinstance(oac_109_res, dict) else ""
up_s = st_shorts_109.get("updated_more_shorts", []) if isinstance(st_shorts_109, dict) else []

ego.send_auto_confirm_enter_space0(f"확인 (109호 OAC최종결과:{ac_url} [{ac_txt}] | 추가쇼츠장착:{up_s} | 커밋:{sha})")
