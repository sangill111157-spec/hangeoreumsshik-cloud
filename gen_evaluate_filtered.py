# -*- coding: utf-8 -*-
"""
Evaluate moving window RAM drift on filtered samples (>= 19:37:13).
Removes initial 2 samples taken during concurrent tool script execution.
"""
import csv
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
DEFAULT_CSV = os.path.join(os.path.dirname(__file__), "ram_baseline_30min.csv")


def evaluate_filtered_window(csv_path=DEFAULT_CSV, filter_time="2026-09-23 19:37:13", window_sizes=(5, 10), threshold_pct=30.0):
    samples = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) >= 2:
                ts, val_s = row[0].strip(), row[1].strip()
                if ts >= filter_time:
                    try:
                        samples.append((ts, float(val_s)))
                    except ValueError:
                        continue

    n = len(samples)
    print("=== Filtered Moving Window RAM Drift Evaluation (>= 19:37:13) ===")
    print(f"Target CSV: {os.path.basename(csv_path)}")
    print(f"Filtered Samples (after concurrent activity): {n}")
    if n == 0:
        print("No valid samples.")
        return False

    vals = [s[1] for s in samples]
    start_v, end_v = vals[0], vals[-1]
    min_v, max_v = min(vals), max(vals)
    mean_v = sum(vals) / n
    drift_pct = abs(end_v - start_v) / start_v * 100.0
    ratio = max_v / min_v

    print(f"Start RAM: {start_v:.1f} MB (at {samples[0][0]})")
    print(f"End RAM: {end_v:.1f} MB (at {samples[-1][0]})")
    print(f"Min: {min_v:.1f} MB | Max: {max_v:.1f} MB | Mean: {mean_v:.1f} MB")
    print(f"Start-to-End Drift: {drift_pct:.1f}%")
    print(f"Max/Min Ratio: {ratio:.2f}x (Limit: <= 1.50x -> Complies: {ratio <= 1.5})")

    for w in window_sizes:
        num_w = n - w + 1
        violated = 0
        max_d = 0.0
        for i in range(num_w):
            win = vals[i : i + w]
            st = win[0]
            m = max(abs(x - st) / st * 100.0 for x in win)
            if m > max_d:
                max_d = m
            if m > threshold_pct:
                violated += 1

        v_ratio = (violated / num_w) * 100.0
        passed = (violated == 0)
        span_sec = (w - 1) * 30
        print(f"Window W={w:2d} ({span_sec:3d}s span): Total={num_w:2d} | Violated={violated:2d} ({v_ratio:5.1f}%) | Max Drift={max_d:5.1f}% | Complies(0%): {passed}")


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV
    evaluate_filtered_window(csv_file)
