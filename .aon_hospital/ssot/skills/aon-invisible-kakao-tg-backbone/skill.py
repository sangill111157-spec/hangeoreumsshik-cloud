# -*- coding: utf-8 -*-
"""
[SKILL-53: AON-INVISIBLE-KAKAO-TG-BACKBONE]
제33기관 아온 인비저블 텔레그램 백본 & 카카오톡형 올인원 만능 대화창 스킬
"""

import os
import sys
import json
from pathlib import Path

SKILL_NAME = "aon_invisible_kakao_tg_backbone"
SKILL_ID = 53
VERSION = "v11.56-AON-INVISIBLE-KAKAO-TG"
ANTIBODY = "R57_INVISIBLE_TELEGRAM_KAKAO_ALL_IN_ONE_CHAT_LOCK"


def execute(action: str = "status", **kwargs):
    import rgon_aon_invisible_kakao_tg_backbone as engine
    if action == "status":
        cfg = engine.load_triple_telegram_config()
        return {
            'skill': SKILL_NAME,
            'id': SKILL_ID,
            'version': VERSION,
            'channels': list(engine.CHANNELS.keys()),
            'bot1': cfg['bot1']['username'],
            'bot2': cfg['bot2']['username'],
            'bot3': cfg['bot3']['username'],
            'nvda_dashboard_exists': os.path.exists(cfg['nvda_dashboard_path'])
        }
    elif action == "send":
        msg = kwargs.get('msg', '지시')
        channel = kwargs.get('channel', 'ALL')
        mgr = engine.InvisibleBackboneManager()
        return mgr.dispatch_invisible(msg, channel=channel)
    elif action == "self_test":
        return engine.run_self_test()
    return {'error': f"Unknown action: {action}"}


if __name__ == '__main__':
    print(execute("status"))
