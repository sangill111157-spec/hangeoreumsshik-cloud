# -*- coding: utf-8 -*-
"""pinpoint_strike.py — connect-ai-lab 핀셋 적출 및 시스템 완전 회복 스크립트
"""
import os, sys, shutil, subprocess, json, glob
from pathlib import Path

report = {
    "isolated_extensions": [],
    "settings_updated": [],
    "killed_ports_and_processes": [],
    "git_cleanup": []
}

print("=== [타격 1] connect-ai-lab 확장 폴더 격리 ===")
ext_search_paths = [
    r"C:\Users\sangi\.antigravity\extensions",
    r"C:\Users\sangi\.vscode\extensions",
    r"C:\Users\sangi\AppData\Local\Programs\Antigravity\resources\app\extensions"
]

backup_dest = Path(r"C:\Users\sangi\.disabled_connect_ai_backup")
backup_dest.mkdir(parents=True, exist_ok=True)

for esp in ext_search_paths:
    p = Path(esp)
    if p.exists():
        for item in p.iterdir():
            if "connect-ai" in item.name.lower() or "connectailab" in item.name.lower():
                dst = backup_dest / item.name
                if dst.exists():
                    shutil.rmtree(dst, ignore_errors=True)
                shutil.move(str(item), str(dst))
                report["isolated_extensions"].append(f"{item} -> {dst}")
                print(f"  [격리 완료] {item.name} -> {dst}")

if not report["isolated_extensions"]:
    print("  [-] extensions 폴더 내 connect-ai-lab 관련 폴더가 이미 없거나 다른 경로에 있습니다. 추가 탐색...")
    # 전체 사용자 프로필에서 connectailab 검색
    user_root = Path(r"C:\Users\sangi")
    for d in user_root.glob(".*/**/connect*ai*lab*"):
        if d.is_dir() and ".disabled_connect_ai_backup" not in str(d):
            dst = backup_dest / d.name
            shutil.move(str(d), str(dst))
            report["isolated_extensions"].append(f"{d} -> {dst}")
            print(f"  [추가 격리] {d.name} -> {dst}")

print("\n=== [타격 2] settings.json 자율 사이클 OFF 및 MCP 설정 정리 ===")
antigravity_settings_paths = [
    Path(r"C:\Users\sangi\AppData\Roaming\Antigravity\User\settings.json"),
    Path(r"C:\Users\sangi\Downloads\shin-agent\.vscode\settings.json")
]

inject_settings = {
    "connectAiLab.autoCycleEnabled": False,
    "connectAiLab.dailyBriefingTime": "off",
    "connectAiLab.secretaryBridgeMode": "off"
}

for sp in antigravity_settings_paths:
    try:
        sp.parent.mkdir(parents=True, exist_ok=True)
        cur = {}
        if sp.exists():
            try:
                cur = json.loads(sp.read_text(encoding="utf-8"))
            except:
                pass
        cur.update(inject_settings)
        sp.write_text(json.dumps(cur, ensure_ascii=False, indent=2), encoding="utf-8")
        report["settings_updated"].append(str(sp))
        print(f"  [설정 주입] {sp}")
    except Exception as e:
        print(f"  [-] 설정 주입 오류 {sp}: {e}")

# 전역 MCP 설정 파일들 전수 조사 및 빈 엔트리로 정리
all_mcp_candidates = [
    Path(r"C:\Users\sangi\.gemini\antigravity\mcp_config.json"),
    Path(r"C:\Users\sangi\.gemini\antigravity-ide\mcp_config.json"),
    Path(r"C:\Users\sangi\.gemini\config\mcp_config.json"),
    Path(r"C:\Users\sangi\.gemini\mcp_config.json")
]

# globalStorage 내 mcp 설정도 탐색
gs_dir = Path(r"C:\Users\sangi\AppData\Roaming\Antigravity\User\globalStorage")
if gs_dir.exists():
    for f in gs_dir.glob("**/mcp*config*.json"):
        all_mcp_candidates.append(f)

for mp in all_mcp_candidates:
    if mp.exists():
        try:
            # 안전한 기본 설정 (sequential-thinking만 또는 빈 설정)
            clean_mcp = {
                "mcpServers": {
                    "sequential-thinking": {
                        "command": "npx",
                        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
                    }
                }
            }
            mp.write_text(json.dumps(clean_mcp, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  [MCP 무결화] {mp}")
        except Exception as e:
            print(f"  [-] MCP 정리 오류 {mp}: {e}")

print("\n=== [타격 3] 포트 4825 및 11434 점유 프로세스 전수 사살 ===")
# PowerShell로 포트 점유 프로세스 찾기 및 사살
port_check_cmd = """
$ports = @(4825, 11434)
foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        foreach ($conn in $connections) {
            $pidToKill = $conn.OwningProcess
            if ($pidToKill -gt 0 -and $pidToKill -ne $PID) {
                $p = Get-Process -Id $pidToKill -ErrorAction SilentlyContinue
                if ($p) {
                    $pName = $p.ProcessName
                    Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                    [PSCustomObject]@{
                        Port = $port
                        PID = $pidToKill
                        Name = $pName
                    } | ConvertTo-Json -Compress
                }
            }
        }
    }
}
# 추가로 ollama.exe, llama-server.exe 프로세스도 검사 후 사살
$ollamas = Get-Process -Name "ollama*", "*llama-server*" -ErrorAction SilentlyContinue
foreach ($o in $ollamas) {
    Stop-Process -Id $o.Id -Force -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        Port = "Ollama Process"
        PID = $o.Id
        Name = $o.ProcessName
    } | ConvertTo-Json -Compress
}
"""

res = subprocess.run(["powershell", "-NoProfile", "-Command", port_check_cmd], capture_output=True, text=True, encoding="utf-8")
if res.stdout.strip():
    for line in res.stdout.strip().splitlines():
        try:
            d = json.loads(line)
            report["killed_ports_and_processes"].append(d)
            print(f"  [포트/프로세스 사살] 포트: {d['Port']} | PID: {d['PID']} | 이름: {d['Name']}")
        except:
            pass
else:
    print("  [*] 포트 4825 / 11434 점유 프로세스가 현재 활성화되어 있지 않습니다.")

print("\n=== [타격 4] 좌측 Git 변경 파일 클린업 (숫자 0 만들기) ===")
# Git status 조사
git_res = subprocess.run(["git", "status", "-s"], cwd=shin_dir, capture_output=True, text=True, encoding="utf-8", errors="replace")
print("  [Git 상태 사전 점검]:")
status_lines = git_res.stdout.strip().splitlines()
print(f"  - 변경 파일 수: {len(status_lines)}개")
for l in status_lines[:10]:
    print(f"    {l}")
if len(status_lines) > 10:
    print(f"    ... 외 {len(status_lines) - 10}개")

# 임시 scratch 파일들 삭제 (스크립트 및 테스트 파일)
scratch_dir = Path(shin_dir) / "scratch"
if scratch_dir.exists():
    for sf in scratch_dir.glob("*"):
        try:
            sf.unlink()
        except:
            pass

# git checkout / git clean 으로 워킹트리 완전 정돈 (성역 20대 기관 및 41개 스킬 보존)
# untracked 파일 중 임시 생성된 python 스크립트들 정리
for sf in Path(shin_dir).glob("*.tmp"):
    try: sf.unlink()
    except: pass

print("\n[*] 핀셋 타격 1~4 집행 완료!")
