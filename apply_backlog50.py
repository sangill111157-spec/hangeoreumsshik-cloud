# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\backend\app\core\config.py'

with open(target_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Verify current lines
assert lines[10] == 'class Settings(BaseSettings):\n'
assert lines[11] == '    ENABLE_TEST_ENDPOINTS: bool = False\n'
assert lines[12] == '    ENABLE_LIVE_ORDERS: Optional[str] = Field(default=None, description="Live order gate token")\n'
assert lines[13] == '    ALLOW_ORDER_EXECUTION: Optional[str] = Field(default=None, description="Allow order execution token")\n'
assert lines[14] == '    """Application Settings - Pydantic BaseSettings"""\n'
assert lines[15] == '\n'

docstring = lines.pop(14)
lines.insert(11, docstring)

with open(target_file, 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(lines)

print('Backlog 50 applied cleanly!')
