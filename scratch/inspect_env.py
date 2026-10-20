from pathlib import Path

p = Path("config/.env")
if p.exists():
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        print(f"{k} (len={len(v)}): {v[:6]}...{v[-4:] if len(v)>4 else ''}")
