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

print("[1/3] 에고라이트 Space 4: Google OAuth 화면에서 'sangill111157@gmail.com' 선택 및 Continue 클릭으로 OAC 신청 완료 중...")
js_oauth_finish = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  // 1) sangill111157@gmail.com 클릭
  const step1 = await page.evaluate(() => {
    const items = Array.from(document.querySelectorAll('li, div[data-identifier], div[role="link"], div[role="button"], a'));
    const target = items.find(el => (el.innerText || '').includes('sangill111157@gmail.com'));
    if (target) {
      target.click();
      return { clicked_account: true, text: (target.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 100) };
    }
    return { clicked_account: false };
  });

  await new Promise(r => setTimeout(r, 4500));

  // 2) 만약 권한 허용/계속(Continue/Allow) 화면이면 버튼 클릭
  const step2 = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button, input[type="submit"], div[role="button"]'));
    const allowBtn = btns.find(b => {
      const t = (b.innerText || b.value || '').trim();
      return t === '계속' || t === '허용' || t.toLowerCase() === 'continue' || t.toLowerCase() === 'allow';
    });
    if (allowBtn) {
      allowBtn.click();
      return { clicked_allow: true, text: (allowBtn.innerText || '').trim() };
    }
    return { clicked_allow: false };
  });

  await new Promise(r => setTimeout(r, 5000));

  // 3) DistroKid OAC 페이지로 돌아왔다면 최종 제출 버튼(#confirmYTChannelSelectionButton 등) 확인 및 클릭
  const step3 = await page.evaluate(() => {
    const confirmBtn = document.querySelector('#confirmYTChannelSelectionButton, input[type="submit"], button.buttonSmall');
    if (confirmBtn && confirmBtn.offsetParent !== null) {
      confirmBtn.click();
    }
    return {
      url: location.href,
      title: document.title,
      text: (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').trim().slice(0, 2500)
    };
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, step1, step2, step3 }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
oac_107_res = s1_ego.run_ego_js(js_oauth_finish, timeout=75)

print("[2/3] 에고라이트 Space 3: 본진 대표 뮤직비디오 5편(빛의 아침 563회, 어머니는 꽃이다 212회 외) 설명란에 솔의 Spotify 링크 일괄 장착 및 저장 중...")
REMAINING_VIDS = ["3nUJqf0ztBw", "v-UdDDTx5Fw", "ZGKDVNLzCyA", "pmiytSqutsQ", "hlIFjM_AGYc"]

js_batch_edit = f"""
let task = null;
try {{
  try {{ task = await takeOverTaskSpace(3); }} catch (_) {{ try {{ task = await claimTaskSpace(3); }} catch (__) {{ task = await taskSpace(3); }} }}
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}
  await page.evaluate(() => {{ window.__ego_overlay_disabled = true; }}).catch(() => {{}});

  const vids = {json.dumps(REMAINING_VIDS)};
  const prefix = {json.dumps(SOL_ABOVE_FOLD)};
  const results = [];

  for (const vid of vids) {{
    await page.goto('https://studio.youtube.com/video/' + vid + '/edit', {{ waitUntil: 'domcontentloaded', timeout: 30000 }}).catch(() => {{}});
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
    results.push({{ video_id: vid, edit: ed.status, saved: sv }});
  }}

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: true, batch_results: results }}));
}} catch (err) {{
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err.message || err) }}));
}} finally {{
  try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
}}
"""
batch_107_res = s1_ego.run_ego_js(js_batch_edit, timeout=150)

out_107 = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_107",
    "executed_at": datetime.datetime.now().isoformat(),
    "oac_oauth_finish": oac_107_res,
    "youtube_5_videos_batch_update": batch_107_res
}
(BASE / "S1_OAC_FINISH_AND_5VIDS_SEO_107.json").write_text(json.dumps(out_107, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_OAC_FINISH_AND_5VIDS_SEO_107.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(107): complete DistroKid OAC Google selection and update remaining 5 music videos with Sol Spotify links"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

b_res = batch_107_res.get("batch_results", []) if isinstance(batch_107_res, dict) else []
s3_txt = oac_107_res.get("step3", {}).get("text", "")[:220] if isinstance(oac_107_res, dict) else ""

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (107호 본진 5대뮤비 스포티파이 링크 일괄장착:{b_res} | OAC최종화면:{s3_txt} | 커밋:{sha})")
