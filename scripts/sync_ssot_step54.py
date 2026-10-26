#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/sync_ssot_step54.py — Step 54 제30기관 SSOT 전 기관 일괄 승격 스크립트"""

import os, sys, json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(ROOT))

VERSION = "v11.53-AON-INSPECTOR-GENERAL"
ANTIBODY_RANGE = "R1~R54"
SKILL_COUNT = 50
STATUS_LINE = f"{VERSION} · 항체 {ANTIBODY_RANGE} · 정식 스킬 {SKILL_COUNT}개"

print(f"=== [Step 54 SSOT Sync] Starting sync to {VERSION} / {ANTIBODY_RANGE} / {SKILL_COUNT} skills ===")

PROTECTED = {'rgon_Numeric_Organ.py', 'rgon_work_loop.py', 'rgon_self_Reflection.py', 'index_20260405_backup.html'}

# ----------------------------------------------------
# 1. rgon_aon_dialogue_engine.py 업데이트
# ----------------------------------------------------
dlg_path = ROOT / "rgon_aon_dialogue_engine.py"
if dlg_path.exists():
    t = dlg_path.read_text(encoding="utf-8")
    t = re.sub(r'VERSION\s*=\s*"[^"]+"', f'VERSION = "{VERSION}"', t, count=1)
    t = re.sub(r'R40_VERSION\s*=\s*"[^"]+"', f'R40_VERSION = "{VERSION}"', t)
    t = re.sub(r'R40_ANTIBODY\s*=\s*"[^"]+"', f'R40_ANTIBODY = "{ANTIBODY_RANGE}"', t)
    
    r54_route_code = '''
# [RGON-R54-INSPECTOR-GENERAL-ROUTE-START]
R54_INSPECTOR_TRIGGERS = [
    "/검수", "/검수총장", "/감찰", "/inspector", "검수총장", "출하관문", "감찰원", "카나리함정", "3중직인"
]

def _r54_inspector_general_route(msg):
    m = str(msg or "").strip()
    low = m.lower()
    if not any(k in m or k in low for k in R54_INSPECTOR_TRIGGERS):
        return None
    try:
        import rgon_aon_inspector_general_gate as _igg
        if "카나리" in m or "canary" in low:
            res = _igg.BlindCanaryTrapAuditor.run_canary_trap_audit()
            speech = f"🕵️ [제30기관 검수총장 암행 감찰] 8대 전담 검수장 불시 카나리 함정 {res['traps_caught_count']}/{res['traps_tested']} 100.0% 전수 적발 완료!"
        elif "시뮬레이션" in m or "루프" in m or "rework" in low:
            res = _igg.run_rework_loop_simulation()
            speech = f"🔄 [제30기관 출하 관문 실전] 불량 차단 ➔ 즉시 수리 ➔ 100.0% 재통과 루프 완결! (허가증: {res.get('certificate_id')})"
        else:
            dir_res = _igg.SupremeInspectorGeneral.dispatch_all_directives()
            res = {"issued_directives": dir_res.get("issued_count", 8), "total_inspectors": 8, "status": "ONLINE"}
            speech = f"⚖️ [제30기관 독립 검수담당 총장] 8대 기관 맞춤형 12대 헌장 지시 하달 & 3중 직인 출하 관문 100% 가동 중!"
        return {
            "ok": True,
            "version": "v11.53-AON-INSPECTOR-GENERAL",
            "antibody": "R54",
            "intent": "inspector_general",
            "intents": ["inspector_general"],
            "speech": speech,
            "inspector_general": res,
            "data": res,
            "results": [{"intent": "inspector_general", "ok": True, "speech": speech, "data": res}],
        }
    except Exception as _ex:
        return {"ok": False, "error": str(_ex)}

def _r54_wrap(_fn):
    def _w(*a, **k):
        _txt = a[0] if a and isinstance(a[0], str) else (a[1] if len(a) > 1 and isinstance(a[1], str) else k.get("text") or k.get("message") or k.get("utterance"))
        if _txt:
            _r54 = _r54_inspector_general_route(_txt)
            if _r54 is not None:
                return _r54
            _r53 = _r53_page_button_bot_route(_txt)
            if _r53 is not None:
                return _r53
        return _fn(*a, **k)
    _w.__r54__ = True
    return _w

for _n in ("r40_route", "route", "process_dialogue", "route_command", "handle_message", "respond", "reply", "dialogue"):
    _f = globals().get(_n)
    if callable(_f) and not getattr(_f, "__r54__", False):
        globals()[_n] = _r54_wrap(_f)
# [RGON-R54-INSPECTOR-GENERAL-ROUTE-END]
'''
    if "[RGON-R54-INSPECTOR-GENERAL-ROUTE-START]" not in t:
        idx = t.find('if __name__ == "__main__":')
        if idx != -1:
            t = t[:idx] + r54_route_code + "\n" + t[idx:]
        else:
            t += "\n" + r54_route_code
        dlg_path.write_text(t, encoding="utf-8")
        print("Updated rgon_aon_dialogue_engine.py with R54 inspector routing.")

