# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OLD_VER = "v11.50-AON-TOKEN-EGOLITE-MASTER"
NEW_VER = "v11.51-AON-COMMANDER-TWIN"
OLD_AB = "R1~R51"
NEW_AB = "R1~R52"

PROTECTED = {
    "rgon_Numeric_Organ.py",
    "rgon_work_loop.py",
    "rgon_self_Reflection.py",
    "index_20260405_backup.html",
}

target_files = [
    "rgon_aon_auto_skill_evolver.py",
    "rgon_aon_cinematic_dispatch.py",
    "rgon_aon_desktop_playground.py",
    "rgon_aon_dialogue_engine.py",
    "rgon_aon_haesang_morph_avatar.py",
    "rgon_aon_hydro_cycle.py",
    "rgon_aon_iching_dao_oracle.py",
    "rgon_aon_iching_planner.py",
    "rgon_aon_impeccable_audit_shield.py",
    "rgon_aon_live_ui_healer.py",
    "rgon_aon_omni_insight_eye.py",
    "rgon_aon_omni_nexus.py",
    "rgon_aon_soul_brain.py",
    "rgon_aon_token_egolite_master.py",
    "rgon_aon_vibe3d_director.py",
    "rgon_aon_zeroclick_studio.py",
    "rgon_daily_cycle.py",
    "rgon_vascular_core.py",
    "rgon_white_blood_cell.py",
    "rgon_excretory_organ.py",
    "rgon_muse_delegator.py",
    "rgon_laptop_hands.py",
    "rgon_active_tickets.json",
    "rgon_circulation_report.json",
    "GLOSSARY.md",
]

for rel in target_files:
    if rel in PROTECTED:
        continue
    p = ROOT / rel
    if not p.exists():
        continue
    txt = p.read_text(encoding="utf-8")
    if OLD_VER in txt or OLD_AB in txt:
        txt = txt.replace(OLD_VER, NEW_VER)
        txt = txt.replace(OLD_AB, NEW_AB)
        p.write_text(txt, encoding="utf-8")
        print(f"Bumped: {rel}")

print("ALL TARGET FILES BUMPED TO STEP 52")
