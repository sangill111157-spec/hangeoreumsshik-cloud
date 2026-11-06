# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
# DIRECTIVE_ID: RGON_DIR_NEW_FOUNDATION_144
import json, datetime, os, sys, time, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

ego.clear_all_spaces_lock()

print("[1/2] Space 6(Google Vids)에서 Closure UI 물리 마우스 좌표 클릭(page.mouse.click)으로 '스톡 및 웹' 서랍 열기 -> 검색창 타이핑 -> 스톡 영상 삽입 실행 중...")
js_vids_physical_mouse = """
let task = null;
try {
  try { task = await takeOverTaskSpace(6); } catch (_) { try { task = await claimTaskSpace(6); } catch (__) { task = await taskSpace(6); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }

  // 1. 우측 사이드바 '스톡 및 웹' 버튼의 정확한 물리 좌표(x, y) 측정
  const stockBox = await page.evaluate(() => {
    const els = Array.from(document.querySelectorAll('*'));
    const target = els.find(e => {
      const al = (e.getAttribute('aria-label') || e.getAttribute('data-tooltip') || '').trim();
      const t = (e.innerText || '').trim();
      const r = e.getBoundingClientRect();
      return r.width > 15 && r.height > 15 && r.left > 500 && (al.includes('스톡 및 웹') || t === '스톡 및 웹');
    });
    if (target) {
      const r = target.getBoundingClientRect();
      return { found: true, x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2), label: target.innerText || target.getAttribute('aria-label') };
    }
    return { found: false };
  });

  if (stockBox && stockBox.found) {
    await page.mouse.click(stockBox.x, stockBox.y);
    await new Promise(r => setTimeout(r, 3000));
  }

  // 2. 메인 페이지 및 모든 프레임(frames) 내부에서 새로 열린 검색 입력창 좌표 탐색
  let searchBox = await page.evaluate(() => {
    const inputs = Array.from(document.querySelectorAll('input, textarea, [role="searchbox"], [contenteditable="true"]')).filter(el => {
      const r = el.getBoundingClientRect();
      return r.width > 40 && r.height > 14 && r.left > 350;
    });
    if (inputs.length > 0) {
      const r = inputs[0].getBoundingClientRect();
      return { found: true, x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2), placeholder: inputs[0].placeholder || inputs[0].getAttribute('aria-label') || '' };
    }
    return { found: false };
  });

  // 만약 iframe 내부에 스톡 패널이 열렸다면 frames() 순회
  let frameUsed = 'main';
  if (!searchBox.found && page.frames) {
    const frames = page.frames();
    for (let fIdx = 0; fIdx < frames.length; fIdx++) {
      const f = frames[fIdx];
      try {
        const fInput = await f.evaluate(() => {
          const ins = Array.from(document.querySelectorAll('input, textarea, [role="searchbox"]')).filter(el => {
            const r = el.getBoundingClientRect();
            return r.width > 40 && r.height > 14;
          });
          if (ins.length > 0) {
            ins[0].focus();
            ins[0].click();
            return { found: true, ph: ins[0].placeholder || ins[0].getAttribute('aria-label') || '' };
          }
          return { found: false };
        });
        if (fInput && fInput.found) {
          searchBox = fInput;
          frameUsed = 'frame_' + fIdx;
          break;
        }
      } catch (e) {}
    }
  }

  let typed = false;
  if (searchBox && searchBox.found) {
    if (searchBox.x && searchBox.y) {
      await page.mouse.click(searchBox.x, searchBox.y);
    }
    await page.keyboard.press('Control+A').catch(() => {});
    await page.keyboard.press('Backspace').catch(() => {});
    await page.keyboard.type('warm tea night', { delay: 20 }).catch(() => {});
    await page.keyboard.press('Enter').catch(() => {});
    typed = true;
    await new Promise(r => setTimeout(r, 4000));
  }

  // 3. 검색 결과 첫 번째 스톡 미디어 물리 클릭하여 삽입
  const clipBox = await page.evaluate(() => {
    const mediaEls = Array.from(document.querySelectorAll('img, video, [role="option"], [role="listitem"]')).filter(el => {
      const r = el.getBoundingClientRect();
      return r.left > 450 && r.top > 140 && r.width > 50 && r.height > 35;
    });
    if (mediaEls.length > 0) {
      const r = mediaEls[0].getBoundingClientRect();
      return { found: true, count: mediaEls.length, x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2) };
    }
    return { found: false, count: 0 };
  });

  if (clipBox && clipBox.found) {
    await page.mouse.click(clipBox.x, clipBox.y);
    await new Promise(r => setTimeout(r, 3000));
  }

  const snap = await page.evaluate(() => {
    return (document.body.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 750);
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({
    ok: true,
    stock_btn: stockBox,
    frame_used: frameUsed,
    search_box: searchBox,
    typed: typed,
    clip_clicked: clipBox,
    snapshot: snap
  }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
res_144 = s1_ego.run_ego_js(js_vids_physical_mouse, timeout=50)

ego.clear_all_spaces_lock()

out_144 = BASE / "S1_VIDS_PHYSICAL_MOUSE_STOCK_144.json"
out_144.write_text(json.dumps({
    "directive_id": "RGON_DIR_NEW_FOUNDATION_144",
    "executed_at": datetime.datetime.now().isoformat(),
    "result": res_144
}, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_VIDS_PHYSICAL_MOUSE_STOCK_144.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(144): use physical mouse coordinates on Space 6 Google Vids to open Stock drawer and insert clip"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

ego.send_auto_confirm_enter_space0(
    f"확인 (144호 Space6물리마우스스톡실행:[스톡좌표:{res_144.get('stock_btn')} / 프레임:{res_144.get('frame_used')} / 검색창:{res_144.get('search_box')} / 타이핑:{res_144.get('typed')} / 클립클릭:{res_144.get('clip_clicked')}] | 화면:{str(res_144.get('snapshot',''))[:180]} | 커밋:{sha})"
)