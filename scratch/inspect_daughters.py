with open("dashboard/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

start = None
end = None
for i, l in enumerate(lines):
    if 'id="tab-daughters"' in l:
        start = i + 1
    if start and 'id="tab-vault"' in l:
        end = i + 1
        break
print(f"tab-daughters lines: {start} to {end}")

# Print headers inside tab-daughters
for i in range(start-1, end-1):
    l = lines[i]
    if "<h" in l or "class=\"glass-panel" in l or "<!--" in l:
        print(f"{i+1}: {l.strip()[:100]}")
