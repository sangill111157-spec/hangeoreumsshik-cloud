import subprocess, sys
from pathlib import Path

BASE = Path.cwd()

# [글로벌 스텔스 패치] s1_rgon_to_anchongri_bridge.py 와 s1_ego.py 최상단에
# subprocess.Popen 자체에 CREATE_NO_WINDOW(0x08000000)를 기본값으로 강제 주입하는 코드 장착!
STEALTH_HEADER = """# [STEALTH_NO_WINDOW_HOOK]
import subprocess as _sp
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
        if "[STEALTH_NO_WINDOW_HOOK]" not in txt:
            txt = STEALTH_HEADER + "\n" + txt
            p.write_text(txt, encoding="utf-8", errors="replace")
            print(f"[OK] Global stealth hook injected into {fname}")

# 기존 python / pythonw 브릿지 프로세스 종료 후 완전 투명(pythonw) 재기동
ps_kill = "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*s1_rgon_to_anchongri_bridge.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill], capture_output=True, creationflags=0x08000000)

pythonw_exe = Path(sys.executable).with_name("pythonw.exe")
exe_to_use = str(pythonw_exe) if pythonw_exe.exists() else sys.executable

p_bg = subprocess.Popen([exe_to_use, "s1_rgon_to_anchongri_bridge.py"], cwd=str(BASE), creationflags=0x08000000)
print(f"[PERFECT] 100% Zero-Flash Stealth Bridge started! (PID: {p_bg.pid}, Exe: {exe_to_use})")
