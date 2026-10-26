import os, sys, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(ROOT))

VERSION = "v11.52-AON-PAGE-BUTTON-BOT"
ANTIBODY_RANGE = "R1~R53"
SKILL_COUNT = 49

# 1. rgon_aon_page_button_bot_engine.py에 load_or_compile 추가
bot_engine_p = ROOT / "rgon_aon_page_button_bot_engine.py"
bet = bot_engine_p.read_text(encoding="utf-8")
if "def load_or_compile" not in bet:
    insert_code = '''    @classmethod
    def load_or_compile(cls):
        catalog_file = ROOT / "rgon_aon_bot_catalog.json"
        if catalog_file.exists():
            try:
                return json.loads(catalog_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        compiler = cls()
        return compiler.compile_all()
'''
    idx = bet.find("def compile_all(self)")
    if idx != -1:
        bet = bet[:idx] + insert_code + "\n    " + bet[idx:]
        bot_engine_p.write_text(bet, encoding="utf-8")
        print("Added load_or_compile to rgon_aon_page_button_bot_engine.py")

# 2. rgon_aon_dialogue_engine.py 버전 & 항체 갱신
dlg_p = ROOT / "rgon_aon_dialogue_engine.py"
dt = dlg_p.read_text(encoding="utf-8")
dt = re.sub(r'R40_VERSION\s*=\s*"[^"]+"', f'R40_VERSION = "{VERSION}"', dt)
dt = re.sub(r'R40_ANTIBODY\s*=\s*"[^"]+"', f'R40_ANTIBODY = "{ANTIBODY_RANGE}"', dt)
dlg_p.write_text(dt, encoding="utf-8")
print("Updated R40_VERSION and R40_ANTIBODY in rgon_aon_dialogue_engine.py")

# 3. rgon_aon_soul_brain.py 버전 갱신
soul_p = ROOT / "rgon_aon_soul_brain.py"
st = soul_p.read_text(encoding="utf-8")
st = re.sub(r'_R40_SB_VER\s*=\s*"[^"]+"', f'_R40_SB_VER = "{VERSION}"', st)
soul_p.write_text(st, encoding="utf-8")
print("Updated _R40_SB_VER in rgon_aon_soul_brain.py")

# 4. ANTIBODY_REGISTRY.md에 R1~R53 명시
ab_p = ROOT / "ANTIBODY_REGISTRY.md"
abt = ab_p.read_text(encoding="utf-8")
if "R1~R53" not in abt:
    abt = abt.replace(
        "### 🛡️ R53: WebMCP Stagehand 전 페이지·전 버튼 자동화 봇 및 n8n-Lite 체인 오케스트레이션 항체",
        f"<!-- [RGON-ANTIBODY-R53] -->\n## R53 — Step 53 · {VERSION} · 2026-10-27\n- **범위**: {ANTIBODY_RANGE} · 정식 스킬 {SKILL_COUNT}개\n### 🛡️ R53: WebMCP Stagehand 전 페이지·전 버튼 자동화 봇 및 n8n-Lite 체인 오케스트레이션 항체"
    )
    ab_p.write_text(abt, encoding="utf-8")
    print("Updated ANTIBODY_REGISTRY.md with R1~R53 and header.")

print("All pinpoint fixes applied.")
