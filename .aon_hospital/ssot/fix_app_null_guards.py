# -*- coding: utf-8 -*-
import sys, os

frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'
app_path = os.path.join(frontend_dir, r'src\App.tsx')

with open(app_path, 'r', encoding='utf-8') as f:
    app_c = f.read()

# Replace stop_loss section with perfect null guards for all 4 fields
old_sl_block = """              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                <p className="text-gray-400 text-xs">스톱로스</p>
                <p className="text-xl font-bold text-red-400">${data?.kelly?.stop_loss?.toFixed(2)}</p>
                <p className="text-xs text-red-400">(-{data?.kelly?.stop_loss_pct}%)</p>
              </div>"""

new_sl_block = """              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                <p className="text-gray-400 text-xs">스톱로스</p>
                <p className="text-xl font-bold text-red-400">
                  {data?.kelly?.stop_loss != null ? `$${data.kelly.stop_loss.toFixed(2)}` : '—'}
                </p>
                <p className="text-xs text-red-400">
                  {data?.kelly?.stop_loss_pct != null ? `(-${data.kelly.stop_loss_pct}%)` : '진입 보류'}
                </p>
              </div>"""

if old_sl_block in app_c:
    app_c = app_c.replace(old_sl_block, new_sl_block)
else:
    # generic replace for safety
    app_c = app_c.replace("${data?.kelly?.stop_loss?.toFixed(2)}", "{data?.kelly?.stop_loss != null ? `$${data.kelly.stop_loss.toFixed(2)}` : '—'}")
    app_c = app_c.replace("(-{data?.kelly?.stop_loss_pct}%)", "{data?.kelly?.stop_loss_pct != null ? `(-${data.kelly.stop_loss_pct}%)` : '진입 보류'}")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_c)

print("App.tsx null guards for stop_loss and stop_loss_pct applied perfectly.")
