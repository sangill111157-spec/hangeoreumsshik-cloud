# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. priceDisplay definition
t1 = """  const currency = market === 'KR' ? '₩' : '$';
  const priceDisplay = price?.current_price?.toFixed(market === 'KR' ? 0 : 2) || '0';"""

r1 = """  const currency = market === 'KR' ? '₩' : '$';
  const hasPrice = price?.current_price != null;
  const priceDisplay = hasPrice
    ? price.current_price.toFixed(market === 'KR' ? 0 : 2)
    : null;"""

# 2. Price card
t2 = """        {/* NVDA Price */}
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">NVDA 현재가</p>
            <span className={`text-xs px-2 py-1 rounded ${isPositive ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
              {isPositive ? '+' : ''}{price?.change_percent?.toFixed(2) || 0}%
            </span>
          </div>
          <p className={`text-2xl font-bold ${isPositive ? 'text-emerald-400' : 'text-red-400'}`}>
            ${priceDisplay}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            거래량 {price?.volume ? price.volume.toLocaleString() : '—'}
          </p>
        </div>"""

r2 = """        {/* NVDA Price */}
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">NVDA 현재가</p>
            {hasPrice && price?.change_percent != null && (
              <span className={`text-xs px-2 py-1 rounded ${isPositive ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                {isPositive ? '+' : ''}{price.change_percent.toFixed(2)}%
              </span>
            )}
          </div>
          <p className={`text-2xl font-bold ${!hasPrice ? 'text-gray-500' : isPositive ? 'text-emerald-400' : 'text-red-400'}`}>
            {hasPrice ? `${currency}${priceDisplay}` : '—'}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            거래량 {price?.volume ? price.volume.toLocaleString() : '—'}
          </p>
        </div>"""

# 3. Quick Stats row
t3 = """      {/* Quick Stats Row */}
      <div className="grid grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-xs">RSI</p>
          <p className={`text-lg font-bold ${
            technical?.rsi?.value > 70 ? 'text-red-400' : technical?.rsi?.value < 30 ? 'text-emerald-400' : 'text-white'
          }`}>
            {technical?.rsi?.value?.toFixed(0) || 'N/A'}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-xs">추세</p>
          <p className={`text-lg font-bold ${
            technical?.trend?.includes('up') ? 'text-emerald-400' : technical?.trend?.includes('down') ? 'text-red-400' : 'text-amber-400'
          }`}>
            {technical?.trend === 'uptrend' ? '상승' : technical?.trend === 'downtrend' ? '하락' : '중립'}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-xs">MACD</p>
          <p className={`text-lg font-bold ${technical?.macd?.histogram >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {technical?.macd?.histogram >= 0 ? '+' : ''}{technical?.macd?.histogram?.toFixed(2) || '0'}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-xs">현재가</p>
          <p className="text-lg font-bold text-white">${priceDisplay}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-xs">보유</p>
          <p className="text-lg font-bold text-blue-400">{nvdaHolding?.quantity || 0}주</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-xs">손익</p>
          <p className={`text-lg font-bold ${(nvdaHolding?.profit_loss || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {(nvdaHolding?.profit_loss || 0) >= 0 ? '+' : ''}${(nvdaHolding?.profit_loss || 0).toFixed(0)}
          </p>
        </div>
      </div>"""

r3 = """      {/* Quick Stats Row */}
      <div className="grid grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-xs">RSI</p>
          <p className={`text-lg font-bold ${
            technical?.rsi?.value == null ? 'text-gray-500' : technical.rsi.value > 70 ? 'text-red-400' : technical.rsi.value < 30 ? 'text-emerald-400' : 'text-white'
          }`}>
            {technical?.rsi?.value != null ? technical.rsi.value.toFixed(0) : '—'}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-xs">추세</p>
          <p className={`text-lg font-bold ${
            technical == null ? 'text-gray-500' : technical?.trend?.includes('up') ? 'text-emerald-400' : technical?.trend?.includes('down') ? 'text-red-400' : 'text-amber-400'
          }`}>
            {technical == null ? '—' : technical?.trend === 'uptrend' ? '상승' : technical?.trend === 'downtrend' ? '하락' : '중립'}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-xs">MACD</p>
          <p className={`text-lg font-bold ${
            technical?.macd?.histogram == null ? 'text-gray-500' : technical.macd.histogram >= 0 ? 'text-emerald-400' : 'text-red-400'
          }`}>
            {technical?.macd?.histogram != null
              ? `${technical.macd.histogram >= 0 ? '+' : ''}${technical.macd.histogram.toFixed(2)}`
              : '—'}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-xs">현재가</p>
          <p className={`text-lg font-bold ${hasPrice ? 'text-white' : 'text-gray-500'}`}>
            {hasPrice ? `${currency}${priceDisplay}` : '—'}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-xs">보유</p>
          <p className={`text-lg font-bold ${nvdaHolding == null ? 'text-gray-500' : 'text-blue-400'}`}>
            {nvdaHolding == null ? '—' : `${nvdaHolding.quantity ?? 0}주`}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-xs">손익</p>
          <p className={`text-lg font-bold ${
            nvdaHolding == null ? 'text-gray-500' : (nvdaHolding.profit_loss ?? 0) >= 0 ? 'text-emerald-400' : 'text-red-400'
          }`}>
            {nvdaHolding == null
              ? '—'
              : `${(nvdaHolding.profit_loss ?? 0) >= 0 ? '+' : ''}${currency}${(nvdaHolding.profit_loss ?? 0).toFixed(0)}`}
          </p>
        </div>
      </div>"""

checks = [('t1', t1), ('t2', t2), ('t3', t3)]
for name, t in checks:
    if t not in content:
        print(f"ERROR: {name} NOT FOUND")
        sys.exit(1)

content = content.replace(t1, r1, 1)
content = content.replace(t2, r2, 1)
content = content.replace(t3, r3, 1)

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("PATCH STEP H APPLIED SUCCESSFULLY")