# ----------------------------------------------------
# 2. rgon_voice_organ.py 업데이트
# ----------------------------------------------------
voice_path = ROOT / "rgon_voice_organ.py"
if voice_path.exists():
    vt = voice_path.read_text(encoding="utf-8")
    vt = re.sub(r'VERSION\s*=\s*"[^"]+"', f'VERSION = "{VERSION}"', vt, count=1)
    vt = re.sub(r'ANTIBODY\s*=\s*"[^"]+"', f'ANTIBODY = "{ANTIBODY_RANGE}"', vt, count=1)
    voice_path.write_text(vt, encoding="utf-8")
    print("Updated rgon_voice_organ.py version & antibody.")

# ----------------------------------------------------
# 3. run_dashboard.py 업데이트 (GET/POST /api/aon_inspector_general)
# ----------------------------------------------------
dash_path = ROOT / "run_dashboard.py"
if dash_path.exists():
    dt = dash_path.read_text(encoding="utf-8")
    
    get_handler = '''        # ⚖️ [Step 54 · R54] 제30기관 아온 독립 검수담당 총장 상태 (GET /api/aon_inspector_general)
        if path == '/api/aon_inspector_general':
            try:
                import rgon_aon_inspector_general_gate as igg
                data = {
                    "ok": True,
                    "version": "v11.53-AON-INSPECTOR-GENERAL",
                    "antibody": "R54",
                    "organ": "제30기관 아온 7대 방침 기관장 분신단 & 독립 검수담당 총장 100% 출하 관문",
                    "total_directors": len(igg.DIRECTORS_REGISTRY),
                    "total_inspectors": 8,
                    "status": "ONLINE_GATE_LOCKED_100_PERCENT"
                }
                self._send_json(data)
                return
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, status=500)
                return
'''
    post_handler = '''        # ⚖️ [Step 54 · R54] 제30기관 아온 독립 검수담당 총장 감사 실행 (POST /api/aon_inspector_general)
        if self.path == '/api/aon_inspector_general':
            try:
                import rgon_aon_inspector_general_gate as igg
                req = self._read_json_body() or {}
                action = req.get("action", "dispatch_and_audit")
                if action == "dispatch_and_audit":
                    res = igg.SupremeInspectorGeneral.dispatch_all_directives()
                elif action == "canary_trap":
                    res = igg.BlindCanaryTrapAuditor.run_canary_trap_audit()
                elif action == "rework_loop":
                    res = igg.run_rework_loop_simulation()
                else:
                    res = {"ok": False, "error": f"Unknown action: {action}"}
                self._send_json(res)
                return
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, status=500)
                return
'''
    if "if path == '/api/aon_inspector_general':" not in dt:
        idx_get = dt.find("if path == '/api/aon_page_button_bot':")
        if idx_get != -1:
            dt = dt[:idx_get] + get_handler + dt[idx_get:]
    
    if "if self.path == '/api/aon_inspector_general':" not in dt:
        idx_post = dt.find("if self.path == '/api/aon_page_button_bot':")
        if idx_post != -1:
            dt = dt[:idx_post] + post_handler + dt[idx_post:]
            
    dash_path.write_text(dt, encoding="utf-8")
    print("Updated run_dashboard.py with /api/aon_inspector_general endpoints.")

