test_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_kis_broker_exchange_codes.py"

with open(test_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add rt_cd and msg_cd to mock response in test_get_open_orders_sync_exchange_codes_no_name_error
old_mock = '''    mock_resp.json.return_value = {
        "output1": ['''

new_mock = '''    mock_resp.json.return_value = {
        "rt_cd": "0",
        "msg_cd": "MCA00000",
        "output1": ['''

assert old_mock in content, "old_mock not found"
content = content.replace(old_mock, new_mock)

with open(test_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated test_kis_broker_exchange_codes.py with rt_cd and msg_cd!")
