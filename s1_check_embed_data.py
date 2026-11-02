# -*- coding: utf-8 -*-
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8")

# Read current index.html to reuse the rich base styles and markup
with open("index.html", "r", encoding="utf-8") as f:
    orig_html = f.read()

# Let's verify what data files we have to embed for offline mobile live sync
data_manifest = {}

# 1. 16 Videos Proof
if os.path.exists("S1_16VIDEOS_VERIFIED_SYSTEMS_PROOF.json"):
    with open("S1_16VIDEOS_VERIFIED_SYSTEMS_PROOF.json", "r", encoding="utf-8") as f:
        data_manifest["proof"] = json.load(f)

# 2. Shorts batch manifest
if os.path.exists("S1_41TRACKS_SHORTS_BATCH_MANIFEST.json"):
    with open("S1_41TRACKS_SHORTS_BATCH_MANIFEST.json", "r", encoding="utf-8") as f:
        data_manifest["shorts"] = json.load(f)

# 3. 9-agent workflow
if os.path.exists("S1_9AGENTS_MASTER_WORKFLOW.json"):
    with open("S1_9AGENTS_MASTER_WORKFLOW.json", "r", encoding="utf-8") as f:
        data_manifest["agents"] = json.load(f)

# 4. Naver Blog Package
blog_text = ""
if os.path.exists("studio_vault/NAVER_BLOG_OUT/NOV06_NAVER_BLOG_POST_PACKAGE.md"):
    with open("studio_vault/NAVER_BLOG_OUT/NOV06_NAVER_BLOG_POST_PACKAGE.md", "r", encoding="utf-8") as f:
        blog_text = f.read()
data_manifest["naver_blog"] = blog_text

# 5. Threads funnel pack
threads_text = ""
if os.path.exists("studio_vault/THREADS_FUNNEL_OUT/S1_7DAYS_THREADS_GLOBAL_PACK.md"):
    with open("studio_vault/THREADS_FUNNEL_OUT/S1_7DAYS_THREADS_GLOBAL_PACK.md", "r", encoding="utf-8") as f:
        threads_text = f.read()
data_manifest["threads"] = threads_text

# 6. DistroKid Lyrics Master
lyrics_text = ""
if os.path.exists("DISTROKID_27TRACKS_LYRICS_MASTER.md"):
    with open("DISTROKID_27TRACKS_LYRICS_MASTER.md", "r", encoding="utf-8") as f:
        lyrics_text = f.read()
data_manifest["lyrics"] = lyrics_text[:12000] # concise preview

print(f"Loaded embedded data manifest: {list(data_manifest.keys())}")

