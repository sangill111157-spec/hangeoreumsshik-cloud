import sys
import re

# 1. Patch app/services/kis_broker.py
with open(r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py", "r", encoding="utf-8") as f:
    code = f.read()

target_broker = '''    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client'''

replacement_broker = '''    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client (Event loop resilient across tasks/threads)"""
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        client_loop = getattr(self, "_client_loop", None)
        if (
            self._client is None
            or self._client.is_closed
            or client_loop != current_loop
            or (client_loop is not None and client_loop.is_closed())
        ):
            self._client = httpx.AsyncClient(timeout=30.0)
            self._client_loop = current_loop
        return self._client'''

if target_broker in code:
    code = code.replace(target_broker, replacement_broker, 1)
    with open(r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("kis_broker.py patched successfully")
else:
    print("kis_broker.py target NOT found")

# 2. Patch app/services/stock_scanner.py to add scan_watchlist
with open(r"C:\trading\package\nvda_trading_system\backend\app\services\stock_scanner.py", "r", encoding="utf-8") as f:
    code = f.read()

target_scanner = '''    async def run_scan(self, market: str = None) -> ScanResult:'''

replacement_scanner = '''    def scan_watchlist(self, market: str = "US") -> dict:
        """동기 인터페이스: 워치리스트 스캔 실행 및 결과 딕셔너리 반환 (hourly_scan 등 스케줄러 연동)"""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                res = pool.submit(asyncio.run, self.run_scan(market=market)).result()
        else:
            res = asyncio.run(self.run_scan(market=market))

        return {
            "candidates": res.final_candidates if res else [],
            "total_scanned": res.total_scanned if res else 0,
            "primary_passed": res.primary_passed if res else 0
        }

    async def run_scan(self, market: str = None) -> ScanResult:'''

if target_scanner in code and "def scan_watchlist" not in code:
    code = code.replace(target_scanner, replacement_scanner, 1)
    with open(r"C:\trading\package\nvda_trading_system\backend\app\services\stock_scanner.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("stock_scanner.py patched successfully")
else:
    print("stock_scanner.py target NOT found or already patched")
