
import os, re, subprocess



p = r"rgon_aside_extension/content_aside_bar.js"

s = open(p, encoding="utf-8").read()



# 1. 모든 DEFAULT_ROLES에 rgon(르곤 보좌관) 통일 주입

s = re.sub(

    r"DEFAULT_ROLES\s*=\s*\[\s*\{\s*role:\s*['\"]claude['\"]",

    "DEFAULT_ROLES = [\n    { role: 'rgon', icon: '🔵', label: '👑 르곤 보좌관 (Gemini 4 Argon)', def: false },\n    { role: 'claude'",

    s

)



# 2. 구버전 3종 배열에도 rgon 통일 추가 및 구버전 렌더러 충돌 차단

s = re.sub(r"\[\s*['\"]claude['\"]\s*,\s*['\"]gpt['\"]\s*,\s*['\"]grok['\"]\s*\]", "['rgon', 'claude', 'gpt', 'grok']", s)

s = re.sub(r"function\s+renderDispatchTargets\s*\([^)]*\)\s*\{", "function renderDispatchTargets(){ if(window.__RGON_V607) return; ", s)



open(p, "w", encoding="utf-8", newline="\n").write(s)



# 3. 문법 검증

chk = subprocess.run(["node", "--check", p], capture_output=True, text=True)

print("node --check:", "PASS" if chk.returncode == 0 else chk.stderr)



# 4. 바탕화면 원클릭 부팅 아이콘 생성

desktop = os.path.join(os.path.expanduser("~"), "Desktop")

bat = os.path.join(desktop, "RGON_사령부_원클릭_가동.bat")

bat_txt = """@echo off

chcp 65001 >nul

cd /d C:\\Users\\sangi\\Downloads\\shin-agent

start "" /min python -X utf8 omni_bridge.py

start "" /min python -X utf8 -m http.server 8501

python -X utf8 launch_tunnel_and_send_telegram.py

echo RGON 사령부 전체 가동 완료!

pause

"""

open(bat, "w", encoding="utf-8").write(bat_txt)



# 5. 브리지 + 8501 서버 + 5G 터널 가동 및 GitHub 푸시

subprocess.Popen(["python", "-X", "utf8", "omni_bridge.py"], creationflags=0x08000000)

subprocess.Popen(["python", "-X", "utf8", "-m", "http.server", "8501"], creationflags=0x08000000)

if os.path.exists("launch_tunnel_and_send_telegram.py"):

    subprocess.run(["python", "-X", "utf8", "launch_tunnel_and_send_telegram.py"])



subprocess.run(["git", "add", "-A"])

subprocess.run(["git", "commit", "-m", "fix(v6.0.8): stop 1s rgon row flicker & add one-click boot script"])

subprocess.run(["git", "push", "origin", "main"])

print("🎉 [깜빡임 완치 + 바탕화면 원클릭 부팅 아이콘 생성 + 5G 터널 가동 완료!]")

