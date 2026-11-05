import os, sys, re, time, json, subprocess, pathlib

BASE = pathlib.Path('.')
TARGETS = [
    BASE / 'index.html',
    BASE / 'rgon_alpha_chat.html',
    BASE / 'docs' / 'index.html',
    BASE / 'docs' / 'rgon_alpha_chat.html',
]

# 1. 063호 2차 정밀 청소 실행 (.s1-kakao-sub-pills 및 중복 버튼 완전 제거)
html = (BASE / 'index.html').read_text(encoding='utf-8')
css_063 = """
/* [063호 2차 정밀 청소] */
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
if "[063호 2차 정밀 청소]" not in html:
    html = html.replace("</style>", css_063 + "\n</style>", 1)

js_063 = """
<script>
(function(){
  function clean063(){
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
      document.querySelectorAll('div, section, nav').forEach(function(el){
        var s = (el.textContent || '').trim();
        if (s.indexOf('\uc218\uc2e0\ucc98:') !== -1 && s.indexOf('\ub974\uace4+\uc548\ucd1d\ub9ac') !== -1 && el.children.length <= 6 && !el.querySelector('#s1-kakao-chat-v055')) {
          el.hidden = true;
          el.style.setProperty('display', 'none', 'important');
        }
      });
    } catch(e) {}
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', clean063);
  else clean063();
  window.addEventListener('hashchange', clean063);
  document.addEventListener('click', function(){ setTimeout(clean063, 50); });
  setTimeout(clean063, 200);
})();
</script>
"""
if "clean063" not in html:
    html = html.replace("</body>", js_063 + "\n</body>", 1)

for t in TARGETS:
    t.write_text(html, encoding='utf-8')

for sw_f in [BASE / 'sw.js', BASE / 'docs' / 'sw.js']:
    st = sw_f.read_text(encoding='utf-8')
    st = re.sub(r"const CACHE = '[^']+';", "const CACHE = 's1-aon-v063-step2-cleanup';", st)
    sw_f.write_text(st, encoding='utf-8')

# 2. s1_rgon_to_anchongri_bridge.py에 [자동 수거 -> 자동 실행 -> Space 0 자동 완료 보고(reply0)] 장착!
bp = BASE / 's1_rgon_to_anchongri_bridge.py'
bt = bp.read_text(encoding='utf-8')

# Space 0 강제 새로고침 활성화
bt = bt.replace('do_reload = (cycle_num % 4 == 1)', 'do_reload = True')
bt = bt.replace('!isFocused && !isSelecting', '!isSelecting')

# auto_execute_directive_trigger 완료 직후 Space 0에 완료 보고서 자동 전송 코드 주입
auto_reply_hook = """                subprocess.run(["git", "push", "origin", "main"], cwd=BASE, check=False)
                # [AUTO_REPLY_TO_SPACE0] 임무 완료 즉시 에고라이트 Space 0(르곤 채팅창)에 완료 보고 자동 회신!
                try:
                    head_sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=BASE, text=True).strip()
                    reply_msg = f"[자동수거·임무완료 보고] 지시서 {directive_id} 실행 및 GitHub 푸시 완료! (커밋: {head_sha}, 린터 exit={linter_res.returncode})"
                    subprocess.run([sys.executable, str(BASE / "s1_ego.py"), "ask", "--space", "0", "--prompt", reply_msg], cwd=BASE, timeout=25, check=False)
                    subprocess.run([sys.executable, str(BASE / "s1_ego.py"), "finish", "--space", "0"], cwd=BASE, timeout=8, check=False)
                    print(f"[RGON_DIRECT_ENGINE] Auto-replied completion to Space 0: {reply_msg}", flush=True)
                except Exception as rep_err:
                    print(f"[RGON_DIRECT_ENGINE] Space 0 auto-reply note: {rep_err}", flush=True)"""

if "[AUTO_REPLY_TO_SPACE0]" not in bt:
    bt = bt.replace('                subprocess.run(["git", "push", "origin", "main"], cwd=BASE, check=False)', auto_reply_hook, 1)
    bp.write_text(bt, encoding='utf-8')

subprocess.run(['python', 's1_qm_structure_linter.py'])
subprocess.run(['git', 'add', '-A'])
subprocess.run(['git', 'commit', '-m', 'feat(063): step 2 precision cleanup and equip Bridge Daemon with Space 0 auto-reply'])
subprocess.run(['git', 'push', 'origin', 'main'])

# 3. 에고라이트 Space 0에 첫 자동 완료 보고 즉시 발사 테스트!
head_sha = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=BASE, text=True).strip()
test_msg = f"[자동수거·임무완료 보고] 063호 2차 정밀 청소 및 Space 0 자동 회신 엔진 장착 완료! (최신 커밋: {head_sha})"
subprocess.run([sys.executable, str(BASE / 's1_ego.py'), 'ask', '--space', '0', '--prompt', test_msg], cwd=BASE, timeout=25, check=False)
subprocess.run([sys.executable, str(BASE / 's1_ego.py'), 'finish', '--space', '0'], cwd=BASE, timeout=8, check=False)
print('=== 063 CLEANUP & AUTO-REPLY TO SPACE 0 SENT! ===')
