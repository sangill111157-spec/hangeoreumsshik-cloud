# -*- coding: utf-8 -*-
import sys

app_file = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx'
with open(app_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Risk Gauge variables (lines 796~801)
t_risk_var = """  // Risk gauge
  const riskScore = riskData?.score || 0;
  const riskLevel = riskData?.level || 'LOW';
  const riskColor = riskLevel === 'HIGH' ? 'text-red-400' : riskLevel === 'MEDIUM' ? 'text-yellow-400' : 'text-emerald-400';
  const riskBgColor = riskLevel === 'HIGH' ? 'bg-red-500/10 border-red-500' : riskLevel === 'MEDIUM' ? 'bg-yellow-500/10 border-yellow-500' : 'bg-emerald-500/10 border-emerald-500';
  const riskGaugeWidth = Math.min(100, riskScore);"""

r_risk_var = """  // Risk gauge
  const hasRisk = riskData?.score != null;
  const riskScore = hasRisk ? riskData.score : null;
  const riskLevel = hasRisk ? (riskData.level || 'LOW') : null;
  const riskColor = !hasRisk ? 'text-gray-500' : riskLevel === 'HIGH' ? 'text-red-400' : riskLevel === 'MEDIUM' ? 'text-yellow-400' : 'text-emerald-400';
  const riskBgColor = !hasRisk ? 'bg-gray-500/10 border-gray-600' : riskLevel === 'HIGH' ? 'bg-red-500/10 border-red-500' : riskLevel === 'MEDIUM' ? 'bg-yellow-500/10 border-yellow-500' : 'bg-emerald-500/10 border-emerald-500';
  const riskGaugeWidth = hasRisk ? Math.min(100, riskScore) : 0;"""

# 2. Trader status variables
t_trader_var = """  // Trader status
  const hasTraderData = traderData != null;
  const traderMode = traderData?.mode || 'DRY_RUN';
  const todayTrades = hasTraderData ? (traderData.today_trades_count ?? 0) : null;"""

r_trader_var = """  // Trader status
  const hasTraderData = traderData != null;
  const traderMode = hasTraderData ? (traderData.mode || 'DRY_RUN') : null;
  const todayTrades = hasTraderData ? (traderData.today_trades_count ?? 0) : null;"""

# 3. Volume rendering
t_vol = """거래량 {price?.volume ? price.volume.toLocaleString() : '—'}"""
r_vol = """거래량 {price?.volume != null ? price.volume.toLocaleString() : '—'}"""

# 4. Risk gauge JSX
t_risk_jsx = """        {/* Risk Gauge (STEP 41) */}
        <div className={`rounded-xl p-4 border-2 ${riskBgColor}`}>
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">리스크 점수</p>
            <span className={`text-xs px-2 py-1 rounded ${riskBgColor}`}>
              {riskLevel}
            </span>
          </div>
          <div className="flex items-end gap-2">
            <p className={`text-3xl font-bold ${riskColor}`}>{riskScore}</p>
            <p className={`text-lg font-bold mb-1 ${riskColor}`}>/100</p>
          </div>
          {/* Risk Gauge Bar */}
          <div className="mt-2 bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${
                riskLevel === 'HIGH' ? 'bg-red-500' : riskLevel === 'MEDIUM' ? 'bg-yellow-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${riskGaugeWidth}%` }}
            />
          </div>
        </div>"""

r_risk_jsx = """        {/* Risk Gauge (STEP 41) */}
        <div className={`rounded-xl p-4 border-2 ${riskBgColor}`}>
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">리스크 점수</p>
            {hasRisk && riskLevel && (
              <span className={`text-xs px-2 py-1 rounded ${riskBgColor}`}>
                {riskLevel}
              </span>
            )}
          </div>
          <div className="flex items-end gap-2">
            <p className={`text-3xl font-bold ${riskColor}`}>{hasRisk ? riskScore : '—'}</p>
            {hasRisk && <p className={`text-lg font-bold mb-1 ${riskColor}`}>/100</p>}
          </div>
          {/* Risk Gauge Bar */}
          <div className="mt-2 bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${
                !hasRisk ? 'bg-gray-600' : riskLevel === 'HIGH' ? 'bg-red-500' : riskLevel === 'MEDIUM' ? 'bg-yellow-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${riskGaugeWidth}%` }}
            />
          </div>
        </div>"""

# 5. Trader card JSX
t_trader_jsx = """        {/* Auto Trader Status */}
        <div className={`rounded-xl p-4 border ${
          traderMode === 'DRY_RUN' ? 'bg-yellow-500/10 border-yellow-500/50' : 'bg-red-500/10 border-red-500/50'
        }`}>
          <div className="flex items-center gap-2 mb-2">
            <Zap className={`w-5 h-5 ${traderMode === 'DRY_RUN' ? 'text-yellow-400' : 'text-red-400'}`} />
            <p className="font-bold text-white">자동매매 상태</p>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-xl font-bold ${traderMode === 'DRY_RUN' ? 'text-yellow-400' : 'text-red-400'}`}>
                {traderMode}
              </p>"""

r_trader_jsx = """        {/* Auto Trader Status */}
        <div className={`rounded-xl p-4 border ${
          !hasTraderData ? 'bg-gray-500/10 border-gray-600' : traderMode === 'DRY_RUN' ? 'bg-yellow-500/10 border-yellow-500/50' : 'bg-red-500/10 border-red-500/50'
        }`}>
          <div className="flex items-center gap-2 mb-2">
            <Zap className={`w-5 h-5 ${!hasTraderData ? 'text-gray-500' : traderMode === 'DRY_RUN' ? 'text-yellow-400' : 'text-red-400'}`} />
            <p className="font-bold text-white">자동매매 상태</p>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-xl font-bold ${!hasTraderData ? 'text-gray-500' : traderMode === 'DRY_RUN' ? 'text-yellow-400' : 'text-red-400'}`}>
                {hasTraderData ? traderMode : '—'}
              </p>"""

for name, target, repl in [
    ('t_risk_var', t_risk_var, r_risk_var),
    ('t_trader_var', t_trader_var, r_trader_var),
    ('t_vol', t_vol, r_vol),
    ('t_risk_jsx', t_risk_jsx, r_risk_jsx),
    ('t_trader_jsx', t_trader_jsx, r_trader_jsx),
]:
    if target not in content:
        print(f"ERROR: {name} not found")
        sys.exit(1)
    content = content.replace(target, repl, 1)

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("PATCH STEP L-3 APPLIED SUCCESSFULLY")
