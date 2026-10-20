# -*- coding: utf-8 -*-
"""
Inspect task-744 sampling window for tool calls in transcript.jsonl.
Verifies whether any tool calls occurred between 2026-09-23 10:37:13Z and 11:07:26Z (UTC).
"""
import datetime
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

LOG_FILE = r"C:\Users\sangi\.gemini\antigravity-ide\brain\ec6dfafd-d033-4251-9255-a00a3f742816\.system_generated\logs\transcript.jsonl"
START_UTC = "2026-09-23T10:37:13Z"
END_UTC = "2026-09-23T11:07:26Z"

start_dt = datetime.datetime.fromisoformat(START_UTC.replace("Z", "+00:00"))
end_dt = datetime.datetime.fromisoformat(END_UTC.replace("Z", "+00:00"))


def inspect_tool_calls_in_window(log_file=LOG_FILE):
    if not os.path.exists(log_file):
        print(f"Log file not found: {log_file}")
        return

    found = []
    total_events = 0
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            total_events += 1
            obj = json.loads(line)
            created_at = obj.get("created_at")
            if not created_at:
                continue
            try:
                cur_dt = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except Exception:
                continue

            if start_dt <= cur_dt <= end_dt:
                tcs = obj.get("tool_calls", [])
                for tc in tcs:
                    found.append((created_at, tc))

    print(f"=== Transcript Inspection (Window: {START_UTC} ~ {END_UTC}) ===")
    print(f"Total events scanned: {total_events}")
    print(f"Total tool calls in window (without filter): {len(found)}")
    for ca, tc in found:
        print(f"[{ca}] {tc.get('name')}: {tc.get('args')}")


if __name__ == "__main__":
    inspect_tool_calls_in_window()
