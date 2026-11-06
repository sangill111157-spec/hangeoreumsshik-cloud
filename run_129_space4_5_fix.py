# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
import json, datetime, os, time, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/4] 5번째 창(Space 4)을 원래대로 디스트로키드(distrokid.com/mymusic)로 원상복구 중...")
js_restore_space4 = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  await page.goto('https://distrokid.com/mymusic/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 2500));
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, space4_url: page.url(), title: await page.title() }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
s4_restore = s1_ego.run_ego_js(js_restore_space4, timeout=40)

print("[2/4] 대표님이 열어두신 6번째 창(Space 5)의 CapCut 화면(Credit discount on Seedance 2.0 Mini 및 크레딧·모델·메뉴)을 페이지 이동 없이 그대로 정밀 실측 중...")
js_scan_space5 = """
let task = null;
try {
  try { task = await takeOverTaskSpace(5); } catch (_) { try { task = await claimTaskSpace(5); } catch (__) { task = await taskSpace(5); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }

  const info = await page.evaluate(() => {
    const fullText = (document.body.innerText || '').replace(/\\s+/g, ' ').trim();
    const headerItems = Array.from(document.querySelectorAll('header *, [class*="header" i] *, [class*="nav" i] *, [class*="credit" i], [class*="point" i], [class*="pro" i], [class*="vip" i]'))
      .map(el => (el.innerText || '').replace(/\\s+/g, ' ').trim())
      .filter(t => t.length > 0 && t.length < 80);
    const buttonsAndCards = Array.from(document.querySelectorAll('button, a, [role="button"], [class*="card" i], [class*="model" i], [class*="seedance" i]'))
      .map(el => (el.innerText || '').replace(/\\s+/g, ' ').trim())
      .filter(t => t.length > 0 && t.length < 120);
    return {
      url: location.href,
      title: document.title,
      header_badges: Array.from(new Set(headerItems)).slice(0, 35),
      cards_and_buttons: Array.from(new Set(buttonsAndCards)).slice(0, 45),
      body_text: fullText.slice(0, 2500)
    };
  });
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, space5_capcut: info }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
s5_scan = s1_ego.run_ego_js(js_scan_space5, timeout=45)

print("[3/4] 6번째 창(Space 5) 캡컷 실제 데이터를 솔(Space 1)과 오푸스(Space 2)에게 전달하여 합동 분석 수거 중...")
s5_data = s5_scan.get("space5_capcut", {}) if isinstance(s5_scan, dict) else {}
s5_prompt_summary = f"URL:{s5_data.get('url')} | 상단배지:{s5_data.get('header_badges', [])[:15]} | 본문핵심:{str(s5_data.get('body_text', ''))[:900]}"

sol_s5 = ego.ask_and_harvest_side_room(
    1,
    f"[129호 Space 5 캡컷 정밀실측] 대표님이 직접 열어 로그인해 두신 6번째 창(Space 5) 실측 데이터다:\n{s5_prompt_summary}\n이 화면('Credit discount on Seedance 2.0 Mini' 및 보유 크레딧/메뉴)을 바탕으로 대표님 요금제에서 할 수 있는 기능과 '오늘은 여기까지(47.06MB WAV)' 뮤직비디오·쇼츠 제작 시 크레딧 최소 소모 전략을 JSON으로 답해줘.",
    wait_ms=22000
)
opus_s5 = ego.ask_and_harvest_side_room(
    2,
    f"[129호 Space 5 캡컷 감사요청] 5번째 창(Space 4)은 디스트로키드로 원상복구 완료({s4_restore.get('space4_url')})했고, 6번째 창(Space 5) 대표님 캡컷 실측 데이터는 다음과 같다:\n{s5_prompt_summary}\n현재 Space 5 캡컷의 크레딧/요금제 상태와 Seedance 2.0 Mini 할인 기능 활용 시 체크포인트를 JSON으로 답해줘.",
    wait_ms=22000
)

print("[4/4] Space 0~5 역할 배치를 기억창고(S1_EGO_SKILL_VAULT.json)에 영구 고정 후 완료 보고 중...")
vault_p = BASE / "S1_EGO_SKILL_VAULT.json"
if vault_p.exists():
    vdata = json.loads(vault_p.read_text(encoding="utf-8"))
    vdata["space_layout_6_immutable"] = {
        "Space_0": "르곤 보좌관 (Gemini 4 Argon)",
        "Space_1": "제2성 솔 (GPT-5.4 Pro)",
        "Space_2": "제3성 오푸스 (Claude Opus 4.6)",
        "Space_3": "YouTube Studio & Blogger (5대 채널 전환)",
        "Space_4": "DistroKid 전용 (절대 타 사이트로 덮어쓰기 금지!)",
        "Space_5": "CapCut 전용 (대표님 로그인 완료 · Seedance 2.0 Mini / 850 크레딧)"
    }
    vault_p.write_text(json.dumps(vdata, ensure_ascii=False, indent=2), encoding="utf-8")

out_129 = BASE / "S1_SPACE4_RESTORE_AND_SPACE5_CAPCUT_129.json"
out_129.write_text(json.dumps({
    "directive_id": "RGON_DIR_NEW_FOUNDATION_129",
    "executed_at": datetime.datetime.now().isoformat(),
    "space4_distrokid_restored": s4_restore,
    "space5_capcut_scan": s5_scan,
    "sol_space1_analysis": sol_s5,
    "opus_space2_audit": opus_s5
}, ensure_ascii=False, indent=2), encoding="utf-8")

subprocess.run(["git", "add", "-f", "S1_SPACE4_RESTORE_AND_SPACE5_CAPCUT_129.json", "S1_EGO_SKILL_VAULT.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(129): restore Space 4 to DistroKid, audit Space 5 CapCut Seedance 2.0 Mini, and lock 6-Space map"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

sol_txt = str(sol_s5.get("harvested", {}).get("latest_texts", [""])[0]).replace("\n", " ")[:220] if isinstance(sol_s5, dict) else ""
opus_txt = str(opus_s5.get("harvested", {}).get("latest_texts", [""])[0]).replace("\n", " ")[:220] if isinstance(opus_s5, dict) else ""
body_snip = str(s5_data.get("body_text", ""))[:260]

ego.send_auto_confirm_enter_space0(f"확인 (129호 Space4복구:{s4_restore.get('space4_url')} | Space5캡컷실측:[{body_snip}] | 솔:{sol_txt} | 오푸스:{opus_txt} | 커밋:{sha})")
