import json
from pathlib import Path
out = Path("S1_RGON_DIRECT_PAYLOAD_PROOF.json")
out.write_text(json.dumps({"status": "SUCCESS", "directive": "RGON_DIR_DIRECT_TEST_049", "message": "Direct execution without anchongri completed!"}, indent=2), encoding="utf-8")
print("SUCCESS: Direct python payload executed cleanly!")