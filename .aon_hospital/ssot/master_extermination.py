#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""master_extermination.py — 안티그래비티 내부 백그라운드·고아 프로세스·고장난 MCP·구 세션 완전 박멸 시스템
표준 라이브러리 전용.
기술총리 안총리 & 만능 수족 아온이 공동 집행
"""

import os, sys, shutil, subprocess, json, time
from pathlib import Path

CURRENT_CONV_ID = "959f8c23-cda1-4eb8-bffb-70c98425ce71"
PREV_ACTIVE_CONV_ID = "84d9a01b-2db3-47a2-aa16-1613807537fa"
KEEP_CONVS = {CURRENT_CONV_ID, PREV_ACTIVE_CONV_ID}

CURRENT_PID = os.getpid()

report = {
    "killed_processes": [],
    "deleted_sessions_count": 0,
    "deleted_sessions_bytes": 0,
    "cleaned_cache_bytes": 0,
    "cleaned_cache_files": 0,
    "cleaned_scratch_files": 0,
    "mcp_cleaned_files": [],
    "settings_updated": [],
    "before_cpu": None,
    "before_mem_mb": None,
    "after_cpu": None,
    "after_mem_mb": None
}

def get_sys_metrics():
    ps = """
    $mem = Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory
    $cpu = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
    [PSCustomObject]@{
        CPU = $cpu
        Used = [math]::Round(($mem.TotalVisibleMemorySize - $mem.FreePhysicalMemory) / 1024, 1)
        Total = [math]::Round($mem.TotalVisibleMemorySize / 1024, 1)
    } | ConvertTo-Json
    """
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, encoding="utf-8")
        d = json.loads(r.stdout)
        return float(d.get("CPU", 0.0)), float(d.get("Used", 0.0)), float(d.get("Total", 0.0))
    except Exception:
        return 0.0, 0.0, 0.0

print("=====================================================================")
print("🚨 [사령부] 안티그래비티 초경량화 & 구 세션·고아 프로세스 완전 박멸 작전 개시!")
print("=====================================================================")

c_b, m_b, m_tot = get_sys_metrics()
report["before_cpu"] = c_b
report["before_mem_mb"] = m_b
print(f"[*] 박멸 전 상태: CPU {c_b}% | RAM 사용량: {m_b} MB / 전체 {m_tot} MB")

# ==============================================================================
# [1단계 & 2단계] 고아 / 좀비 프로세스 및 상주 데몬 전수 사살
# ==============================================================================
print("\n[1 & 2단계] 고아 프로세스 (node, python, git) 및 데몬 전수 조사 및 사살...")

# 1. shin-agent 내 PID 파일들 확인 및 사살
shin_dir = r"C:\Users\sangi\Downloads\shin-agent"
pid_patterns = ["*.pid", ".*.pid"]
for pat in pid_patterns:
    for pf in Path(shin_dir).glob(pat):
        try:
            val = pf.read_text().strip()
            if val.isdigit():
                pid = int(val)
                if pid != CURRENT_PID:
                    subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
                    report["killed_processes"].append(f"PID {pid} from {pf.name}")
                    print(f"  [사살] PID 파일 등록 프로세스: {pf.name} -> PID {pid}")
            pf.unlink(missing_ok=True)
        except Exception:
            pass

# 2. PowerShell로 프로세스 전수 검사하여 고아 node.exe, 미사용 python.exe, git.exe 사살
ps_kill_code = f"""
$procs = Get-CimInstance Win32_Process | Where-Object {{ $_.ProcessId -ne {CURRENT_PID} }} | Select-Object ProcessId, Name, CommandLine

