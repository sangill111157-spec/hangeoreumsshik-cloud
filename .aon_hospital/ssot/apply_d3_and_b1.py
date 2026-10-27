# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time, urllib.request
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [D-3 PATCH] Normalize component signals to UPPERCASE & NEUTRAL->HOLD")
print("==================================================")
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_content = f.read()

# Helper function or inline normalization in ComponentScore block
old_block = """        # 3. 7개 컴포넌트 점수 리스트 생성
        components = [
            ComponentScore(
                name="5대 투자자",
                score=investor_score,
                signal=investor_analysis.get("overall_signal", "HOLD"),
                confidence=investor_analysis.get("overall_confidence", 50),
                details={
                    "bull_count": investor_analysis.get("bull_count", 0),
                    "bear_count": investor_analysis.get("bear_count", 0)
                }
            ),
            ComponentScore(
                name="멀티전략",
                score=pod_score,
                signal=pod_composite_signal if pod_composite_signal is not None else (
                    logger.warning("pod_composite_signal is None, falling back to pod_signals[0]") or (
                        pod_signals[0].get("signal", "HOLD") if pod_signals else "HOLD"
                    )
                ),
                confidence=int(pod_score),
                details={"pod_count": len(pod_signals)}
            ),
            ComponentScore(
                name="기술적",
                score=tech_score,
                signal=technical.get("overall_signal", "HOLD"),
                confidence=min(100, technical.get("confidence", 50)),
                details={
                    "trend": technical.get("trend", "NEUTRAL"),
                    "rsi": technical.get("rsi", {}).get("value", 50)
                }
            ),
            ComponentScore(
                name="AI 뉴스",
                score=news_score,
                signal=llm_news.get("sentiment_label", "HOLD"),
                confidence=min(100, llm_news.get("total_news_analyzed", 0) * 5),
                details={"news_count": llm_news.get("total_news_analyzed", 0)}
            ),
            ComponentScore(
                name="기관/13F",
                score=inst_score,
                signal="BUY" if inst_score >= 60 else "SELL" if inst_score <= 40 else "HOLD",
                confidence=50,
                details={}
            ),
            ComponentScore(
                name="옵션 플로우",
                score=options_score,
                signal=options_flow.get("options_signal", "HOLD"),
                confidence=int(options_score),
                details={"available": options_flow.get("available", False)}
            ),
            ComponentScore(
                name="다크풀",
                score=darkpool_score,
                signal=darkpool.get("darkpool_signal", "HOLD"),
                confidence=int(darkpool_score),
                details={"available": darkpool.get("available", False)}
            )
        ]"""

new_block = """        # 3. 7개 컴포넌트 점수 리스트 생성 (라벨 대문자 정규화 및 NEUTRAL->HOLD 통일)
        def _norm_sig(sig: Optional[str]) -> str:
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
                    logger.warning("pod_composite_signal is None, falling back to pod_signals[0]") or (
                        pod_signals[0].get("signal", "HOLD") if pod_signals else "HOLD"
                    )
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

assert old_block in ms_content, "old_block not found in master_signal.py"
new_ms_content = ms_content.replace(old_block, new_block)
with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(new_ms_content)

out_diff, _ = run_cmd('git diff app/services/master_signal.py')
print("--- git diff app/services/master_signal.py ---")
print(out_diff)

run_cmd('git add app/services/master_signal.py')
c_msg, _ = run_cmd('git commit -m "fix(signal): normalize component signal labels to uppercase"')
print("Commit D-3 Output:\n", c_msg)

print("\n==================================================")
print("2. [D-3 VERIFICATION] /api/stock/NVDA/signal live check")
print("==================================================")
try:
    req = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/signal", headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        res_json = json.loads(resp.read().decode('utf-8'))
        print("Live master_score:", res_json.get("master_score"))
        print("Live raw_score   :", res_json.get("raw_score"))
        print("Components signals:")
        for c in res_json.get("components", []):
            print(f"  - {c.get('name'):12s}: signal={c.get('signal'):12s} (is_upper={c.get('signal').isupper()})")
except Exception as e:
    print("Verification Error:", e)

print("\n==================================================")
print("3. [B-1 RE-PATCH] App.tsx conditional gauge rendering & confidence null-safe")
print("==================================================")
app_path = os.path.join(frontend_dir, r'src\App.tsx')
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

# Line 1942 & Gauge conditional rendering
# Replace gauge area to conditionally render '—' when master_score == null
# Also line 1002
old_gauge_area = """  // Calculate gauge percentage (0-100)
  const gaugePercent = data?.master_score ?? 50;

  return (
    <div className="space-y-6">
      {/* Main Signal Card */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl border border-gray-700/50 p-6">
        <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
          {/* Signal Badge & Score */}
          <div className="flex items-center gap-6">
            <div className="relative w-32 h-32">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  className="text-gray-700"
                  strokeWidth="10"
                  stroke="currentColor"
                  fill="transparent"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  className={gaugeColor}
                  strokeWidth="10"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="transparent"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-4xl font-bold text-white">{data?.master_score != null ? data.master_score.toFixed(0) : '—'}</span>
                <span className="text-xs text-gray-400">/100</span>
              </div>
            </div>"""

new_gauge_area = """  // Calculate gauge percentage (0-100) - null safe, no 50 default fallback
  const hasMasterScore = data?.master_score != null;
  const gaugePercent = hasMasterScore ? data.master_score : 0;

  return (
    <div className="space-y-6">
      {/* Main Signal Card */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl border border-gray-700/50 p-6">
        <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
          {/* Signal Badge & Score */}
          <div className="flex items-center gap-6">
            <div className="relative w-32 h-32">
              {hasMasterScore ? (
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    className="text-gray-700"
                    strokeWidth="10"
                    stroke="currentColor"
                    fill="transparent"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    className={gaugeColor}
                    strokeWidth="10"
                    strokeDasharray={circumference}
                    strokeDashoffset={strokeDashoffset}
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="transparent"
                  />
                </svg>
              ) : (
                <div className="w-full h-full rounded-full border-4 border-dashed border-gray-600 flex items-center justify-center" />
              )}
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-4xl font-bold text-white">{hasMasterScore ? data.master_score.toFixed(0) : '—'}</span>
                <span className="text-xs text-gray-400">{hasMasterScore ? '/100' : '데이터 부족'}</span>
              </div>
            </div>"""

if old_gauge_area in app_content:
    app_content = app_content.replace(old_gauge_area, new_gauge_area)
    print("Replaced Gauge Area successfully!")
else:
    print("Warning: old_gauge_area pattern not matched directly.")

# Check for masterSignal?.confidence || 50
app_content = app_content.replace('masterSignal?.confidence || 50', "masterSignal?.confidence != null ? `${masterSignal.confidence}%` : '—'")
app_content = app_content.replace('masterSignal?.confidence ?? 50', "masterSignal?.confidence != null ? `${masterSignal.confidence}%` : '—'")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_content)

out_ui_diff, _ = run_cmd('git diff src/App.tsx', cwd=frontend_dir)
print("--- git diff src/App.tsx ---")
print(out_ui_diff)

run_cmd('git add src/App.tsx', cwd=frontend_dir)
c_ui, _ = run_cmd('git commit -m "fix(ui): conditional gauge rendering and null-safe confidence for master_score"', cwd=frontend_dir)
print("Commit B-1 Output:\n", c_ui)
