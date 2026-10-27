#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 1. Update SKILL_INDEX.json
idx_path = ROOT / "skills" / "SKILL_INDEX.json"
idx = json.loads(idx_path.read_text(encoding="utf-8"))

idx["version"] = "v11.53-AON-INSPECTOR-GENERAL"
idx["antibody"] = "R1~R54"
idx["antibody_range"] = "R1~R54"

new_skill = {
    "slug": "aon-inspector-general-gate",
    "id": "aon-inspector-general-gate",
    "name": "아온 7대 방침 기관장 분신단 & 독립 검수담당 총장·기관별 특화 검수장 100% 출하 봉인 관문 시스템",
    "category": "governance-inspection",
    "hexagram_tag": "#21-噬嗑 · #15-謙",
    "source_url": "rgon_aon_inspector_general_gate.py",
    "origin": "organ-30",
    "path": "skills/aon-inspector-general-gate/SKILL.md"
}

# check if already exists
exists = False
for s in idx.get("skills", []):
    if s.get("slug") == "aon-inspector-general-gate":
        exists = True
        break

if not exists:
    idx["skills"].append(new_skill)

total = len(idx["skills"])
idx["count"] = total
idx["total"] = total
idx["skill_count"] = total
idx["total_skills"] = total

idx_path.write_text(json.dumps(idx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Updated SKILL_INDEX.json: {total} skills")

# 2. Update SKILL_INDEX.md
md_path = ROOT / "skills" / "SKILL_INDEX.md"
md_text = md_path.read_text(encoding="utf-8")
if "aon-inspector-general-gate" not in md_text:
    entry = f"\n- **`aon-inspector-general-gate`** (50번): 아온 7대 방침 기관장 분신단 & 독립 검수담당 총장 100% 출하 봉인 관문 시스템 (`skills/aon-inspector-general-gate/SKILL.md`)\n"
    md_text += entry
    md_path.write_text(md_text, encoding="utf-8")
    print("Updated SKILL_INDEX.md with skill 50")

# 3. Verify triplet
sk_dir = ROOT / "skills"
dirs = sum(1 for d in sk_dir.iterdir() if d.is_dir() and ((d / "SKILL.md").exists() or (d / "skill.md").exists()))
slugs = [s["slug"] for s in idx["skills"]]
md_count = sum(1 for s in slugs if s in md_path.read_text(encoding="utf-8"))
print(f"Triplet Check: dirs={dirs}, json={len(slugs)}, md={md_count}")