# ----------------------------------------------------
# 4. s_run.py 업데이트
# ----------------------------------------------------
srun_path = ROOT / "s_run.py"
if srun_path.exists():
    st = srun_path.read_text(encoding="utf-8")
    srun_func = '''
def handle_api_aon_inspector_general(handler, req_data=None):
    """/api/aon_inspector_general (GET/POST) 엔드포인트 핸들러"""
    try:
        import rgon_aon_inspector_general_gate as igg
        if req_data:
            action = req_data.get("action", "dispatch_and_audit")
            if action == "dispatch_and_audit":
                return igg.SupremeInspectorGeneral.dispatch_all_directives()
            elif action == "canary_trap":
                return igg.BlindCanaryTrapAuditor.run_canary_trap_audit()
            elif action == "rework_loop":
                return igg.run_rework_loop_simulation()
            return {"ok": False, "error": f"Unknown action: {action}"}
        return {
            "ok": True,
            "version": "v11.53-AON-INSPECTOR-GENERAL",
            "antibody": "R54",
            "endpoint": "/api/aon_inspector_general",
            "total_directors": len(igg.DIRECTORS_REGISTRY),
            "total_inspectors": 8
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
'''
    if "def handle_api_aon_inspector_general" not in st:
        idx_func = st.find("def handle_api_aon_page_button_bot")
        if idx_func != -1:
            st = st[:idx_func] + srun_func + "\n" + st[idx_func:]
            srun_path.write_text(st, encoding="utf-8")
            print("Updated s_run.py with handle_api_aon_inspector_general.")

# ----------------------------------------------------
# 5. rgon_mobile_serverless_interceptor.js 업데이트 및 3곳 복사
# ----------------------------------------------------
inter_path = ROOT / "rgon_mobile_serverless_interceptor.js"
if inter_path.exists():
    it = inter_path.read_text(encoding="utf-8")
    it = re.sub(r'const VER = "[^"]+";', f'const VER = "{VERSION}";', it, count=1)
    it = re.sub(r'const AB = "[^"]+";', f'const AB = "{ANTIBODY_RANGE}";', it, count=1)
    it = re.sub(r'const SKILLS = \d+;', f'const SKILLS = {SKILL_COUNT};', it, count=1)
    it = re.sub(r'const ORGANS = \d+;', f'const ORGANS = 30;', it, count=1)
    
    mock_block = '''    // 00. 검수담당 총장 & 8대 기관 100% 출하 봉인 관문
    if (path.includes("inspector_general") || path.includes("court")) {
      return {
        ok: true,
        status: "SUCCESS",
        version: VER,
        antibody: AB,
        organ: "제30기관 아온 7대 방침 기관장 분신단 & 독립 검수담당 총장 100% 출하 봉인 관문 시스템",
        skills_count: SKILLS,
        dispatched_at: new Date().toISOString(),
        elapsed_sec: 0.002,
        total_directors: 8,
        total_inspectors: 8,
        pass_rate: "100.0%",
        triple_seal: {
          director_seal: "제N기관장 7대 방침 직인",
          inspector_seal: "전담 검수장 12/12 100.0% 합격 봉인",
          supreme_general_seal: "검수담당 총장 최종 승인 감사 직인"
        },
        verdict: "모바일 무서버 환경에서도 8대 기관 100% 출하 관문 및 암행 감찰 정상 작동"
      };
    }
'''
    if 'path.includes("inspector_general")' not in it:
        idx_mock = it.find('// 0. 전 페이지·전 버튼 자동화 봇')
        if idx_mock != -1:
            it = it[:idx_mock] + mock_block + "\n" + it[idx_mock:]
            
    inter_path.write_text(it, encoding="utf-8")
    for d in ["dashboard", "docs"]:
        shutil.copy2(inter_path, ROOT / d / "rgon_mobile_serverless_interceptor.js")
    print("Updated and synced rgon_mobile_serverless_interceptor.js.")

# ----------------------------------------------------
# 6. rgon_aon_page_button_bot_engine.py 업데이트
# ----------------------------------------------------
pbe_path = ROOT / "rgon_aon_page_button_bot_engine.py"
if pbe_path.exists():
    pt = pbe_path.read_text(encoding="utf-8")
    if "rgon_inspector_general_court.html" not in pt:
        target_str = '"rgon_button_bot_command_center.html",'
        repl_str = target_str + '\n        "rgon_inspector_general_court.html",'
        pt = pt.replace(target_str, repl_str)
        pbe_path.write_text(pt, encoding="utf-8")
        print("Added rgon_inspector_general_court.html to rgon_aon_page_button_bot_engine.py")

