# -*- coding: utf-8 -*-
"""
Audit all ledger rows against disk log files in antigravity-ide brain.
Enhanced for Round 3-j to include:
- Disambiguation of task logs by full path (collecting all duplicate task logs)
- Comparison column between ledger value and raw log value
- Display all test execution runs within multi-run logs (e.g., task-2192, task-1099, task-123)
- Explicit reason for EXISTS with N/A (e.g. non-pytest task, timer, bash/powershell wrapper)
"""
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

DOC_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "testing_runtime_protocol.md")
BRAIN_ROOT = r"C:\Users\sangi\.gemini\antigravity-ide\brain"
REPO_LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")

# Index all task logs across all sessions in brain
brain_task_paths = defaultdict(list)
if os.path.exists(BRAIN_ROOT):
    for root, dirs, files in os.walk(BRAIN_ROOT):
        for f in files:
            if f.startswith("task-") and f.endswith(".log"):
                full_path = os.path.join(root, f)
                brain_task_paths[f].append(full_path)

# Also index repository preserved logs
repo_task_paths = {}
if os.path.exists(REPO_LOGS_DIR):
    for f in os.listdir(REPO_LOGS_DIR):
        if f.endswith(".log"):
            repo_task_paths[f] = os.path.join(REPO_LOGS_DIR, f)

with open(DOC_PATH, "r", encoding="utf-8") as f:
    doc_lines = f.readlines()

print("=== Enhanced Audit of Ledger Rows and Log Files (1..142) ===")
print(f"Unique task log filenames discovered across brain: {len(brain_task_paths)}")
print(f"Repo preserved logs: {len(repo_task_paths)}")

rows = []
for line in doc_lines:
    s = line.strip()
    if s.startswith("|") and not s.startswith("|---") and not s.startswith("|:---"):
        parts = [p.strip() for p in s.split("|")[1:-1]]
        if len(parts) >= 5 and parts[0].isdigit():
            r_num = int(parts[0])
            r_time = parts[1]
            r_min = parts[2]
            r_desc = parts[3]
            r_log = parts[4]

            m_abs = re.search(r"([A-Za-z]:\\[^`\s;]+\.log)", r_log)
            m_repo = re.search(r"`scripts/bench/logs/([^`\s;]+\.log)`", r_log)
            m_task = re.search(r"(task-\d+)", r_log + " " + r_desc)

            matched_paths = []
            if m_repo and m_repo.group(1) in repo_task_paths:
                matched_paths = [repo_task_paths[m_repo.group(1)]]
            elif m_abs and os.path.exists(m_abs.group(1)):
                matched_paths = [m_abs.group(1)]
            elif m_task:
                task_name = m_task.group(1) + ".log"
                if task_name in repo_task_paths:
                    matched_paths = [repo_task_paths[task_name]]
                elif task_name in brain_task_paths:
                    matched_paths = brain_task_paths[task_name]

            # Parse log content from the matched path
            # If multiple paths exist, inspect each
            parsed_runs = []
            na_reason = None

            if not matched_paths:
                if "미보존" in r_log:
                    na_reason = "LOG_NOT_PRESERVED"
                else:
                    na_reason = "NO_LOG_FILE"
            else:
                target_path = matched_paths[0]
                try:
                    with open(target_path, "r", encoding="utf-8", errors="ignore") as lf:
                        c_text = lf.read()

                    # Check if timer or non-pytest log
                    if "Successfully scheduled one-shot timer" in c_text:
                        na_reason = "TIMER_SCHEDULE_LOG(NO_TEST_OUTPUT)"
                    elif "=== RUN 1 ===" in c_text and "=== FINAL 3 RUNS SUMMARY ===" in c_text:
                        # Multi-run log format (e.g. task-2192, task-2292)
                        run_matches = re.findall(r"Run (\d+): Total elapsed ([\d\.]+)s", c_text)
                        parsed_runs = [f"Run{r}:{sec}s" for r, sec in run_matches]
                        na_reason = f"MULTI_RUN_HARNESS({len(run_matches)}_RUNS)"
                    else:
                        # Standard pytest run or verify run
                        pm = re.search(r"(\d+)\s+passed", c_text)
                        sm = re.search(r"(\d+)\s+skipped", c_text)
                        cm = re.search(r"collected\s+(\d+)\s+items", c_text)
                        tm = re.search(r"in\s+([\d\.]+)s", c_text)

                        raw_passed = int(pm.group(1)) if pm else None
                        raw_skipped = int(sm.group(1)) if sm else 0
                        raw_collected = int(cm.group(1)) if cm else ((raw_passed + raw_skipped) if raw_passed is not None else None)
                        raw_sec = tm.group(1) if tm else None

                        if raw_passed is not None:
                            parsed_runs.append({
                                "passed": raw_passed,
                                "skipped": raw_skipped,
                                "collected": raw_collected,
                                "sec": raw_sec,
                            })
                        else:
                            na_reason = "NON_PYTEST_OR_BUFFER_FLUSH_LOG"
                except Exception as ex:
                    na_reason = f"READ_ERROR({ex})"

            rows.append({
                "round": r_num,
                "ledger_time": r_time,
                "ledger_min": r_min,
                "log_target": m_task.group(1) if m_task else (os.path.basename(matched_paths[0]) if matched_paths else "None"),
                "num_candidates": len(matched_paths),
                "matched_paths": matched_paths,
                "parsed_runs": parsed_runs,
                "na_reason": na_reason,
            })

rows.sort(key=lambda x: x["round"])

# Header format
print("-" * 140)
print(f"{'Round':<6} | {'LedgerMin':<9} | {'LedgerTime':<22} | {'LogID':<10} | {'Status/Parsed':<35} | {'Duplicate Paths / Audit Note'}")
print("-" * 140)

for r in rows:
    r_id = f"R{r['round']:03d}"
    l_min = str(r['ledger_min'])
    l_time = str(r['ledger_time'])[:22]
    log_id = str(r['log_target'])

    status_str = ""
    audit_note = ""

    if r["parsed_runs"]:
        first = r["parsed_runs"][0]
        if isinstance(first, dict):
            p = first["passed"]
            s = first["skipped"]
            c = first["collected"]
            sec = first["sec"]
            # Ledger comparison
            match_min = "OK" if str(p) == l_min or str(c) == l_min else f"DIFF(raw={p})"
            status_str = f"P={p} S={s} C={c} ({sec}s) [{match_min}]"
        else:
            status_str = f"MULTI: {', '.join(r['parsed_runs'][:3])}"
    else:
        status_str = f"N/A ({r['na_reason']})"

    if r["num_candidates"] > 1:
        audit_note = f"[MULTIPLE PATHS({r['num_candidates']})]: " + " ; ".join(r["matched_paths"])
    elif r["num_candidates"] == 1:
        audit_note = r["matched_paths"][0]
    else:
        audit_note = f"Reason: {r['na_reason']}"

    print(f"{r_id:<6} | {l_min:<9} | {l_time:<22} | {log_id:<10} | {status_str:<35} | {audit_note}")

print("-" * 140)
print(f"Total rows audited: {len(rows)}")
