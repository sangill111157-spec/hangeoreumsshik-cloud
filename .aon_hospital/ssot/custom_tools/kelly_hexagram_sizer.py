#!/usr/bin/env python3
# [AUTO-FORGED by RGON Creator Forge #50-鼎] Kelly x 주역 금고 보존 비중 (#60-수택절 절제 / #02-중지곤 수성)
import json, sys
def size(bull, bear, cap=25.0):
    bull, bear = float(bull), float(bear); p = bull / max(1e-9, bull + bear); edge = 2 * p - 1; bet = round(min(cap, max(0.0, edge) * 50), 1)
    return {"p_win": round(p, 3), "half_kelly_pct": bet, "vault_keep_pct": round(100 - bet, 1), "hexagram": "#60-수택절" if edge > 0 else "#02-중지곤"}
def _self_test():
    a, b = size(70, 30), size(30, 70)
    assert a["hexagram"] == "#60-수택절" and a["half_kelly_pct"] == 20.0 and a["vault_keep_pct"] == 80.0
    assert b["hexagram"] == "#02-중지곤" and b["vault_keep_pct"] == 100.0
    return True
if __name__ == "__main__":
    print(json.dumps(size(*sys.argv[1:3]) if len(sys.argv) > 2 else {"self_test": _self_test()}, ensure_ascii=False))
