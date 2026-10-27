# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update LLMNewsResult dataclass in llm_analyzer.py (defect 73)
llm_path = os.path.join(backend_dir, r'app\services\llm_analyzer.py')
with open(llm_path, 'r', encoding='utf-8') as f:
    llm_c = f.read()

old_llm_dc = """    news_signal: str = "HOLD"
    summary_kr: str = ""
    news_items: List[Dict[str, Any]] = field(default_factory=list)"""

new_llm_dc = """    news_signal: str = "HOLD"
    confidence: int = 50
    summary_kr: str = ""
    news_items: List[Dict[str, Any]] = field(default_factory=list)"""

if old_llm_dc in llm_c:
    llm_c = llm_c.replace(old_llm_dc, new_llm_dc)

# Update analyze return in llm_analyzer.py to calculate and set confidence
old_llm_ret = """            summary_kr=summary_kr,
            news_items=all_news
        )"""

new_llm_ret = """            confidence=min(95, max(10, len(news_items) * 10)) if len(news_items) > 0 else 50,
            summary_kr=summary_kr,
            news_items=all_news
        )"""

if old_llm_ret in llm_c:
    llm_c = llm_c.replace(old_llm_ret, new_llm_ret)

with open(llm_path, 'w', encoding='utf-8') as f:
    f.write(llm_c)

subprocess.run('git add app/services/llm_analyzer.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(llm): declare and populate confidence field on LLMNewsResult (defect 73)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit 1:\n", res_c.stdout)

