# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. State declaration
t1 = """  const [masterSignalData, setMasterSignalData] = useState<any>(null);"""
r1 = """  const [masterSignalData, setMasterSignalData] = useState<any>(null);
  const [masterSignalError, setMasterSignalError] = useState<string | null>(null);"""

# 2. Search ticker reset (line 109)
t2 = """    setMasterSignalData(null);"""
r2 = """    setMasterSignalData(null);
    setMasterSignalError(null);"""

# 3. loadMasterSignalData & useEffect
t3 = """  const masterLoadingRef = useRef(false);
  const loadMasterSignalData = async () => {
    if (masterLoadingRef.current) return;
    masterLoadingRef.current = true;
    const targetTicker = currentTicker;
    try {
      const data = await api.fetchSignal(targetTicker) as any;
      if (targetTicker === currentTicker) {
        setMasterSignalData(data);
      }
    } catch (err) {
      console.warn('Failed to load master signal:', err);
    } finally {
      masterLoadingRef.current = false;
    }
  };

  useEffect(() => {
    if (activeTab === 'dashboard' && !masterSignalData) {
      loadMasterSignalData();
    }
  }, [activeTab, masterSignalData, currentTicker]);"""

r3 = """  const masterLoadingRef = useRef(false);
  const loadMasterSignalData = async () => {
    if (masterLoadingRef.current) return;
    masterLoadingRef.current = true;
    setMasterSignalError(null);
    const targetTicker = currentTicker;
    try {
      const data = await api.fetchSignal(targetTicker) as any;
      if (targetTicker === currentTicker) {
        setMasterSignalData(data);
      }
    } catch (err: any) {
      console.warn('Failed to load master signal:', err);
      setMasterSignalError(err?.message === 'TIMEOUT' ? '응답 시간 초과 (30초)' : '불러오기 실패');
    } finally {
      masterLoadingRef.current = false;
    }
  };

  useEffect(() => {
    if (activeTab === 'dashboard' && !masterSignalData && !masterSignalError) {
      loadMasterSignalData();
    }
  }, [activeTab, masterSignalData, masterSignalError, currentTicker]);"""

# 4. DashboardView prop passing
t4 = """            masterSignal={masterSignalData}
            portfolioData={portfolioData}"""

r4 = """            masterSignal={masterSignalData}
            masterSignalError={masterSignalError}
            onRetryMasterSignal={() => { setMasterSignalError(null); }}
            portfolioData={portfolioData}"""

# 5. DashboardView prop receive & modules def
t5_1 = """function DashboardView({ price, analysis, technical, balance, nvdaHolding, onOrder, isPositive, ticker, market, masterSignal, portfolioData, traderData, scannerData, earningsData, riskData, rebalanceData }: any) {"""
r5_1 = """function DashboardView({ price, analysis, technical, balance, nvdaHolding, onOrder, isPositive, ticker, market, masterSignal, masterSignalError, onRetryMasterSignal, portfolioData, traderData, scannerData, earningsData, riskData, rebalanceData }: any) {"""

t5_2 = """  // Module scores from master signal
  const modules = masterSignal?.components || null;"""
r5_2 = """  // Module scores from master signal
  const modules = (masterSignal?.components?.length ?? 0) > 0 ? masterSignal.components : null;"""

