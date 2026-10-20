import re

with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. DashboardView 변수 영역에 nowTime 정의 및 hasRisk, hasPrice 강화
var_target = '''  const currency = market === 'KR' ? '₩' : '$';
  const hasPrice = price?.current_price != null;
  const priceDisplay = hasPrice
    ? price.current_price.toFixed(market === 'KR' ? 0 : 2)
    : null;

  // Risk gauge
  const hasRisk = riskData?.score != null;
  const riskScore = hasRisk ? riskData.score : null;
  const riskLevel = hasRisk ? (riskData.level || 'LOW') : null;'''

var_replacement = '''  const currency = market === 'KR' ? '₩' : '$';
  const nowTime = new Date().toLocaleTimeString('ko-KR', { hour12: false });
  const hasPrice = price?.current_price != null && price?.current_price > 0 && price?.available !== false;
  const priceDisplay = hasPrice
    ? price.current_price.toFixed(market === 'KR' ? 0 : 2)
    : null;

  // Risk gauge (데이터 미연결 시 LOW 기본값 방지)
  const hasRisk = riskData?.score != null && riskData?.available !== false;
  const riskScore = hasRisk ? riskData.score : null;
  const rawRiskLevel = hasRisk ? riskData.level : null;
  const riskLevel = rawRiskLevel === 'HIGH' ? '높음' : rawRiskLevel === 'MEDIUM' ? '보통' : rawRiskLevel === 'LOW' ? '낮음' : null;'''

text = text.replace(var_target, var_replacement, 1)

# 2. 리스크 게이지 렌더링 영역 한글화 및 데이터 없음 표시
risk_target = '''        {/* Risk Gauge (STEP 41) */}
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
        </div>'''

risk_replacement = '''        {/* Risk Gauge (STEP 41) */}
        <div className={`rounded-xl p-4 border-2 ${riskBgColor}`}>
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">리스크 점수</p>
            {hasRisk && riskLevel && (
              <span className={`text-xs px-2 py-1 rounded font-bold ${riskBgColor}`}>
                {riskLevel}
              </span>
            )}
          </div>
          <div className="flex items-end gap-2">
            <p className={`text-3xl font-bold ${riskColor}`}>{hasRisk ? riskScore : '데이터 없음'}</p>
            {hasRisk && <p className={`text-lg font-bold mb-1 ${riskColor}`}>/100</p>}
          </div>
          {/* Risk Gauge Bar */}
          <div className="mt-2 bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${
                !hasRisk ? 'bg-gray-600' : rawRiskLevel === 'HIGH' ? 'bg-red-500' : rawRiskLevel === 'MEDIUM' ? 'bg-yellow-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${riskGaugeWidth}%` }}
            />
          </div>
          <p className="text-[10px] text-gray-500 mt-2 text-right">갱신: {nowTime}</p>
        </div>'''

text = text.replace(risk_target, risk_replacement, 1)

# 3. 현재가, 마스터시그널, 포트폴리오 카드에 갱신 시각 및 translate="no" 추가
price_card_target = '''        {/* NVDA Price */}
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
            거래량 {price?.volume != null ? price.volume.toLocaleString() : '—'}
          </p>
        </div>'''

price_card_replacement = '''        {/* NVDA Price */}
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm"><span translate="no">{ticker || 'NVDA'}</span> 현재가</p>
            {hasPrice && price?.change_percent != null && (
              <span className={`text-xs px-2 py-1 rounded ${isPositive ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                {isPositive ? '+' : ''}{price.change_percent.toFixed(2)}%
              </span>
            )}
          </div>
          <p className={`text-2xl font-bold ${!hasPrice ? 'text-gray-500' : isPositive ? 'text-emerald-400' : 'text-red-400'}`}>
            {hasPrice ? `${currency}${priceDisplay}` : '데이터 없음'}
          </p>
          <div className="flex justify-between items-center text-xs text-gray-400 mt-1">
            <span>거래량 {price?.volume != null && price.volume > 0 ? price.volume.toLocaleString() : '—'}</span>
            <span className="text-[10px] text-gray-500">갱신: {nowTime}</span>
          </div>
        </div>'''

text = text.replace(price_card_target, price_card_replacement, 1)

# 마스터 시그널 카드 갱신 시각 추가
signal_card_target = '''            <p className={`text-xs ${
              !hasMasterSignal ? 'text-gray-500' :
              masterSignal?.signal === 'BUY' ? 'text-emerald-400' :
              masterSignal?.signal === 'SELL' ? 'text-red-400' : 'text-amber-400'
            }`}>
              {masterSignalText}
            </p>
          </div>
        </div>'''

