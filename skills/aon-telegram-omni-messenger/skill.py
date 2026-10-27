# -*- coding: utf-8 -*-
"""
[SKILL-52: AON-TELEGRAM-OMNI-MESSENGER]
제32기관 아온 듀얼 텔레그램·카톡형 실시간 양방향 메신저 연동 스킬
"""

import os
import sys
import json
from pathlib import Path

SKILL_NAME = "aon_telegram_omni_messenger"
SKILL_ID = 52
VERSION = "v11.55-AON-TELEGRAM-MESSENGER"
ANTIBODY = "R56_TELEGRAM_KAKAO_BIDIRECTIONAL_LIVE_MESSENGER_LOCK"


def execute(action: str = "status", **kwargs):
    import rgon_aon_telegram_omni_messenger as engine
    if action == "status":
        cfg = engine.load_dual_telegram_config()
        return {
            'skill': SKILL_NAME,
            'id': SKILL_ID,
            'version': VERSION,
            'bot1': cfg['bot1']['username'],
            'bot2': cfg['bot2']['username'],
            'chat_id_active': bool(cfg['chat_id'])
        }
    elif action == "send":
        msg = kwargs.get('msg', '테스트 지시')
        bot = kwargs.get('bot', 'both')
        entry, results = engine.dispatch_dual_telegram(msg, target=bot)
        return {'entry': entry, 'results': results}
    elif action == "self_test":
        return engine.run_self_test()
    return {'error': f"Unknown action: {action}"}


if __name__ == '__main__':
    print(execute("status"))