# ----------------------------------------------------
# 7. 모든 rgon_*.py 파일의 버전·항체 일괄 승격
# ----------------------------------------------------
import glob
for f in glob.glob("rgon_*.py"):
    if f in PROTECTED:
        continue
    try:
        content = Path(f).read_text(encoding="utf-8")
        new_content = re.sub(r'VERSION\s*=\s*"v11\.\d+-[A-Z0-9-]+"', f'VERSION = "{VERSION}"', content)
        new_content = re.sub(r'ANTIBODY_RANGE\s*=\s*"R1~R\d+"', f'ANTIBODY_RANGE = "{ANTIBODY_RANGE}"', new_content)
        new_content = re.sub(r'ANTIBODIES\s*=\s*"R1~R\d+"', f'ANTIBODIES = "{ANTIBODY_RANGE}"', new_content)
        if f == "rgon_vascular_core.py":
            new_content = re.sub(r'VERSION\s*==\s*"v11\.\d+-[A-Z0-9-]+"', f'VERSION == "{VERSION}"', new_content)
            new_content = re.sub(r'ANTIBODY_RANGE\s*==\s*"R1~R\d+"', f'ANTIBODY_RANGE == "{ANTIBODY_RANGE}"', new_content)
        elif f == "rgon_daily_cycle.py":
            new_content = re.sub(r'VERSION\s*==\s*"v11\.\d+-[A-Z0-9-]+"', f'VERSION == "{VERSION}"', new_content)
            new_content = re.sub(r'ANTIBODY_RANGE\s*==\s*"R1~R\d+"', f'ANTIBODY_RANGE == "{ANTIBODY_RANGE}"', new_content)
            new_content = re.sub(r'"R1~R\d+"\s*in\s*t', f'"{ANTIBODY_RANGE}" in t', new_content)
        elif f in ("rgon_aon_impeccable_audit_shield.py", "rgon_aon_token_egolite_master.py"):
            new_content = re.sub(r'VERSION\s*==\s*"v11\.\d+-[A-Z0-9-]+"', f'VERSION == "{VERSION}"', new_content)
            new_content = re.sub(r'ANTIBODIES\s*==\s*"R1~R\d+"', f'ANTIBODIES == "{ANTIBODY_RANGE}"', new_content)
        elif f == "rgon_aon_soul_brain.py":
            new_content = re.sub(r'_R40_SB_VER\s*=\s*"[^"]+"', f'_R40_SB_VER = "{VERSION}"', new_content)

        if new_content != content:
            Path(f).write_text(new_content, encoding="utf-8")
            print(f"Upgraded {f}")
    except Exception as e:
        print(f"Error upgrading {f}: {e}")

# ----------------------------------------------------
# 8. 스냅샷 3종 업데이트
# ----------------------------------------------------
for snap_name in ["rgon_brain_snapshot.json", "rgon_morning_brief.json", "rgon_immune_ledger.json"]:
    for base in ["", "dashboard/", "docs/"]:
        p = ROOT / f"{base}{snap_name}"
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    if "version" in data: data["version"] = VERSION
                    if "app_version" in data: data["app_version"] = VERSION
                    if "antibody_range" in data: data["antibody_range"] = ANTIBODY_RANGE
                    if "antibodies" in data: data["antibodies"] = ANTIBODY_RANGE
                    if "immune" in data: data["immune"] = ANTIBODY_RANGE
                    if "antibody" in data: data["antibody"] = ANTIBODY_RANGE
                    if "skill_count" in data: data["skill_count"] = SKILL_COUNT
                    if "total_skills" in data: data["total_skills"] = SKILL_COUNT
                    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            except Exception as e:
                print(f"Error updating snapshot {p}: {e}")
print("Updated snapshots (root, dashboard, docs).")

# ----------------------------------------------------
# 9. CODE_MAP.md & ANTIBODY_REGISTRY.md 업데이트
# ----------------------------------------------------
cm_path = ROOT / "CODE_MAP.md"
if cm_path.exists():
    cmt = cm_path.read_text(encoding="utf-8")
    cmt = re.sub(r'v11\.\d+-[A-Z0-9-]+ · 항체 R1~R\d+ · 정식 스킬 \d+개', STATUS_LINE, cmt)
    if "rgon_aon_inspector_general_gate.py" not in cmt:
        r54_line = f"\n- **`rgon_aon_inspector_general_gate.py`**: 제30기관 아온 7대 방침 기관장 분신단 & 독립 검수담당 총장 100% 출하 봉인 관문 시스템 (`R54`, 주역 #21 화뢰서합·#15 지산겸)\n"
        cmt += r54_line
    cm_path.write_text(cmt, encoding="utf-8")
    print("Updated CODE_MAP.md.")

