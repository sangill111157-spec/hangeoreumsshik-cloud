conftest_path = r"C:\trading\package\nvda_trading_system\backend\tests\conftest.py"
with open(conftest_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = ["import pytest\n"] + [line for line in lines if line.strip() != "import pytest"]
with open(conftest_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("Updated conftest.py with import pytest at the top.")
