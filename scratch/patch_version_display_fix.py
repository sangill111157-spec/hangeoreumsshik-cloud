import re

# 1. Update run_dashboard.py
run_path = 'run_dashboard.py'
with open(run_path, 'r', encoding='utf-8') as f:
    run_code = f.read()

run_code = run_code.replace('"version": "v3.1-OTA"', '"version": "v3.3-Minimal"')
with open(run_path, 'w', encoding='utf-8') as f:
    f.write(run_code)
print("Updated run_dashboard.py version to v3.3-Minimal!")


# 2. Update dashboard/index.html
dash_path = 'dashboard/index.html'
with open(dash_path, 'r', encoding='utf-8') as f:
    dash_html = f.read()

# Replace hardcoded v3.1 Auto-Sync in header
dash_html = dash_html.replace(
    '<span id="ota-version-text">v3.1 Auto-Sync</span>',
    '<span id="ota-version-text" class="font-bold text-amber-300">v3.3 Minimal [보이스스튜디오]</span>'
)

# Update initOtaHotReload text formatting
dash_html = re.sub(
    r"vBadge\.textContent\s*=\s*`\$\{data\.version\s*\|\|\s*'v3\.1'\}\s*\[\$\{data\.git_commit\s*\|\|\s*'Auto'\}\]`;",
    "vBadge.textContent = `${data.version || 'v3.3 Minimal'} [보이스스튜디오]`;",
    dash_html
)

# Insert a prominent persistent quick-jump banner right under the top header
# Visible in BOTH mobile and desktop, so whatever tab user is currently viewing, they see the direct button to Dream Closet!
persistent_banner = '''
    <!-- 👗🔥 [전 화면 공통 영구 노출] 꿈의 옷장 & 5대 보이스 스튜디오 직통 배너 -->
    <div class="px-4 py-2 bg-gradient-to-r from-purple-950 via-slate-900 to-amber-950 border-b border-amber-500/40 flex items-center justify-between gap-3 shadow-lg z-30">
      <div class="flex items-center gap-2 overflow-hidden">
        <span class="text-xl shrink-0 p-1 rounded-lg bg-amber-400 text-slate-950 font-black animate-pulse">👗</span>
        <div class="truncate">
          <span class="text-xs sm:text-sm font-black text-white">〈한걸음씩 상생나눔 제1호: 꿈의 옷장 & 5대 보이스 스튜디오〉</span>
          <span class="hidden sm:inline-block text-[11px] text-amber-300/90 ml-2 font-medium">실제 청담 디자이너·하이틴 언니 목소리 탑재!</span>
        </div>
      </div>
      <button type="button" onclick="switchTab('tab-daughters')" class="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-amber-400 to-pink-500 hover:from-amber-300 hover:to-pink-400 text-slate-950 font-black text-xs shrink-0 shadow-md shadow-amber-500/20 transition active:scale-95 flex items-center gap-1.5">
        <span>지금 바로 열기</span>
        <span>➔</span>
      </button>
    </div>
'''

if '꿈의 옷장 & 5대 보이스 스튜디오 직통 배너' not in dash_html:
    # insert right after </header>
    h_pos = dash_html.find('</header>')
    if h_pos != -1:
        dash_html = dash_html[:h_pos + len('</header>')] + '\n' + persistent_banner + dash_html[h_pos + len('</header>'):]
        print("Injected persistent banner right under </header> in dashboard/index.html!")

with open(dash_path, 'w', encoding='utf-8') as f:
    f.write(dash_html)

print("dashboard/index.html updated successfully!")
