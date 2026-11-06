from pathlib import Path
import subprocess, sys

p = Path("s1_ego.py")
txt = p.read_text(encoding="utf-8", errors="replace")
txt = txt.replace('res = json.loads(line[len("S1EGO_JSON::"):])', 'res, _ = json.JSONDecoder().raw_decode(line[len("S1EGO_JSON::"):].lstrip())')
p.write_text(txt, encoding="utf-8", errors="replace")
print("[FIXED] raw_decode installed in s1_ego.py!")
subprocess.run([sys.executable, "run_live_monetization_test.py"])
