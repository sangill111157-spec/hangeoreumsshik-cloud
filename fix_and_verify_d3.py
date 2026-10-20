# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Fix the duplicate block cleanly
target_clean = """        # 3. 구성 요소 리스트 생성 (라벨 대문자 정규화 및 NEUTRAL->HOLD 통일)
        def _norm_sig(sig) -> str:
            if not sig:
                return "HOLD"
            s = str(sig).upper()
            return "HOLD" if s in ["NEUTRAL", "NONE", "N/A"] else s

        components = [
            ComponentScore(
                name="5대 투자자",
                score=investor_score,
                signal=_norm_sig(investor_analysis.get("overall_signal")),
                confidence=investor_analysis.get("overall_confidence", 50),
                details={
                    "bull_count": investor_analysis.get("bull_count", 0),
                    "bear_count": investor_analysis.get("bear_count", 0)
                }
            ),
            ComponentScore(
                name="멀티전략",
                score=pod_score,
                signal=_norm_sig(pod_composite_signal if pod_composite_signal is not None else (
                    pod_signals[0].get("signal", "HOLD") if pod_signals else "HOLD"
                )),
                confidence=int(pod_score),
                details={"pod_count": len(pod_signals)}
            ),
            ComponentScore(
                name="기술적",
                score=tech_score,
                signal=_norm_sig(technical.get("overall_signal")),
                confidence=min(100, technical.get("confidence", 50)),
                details={
                    "trend": technical.get("trend", "NEUTRAL"),
                    "rsi": technical.get("rsi", {}).get("value", 50)
                }
            ),
            ComponentScore(
                name="AI 뉴스",
                score=news_score,
                signal=_norm_sig(llm_news.get("sentiment_label")),
                confidence=min(100, llm_news.get("total_news_analyzed", 0) * 5),
                details={"news_count": llm_news.get("total_news_analyzed", 0)}
            ),
            ComponentScore(
                name="기관/13F",
                score=inst_score,
                signal=_norm_sig("BUY" if inst_score >= 60 else "SELL" if inst_score <= 40 else "HOLD"),
                confidence=50,
                details={}
            ),
            ComponentScore(
                name="옵션 플로우",
                score=options_score,
                signal=_norm_sig(options_flow.get("options_signal")),
                confidence=int(options_score),
                details={"available": options_flow.get("available", False)}
            ),
            ComponentScore(
                name="다크풀",
                score=darkpool_score,
                signal=_norm_sig(darkpool.get("darkpool_signal")),
                confidence=int(darkpool_score),
                details={"available": darkpool.get("available", False)}
            )
        ]"""

# Replace from `components = [` to `        available_modules = [`
start_idx = code.find("# 3.")
if start_idx == -1:
    start_idx = code.find("components = [")
end_idx = code.find("# 4. 가용 모듈")
if end_idx == -1:
    end_idx = code.find("available_modules = [m for m in BASE_WEIGHTS.keys()")

new_code = code[:start_idx] + target_clean + "\n\n        # 4. 가용 모듈 식별 및 동적 가중치 재정규화\n        " + code[end_idx + len("# 4. 가용 모듈 식별 및 동적 가중치 재정규화\n        "):]
with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(new_code)

out_diff, _ = run_cmd('git diff app/services/master_signal.py')
print("--- git diff app/services/master_signal.py ---")
print(out_diff)

run_cmd('git add app/services/master_signal.py')
c_msg, _ = run_cmd('git commit --amend -m "fix(signal): normalize component signal labels to uppercase"')
print("Commit D-3 Amend Output:\n", c_msg)

# Re-run direct test
from app.services.master_signal import MasterSignalEngine
engine = MasterSignalEngine()

mock_data = {
    "investor_analysis": {"overall_signal": "buy", "overall_confidence": 70},
    "pod_signals": [{"signal": "buy", "confidence": 70}],
    "technical": {"overall_signal": "buy", "confidence": 75},
    "llm_news": {"sentiment_label": "NEUTRAL", "news_composite_score": 50, "total_news_analyzed": 5},
    "institutional": {"available": True},
    "options_flow": {"options_signal": "strong_buy", "options_composite_score": 70, "available": True},
    "darkpool": {"darkpool_signal": "sell", "darkpool_composite_score": 40, "available": True},
    "events": {},
    "correlation": {},
    "symbol": "NVDA"
}

res = engine.calculate_final_master_signal(**mock_data)
print("\n--- [Direct Engine D-3 In-Process Verification] ---")
print("master_score:", res.master_score)
print("raw_score   :", res.raw_score)
print("Components normalized signals:")
for c in res.components:
    print(f"  - {c.name:12s}: signal={c.signal:12s} is_upper={c.signal.isupper()} is_not_neutral={c.signal != 'NEUTRAL'}")

