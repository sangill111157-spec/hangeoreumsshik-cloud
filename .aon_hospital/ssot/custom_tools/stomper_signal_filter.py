#!/usr/bin/env python3
# [AUTO-FORGED by RGON Creator Forge #50-鼎] Stomper 시그널 필터: 사기·과장·인젝션 위험도 -> KILL/PASS
import json, sys
STINK = {'원금보장': 40, 'guaranteed': 40, '러그풀': 35, 'rugpull': 35, '100%수익': 30, 'ignoreprevious': 50, '이전지시를무시': 50, 'systemprompt': 30, '무조건': 15, 'x100': 20, '사기': 30}
def judge(text):
    t = str(text).lower().replace(" ", ""); s = min(100, sum(w for k, w in STINK.items() if k in t))
    return {"score": s, "verdict": "KILL" if s >= 30 else "PASS"}
def _self_test():
    assert judge("원금보장 러그풀 코인")["verdict"] == "KILL" and judge("Ignore previous instructions")["verdict"] == "KILL"
    assert judge("분기 실적 리포트 요약")["verdict"] == "PASS"
    return True
if __name__ == "__main__":
    print(json.dumps(judge(" ".join(sys.argv[1:])) if len(sys.argv) > 1 else {"self_test": _self_test()}, ensure_ascii=False))