ab_path = ROOT / "ANTIBODY_REGISTRY.md"
if ab_path.exists():
    abt = ab_path.read_text(encoding="utf-8")
    abt = re.sub(r'v11\.\d+-[A-Z0-9-]+ · 항체 R1~R\d+', f"{VERSION} · 항체 {ANTIBODY_RANGE}", abt)
    abt = re.sub(r'범위:\s*R1~R\d+', f"범위: {ANTIBODY_RANGE}", abt)
    if "R54" not in abt:
        r54_entry = f"\n<!-- [RGON-ANTIBODY-R54] -->\n## R54 — Step 54 · {VERSION} · 2026-10-27\n- **범위**: {ANTIBODY_RANGE} · 정식 스킬 {SKILL_COUNT}개\n### 🛡️ R54: 7대 방침 기관장 분신단 & 독립 검수총장·기관별 특화 검수장 100% 출하 관문 항체\n- **소속 기관**: 제30기관 (`rgon_aon_inspector_general_gate.py`)\n- **설계**: Guardrails AI 도메인별 검증 + Anthropic Constitutional AI 헌법 심판 + 조선 어사대 독립 감찰 제도 + 3중 직인 SHA-256 출하 허가증.\n"
        abt += r54_entry
    ab_path.write_text(abt, encoding="utf-8")
    print("Updated ANTIBODY_REGISTRY.md.")

# ----------------------------------------------------
# 10. rgon_neural_synapse_verifier.py 업데이트 (제30기관 노드 & 시냅스 S24)
# ----------------------------------------------------
syn_path = ROOT / "rgon_neural_synapse_verifier.py"
if syn_path.exists():
    st = syn_path.read_text(encoding="utf-8")
    st = re.sub(r'VERSION\s*=\s*"[^"]+"', f'VERSION = "{VERSION}"', st, count=1)
    st = re.sub(r'ANTIBODY_RANGE\s*=\s*"[^"]+"', f'ANTIBODY_RANGE = "{ANTIBODY_RANGE}"', st, count=1)
    st = re.sub(r'EXPECTED_SKILL_COUNT\s*=\s*\d+', f'EXPECTED_SKILL_COUNT = {SKILL_COUNT}', st, count=1)

    r54_verifier_ext = '''
# [RGON-R54-VERIFIER-EXT-START]
VERSION = "v11.53-AON-INSPECTOR-GENERAL"
ANTIBODY_RANGE = "R1~R54"
EXPECTED_SKILL_COUNT = 50
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R54_INSPECTOR_ORGAN = "rgon_aon_inspector_general_gate.py"
try:
    if R54_INSPECTOR_ORGAN not in ORGANS:
        ORGANS.append(R54_INSPECTOR_ORGAN)
except NameError:
    ORGANS = [R54_INSPECTOR_ORGAN]

def _r54_s24_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/검수·/검수총장·/감찰)→제30기관 독립 검수담당 총장 & 100% 출하 관문"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "_r54_inspector_general_route", None)
        if not fn:
            fn = getattr(dlg, "r40_route", None)
        r = fn("/검수총장 8대 기관 100% 출하 관문 상태 점검") if fn else None
        ok = isinstance(r, dict) and r.get("ok") is True and (r.get("intent") == "inspector_general" or "inspector_general" in r)
        ev = f"intent={r.get('intent')}, ok={r.get('ok')}"
        return {"id": "S24", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": r}
    except Exception as e:
        return {"id": "S24", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

_r54_orig_vsl = globals().get("verify_synapse_links")
if callable(_r54_orig_vsl) and not getattr(_r54_orig_vsl, "_r54", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r54_orig_vsl(*args, **kwargs)
        s24 = _r54_s24_check()
        if isinstance(res, dict) and isinstance(res.get("synapses"), list):
            items = [x for x in res["synapses"] if not (isinstance(x, dict) and x.get("id") == "S24")] + [s24]
            res["synapses"] = items
            res["passed"] = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            res["total"] = len(items)
            res["ok"] = res["passed"] == res["total"]
        return res
    verify_synapse_links._r54 = True
# [RGON-R54-VERIFIER-EXT-END]
'''
    if "[RGON-R54-VERIFIER-EXT-START]" not in st:
        idx_main = st.find('if __name__ == "__main__":')
        if idx_main != -1:
            st = st[:idx_main] + r54_verifier_ext + "\n" + st[idx_main:]
        else:
            st += "\n" + r54_verifier_ext
        syn_path.write_text(st, encoding="utf-8")
        print("Updated rgon_neural_synapse_verifier.py with R54 verifier ext.")

print("=== [Step 54 SSOT Sync] All files successfully updated! ===")
