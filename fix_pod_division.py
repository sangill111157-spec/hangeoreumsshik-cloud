import re

with open(r'C:\trading\package\nvda_trading_system\backend\app\services\pod_manager.py', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = r'(\s+# Growth potential\s+price_vs_52w_high = \(1 - \(current_price / stock_info\.get\("week_52_high", current_price\)\)\) \* 100[\s\S]*?score -= 15)'

replacement = '''        # Growth potential
        w52_high = float(stock_info.get("week_52_high") or 0.0)
        if w52_high > 0 and current_price > 0:
            price_vs_52w_high = (1 - (current_price / w52_high)) * 100
            if price_vs_52w_high > 30:
                factors.append(f"52주 고점 대비 ({price_vs_52w_high:.0f}% 하락)")
                score += 20
            elif price_vs_52w_high > 15:
                factors.append("52주 중간 반등")
                score += 5
            else:
                factors.append("52주 고점 근처")
                score -= 15
        else:
            factors.append("52주 고점 데이터 부족")'''

new_text, count = re.subn(pattern, replacement, text, count=1)
if count > 0:
    with open(r'C:\trading\package\nvda_trading_system\backend\app\services\pod_manager.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print(f"Fixed {count} instances of zero-division")
else:
    print("Pattern not found")
