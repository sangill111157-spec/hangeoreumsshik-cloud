import re

path = 'dashboard/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. URL Query Parameter Tab Auto-Selection in DOMContentLoaded
old_init = "switchTab('tab-command');"
new_init = """// URL 쿼리 파라미터 또는 해시 기반 탭 자동 선택
      const urlParams = new URLSearchParams(window.location.search);
      const tabParam = urlParams.get('tab') || window.location.hash.replace('#', '');
      if (tabParam === 'daughters' || tabParam === 'tab-daughters') {
        switchTab('tab-daughters');
      } else if (tabParam && document.getElementById(tabParam.startsWith('tab-') ? tabParam : 'tab-' + tabParam)) {
        switchTab(tabParam.startsWith('tab-') ? tabParam : 'tab-' + tabParam);
      } else {
        switchTab('tab-command');
      }"""

if old_init in html:
    html = html.replace(old_init, new_init, 1)
    print("Replaced hardcoded switchTab('tab-command') with smart URL tab selector!")
else:
    print("old_init not found, checking...")

# 2. Add floating mobile quick-switcher badge at top of mobile header if not present
mob_quick_badge = """
      <!-- 모바일 전용 인성학교 & 꿈의 옷장 원터치 다이렉트 칩 -->
      <div class="md:hidden flex items-center gap-1.5 overflow-x-auto py-1 px-3 bg-slate-950/90 border-b border-amber-500/30 text-[11px] shrink-0">
        <span class="text-amber-400 font-bold shrink-0">🚀 빠른이동:</span>
        <button type="button" onclick="switchTab('tab-daughters')" class="px-2.5 py-0.5 rounded-full bg-gradient-to-r from-pink-500 to-purple-600 text-white font-black shrink-0 shadow-sm animate-pulse">
          👗 꿈의 옷장 (보이스 스튜디오)
        </button>
        <button type="button" onclick="switchTab('tab-command')" class="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 shrink-0">
          🎛️ 사령부
        </button>
        <button type="button" onclick="forceBustMobileCache()" class="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-400/40 shrink-0">
          🔄 캐시강제갱신
        </button>
      </div>
"""

# Insert right after mobile top header
if '모바일 전용 인성학교 & 꿈의 옷장 원터치 다이렉트 칩' not in html:
    header_end = '</header>'
    pos = html.find(header_end)
    if pos != -1:
        html = html[:pos + len(header_end)] + '\n' + mob_quick_badge + html[pos + len(header_end):]
        print("Inserted mobile quick switcher badge under header!")

# 3. Ensure reload button in header also calls forceBustMobileCache
html = re.sub(
    r'<button\s+onclick="location\.reload\(\)"\s+class="([^"]*)"\s+title="새로고침">',
    r'<button onclick="forceBustMobileCache()" class="\1" title="캐시 강제 파괴 새로고침">',
    html
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print("dashboard/index.html updated with smart tab loader and mobile direct chips!")
