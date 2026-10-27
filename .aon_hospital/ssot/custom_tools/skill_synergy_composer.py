#!/usr/bin/env python3
# [AUTO-FORGED by RGON Creator Forge #50-鼎] 스킬 유전자 시너지 체인 합성기
import json, sys
def compose(skills, total=23):
    s = sorted({str(x) for x in skills}); chain = [a + " -> " + b for a, b in zip(s, s[1:])]
    return {"n": len(s), "chain": chain, "synergy": round(min(100.0, 100.0 * len(s) / total), 1)}
def _self_test():
    r = compose(["stomper-kill-list-gate", "autonomous-creator-forge", "stomper-kill-list-gate"]); assert r["n"] == 2 and len(r["chain"]) == 1
    return True
if __name__ == "__main__":
    print(json.dumps(compose(sys.argv[1:]) if len(sys.argv) > 1 else {"self_test": _self_test()}, ensure_ascii=False))
