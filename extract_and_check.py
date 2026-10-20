# -*- coding: utf-8 -*-
import subprocess
import re
from pathlib import Path

content = Path("dashboard/index.html").read_text(encoding="utf-8")
scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
for idx, s in enumerate(scripts):
    Path(f".temp_s_{idx}.js").write_text(s, encoding="utf-8")
    res = subprocess.run(["node", "--check", f".temp_s_{idx}.js"], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Script {idx} syntax error:\n{res.stderr}")
    else:
        print(f"✅ Script {idx} OK!")
