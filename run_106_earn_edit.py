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

print("[1/3] 에고라이트 Space 3: '한걸음씩' YouTube Studio 수익 창출(Earn) 탭 실측 및 대표 뮤직비디오(P90h3HLw9Qk, 3nUJqf0ztBw) 설명란에 솔의 Spotify 링크 장착 중...")
js_studio_earn_and_edit = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}
  await page.evaluate(() => {{ window.__ego_overlay_disabled = true; }}).catch(() => {{}});

  // 1) 수익 창출(monetization) 탭 스캔
  await page.goto('https://studio.youtube.com/channel/UCMJn01WLs9ooIhh5x0eJeHg/monetization', {{ waitUntil: 'domcontentloaded', timeout: 30000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 4500));
  const earnData = await page.evaluate(() => ({{
    url: location.href,
    text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 3000)
  }}));

  // 2) 대표 뮤직비디오 '사냥꾼의 새벽' (P90h3HLw9Qk) 편집 페이지 진입 및 설명란 업데이트
  const prefix = {json.dumps(SOL_ABOVE_FOLD)};
  await page.goto('https://studio.youtube.com/video/P90h3HLw9Qk/edit', {{ waitUntil: 'domcontentloaded', timeout: 30000 }}).catch(() => {{}});
  await new Promise(r => setTimeout(r, 5000));

  const editRes = await page.evaluate(( prependText ) => {{
    const boxes = Array.from(document.querySelectorAll('#textbox[contenteditable="true"], div[contenteditable="true"][aria-label*="설명" i], div[contenteditable="true"][aria-label*="description" i]'));
    // 두 번째 textbox가 보통 설명란(첫 번째는 제목)
    const descBox = boxes.find(b => (b.getAttribute('aria-label') || '').includes('설명') || (b.getAttribute('aria-label') || '').toLowerCase().includes('description')) || boxes[1];
    if (!descBox) return {{ found: false, box_count: boxes.length }};
    const oldText = descBox.innerText || descBox.textContent || '';
    if (oldText.includes('44chP2pw8CFr0Z4aPNj4SO')) {{
      return {{ found: true, status: 'ALREADY_HAS_LINK', preview: oldText.slice(0, 200) }};
    }}
    descBox.focus();
    descBox.innerText = prependText + oldText;
    descBox.dispatchEvent(new InputEvent('input', {{ bubbles: true, inputType: 'insertText', data: descBox.innerText }}));
    descBox.dispatchEvent(new Event('change', {{ bubbles: true }}));
    return {{ found: true, status: 'INSERTED', preview: descBox.innerText.slice(0, 250) }};
  }}, prefix);

  await new Promise(r => setTimeout(r, 2000));
  const saveRes = await page.evaluate(() => {{
    const saveBtn = document.querySelector('#save-button, ytcp-button#save');
    if (saveBtn && !saveBtn.hasAttribute('disabled')) {{
      saveBtn.click();
      return {{ clicked_save: true }};
    }}
    // 내부 button 탐색
    const btns = Array.from(document.querySelectorAll('ytcp-button, button')).filter(b => (b.innerText || '').trim() === '저장' || (b.innerText || '').trim().toLowerCase() === 'save');
    if (btns.length > 0) {{
      btns[0].click();
      return {{ clicked_save: true, via: 'text_match' }};
    }}
    return {{ clicked_save: false }};
  }});
  await new Promise(r => setTimeout(r, 3500));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: true, earn_tab: earnData, edit_res: editRes, save_res: saveRes }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err.message || err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
st_106_res = s1_ego.run_ego_js(js_studio_earn_and_edit, timeout=85)

print("[2/3] 에고라이트 Space 4: 디스트로키드 OAC '/api/googleoauth' 직접 진입하여 Google 채널 선택 화면 확인 중...")
js_dk_oauth = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  await page.goto('https://distrokid.com/api/googleoauth', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 4000));
  const oauthScreen = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 2000)
  }));

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, oauth_screen: oauthScreen }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
dk_106_res = s1_ego.run_ego_js(js_dk_oauth, timeout=50)

out_106 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_106",
    "executed_at": datetime.datetime.now().isoformat(),
    "space3_earn_and_video_edit": st_106_res,
    "space4_dk_googleoauth": dk_106_res
}
(BASE / "S1_EARN_EDIT_AND_OAC_OAUTH_106.json").write_text(json.dumps(out_106, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_EARN_EDIT_AND_OAC_OAUTH_106.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(106): audit Hangeoreumsshik Earn tab, inject Sol Spotify formula into video P90h3HLw9Qk, and open DistroKid Google OAuth"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

earn_txt = st_106_res.get("earn_tab", {}).get("text", "")[:200] if isinstance(st_106_res, dict) else ""
ed_stat = st_106_res.get("edit_res", {}).get("status", "") if isinstance(st_106_res, dict) else ""
sv_stat = st_106_res.get("save_res", {}).get("clicked_save", False) if isinstance(st_106_res, dict) else False
oa_url = dk_106_res.get("oauth_screen", {}).get("url", "")[:120] if isinstance(dk_106_res, dict) else ""

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (106호 @한걸음씩 수익창출탭:{earn_txt} | 뮤비설명란장착:{ed_stat}(저장:{sv_stat}) | OAC_OAuth:{oa_url} | 커밋:{sha})")
