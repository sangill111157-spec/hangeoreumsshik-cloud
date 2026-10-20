# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. nvda.py
nvda_path = os.path.join(backend_dir, r'app\api\routes\nvda.py')
with open(nvda_path, 'r', encoding='utf-8') as f:
    c = f.read()

if "from app.core.config import settings" not in c:
    c = "from app.core.config import settings\n" + c

target_nvda = """    notifier: TelegramNotifier = Depends(get_telegram_notifier)
):
    \"\"\"
    NVDA 매수/매도 주문"""

repl_nvda = """    notifier: TelegramNotifier = Depends(get_telegram_notifier)
):
    # 결함 166 완결: Gate 1 dry-run 중 ENABLE_LIVE_ORDERS 미설정 시 HTTP 404 차단
    if not getattr(settings, "ENABLE_LIVE_ORDERS", False):
        raise HTTPException(status_code=404, detail="Live order execution is disabled in Gate 1 dry-run mode (ENABLE_LIVE_ORDERS=False)")
    \"\"\"
    NVDA 매수/매도 주문"""

if target_nvda in c:
    c = c.replace(target_nvda, repl_nvda)

with open(nvda_path, 'w', encoding='utf-8') as f:
    f.write(c)

# 2. trader.py
trader_path = os.path.join(backend_dir, r'app\api\routes\trader.py')
with open(trader_path, 'r', encoding='utf-8') as f:
    c = f.read()

if "from app.core.config import settings" not in c:
    c = "from app.core.config import settings\n" + c

# Let's inspect trader.py execute_trade
with open(trader_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if "async def execute_trade(" in line:
        pass
    if "def execute_trade" in lines[max(0, i-10):i+1] and line.strip().endswith("):"):
        new_lines.append('    # 결함 166 완결: Gate 1 dry-run 중 ENABLE_LIVE_ORDERS 미설정 시 HTTP 404 차단\n')
        new_lines.append('    if not getattr(settings, "ENABLE_LIVE_ORDERS", False):\n')
        new_lines.append('        raise HTTPException(status_code=404, detail="Live order execution is disabled in Gate 1 dry-run mode (ENABLE_LIVE_ORDERS=False)")\n')

with open(trader_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# 3. rebalance.py
rebal_path = os.path.join(backend_dir, r'app\api\routes\rebalance.py')
with open(rebal_path, 'r', encoding='utf-8') as f:
    c = f.read()

if "from app.core.config import settings" not in c:
    c = "from app.core.config import settings\n" + c

with open(rebal_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if "def execute_rebalance" in lines[max(0, i-10):i+1] and line.strip().endswith("):"):
        new_lines.append('    # 결함 166 완결: Gate 1 dry-run 중 ENABLE_LIVE_ORDERS 미설정 시 HTTP 404 차단\n')
        new_lines.append('    if not getattr(settings, "ENABLE_LIVE_ORDERS", False):\n')
        new_lines.append('        raise HTTPException(status_code=404, detail="Live order execution is disabled in Gate 1 dry-run mode (ENABLE_LIVE_ORDERS=False)")\n')

with open(rebal_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

subprocess.run('git add app/api/routes/nvda.py app/api/routes/trader.py app/api/routes/rebalance.py', cwd=backend_dir, shell=True)
subprocess.run('git commit -m "fix(order_guards): cleanly inject 404 guard into nvda, trader, rebalance execution routes (defect 166)"', cwd=backend_dir, shell=True)
print("All execution routes safely guarded with 404!")