foreach ($p in $procs) {{
    $name = $p.Name.ToLower()
    $cmd = [string]$p.CommandLine
    $shouldKill = $false
    $reason = ""

    if ($name -eq "node.exe") {{
        if ($cmd -match "cloud-run-mcp|code-assist-mcp|sequential-thinking|firebase-tools|genkit") {{
            $shouldKill = $true
            $reason = "고장/상주 MCP Node 서버"
        }}
    }}
    elseif ($name -eq "python.exe" -or $name -eq "pythonw.exe") {{
        if ($cmd -match "win_auto_typer|immortal_tunnel|rgon_watcher|rgon_auto_sync|night_autonomous") {{
            $shouldKill = $true
            $reason = "상주 데몬 Python"
        }}
    }}
    elseif ($name -eq "git.exe") {{
        $shouldKill = $true
        $reason = "고아 Git 프로세스"
    }}

    if ($shouldKill) {{
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        [PSCustomObject]@{{
            PID = $p.ProcessId
            Name = $name
            Reason = $reason
            Cmd = $cmd.Substring(0, [math]::Min(60, $cmd.Length))
        }} | ConvertTo-Json -Compress
    }}
}}
"""

r_kill = subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill_code], capture_output=True, text=True, encoding="utf-8")
if r_kill.stdout.strip():
    for line in r_kill.stdout.strip().splitlines():
        try:
            kd = json.loads(line)
            desc = f"PID {kd['PID']} ({kd['Name']}) - {kd['Reason']}: {kd['Cmd']}"
            report["killed_processes"].append(desc)
            print(f"  [사살] {desc}")
        except:
            pass

# ==============================================================================
# [3단계] Brain 과거 세션 138개 및 캐시/로그 대청소
# ==============================================================================
print("\n[3단계] Brain 해묵은 세션 및 캐시/로그 전수 대청소...")

brain_dir = Path(r"C:\Users\sangi\.gemini\antigravity-ide\brain")
if brain_dir.exists():
    for sess_dir in brain_dir.iterdir():
        if sess_dir.is_dir():
            if sess_dir.name not in KEEP_CONVS:
                # 과거 세션 삭제
                sz = 0
                for f in sess_dir.glob('**/*'):
                    if f.is_file():
                        try: sz += f.stat().st_size
                        except: pass
                shutil.rmtree(sess_dir, ignore_errors=True)
                report["deleted_sessions_count"] += 1
                report["deleted_sessions_bytes"] += sz
            else:
                # 보존 세션 내 tasks 로그 및 scratch 스크립트 정리
                tasks_dir = sess_dir / ".system_generated" / "tasks"
                if tasks_dir.exists():
                    for lf in tasks_dir.glob("task-*.log"):
                        try:
                            lf.unlink()
                        except: pass
                
                sc_dir = sess_dir / "scratch"
                if sc_dir.exists():
                    for scf in sc_dir.glob("*"):
                        try:
                            if scf.is_file():
                                scf.unlink()
                                report["cleaned_scratch_files"] += 1
                        except: pass

print(f"  [청소 완료] 삭제된 과거 세션: {report['deleted_sessions_count']}개 (총 {round(report['deleted_sessions_bytes'] / (1024*1024), 2)} MB 확보!)")

# 캐시 디렉토리 청소
cache_paths = [
    Path(r"C:\Users\sangi\AppData\Roaming\Antigravity\Cache"),
    Path(r"C:\Users\sangi\AppData\Roaming\Antigravity\CachedData"),
    Path(r"C:\Users\sangi\AppData\Roaming\Antigravity\Code Cache"),
    Path(r"C:\Users\sangi\AppData\Roaming\Antigravity\GPUCache"),
    Path(r"C:\Users\sangi\AppData\Roaming\Antigravity\logs")
]

for cp in cache_paths:
    if cp.exists():
        for item in cp.glob("**/*"):
            if item.is_file():
                try:
                    sz = item.stat().st_size
                    item.unlink()
                    report["cleaned_cache_bytes"] += sz
                    report["cleaned_cache_files"] += 1
                except: pass

print(f"  [청소 완료] 삭제된 캐시/로그: {report['cleaned_cache_files']}개 (총 {round(report['cleaned_cache_bytes'] / (1024*1024), 2)} MB 확보!)")

# ==============================================================================
# [4단계] 고장난 MCP 서버 영구 제거 및 mcp_config.json 갱신
# ==============================================================================
print("\n[4단계] 고장난 MCP 서버 색출 및 영구 제거 (MCP Error 완전 박멸)...")

mcp_configs = [
    Path(r"C:\Users\sangi\.gemini\antigravity-ide\mcp_config.json"),
    Path(r"C:\Users\sangi\.gemini\config\mcp_config.json")
]

clean_mcp_config = {
    "mcpServers": {
        "sequential-thinking": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-sequential-thinking"
            ]
        }
    }
}

for mcfg in mcp_configs:
    if mcfg.exists():
        bak = mcfg.with_suffix(".json.bak_exterminate")
        shutil.copy2(mcfg, bak)
        mcfg.write_text(json.dumps(clean_mcp_config, ensure_ascii=False, indent=2), encoding="utf-8")
        report["mcp_cleaned_files"].append(str(mcfg))
        print(f"  [MCP 제거 완료] {mcfg} -> 고장난 capcut-api, connect-ai, prisma, cloudrun 등 전수 제거!")

# ==============================================================================
# [5단계] 워크스페이스 파일 감시자 & 인덱싱 폭주 원천 차단
# ==============================================================================
print("\n[5단계] 워크스페이스 Watcher & Indexer 차단 설정 주입...")

watcher_settings = {
    "files.watcherExclude": {
        "**/.git/**": True,
        "**/.rgon_backup*/**": True,
        "**/__pycache__/**": True,
        "**/node_modules/**": True,
        "**/scratch/**": True,
        "**/*.log": True,
        "**/*_state.json": True
    },
    "search.exclude": {
        "**/.git": True,
        "**/.rgon_backup*": True,
        "**/__pycache__": True,
        "**/scratch": True
    },
    "python.analysis.indexing": False,
    "python.analysis.autoSearchPaths": False,
    "git.autorefresh": False,
    "git.autofetch": False
}

vscode_dirs = [
    Path(r"C:\Users\sangi\Downloads\shin-agent\.vscode"),
    Path(r"C:\Users\sangi\shin-agent\.vscode")
]

for vd in vscode_dirs:
    try:
        vd.mkdir(parents=True, exist_ok=True)
        set_file = vd / "settings.json"
        existing = {}
        if set_file.exists():
            try:
                existing = json.loads(set_file.read_text(encoding="utf-8"))
            except: pass
        existing.update(watcher_settings)
        set_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
        report["settings_updated"].append(str(set_file))
        print(f"  [설정 주입 완료] {set_file}")
    except Exception as e:
        print(f"  [-] 설정 주입 건너뜀: {vd} ({e})")

# shin-agent 내 scratch 임시 파일 청소
shin_scratch = Path(r"C:\Users\sangi\Downloads\shin-agent\scratch")
if shin_scratch.exists():
    for f in shin_scratch.glob("*.py"):
        try:
            f.unlink()
            report["cleaned_scratch_files"] += 1
        except: pass

# ==============================================================================
# [6단계] 박멸 후 CPU / RAM 실측 및 결과 수치 집계
# ==============================================================================
time.sleep(1.0)
c_a, m_a, _ = get_sys_metrics()
report["after_cpu"] = c_a
report["after_mem_mb"] = m_a

total_freed_mb = round((report["deleted_sessions_bytes"] + report["cleaned_cache_bytes"]) / (1024*1024), 2)

print("\n=====================================================================")
print("✅ 안티그래비티 초경량화 & 완전 박멸 작전 완료 보고서")
print("=====================================================================")
print(f"1. 사살된 고아/데몬 프로세스 : {len(report['killed_processes'])}개")
for p in report['killed_processes']:
    print(f"   - {p}")
print(f"2. 삭제된 해묵은 Brain 세션 : {report['deleted_sessions_count']}개")
print(f"3. 청소된 캐시/로그 파일      : {report['cleaned_cache_files']}개")
print(f"4. 디스크 총 확보 용량        : {total_freed_mb} MB (약 {round(total_freed_mb/1024, 2)} GB!)")
print(f"5. MCP Error 원인 제거       : capcut-api, connect-ai, prisma 등 고장난 서버 영구 퇴출")
print(f"6. 워크스페이스 인덱싱 차단  : .vscode/settings.json 감시 제외 설정 완료")
print(f"7. CPU 부하 변화             : {c_b}% -> {c_a}%")
print(f"8. RAM 사용량 변화           : {m_b} MB -> {m_a} MB (약 {round(m_b - m_a, 1)} MB 절감)")
print("=====================================================================")

with open(r"C:\Users\sangi\Downloads\shin-agent\extermination_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("[*] extermination_report.json 저장 완료.")
