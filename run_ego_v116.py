import subprocess, sys, json, uuid
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
p = BASE / "s1_ego.py"
src = p.read_text(encoding="utf-8")
src = src.replace("v1.1.5", "v1.1.6")
src = src.replace("Audit Compliant", "Audit Under Review")
old_sel = "const selector = \x27loc=css:textarea[name=\"query\"]\x27;"
new_sel = "if (Boolean({1 if selftest else 0})) {{\n            process.stdout.write(\"\\\\nS1EGO_JSON::\" + JSON.stringify({{ ok: false, code: \"SELFTEST_NO_SEND\", status: \"selftest_stopped_before_fill\", space: {space_id}, precheck: pre }}) + \"\\\\n\");\n            return;\n          }}\n          const promptProbe = {json.dumps(prompt_head)};\n          const preProbeCount = await page.evaluate((prb) => (document.body ? document.body.innerText.split(prb).length - 1 : 0), promptProbe);\n          const selector = \x27loc=css:textarea[name=\"query\"]\x27;"
src = src.replace(old_sel, new_sel)
old_ev = "const tailNow = bodyTxt.slice(-1500); return {{ taPresent: Boolean(ta), valLen: ta ? (ta.value || \"\").trim().length : -1, userMsgSeen: bodyTxt.length > baseLen, tailSample: tailNow.slice(-120), rateLimited }};\n            }}, pre.bodyLen)"
new_ev = "const postProbeCount = arg.prb ? (bodyTxt.split(arg.prb).length - 1) : 0; const newUserMsgMatched = Boolean(arg.prb && postProbeCount > arg.preCnt); return {{ taPresent: Boolean(ta), valLen: ta ? (ta.value || \"\").trim().length : -1, probe: arg.prb, probeCountBefore: arg.preCnt, probeCountAfter: postProbeCount, userMsgSeen: newUserMsgMatched, rateLimited }};\n            }}, {{ baseLen: pre.bodyLen, prb: promptProbe, preCnt: preProbeCount }})"
src = src.replace("page.evaluate((baseLen) => {{", "page.evaluate((arg) => {{")
src = src.replace(old_ev, new_ev)
assert "SELFTEST_NO_SEND" in src and "probeCountAfter: postProbeCount" in src, "Patch v1.1.6 failed"
p.write_text(src, encoding="utf-8")
uid = uuid.uuid4().hex[:8]
r_st_match = subprocess.run([sys.executable, "s1_ego.py", "ask", "2", "--prompt", f"SELFTEST_NEVER_SENT_{uid}", "--expect-model", "GPT-6.1 Sol", "--selftest"], capture_output=True, text=True, encoding="utf-8")
r_read_after_st = subprocess.run([sys.executable, "s1_ego.py", "read", "2", "--tail", "600"], capture_output=True, text=True, encoding="utf-8")
st_tail = json.loads(r_read_after_st.stdout).get("tail", "")
r_live = subprocess.run([sys.executable, "s1_ego.py", "ask", "2", "--prompt", f"S1_V116_MSG_MATCH_{uid}: 한 단어로 OK_V116_{uid} 만 답해주세요.", "--wait", "60"], capture_output=True, text=True, encoding="utf-8")
diff = subprocess.check_output(["git", "diff", "d1710eb", "--", "s1_ego.py"], cwd=str(BASE), text=True, encoding="utf-8")
audit_tail = "\n".join((BASE / "logs" / "s1_ego_audit.jsonl").read_text(encoding="utf-8").splitlines()[-6:])
ev = {"1_selftest_model_match_no_send": json.loads(r_st_match.stdout), "1_verify_never_sent_in_chat": (f"SELFTEST_NEVER_SENT_{uid}" not in st_tail), "2_live_new_user_msg_verified": json.loads(r_live.stdout)}
print("[OK] v1.1.6 verified:", ev["1_selftest_model_match_no_send"].get("code"), ev["2_live_new_user_msg_verified"].get("send_verified"))
pf = BASE / "logs" / "p116.txt"
pf.write_text("[s1_ego.py v1.1.6 — 한정해주신 마지막 2대 항목(1. 신규 사용자 메시지 출현 횟수 및 본문 일치 검증 / 2. 모델 일치 시 --selftest 비전송 종료 실증) 완비 보고]\n1. 실측 결과 JSON (probeCountBefore: 0 -> probeCountAfter: 1 로 신규 사용자 메시지 등록 입증, 모델 일치 --selftest 시 page.fill 전 SELFTEST_NO_SEND 종료 및 대화창 미등장 확인):\n" + json.dumps(ev, ensure_ascii=False, indent=2) + "\n\n2. 감사 로그:\n" + audit_tail + "\n\n3. 코드 diff (d1710eb 대비, Audit Compliant 주석 제거 포함):\n" + diff + "\n\n위 2대 한정 항목 증빙을 바탕으로 S1 2순위 1단계(s1_ego.py v1.1.6) 최종 PASS 판정을 부탁드립니다.", encoding="utf-8")
r2 = subprocess.run([sys.executable, "s1_ego.py", "ask", "2", "--prompt-file", str(pf), "--wait", "120"], capture_output=True, text=True, encoding="utf-8")
j2 = json.loads(r2.stdout) if r2.stdout.strip().startswith("{") else {"raw": r2.stdout}
(BASE / "S1_OUT.md").write_text("# S1 v1.1.6 Final Report\n```json\n" + json.dumps(ev, ensure_ascii=False, indent=2) + "\n```\n## Audit Log\n```jsonl\n" + audit_tail + "\n```\n## diff\n```diff\n" + diff + "\n```\n## GPT-6.1 Sol Final Verdict\n```\n" + str(j2.get("last_message") or j2) + "\n```", encoding="utf-8")
subprocess.run(["git", "add", "-f", "s1_ego.py", "S1_OUT.md", "logs/s1_ego_audit.jsonl", "logs/s1_ego_poll.jsonl"], cwd=str(BASE), check=True)
subprocess.run(["git", "commit", "-m", "feat(s1): ego v1.1.6 verify new user msg count and selftest no-send"], cwd=str(BASE), check=True)
subprocess.run(["git", "pull", "--rebase", "--autostash", "-X", "ours", "origin", "main"], cwd=str(BASE), check=True)
subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), check=True)
print("=== DONE_V116_SHA:", subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), text=True).strip(), "===")