signal_card_replacement = '''            <p className={`text-xs ${
              !hasMasterSignal ? 'text-gray-500' :
              masterSignal?.signal === 'BUY' ? 'text-emerald-400' :
              masterSignal?.signal === 'SELL' ? 'text-red-400' : 'text-amber-400'
            }`}>
              {masterSignalText}
            </p>
          </div>
          <p className="text-[10px] text-gray-500 mt-2 text-right">갱신: {nowTime}</p>
        </div>'''

text = text.replace(signal_card_target, signal_card_replacement, 1)

# 포트폴리오 카드 갱신 시각 추가
port_card_target = '''          {hasPortfolio && portfolioPnL != null && (
            <p className={`text-sm font-medium ${portfolioPnL >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {portfolioPnL >= 0 ? '+' : ''}{portfolioPnL.toFixed(2)}%
            </p>
          )}
        </div>'''

port_card_replacement = '''          {hasPortfolio && portfolioPnL != null && (
            <p className={`text-sm font-medium ${portfolioPnL >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {portfolioPnL >= 0 ? '+' : ''}{portfolioPnL.toFixed(2)}%
            </p>
          )}
          <p className="text-[10px] text-gray-500 mt-2 text-right">갱신: {nowTime}</p>
        </div>'''

text = text.replace(port_card_target, port_card_replacement, 1)

# 4. 7개 모듈 영역: 상태 문구(두뇌 미연결/오류) 및 "데이터 있음 / 없음" 배지 추가
modules_target = '''        {modules ? (
          <div className="space-y-3">
            {modules.map((mod: any, idx: number) => {
              const style =
                (mod.signal === 'BUY' || mod.signal === 'STRONG_BUY')
                  ? { bar: 'bg-emerald-400', chip: 'bg-emerald-400/20 text-emerald-400' }
                : (mod.signal === 'SELL' || mod.signal === 'STRONG_SELL')
                  ? { bar: 'bg-red-400', chip: 'bg-red-400/20 text-red-400' }
                  : { bar: 'bg-amber-400', chip: 'bg-amber-400/20 text-amber-400' };

              const barWidth = Math.max(0, Math.min(100, Number(mod.score) || 0));
              const signalLabel = mod.signal === 'STRONG_BUY' ? 'S.BUY' : mod.signal === 'BUY' ? 'BUY' : mod.signal === 'STRONG_SELL' ? 'S.SELL' : mod.signal === 'SELL' ? 'SELL' : 'HOLD';
              return (
                <div key={idx} className="flex items-center gap-3">
                  <div className="w-24 text-sm text-gray-400">{mod.name}</div>
                  <div className="flex-1 bg-gray-700 rounded-full h-4 overflow-hidden">
                    <div
                      className={`h-full ${style.bar} rounded-full`}
                      style={{ width: `${barWidth}%` }}
                    />
                  </div>
                  <div className="w-12 text-right">
                    <span className="text-sm font-bold text-white">
                      {typeof mod.score === 'number' ? mod.score.toFixed(1) : mod.score}
                    </span>
                  </div>
                  <div className={`w-16 px-2 py-1 rounded text-xs font-bold text-center ${style.chip}`}>
                    {signalLabel}
                  </div>
                </div>
              );
            })}
          </div>
        ) : masterSignalError ? (
          <div className="text-center py-6">
            <p className="text-sm text-red-400 mb-3">
              모듈 분석을 불러오지 못했습니다 ({masterSignalError})
            </p>
            <button
              onClick={onRetryMasterSignal}
              className="px-4 py-2 text-sm rounded bg-gray-700 text-white hover:bg-gray-600"
            >
              다시 시도
            </button>
          </div>
        ) : ('''

