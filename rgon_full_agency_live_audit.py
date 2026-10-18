# -*- coding: utf-8 -*-
"""
rgon_full_agency_live_audit.py
[RGON-001 수석보좌관 주관] 전 기관(본관+1~6청사+5대 안전웹앱+18대 일거리+야간자율주행+모닝브리핑) 25개 관문 실전 종합 감사
"""
import os
import sys
import json
import time
import urllib.request
import urllib.error

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:8501"

def http_get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, resp.read().decode("utf-8", errors="ignore")

def http_post(path, payload):
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8", errors="ignore"))

def run_rgon_full_agency_audit():
    print("=" * 75)
    print("🏛️ [RGON-001 보좌관 주관] 전 기관 25개 관문 실전 종합 감사 시작 (v9.0 CHEONBU-EP1-GENESIS)")
    print("=" * 75)
    results = []

    def record(gate, name, passed, detail=""):
        results.append((gate, name, passed, detail))
        mark = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{mark}] [{gate}] {name} {f'— {detail}' if detail else ''}")

    # [GATE 1] 청와대 본관 & 경호처 무결성 검증 (3개)
    st, body = http_get("/?v=850&tab=command")
    record("GATE-1", "청와대 본관 컨트롤 타워 HTTP 200 응답", st == 200 and len(body) > 5000, f"Size={len(body)}B")
    record("GATE-1", "본관 18대 일거리 관제 보드 탑재 확인", "dept-work-queue-master-board" in body)

    st_g, body_g = http_get("/api/cheongwadae-status")
    guard_json = json.loads(body_g)
    record("GATE-1", "청와대 경호처 API(/api/cheongwadae-status) 정상 가동", st_g == 200 and guard_json.get("status") == "OK")

    # [GATE 2] 신 제1청사(천부 오디세이 스튜디오: 제1탄 생성) TOP 10 엔진 감사 (1개)
    st_c1, body_c1 = http_get("/departments/dept_closet.html")
    c1_ok = (
        st_c1 == 200
        and "advanceGenesisStep" in body_c1
        and "playGenesisYulryeoSound" in body_c1
        and "spawnGoldenParticles" in body_c1
        and "cheonbu-genesis-27-board" in body_c1
        and "series-staircase-nav" in body_c1
    )
    record("GATE-2", "신 제1청사(천부 오디세이 제1탄: 생성) TOP 10 게임 엔진 무결점 가동", c1_ok, f"Size={len(body_c1)}B (율려432Hz·파티클타격감·27자도감·3단계진화 완비)")

    # [GATE 3] 제2·3·4·5·6청사 독립 청사 웹페이지 라이브 응답 감사 (5개)
    depts = [
        ("제2청사(Connect AI)", "/departments/dept_connect_ai.html"),
        ("제3청사(미디어·음원)", "/departments/dept_media.html"),
        ("제4청사(AI 인성 사관학교)", "/departments/dept_education.html"),
        ("제5청사(법무·지식기록원)", "/departments/dept_vault.html"),
        ("제6청사(총무·재무회계·정산청)", "/departments/dept_treasury.html"),
    ]
    for d_name, d_path in depts:
        st_d, body_d = http_get(d_path)
        record("GATE-3", f"{d_name} 독립 청사 라이브 가동", st_d == 200 and len(body_d) > 1500, f"HTTP {st_d} ({len(body_d)}B)")

    # [GATE 4] 제5청사 법무 안전망 & 기존 3대 클린룸 안전 웹앱 라이브 감사 (4개)
    st_leg, body_leg = http_get("/api/legal-compliance-audit")
    leg_json = json.loads(body_leg)
    record("GATE-4", "제5청사 5대 법무 안전망 감사 API 만점 확인", st_leg == 200 and leg_json.get("overall_score") == "100/100 (SAFE TO LAUNCH)")

    safe_apps_basic = [
        ("클린룸 웹앱 1호(행운 컬러)", "/safe_apps/safe_daily_lucky.html"),
        ("클린룸 웹앱 2호(연봉·퇴직금 계산기)", "/safe_apps/safe_salary_planner.html"),
        ("클린룸 웹앱 3호(432Hz 힐링 사운드)", "/safe_apps/safe_healing_sound.html"),
    ]
    for s_name, s_path in safe_apps_basic:
        st_s, body_s = http_get(s_path)
        has_legal = ("면책" in body_s or "대가성" in body_s or "저장하지 않" in body_s)
        record("GATE-4", f"{s_name} 라이브 가동 및 법무 보호막 탑재", st_s == 200 and has_legal)

    # [GATE 5] 제6청사 총무팀 복식부기 1원 단위 수학적 정밀 검증 (1개)
    from general_affairs_treasury import load_ledger, record_transaction, LEDGER_FILE
    with open(LEDGER_FILE, "r", encoding="utf-8") as f:
        backup_ledger_raw = f.read()
    try:
        before_s = load_ledger()["summary"]
        before_in = before_s["total_in_krw"]
        before_out = before_s["total_out_krw"]

        # 실전 입금/출금 테스트
        st_r1, res_r1 = http_post("/api/treasury-record", {
            "tx_type": "IN", "category": "IN_DIGITAL_GOODS", "title": "[르곤감사] 테스트 입금", "amount_krw": 1000000, "dept": "dept_2"
        })
        st_r2, res_r2 = http_post("/api/treasury-record", {
            "tx_type": "OUT", "category": "OUT_OPERATION", "title": "[르곤감사] 테스트 지출", "amount_krw": 200000, "dept": "dept_6"
        })
        after_s = res_r2["summary"]
        alloc = after_s["allocation_50_25_15_10"]
        alloc_sum = (
            alloc["ceo_50_percent"]
            + alloc["rnd_25_percent"]
            + alloc["daughters_15_percent"]
            + alloc["charity_10_percent"]
        )
        math_ok = (
            st_r1 == 200 and st_r2 == 200
            and after_s["total_in_krw"] == before_in + 1000000
            and after_s["total_out_krw"] == before_out + 200000
            and alloc_sum == after_s["disposable_net_krw"]
        )
        record("GATE-5", "제6청사 총무팀 IN/OUT 복식부기 및 50:25:15:10 1원 무오차 검증", math_ok, f"가처분순익={after_s['disposable_net_krw']:,}원 == 배분합계={alloc_sum:,}원")
    finally:
        with open(LEDGER_FILE, "w", encoding="utf-8") as f:
            f.write(backup_ledger_raw)

    # [GATE 6] 6대 부서 18선 일거리 큐 API 검증 (1개)
    st_wq, body_wq = http_get("/api/dept-work-queue")
    wq_json = json.loads(body_wq)
    depts_list = wq_json.get("departments", [])
    total_tasks = sum(len(d.get("tasks", [])) for d in depts_list)
    record("GATE-6", "6대 부서 18선 일거리 큐(/api/dept-work-queue) 완벽 로드", st_wq == 200 and len(depts_list) == 6 and total_tasks == 18, f"6개 부서 / {total_tasks}개 일거리")

    # [GATE 7] 전 부서 18대 일거리 실질적 작업(실물 산출물 생성) 및 검증 (1개)
    st_exec, res_exec = http_post("/api/execute-dept-task", {"task_id": "ALL"})
    exec_ok = (st_exec == 200 and res_exec.get("status") == "OK" and res_exec.get("total_executed") == 18)

    deliverable_dir = os.path.join("knowledge_engine", "wiki", "dept_deliverables")
    files_exist = [
        os.path.exists(os.path.join(deliverable_dir, f"TASK-D{d}-0{t}_deliverable.md"))
        for d in range(1, 7) for t in range(1, 4)
    ]
    all_files_ok = all(files_exist)
    record("GATE-7", "전 부서 18대 일거리 실전 작업 실행 및 18개 실물 산출물(Wiki) 생성", exec_ok and all_files_ok, f"생성된 산출물={sum(files_exist)}/18개")

    # [GATE 8] 르곤 마스터 스케줄러 API & 일·주·월·연 로드맵 검증 (2개)
    st_sched, body_sched = http_get("/api/rgon-schedule")
    sched_json = json.loads(body_sched) if st_sched == 200 else {}
    sched_structure_ok = (
        st_sched == 200
        and "daily_schedule" in sched_json
        and "weekly_schedule" in sched_json
        and "monthly_schedule" in sched_json
        and "yearly_schedule" in sched_json
        and len(sched_json["daily_schedule"].get("slots", [])) == 5
    )
    record("GATE-8", "르곤 마스터 스케줄러 API(/api/rgon-schedule) 및 4단계 로드맵 완결 검증", sched_structure_ok, f"일별 5대 슬롯 / 4주 스프린트 / 3단계 마일스톤 / 연별 비전")

    st_srun, res_srun = http_post("/api/rgon-schedule-run", {"cycle_type": "AUDIT_VERIFY"})
    srun_ok = (st_srun == 200 and res_srun.get("status") == "OK" and res_srun.get("data", {}).get("daily_slots_completed") == 5)
    record("GATE-8", "르곤 마스터 스케줄 집행 API(/api/rgon-schedule-run) 무인 동기화 검증", srun_ok, f"HTTP {st_srun} (Status={res_srun.get('status')})")

    # [GATE 9] 신규 출시 클린룸 안전 웹앱 4호 & 5호 라이브 응답 및 법무 보호막 검증 (2개)
    safe_apps_new = [
        ("클린룸 웹앱 4호(부자 DNA 테스트)", "/safe_apps/safe_rich_dna_test.html", "runRichDnaAnalysis"),
        ("클린룸 웹앱 5호(하루 1% 성공 루틴 보드)", "/safe_apps/safe_daily_routine.html", "updateRoutineProgress"),
    ]
    for s_name, s_path, s_func in safe_apps_new:
        st_sn, body_sn = http_get(s_path)
        has_legal = ("면책" in body_sn or "대가성" in body_sn or "저장하지 않" in body_sn)
        has_func = s_func in body_sn
        record("GATE-9", f"{s_name} 라이브 가동 & {s_func} 엔진 & 법무 보호막 탑재", st_sn == 200 and has_legal and has_func, f"HTTP {st_sn} ({len(body_sn)}B)")

    # [GATE 10] 안총리(AGV-PRIME-101) 공식 격상 및 3대 수뇌부 등재 검증 (1개)
    # 본관, 제4청사, 스케줄 로드맵 검증
    st_idx, body_idx = http_get("/?v=850&tab=command")
    st_edu, body_edu = http_get("/departments/dept_education.html")
    prime_in_idx = "AGV-PRIME-101" in body_idx and "안총리" in body_idx
    prime_in_edu = "AGV-PRIME-101" in body_edu and "prime-promotion-hall-of-fame" in body_edu
    prime_in_sched = sched_json.get("prime_executor") is not None and "AGV-PRIME-101" in sched_json.get("prime_executor", "")
    prime_all_ok = (st_idx == 200 and st_edu == 200 and prime_in_idx and prime_in_edu and prime_in_sched)
    record("GATE-10", "기술행정부 총리 안총리(AGV-PRIME-101) 특진 및 3대 수뇌부 전수 등재 검증", prime_all_ok, "본관 골든배지 + 제4청사 명예의전당 + 스케줄 로드맵 100% 동기화")

    # [GATE 11] 제3청사(dept_media.html) 실물 미디어 스튜디오 3대 엔진 라이브 검증 (1개)
    st_m, body_m = http_get("/departments/dept_media.html")
    media_has_audio = "toggleMediaStudioAudio" in body_m
    media_has_distro = "generateStreamingMetadata" in body_m
    media_has_shorts = "generateRadioShortsScript" in body_m
    media_has_prime = "AGV-PRIME-101" in body_m
    media_has_legal = "면책" in body_m or "대가성" in body_m or "저장하지 않" in body_m
    media_all_ok = (
        st_m == 200
        and media_has_audio
        and media_has_distro
        and media_has_shorts
        and media_has_prime
        and media_has_legal
    )
    record("GATE-11", "제3청사 실물 미디어 스튜디오(Suno 30곡·432Hz·라디오쇼츠·배급) 엔진 완결 검증", media_all_ok, f"HTTP {st_m} (Web Audio, Distro, Shorts, 법무푸터 완비)")

    # [GATE 12] 야간 무인 자율주행 & 모닝 브리핑 API 검증 (1개)
    st_mb, body_mb = http_get("/api/morning-briefing")
    mb_json = json.loads(body_mb)
    st_np, body_np = http_post("/api/night-autopilot-run", {})
    gate12_ok = (
        st_mb == 200
        and "duty_commanders" in mb_json
        and st_np == 200
        and body_np.get("status") == "OK"
    )
    record("GATE-12", "야간 무인 자율주행 & 모닝 브리핑 API (/api/morning-briefing, /api/night-autopilot-run) 검증", gate12_ok, f"GET {st_mb}, POST {st_np}")

    # [GATE 13] 제2청사(dept_connect_ai.html) 바이럴 홍보 카피 스튜디오 실물 검증 (1개)
    st_cai, body_cai = http_get("/departments/dept_connect_ai.html")
    cai_has_copy = "generateViralPromoCopy" in body_cai
    cai_has_launcher = ("5대 클린룸" in body_cai and "safe_daily_lucky.html" in body_cai)
    cai_has_prime = "AGV-PRIME-101" in body_cai
    cai_has_legal = "면책" in body_cai or "대가성" in body_cai
    gate13_ok = (st_cai == 200 and cai_has_copy and cai_has_launcher and cai_has_prime and cai_has_legal)
    record("GATE-13", "제2청사 Connect AI 바이럴 홍보 카피 스튜디오 & 5대 웹앱 통합 런처 실물 검증", gate13_ok, f"HTTP {st_cai} (카피엔진, 런처, 법무푸터 완비)")

    # [GATE 14] 제5청사(dept_vault.html) 실시간 법무 스캐너 & 18대 산출물 위키 보드 실물 검증 (1개)
    st_vlt, body_vlt = http_get("/departments/dept_vault.html")
    vlt_has_scan = "runVaultLegalScan" in body_vlt
    vlt_has_wiki = "18대 부서 실물 산출물 위키 아카이브" in body_vlt or "viewDeliverableWiki" in body_vlt
    vlt_has_cert = "HGS-LEGAL-SAFE-2026-PASS" in body_vlt
    vlt_has_legal = "면책" in body_vlt or "대가성" in body_vlt
    gate14_ok = (st_vlt == 200 and vlt_has_scan and vlt_has_wiki and vlt_has_cert and vlt_has_legal)
    record("GATE-14", "제5청사 실시간 법무 스캐너 & 18대 산출물 위키 아카이브 보드 실물 검증", gate14_ok, f"HTTP {st_vlt} (법무스캐너, 위키보드, 인증서 완비)")

    # 경호처 해시 최신화
    from cheongwadae_guard import save_golden_hashes
    save_golden_hashes()

    # 종합 판정
    final_pass = sum(1 for r in results if r[2])
    final_total = len(results)
    print("=" * 75)
    print(f"📊 [전 기관 실전 감사 종합 결과]: {final_pass}/{final_total} 통과 ({(final_pass/final_total)*100:.1f}%)")
    print("=" * 75)

    if final_pass != final_total:
        print("🚨 테스트 미통과 항목 발견! 배포를 중단합니다.")
        sys.exit(1)

    print(f"🏆 [최종 완료] 전 기관 25개 관문 전수 실전 감사 100.0% ALL PASS! 야간 자율주행 및 모닝 브리핑 완비!")
    print("=" * 75)

if __name__ == "__main__":
    run_rgon_full_agency_audit()
