target = r"C:\trading\package\nvda_trading_system\backend\tests\test_scheduler_all_jobs_mock.py"

with open(target, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("patch('app.services.scheduler.get_auto_trader') as mock_trader:", "patch('app.services.scheduler.get_auto_trader'):")
c = c.replace('patch("app.services.scheduler.get_auto_trader") as mock_trader:', 'patch("app.services.scheduler.get_auto_trader"):')

with open(target, "w", encoding="utf-8") as f:
    f.write(c)

print("SUCCESS: mock_trader patched")