# 6. Render 3-way branch
t6 = """        {modules ? (
          <div className="space-y-3">
            {modules.map((mod: any, idx: number) => {
              const signalColor = (mod.signal === 'BUY' || mod.signal === 'STRONG_BUY') ? 'emerald-400' : (mod.signal === 'SELL' || mod.signal === 'STRONG_SELL') ? 'red-400' : 'amber-400';
              const signalLabel = mod.signal === 'STRONG_BUY' ? 'STRONG BUY' : mod.signal === 'BUY' ? 'BUY' : mod.signal === 'STRONG_SELL' ? 'STRONG SELL' : mod.signal === 'SELL' ? 'SELL' : 'HOLD';
              return (
                <div key={idx} className="flex items-center gap-3">
                  <div className="w-24 text-sm text-gray-400">{mod.name}</div>
                  <div className="flex-1 bg-gray-700 rounded-full h-4 overflow-hidden">
                    <div
                      className={`h-full bg-${signalColor} rounded-full`}
                      style={{ width: `${mod.score}%` }}
                    />
                  </div>
                  <div className="w-12 text-right">
                    <span className="text-sm font-bold text-white">
                      {typeof mod.score === 'number' ? mod.score.toFixed(1) : mod.score}
                    </span>
                  </div>
                  <div className={`w-16 px-2 py-1 rounded text-xs font-bold text-center bg-${signalColor}/20 text-${signalColor}`}>
                    {signalLabel}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="space-y-3">
            {[0, 1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="flex items-center gap-3 animate-pulse">
                <div className="w-24 h-4 bg-gray-700 rounded" />
                <div className="flex-1 h-4 bg-gray-700 rounded-full" />
                <div className="w-12 h-4 bg-gray-700 rounded" />
                <div className="w-16 h-6 bg-gray-700 rounded" />
              </div>
            ))}
            <p className="text-center text-sm text-gray-500 pt-2">
              7개 모듈 분석 중... (최대 20초)
            </p>
          </div>
        )}"""

r6 = """        {modules ? (
          <div className="space-y-3">
            {modules.map((mod: any, idx: number) => {
              const signalColor = (mod.signal === 'BUY' || mod.signal === 'STRONG_BUY') ? 'emerald-400' : (mod.signal === 'SELL' || mod.signal === 'STRONG_SELL') ? 'red-400' : 'amber-400';
              const signalLabel = mod.signal === 'STRONG_BUY' ? 'STRONG BUY' : mod.signal === 'BUY' ? 'BUY' : mod.signal === 'STRONG_SELL' ? 'STRONG SELL' : mod.signal === 'SELL' ? 'SELL' : 'HOLD';
              return (
                <div key={idx} className="flex items-center gap-3">
                  <div className="w-24 text-sm text-gray-400">{mod.name}</div>
                  <div className="flex-1 bg-gray-700 rounded-full h-4 overflow-hidden">
                    <div
                      className={`h-full bg-${signalColor} rounded-full`}
                      style={{ width: `${mod.score}%` }}
                    />
                  </div>
                  <div className="w-12 text-right">
                    <span className="text-sm font-bold text-white">
                      {typeof mod.score === 'number' ? mod.score.toFixed(1) : mod.score}
                    </span>
                  </div>
                  <div className={`w-16 px-2 py-1 rounded text-xs font-bold text-center bg-${signalColor}/20 text-${signalColor}`}>
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
        ) : (
          <div className="space-y-3">
            {[0, 1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="flex items-center gap-3 animate-pulse">
                <div className="w-24 h-4 bg-gray-700 rounded" />
                <div className="flex-1 h-4 bg-gray-700 rounded-full" />
                <div className="w-12 h-4 bg-gray-700 rounded" />
                <div className="w-16 h-6 bg-gray-700 rounded" />
              </div>
            ))}
            <p className="text-center text-sm text-gray-500 pt-2">
              7개 모듈 분석 중... (최대 20초)
            </p>
          </div>
        )}"""

checks = [('t1', t1), ('t2', t2), ('t3', t3), ('t4', t4), ('t5_1', t5_1), ('t5_2', t5_2), ('t6', t6)]
for name, t in checks:
    if t not in content:
        print(f"ERROR: {name} NOT FOUND")
        sys.exit(1)

content = content.replace(t1, r1, 1)
content = content.replace(t2, r2, 1)
content = content.replace(t3, r3, 1)
content = content.replace(t4, r4, 1)
content = content.replace(t5_1, r5_1, 1)
content = content.replace(t5_2, r5_2, 1)
content = content.replace(t6, r6, 1)

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("PATCH STEP D-2 APPLIED SUCCESSFULLY")
