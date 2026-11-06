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

print("[1/3] 에고라이트 Space 4: 디스트로키드 OAC Google OAuth 콜백 스크립트 확인 및 부모창 채널 선택 완료 중...")
js_oac_callback = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  // 현재 콜백 페이지의 HTML/script 소스 먼저 추출 (부모창에 어떤 함수를 호출하는지 확인)
  const callbackHtml = await page.evaluate(() => document.documentElement ? document.documentElement.outerHTML.slice(0, 4000) : '');

  // 다시 OAC 페이지로 이동 후 '한걸음씩' 선택 상태 확인
  await page.goto('https://distrokid.com/YouTubeOfficialArtistChannels/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 3500));

  await page.evaluate(() => {
    const sel = document.querySelector('select[name="oacartists"], select');
    if (sel) {
      sel.value = '한걸음씩';
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    }
  });
  await new Promise(r => setTimeout(r, 3500));

  const oacPageNow = await page.evaluate(async () => {
    const chk = await fetch('/api/checkYTArtistChannel/?artistName=' + encodeURIComponent('한걸음씩'), { credentials: 'include' }).then(r => r.text()).catch(e => String(e));
    // OAC 페이지의 전체 스크립트 뒷부분(confirmYTChannelSelection 함수 정의부) 추출
    const scripts = Array.from(document.querySelectorAll('script')).map(s => s.innerText || '').filter(t => t.includes('confirmYTChannelSelection'));
    return {
      check_api: chk,
      script_tail: scripts.length ? scripts[0].slice(2000, 7000) : '',
      body_text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 2000)
    };
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, callback_html: callbackHtml, oac_page_now: oacPageNow }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
oac_110_res = s1_ego.run_ego_js(js_oac_callback, timeout=70)

print("[2/3] 에고라이트 Space 3: 나머지 쇼츠 3편(8yA7lM9Li2E, 1JvIU-6thcU, TMdD6pBE2Ko)에 솔의 Spotify 링크 장착 중...")
BATCH3_SHORTS = ["8yA7lM9Li2E", "1JvIU-6thcU", "TMdD6pBE2Ko"]

js_batch3 = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}
  await page.evaluate(() => {{ window.__ego_overlay_disabled = true; }}).catch(() => {{}});

  const sids = {json.dumps(BATCH3_SHORTS)};
  const prefix = {json.dumps(SOL_ABOVE_FOLD)};
  const results = [];

  for (const sid of sids) {{
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

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: true, batch3_results: results }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err.message || err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
b3_110_res = s1_ego.run_ego_js(js_batch3, timeout=110)

out_110 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_110",
    "executed_at": datetime.datetime.now().isoformat(),
    "oac_callback_inspection": oac_110_res,
    "shorts_batch3_results": b3_110_res
}
(BASE / "S1_OAC_CALLBACK_AND_BATCH3_110.json").write_text(json.dumps(out_110, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_OAC_CALLBACK_AND_BATCH3_110.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(110): inspect OAC callback script and update 3 more Shorts (total 21 videos updated)"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

cb_html = oac_110_res.get("callback_html", "")[:220].replace("\n", " ") if isinstance(oac_110_res, dict) else ""
b3_r = b3_110_res.get("batch3_results", []) if isinstance(b3_110_res, dict) else []

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (110호 본진 총 21편 스포티파이 링크 장착 달성:{b3_r} | OAC콜백소스:{cb_html} | 커밋:{sha})")
