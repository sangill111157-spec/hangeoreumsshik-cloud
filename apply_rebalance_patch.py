with open(r'C:\trading\package\nvda_trading_system\backend\app\services\rebalance_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# line 199 (0-indexed 198):
for i, line in enumerate(lines):
    if 'risk_after = max(0, risk_before - 15)' in line:
        lines[i] = '            risk_after = max(0, risk_before - 15) if risk_before is not None else None\n'
        print("Updated line 199")

# line 276 (0-indexed 275):
for i, line in enumerate(lines):
    if '"improvement": plan.get("data", {}).get("risk_before", 0) - plan.get("data", {}).get("risk_after", 0)' in line:
        lines[i] = '                        "improvement": ((plan.get("data", {}).get("risk_before") or 0) - (plan.get("data", {}).get("risk_after") or 0))\n'
        print("Updated line 276")

# _generate_summary definition and body:
for i, line in enumerate(lines):
    if 'def _generate_summary(self, actions: List[Dict], risk_before: int, risk_after: int) -> str:' in line:
        lines[i] = '    def _generate_summary(self, actions: List[Dict], risk_before: Optional[int], risk_after: Optional[int]) -> str:\n'
        print("Updated _generate_summary signature")
    if 'summary += f" | ' in line and '{risk_before}' in line:
        # replace with conditional
        indent = line[:line.find('summary')]
        lines[i] = (
            f'{indent}if risk_before is not None and risk_after is not None:\n'
            f'{indent}    risk_change = "▼" if risk_after < risk_before else "▲" if risk_after > risk_before else "━"\n'
            f'{indent}    summary += f" | 리스크 {{risk_before}}점 {{risk_change}} {{risk_after}}점"\n'
            f'{indent}else:\n'
            f'{indent}    summary += " | 리스크: 미제공"\n'
        )
        print("Updated summary string")
    elif 'risk_change = ' in line and '{risk_before}' not in line and i > 280 and i < 300:
        # comment out or empty the previous risk_change line
        lines[i] = ''
        print("Cleared previous risk_change line")

with open(r'C:\trading\package\nvda_trading_system\backend\app\services\rebalance_engine.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Saved rebalance_engine.py")
