# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

test_file = os.path.join(backend_dir, 'tests', 'test_stop_loss_disabled_alert.py')
with open(test_file, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'from app.services.scheduler import TradingScheduler, STOP_LOSS_STATE_FILE',
    'from app.services.scheduler import TradingScheduler\nimport app.services.scheduler as sched_mod'
)
code = code.replace(
    'state_file = Path(STOP_LOSS_STATE_FILE)',
    'state_file = Path(sched_mod.STOP_LOSS_STATE_FILE)'
)

with open(test_file, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated test_stop_loss_disabled_alert.py")

# Commit this fix
res_add = subprocess.run('git add tests/test_stop_loss_disabled_alert.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
res_com = subprocess.run('git commit -m "fix(test): use dynamic sched_mod.STOP_LOSS_STATE_FILE for isolated state file test"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit result:")
print(res_com.stdout)

# Run full pytest
res_py = subprocess.run([os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/', '-v'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
lines = [l.strip() for l in res_py.stdout.splitlines() if l.strip()]
print("\npytest returncode:", res_py.returncode)
print("pytest exact last line:", repr(lines[-1]))
