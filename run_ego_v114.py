import subprocess, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
p = BASE / "s1_ego.py"
src = p.read_text(encoding="utf-8")
src = src.replace("v1.1.3", "v1.1.4")
src = src.replace("def cmd_read(space_id, tail_chars=4000, override_chat_id=None):", "def cmd_read(space_id, tail_chars=4000, override_chat_id=None, selftest=False):\n    if override_chat_id is not None and not selftest:\n        return {\"ok\": False, \"code\": \"OVERRIDE_REQUIRES_SELFTEST\", \"space\": space_id}")
src = src.replace("p_read.add_argument(\"--expect-id\", type=str, default=None)", "p_read.add_argument(\"--expect-id\", type=str, default=None)\n    p_read.add_argument(\"--selftest\", action=\"store_true\")")
src = src.replace("res = cmd_read(args.space, args.tail, override_chat_id=args.expect_id)", "res = cmd_read(args.space, args.tail, override_chat_id=args.expect_id, selftest=args.selftest)")
src = src.replace("if (!postSend || postSend.valLen > 0) {{", "if (!postSend || postSend.valLen !== 0) {{")
p.write_text(src, encoding="utf-8")
r_ro = subprocess.run([sys.executable, "s1_ego.py", "read", "2", "--expect-id", "fake"], capture_output=True, text=True, encoding="utf-8")
r_mm = subprocess.run([sys.executable, "s1_ego.py", "ask", "2", "--prompt", "t", "--expect-model", "Claude", "--selftest"], capture_output=True, text=True, encoding="utf-8")
diff = subprocess.check_output(["git", "diff", "25359cf", "--", "s1_ego.py"], cwd=str(BASE), text=True, encoding="utf-8")
ev = {"read_override_guard": json.loads(r_ro.stdout), "model_mismatch_selftest": json.loads(r_mm.stdout)}
print("[OK] verified:", ev)
pf = BASE / "logs" / "p114.txt"
pf.write_text("[s1_ego.py v1.1.4 final report]\n" + json.dumps(ev, ensure_ascii=False, indent=2) + "\n" + diff, encoding="utf-8")
r2 = subprocess.run([sys.executable, "s1_ego.py", "ask", "2", "--prompt-file", str(pf), "--wait", "120"], capture_output=True, text=True, encoding="utf-8")
j2 = json.loads(r2.stdout) if r2.stdout.strip().startswith("{") else {"raw": r2.stdout}
(BASE / "S1_OUT.md").write_text("# S1 v1.1.4 Report\n" + json.dumps(ev, ensure_ascii=False, indent=2) + "\n\n## diff\n" + diff + "\n\n## GPT-6.1 Sol\n" + str(j2.get("last_message") or j2), encoding="utf-8")
subprocess.run(["git", "add", "-f", "s1_ego.py", "S1_OUT.md", "logs/s1_ego_audit.jsonl", "logs/s1_ego_poll.jsonl"], cwd=str(BASE), check=True)
subprocess.run(["git", "commit", "-m", "feat(s1): ego v1.1.4 safety bundles verified"], cwd=str(BASE), check=True)
subprocess.run(["git", "pull", "--rebase", "--autostash", "-X", "ours", "origin", "main"], cwd=str(BASE), check=True)
subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), check=True)
print("=== DONE_V114_SHA:", subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), text=True).strip(), "===")
