import os, sys, re

with open("scratch/upgraded_bridge.js", "r", encoding="utf-8") as f:
    upgraded_js = f.read()

for fn in ["s_run.py", "omni_rgon_20261026_073143.py", os.path.expanduser("~/Downloads/omni_rgon_20261026_073143.py")]:
    if not os.path.isfile(fn): continue
    content = open(fn, "r", encoding="utf-8").read()
    # Replace BRIDGE_JS = r"""..."""
    m = re.search(r'BRIDGE_JS\s*=\s*r?"""[\s\S]*?"""', content)
    if m:
        new_block = 'BRIDGE_JS = r"""\n' + upgraded_js.strip() + '\n"""'
        new_content = content[:m.start()] + new_block + content[m.end():]
        with open(fn, "w", encoding="utf-8") as out:
            out.write(new_content)
        print("Updated BRIDGE_JS in", fn)
    else:
        print("BRIDGE_JS not found in", fn)
