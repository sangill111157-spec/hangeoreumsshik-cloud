# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

with open(ms_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "components = [" in line:
        start_idx = i
    if start_idx != -1 and line.strip().startswith("]"):
        end_idx = i + 1
        break

print(f"Found components block from line {start_idx} to {end_idx}")

new_block = [
    "        components = [\n",
    "            ComponentSignal(\n",
    "                name='5대 투자자',\n",
    "                score=round(inv_score, 1) if 'investor_analysis' not in unavailable_modules else None,\n",
    "                signal=score_to_5level_signal(inv_score) if 'investor_analysis' not in unavailable_modules else 'UNAVAILABLE',\n",
    "                confidence=None if 'investor_analysis' in unavailable_modules else conf_map['investor_analysis'],\n",
    "                module_signal=score_to_5level_signal(inv_score) if 'investor_analysis' not in unavailable_modules else 'UNAVAILABLE'\n",
    "            ),\n",
    "            ComponentSignal(\n",
    "                name='멀티전략',\n",
    "                score=round(pod_score, 1) if 'pod_signals' not in unavailable_modules else None,\n",
    "                signal=score_to_5level_signal(pod_score) if 'pod_signals' not in unavailable_modules else 'UNAVAILABLE',\n",
    "                confidence=None if 'pod_signals' in unavailable_modules else clamp_conf(conf_map['pod_signals']),\n",
    "                module_signal=score_to_5level_signal(pod_score) if 'pod_signals' not in unavailable_modules else 'UNAVAILABLE'\n",
    "            ),\n",
    "            ComponentSignal(\n",
    "                name='기술적',\n",
    "                score=round(tech_score, 1) if 'technical' not in unavailable_modules else None,\n",
    "                signal=score_to_5level_signal(tech_score) if 'technical' not in unavailable_modules else 'UNAVAILABLE',\n",
    "                confidence=None if 'technical' in unavailable_modules else conf_map['technical'],\n",
    "                module_signal=score_to_5level_signal(tech_score) if 'technical' not in unavailable_modules else 'UNAVAILABLE'\n",
    "            ),\n",
    "            ComponentSignal(\n",
    "                name='AI 뉴스',\n",
    "                score=round(news_score, 1) if 'llm_news' not in unavailable_modules else None,\n",
    "                signal=score_to_5level_signal(news_score) if 'llm_news' not in unavailable_modules else 'UNAVAILABLE',\n",
    "                confidence=None if 'llm_news' in unavailable_modules else conf_map['llm_news'],\n",
    "                module_signal=score_to_5level_signal(news_score) if 'llm_news' not in unavailable_modules else 'UNAVAILABLE'\n",
    "            ),\n",
    "            ComponentSignal(\n",
    "                name='기관/13F',\n",
    "                score=round(inst_score, 1) if 'institutional' not in unavailable_modules else None,\n",
    "                signal=score_to_5level_signal(inst_score) if 'institutional' not in unavailable_modules else 'UNAVAILABLE',\n",
    "                confidence=None if 'institutional' in unavailable_modules else conf_map['institutional'],\n",
    "                module_signal=score_to_5level_signal(inst_score) if 'institutional' not in unavailable_modules else 'UNAVAILABLE'\n",
    "            ),\n",
    "            ComponentSignal(\n",
    "                name='옵션 플로우',\n",
    "                score=round(options_score, 1) if 'options_flow' not in unavailable_modules else None,\n",
    "                signal=score_to_5level_signal(options_score) if 'options_flow' not in unavailable_modules else 'UNAVAILABLE',\n",
    "                confidence=None if 'options_flow' in unavailable_modules else conf_map['options_flow'],\n",
    "                module_signal=score_to_5level_signal(options_score) if 'options_flow' not in unavailable_modules else 'UNAVAILABLE'\n",
    "            ),\n",
    "            ComponentSignal(\n",
    "                name='다크풀',\n",
    "                score=round(darkpool_score, 1) if 'darkpool' not in unavailable_modules else None,\n",
    "                signal=score_to_5level_signal(darkpool_score) if 'darkpool' not in unavailable_modules else 'UNAVAILABLE',\n",
    "                confidence=None if 'darkpool' in unavailable_modules else conf_map['darkpool'],\n",
    "                module_signal=score_to_5level_signal(darkpool_score) if 'darkpool' not in unavailable_modules else 'UNAVAILABLE'\n",
    "            )\n",
    "        ]\n"
]

lines[start_idx:end_idx] = new_block

with open(ms_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(components): strictly unify module_signal to score_to_5level_signal for all 7 modules (defect 127)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)

