with open(r'C:\trading\package\nvda_trading_system\backend\app\services\rebalance_engine.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace line 199 safely
old_chunk = '''            # 리스크 예측 (매도 시 단순 감소)
            risk_after = max(0, risk_before - 15)'''
# In case comment encoding differs, let's use regex or search for line
import re
code_new = re.sub(
    r'risk_after\s*=\s*max\(0,\s*risk_before\s*-\s*15\)[^\n]*',
    'risk_after = max(0, risk_before - 15) if risk_before is not None else None',
    code
)

summary_old = '''        risk_change = "▼" if risk_after < risk_before else "▲" if risk_after > risk_before else "━"

        summary = f"매도 {sell_count}건"
        if buy_count > 0:
            summary += f", 매수 {buy_count}건"
        summary += f" | 리스크 {risk_before}점 {risk_change} {risk_after}점"'''

# Let's inspect _generate_summary
code_new = re.sub(
    r'def _generate_summary\(self,\s*actions:\s*List\[Dict\],\s*risk_before:\s*[^)]+\)\s*->\s*str:',
    'def _generate_summary(self, actions: List[Dict], risk_before: Optional[int], risk_after: Optional[int]) -> str:',
    code_new
)

# And in _generate_summary body:
old_gen = '''        summary = f"매도 {sell_count}건"'''
# Let's see what is inside _generate_summary
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\rebalance_engine.py', 'w', encoding='utf-8') as f:
    f.write(code_new)

print("Updated rebalance_engine.py")
