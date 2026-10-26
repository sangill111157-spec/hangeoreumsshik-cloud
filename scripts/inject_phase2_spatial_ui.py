# -*- coding: utf-8 -*-
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

src = ROOT / "rgon_spatial_glass_2026.css"
for d in [ROOT / "dashboard", ROOT / "docs"]:
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, d / "rgon_spatial_glass_2026.css")
    print(f"Synced {src.name} to {d}")

all_html = []
for pat in ["*.html", "dashboard/*.html", "docs/*.html", "safe_apps/*.html", "dashboard/safe_apps/*.html", "docs/safe_apps/*.html"]:
    for p in ROOT.glob(pat):
        if "backup" not in p.name and p not in all_html:
            all_html.append(p)

injected = 0
for p in all_html:
    content = p.read_text(encoding="utf-8")
    if "rgon_spatial_glass_2026.css" not in content:
        rel_depth = len(p.relative_to(ROOT).parts) - 1
        css_path = ("../" * rel_depth) + "rgon_spatial_glass_2026.css" if rel_depth > 0 else "rgon_spatial_glass_2026.css"
        tag = f'<link rel="stylesheet" href="{css_path}">'
        if "</head>" in content:
            content = content.replace("</head>", f"  {tag}\n</head>", 1)
            p.write_text(content, encoding="utf-8")
            injected += 1
            print(f"Injected 2026 CSS into: {p.relative_to(ROOT)}")

print(f"Phase 2 Complete: Injected 2026 Spatial UI into {injected} pages.")
