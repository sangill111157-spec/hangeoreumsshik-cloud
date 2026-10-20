# -*- coding: utf-8 -*-
"""Verify line counts and diffs of docs/testing_runtime_protocol.md across commits."""
import subprocess

commits = ["05a9d63", "faa325b", "a460ca2", "8ccbec4", "a068ae8", "1386330", "b055514", "9594689"]
doc = "docs/testing_runtime_protocol.md"

print("=== Verification of testing_runtime_protocol.md line counts (Up to HEAD) ===")
prev_lines = None
for i, c in enumerate(commits):
    out = subprocess.check_output(["git", "show", f"{c}:{doc}"], text=True, encoding="utf-8")
    lf = out.count("\n")
    print(f"Commit {c}: {lf} lines (LF)")
    if prev_lines is not None:
        c_prev = commits[i - 1]
        stat = subprocess.check_output(
            ["git", "diff", "--numstat", c_prev, c, "--", doc], text=True, encoding="utf-8"
        ).strip()
        ins, dele = (0, 0)
        if stat:
            p = stat.split()
            ins, dele = int(p[0]), int(p[1])
        calculated = prev_lines + ins - dele
        match = calculated == lf
        print(
            f"  Diff {c_prev} -> {c}: +{ins}, -{dele} (net {ins - dele:+d}) | {prev_lines} {ins - dele:+d} = {calculated} | Match: {match}"
        )
    prev_lines = lf
