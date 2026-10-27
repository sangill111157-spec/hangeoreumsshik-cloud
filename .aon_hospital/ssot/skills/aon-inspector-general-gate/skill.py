#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""skills/aon-inspector-general-gate/skill.py — 정식 스킬 #50 실행 어댑터"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import rgon_aon_inspector_general_gate as ig

def run_skill(*args, **kwargs):
    return ig.self_test(verbose=False)

if __name__ == "__main__":
    sys.exit(0 if ig.self_test(verbose=True) else 1)
