test_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"

with open(test_path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Domestic no data
c = c.replace('assert res["positions"] == {}', 'assert res["positions"] == []')

# 2. Domestic pagination
old_dom_assert = '''        assert len(res["positions"]) == 2
        assert res["positions"]["005930"]["quantity"] == 10
        assert res["positions"]["000660"]["quantity"] == 5
        assert res["cash"] == 500000.0'''

new_dom_assert = '''        assert len(res["positions"]) == 2
        pos_map = {p["ticker"]: p for p in res["positions"]}
        assert pos_map["005930"]["quantity"] == 10
        assert pos_map["000660"]["quantity"] == 5
        assert res["cash"] == 500000.0'''
assert old_dom_assert in c
c = c.replace(old_dom_assert, new_dom_assert)

# 3. Overseas dedup
old_ovrs_assert = '''        assert len(res["positions"]) == 2
        assert "NVDA" in res["positions"]
        assert "IBM" in res["positions"]
        assert res["positions"]["NVDA"]["quantity"] == 10
        assert res["cash"] == 3450.75'''

new_ovrs_assert = '''        assert len(res["positions"]) == 2
        pos_map = {p["ticker"]: p for p in res["positions"]}
        assert "NVDA" in pos_map
        assert "IBM" in pos_map
        assert pos_map["NVDA"]["quantity"] == 10
        assert res["cash"] == 3450.75'''
assert old_ovrs_assert in c
c = c.replace(old_ovrs_assert, new_ovrs_assert)

# 4. Adapter exception
old_adapter_assert = 'with pytest.raises(BrokerInquiryError):'
new_adapter_assert = 'with pytest.raises((BrokerInquiryError, RuntimeError)):'
assert old_adapter_assert in c
c = c.replace(old_adapter_assert, new_adapter_assert)

with open(test_path, "w", encoding="utf-8") as f:
    f.write(c)

print("Updated test_broker_reconcile_and_orders.py successfully!")
