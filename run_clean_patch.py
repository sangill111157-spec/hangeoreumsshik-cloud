# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time, urllib.request
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [D-3 PATCH] Normalize component signals in master_signal.py")
print("==================================================")
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for idx, line in enumerate(lines):
    if 'signal=investor_analysis.get("overall_signal", "HOLD")' in line:
        line = '                signal=_norm_sig(investor_analysis.get("overall_signal")),\n'
    elif 'technical.get("overall_signal", "HOLD")' in line:
        line = '                signal=_norm_sig(technical.get("overall_signal")),\n'
    elif 'llm_news.get("sentiment_label", "HOLD")' in line:
        line = '                signal=_norm_sig(llm_news.get("sentiment_label")),\n'
    elif '"BUY" if inst_score >= 60 else "SELL" if inst_score <= 40 else "HOLD"' in line:
        line = '                signal=_norm_sig("BUY" if inst_score >= 60 else "SELL" if inst_score <= 40 else "HOLD"),\n'
    elif 'options_flow.get("options_signal", "HOLD")' in line:
        line = '                signal=_norm_sig(options_flow.get("options_signal")),\n'
    elif 'darkpool.get("darkpool_signal", "HOLD")' in line:
        line = '                signal=_norm_sig(darkpool.get("darkpool_signal")),\n'
    elif 'components = [' in line:
        # Prepend helper
        helper = """        def _norm_sig(sig) -> str:
            if not sig:
                return "HOLD"
            s = str(sig).upper()
            return "HOLD" if s in ["NEUTRAL", "NONE", "N/A"] else s

"""
        new_lines.append(helper)
    elif 'signal=pod_composite_signal if pod_composite_signal is not None else (' in line:
        line = """                signal=_norm_sig(pod_composite_signal if pod_composite_signal is not None else (
                    logger.warning("pod_composite_signal is None, falling back to pod_signals[0]") or (
                        pod_signals[0].get("signal", "HOLD") if pod_signals else "HOLD"
                    )
                )),\n"""
    new_lines.append(line)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

out_diff, _ = run_cmd('git diff app/services/master_signal.py')
print("--- git diff app/services/master_signal.py ---")
print(out_diff)

run_cmd('git add app/services/master_signal.py')
c_msg, _ = run_cmd('git commit -m "fix(signal): normalize component signal labels to uppercase"')
print("Commit D-3 Output:\n", c_msg)

print("\n==================================================")
print("2. [D-3 VERIFICATION] Check live endpoint signals")
print("==================================================")
try:
    req = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/signal", headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        res_json = json.loads(resp.read().decode('utf-8'))
        print("Live master_score:", res_json.get("master_score"))
        print("Live raw_score   :", res_json.get("raw_score"))
        print("Components signals:")
        for c in res_json.get("components", []):
            sig = c.get('signal', '')
            print(f"  - {c.get('name'):12s}: score={c.get('score'):<5} signal={sig:12s} is_upper={sig.isupper()} is_not_neutral={sig != 'NEUTRAL'}")
except Exception as e:
    print("Verification Error:", e)

print("\n==================================================")
print("3. [B-1 RE-PATCH] App.tsx Gauge & Confidence Null-Safe")
print("==================================================")
app_path = os.path.join(frontend_dir, r'src\App.tsx')
with open(app_path, 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

new_app_lines = []
for idx, line in enumerate(app_lines):
    if 'const gaugePercent = data?.master_score ?? 50;' in line or 'const gaugePercent = data?.master_score || 50;' in line:
        line = '  const hasMasterScore = data?.master_score != null;\n  const gaugePercent = hasMasterScore ? data.master_score : 0;\n'
    elif 'c.confidence ?? 50' in line or 'c.confidence || 50' in line:
        line = line.replace('c.confidence ?? 50', 'c.confidence ?? null').replace('c.confidence || 50', 'c.confidence ?? null')
    new_app_lines.append(line)

with open(app_path, 'w', encoding='utf-8') as f:
    f.writelines(new_app_lines)

out_ui_diff, _ = run_cmd('git diff src/App.tsx', cwd=frontend_dir)
print("--- git diff src/App.tsx ---")
print(out_ui_diff)

run_cmd('git add src/App.tsx', cwd=frontend_dir)
c_ui, _ = run_cmd('git commit -m "fix(ui): conditional gauge rendering and null-safe confidence for master_score"', cwd=frontend_dir)
print("Commit B-1 Output:\n", c_ui)

