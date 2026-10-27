# -*- coding: utf-8 -*-
"""cleanse_phase1_redundancy.py — Phase 1: 49개 HTML 전수 중복·반복 군더더기 대청소
상선약수 비움의 미학: 중복 스타일, 중복 스크립트, 중복 마커 1-by-1 정리
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PROTECTED = {"index_20260405_backup.html"}

html_files = []
for pat in ["*.html", "dashboard/*.html", "docs/*.html", "safe_apps/*.html", "dashboard/safe_apps/*.html", "docs/safe_apps/*.html"]:
    for p in ROOT.glob(pat):
        if p.name not in PROTECTED and p not in html_files:
            html_files.append(p)

cleaned_count = 0

for p in html_files:
    content = p.read_text(encoding="utf-8")
    original = content

    # 1. 중복된 touch-action 스타일 블록 정리 (여러 번 들어간 경우 1개로 압축)
    touch_pattern = r"<style>button,a,\[role='button'\],\.btn\{touch-action:\s*manipulation;-webkit-tap-highlight-color:\s*transparent;\}<\/style>\s*"
    matches = list(re.finditer(touch_pattern, content))
    if len(matches) > 1:
        # 첫 번째만 남기고 나머지 제거
        content = re.sub(touch_pattern, "", content)
        # </head> 바로 앞에 1회만 단정하게 삽입
        clean_tag = "<style id=\"rgon-touch-action-guard\">button,a,[role='button'],.btn{touch-action:manipulation;-webkit-tap-highlight-color:transparent;}</style>\n"
        if "</head>" in content:
            content = content.replace("</head>", f"{clean_tag}</head>", 1)
        elif "<body" in content:
            content = clean_tag + content

    # 2. 중복된 #rgyt-wrap 스타일 블록 정리
    rgyt_pattern = r"<style>#rgyt-wrap\{transform:none!important;rotate:none!important;\}<\/style>\s*"
    rgyt_matches = list(re.finditer(rgyt_pattern, content))
    if len(rgyt_matches) > 1:
        content = re.sub(rgyt_pattern, "", content)
        clean_rgyt = "<style id=\"rgon-rgyt-guard\">#rgyt-wrap{transform:none!important;rotate:none!important;}</style>\n"
        if "</head>" in content:
            content = content.replace("</head>", f"{clean_rgyt}</head>", 1)

    # 3. 중복된 rgon_mobile_serverless_interceptor.js 태그 정리
    interceptor_pattern = r"<script src=\"(?:\.\./)*rgon_mobile_serverless_interceptor\.js\"><\/script>\s*"
    ic_matches = list(re.finditer(interceptor_pattern, content))
    if len(ic_matches) > 1:
        rel_depth = len(p.relative_to(ROOT).parts) - 1
        script_path = ("../" * rel_depth) + "rgon_mobile_serverless_interceptor.js" if rel_depth > 0 else "rgon_mobile_serverless_interceptor.js"
        content = re.sub(interceptor_pattern, "", content)
        clean_ic = f"<script src=\"{script_path}\"></script>\n"
        if "<head>" in content:
            content = content.replace("<head>", f"<head>\n  {clean_ic}", 1)

    # 4. 연속된 빈 줄 정리 (3줄 이상 연속 빈 줄을 1줄로)
    content = re.sub(r"\n\s*\n\s*\n+", "\n\n", content)

    if content != original:
        p.write_text(content, encoding="utf-8")
        cleaned_count += 1
        print(f"Cleaned redundancy: {p.relative_to(ROOT)}")

print(f"Phase 1 Complete: {cleaned_count} files cleaned and consolidated.")
