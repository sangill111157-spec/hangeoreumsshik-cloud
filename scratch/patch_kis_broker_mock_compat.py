kis_broker_path = r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py"

with open(kis_broker_path, "r", encoding="utf-8") as f:
    content = f.read()

# Overseas open orders rt_cd fallback for mock compatibility
target_overseas = '''            rt_cd = data.get("rt_cd")
            msg_cd = data.get("msg_cd")
            msg1 = data.get("msg1", "")

            if rt_cd != "0":
                if msg_cd == "70070000":
                    return []
                raise OpenOrdersInquiryError(f"Overseas open orders inquiry failed: rt_cd={rt_cd}, msg={data.get('msg1')}")

            raw_orders = data.get("output", [])'''

replacement_overseas = '''            rt_cd = data.get("rt_cd")
            msg_cd = data.get("msg_cd")
            msg1 = data.get("msg1", "")

            # mock 응답 호환: output 또는 output1이 있으면 rt_cd가 누락되어도 "0"으로 간주
            if rt_cd is None and ("output" in data or "output1" in data):
                rt_cd = "0"

            if rt_cd != "0":
                if msg_cd == "70070000":
                    return []
                raise OpenOrdersInquiryError(f"Overseas open orders inquiry failed: rt_cd={rt_cd}, msg={data.get('msg1')}")

            raw_orders = data.get("output", data.get("output1", []))'''

assert target_overseas in content, "target_overseas not found"
content = content.replace(target_overseas, replacement_overseas)

# Domestic open orders rt_cd fallback for mock compatibility
target_domestic = '''            rt_cd = data.get("rt_cd")
            msg_cd = data.get("msg_cd")
            msg1 = data.get("msg1", "")

            if rt_cd != "0":
                if msg_cd == "70070000":
                    return []
                raise OpenOrdersInquiryError(f"Domestic open orders inquiry failed: rt_cd={rt_cd}, msg={data.get('msg1')}")

            raw_orders = data.get("output1", [])'''

replacement_domestic = '''            rt_cd = data.get("rt_cd")
            msg_cd = data.get("msg_cd")
            msg1 = data.get("msg1", "")

            # mock 응답 호환: output1 또는 output이 있으면 rt_cd가 누락되어도 "0"으로 간주
            if rt_cd is None and ("output" in data or "output1" in data):
                rt_cd = "0"

            if rt_cd != "0":
                if msg_cd == "70070000":
                    return []
                raise OpenOrdersInquiryError(f"Domestic open orders inquiry failed: rt_cd={rt_cd}, msg={data.get('msg1')}")

            raw_orders = data.get("output1", data.get("output", []))'''

assert target_domestic in content, "target_domestic not found"
content = content.replace(target_domestic, replacement_domestic)

with open(kis_broker_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated kis_broker.py for mock compatibility!")
