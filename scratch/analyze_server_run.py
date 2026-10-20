import os
import sys
import re
from datetime import datetime
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

server_log_path = r"C:\trading\package\nvda_trading_system\backend\logs\server_20261004.log"
app_log_path = r"C:\trading\package\nvda_trading_system\backend\logs\app.log"
portfolio_path = r"C:\trading\package\nvda_trading_system\backend\data\portfolio.json"

with open(server_log_path, "r", encoding="utf-8", errors="replace") as f:
    s_lines = f.readlines()

print(f"Total lines in server_20261004.log: {len(s_lines)}")

# =========================================================================
# 2. Check legacy paths & 404
# =========================================================================
print("\n" + "="*50)
print("■ 2. 옛 경로·404 확인")
print("="*50)

legacy_patterns = [
    "TTTT3016R",
    "inquire-orders",
    "Open orders check HTTP 404",
    "HTTP 404"
]

for pat in legacy_patterns:
    matches = [l.strip() for l in s_lines if pat in l]
    print(f"'{pat}' count: {len(matches)}")
    if matches:
        for m in matches[:5]:
            print(f"  -> {m}")

# Also check app.log for legacy paths
with open(app_log_path, "r", encoding="utf-8", errors="replace") as f:
    a_lines = f.readlines()

print(f"\nIn app.log (total {len(a_lines)} lines):")
for pat in legacy_patterns:
    matches = [l.strip() for l in a_lines if pat in l]
    print(f"  '{pat}' count: {len(matches)}")


# =========================================================================
# 3. Check Reconciler behavior
# =========================================================================
print("\n" + "="*50)
print("■ 3. Reconciler 증권사 잔고 비교 확인")
print("="*50)

rec_runs = []
for l in s_lines:
    if "[RECONCILER_RUN]" in l:
        rec_runs.append(l.strip())

print(f"Total [RECONCILER_RUN] occurrences: {len(rec_runs)}")
if rec_runs:
    print(f"First run: {rec_runs[0]}")
    if len(rec_runs) > 1:
        print(f"Second run: {rec_runs[1]}")
        print(f"Third run: {rec_runs[2]}")
        print(f"Last run: {rec_runs[-1]}")

# Interval calculation between runs
intervals = []
for i in range(min(10, len(rec_runs) - 1)):
    t1_str = rec_runs[i][:23]
    t2_str = rec_runs[i+1][:23]
    try:
        t1 = datetime.strptime(t1_str, "%Y-%m-%d %H:%M:%S,%f")
        t2 = datetime.strptime(t2_str, "%Y-%m-%d %H:%M:%S,%f")
        diff = (t2 - t1).total_seconds()
        intervals.append(diff)
    except Exception:
        pass
print(f"First 10 execution intervals (seconds): {intervals}")

# RECONCILER_BLOCKING_ALERT / QTY_MISMATCH quote
blocking_alerts = [l.strip() for l in s_lines if "RECONCILER_BLOCKING_ALERT" in l]
print(f"\nTotal RECONCILER_BLOCKING_ALERT count: {len(blocking_alerts)}")
if blocking_alerts:
    print("Sample RECONCILER_BLOCKING_ALERT (masked):")
    masked_sample = re.sub(r"\b\d{8}-\d{2}\b", "5018****-01", blocking_alerts[0])
    print(masked_sample)

# CASH_SURPLUS checks
cash_surplus = [l.strip() for l in s_lines if "CASH_SURPLUS" in l]
print(f"\nTotal CASH_SURPLUS mentions: {len(cash_surplus)}")

# 10 minute summary WARNING (same mismatch persists)
summary_10m = [l.strip() for l in s_lines if "same mismatch persists" in l or "10분" in l or "요약" in l]
print(f"10-min summary WARNING count: {len(summary_10m)}")
for s in summary_10m[:5]:
    print(f"  -> {s}")

# Check portfolio.json
print("\nChecking portfolio.json holdings:")
with open(portfolio_path, "r", encoding="utf-8") as f:
    port_content = f.read()
print(port_content[:400])


# =========================================================================
# 4. Check inquiry failure & rate limit
# =========================================================================
print("\n" + "="*50)
print("■ 4. 조회 실패·속도 제한 확인")
print("="*50)

fail_keywords = ["BrokerInquiryError", "OpenOrdersInquiryError", "INQUIRY_FAILURE", "INQUIRY_TRANSIENT_HOLD"]
for kw in fail_keywords:
    m_list = [l.strip() for l in s_lines if kw in l]
    print(f"'{kw}' count: {len(m_list)}")
    for m in m_list[:3]:
        print(f"  -> {m}")

