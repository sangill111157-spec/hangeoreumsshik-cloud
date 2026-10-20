# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'

# 1. Fix investor_analysis.py: branch order (bear >= 4 before bear >= 3) & clamp (10~95) (defects 101, 102)
inv_path = os.path.join(backend_dir, r'app\services\investor_analysis.py')
with open(inv_path, 'r', encoding='utf-8') as f:
    inv_c = f.read()

old_inv_branch = """        if bullish_count >= 4:
            overall_signal = "STRONG_BUY"
            overall_confidence = int(70 + (bullish_count / total) * 30)
        elif bullish_count >= 3:
            overall_signal = "BUY"
            overall_confidence = int(55 + (bullish_count / total) * 25)
        elif bear_count >= 3:
            overall_signal = "SELL"
            overall_confidence = int(55 + (bear_count / total) * 25)
        elif bear_count >= 4:
            overall_signal = "STRONG_SELL"
            overall_confidence = int(70 + (bear_count / total) * 30)
        else:
            overall_signal = "HOLD"
            overall_confidence = 50"""

new_inv_branch = """        # 결함 101·102 시정: STRONG_SELL (>=4) 분기 우선 배치, 상·하방 대칭화 및 10~95 엄격 클램프
        if bullish_count >= 4:
            overall_signal = "STRONG_BUY"
            overall_confidence = min(95, max(10, int(70 + (bullish_count / total) * 30)))
        elif bullish_count >= 3:
            overall_signal = "BUY"
            overall_confidence = min(95, max(10, int(55 + (bullish_count / total) * 25)))
        elif bear_count >= 4:
            overall_signal = "STRONG_SELL"
            overall_confidence = min(95, max(10, int(70 + (bear_count / total) * 30)))
        elif bear_count >= 3:
            overall_signal = "SELL"
            overall_confidence = min(95, max(10, int(55 + (bear_count / total) * 25)))
        else:
            overall_signal = "HOLD"
            overall_confidence = 50"""

if old_inv_branch in inv_c:
    inv_c = inv_c.replace(old_inv_branch, new_inv_branch)

with open(inv_path, 'w', encoding='utf-8') as f:
    f.write(inv_c)

# 2. Fix technical_analysis.py: clamp confidence (10~95) (defect 102)
tech_path = os.path.join(backend_dir, r'app\services\technical_analysis.py')
with open(tech_path, 'r', encoding='utf-8') as f:
    tech_c = f.read()

old_tech_clamp = "confidence = int(ratio * 100)"
new_tech_clamp = "confidence = min(95, max(10, int(ratio * 100)))  # 결함 102: 10~95 엄격 클램프"

if old_tech_clamp in tech_c:
    tech_c = tech_c.replace(old_tech_clamp, new_tech_clamp)

with open(tech_path, 'w', encoding='utf-8') as f:
    f.write(tech_c)

# 3. Unify backtester.py DEFAULT_WEIGHTS to BASE_WEIGHTS SSOT (defect 103)
bt_path = os.path.join(backend_dir, r'app\services\backtester.py')
with open(bt_path, 'r', encoding='utf-8') as f:
    bt_c = f.read()

# Replace DEFAULT_WEIGHTS dict with import from master_signal
if "from app.services.master_signal import BASE_WEIGHTS" not in bt_c:
    bt_c = "from app.services.master_signal import BASE_WEIGHTS\n" + bt_c

old_bt_weights = """DEFAULT_WEIGHTS = {
    "investor_analysis": 0.20,
    "pod_signals": 0.20,
    "technical": 0.15,
    "options_flow": 0.15,
    "llm_news": 0.12,
    "darkpool": 0.10,
    "institutional": 0.08,
}"""

new_bt_weights = """# 결함 103 해소: BASE_WEIGHTS SSOT 단일 원천 통일
DEFAULT_WEIGHTS = BASE_WEIGHTS"""

if old_bt_weights in bt_c:
    bt_c = bt_c.replace(old_bt_weights, new_bt_weights)

with open(bt_path, 'w', encoding='utf-8') as f:
    f.write(bt_c)

# 4. Update App.tsx for account_percentage null guard & perfect kelly display (defect 104)
app_path = os.path.join(frontend_dir, r'src\App.tsx')
with open(app_path, 'r', encoding='utf-8') as f:
    app_c = f.read()

# Ensure kelly_percentage shows true edge, and account_percentage has null guard
old_app_k = """              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 text-center">
                <p className="text-3xl font-bold text-blue-400">{data?.kelly?.kelly_percentage?.toFixed(1) || 0}%</p>
                <p className="text-gray-400 text-xs mt-1">켈리 비중</p>
              </div>"""

new_app_k = """              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 text-center">
                <p className="text-3xl font-bold text-blue-400">{data?.kelly?.kelly_percentage != null ? `${data.kelly.kelly_percentage.toFixed(1)}%` : '0%'}</p>
                <p className="text-gray-400 text-xs mt-1">켈리 엣지 비중</p>
              </div>"""

if old_app_k in app_c:
    app_c = app_c.replace(old_app_k, new_app_k)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_c)

subprocess.run('git add app/services/investor_analysis.py app/services/technical_analysis.py app/services/backtester.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(investor,technical,backtest): fix STRONG_SELL branch order, clamp conf 10-95, and unify backtester to BASE_WEIGHTS (defects 101,102,103)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)

