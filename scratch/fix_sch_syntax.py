# -*- coding: utf-8 -*-
from pathlib import Path

sch_file = Path(r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py")
text = sch_file.read_text(encoding="utf-8", errors="ignore")

# 라인 1024, 1030 교정
text = text.replace('self._send_telegram("\n".join(lines))', 'self._send_telegram("\\n".join(lines))')
text = text.replace('self._send_telegram(f"⚠️ *스캔 오류 발생*\n{str(e)}")', 'self._send_telegram(f"⚠️ *스캔 오류 발생*\\n{str(e)}")')
text = text.replace('self._send_telegram("\r\n".join(lines))', 'self._send_telegram("\\n".join(lines))')
text = text.replace('self._send_telegram(f"⚠️ *스캔 오류 발생*\r\n{str(e)}")', 'self._send_telegram(f"⚠️ *스캔 오류 발생*\\n{str(e)}")')

sch_file.write_text(text, encoding="utf-8")
print("교정 완료")
