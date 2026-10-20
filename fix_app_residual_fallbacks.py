# -*- coding: utf-8 -*-
import sys, os, subprocess
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'

app_path = os.path.join(frontend_dir, r'src\App.tsx')
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

# Fix line 1002, 1477, 1643
app_content = app_content.replace('{masterSignal?.confidence || 50}% 신뢰도', "{masterSignal?.confidence != null ? `${masterSignal.confidence}%` : '—'} 신뢰도")
app_content = app_content.replace('{masterSignal?.confidence ?? 50}% 신뢰도', "{masterSignal?.confidence != null ? `${masterSignal.confidence}%` : '—'} 신뢰도")
app_content = app_content.replace('{data?.options_composite_score || 50}', "{data?.options_composite_score != null ? data.options_composite_score : '—'}")
app_content = app_content.replace('{data?.darkpool_composite_score || 50}', "{data?.darkpool_composite_score != null ? data.darkpool_composite_score : '—'}")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_content)

res = subprocess.run('git diff src/App.tsx', cwd=frontend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("--- git diff src/App.tsx ---")
print(res.stdout)

subprocess.run('git add src/App.tsx', cwd=frontend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(ui): eliminate remaining || 50 fallbacks in confidence and composite scores"', cwd=frontend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)

res_g = subprocess.run('git grep -n -E "confidence \\|\\| 50|options_composite_score \\|\\| 50|darkpool_composite_score \\|\\| 50" src/', cwd=frontend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Residual grep check:\n", res_g.stdout if res_g.stdout.strip() else "  (0건 - 완벽 제거 확인)")
