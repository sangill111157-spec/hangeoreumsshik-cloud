import os
import sys
import subprocess
import json

sys.stdout.reconfigure(encoding='utf-8')

AGENTS_DIR = r'C:\Users\sangi\.connect-ai-brain\_company\_agents'

def run_script(agent_name, script_name, script_path):
    print(f"▶ Testing [{agent_name.upper()}] / {script_name}...")
    try:
        res = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=15
        )
        if res.returncode == 0:
            print(f"  ✅ [PASS] {script_name} (exit 0)")
            return True, "PASS", res.stdout[:150]
        else:
            print(f"  ❌ [FAIL] {script_name} (exit {res.returncode})")
            err_msg = res.stderr[:200] if res.stderr else res.stdout[:200]
            print(f"     Error: {err_msg.strip()}")
            return False, f"FAIL ({res.returncode})", err_msg
    except subprocess.TimeoutExpired:
        print(f"  ⚠️ [TIMEOUT] {script_name} (10s)")
        return False, "TIMEOUT", "Execution timed out"
    except Exception as e:
        print(f"  ❌ [EXCEPTION] {script_name}: {e}")
        return False, f"EXCEPTION ({e})", str(e)

results = {}

for agent_name in sorted(os.listdir(AGENTS_DIR)):
    agent_path = os.path.join(AGENTS_DIR, agent_name)
    if not os.path.isdir(agent_path):
        continue
    
    tools_dir = os.path.join(agent_path, 'tools')
    results[agent_name] = []
    
    if not os.path.exists(tools_dir):
        results[agent_name].append({'tool': 'Config/Prompt', 'ok': True, 'status': 'PASS (Config Only)'})
        continue

    py_files = [f for f in os.listdir(tools_dir) if f.endswith('.py')]
    if not py_files:
        results[agent_name].append({'tool': 'Config/Prompt', 'ok': True, 'status': 'PASS (Config Only)'})
        continue

    for pf in py_files:
        pf_path = os.path.join(tools_dir, pf)
        ok, status, msg = run_script(agent_name, pf, pf_path)
        results[agent_name].append({
            'tool': pf,
            'ok': ok,
            'status': status,
            'msg': msg,
            'path': pf_path
        })

print("\n=================================================================")
print("📊 [AGENT SYSTEM AUDIT SUMMARY]")
print("=================================================================")
total_cnt = 0
pass_cnt = 0
for ag, tlist in results.items():
    print(f"\n📂 Agent: {ag.upper()}")
    for t in tlist:
        total_cnt += 1
        st_symbol = "✅" if t['ok'] else "❌"
        if t['ok']: pass_cnt += 1
        print(f"  {st_symbol} {t['tool']} : {t['status']}")

print(f"\nTOTAL TOOLS AUDITED: {total_cnt} | PASS: {pass_cnt} | FAIL: {total_cnt - pass_cnt}")
