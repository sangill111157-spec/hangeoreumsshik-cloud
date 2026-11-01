# -*- coding: utf-8 -*-
from pathlib import Path
import subprocess, sys

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
p = BASE / "s1.py"
p.write_text(p.read_text(encoding="utf-8").replace("Boolean(", "bool("), encoding="utf-8")
print("[OK] s1.py Boolean -> bool 수정 완료!")
subprocess.run([sys.executable, "run_stage2_resume.py"], cwd=str(BASE), check=True)
