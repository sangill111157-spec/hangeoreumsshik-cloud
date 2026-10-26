import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

court_card_index = """        <a 
          id="btn-goto-inspector-court"
          href="rgon_inspector_general_court.html"
          class="p-3 sm:p-3.5 rounded-xl bg-gradient-to-r from-amber-950/90 via-yellow-950/80 to-slate-950/90 hover:opacity-95 text-white font-bold text-xs shadow-lg border border-amber-400/50 transition flex items-center justify-between gap-2.5 active:scale-98">
          <div class="flex items-center gap-2.5">
            <span class="text-xl">⚖️</span>
            <div class="text-left">
              <div class="text-amber-200 font-extrabold">독립 검수총장 & 8대 기관 100% 출하 관문 ➔</div>
              <div class="text-[10.5px] text-slate-300">기관장 셀프채점 금지 · 8대 전담 검수장 12대 헌장 · 3중 직인 봉인</div>
            </div>
          </div>
          <span class="text-amber-300 font-mono text-xs">GATE</span>
        </a>"""

# 1. Update index.html (root, dashboard, docs)
for base in ['', 'dashboard/', 'docs/']:
    p = ROOT / f"{base}index.html"
    if p.exists():
        content = p.read_text(encoding="utf-8")
        if 'id="btn-goto-inspector-court"' not in content:
            target = 'id="btn-goto-button-bot"'
            idx = content.find(target)
            if idx != -1:
                end_a = content.find('</a>', idx) + 4
                new_content = content[:end_a] + '\n' + court_card_index + content[end_a:]
                p.write_text(new_content, encoding="utf-8")
                print(f"Added court card to {p}")

# 2. Update nav links in other main html files
for html_name in ["commander_twin_deck.html", "commander_assets_synergy_hub.html", "rgon_button_bot_command_center.html"]:
    for base in ['', 'dashboard/', 'docs/']:
        p = ROOT / f"{base}{html_name}"
        if p.exists():
            content = p.read_text(encoding="utf-8")
            if 'rgon_inspector_general_court.html' not in content:
                # find rgon_button_bot_command_center.html link
                target = 'href="rgon_button_bot_command_center.html"'
                idx = content.find(target)
                if idx != -1:
                    end_a = content.find('</a>', idx) + 4
                    repl = '\n      <span style="color:#475569">·</span>\n      <a href="rgon_inspector_general_court.html" class="nav-link">⚖️ 독립 검수총장 & 8대 기관 관문</a>'
                    new_content = content[:end_a] + repl + content[end_a:]
                    p.write_text(new_content, encoding="utf-8")
                    print(f"Added court nav link to {p}")

print("Navigation update for inspector court complete.")
