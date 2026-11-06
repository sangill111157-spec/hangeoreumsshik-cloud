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

print("[1/3] 에고라이트 Space 4: Google OAuth 화면에서 물리 마우스 좌표 클릭(page.mouse.click)으로 'sangill111157@gmail.com' 선택 및 통과 중...")
js_oauth_mouse = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  const accBox = await page.evaluate(() => {
    const els = Array.from(document.querySelectorAll('div[data-identifier], li, div[role="link"], div[role="button"]')).filter(el => {
      const t = (el.innerText || '').trim();
      return t.includes('sangill111157@gmail.com') && el.getBoundingClientRect().height > 20 && el.getBoundingClientRect().height < 120;
    });
    const target = els[els.length - 1];
    if (!target) return null;
    const r = target.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2, w: r.width, h: r.height };
  });

  if (accBox && page.mouse) {
    await page.mouse.click(accBox.x, accBox.y);
  }
  await new Promise(r => setTimeout(r, 5000));

  // 다음 화면(권한 동의 Continue/Allow 버튼) 물리 마우스 클릭
  const allowBox = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button, input[type="submit"], div[role="button"]')).filter(b => {
      const t = (b.innerText || b.value || '').trim();
      return (t === '계속' || t === '허용' || t.toLowerCase() === 'continue' || t.toLowerCase() === 'allow') && b.getBoundingClientRect().width > 0;
    });
    const target = btns[btns.length - 1];
    if (!target) return null;
    const r = target.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2, text: (target.innerText || '').trim() };
  });

  if (allowBox && page.mouse) {
    await page.mouse.click(allowBox.x, allowBox.y);
    await new Promise(r => setTimeout(r, 5500));
  }

  // DistroKid 복귀 후 '채널 선택'(#confirmYTChannelSelectionButton) 클릭
  const finalState = await page.evaluate(() => {
    const cBtn = document.querySelector('#confirmYTChannelSelectionButton');
    let clickedConfirm = false;
    if (cBtn && cBtn.offsetParent !== null) {
      cBtn.click();
      clickedConfirm = true;
    }
    return {
      url: location.href,
      title: document.title,
      clicked_confirm: clickedConfirm,
      text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 2000)
    };
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, acc_box: accBox, allow_box: allowBox, final_state: finalState }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
oac_108_res = s1_ego.run_ego_js(js_oauth_mouse, timeout=75)

print("[2/3] 에고라이트 Space 3: @한걸음씩-r4i 인기 쇼츠 6편에 솔(Space 1)의 Spotify 전환 링크 일괄 장착 및 저장 중...")
SHORTS_IDS = ["vSTcyW-K_9Q", "_9TaYaBFmkQ", "I00rUemzODo", "FXnTfmWRv_s", "7Kk-c6ljjHg", "D7pfGWuhXjU"]

js_shorts_edit = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}
  await page.evaluate(() => {{ window.__ego_overlay_disabled = true; }}).catch(() => {{}});

  const sids = {json.dumps(SHORTS_IDS)};
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
      if (btns.length > 0) {{
        btns[0].click();
        return true;
      }}
      return false;
    }});
    await new Promise(r => setTimeout(r, 3000));
    results.push({{ short_id: sid, edit: ed.status, saved: sv }});
  }}

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: true, shorts_results: results }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err.message || err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
shorts_108_res = s1_ego.run_ego_js(js_shorts_edit, timeout=150)

out_108 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_108",
    "executed_at": datetime.datetime.now().isoformat(),
    "oac_mouse_oauth": oac_108_res,
    "shorts_6_batch_update": shorts_108_res
}
(BASE / "S1_SHORTS_SEO_AND_OAC_MOUSE_108.json").write_text(json.dumps(out_108, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_SHORTS_SEO_AND_OAC_MOUSE_108.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(108): inject Sol Spotify links into 6 Shorts and click Google OAuth account via mouse coordinates"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

s_res = shorts_108_res.get("shorts_results", []) if isinstance(shorts_108_res, dict) else []
f_url = oac_108_res.get("final_state", {}).get("url", "")[:100] if isinstance(oac_108_res, dict) else ""
f_txt = oac_108_res.get("final_state", {}).get("text", "")[:200] if isinstance(oac_108_res, dict) else ""

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (108호 본진 쇼츠 6편 스포티파이 링크 일괄장착:{s_res} | OAC마우스클릭후:{f_url} [{f_txt}] | 커밋:{sha})")
