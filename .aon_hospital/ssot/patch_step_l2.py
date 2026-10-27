# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Variables
t1 = """  // Trader status
  const traderMode = traderData?.mode || 'DRY_RUN';
  const todayTrades = traderData?.today_trades_count || 0;

  // Portfolio
  const hasPortfolio = portfolioData?.summary?.total_value_usd != null;
  const portfolioValue = hasPortfolio ? portfolioData.summary.total_value_usd : null;
  const portfolioPnL = hasPortfolio ? portfolioData.summary.total_profit_loss_pct : null;

  // Master signal
  const masterScore = masterSignal?.master_score || 50;
  const masterSignalText = masterSignal?.signal_ko || '보유';"""

r1 = """  // Trader status
  const hasTraderData = traderData != null;
  const traderMode = traderData?.mode || 'DRY_RUN';
  const todayTrades = hasTraderData ? (traderData.today_trades_count ?? 0) : null;

  // Portfolio
  const hasPortfolio = portfolioData?.summary?.total_value_usd != null;
  const portfolioValue = hasPortfolio ? portfolioData.summary.total_value_usd : null;
  const portfolioPnL = hasPortfolio ? portfolioData.summary.total_profit_loss_pct : null;

  // Master signal
  const hasMasterSignal = masterSignal?.master_score != null;
  const masterScore = hasMasterSignal ? masterSignal.master_score : null;
  const masterSignalText = hasMasterSignal ? (masterSignal?.signal_ko || '보유') : '—';"""

# 2. Master signal card
t2 = """        {/* Master Signal Score */}
        <div className={`rounded-xl p-4 border-2 ${
          masterSignal?.signal === 'BUY' ? 'bg-emerald-500/10 border-emerald-500' :
          masterSignal?.signal === 'SELL' ? 'bg-red-500/10 border-red-500' :
          'bg-amber-500/10 border-amber-500'
        }`}>
          <p className="text-gray-400 text-sm mb-1">마스터시그널</p>
          <div className="flex items-end gap-2">
            <p className="text-3xl font-bold text-white">{masterScore.toFixed(0)}</p>
            <p className={`text-lg font-bold mb-1 ${
              masterSignal?.signal === 'BUY' ? 'text-emerald-400' :
              masterSignal?.signal === 'SELL' ? 'text-red-400' : 'text-amber-400'
            }`}>
              {masterSignalText}
            </p>
          </div>
        </div>"""

r2 = """        {/* Master Signal Score */}
        <div className={`rounded-xl p-4 border-2 ${
          !hasMasterSignal ? 'bg-gray-500/10 border-gray-600' :
          masterSignal?.signal === 'BUY' ? 'bg-emerald-500/10 border-emerald-500' :
          masterSignal?.signal === 'SELL' ? 'bg-red-500/10 border-red-500' :
          'bg-amber-500/10 border-amber-500'
        }`}>
          <p className="text-gray-400 text-sm mb-1">마스터시그널</p>
          <div className="flex items-end gap-2">
            <p className={`text-3xl font-bold ${hasMasterSignal ? 'text-white' : 'text-gray-500'}`}>
              {hasMasterSignal ? masterScore.toFixed(0) : '—'}
            </p>
            <p className={`text-lg font-bold mb-1 ${
              !hasMasterSignal ? 'text-gray-500' :
              masterSignal?.signal === 'BUY' ? 'text-emerald-400' :
              masterSignal?.signal === 'SELL' ? 'text-red-400' : 'text-amber-400'
            }`}>
              {masterSignalText}
            </p>
          </div>
        </div>"""

# 3. Today trades render
t3 = """<p className="text-sm text-gray-400">오늘 거래 {todayTrades}건</p>"""
r3 = """<p className="text-sm text-gray-400">오늘 거래 {hasTraderData ? `${todayTrades}건` : '—'}</p>"""

for name, t in [('t1', t1), ('t2', t2), ('t3', t3)]:
    if t not in content:
        print(f"ERROR: {name} NOT FOUND")
        sys.exit(1)

content = content.replace(t1, r1, 1)
content = content.replace(t2, r2, 1)
content = content.replace(t3, r3, 1)

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("PATCH STEP L-2 APPLIED SUCCESSFULLY")
