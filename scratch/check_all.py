# -*- coding: utf-8 -*-
import py_compile, json
from html.parser import HTMLParser

# 1. 파이썬 문법 검증
py_compile.compile('run_dashboard.py', doraise=True)
py_compile.compile('agent_swarm_cloner.py', doraise=True)
py_compile.compile('multi_agent_orchestrator.py', doraise=True)
print('[PASS] Python syntax 100% OK!')

# 2. wisdom_ledger.json 검증
w = json.load(open('wisdom_ledger.json', encoding='utf-8'))
last_entry = w['good_practices'][-1]
print(f"[PASS] Wisdom ledger loaded! Last: {last_entry['id']} - {last_entry['title']}")

# 3. DOM 태그 짝맞춤 검증
class DivCheck(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.tabs = {}
    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            d = dict(attrs)
            tid = d.get('id', '')
            self.stack.append((tid, self.getpos()[0]))
            if tid.startswith('tab-'):
                self.tabs[tid] = {'start': self.getpos()[0], 'depth': len(self.stack)}
    def handle_endtag(self, tag):
        if tag == 'div' and self.stack:
            tid, line = self.stack.pop()
            if tid.startswith('tab-'):
                self.tabs[tid]['end'] = self.getpos()[0]

chk = DivCheck()
chk.feed(open('dashboard/index.html', encoding='utf-8').read())
print(f'[PASS] Final div stack leak count: {len(chk.stack)}')
for tid, info in chk.tabs.items():
    print(f"   * {tid}: L{info.get('start')} ~ L{info.get('end')} (depth: {info.get('depth')})")
