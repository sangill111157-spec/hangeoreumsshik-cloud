#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""skill.py — 정식 스킬 #48 aon-commander-digital-twin 실행 및 자가진단 진입점
Step 52 · v11.51-AON-COMMANDER-TWIN · 항체 R1~R52
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rgon_aon_commander_twin import (
    get_commander_twin,
    self_test,
    VERSION,
    ANTIBODY_RANGE,
    SKILL_COUNT,
    ORGAN_NAME,
)


def run_skill(query: str = "") -> dict:
    twin = get_commander_twin()
    if not query:
        return twin.laptop_only_autopilot()
    return twin.smartphone_pocket_dispatch(query)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test(verbose=True))
    res = run_skill(" ".join(sys.argv[1:]))
    print(f"[{ORGAN_NAME} · {VERSION}]")
    print(f"결과: {res.get('stages', [{}])[4].get('verdict')}")
    sys.exit(0)