egw_list = [l.strip() for l in s_lines if "EGW00201" in l or "초당 거래건수를 초과" in l]
print(f"\nEGW00201 / '초과' count: {len(egw_list)}")
for m in egw_list[:3]:
    print(f"  -> {m}")

token_issues = [l.strip() for l in s_lines if "access token" in l.lower() or "토큰 발급" in l or "token issued" in l.lower() or "token_init" in l.lower()]
print(f"\nToken issuance logs count: {len(token_issues)}")
for m in token_issues[:5]:
    print(f"  -> {m}")

# Reconciler 1-cycle duration calculation
print("\nReconciler duration check (from log start to end of job):")
durations = []
for i, l in enumerate(s_lines):
    if "[RECONCILER_RUN] Starting reconciliation run" in l:
        t_start_str = l[:23]
        # find corresponding job finish in next 30 lines
        for j in range(i+1, min(len(s_lines), i+40)):
            if "포지션·주문 정합성 대조 루프" in s_lines[j] and "executed successfully" in s_lines[j]:
                t_end_str = s_lines[j][:23]
                try:
                    t_s = datetime.strptime(t_start_str, "%Y-%m-%d %H:%M:%S,%f")
                    t_e = datetime.strptime(t_end_str, "%Y-%m-%d %H:%M:%S,%f")
                    durations.append((t_e - t_s).total_seconds())
                except Exception:
                    pass
                break
if durations:
    print(f"Sample cycle durations (seconds): {durations[:10]}")
    print(f"Min: {min(durations):.2f}s, Max: {max(durations):.2f}s, Avg: {sum(durations)/len(durations):.2f}s")

# Check 손절/익절 모니터링 timing vs Reconciler timing
print("\nCheck StopLoss/TakeProfit timing vs Reconciler timing:")
stop_loss_runs = [l[:23] for l in s_lines if "Running job \"손절/익절 모니터링" in l]
rec_job_runs = [l[:23] for l in s_lines if "Running job \"포지션·주문 정합성 대조 루프" in l]
print(f"Sample StopLoss times: {stop_loss_runs[:3]}")
print(f"Sample Reconciler times: {rec_job_runs[:6]}")


# =========================================================================
# 5. Log size & message stats
# =========================================================================
print("\n" + "="*50)
print("■ 5. 로그 크기 및 상위 메시지")
print("="*50)

server_stat = os.stat(server_log_path)
app_stat = os.stat(app_log_path)
print(f"server_20261004.log size: {server_stat.st_size} bytes ({server_stat.st_size / 1024:.2f} KB)")
print(f"app.log size: {app_stat.st_size} bytes ({app_stat.st_size / 1024:.2f} KB)")

# Server start time
start_time_str = s_lines[0][:19] if s_lines else "unknown"
end_time_str = s_lines[-1][:19] if s_lines else "unknown"
print(f"Server log start time: {start_time_str}")
print(f"Server log latest time: {end_time_str}")

try:
    t_start = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
    t_end = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
    elapsed_seconds = (t_end - t_start).total_seconds()
    elapsed_hours = elapsed_seconds / 3600.0
    print(f"Elapsed time: {elapsed_seconds:.0f} seconds ({elapsed_hours:.2f} hours)")

    daily_server_bytes = (server_stat.st_size / elapsed_seconds) * 86400.0
    print(f"Estimated daily server_log size: {daily_server_bytes / (1024*1024):.2f} MB / day")
except Exception as e:
    print(f"Could not compute daily rate: {e}")

# Top 5 messages in server_log
# Normalize messages by stripping timestamp and specific numbers
normalized_msgs = []
for l in s_lines:
    # remove timestamp
    msg = re.sub(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - ", "", l.strip())
    # remove elapsed_sec
    msg = re.sub(r"'elapsed_sec': \d+\.\d+", "'elapsed_sec': <N>", msg)
    # remove next run at
    msg = re.sub(r"next run at: [^\)]+", "next run at: <TIME>", msg)
    msg = re.sub(r"scheduled at: [^\)]+", "scheduled at: <TIME>", msg)
    normalized_msgs.append(msg)

counts = Counter(normalized_msgs)
print("\nTop 5 messages in server_20261004.log:")
for msg, cnt in counts.most_common(5):
    print(f"  [{cnt}회] {msg[:120]}")
