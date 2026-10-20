import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('dashboard/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove the premature </div> at line 863
premature_marker = '''      <!-- 2 Columns: Cloud Runs Monitor & Financial Constitution -->
</div>


    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">'''

correct_marker = '''      <!-- 2 Columns: Cloud Runs Monitor & Financial Constitution -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">'''

if premature_marker in html:
    html = html.replace(premature_marker, correct_marker, 1)
    print("SUCCESS: Removed premature </div> before Cloud Runs Monitor!")
else:
    print("Searching flexibly for premature </div>...")
    pat = re.compile(r'(<!-- 2 Columns: Cloud Runs Monitor & Financial Constitution -->)\s*</div>\s*(<div class="grid grid-cols-1 lg:grid-cols-12 gap-6">)', re.DOTALL)
    html, count = pat.subn(r'\1\n      \2', html)
    print(f"Flexible regex replaced count: {count}")

# 2. Verify and insert tab-vault panel right after tab-daughters
# Let's inspect where tab-daughters ends
tab_vault_panel = '''
    <!-- ══════════════════════════════════════════════════════════════
         TAB 5. 🧠 기억 금고 & 보안 설정 (Memory Vault & Zero-Leak)
    ══════════════════════════════════════════════════════════════ -->
    <div id="tab-vault" class="tab-pane hidden p-4 sm:p-6 lg:p-8 space-y-6">
      <div class="rounded-2xl bg-gradient-to-r from-slate-900/90 via-purple-950/40 to-slate-900/90 p-5 border border-purple-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <span class="text-3xl p-2 rounded-2xl bg-purple-600/30 text-purple-300 border border-purple-500/30">🧠</span>
          <div>
            <h3 class="text-base font-bold text-white flex items-center gap-2">
              기억 금고 & 보안 설정 <span class="text-xs font-mono text-purple-300">Memory Vault</span>
            </h3>
            <p class="text-xs text-slate-400">Zero-Leak 브라우저 로컬 스토리지 기반 보안 키 & 안실장 작업 큐 관리소</p>
          </div>
        </div>
        <button type="button" onclick="loadMemoryVault()" class="px-3 py-1.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs transition">
          🔄 새로고침
        </button>
      </div>

      <!-- 기억 목록 카드 -->
      <div class="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <h4 class="font-bold text-white text-sm flex items-center gap-2">
            <span>📚</span> 영구 기억 보관소 (Memory Vault Items)
          </h4>
          <span class="text-xs text-slate-400">memory_vault.json 연동</span>
        </div>
        <div id="vault-memories-list" class="space-y-2 text-xs">
          <div class="text-slate-400 text-center py-4">기억 금고 로드 중...</div>
        </div>
      </div>

      <!-- 보안 키 설정 카드 -->
      <div class="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <h4 class="font-bold text-white text-sm flex items-center gap-2">
            <span>🔐</span> Zero-Leak 보안 자격증명 설정
          </h4>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div>
            <label class="block font-semibold text-slate-300 mb-1">GitHub Personal Access Token</label>
            <input type="password" id="vault-gh-token" class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-white font-mono" placeholder="ghp_..." />
          </div>
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Gemini API Key</label>
            <input type="password" id="vault-gemini-key" class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-white font-mono" placeholder="AIzaSy..." />
          </div>
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Telegram Bot Token</label>
            <input type="password" id="vault-tg-token" class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-white font-mono" placeholder="8378111824:..." />
          </div>
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Telegram Chat ID</label>
            <input type="text" id="vault-tg-chat" class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-white font-mono" placeholder="8724874502" />
          </div>
        </div>
        <button type="button" onclick="saveVaultCredentials()" class="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs transition">
          보안 키 브라우저 로컬 저장
        </button>
      </div>
    </div>
'''

if 'id="tab-vault"' not in html:
    # insert before </main> or settings-modal
    target = '<!-- Settings Modal (Quick Edit) -->'
    pos = html.find(target)
    if pos != -1:
        html = html[:pos] + tab_vault_panel + '\n\n  ' + html[pos:]
        print("SUCCESS: Injected tab-vault panel into index.html!")

# 3. Enhance switchTab(tabId) to strictly hide all tabs and instant scroll to top (0, 0)
old_switch_tab = re.compile(r'function switchTab\(tabId\)\s*\{.*?document\.getElementById\(\'top-workspace-title\'\)\.textContent\s*=\s*titles\[tabId\]\s*\|\|\s*\'사령부\';\s*\}', re.DOTALL)

new_switch_tab = '''function switchTab(tabId) {
      // 1. 모든 탭을 완벽히 숨김
      document.querySelectorAll('.tab-pane').forEach(el => {
        el.classList.add('hidden');
        el.style.display = 'none';
      });

      // 2. 선택된 탭만 정확히 활성화
      const activePane = document.getElementById(tabId);
      if (activePane) {
        activePane.classList.remove('hidden');
        activePane.style.display = 'block';
      }

      // 3. 최상단으로 즉시 스크롤 (0.01초 만에 최상단 첫 화면 노출)
      window.scrollTo({ top: 0, behavior: 'instant' });

      // 4. 네비게이션 버튼 갱신
      document.querySelectorAll('.nav-tab-btn').forEach(btn => {
        btn.classList.remove('bg-emerald-500/10', 'text-emerald-300', 'border', 'border-emerald-500/30');
        btn.classList.add('text-slate-300');
      });
      const activeNav = document.getElementById('nav-' + tabId);
      if (activeNav) {
        activeNav.classList.add('bg-emerald-500/10', 'text-emerald-300', 'border', 'border-emerald-500/30');
        activeNav.classList.remove('text-slate-300');
      }

      // 모바일 탭 바 갱신
      document.querySelectorAll('.mob-tab-btn').forEach(btn => {
        btn.classList.replace('text-emerald-400', 'text-slate-400');
      });
      const activeMob = document.getElementById('mob-' + tabId);
      if (activeMob) activeMob.classList.replace('text-slate-400', 'text-emerald-400');

      const titles = {
        'tab-command': '🎛️ 1. 통합 관제 사령부',
        'tab-suno': '🎹 2. Suno & 비주얼 스튜디오',
        'tab-brain': '💬 3. AI 소통 & OSMU 개발실',
        'tab-daughters': '👨‍👧‍👧 4. 세 딸 인성 게임 연구소',
        'tab-vault': '🧠 5. 기억 금고 & 보안 설정'
      };
      const titleEl = document.getElementById('top-workspace-title');
      if (titleEl) titleEl.textContent = titles[tabId] || '사령부';
    }'''

if old_switch_tab.search(html):
    html = old_switch_tab.sub(new_switch_tab, html, count=1)
    print("SUCCESS: Enhanced switchTab with display:none and instant scroll!")
else:
    print("Warning: old_switch_tab regex not matched, checking manually...")

with open('dashboard/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("dashboard/index.html saved successfully!")
