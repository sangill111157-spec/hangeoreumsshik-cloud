kis_broker_path = r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py"

with open(kis_broker_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update tr_cont condition for domestic
old_dom_tr_cont = 'if tr_cont in ("M", "F") and (ctx_fk or ctx_nk):'
new_dom_tr_cont = 'if tr_cont in ("M", "F", "D") and (ctx_fk or ctx_nk):'
assert old_dom_tr_cont in content, "old_dom_tr_cont not found"
content = content.replace(old_dom_tr_cont, new_dom_tr_cont)

# 2. Update domestic return dict to include "cash"
old_dom_return = '''        return {
            "positions": list(positions_map.values()),
            "cash_balance_krw": cash_krw,
        }'''
new_dom_return = '''        return {
            "positions": list(positions_map.values()),
            "cash_balance_krw": cash_krw,
            "cash": cash_krw,
        }'''
assert old_dom_return in content, "old_dom_return not found"
content = content.replace(old_dom_return, new_dom_return)

# 3. Update overseas return dict to include "cash"
old_ovrs_return = '''        return {
            "positions": list(positions_map.values()),
            "cash_balance_usd": cash_usd,
        }'''
new_ovrs_return = '''        return {
            "positions": list(positions_map.values()),
            "cash_balance_usd": cash_usd,
            "cash": cash_usd,
        }'''
assert old_ovrs_return in content, "old_ovrs_return not found"
content = content.replace(old_ovrs_return, new_ovrs_return)

with open(kis_broker_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated kis_broker.py with tr_cont D and cash keys!")
