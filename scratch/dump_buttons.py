import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rgon_aon_live_ui_healer import _audit_page

buttons, br = _audit_page("index.html", "LIVE-IDX", True)
print("Total buttons:", len(buttons))
with open("scratch/index_buttons_dump.json", "w", encoding="utf-8") as f:
    json.dump(buttons, f, ensure_ascii=False, indent=2)

for b in buttons:
    print(f"{b['serial']} | line {b['line']:4d} | {b['tag']:6s} | {b['label'][:30]:30s} | {b['reason']}")
