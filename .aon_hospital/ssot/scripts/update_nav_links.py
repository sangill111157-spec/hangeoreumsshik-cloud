import os

btn_bot_card_index = """        <a 
          id="btn-goto-button-bot"
          href="rgon_button_bot_command_center.html"
          class="p-3 sm:p-3.5 rounded-xl bg-gradient-to-r from-emerald-900/80 via-teal-900/80 to-slate-950/80 hover:opacity-95 text-white font-bold text-xs shadow-lg border border-emerald-400/40 transition flex items-center justify-between gap-2.5 active:scale-98">
          <div class="flex items-center gap-2.5">
            <span class="text-xl">🤖</span>
            <div class="text-left">
              <div class="text-emerald-200 font-extrabold">전 페이지·버튼 자동화 봇 사령부 ➔</div>
              <div class="text-[10.5px] text-slate-300">WebMCP Stagehand · 5대 황금 체인 릴레이 · 무토큰 0.001초</div>
            </div>
          </div>
          <span class="text-emerald-300 font-mono text-xs">BOT</span>
        </a>"""

for base in ['', 'dashboard/', 'docs/']:
    idx_path = f"{base}index.html" if base else 'index.html'
    if os.path.exists(idx_path):
        with open(idx_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'id="btn-goto-button-bot"' not in content:
            target = 'id="btn-goto-synergy-hub"'
            idx = content.find(target)
            if idx != -1:
                end_a = content.find('</a>', idx) + 4
                new_content = content[:end_a] + '\n' + btn_bot_card_index + content[end_a:]
                with open(idx_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Added button bot card to {idx_path}")

for base in ['', 'dashboard/', 'docs/']:
    twin_path = f"{base}commander_twin_deck.html" if base else 'commander_twin_deck.html'
    if os.path.exists(twin_path):
        with open(twin_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'rgon_button_bot_command_center.html' not in content:
            target = '<a href="commander_assets_synergy_hub.html" class="nav-link">💎 전 자산 통합 관제 허브</a>'
            repl = target + '\n      <span style="color:#475569">·</span>\n      <a href="rgon_button_bot_command_center.html" class="nav-link">🤖 전 페이지·버튼 자동화 봇 사령부</a>'
            new_content = content.replace(target, repl)
            with open(twin_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Added nav link to {twin_path}")

for base in ['', 'dashboard/', 'docs/']:
    hub_path = f"{base}commander_assets_synergy_hub.html" if base else 'commander_assets_synergy_hub.html'
    if os.path.exists(hub_path):
        with open(hub_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'rgon_button_bot_command_center.html' not in content:
            target = '<a href="commander_twin_deck.html" class="nav-link">👑 대표님 인지 디지털 트윈 지휘 덱</a>'
            repl = target + '\n      <span style="color:#475569">·</span>\n      <a href="rgon_button_bot_command_center.html" class="nav-link">🤖 전 페이지·버튼 자동화 봇 사령부</a>'
            new_content = content.replace(target, repl)
            with open(hub_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Added nav link to {hub_path}")

print("Navigation links updated successfully.")
