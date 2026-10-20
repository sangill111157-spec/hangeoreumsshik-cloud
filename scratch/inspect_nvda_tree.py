# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
import json

base_path = Path(r"C:\trading\package\nvda_trading_system")

def inspect_tree(p, depth=0, max_depth=3):
    if depth > max_depth or not p.exists():
        return
    for item in sorted(p.iterdir()):
        if item.name in [".git", "__pycache__", ".venv", "venv", "node_modules"]:
            continue
        indent = "  " * depth
        if item.is_dir():
            print(f"{indent}📁 {item.name}/")
            inspect_tree(item, depth + 1, max_depth)
        else:
            size_kb = item.stat().st_size / 1024
            print(f"{indent}📄 {item.name} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    if base_path.exists():
        print(f"=== NVDA Trading System 구조 탐색: {base_path} ===")
        inspect_tree(base_path)
    else:
        print(f"경로가 존재하지 않습니다: {base_path}")
