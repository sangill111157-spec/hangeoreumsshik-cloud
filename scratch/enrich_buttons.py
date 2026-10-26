import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

raw = open("index.html", "r", encoding="utf-8").read()
lines = raw.splitlines()
with open("scratch/index_buttons_dump.json", "r", encoding="utf-8") as f:
    buttons = json.load(f)

# Find screen area and function details for each button
enriched = []
for b in buttons:
    ln = b["line"]
    start = max(0, ln - 20)
    end = min(len(lines), ln + 20)
    context = "\n".join(lines[start:end])
    
    # Determine zone
    zone = "중앙 관제실"
    if ln < 850:
        zone = "최상단 헤더 / 터널 바"
    elif "sidebar" in context.lower() or "gnb" in context.lower() or ln in range(850, 950):
        zone = "상단 퀵액션 바"
    elif "청와대" in context or "cheongwadae" in context.lower():
        zone = "좌측 청와대 국정 관제"
    elif "국무총리" in context or "대화" in context or "aon" in context.lower():
        zone = "중앙 국무총리실 / 아온 집무실"
    elif "신경망" in context or "synapse" in context.lower() or "antibody" in context.lower():
        zone = "우측 전신 신경망 / 항체 현황"
    elif "footer" in context.lower() or ln > 3200:
        zone = "최하단 시스템 상태 바"
    
    # Extract onclick or href
    curr_line = lines[ln - 1] if ln <= len(lines) else ""
    # find tag in surrounding lines
    tag_snippet = ""
    for idx in range(max(0, ln - 3), min(len(lines), ln + 4)):
        tag_snippet += " " + lines[idx]
    
    onclick_m = re.search(r'onclick=["\']([^"\']+)["\']', tag_snippet)
    href_m = re.search(r'href=["\']([^"\']+)["\']', tag_snippet)
    handler = onclick_m.group(1) if onclick_m else (href_m.group(1) if href_m else b["reason"])
    
    enriched.append({
        "serial": b["serial"],
        "line": ln,
        "zone": zone,
        "label": b["label"],
        "tag": b["tag"],
        "handler": handler,
        "reason": b["reason"],
        "status": b["status"]
    })

with open("scratch/index_buttons_enriched.json", "w", encoding="utf-8") as f:
    json.dump(enriched, f, ensure_ascii=False, indent=2)

print(f"Enriched {len(enriched)} buttons successfully.")
