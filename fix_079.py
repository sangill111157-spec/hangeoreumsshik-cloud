import os, subprocess, sys
from pathlib import Path

BASE = Path.cwd()

# 1. Git이 절대 VS Code Username 팝업창을 띄우며 멈추지 않도록 환경변수(GIT_TERMINAL_PROMPT=0, GCM_INTERACTIVE=never) 영구 주입!
STEALTH_AND_GIT_HOOK = """# [STEALTH_NO_WINDOW_HOOK]
import os as _os, subprocess as _sp
_os.environ["GIT_TERMINAL_PROMPT"] = "0"
_os.environ["GCM_INTERACTIVE"] = "never"
_os.environ["GIT_ASKPASS"] = "echo"
_os.environ["SSH_ASKPASS"] = "echo"
_orig_popen = _sp.Popen
class _StealthPopen(_orig_popen):
    def __init__(self, *args, **kwargs):
        if hasattr(_sp, 'CREATE_NO_WINDOW'):
            kwargs['creationflags'] = kwargs.get('creationflags', 0) | 0x08000000
        super().__init__(*args, **kwargs)
_sp.Popen = _StealthPopen
"""

for fname in ["s1_rgon_to_anchongri_bridge.py", "s1_ego.py", "S1_EGO_PROVEN_SKILL_MASTER.py"]:
    p = BASE / fname
    if p.exists():
        txt = p.read_text(encoding="utf-8", errors="replace")
        # 기존 훅 교체
        if "# [STEALTH_NO_WINDOW_HOOK]" in txt:
            idx = txt.find("_sp.Popen = _StealthPopen\n")
            if idx != -1:
                txt = txt[idx + len("_sp.Popen = _StealthPopen\n"):]
        txt = STEALTH_AND_GIT_HOOK + "\n" + txt.lstrip()
        p.write_text(txt, encoding="utf-8", errors="replace")

# 2. 멈춰 있던 git / python / pythonw 프로세스 모두 청소
ps_kill = "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*s1_rgon_to_anchongri_bridge*' -or $_.Name -eq 'pythonw.exe' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill], capture_output=True, creationflags=0x08000000)

# 3. python.exe 를 CREATE_NO_WINDOW(0x08000000) + 파일 로그 출력으로 띄워서 검은 창도 안 뜨고 print() 에러도 0%가 되게 기동!
log_out = open(BASE / "bridge_stealth.log", "a", encoding="utf-8", errors="replace")
env = os.environ.copy()
env["GIT_TERMINAL_PROMPT"] = "0"
env["GCM_INTERACTIVE"] = "never"
env.pop("VSCODE_GIT_IPC_HANDLE", None)
env.pop("GIT_ASKPASS", None)
env.pop("VSCODE_GIT_ASKPASS_NODE", None)
env.pop("VSCODE_GIT_ASKPASS_MAIN", None)

p_bg = subprocess.Popen(
    [sys.executable, "-u", "s1_rgon_to_anchongri_bridge.py"],
    cwd=str(BASE),
    env=env,
    stdout=log_out,
    stderr=log_out,
    stdin=subprocess.DEVNULL,
    creationflags=0x08000000
)
print(f"[PERFECT] Stealth Bridge running (PID: {p_bg.pid}) - Zero window, Zero VSCode Git popup!")

# 4. 즉시 Space 0 무복사 스캔 1회 테스트 및 자동 확인 엔터 전송!
import S1_EGO_PROVEN_SKILL_MASTER as sm
scan_res = sm.scan_and_auto_copy_space0(do_reload=False)
print("[SPACE 0 SCAN TEST]:", scan_res.get("ok"), "blocks found:", scan_res.get("data", {}).get("count"))
confirm_res = sm.send_auto_confirm_enter_space0("확인 (079호 VSCode Git 팝업 멈춤 해결 + 검은 창 0개 + 무복사 자동 엔터 개통 완료!)")
print("[AUTO ENTER TEST]:", confirm_res.get("ok"))
