# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

target = """        {modules ? (
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
          </div>"""

replacement = """        {modules ? (
          <div className="space-y-3">
            {modules.map((mod: any, idx: number) => {
              const style =
                (mod.signal === 'BUY' || mod.signal === 'STRONG_BUY')
                  ? { bar: 'bg-emerald-400', chip: 'bg-emerald-400/20 text-emerald-400' }
                : (mod.signal === 'SELL' || mod.signal === 'STRONG_SELL')
                  ? { bar: 'bg-red-400', chip: 'bg-red-400/20 text-red-400' }
                  : { bar: 'bg-amber-400', chip: 'bg-amber-400/20 text-amber-400' };

              const barWidth = Math.max(0, Math.min(100, Number(mod.score) || 0));
              const signalLabel = mod.signal === 'STRONG_BUY' ? 'STRONG BUY' : mod.signal === 'BUY' ? 'BUY' : mod.signal === 'STRONG_SELL' ? 'STRONG SELL' : mod.signal === 'SELL' ? 'SELL' : 'HOLD';
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
          </div>"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCH STEP F-1 APPLIED SUCCESSFULLY")
else:
    print("ERROR: TARGET NOT FOUND")
    sys.exit(1)
