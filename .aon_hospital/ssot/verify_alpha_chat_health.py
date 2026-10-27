# -*- coding: utf-8 -*-
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def check_file(p: Path):
    print(f"--- Checking {p} ---")
    txt = p.read_text(encoding="utf-8")
    
    # 1. Adobe occurrences
    adobe_matches = txt.count("Adobe 무료 3대장 직통")
    print(f"  • 'Adobe 무료 3대장 직통' count: {adobe_matches} (Target: <= 1)")
    
    # 2. 2026-10-19 occurrences
    date_matches = txt.count("2026-10-19")
    print(f"  • '2026-10-19' count: {date_matches} (Target: 0)")
    
    # 3. 210개 occurrences
    btn210_matches = txt.count("210개")
    print(f"  • '210개' count: {btn210_matches} (Target: 0)")
    
    # 4. Stream min-height
    has_stream_rescue = "min-height: 480px" in txt
    print(f"  • Chat stream min-height 480px present: {has_stream_rescue} (Target: True)")
    
    # 5. Slash pills in footer
    has_slash = "aon-dlg-slash-bar" in txt and "/통찰" in txt
    print(f"  • Slash command pills in footer: {has_slash} (Target: True)")
    
    # 6. Tools drawer
    has_tools_drawer = "rgon-tools-drawer" in txt
    print(f"  • Collapsed tools drawer below stream: {has_tools_drawer} (Target: True)")

    assert adobe_matches <= 1, f"Failed: Adobe matches {adobe_matches} > 1"
    assert date_matches == 0, f"Failed: 2026-10-19 matches {date_matches} != 0"
    assert btn210_matches == 0, f"Failed: 210개 matches {btn210_matches} != 0"
    assert has_stream_rescue, "Failed: Stream rescue CSS missing"
    assert has_slash, "Failed: Slash pills missing"
    assert has_tools_drawer, "Failed: Tools drawer missing"
    print("  ✅ All checks PASSED!")

def main():
    files = [
        ROOT / "rgon_alpha_chat.html",
        ROOT / "rgon_alpha_audience.html",
        ROOT / "dashboard" / "rgon_alpha_chat.html",
        ROOT / "dashboard" / "rgon_alpha_audience.html",
        ROOT / "docs" / "rgon_alpha_chat.html",
        ROOT / "docs" / "rgon_alpha_audience.html"
    ]
    for f in files:
        check_file(f)
    print("\n🎉 ALL AUDIENCE & CHAT FILES PERFECTLY VERIFIED!")

if __name__ == "__main__":
    main()
