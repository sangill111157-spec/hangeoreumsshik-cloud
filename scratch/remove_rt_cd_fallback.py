kis_broker_path = r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py"

with open(kis_broker_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove domestic open orders rt_cd fallback
old_dom = '''            rt_cd = data.get("rt_cd")
            if rt_cd is None and ("output" in data or "output1" in data):
                rt_cd = "0"
            if rt_cd != "0":'''

new_dom = '''            rt_cd = data.get("rt_cd")
            if rt_cd != "0":'''

assert old_dom in content, "old_dom not found in kis_broker.py"
content = content.replace(old_dom, new_dom)

# 2. Remove overseas open orders rt_cd fallback
old_ovrs = '''            rt_cd = data.get("rt_cd")
            if rt_cd is None and ("output" in data or "output1" in data):
                rt_cd = "0"
            if rt_cd != "0":'''

new_ovrs = '''            rt_cd = data.get("rt_cd")
            if rt_cd != "0":'''

assert old_ovrs in content, "old_ovrs not found in kis_broker.py"
content = content.replace(old_ovrs, new_ovrs)

with open(kis_broker_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully removed rt_cd fallback from kis_broker.py!")
