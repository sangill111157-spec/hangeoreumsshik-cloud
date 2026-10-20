import os
import re

dept_dir = r"c:\Users\sangi\Downloads\shin-agent\dashboard\departments"
files = [
    "dept_closet.html",
    "dept_connect_ai.html",
    "dept_media.html",
    "dept_education.html",
    "dept_treasury.html",
    "dept_vault.html"
]

header_btn = '''      <a href="../rgon_alpha_chat.html" class="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 via-yellow-500 to-amber-600 hover:from-amber-400 hover:to-yellow-400 text-slate-950 font-black text-xs transition flex items-center justify-center gap-1.5 shadow-lg shadow-amber-500/25 active:scale-95">
        <span>💬 르곤-알파 1:1 독대실 ➔</span>
      </a>\n'''

deck_chip = '''          <a href="../rgon_alpha_chat.html" class="px-2.5 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30 transition flex items-center gap-1 font-bold text-[10px] sm:text-[11px]">
            <span>💬 르곤-알파 1:1 독대실</span>
          </a>\n'''

for f in files:
    path = os.path.join(dept_dir, f)
    if not os.path.exists(path):
        print(f"Skipping {f} - not found")
        continue
    with open(path, "r", encoding="utf-8") as fp:
        content = fp.read()
    
    # Check if already added
    if "💬 르곤-알파 1:1 독대실" in content:
        print(f"Already added in {f}")
        continue
    
    # 1. Add before 본관 복귀 button
    # Pattern: <a href="/?v=... class="... flex items-center justify-center gap-1.5 ...">
    #          <span>🏛️ 청와대 본관 복귀 ➔</span>
    target_pattern = r'(<a\s+href=[\'"][^\'"]*tab=command[^\'"]*[\'"][^>]*>[\s\S]*?청와대\s*본관\s*복귀[\s\S]*?</a>)'
    m = re.search(target_pattern, content)
    if m:
        content = content[:m.start()] + header_btn + content[m.start():]
    else:
        # Fallback: find any link with 청와대 본관 복귀
        target_pattern2 = r'(<a\s+[^>]*href=[\'"][^\'"]*[\'"][^>]*>[\s\S]*?본관\s*복귀[\s\S]*?</a>)'
        m2 = re.search(target_pattern2, content)
        if m2:
            content = content[:m2.start()] + header_btn + content[m2.start():]
        else:
            print(f"Warning: could not find return button in {f}")
            
    # 2. Add to dept-sub-agent-deck if exists
    if 'id="dept-sub-agent-deck"' in content:
        # Find the sub agent status badge area
        sub_pattern = r'(<div class="flex flex-wrap items-center gap-[^"]*text-\[[^"]*\]">)'
        m_deck = re.search(sub_pattern, content)
        if m_deck:
            content = content[:m_deck.end()] + "\n" + deck_chip + content[m_deck.end():]
        else:
            print(f"Deck badge area pattern not matched in {f}")
            
    with open(path, "w", encoding="utf-8") as fp:
        fp.write(content)
    print(f"Successfully updated {f}")

print("ALL_DEPTS_UPDATED_WITH_ALPHA_CHAT_LINKS")
