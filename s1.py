# -*- coding: utf-8 -*-
import subprocess, sys, datetime
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent
def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "s1_ego.py"
    args = sys.argv[2:] if len(sys.argv) > 1 else ["spaces"]
    t0 = datetime.datetime.now().isoformat()
    r = subprocess.run([sys.executable, target] + args, cwd=str(BASE), capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        cmd_str = target + " " + " ".join(args)
        err_md = "# S1.py Auto-Error Report (" + t0 + ")\n- Command: " + cmd_str + "\n- RC: " + str(r.returncode) + "\n## STDOUT\n```\n" + r.stdout[-3000:] + "\n```\n## STDERR\n```\n" + r.stderr[-3000:] + "\n```"
        (BASE / "S1_OUT.md").write_text(err_md, encoding="utf-8")
        subprocess.run(["git", "add", "S1_OUT.md"], cwd=str(BASE))
        subprocess.run(["git", "commit", "-m", "chore(s1): auto-error report"], cwd=str(BASE))
        subprocess.run(["git", "pull", "--rebase", "--autostash", "-X", "ours", "origin", "main"], cwd=str(BASE))
        subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE))
    print(r.stdout)
    if r.stderr: print(r.stderr, file=sys.stderr)
    sys.exit(r.returncode)
if __name__ == "__main__": main()
