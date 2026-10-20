import sys
import re
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

server_log_path = r"C:\trading\package\nvda_trading_system\backend\logs\server_20261004.log"
with open(server_log_path, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

print("="*60)
print("■ 2. Traceback 2건 원문 정밀 분석")
print("="*60)

for line_idx in [428, 1537]:  # around 430 and 1539
    print(f"\n--- Target line {line_idx+1} ---")
    start = max(0, line_idx - 10)
    end = min(len(lines), line_idx + 22)
    for j in range(start, end):
        print(f"{j+1}: {lines[j]}", end="")

print("\n" + "="*60)
print("■ 3. EGW00201 27건 전수 표 생성")
print("="*60)

egw_lines = []
for i, l in enumerate(lines):
    if "EGW00201" in l or "초당 거래건수를 초과" in l:
        egw_lines.append((i, l))

print(f"Total matching lines: {len(egw_lines)}")

# We need to classify each into:
# (a) Reconciler 구간 (:06~:26, :36~:56)
# (b) 손절 감시 (:21) 직후
# (c) GET /api/... 요청 직후 1초 이내
# (d) 기타

# First, collect all GET /api timestamps
api_requests = []
for l in lines:
    m = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*GET (/api/\S+)", l)
    if m:
        t = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S,%f")
        api_requests.append((t, m.group(2)))

print(f"Total GET /api requests found: {len(api_requests)}")
for t, ep in api_requests:
    print(f"  API: {t} -> {ep}")

table_rows = []
for idx, l in egw_lines:
    ts_m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})", l)
    if ts_m:
        ts_str = ts_m.group(1)
        dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S,%f")
    else:
        # Check preceding line
        ts_prev = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})", lines[idx-1])
        ts_str = ts_prev.group(1) if ts_prev else "unknown"
        dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S,%f") if ts_prev else datetime.min

    sec = dt.second

    # Determine classification
    # Reconciler runs at :06 and :36. Reconciler 구간: (:06 ~ :26, :36 ~ :56)
    # 손절 감시 runs at :21. (:21 ~ :25)
    # Note: :21~:25 is both in Reconciler interval (:06~:26) and 손절 감시 (:21) 직후!
    # Let's inspect which module actually triggered it:
    # Check context lines (±3 lines)
    ctx = lines[max(0, idx-3):min(len(lines), idx+4)]
    ctx_text = "".join(ctx)

    # TR_ID / URL
    tr_id = "미확인"
    if "US_BALANCE_INQUIRE_NYSE" in l:
        tr_id = "TTTS3012R (NYSE balance)"
    elif "US_BALANCE_INQUIRE_AMEX" in l:
        tr_id = "TTTS3012R (AMEX balance)"
    elif "US_BALANCE_INQUIRE_NASD" in l:
        tr_id = "TTTS3012R (NASD balance)"
    elif "Overseas cash inquiry" in l or "3007R" in l:
        tr_id = "VTTS3007R (inquire-psamount)"
    elif "Overseas open orders inquiry" in l or "inquire-ccnl" in l or "3035R" in l:
        tr_id = "VTTS3035R (inquire-ccnl)"
    elif "domestic" in l.lower():
        tr_id = "VTTC8001R / VTTC8434R"
    else:
        # find from context
        if "3007R" in ctx_text:
            tr_id = "VTTS3007R (inquire-psamount)"
        elif "open orders" in ctx_text:
            tr_id = "VTTS3035R (inquire-ccnl)"
        elif "inquire-balance" in ctx_text or "US_BALANCE" in ctx_text:
            tr_id = "TTTS3012R (inquire-balance)"

    # Logger / module
    logger_name = "unknown"
    log_m = re.search(r" - (app\.\S+) - ", l)
    if log_m:
        logger_name = log_m.group(1)
    else:
        for c in ctx:
            log_m2 = re.search(r" - (app\.\S+) - ", c)
            if log_m2:
                logger_name = log_m2.group(1)
                break

    # Success after retry
    retry_success = "성공(재시도 복구)"
    if "ERROR" in l or "Traceback" in ctx_text or "INQUIRY_TRANSIENT_HOLD" in ctx_text:
        retry_success = "실패(Hold 전환)"
    elif "attempt 1/3, retrying" in l:
        # Check if next lines have attempt 2 or success
        retry_success = "재시도 후 성공(추정)"

    # Check classification:
    cat = "(d) 기타"
    # Check if within 1 sec of API request
    is_api = any(abs((dt - api_t).total_seconds()) <= 1.0 for api_t, _ in api_requests)
    if is_api:
        cat = "(c) GET /api/ 요청 직후"
    elif sec in range(21, 26):
        cat = "(b) 손절 감시(:21) 직후"
    elif (6 <= sec <= 26) or (36 <= sec <= 56):
        cat = "(a) Reconciler 구간"

    # Concurrent KIS calls at same second (±1 sec)
    nearby_calls = []
    for j in range(max(0, idx-10), min(len(lines), idx+11)):
        if j == idx:
            continue
        line_j = lines[j]
        if any(k in line_j for k in ["[RECONCILER_RUN]", "ACCOUNT_STATE", "US_BALANCE", "inquire-", "3007R", "3035R", "3012R"]):
            ts_j_m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})", line_j)
            if ts_j_m:
                dt_j = datetime.strptime(ts_j_m.group(1), "%Y-%m-%d %H:%M:%S,%f")
                if abs((dt_j - dt).total_seconds()) <= 1.5:
                    nearby_calls.append(line_j.strip()[:90])

    table_rows.append({
        "line_no": idx + 1,
        "timestamp": ts_str,
        "tr_id": tr_id,
        "logger": logger_name,
        "retry_success": retry_success,
        "category": cat,
        "nearby_calls": nearby_calls[:2]
    })

print(f"\nCollected {len(table_rows)} rows. Summary of categories:")
cat_counts = Counter(r["category"] for r in table_rows)
for c, cnt in cat_counts.items():
    print(f"  {c}: {cnt}건")

for r in table_rows:
    print(f"[{r['timestamp']}] Line {r['line_no']} | {r['tr_id']} | {r['logger']} | {r['retry_success']} | {r['category']}")
    if r['nearby_calls']:
        for nc in r['nearby_calls']:
            print(f"    동일초 호출: {nc}")
