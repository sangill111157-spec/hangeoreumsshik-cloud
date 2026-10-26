# -*- coding: utf-8 -*-
"""apply_mobile_interceptor_all.py
모든 HTML 파일에 rgon_mobile_serverless_interceptor.js 주입 및 하드코딩 제거
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Protect immutable files
PROTECTED = {
    "index_20260405_backup.html",
}

all_html_files = []
for pattern in ["*.html", "dashboard/*.html", "docs/*.html", "safe_apps/*.html", "dashboard/safe_apps/*.html", "docs/safe_apps/*.html"]:
    for p in ROOT.glob(pattern):
        if p.name not in PROTECTED:
            all_html_files.append(p)

print(f"Total HTML files to patch: {len(all_html_files)}")

interceptor_filename = "rgon_mobile_serverless_interceptor.js"

for p in all_html_files:
    content = p.read_text(encoding="utf-8")
    original = content
    
    # 1. Determine relative path to interceptor
    rel_depth = len(p.relative_to(ROOT).parts) - 1
    script_path = ("../" * rel_depth) + interceptor_filename if rel_depth > 0 else interceptor_filename
    script_tag = f'<script src="{script_path}"></script>'
    
    # Insert interceptor script tag right after <head> if not present
    if "rgon_mobile_serverless_interceptor.js" not in content:
        if "<head>" in content:
            content = content.replace("<head>", f"<head>\n  {script_tag}", 1)
        elif "<HEAD>" in content:
            content = content.replace("<HEAD>", f"<HEAD>\n  {script_tag}", 1)
        else:
            content = script_tag + "\n" + content

    # 2. Viewport meta tag ensure
    if "viewport" not in content:
        vp_tag = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">'
        if "<head>" in content:
            content = content.replace("<head>", f"<head>\n  {vp_tag}", 1)

    # 3. 127.0.0.1:8765 hardcoding sanitize to relative /api/
    content = content.replace("http://127.0.0.1:8765/api/candidates", "/api/candidates")
    content = content.replace("http://127.0.0.1:8765/api/dispatch", "/api/dispatch")
    content = content.replace("http://127.0.0.1:8765/queue", "/api/queue")
    content = content.replace("http://127.0.0.1:8765/chat", "/api/chat")
    content = content.replace('var BR = "http://127.0.0.1:8765";', 'var BR = "";')

    # 4. Root absolute path sanitize: href="/dept... -> href="dept...
    content = re.sub(r'href\s*=\s*["\']/dept(\d+)', r'href="dept\1', content)
    content = re.sub(r'href\s*=\s*["\']/safe_apps/', r'href="safe_apps/', content)

    if content != original:
        p.write_text(content, encoding="utf-8")
        print(f"Patched: {p.relative_to(ROOT)}")

print("ALL HTML FILES MOBILE-PATCHED SUCCESSFULLY")
