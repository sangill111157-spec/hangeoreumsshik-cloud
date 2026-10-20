import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('dashboard/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Locate tab-vault currently outside </main>
vault_start = html.find('<!-- ══════════════════════════════════════════════════════════════\n         TAB 5. 🧠 기억 금고 & 보안 설정')
if vault_start == -1:
    vault_start = html.find('<div id="tab-vault"')

# Extract tab-vault HTML
vault_end = html.find('</div>\n    </div>', vault_start)
if vault_end != -1:
    vault_end += len('</div>\n    </div>')
else:
    vault_end = html.find('<!-- Settings Modal', vault_start)
    vault_end = html.rfind('</div>', vault_start, vault_end) + len('</div>')

vault_block = html[vault_start:vault_end].strip()

# Remove vault_block from its current location
html = html[:vault_start] + html[vault_end:]

# Now find </main>
main_end_pos = html.find('</main>')

# Insert tab-vault right before </main>, with proper closing </div>
tab_vault_clean = f'''
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

html = html[:main_end_pos] + '\n' + tab_vault_clean + '\n  ' + html[main_end_pos:]

with open('dashboard/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved aligned dashboard/index.html!")
