# -*- coding: utf-8 -*-
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 1. Update SKILL_INDEX.json
p_json = ROOT / "skills" / "SKILL_INDEX.json"
data = json.loads(p_json.read_text(encoding="utf-8"))

data["version"] = "v11.51-AON-COMMANDER-TWIN"
data["antibody"] = "R1~R52"
data["antibodies"] = "R1~R52"
data["antibody_range"] = "R1~R52"
data["immune"] = "R1~R52"
data["count"] = 48
data["total"] = 48
data["skill_count"] = 48
data["total_skills"] = 48

# Check if skill 48 already exists
has_48 = any(s.get("slug") == "aon_commander_digital_twin" for s in data["skills"])
if not has_48:
    data["skills"].append({
        "index": 48,
        "slug": "aon_commander_digital_twin",
        "name": "aon_commander_digital_twin",
        "version": "v11.51-AON-COMMANDER-TWIN",
        "antibody": "R52",
        "organ": "rgon_aon_commander_twin.py",
        "title": "아온 대표님 인지 디지털 트윈 & 노트북·스마트폰 무인 대행 사령관",
        "hexagrams": [
            "#01",
            "#30"
        ],
        "path": "skills/aon_commander_digital_twin/SKILL.md",
        "description": "이상일 대표님의 7단계 일처리 DNA(The Sang-Il Command Loop) 파이프라인 + 노트북 단독 무인 대행 & 스마트폰 1-Tap 1초 지휘 직결"
    })

p_json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("SKILL_INDEX.json updated to 48 skills")

# 2. Update SKILL_INDEX.md
p_md = ROOT / "skills" / "SKILL_INDEX.md"
md_text = p_md.read_text(encoding="utf-8")

if "aon_commander_digital_twin" not in md_text:
    new_entry = """
<!-- [RGON-SKILL-48] -->
## 48. `aon_commander_digital_twin` (R52 · v11.51-AON-COMMANDER-TWIN)
- 경로: `skills/aon_commander_digital_twin/SKILL.md`
- 기관: 제28기관 아온 대표님 인지 디지털 트윈 & 노트북·스마트폰 무인 대행 사령관 (`rgon_aon_commander_twin.py`)
- 핵심: 이상일 대표님의 7단계 일처리 DNA(The Sang-Il Command Loop) 파이프라인 + 노트북 단독 무인 대행 & 스마트폰 1-Tap 1초 지휘 직결
"""
    md_text = md_text.strip() + "\n" + new_entry
    p_md.write_text(md_text, encoding="utf-8")
    print("SKILL_INDEX.md updated with skill 48")
else:
    print("SKILL_INDEX.md already contains skill 48")

print("SKILL INDEX SYNC COMPLETE")
