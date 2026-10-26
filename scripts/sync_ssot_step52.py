# -*- coding: utf-8 -*-
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VERSION = "v11.51-AON-COMMANDER-TWIN"
ANTIBODY = "R1~R52"
SKILLS_COUNT = 48

# 1. Update CODE_MAP.md
p_cm = ROOT / "CODE_MAP.md"
if p_cm.exists():
    cm = p_cm.read_text(encoding="utf-8")
    cm = cm.replace("v11.50-AON-TOKEN-EGOLITE-MASTER", VERSION)
    cm = cm.replace("항체 R1~R51", f"항체 {ANTIBODY}")
    cm = cm.replace("정식 스킬 47개", f"정식 스킬 {SKILLS_COUNT}개")
    p_cm.write_text(cm, encoding="utf-8")
    print("CODE_MAP.md updated")

# 2. Update ANTIBODY_REGISTRY.md
p_ab = ROOT / "ANTIBODY_REGISTRY.md"
if p_ab.exists():
    ab = p_ab.read_text(encoding="utf-8")
    ab = ab.replace("v11.50-AON-TOKEN-EGOLITE-MASTER", VERSION)
    ab = ab.replace("R1~R51", ANTIBODY)
    if "## R52" not in ab:
        r52_entry = f"""
<!-- [RGON-ANTIBODY-R52] -->
## R52 — Step 52 · {VERSION} · 2026-10-26
- R52: 제28기관 아온 대표님 인지 디지털 트윈 & 노트북·스마트폰 무인 대행 사령관 (`rgon_aon_commander_twin.py`, 스킬 `aon-commander-digital-twin`, 주역 #01 중천건 · #30 중화리)
- 이상일 대표님의 7단계 일처리 DNA(The Sang-Il Command Loop) 의사결정 파이프라인 + 온디맨드 노트북 무인 대행 & 스마트폰 1-Tap 원터치 지휘 직결
- 전용 지휘 덱: `commander_twin_deck.html`
- 시냅스: S22 대화허브(/twin·/commander)→제28기관 대표님 디지털 트윈 사령관
- 범위: {ANTIBODY} · 정식 스킬 {SKILLS_COUNT}개
"""
        ab = ab.strip() + "\n" + r52_entry
    p_ab.write_text(ab, encoding="utf-8")
    print("ANTIBODY_REGISTRY.md updated")

# 3. Update snapshots: rgon_brain_snapshot.json in 3 locations
for rel in ["rgon_brain_snapshot.json", "dashboard/rgon_brain_snapshot.json", "docs/rgon_brain_snapshot.json"]:
    p = ROOT / rel
    if p.exists():
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            d["version"] = VERSION
            d["antibody_range"] = ANTIBODY
            d["antibody"] = ANTIBODY
            d["immune"] = ANTIBODY
            d["skills_count"] = SKILLS_COUNT
            d["skill_count"] = SKILLS_COUNT
            d["total_skills"] = SKILLS_COUNT
            d["updated_step"] = "Step 52"
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"{rel} updated")
        except Exception as e:
            print(f"Error updating {rel}: {e}")

# 4. Update rgon_immune_ledger.json
p_im = ROOT / "rgon_immune_ledger.json"
if p_im.exists():
    try:
        im = json.loads(p_im.read_text(encoding="utf-8"))
        im["version"] = VERSION
        im["antibody_range"] = ANTIBODY
        im["antibody"] = ANTIBODY
        im["immune"] = ANTIBODY
        im["skills_count"] = SKILLS_COUNT
        im["total_skills"] = SKILLS_COUNT
        p_im.write_text(json.dumps(im, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("rgon_immune_ledger.json updated")
    except Exception as e:
        print(f"Error updating immune ledger: {e}")

# 5. Update rgon_morning_brief.json in 3 locations
for rel in ["rgon_morning_brief.json", "dashboard/rgon_morning_brief.json", "docs/rgon_morning_brief.json"]:
    p = ROOT / rel
    if p.exists():
        try:
            mb = json.loads(p.read_text(encoding="utf-8"))
            mb["version"] = VERSION
            mb["antibody_range"] = ANTIBODY
            mb["antibody"] = ANTIBODY
            mb["immune"] = ANTIBODY
            mb["skills_count"] = SKILLS_COUNT
            mb["total_skills"] = SKILLS_COUNT
            p.write_text(json.dumps(mb, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"{rel} updated")
        except Exception as e:
            print(f"Error updating {rel}: {e}")

print("ALL SSOT METADATA SYNCHRONIZED FOR STEP 52")
