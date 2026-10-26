import os, sys, re, json
sys.path.insert(0, ".")

import rgon_aon_live_ui_healer as healer

with open("scratch/upgraded_bridge.js", "r", encoding="utf-8") as f:
    upgraded_js = f.read()

mark = healer.MARK
bridge_re = healer.BRIDGE_RE
new_bridge = f"<!-- {mark} START -->\n<script id=\"rgon-r44-live-ui-healer\">\n{upgraded_js.strip()}\n</script>\n<!-- {mark} END -->"

# Inject into all DASH pages
pages = [
    "index.html", "rgon_alpha_chat.html", "rgon_alpha_audience.html", "offline.html",
    "docs/index.html", "docs/rgon_alpha_chat.html", "docs/offline.html",
    "dashboard/index.html", "dashboard/rgon_alpha_chat.html", "dashboard/offline.html"
]

for p in pages:
    if not os.path.isfile(p):
        continue
    content = open(p, "r", encoding="utf-8").read()
    content_stripped = bridge_re.sub("", content)
    # inject before </body>
    m = None
    for m in re.finditer(r"</body\s*>", content_stripped, re.I): pass
    if m:
        final_content = content_stripped[:m.start()] + new_bridge + "\n" + content_stripped[m.start():]
    else:
        final_content = content_stripped + "\n" + new_bridge + "\n"
    with open(p, "w", encoding="utf-8") as out:
        out.write(final_content)
    print(f"Injected into {p}")

# Now test self-test
st = healer.self_test()
print("healer self-test return code:", st)
