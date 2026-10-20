import re

with open("dashboard/index.html", "r", encoding="utf-8") as f:
    c = f.read()

tabs = re.findall(r'id=["\'](tab-[^"\']+)["\']', c)
print("Found tabs:", set(tabs))

nav_matches = re.findall(r'<button[^>]*onclick=["\']switchTab\([^)]+\)["\'][^>]*>[\s\S]*?</button>', c)
print(f"Nav buttons count: {len(nav_matches)}")
for n in nav_matches:
    clean = " ".join(n.split())
    print(" ", clean[:120])
