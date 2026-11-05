import re, subprocess, pathlib

p = pathlib.Path('.')
h = p / 'index.html'
t = h.read_text(encoding='utf-8')

css_061 = """
/* [061-STEP1-CLEANUP] */
#s1-kakao-header-home .s1-sub-pills,
#s1-kakao-header-now .s1-sub-pills,
#s1-kakao-header-pick .s1-sub-pills,
#s1-kakao-header-more .s1-sub-pills,
.s1-chatroom-header .s1-chatroom-actions button {
  display: none !important;
}
"""
if "[061-STEP1-CLEANUP]" not in t:
    t = t.replace("</style>", css_061 + "\n</style>", 1)

js_061 = """
<script>
(function(){
  function cl061(){
    try {
      ['home','now','pick','more'].forEach(function(k){
        var e = document.getElementById('s1-kakao-header-' + k);
        if (e) {
          e.querySelectorAll('.s1-sub-pills').forEach(function(x){
            x.hidden = true;
            x.style.display = 'none';
          });
        }
      });
      document.querySelectorAll('div, section, nav').forEach(function(el){
        var s = (el.textContent || '').trim();
        if (s.indexOf('\uc218\uc2e0\ucc98:') !== -1 && s.indexOf('\ub974\uace4+\uc548\ucd1d\ub9ac \ub3d9\uc2dc') !== -1 && el.children.length <= 6 && !el.querySelector('#s1-kakao-chat-v055')) {
          el.hidden = true;
          el.style.display = 'none';
        }
      });
      document.querySelectorAll('a, button').forEach(function(b){
        var s = (b.textContent || '').trim();
        if ((s.indexOf('53\uace1 \ub9c8\uc2a4\ud130 \uc6d0\uc7a5 JSON') !== -1 || s.indexOf('1+12 \ud3ed\ud3ec\uc218 \ud37c\ub110 \ub9c8\uc2a4\ud130\ubd81') !== -1) && !b.classList.contains('s1-more-grid-item')) {
          b.hidden = true;
          b.style.display = 'none';
        }
        if (s.indexOf('\uc6d0\uc7a5') !== -1 && b.closest('#s1-kakao-header-chat, .s1-chat-list-header, .s1-kakao-top-header')) {
          b.hidden = true;
          b.style.display = 'none';
        }
      });
    } catch(e) {}
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', cl061);
  else cl061();
  setTimeout(cl061, 300);
})();
</script>
"""
if "cl061" not in t:
    t = t.replace("</body>", js_061 + "\n</body>", 1)

for f in ['index.html', 'rgon_alpha_chat.html', 'docs/index.html', 'docs/rgon_alpha_chat.html']:
    pathlib.Path(f).write_text(t, encoding='utf-8')

for f in ['sw.js', 'docs/sw.js']:
    st = pathlib.Path(f).read_text(encoding='utf-8')
    st = re.sub(r"const CACHE = '[^']+';", "const CACHE = 's1-aon-v061-step1-cleanup';", st)
    pathlib.Path(f).write_text(st, encoding='utf-8')

bp = p / 's1_rgon_to_anchongri_bridge.py'
if bp.exists():
    bt = bp.read_text(encoding='utf-8')
    bt = bt.replace('do_reload = (cycle_num % 4 == 1)', 'do_reload = True').replace('!isFocused && !isSelecting', '!isSelecting')
    bp.write_text(bt, encoding='utf-8')

subprocess.run(['python', 's1_qm_structure_linter.py'])
subprocess.run(['git', 'add', '-A'])
subprocess.run(['git', 'commit', '-m', 'feat(061): step 1 redundant button cleanup and force Space 0 auto-reload'])
subprocess.run(['git', 'push', 'origin', 'main'])
print('=== 061 CLEANUP & BRIDGE UPGRADE DONE! ===')
