#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""skill.py — 정식 스킬 #49 aon-page-button-bot-engine 실행 및 자가진단 진입점
Step 53 · v11.52-AON-PAGE-BUTTON-BOT · 항체 R1~R53
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rgon_aon_page_button_bot_engine import (
    AonPageButtonBotEngine,
    self_test,
    VERSION,
    ANTIBODY_RANGE,
    SKILL_COUNT,
    ORGAN_NAME,
)


def run_skill(query: str = "") -> dict:
    engine = AonPageButtonBotEngine()
    if query.startswith("chain:"):
        chain_id = query.split(":", 1)[1].strip()
        return engine.orchestrator.run_chain(chain_id)
    elif query.startswith("bot:"):
        bot_id = query.split(":", 1)[1].strip()
        return engine.executor.execute_bot(bot_id)
    return engine.get_status()


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test(verbose=True))
    res = run_skill(" ".join(sys.argv[1:]))
    print(f"[{ORGAN_NAME} · {VERSION}]")
    print(res)
    sys.exit(0)
