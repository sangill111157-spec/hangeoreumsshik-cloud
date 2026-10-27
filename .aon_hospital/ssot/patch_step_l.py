# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Variables definition
t1 = """  // Scanner candidates
  const candidates = scannerData?.final_candidates || [];
  const candidateCount = candidates.length;"""

r1 = """  // Scanner candidates
  const hasScanner = scannerData?.final_candidates != null;
  const candidates = hasScanner ? scannerData.final_candidates : null;
  const candidateCount = candidates ? candidates.length : null;"""

t2 = """  // Portfolio
  const portfolioValue = portfolioData?.summary?.total_value_usd || 0;
  const portfolioPnL = portfolioData?.summary?.total_profit_loss_pct || 0;"""

r2 = """  // Portfolio
  const hasPortfolio = portfolioData?.summary?.total_value_usd != null;
  const portfolioValue = hasPortfolio ? portfolioData.summary.total_value_usd : null;
  const portfolioPnL = hasPortfolio ? portfolioData.summary.total_profit_loss_pct : null;"""

# 2. Portfolio card render
t3 = """        {/* Portfolio Value */}
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <p className="text-gray-400 text-sm mb-1">포트폴리오 총자산</p>
          <p className="text-2xl font-bold text-white">${portfolioValue.toLocaleString('en-US', { maximumFractionDigits: 0 })}</p>
          <p className={`text-sm font-medium ${portfolioPnL >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {portfolioPnL >= 0 ? '+' : ''}{portfolioPnL.toFixed(2)}%
          </p>
        </div>"""

r3 = """        {/* Portfolio Value */}
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <p className="text-gray-400 text-sm mb-1">포트폴리오 총자산</p>
          <p className={`text-2xl font-bold ${hasPortfolio ? 'text-white' : 'text-gray-500'}`}>
            {hasPortfolio ? `$${portfolioValue.toLocaleString('en-US', { maximumFractionDigits: 0 })}` : '—'}
          </p>
          {hasPortfolio && portfolioPnL != null && (
            <p className={`text-sm font-medium ${portfolioPnL >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {portfolioPnL >= 0 ? '+' : ''}{portfolioPnL.toFixed(2)}%
            </p>
          )}
        </div>"""

# 3. Scanner card render
t4 = """          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-bold text-blue-400">{candidateCount}개</p>
              <p className="text-sm text-gray-400">후보 종목</p>
            </div>
            {candidateCount > 0 ? (
              <div className="text-right">
                {candidates.slice(0, 2).map((c: any, idx: number) => (
                  <p key={idx} className="text-sm text-white">{c.ticker} ({c.master_score}점)</p>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-400">조건 충족 종목 없음</p>
            )}
          </div>"""

r4 = """          <div className="flex items-center justify-between">
            <div>
              <p className={`text-2xl font-bold ${hasScanner ? 'text-blue-400' : 'text-gray-500'}`}>
                {hasScanner ? `${candidateCount}개` : '—'}
              </p>
              <p className="text-sm text-gray-400">후보 종목</p>
            </div>
            {!hasScanner ? (
              <p className="text-sm text-gray-500">조회 중...</p>
            ) : candidateCount! > 0 ? (
              <div className="text-right">
                {candidates!.slice(0, 2).map((c: any, idx: number) => (
                  <p key={idx} className="text-sm text-white">{c.ticker} ({c.master_score}점)</p>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-400">조건 충족 종목 없음</p>
            )}
          </div>"""

for name, t in [('t1', t1), ('t2', t2), ('t3', t3), ('t4', t4)]:
    if t not in content:
        print(f"ERROR: {name} NOT FOUND")
        sys.exit(1)

content = content.replace(t1, r1, 1)
content = content.replace(t2, r2, 1)
content = content.replace(t3, r3, 1)
content = content.replace(t4, r4, 1)

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("PATCH STEP L APPLIED SUCCESSFULLY")
