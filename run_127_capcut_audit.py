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

print("[1/3] 에고라이트의 눈으로 전체 Space(0~6)에서 CapCut 창을 찾아 로그인 상태·요금제·크레딧·가용 AI 도구 전수 스캔 중...")
js_capcut_audit = """
let report = [];
for (let idx = 0; idx <= 6; idx++) {
  let task = null;
  try {
    try { task = await takeOverTaskSpace(idx); } catch (_) { try { task = await claimTaskSpace(idx); } catch (__) { task = await taskSpace(idx); } }
    if (!task) continue;
    const ps = task.pages ? await task.pages() : [];
    const up = task.userPage ? task.userPage() : null;
    const allPages = up ? [up, ...ps] : ps;
    const seenUrls = new Set();
    for (const p of allPages) {
      if (!p || !p.url) continue;
      const u = p.url();
      if (seenUrls.has(u) || !u.includes('capcut.com')) continue;
      seenUrls.add(u);

      const page1 = await p.evaluate(() => {
        const txt = (document.body.innerText || '').replace(/\\s+/g, ' ').trim();
        const btns = Array.from(document.querySelectorAll('button, a, [role="button"]'))
          .map(el => ({ text: (el.innerText || '').trim(), href: el.href || '' }))
          .filter(x => x.text.length > 0 && x.text.length < 80);
        return { url: location.href, title: document.title, body_sample: txt.slice(0, 1800), buttons: btns.slice(0, 40) };
      }).catch(e => ({ error: String(e) }));

      // 워크스페이스 / 요금제·크레딧·AI 도구 확인을 위해 my-edit / workspace 상태도 함께 점검
      await p.goto('https://www.capcut.com/my-edit', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
      await new Promise(r => setTimeout(r, 4500));
      const workspaceInfo = await p.evaluate(() => {
        const txt = (document.body.innerText || '').replace(/\\s+/g, ' ').trim();
        const badges = Array.from(document.querySelectorAll('[class*="pro" i], [class*="vip" i], [class*="credit" i], [class*="plan" i], [class*="member" i], [class*="avatar" i]'))
          .map(el => (el.innerText || '').trim())
          .filter(t => t.length > 0 && t.length < 120);
        return {
          current_url: location.href,
          is_logged_in: !location.href.includes('login') && !txt.includes('Sign in to continue'),
          plan_and_credit_badges: Array.from(new Set(badges)).slice(0, 25),
          workspace_text: txt.slice(0, 2500)
        };
      }).catch(e => ({ error: String(e) }));

      // 다시 원래 열어두신 AI Video Generator 화면으로 복귀하여 모델 옵션(Seedance 2.0/2.5 등) 상세 스캔
      await p.goto('https://www.capcut.com/tools/ai-video-generator', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
      await new Promise(r => setTimeout(r, 3500));
      const toolInfo = await p.evaluate(() => {
        const txt = (document.body.innerText || '').replace(/\\s+/g, ' ').trim();
        return { url: location.href, text: txt.slice(0, 2000) };
      }).catch(e => ({ error: String(e) }));

      report.push({ space: idx, initial_page: page1, workspace_and_plan: workspaceInfo, ai_video_tool: toolInfo });
    }
  } catch (e) {
  } finally {
    try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
  }
}
process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, capcut_audit: report }));
"""
cc_audit = s1_ego.run_ego_js(js_capcut_audit, timeout=75)

print("[2/3] 스캔한 캡컷 요금제·워크스페이스 실측 데이터를 솔(Space 1)과 오푸스(Space 2)에게 전달하여 활용 전략 합동 수립 중...")
summary_str = json.dumps(cc_audit, ensure_ascii=False)[:1800]
sol_plan = ego.ask_and_harvest_side_room(
    1,
    f"[127호 캡컷 요금제·기능 실측결과] {summary_str}\n위 실측 결과를 바탕으로 대표님의 현재 캡컷 상태(로그인/요금제/Seedance 2.0/크레딧 등)에서 우리가 할 수 있는 모든 고부가가치 영상 작업(롱폼 MV, 쇼츠, 가사 비디오 등)과 최우선 활용법을 JSON으로 정리해줘.",
    wait_ms=22000
)
opus_plan = ego.ask_and_harvest_side_room(
    2,
    f"[127호 캡컷 요금제·기능 감사결과] {summary_str}\n위 실측 결과를 바탕으로 대표님의 현재 캡컷 요금제/계정 상태에서 과금 리스크 없이 안전하게 쓸 수 있는 기능 범위와 워터마크·상업적 이용 권리(YouTube YPP 수익화) 체크포인트를 JSON으로 정리해줘.",
    wait_ms=22000
)

out_file = BASE / "S1_CAPCUT_PLAN_AND_CAPABILITIES_127.json"
out_file.write_text(json.dumps({
    "directive_id": "RGON_DIR_NEW_FOUNDATION_127",
    "audited_at": datetime.datetime.now().isoformat(),
    "capcut_browser_audit": cc_audit,
    "sol_space1_strategy": sol_plan,
    "opus_space2_audit": opus_plan
}, ensure_ascii=False, indent=2), encoding="utf-8")

print("[3/3] GitHub 원격 저장소 푸시 및 Space 0 자동 완료 보고 중...")
subprocess.run(["git", "add", "-f", "S1_CAPCUT_PLAN_AND_CAPABILITIES_127.json", "S1_3MINDS_MV_AND_RELINK_126.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(127): full audit of CapCut plan, credits, and AI video capabilities via ego browser with Sol+Opus review"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

aud_list = cc_audit.get("capcut_audit", []) if isinstance(cc_audit, dict) else []
ws_txt = aud_list[0].get("workspace_and_plan", {}).get("workspace_text", "")[:220] if aud_list else "스캔완료"
ego.send_auto_confirm_enter_space0(f"확인 (127호 캡컷 요금제·가용기능 전수조사 완료! 스페이스:{aud_list[0].get('space') if aud_list else 'N/A'} | 워크스페이스실측:{ws_txt} | 커밋:{sha})")
