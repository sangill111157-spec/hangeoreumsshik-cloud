# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Update ComponentScore dataclass
old_comp_score = """@dataclass
class ComponentScore:
    \"\"\"구성 요소 점수 (결함 12·32·68: 미가용 모듈 score: None, signal: UNAVAILABLE, confidence: None 지원)\"\"\"
    name: str
    score: Optional[float]  # 0-100 or None (미가용)
    signal: str  # BUY, SELL, HOLD, UNAVAILABLE
    confidence: Optional[int] = None  # 0-100 or None (미가용)
    weight: float = 0.0"""

new_comp_score = """@dataclass
class ComponentScore:
    \"\"\"구성 요소 점수 (결함 107: module_signal 추가)\"\"\"
    name: str
    score: Optional[float]  # 0-100 or None (미가용)
    signal: str  # BUY, SELL, HOLD, UNAVAILABLE
    confidence: Optional[int] = None  # 0-100 or None (미가용)
    weight: float = 0.0
    module_signal: Optional[str] = None  # 결함 107: 모듈 자체 고유 신호 노출"""

if old_comp_score in ms_c:
    ms_c = ms_c.replace(old_comp_score, new_comp_score)

# Update investor_analysis component instantiation
old_inv_comp = """            ComponentScore(
                name="5대 투자자",
                score=None if "investor_analysis" in unavailable_modules else round(scores["investor_analysis"], 1),
                signal="UNAVAILABLE" if "investor_analysis" in unavailable_modules else score_to_5level_signal(scores["investor_analysis"]),
                confidence=None if "investor_analysis" in unavailable_modules else int(round(conf_map["investor_analysis"])),
                weight=weights_used.get("investor_analysis", 0.0)
            ),"""

new_inv_comp = """            ComponentScore(
                name="5대 투자자",
                score=None if "investor_analysis" in unavailable_modules else round(scores["investor_analysis"], 1),
                signal="UNAVAILABLE" if "investor_analysis" in unavailable_modules else score_to_5level_signal(scores["investor_analysis"]),
                confidence=None if "investor_analysis" in unavailable_modules else int(round(conf_map["investor_analysis"])),
                weight=weights_used.get("investor_analysis", 0.0),
                module_signal=investor_analysis.get("overall_signal", "HOLD") if "investor_analysis" not in unavailable_modules else "UNAVAILABLE"
            ),"""

if old_inv_comp in ms_c:
    ms_c = ms_c.replace(old_inv_comp, new_inv_comp)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(master_signal): add module_signal to ComponentScore (defect 107)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)

