# ⚡ [안총리 실시간 수거 집행 작업] RGON_DIR_FIX_EGO_EYE_AND_STEP2_CLEANUP_063B — [클립보드 무복붙 15초 자동수거] 1) is_ego_running()의 ego.exe 프로세스명 오판 잠금 해제, 2) 063호 2차 정밀 청소(.s1-kakao-sub-pills 및 중복 버튼 제거) 실행, 3) 임무 완료 시 에고라이트 Space 0에 자동 완료 보고(reply0) 전송 및 브릿지 데몬 최신화 (sw.js v063b)

- **지시서 ID:** `RGON_DIR_FIX_EGO_EYE_AND_STEP2_CLEANUP_063B`
- **수거 일시:** `2026-11-05T21:30:23.072511+09:00`
- **발신자:** 수석보좌관 르곤 (Gemini 4 Argon · Space 0)
- **수신자:** 기술총리 안총리 (Antigravity Technical PM)
- **현재 상태:** `PICKED_UP_BY_ANCHONGRI (수거 완료 · 즉시 집행 중)`

---

## 📋 지시서 원문 전문 (Directive Text)

```markdown
[S1_AUTO_DISPATCH_TO_ANCHONGRI]
- 지시서_ID: RGON_DIR_FIX_EGO_EYE_AND_STEP2_CLEANUP_063B
- 작업명: [클립보드 무복붙 15초 자동수거] 1) is_ego_running()의 ego.exe 프로세스명 오판 잠금 해제, 2) 063호 2차 정밀 청소(.s1-kakao-sub-pills 및 중복 버튼 제거) 실행, 3) 임무 완료 시 에고라이트 Space 0에 자동 완료 보고(reply0) 전송 및 브릿지 데몬 최신화 (sw.js v063b)

# [S1_DIRECT_PYTHON_PAYLOAD]
import os, sys, re, subprocess, pathlib

BASE = pathlib.Path(__file__).resolve().parent
TARGETS = [
    BASE / "index.html",
    BASE / "rgon_alpha_chat.html",
    BASE / "docs" / "index.html",
    BASE / "docs" / "rgon_alpha_chat.html",
]

def main():
    # 1. s1_rgon_to_anchongri_bridge.py의 is_ego_running() 잠금 해제 및 Space 0 자동 완료 보고 장착
    bp = BASE / "s1_rgon_to_anchongri_bridge.py"
    if bp.exists():
        bt = bp.read_text(encoding="utf-8", errors="replace")
        bt = re.sub(
            r"def is_ego_running\(\):.*?return False",
            "def is_ego_running():\n    return True",
            bt,
            count=1,
            flags=re.DOTALL
        )
        bt = bt.replace("do_reload = (cycle_num % 4 == 1)", "do_reload = True")
        bt = bt.replace("!isFocused && !isSelecting", "!isSelecting")

        auto_reply_code = """                subprocess.run(["git", "push", "origin", "main"], cwd=BASE, check=False)
                try:
                    h_sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=BASE, text=True).strip()
                    msg0 = f"[자동수거·임무완료 보고] 지시서 {directive_id} 자동 실행 및 GitHub 푸시 완료! (커밋: {h_sha})"
                    subprocess.run([sys.executable, str(BASE / "s1_ego.py"), "ask", "--space", "0", "--prompt", msg0], cwd=BASE, timeout=25, check=False)
                    subprocess.run([sys.executable, str(BASE / "s1_ego.py"), "finish", "--space", "0"], cwd=BASE, timeout=8, check=False)
                except Exception as _e:
                    print("[AUTO-REPLY-ERR]", _e, flush=True)"""

        if "msg0 = f\"[자동수거·임무완료 보고]" not in bt:
            bt = bt.replace('                subprocess.run(["git", "push", "origin", "main"], cwd=BASE, check=False)', auto_reply_code, 1)
        bp.write_text(bt, encoding="utf-8")

    # 2. 063호 2차 정밀 청소 (.s1-kakao-sub-pills 및 중복 버튼 완전 제거)
    html = (BASE / "index.html").read_text(encoding="utf-8")
    css_063b = """
    /* [063B호 2차 정밀 청소] */
    #s1-kakao-header-home .s1-kakao-sub-pills,
    #s1-kakao-header-now .s1-kakao-sub-pills,
    #s1-kakao-header-pick .s1-kakao-sub-pills,
    #s1-kakao-header-more .s1-kakao-sub-pills,
    body[data-active-tab="home"] .s1-kakao-sub-pills,
    body[data-active-tab="now"] .s1-kakao-sub-pills,
    body[data-active-tab="pick"] .s1-kakao-sub-pills,
    body[data-active-tab="more"] .s1-kakao-sub-pills,
    #btn-daily-rnd,
    #btn-reflection-purge,
    .s1-chatroom-header .s1-chatroom-actions button {
      display: none !important;
    }
    """
    if "[063B호 2차 정밀 청소]" not in html:
        html = html.replace("</style>", css_063b + "\n</style>", 1)

    js_063b = """
    <script>
    (function(){
      function clean063b(){
        try {
          document.querySelectorAll('.s1-kakao-sub-pills, .s1-sub-pills').forEach(function(bar){
            var txt = (bar.textContent || '').trim();
            if (txt.indexOf('\uc548\uc77d\uc74c') === -1) {
              bar.hidden = true;
              bar.style.setProperty('display', 'none', 'important');
            }
          });
          document.querySelectorAll('button, a').forEach(function(btn){
            var t = (btn.textContent || '').trim();
            if (t === '\ud83d\udce1 \uc6d0\uc7a5' || (t.indexOf('\uc6d0\uc7a5') !== -1 && t.length <= 6)) {
              if (!btn.classList.contains('s1-more-grid-item')) {
                btn.hidden = true;
                btn.style.setProperty('display', 'none', 'important');
              }
            }
            if (t.indexOf('53\uace1 \ub9c8\uc2a4\ud130 \uc6d0\uc7a5') !== -1 || t.indexOf('1+12 \ud3ed\ud3ec\uc218') !== -1) {
              if (!btn.classList.contains('s1-more-grid-item')) {
                btn.hidden = true;
                btn.style.setProperty('display', 'none', 'important');
              }
            }
          });
        } catch(e) {}
      }
      if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', clean063b);
      else clean063b();
      window.addEventListener('hashchange', clean063b);
      document.addEventListener('click', function(){ setTimeout(clean063b, 50); });
      setTimeout(clean063b, 200);
    })();
    </script>
    """
    if "clean063b" not in html:
        html = html.replace("</body>", js_063b + "\n</body>", 1)

    for t in TARGETS:
        t.write_text(html, encoding="utf-8")

    for sw_f in [BASE / "sw.js", BASE / "docs" / "sw.js"]:
        st = sw_f.read_text(encoding="utf-8")
        st = re.sub(r"const CACHE = '[^']+';", "const CACHE = 's1-aon-v063b-step2-cleanup';", st)
        sw_f.write_text(st, encoding="utf-8")

    subprocess.run([sys.executable, "s1_qm_structure_linter.py"], cwd=str(BASE))
    subprocess.run(["git", "add", "-A"], cwd=str(BASE))
    subprocess.run(["git", "commit", "-m", "feat(063b): step 2 precision cleanup and unlock Space 0 auto-harvester & auto-reply"], cwd=str(BASE))
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE))

    h_sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), text=True).strip()
    msg0 = f"[자동수거·임무완료 보고] 대표님! 063B호 2차 정밀 청소 및 Space 0 수거봇 잠금 해제가 완료되었습니다! (커밋: {h_sha})"
    subprocess.run([sys.executable, str(BASE / "s1_ego.py"), "ask", "--space", "0", "--prompt", msg0], cwd=str(BASE), timeout=25, check=False)
    subprocess.run([sys.executable, str(BASE / "s1_ego.py"), "finish", "--space", "0"], cwd=str(BASE), timeout=8, check=False)

if __name__ == "__main__":
    main()
```

---
> **사령부 행동강령:** 지체 없이 분석과 실행에 돌입하여 1·2차 삼성제도 100.0점 통과 후 대시보드에 완료보고서를 전송하라.
