import os

for fname in ['dept_connect_ai.html', 'dept_media.html', 'dept_vault.html']:
    fpath = os.path.join('dashboard', 'departments', fname)
    print(f"=== {fname} ===")
    with open(fpath, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            if any(k in line for k in ['<main', '</main>', '<section', 'id="one-touch', 'id="btn-', 'id="panel-']):
                print(f"  {idx+1}: {line.strip()[:90]}")
