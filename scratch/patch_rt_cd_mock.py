kis_broker_path = r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py"

with open(kis_broker_path, "r", encoding="utf-8") as f:
    content = f.read()

# Domestic
old_dom = '''            if data.get("rt_cd") != "0":
                if data.get("msg_cd") == "70070000":
                    return []
                raise OpenOrdersInquiryError(f"Domestic open orders inquiry failed: rt_cd={data.get('rt_cd')}, msg={data.get('msg1')}")'''

new_dom = '''            rt_cd = data.get("rt_cd")
            if rt_cd is None and ("output" in data or "output1" in data):
                rt_cd = "0"
            if rt_cd != "0":
                if data.get("msg_cd") == "70070000":
                    return []
                raise OpenOrdersInquiryError(f"Domestic open orders inquiry failed: rt_cd={rt_cd}, msg={data.get('msg1')}")'''

assert old_dom in content, "old_dom not found"
content = content.replace(old_dom, new_dom)

# Overseas
old_ovrs = '''            if data.get("rt_cd") != "0":
                if data.get("msg_cd") == "70070000":
                    return []
                raise OpenOrdersInquiryError(f"Overseas open orders inquiry failed: rt_cd={data.get('rt_cd')}, msg={data.get('msg1')}")'''

new_ovrs = '''            rt_cd = data.get("rt_cd")
            if rt_cd is None and ("output" in data or "output1" in data):
                rt_cd = "0"
            if rt_cd != "0":
                if data.get("msg_cd") == "70070000":
                    return []
                raise OpenOrdersInquiryError(f"Overseas open orders inquiry failed: rt_cd={rt_cd}, msg={data.get('msg1')}")'''

assert old_ovrs in content, "old_ovrs not found"
content = content.replace(old_ovrs, new_ovrs)

with open(kis_broker_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated kis_broker.py open orders mock compatibility!")
