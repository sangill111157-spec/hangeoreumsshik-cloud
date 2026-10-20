# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

pm_path = os.path.join(backend_dir, r'app\services\pod_manager.py')
with open(pm_path, 'r', encoding='utf-8') as f:
    pm_c = f.read()

old_ms_dc = """@dataclass
class MasterSignal:
    \"\"\"마스터 종합 신호\"\"\"
    symbol: str
    master_score: float  # 0-100
    signal: SignalType
    confidence: int
    pod_signals: List[PodSignal]
    allocation: Dict[str, float]  # Pod별 자본 배분
    timestamp: str"""

new_ms_dc = """@dataclass
class MasterSignal:
    \"\"\"마스터 종합 신호\"\"\"
    symbol: str
    master_score: float  # 0-100
    signal: SignalType
    confidence: int
    pod_signals: List[PodSignal]
    allocation: Dict[str, float]  # Pod별 자본 배분
    timestamp: str
    available: bool = False"""

if old_ms_dc in pm_c:
    pm_c = pm_c.replace(old_ms_dc, new_ms_dc)
    with open(pm_path, 'w', encoding='utf-8') as f:
        f.write(pm_c)
    print("pod_manager.py MasterSignal dataclass updated with available: bool = False!")

subprocess.run('git add app/services/pod_manager.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(pod): declare available field on MasterSignal dataclass (defects 47,51)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)

