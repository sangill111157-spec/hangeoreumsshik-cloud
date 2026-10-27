# -*- coding: utf-8 -*-
"""
Calculate exact elapsed times from task-123.log for 6 alternating runs.
Parses run pairs and measures individual run metrics and total times.
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

LOG_PATH = os.path.join(os.path.dirname(__file__), "logs", "task-123.log")


def parse_task123_timing(log_path=LOG_PATH):
    if not os.path.exists(log_path):
        print(f"Log not found: {log_path}")
        return

    with open(log_path, "r", encoding="utf-8") as f:
        text = f.read()

    pair_runs = []
    # Match patterns like:
    # [A] Running verify.ps1... ExtWall=27.73s, Pytest=25.45s
    # [B] Running harness --consecutive 1 --no-warmup... ExtWall=19.78s, HarnessWall=18.9s, Pure=14.62s, Passed=452
    lines = text.splitlines()
    for line in lines:
        m_a = re.search(r"\[A\] Running verify\.ps1\.\.\. ExtWall=([\d\.]+)s, Pytest=([\d\.]+)s", line)
        if m_a:
            pair_runs.append({
                "type": "A (verify.ps1)",
                "ext_wall": float(m_a.group(1)),
                "framework_wall": float(m_a.group(2)),
                "pure": None,
            })
        m_b = re.search(r"\[B\] Running harness.*?ExtWall=([\d\.]+)s, HarnessWall=([\d\.]+)s, Pure=([\d\.]+)s", line)
        if m_b:
            pair_runs.append({
                "type": "B (harness)",
                "ext_wall": float(m_b.group(1)),
                "framework_wall": float(m_b.group(2)),
                "pure": float(m_b.group(3)),
            })

    # Summary table pure times for A:
    # 1     27.73    25.45 452 passed, 9 skipped, 87 subtests passed in 18.60s
    a_pure_matches = re.findall(r"\d+\s+[\d\.]+\s+[\d\.]+\s+\d+ passed, 9 skipped, 87 subtests passed in ([\d\.]+)s", text)
    a_idx = 0
    for r in pair_runs:
        if r["type"].startswith("A") and a_idx < len(a_pure_matches):
            r["pure"] = float(a_pure_matches[a_idx])
            a_idx += 1

    print("=== Detailed Timing Analysis of task-123.log (Alternating 6 Runs) ===")
    print(f"Total runs parsed: {len(pair_runs)}")
    print(f"{'Run':<4} | {'Target':<16} | {'ExtWall':<10} | {'FrameworkWall':<14} | {'Pure':<10}")
    print("-" * 65)

    tot_ext = 0.0
    tot_fw = 0.0
    tot_pure = 0.0

    for i, r in enumerate(pair_runs, 1):
        ext = r["ext_wall"]
        fw = r["framework_wall"]
        p = r["pure"]
        tot_ext += ext
        tot_fw += fw
        tot_pure += p
        print(f"{i:<4} | {r['type']:<16} | {ext:6.2f} s   | {fw:6.2f} s        | {p:6.2f} s")

    print("-" * 65)
    print(f"Total ExtWall (sum of 6 runs): {tot_ext:.2f} s")
    print(f"Total FrameworkWall (Pytest/Harness internal sum): {tot_fw:.2f} s")
    print(f"Total Pure Runtime (sum of 6 runs): {tot_pure:.2f} s")
    print("\nNote: Between-run script orchestration and process startup intervals are not logged with absolute wall-clock timestamps in task-123.log; the ExtWall sum (156.13 s) represents the strict active execution duration lower bound.")


if __name__ == "__main__":
    parse_task123_timing()
