import sys

# 1. Update stock_scanner.py
path = r"C:\trading\package\nvda_trading_system\backend\app\services\stock_scanner.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

t1 = """    volume_ratio: float = 0.0
    bollinger_position: float = 0.0
    investor_buy_count: int = 0"""
r1 = """    volume_ratio: Optional[float] = None
    bollinger_position: float = 0.0
    investor_buy_count: Optional[int] = None"""
assert t1 in code, "t1 not found"
code = code.replace(t1, r1, 1)

t2 = """            # Mock investor data (in real implementation, would call investor analysis service)
            # For now, use technical signals as proxy
            investor_buy_count = 0
            if tech_result.rsi.value < 35:
                investor_buy_count += 1
            if tech_result.macd.histogram > 0:
                investor_buy_count += 1
            if bb.position < 20:
                investor_buy_count += 1
            if bollinger_position < 10:
                investor_buy_count += 1"""

r2 = """            # 미국 종목은 실제 기관/외인 수급 데이터가 부재하므로 null(None) 처리 (가짜 프록시 제거)
            if market == "US":
                investor_buy_count = None
            else:
                investor_buy_count = None"""
assert t2 in code, "t2 not found"
code = code.replace(t2, r2, 1)

t3 = """                volume_ratio=volume / avg_volume if avg_volume > 0 else 1.0,"""
r3 = """                volume_ratio=(volume / avg_volume) if (avg_volume > 0 and volume is not None and volume > 0) else None,"""
assert t3 in code, "t3 not found"
code = code.replace(t3, r3, 1)

t4 = """                    if candidate.investor_buy_count >= self.config["secondary_filters"]["min_investor_buy_count"]:"""
r4 = """                    min_inv = self.config["secondary_filters"]["min_investor_buy_count"]
                    if candidate.investor_buy_count is None or candidate.investor_buy_count >= min_inv:"""
assert t4 in code, "t4 not found"
code = code.replace(t4, r4, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)
print("SUCCESS: updated stock_scanner.py")
