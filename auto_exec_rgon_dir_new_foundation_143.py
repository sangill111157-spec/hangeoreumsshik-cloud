# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
# DIRECTIVE_ID: RGON_DIR_NEW_FOUNDATION_143
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

print("[1/2] Google Vids 공식 매뉴얼(answer/14907575) 1~4단계 절차 그대로 Space 6에서 '스톡 및 웹' 클릭 -> 검색창 입력 -> 첫 번째 무료 시네마틱 스톡 동영상 삽입 실행 중...")
js_vids_stock_manual = """
let task = null;
try {
  try { task = await takeOverTaskSpace(6); } catch (_) { try { task = await claimTaskSpace(6); } catch (__) { task = await taskSpace(6); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }

  // Step 2: 캔버스 오른쪽 측면 패널에서 '스톡 및 웹' 클릭
  const stockTabClick = await page.evaluate(() => {
    const els = Array.from(document.querySelectorAll('button, [role="button"], [role="tab"], div, span'));
    const btn = els.find(e => {
      const al = (e.getAttribute('aria-label') || e.getAttribute('data-tooltip') || '').trim();
      const t = (e.innerText || '').trim();
      const r = e.getBoundingClientRect();
      return r.width > 10 && (al.includes('스톡 및 웹') || al.includes('스톡 미디어') || t === '스톡 및 웹');
    });
    if (btn) {
      btn.click();
      return { clicked: true, label: (btn.getAttribute('aria-label') || btn.innerText || '').trim() };
    }
    return { clicked: false };
  });
  await new Promise(r => setTimeout(r, 2500));

  // Step 3: 열린 '스톡 및 웹' 측면 패널의 검색창(화면 오른쪽 영역 input) 포커스 및 검색어 입력
  const searchInput = await page.evaluate(() => {
    const inputs = Array.from(document.querySelectorAll('input[type="text"], input[type="search"], input:not([type]), textarea')).filter(el => {
      const r = el.getBoundingClientRect();
      // 왼쪽 상단 문서 제목('이름 바꾸기', left < 300) 제외하고 우측 사이드 패널(left > 500) 입력창 선택
      return r.width > 50 && r.height > 15 && r.left > 400;
    });
    if (inputs.length > 0) {
      const target = inputs[0];
      target.focus();
      target.click();
      return { found: true, left_x: Math.round(target.getBoundingClientRect().left), ph: target.placeholder || target.getAttribute('aria-label') || '' };
    }
    return { found: false };
  });

  if (searchInput && searchInput.found) {
    await page.keyboard.press('Control+A').catch(() => {});
    await page.keyboard.press('Backspace').catch(() => {});
    await page.keyboard.type('warm tea night window', { delay: 15 }).catch(() => {});
    await page.keyboard.press('Enter').catch(() => {});
    await new Promise(r => setTimeout(r, 3500));
  }

  // Step 4: 검색 결과에서 첫 번째 스톡 동영상 항목 클릭하여 캔버스에 삽입
  const insertStock = await page.evaluate(() => {
    const items = Array.from(document.querySelectorAll('[role="listitem"], [role="option"], [role="button"], img, video')).filter(el => {
      const r = el.getBoundingClientRect();
      return r.left > 500 && r.top > 150 && r.width > 60 && r.height > 40;
    });
    if (items.length > 0) {
      items[0].click();
      return { inserted: true, candidate_count: items.length };
    }
    return { inserted: false, candidate_count: 0 };
  });
  await new Promise(r => setTimeout(r, 2500));

  const panelTxt = await page.evaluate(() => {
    return (document.body.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 700);
  });

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({
    ok: true,
    stock_tab: stockTabClick,
    search_input: searchInput,
    insert_result: insertStock,
    panel_text: panelTxt
  }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
res_143 = s1_ego.run_ego_js(js_vids_stock_manual, timeout=45)

ego.clear_all_spaces_lock()

out_143 = BASE / "S1_VIDS_STOCK_MANUAL_EXEC_143.json"
out_143.write_text(json.dumps({
    "directive_id": "RGON_DIR_NEW_FOUNDATION_143",
    "executed_at": datetime.datetime.now().isoformat(),
    "manual_reference": "https://support.google.com/a/users/answer/14907575?hl=ko",
    "result": res_143
}, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_VIDS_STOCK_MANUAL_EXEC_143.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(143): follow official Google Vids manual (answer/14907575) to search and insert free stock video on Space 6"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

ego.send_auto_confirm_enter_space0(
    f"확인 (143호 선사용설명서마스터후 Space6무료스톡삽입:[스톡탭클릭:{res_143.get('stock_tab')} / 우측검색창:{res_143.get('search_input')} / 클립삽입:{res_143.get('insert_result')}] | 화면:{str(res_143.get('panel_text',''))[:180]} | 커밋:{sha})"
)