modules_replacement = '''        {modules ? (
          <div className="space-y-3">
            {masterSignal?.blocked_by_gate && (
              <div className="mb-3 px-3 py-2 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs flex justify-between items-center">
                <span>두뇌 미연결 - 비활성(정상 차단)</span>
                <span className="text-gray-400">갱신: {nowTime}</span>
              </div>
            )}
            {modules.map((mod: any, idx: number) => {
              const hasData = mod.score != null && mod.signal !== 'UNAVAILABLE';
              const style = !hasData
                ? { bar: 'bg-gray-600', chip: 'bg-gray-700 text-gray-400' }
                : (mod.signal === 'BUY' || mod.signal === 'STRONG_BUY')
                ? { bar: 'bg-emerald-400', chip: 'bg-emerald-400/20 text-emerald-400' }
                : (mod.signal === 'SELL' || mod.signal === 'STRONG_SELL')
                ? { bar: 'bg-red-400', chip: 'bg-red-400/20 text-red-400' }
                : { bar: 'bg-amber-400', chip: 'bg-amber-400/20 text-amber-400' };

              const barWidth = hasData ? Math.max(0, Math.min(100, Number(mod.score) || 0)) : 0;
              const signalLabel = !hasData ? '미제공' : mod.signal === 'STRONG_BUY' ? '적극매수' : mod.signal === 'BUY' ? '매수' : mod.signal === 'STRONG_SELL' ? '적극매도' : mod.signal === 'SELL' ? '매도' : '보류';
              return (
                <div key={idx} className="flex items-center gap-3">
                  <div className="w-28 text-sm text-gray-400 flex items-center justify-between">
                    <span>{mod.name}</span>
                  </div>
                  <div className="flex-1 bg-gray-700 rounded-full h-4 overflow-hidden">
                    <div
                      className={`h-full ${style.bar} rounded-full`}
                      style={{ width: `${barWidth}%` }}
                    />
                  </div>
                  <div className="w-14 text-right">
                    <span className="text-sm font-bold text-white">
                      {hasData ? (typeof mod.score === 'number' ? mod.score.toFixed(1) : mod.score) : '—'}
                    </span>
                  </div>
                  <div className={`w-20 px-2 py-1 rounded text-xs font-bold text-center ${style.chip}`}>
                    {signalLabel}
                  </div>
                  <div className="w-24 text-right">
                    <span className={`text-[11px] px-2 py-0.5 rounded font-medium ${hasData ? 'bg-emerald-500/20 text-emerald-400' : 'bg-gray-700 text-gray-400'}`}>
                      {hasData ? '데이터 있음' : '데이터 없음'}
                    </span>
                  </div>
                </div>
              );
            })}
            <p className="text-[10px] text-gray-500 text-right pt-2">마지막 갱신: {nowTime}</p>
          </div>
        ) : masterSignalError ? (
          <div className="text-center py-6">
            <p className="text-sm font-medium mb-3 text-amber-400">
              {masterSignalError.includes('의도') || masterSignalError.includes('차단') || masterSignalError.includes('GATE')
                ? '두뇌 미연결 - 비활성(정상 차단)'
                : `오류: ${masterSignalError}`}
            </p>
            <button
              onClick={onRetryMasterSignal}
              className="px-4 py-2 text-sm rounded bg-gray-700 text-white hover:bg-gray-600"
            >
              다시 시도
            </button>
            <p className="text-[10px] text-gray-500 mt-2">갱신 시각: {nowTime}</p>
          </div>
        ) : ('''

text = text.replace(modules_target, modules_replacement, 1)

# 5. Quick Stats Row (RSI, 추세, MACD 가짜값 제거 및 translate="no")
quick_stats_target = '''      {/* Quick Stats Row */}
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
        </div>'''

quick_stats_replacement = '''      {/* Quick Stats Row */}
      <div className="grid grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-xs" translate="no">RSI</p>
          <p className={`text-lg font-bold ${
            !technical?.available || technical?.rsi?.value == null ? 'text-gray-500' : technical.rsi.value > 70 ? 'text-red-400' : technical.rsi.value < 30 ? 'text-emerald-400' : 'text-white'
          }`}>
            {technical?.available && technical?.rsi?.value != null ? technical.rsi.value.toFixed(0) : '데이터 없음'}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-xs">추세</p>
          <p className={`text-lg font-bold ${
            !technical?.available || technical == null ? 'text-gray-500' : technical?.trend?.includes('up') ? 'text-emerald-400' : technical?.trend?.includes('down') ? 'text-red-400' : 'text-amber-400'
          }`}>
            {!technical?.available || technical == null ? '데이터 없음' : technical?.trend === 'uptrend' ? '상승' : technical?.trend === 'downtrend' ? '하락' : '중립'}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <p className="text-gray-400 text-xs" translate="no">MACD</p>
          <p className={`text-lg font-bold ${
            !technical?.available || technical?.macd?.histogram == null ? 'text-gray-500' : technical.macd.histogram >= 0 ? 'text-emerald-400' : 'text-red-400'
          }`}>
            {technical?.available && technical?.macd?.histogram != null
              ? `${technical.macd.histogram >= 0 ? '+' : ''}${technical.macd.histogram.toFixed(2)}`
              : '데이터 없음'}
          </p>
        </div>'''

text = text.replace(quick_stats_target, quick_stats_replacement, 1)

with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("Part 2 applied successfully")
