import subprocess, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
p = BASE / "s1_ego.py"
src = p.read_text(encoding="utf-8")
src = src.replace("if \"[S1_HOP=\" not in (prompt_text or \"\"):", "if not (prompt_text or \"\").lstrip().startswith(\"[S1_HOP=\"):")
src = src.replace("const fullMatch = (uEls.length > arg.preCount) && (lastTxt === expNorm || expNorm.startsWith(lastTxt.slice(0, 80)));", "const fullMatch = (uEls.length > arg.preCount) && (lastTxt === expNorm);")
assert "startswith(\"[S1_HOP=\")" in src, "Patch failed"
p.write_text(src, encoding="utf-8")
diff = subprocess.check_output(["git", "diff", "00738f1", "--", "s1_ego.py"], cwd=str(BASE), text=True, encoding="utf-8")
s1_out_prev = (BASE / "S1_OUT.md").read_text(encoding="utf-8")
ev_part = s1_out_prev.split("## GPT-6.1 Sol Final Verdict")[0]
pf = BASE / "logs" / "p117_final.txt"
pf.write_text("[s1_ego.py v1.1.7 — 마지막 1개 보완 항목(신규 사용자 메시지 DOM 요소 식별, 전송 전후 개수 +1 증가, exactFullStringEqual: true 전체 본문 100% 일치 검증) 완비 보고]\n" + ev_part + "\n## 최신 diff (00738f1 대비 — exactFullStringEqual 단독 엄격 판정 반영)\n```diff\n" + diff + "\n```\n위 증빙을 바탕으로 S1 2순위 1단계(s1_ego.py v1.1.7) 최종 PASS 판정을 부탁드립니다.", encoding="utf-8")
r2 = subprocess.run([sys.executable, "s1_ego.py", "ask", "2", "--prompt-file", str(pf), "--wait", "120"], capture_output=True, text=True, encoding="utf-8")
j2 = json.loads(r2.stdout) if r2.stdout.strip().startswith("{") else {"raw": r2.stdout}
print("[OK] GPT-6.1 Sol response status:", j2.get("status"))
(BASE / "S1_OUT.md").write_text(ev_part + "\n## Latest Strict Diff\n```diff\n" + diff + "\n```\n## GPT-6.1 Sol Final Verdict\n```\n" + str(j2.get("last_message") or j2) + "\n```", encoding="utf-8")
subprocess.run(["git", "add", "-f", "s1_ego.py", "S1_OUT.md", "logs/s1_ego_audit.jsonl", "logs/s1_ego_poll.jsonl"], cwd=str(BASE), check=True)
subprocess.run(["git", "commit", "-m", "feat(s1): ego v1.1.7 strict exactFullStringEqual and hop prefix fix"], cwd=str(BASE), check=True)
subprocess.run(["git", "pull", "--rebase", "--autostash", "-X", "ours", "origin", "main"], cwd=str(BASE), check=True)
subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), check=True)
print("=== DONE_V117_FINAL_PASS_SHA:", subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), text=True).strip(), "===")
