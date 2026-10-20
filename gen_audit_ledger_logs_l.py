# -*- coding: utf-8 -*-
"""
Audit all ledger rows against disk log files in antigravity-ide brain.
Enhanced for Round 3-l:
- Full runtime comparison and detailed note
- R038-044 defect handling
- R080 format handling
- R092/R093 runtime inspection
- R114 missing log note
- Definition shift at R078 (MinPassed = Passed)
- Session boundary detection for R072 -> R073
"""
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

DOC_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "testing_runtime_protocol.md")
BRAIN_ROOT = r"C:\Users\sangi\.gemini\antigravity-ide\brain"
REPO_LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")

brain_task_paths = defaultdict(list)
if os.path.exists(BRAIN_ROOT):
    for root, dirs, files in os.walk(BRAIN_ROOT):
        for f in files:
            if f.startswith("task-") and f.endswith(".log"):
                full_path = os.path.join(root, f)
                brain_task_paths[f].append(full_path)

repo_task_paths = {}
if os.path.exists(REPO_LOGS_DIR):
    for f in os.listdir(REPO_LOGS_DIR):
        if f.endswith(".log"):
            repo_task_paths[f] = os.path.join(REPO_LOGS_DIR, f)

with open(DOC_PATH, "r", encoding="utf-8") as f:
    doc_lines = f.readlines()

print("=== Complete Audit of Ledger Rows and Log Files (1..142) ===")

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

                    if "Successfully scheduled one-shot timer" in c_text:
                        na_reason = "DEFECT_SOURCE_TIMER_LOG"
                    elif "=== RUN 1 ===" in c_text and "=== FINAL 3 RUNS SUMMARY ===" in c_text:
                        run_matches = re.findall(r"Run (\d+): Total elapsed ([\d\.]+)s", c_text)
                        parsed_runs = [{"run": int(r), "sec": float(sec)} for r, sec in run_matches]
                        na_reason = f"MULTI_RUN_HARNESS({len(run_matches)}_RUNS)"
                    else:
                        pm = re.search(r"(\d+)\s+passed", c_text)
                        sm = re.search(r"(\d+)\s+skipped", c_text)
                        cm = re.search(r"collected\s+(\d+)\s+items", c_text)
                        tm = re.search(r"in\s+([\d\.]+)s", c_text)
                        rm = re.search(r"Pytest runtime:\s*([\d\.]+)s", c_text)

                        raw_passed = int(pm.group(1)) if pm else None
                        raw_skipped = int(sm.group(1)) if sm else 0
                        raw_collected = int(cm.group(1)) if cm else ((raw_passed + raw_skipped) if raw_passed is not None else None)
                        pure_sec = float(tm.group(1)) if tm else None
                        pytest_sec = float(rm.group(1)) if rm else None

                        if raw_passed is not None:
                            parsed_runs.append({
                                "passed": raw_passed,
                                "skipped": raw_skipped,
                                "collected": raw_collected,
                                "pure_sec": pure_sec,
                                "pytest_sec": pytest_sec,
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

print("-" * 155)
print(f"{'Round':<6} | {'LedgerMin':<9} | {'LedgerTime':<24} | {'LogID':<10} | {'Status/Parsed':<45} | {'Runtime Match':<16} | {'Audit Note'}")
print("-" * 155)

for r in rows:
    r_id = f"R{r['round']:03d}"
    l_min = str(r['ledger_min'])
    l_time = str(r['ledger_time'])[:24]
    log_id = str(r['log_target'])

    status_str = ""
    rt_match = "N/A"
    audit_note = ""

    m_l_sec = re.search(r"([\d\.]+)\s*s", l_time)
    l_sec_val = float(m_l_sec.group(1)) if m_l_sec else None

    m_pure = re.search(r"순수\s*([\d\.]+)\s*s", l_time)
    l_pure_val = float(m_pure.group(1)) if m_pure else None

    if r["parsed_runs"]:
        first = r["parsed_runs"][0]
        if "passed" in first:
            p = first["passed"]
            s = first["skipped"]
            c = first["collected"]
            pure = first["pure_sec"]
            p_rt = first["pytest_sec"]
            match_min = "OK" if str(p) == l_min or str(c) == l_min else f"DIFF(raw={p})"
            status_str = f"P={p} S={s} C={c} (pure={pure}s) [{match_min}]"

            if l_pure_val is not None and pure is not None:
                rt_match = "RT_OK" if abs(l_pure_val - pure) < 0.05 else f"RT_DIFF({pure}s)"
            elif l_sec_val is not None:
                if pure is not None and abs(l_sec_val - pure) < 0.05:
                    rt_match = "RT_OK(pure)"
                elif p_rt is not None and abs(l_sec_val - p_rt) < 0.05:
                    rt_match = "RT_OK(pytest)"
                else:
                    rt_match = f"RT_DIFF({pure}s)"
        else:
            runs_summary = ", ".join(f"R{x['run']}:{x['sec']}s" for x in r["parsed_runs"][:3])
            status_str = f"MULTI: {runs_summary}"
            if l_sec_val is not None:
                matched_run = any(abs(l_sec_val - x["sec"]) < 0.05 for x in r["parsed_runs"])
                rt_match = "RT_OK(multi)" if matched_run else "RT_DIFF(multi)"
    else:
        status_str = f"N/A ({r['na_reason']})"
        rt_match = "NO_LOG"

    if 38 <= r["round"] <= 44:
        audit_note = f"[DEFECT]: Ledger R{r['round']:03d} references timer schedule log task-1099 (no test output)"
    elif r["round"] == 80:
        audit_note = "[SPECIAL]: Single test unit gate check (fa036a7, 4 passed)"
    elif r["round"] == 92:
        audit_note = "task-2292 Run 3 (41.58s) matched multi-run summary"
    elif r["round"] == 93:
        audit_note = "task-2584 verify run (pure 37.89s, total pytest 49.80s)"
    elif r["round"] == 114:
        audit_note = "[DEFECT]: task-4009.log unpreserved across all brain directories"
    elif r["round"] == 139:
        audit_note = "[DEFECT]: Ledger cites 15.17s pure but task-8675 contains 32.96s (15.17s source log unpreserved)"
    elif r["round"] == 141:
        audit_note = "[DEFECT]: Pre-adjustment log task-123 cites 452 passed (raw basis is task-233)"
    elif r["round"] in (35, 36, 37, 49, 50, 51, 53, 54, 56, 57, 58, 59, 60, 61, 62):
        audit_note = "[SHARED_LOG_RT_DIFF]: Multi-round series sharing single session task log"
    elif r["num_candidates"] > 1:
        audit_note = f"[MULTIPLE PATHS({r['num_candidates']})]: " + " ; ".join(r["matched_paths"][:2])
    elif r["num_candidates"] == 1:
        audit_note = r["matched_paths"][0]
    else:
        audit_note = f"Reason: {r['na_reason']}"

    print(f"{r_id:<6} | {l_min:<9} | {l_time:<24} | {log_id:<10} | {status_str:<45} | {rt_match:<16} | {audit_note}")

print("-" * 155)
print(f"Total rows audited: {len(rows)}")
