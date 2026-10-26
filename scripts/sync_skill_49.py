# -*- coding: utf-8 -*-
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 1. Update SKILL_INDEX.json
p_json = ROOT / "skills" / "SKILL_INDEX.json"
data = json.loads(p_json.read_text(encoding="utf-8"))

data["version"] = "v11.52-AON-PAGE-BUTTON-BOT"
data["antibody"] = "R1~R53"
data["antibodies"] = "R1~R53"
data["antibody_range"] = "R1~R53"
data["immune"] = "R1~R53"
data["count"] = 49
data["total"] = 49
data["skill_count"] = 49
data["total_skills"] = 49

# Check if skill 49 already exists
has_49 = any(s.get("slug") in ["aon-page-button-bot-engine", "aon_page_button_bot_engine"] for s in data["skills"])
if not has_49:
    data["skills"].append({
        "index": 49,
        "slug": "aon-page-button-bot-engine",
        "name": "aon-page-button-bot-engine",
        "version": "v11.52-AON-PAGE-BUTTON-BOT",
        "antibody": "R53",
        "organ": "rgon_aon_page_button_bot_engine.py",
        "title": "아온 WebMCP & Stagehand/n8n-Lite 전 페이지·전 버튼 자율 자동화 봇 전환 엔진",
        "hexagrams": [
            "#16",
            "#60"
        ],
        "path": "skills/aon-page-button-bot-engine/SKILL.md",
        "description": "WebMCP/Stagehand 전 페이지·전 버튼 결정론적 자동화 봇 전환 + n8n-Lite 5대 표준 체인 오케스트레이터 및 SHA-256 감사 영수증"
    })

p_json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("SKILL_INDEX.json updated to 49 skills")

# 2. Update SKILL_INDEX.md
p_md = ROOT / "skills" / "SKILL_INDEX.md"
md_text = p_md.read_text(encoding="utf-8")

if "aon-page-button-bot-engine" not in md_text:
    new_entry = """
<!-- [RGON-SKILL-49] -->
## 49. `aon-page-button-bot-engine` (R53 · v11.52-AON-PAGE-BUTTON-BOT)
- 경로: `skills/aon-page-button-bot-engine/SKILL.md`
- 기관: 제29기관 아온 WebMCP & Stagehand/n8n-Lite 전 페이지·전 버튼 자율 자동화 봇 전환 엔진 (`rgon_aon_page_button_bot_engine.py`)
- 핵심: WebMCP/Stagehand 전 페이지·전 버튼 결정론적 자동화 봇 전환 + n8n-Lite 5대 표준 체인 오케스트레이터 및 SHA-256 감사 영수증
"""
    md_text = md_text.strip() + "\n" + new_entry
    p_md.write_text(md_text, encoding="utf-8")
    print("SKILL_INDEX.md updated with skill 49")
else:
    print("SKILL_INDEX.md already contains skill 49")
