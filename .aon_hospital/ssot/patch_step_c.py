# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Definition replacement
def_target = """  // Module scores from master signal
  const modules = masterSignal?.components || [
    { name: '투자자분석', score: analysis?.overall_confidence || 50, signal: analysis?.overall_signal || 'HOLD' },
    { name: '기술분석', score: technical?.confidence || 50, signal: technical?.overall_signal || 'HOLD' },
    { name: '옵션플로우', score: 70, signal: 'BUY' },
    { name: '다크풀', score: 54, signal: 'HOLD' },
    { name: '뉴스분석', score: 52, signal: 'NEUTRAL' },
    { name: '상관관계', score: 55, signal: 'HOLD' },
    { name: '이벤트', score: 60, signal: 'BUY' },
  ];"""

def_replacement = """  // Module scores from master signal
  const modules = masterSignal?.components || null;"""

# 2. Render replacement
render_target = """        <div className="space-y-3">
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
        </div>"""

render_replacement = """        {modules ? (
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

if def_target not in content:
    print("ERROR: def_target NOT FOUND")
    sys.exit(1)

if render_target not in content:
    print("ERROR: render_target NOT FOUND")
    sys.exit(1)

content = content.replace(def_target, def_replacement, 1)
content = content.replace(render_target, render_replacement, 1)

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("PATCH STEP C APPLIED SUCCESSFULLY")
