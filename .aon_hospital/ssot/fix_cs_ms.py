# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

old_cs = """@dataclass
class ComponentScore:
    \"\"\"구성 요소 점수 (결함 12·32·68: 미가용 모듈 score: None, signal: UNAVAILABLE, confidence: None 지원)\"\"\"
    name: str
    score: Optional[float] = None  # 0-100 or None (미가용)
    signal: str = "UNAVAILABLE"
    confidence: Optional[int] = None  # 0-100 or None (미가용)
    details: Dict = field(default_factory=dict)"""

new_cs = """@dataclass
class ComponentScore:
    \"\"\"구성 요소 점수 (결함 107: module_signal 추가)\"\"\"
    name: str
    score: Optional[float] = None  # 0-100 or None (미가용)
    signal: str = "UNAVAILABLE"
    confidence: Optional[int] = None  # 0-100 or None (미가용)
    details: Dict = field(default_factory=dict)
    module_signal: Optional[str] = None  # 결함 107: 모듈 자체 고유 신호 노출"""

if old_cs in ms_c:
    ms_c = ms_c.replace(old_cs, new_cs)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(master_signal): add module_signal to ComponentScore dataclass (defect 107)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)

