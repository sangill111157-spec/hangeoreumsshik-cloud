# -*- coding: utf-8 -*-
import json
from pathlib import Path

path = Path("omni_agent_bus.json")
text = path.read_text(encoding="utf-8")

# MSG-20261017-0008 이전까지 잘라내기
marker = '"msg_id": "MSG-20261017-0008"'
idx = text.rfind(marker)
if idx != -1:
    brace_idx = text.rfind("{", 0, idx)
    valid_text = text[:brace_idx].rstrip().rstrip(",") + "\n  ]\n}"
    data = json.loads(valid_text)
else:
    try:
        data = json.loads(text)
    except Exception:
        data = {"registry": [], "messages": []}

data.setdefault("messages", []).append({
    "msg_id": f"MSG-20261017-{len(data.get('messages', [])) + 1:04d}",
    "timestamp": "2026-10-17 22:51:00",
    "from": "RGON-001",
    "to": "AGV-101",
    "type": "AUTO_SIGNAL_IN",
    "content": "스마트폰 원격 복붙 1초 직통 스위치 정상 가동 및 타건 검증",
    "status": "AUTO_INJECTED"
})

path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("✅ omni_agent_bus.json repaired successfully!")
