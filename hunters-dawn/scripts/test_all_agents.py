import os
import sys
import subprocess
import json

sys.stdout.reconfigure(encoding='utf-8')

AGENTS_DIR = r'C:\Users\sangi\.connect-ai-brain\_company\_agents'

print("=================================================================")
print("🧪 [Connect AI 전체 에이전트 10개 부서 전수 실측 테스트]")
print("=================================================================")

test_results = []

for agent_name in os.listdir(AGENTS_DIR):
    agent_path = os.path.join(AGENTS_DIR, agent_name)
    if not os.path.isdir(agent_path):
        continue
        
    tools_dir = os.path.join(agent_path, 'tools')
    print(f"\n▶ [{agent_name.upper()} 에이전트 부서 검증 시작]")
    
    if not os.path.exists(tools_dir):
        print(f"  ℹ️ {agent_name}: 전용 파이썬 툴 없음 (프롬프트/설정 전담)")
        test_results.append({
            'agent': agent_name,
            'tool': 'Prompt/Config Only',
            'status': 'PASS (Config Only)'
        })
        continue

    tool_files = [f for f in os.listdir(tools_dir) if f.endswith('.py')]
    if not tool_files:
        print(f"  ℹ️ {agent_name}: 등록된 파이썬 스크립트 없음")
        test_results.append({
            'agent': agent_name,
            'tool': 'None',
            'status': 'PASS (Config Only)'
        })
        continue

    for tf in tool_files:
        tf_path = os.path.join(tools_dir, tf)
        print(f"  ⚡ 테스트 실행 중: {tf} ...")
        
        try:
            res = subprocess.run(
                [sys.executable, tf_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=15
            )
            code = res.returncode
            if code == 0:
                print(f"     ✅ {tf} -> SUCCESS (exit 0)")
                test_results.append({
                    'agent': agent_name,
                    'tool': tf,
                    'status': 'PASS',
                    'output': res.stdout[:150]
                })
            else:
                print(f"     ❌ {tf} -> FAIL (exit {code})")
                print(f"        에러: {res.stderr[:200]}")
                test_results.append({
                    'agent': agent_name,
                    'tool': tf,
                    'status': f'FAIL (exit {code})',
                    'error': res.stderr[:200],
                    'path': tf_path
                })
        except subprocess.TimeoutExpired:
            print(f"     ⚠️ {tf} -> TIMEOUT (15s)")
            test_results.append({
                'agent': agent_name,
                'tool': tf,
                'status': 'TIMEOUT (15s)',
                'path': tf_path
            })
        except Exception as e:
            print(f"     ❌ {tf} -> EXCEPTION: {e}")
            test_results.append({
                'agent': agent_name,
                'tool': tf,
                'status': f'EXCEPTION ({e})',
                'path': tf_path
            })

print("\n=================================================================")
print("📊 [1차 실측 테스트 결과 요약]")
print("=================================================================")
for r in test_results:
    print(f"[{r['agent'].upper()}] {r['tool']} => {r['status']}")

print("=================================================================")
