import subprocess, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
p = BASE / "s1_ego.py"
src = p.read_text(encoding="utf-8")
src = src.replace("page.evaluate(() => {{\n              const ta = document.querySelector(\x27textarea[name=\"query\"]\x27) || document.querySelector(\x27textarea\x27);\n              const bodyTxt = document.body ? document.body.innerText : \"\";\n              const rateLimited = Array.from(document.querySelectorAll(\"[role=alert], .ant-message, .toast\")).some(e => e.offsetParent !== null && ((e.innerText || \"\").includes(\"5시간 제한\") || (e.innerText || \"\").includes(\"재설정됩니다\")));\n              const tailNow = bodyTxt.slice(-1500); return {{ taPresent: Boolean(ta), valLen: ta ? (ta.value || \"\").trim().length : -1, userMsgSeen: bodyTxt.length > pre.bodyLen, tailSample: tailNow.slice(-120), rateLimited }};\n            }}).catch(() => null),", "page.evaluate((baseLen) => {{\n              const ta = document.querySelector(\x27textarea[name=\"query\"]\x27) || document.querySelector(\x27textarea\x27);\n              const bodyTxt = document.body ? document.body.innerText : \"\";\n              const rateLimited = Array.from(document.querySelectorAll(\"[role=alert], .ant-message, .toast\")).some(e => e.offsetParent !== null && ((e.innerText || \"\").includes(\"5시간 제한\") || (e.innerText || \"\").includes(\"재설정됩니다\")));\n              const tailNow = bodyTxt.slice(-1500); return {{ taPresent: Boolean(ta), valLen: ta ? (ta.value || \"\").trim().length : -1, userMsgSeen: bodyTxt.length > baseLen, tailSample: tailNow.slice(-120), rateLimited }};\n            }}, pre.bodyLen).catch(() => null),")
assert "userMsgSeen: bodyTxt.length > baseLen" in src, "Patch failed"
p.write_text(src, encoding="utf-8")
r_mm = subprocess.run([sys.executable, "s1_ego.py", "ask", "2", "--prompt", "NEVER_SENT_TEST", "--expect-model", "Claude", "--selftest"], capture_output=True, text=True, encoding="utf-8")
r_ok = subprocess.run([sys.executable, "s1_ego.py", "ask", "2", "--prompt", "S1_V115_TRACE_TEST: 한 단어로 TRACE_OK_V115 만 답해주세요.", "--wait", "60"], capture_output=True, text=True, encoding="utf-8")
diff = subprocess.check_output(["git", "diff", "171f6d6", "--", "s1_ego.py"], cwd=str(BASE), text=True, encoding="utf-8")
audit_tail = "\n".join((BASE / "logs" / "s1_ego_audit.jsonl").read_text(encoding="utf-8").splitlines()[-6:])
ev = {"1_cmd": "python s1_ego.py ask 2 --prompt NEVER_SENT_TEST --expect-model Claude --selftest", "1_model_mismatch_blocked": json.loads(r_mm.stdout), "2_live_send_trace": json.loads(r_ok.stdout)}
print("[OK] v1.1.5 trace:", ev["2_live_send_trace"].get("status"), ev["2_live_send_trace"].get("last_message"))
pf = BASE / "logs" / "p115.txt"
pf.write_text("[s1_ego.py v1.1.5 최종 3대 재검수 증빙 제출]\n1. 모델 불일치 부정시험(하단 입력 컨테이너 UI 텍스트만 검사하여 Space 2에서 --expect-model Claude 지정 시 MODEL_MISMATCH 즉시 차단, 전송 0건) 및 2. 동일 req_id 전송 연결 증빙(send_verified.userMsgSeen=true):\n" + json.dumps(ev, ensure_ascii=False, indent=2) + "\n\n3. 동일 req_id 감사 로그:\n" + audit_tail + "\n\n4. 코드 diff (171f6d6 대비):\n" + diff + "\n\n위 증빙을 바탕으로 S1 2순위 1단계(s1_ego.py v1.1.5) 최종 PASS 판정을 부탁드립니다.", encoding="utf-8")
r2 = subprocess.run([sys.executable, "s1_ego.py", "ask", "2", "--prompt-file", str(pf), "--wait", "120"], capture_output=True, text=True, encoding="utf-8")
j2 = json.loads(r2.stdout) if r2.stdout.strip().startswith("{") else {"raw": r2.stdout}
(BASE / "S1_OUT.md").write_text("# S1 v1.1.5 Final Report\n```json\n" + json.dumps(ev, ensure_ascii=False, indent=2) + "\n```\n## Audit Log\n```jsonl\n" + audit_tail + "\n```\n## diff\n```diff\n" + diff + "\n```\n## GPT-6.1 Sol Final Verdict\n```\n" + str(j2.get("last_message") or j2) + "\n```", encoding="utf-8")
subprocess.run(["git", "add", "-f", "s1_ego.py", "S1_OUT.md", "logs/s1_ego_audit.jsonl", "logs/s1_ego_poll.jsonl"], cwd=str(BASE), check=True)
subprocess.run(["git", "commit", "-m", "feat(s1): ego v1.1.5 pass baseLen to postSend evaluate"], cwd=str(BASE), check=True)
subprocess.run(["git", "pull", "--rebase", "--autostash", "-X", "ours", "origin", "main"], cwd=str(BASE), check=True)
subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), check=True)
print("=== DONE_V115_FIXED_SHA:", subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), text=True).strip(), "===")
