import re

with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 헤더 Trading System 한글화 & translate="no"
content = content.replace('<h1 className="text-lg font-bold text-white">Trading System</h1>', '<h1 className="text-lg font-bold text-white" translate="no">트레이딩 시스템</h1>')
content = content.replace('<span className="text-white font-bold text-lg">{currentTicker}</span>', '<span className="text-white font-bold text-lg" translate="no">{currentTicker}</span>')

# 2. 탭 네비게이션 whitespace-nowrap 및 줄바꿈 방지
tab_nav_old = '''            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-white'
                    : 'border-transparent text-gray-400 hover:text-white'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}'''

tab_nav_new = '''            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 whitespace-nowrap flex-shrink-0 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-white'
                    : 'border-transparent text-gray-400 hover:text-white'
                }`}
              >
                {tab.icon}
                <span className="whitespace-nowrap">{tab.label}</span>
              </button>
            ))}'''

if tab_nav_old in content:
    content = content.replace(tab_nav_old, tab_nav_new, 1)
    print("Tab nav updated with whitespace-nowrap")
else:
    print("Tab nav pattern not found")

# 3. DashboardView 내의 7개 모듈 요약, 리스크 점수, RSI/MACD, 갱신 시각 업데이트
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Part 1 applied")
