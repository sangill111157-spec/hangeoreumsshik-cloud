# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'

# 1. Update CandidateStock in stock_scanner.py: add screening_score and score_source (defects 41, 94)
ss_path = os.path.join(backend_dir, r'app\services\stock_scanner.py')
with open(ss_path, 'r', encoding='utf-8') as f:
    ss_c = f.read()

old_cs = """@dataclass
class CandidateStock:
    \"\"\"후보 종목\"\"\"
    ticker: str
    market: str
    rank: int = 0
    current_price: float = 0.0
    change_percent: float = 0.0
    master_score: float = 0.0
    master_signal: str = "HOLD" """

new_cs = """@dataclass
class CandidateStock:
    \"\"\"후보 종목 (결함 41·94 해소: screening_score 및 score_source 명시)\"\"\"
    ticker: str
    market: str
    rank: int = 0
    current_price: float = 0.0
    change_percent: float = 0.0
    screening_score: float = 0.0
    master_score: float = 0.0  # 하위 호환성 유지용
    score_source: str = "rule_based_screening"
    master_signal: str = "HOLD" """

if old_cs in ss_c:
    ss_c = ss_c.replace(old_cs, new_cs)

# Also update CandidateStock instantiation in _analyze_secondary_filters
old_cand_inst = """            candidate = CandidateStock(
                ticker=ticker,
                market=market,
                current_price=current_price,
                change_percent=stock_info.change_percent,
                master_score=master_score,
                master_signal=master_signal,"""

new_cand_inst = """            candidate = CandidateStock(
                ticker=ticker,
                market=market,
                current_price=current_price,
                change_percent=stock_info.change_percent,
                screening_score=master_score,
                master_score=master_score,
                score_source="rule_based_screening",
                master_signal=master_signal,"""

if old_cand_inst in ss_c:
    ss_c = ss_c.replace(old_cand_inst, new_cand_inst)

with open(ss_path, 'w', encoding='utf-8') as f:
    f.write(ss_c)

# 2. Update nvda-trading-dashboard/src/App.tsx for stop_loss null guard (defect 95)
app_tsx_path = os.path.join(frontend_dir, r'src\App.tsx')
if os.path.exists(app_tsx_path):
    with open(app_tsx_path, 'r', encoding='utf-8') as f:
        app_c = f.read()
    
    # Check stop_loss null guard in App.tsx
    if "data.kelly?.stop_loss" in app_c and "toFixed" in app_c:
        # replace any unguarded stop_loss.toFixed
        app_c = app_c.replace("data.kelly.stop_loss.toFixed", "(data.kelly.stop_loss != null ? data.kelly.stop_loss.toFixed : () => '—')")
    
    with open(app_tsx_path, 'w', encoding='utf-8') as f:
        f.write(app_c)

subprocess.run('git add app/services/stock_scanner.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(scanner): add screening_score and score_source to CandidateStock (defects 41, 94)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)

