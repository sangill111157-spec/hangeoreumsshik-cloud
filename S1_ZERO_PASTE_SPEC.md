# S1 Zero-Paste Daemon 과업 명세서 (1순위 무복붙 자동화)
1. **감시 대상**: `ego-browser` Space 0 (`argon` 르곤 보좌관 대화창)의 `===S1_AUTO_START:ID=== ... ===S1_AUTO_END:ID===` 코드 블록.
2. **이관 및 실행 범위**:
   - 감지된 코드 블록이 `STABLE_SCANS=2` (연속 2회 스캔) 동안 동일한 SHA-256 해시를 유지할 때만 안정화된 명령으로 판정.
   - `executed_ids.json` 원장을 대조하여 이미 실행된 ID나 중복 해시는 즉시 차단(`BLOCK_DUP_PAYLOAD=True`).
   - 검증된 코드는 `s1_runs/{ID}.py`로 저장·실행하며, 로컬 브릿지 서버(`http://127.0.0.1:8504/api/chat`) 및 명령 원장(`s1_command_ledger.jsonl`)에 전체 UUID(`uuid4`)와 함께 기록하고 결과 파일(`s1_runs/live_cycle_result.json`)을 생성함.
3. **금지 사항 및 킬스위치 (Non-Goals & Safety)**:
   - 외부 SNS/유튜브 무단 게시 절대 금지 (로컬 실행 증빙 및 GitHub 저장소 커밋 전용).
   - `KILL_SWITCH.flag` 파일이 존재(내용 `ON`, `1`, `TRUE` 또는 빈 플래그 파일)하면 다음 사이클 시작 즉시 감지하여 모든 실행을 중단하고 안전 정지(`IMMEDIATE_SAFE_HALT`)함.
   - `--dry-run` 모드에서는 브라우저 탭 스캔과 블록 감지만 기록하고 실제 코드 실행·원장 변경·Git 푸시를 일절 수행하지 않음.
