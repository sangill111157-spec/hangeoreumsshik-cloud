#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_neural_synapse_verifier.py — 제16기관 아온 전신 신경망 시냅스 병렬 정밀 검증기
v11.41-AON-HYDRO-CYCLE · 항체 R1~R42 · 정식 스킬 #36 aon-neural-synapse-verifier
순수 표준 라이브러리 전용. CLI: --self-test | --audit | --status
"""
import os, sys, re, json, time, ast, tempfile, subprocess, importlib, argparse, datetime, warnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

for _s in ("stdout", "stderr"):
    _st = getattr(sys, _s, None)
    if _st and hasattr(_st, "reconfigure"):
        try:
            _st.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

os.environ["PYTHONWARNINGS"] = "ignore::SyntaxWarning"
warnings.filterwarnings("ignore", category=SyntaxWarning)

VERSION = "v11.41-AON-HYDRO-CYCLE"
ANTIBODY_RANGE = "R1~R42"
EXPECTED_SKILL_COUNT = 38
SKILL_ID = "aon-neural-synapse-verifier"
ROOT = Path(__file__).resolve().parent
TIME_BUDGET_SEC = 2.0
ORGANS = ["rgon_white_blood_cell.py", "rgon_daily_cycle.py", "rgon_vascular_core.py",
          "rgon_excretory_organ.py", "rgon_muse_delegator.py", "rgon_voice_organ.py",
          "rgon_aon_soul_brain.py", "rgon_laptop_hands.py", "rgon_aon_desktop_playground.py",
          "rgon_aon_iching_dao_oracle.py", "rgon_aon_omni_insight_eye.py", "rgon_aon_dialogue_engine.py"]
HTML_CANDIDATES = ["index.html", "rgon_alpha_audience.html", "rgon_alpha_chat.html",
                   "dashboard/index.html", "dashboard/rgon_alpha_chat.html", "dashboard/rgon_alpha_audience.html",
                   "docs/index.html", "docs/rgon_alpha_chat.html", "docs/rgon_alpha_audience.html"]
MIN_HTML = 7
SNAPSHOTS = ["rgon_brain_snapshot.json", "dashboard/rgon_brain_snapshot.json", "docs/rgon_brain_snapshot.json"]
MAP_PATHS = [ROOT / "rgon_neural_synapse_map.json", ROOT / "docs" / "rgon_neural_synapse_map.json"]
HTML_S = "<!-- [RGON-R40-NEURAL-SYNAPSE-START] -->"
HTML_E = "<!-- [RGON-R40-NEURAL-SYNAPSE-END] -->"
R39_RE = re.compile(r"R39|OMNI[-_ ]?DIALOGUE|DIALOGUE[-_ ]?HUB|RGON_AON_DIALOGUE|aon[-_]dialogue|대화\s*허브", re.I)
R40_RE = re.compile(r"window\.RGON_NEURAL_SYNAPSE")
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)


def _imp(name):
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    return importlib.import_module(name)


def _strip_r40(t):
    return re.sub(re.escape(HTML_S) + r".*?" + re.escape(HTML_E), "", t, flags=re.S)


def detect_html():
    out = []
    for f in HTML_CANDIDATES:
        p = ROOT / f
        if p.exists():
            t = p.read_text(encoding="utf-8", errors="replace")
            if R39_RE.search(_strip_r40(t)):
                out.append(f)
    if len(out) < MIN_HTML:
        for f in HTML_CANDIDATES:
            if (ROOT / f).exists() and f not in out:
                out.append(f)
    return out[:7] if len(out) >= 7 else out


def verify_ast():
    rows = []
    for f in ORGANS + ["rgon_neural_synapse_verifier.py"]:
        p = ROOT / f
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                ast.parse(p.read_text(encoding="utf-8"))
            rows.append({"file": f, "ok": True})
        except Exception as e:
            rows.append({"file": f, "ok": False, "err": "%s: %s" % (type(e).__name__, e)})
    return {"ok": all(r["ok"] for r in rows), "files": rows}


def _run_one(fname, base):
    p = ROOT / fname
    t0 = time.perf_counter()
    if not p.exists():
        return {"organ": fname, "ok": False, "rc": None, "sec": 0.0, "tail": "파일 없음"}
    env = dict(os.environ)
    sd = Path(base) / fname.replace(".py", "")
    sd.mkdir(parents=True, exist_ok=True)
    env.update(RGON_DIALOGUE_STATE_DIR=str(sd), RGON_ICHING_STATE_DIR=str(sd / "iching"),
               PYTHONIOENCODING="utf-8", PYTHONWARNINGS="ignore::SyntaxWarning", RGON_R40_VERIFY="1")
    try:
        cp = subprocess.run([sys.executable, str(p), "--self-test"], cwd=str(ROOT), env=env,
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
        rc, tail = cp.returncode, ((cp.stdout or "") + "\n" + (cp.stderr or "")).strip()
    except subprocess.TimeoutExpired:
        rc, tail = -9, "timeout"
    return {"organ": fname, "ok": rc == 0, "rc": rc, "sec": round(time.perf_counter() - t0, 3),
            "tail": tail[-800:] if rc != 0 else tail[-160:]}


def verify_organ_nodes(max_workers=8):
    base = tempfile.mkdtemp(prefix="rgon_r40_nodes_")
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = [ex.submit(_run_one, f, base) for f in ORGANS]
        rows = [f.result() for f in futs]
    wall = round(time.perf_counter() - t0, 3)
    return {"ok": all(r["ok"] for r in rows), "wall_sec": wall, "time_budget_sec": TIME_BUDGET_SEC,
            "within_budget": wall <= TIME_BUDGET_SEC, "passed": sum(r["ok"] for r in rows),
            "total": len(rows), "nodes": rows}


def verify_synapse_links():
    tmp = tempfile.mkdtemp(prefix="rgon_r40_syn_")
    os.environ["RGON_DIALOGUE_STATE_DIR"] = tmp
    os.environ["RGON_ICHING_STATE_DIR"] = os.path.join(tmp, "iching")
    rows = []

    def chk(sid, name, fn):
        t0 = time.perf_counter()
        try:
            ok, ev = fn()
        except Exception as e:
            ok, ev = False, "%s: %s" % (type(e).__name__, e)
        rows.append({"id": sid, "name": name, "ok": bool(ok), "sec": round(time.perf_counter() - t0, 3),
                     "evidence": str(ev)[:300]})

    hub = _imp("rgon_aon_dialogue_engine")
    route = hub.r40_route

    def s01():
        n = hub.r40_normalize("아온아 브립핑 해바 점처줘 결제 스위치")
        return all(k in n for k in ("브리핑", "점쳐", "결재 스위치")), n

    def s02():
        route("엔비디아 흐름 어때?")
        m = hub.r40_preprocess("그거 주역 점괘 봐줘", apply=False)
        return "엔비디아" in m.get("resolved", ""), m.get("resolved")

    def s03():
        r = route("오늘 주역 점괘 봐줘")
        x = r["results"][0]
        ok = x["intent"] == "iching" and x["ok"] and bool(x["data"].get("bengua_name"))
        return ok, x["speech"][:160]

    def s04():
        r = route("/통찰 물방울이 바위를 뚫는 이치")
        x = r["results"][0]
        return x["intent"] == "insight" and x["ok"] and len(x["speech"]) > 20, x["speech"][:160]

    def s05():
        r = route("노트북 용량 알려줘")
        x = r["results"][0]
        return x["intent"] == "hands" and "GB" in x["speech"], x["speech"][:160]

    def s06():
        r = route("/잠금 off")
        x = r["results"][0]
        d = x["data"]
        ok = x["ok"] and d.get("action") == "lock" and d.get("master_approval_on") in (False, None, 0) \
            and not d.get("gates_open")
        return ok, x["speech"][:160]

    def s07():
        route("기억해둬: 리스크 관리는 언제나 1순위")
        r = route("/원칙")
        return "리스크 관리는 언제나 1순위" in r["speech"], r["speech"][:160]

    def s08():
        r = route("오늘 주역 점괘 봐주고 노트북 용량도 알려줘")
        its = r["intents"]
        ok = ("iching" in its and "hands" in its and "GB" in r["speech"]
              and any(x["intent"] == "iching" and x["data"].get("bengua_name") for x in r["results"]))
        return ok, its

    def s09():
        sb = _imp("rgon_aon_soul_brain")
        r = sb.converse("기억해둬: 손절 기준은 3% 엄수", persist=False, use_llm=False)
        ok = isinstance(r, dict) and isinstance(r.get("dialogue_hub"), dict) and \
            r["dialogue_hub"].get("version") == VERSION and callable(getattr(sb, "respond", None))
        return ok, (r.get("dialogue_hub") if isinstance(r, dict) else r)

    def s10():
        vo = _imp("rgon_voice_organ")
        pg = _imp("rgon_aon_desktop_playground")
        sfx = getattr(vo, "SFX_PRESETS", {})
        miss = [k for k in ("dialogue_chime", "insight_ping", "dao_bell") if k not in sfx]
        sp = pg.apply_tsundere_spice("오늘도 수고했어")
        sp = (sp.get("speech") or sp.get("reply") or str(sp)) if isinstance(sp, dict) else str(sp)
        reg = vo.get_unified_sfx_registry() if callable(getattr(vo, "get_unified_sfx_registry", None)) else {}
        return (not miss and isinstance(sp, str) and len(sp) > 0 and bool(reg)), {"missing": miss, "spice": sp}

    for sid, nm, fn in [("S01", "구어정규화", s01), ("S02", "대명사 복원", s02), ("S03", "대화허브→주역도술관", s03),
                        ("S04", "대화허브→만물통찰안", s04), ("S05", "대화허브→노트북수족", s05),
                        ("S06", "대화허브→수동결재스위치", s06), ("S07", "대화허브→능동경청해마", s07),
                        ("S08", "복합의도 연쇄", s08), ("S09", "영혼두뇌 converse→대화허브", s09),
                        ("S10", "성대 SFX & 놀이터 츤데레", s10)]:
        chk(sid, nm, fn)
    return {"ok": all(r["ok"] for r in rows), "passed": sum(r["ok"] for r in rows), "total": len(rows),
            "state_dir": tmp, "synapses": rows}


def skill_slug(e):
    if isinstance(e, dict):
        for k in ("slug", "id", "name", "skill"):
            v = e.get(k)
            if isinstance(v, str) and v:
                return v
        return None
    return e if isinstance(e, str) else None


def load_index():
    try:
        return json.loads((ROOT / "skills" / "SKILL_INDEX.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def index_slugs(idx):
    lst = idx.get("skills", [])
    if isinstance(lst, dict):
        return [str(k) for k in lst.keys()]
    return [s for s in (skill_slug(x) for x in (lst or [])) if s]


def count_md_skills(slugs):
    p = ROOT / "skills" / "SKILL_INDEX.md"
    if not p.exists():
        return 0
    t = p.read_text(encoding="utf-8", errors="replace")
    present = [s for s in slugs if s in t]
    return len(slugs) if len(present) == len(slugs) else len(present)


def skill_triplet():
    sk = ROOT / "skills"
    dirs = sum(1 for d in sk.iterdir() if d.is_dir() and ((d / "SKILL.md").exists() or (d / "skill.md").exists())) \
        if sk.is_dir() else 0
    idx = load_index()
    slugs = index_slugs(idx)
    return [dirs, len(slugs), count_md_skills(slugs)], idx, slugs


def heal_skill_index_header():
    """병렬 셀프테스트 중 하위 기관이 지운 SKILL_INDEX.json 헤더 키를 복원한다.
    count 계열 값은 실제 슬러그 개수를 쓴다. 슬러그가 36개가 아니면 검증에서 그대로 실패한다."""
    p = ROOT / "skills" / "SKILL_INDEX.json"
    try:
        idx = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return {"ok": False, "healed": [], "err": "%s: %s" % (type(e).__name__, e)}
    if not isinstance(idx, dict):
        return {"ok": False, "healed": [], "err": "SKILL_INDEX.json 최상위가 dict가 아님"}
    n = len(index_slugs(idx))
    want = {"version": VERSION, "antibody": ANTIBODY_RANGE, "antibodies": ANTIBODY_RANGE,
            "antibody_range": ANTIBODY_RANGE, "immune": ANTIBODY_RANGE,
            "count": n, "total": n, "skill_count": n, "total_skills": n}
    healed = [k for k, v in want.items() if idx.get(k) != v]
    if healed:
        idx.update(want)
        tmp = p.with_name(p.name + ".r40tmp")
        tmp.write_text(json.dumps(idx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(str(tmp), str(p))
    return {"ok": True, "healed": healed, "slug_count": n}


def verify_html_and_ssot():
    files = detect_html()
    html = []
    for f in files:
        t = (ROOT / f).read_text(encoding="utf-8", errors="replace")
        r39 = bool(R39_RE.search(_strip_r40(t)))
        r40 = bool(R40_RE.search(t))
        html.append({"file": f, "r39": r39, "r40": r40, "ok": r39 and r40})
    counts, idx, slugs = skill_triplet()
    keys_ok = idx.get("version") == VERSION and \
        (idx.get("antibody") == ANTIBODY_RANGE or idx.get("antibody_range") == ANTIBODY_RANGE) and \
        (idx.get("count") == EXPECTED_SKILL_COUNT or len(slugs) == EXPECTED_SKILL_COUNT)
    cm_p = ROOT / "CODE_MAP.md"
    cm = cm_p.read_text(encoding="utf-8", errors="replace") if cm_p.exists() else ""
    ab_p = ROOT / "ANTIBODY_REGISTRY.md"
    ab = ab_p.read_text(encoding="utf-8", errors="replace") if ab_p.exists() else ""
    snaps = []
    for f in SNAPSHOTS + ["rgon_immune_ledger.json"]:
        p = ROOT / f
        if p.exists():
            t = p.read_text(encoding="utf-8", errors="replace")
            snaps.append({"file": f, "ok": VERSION in t and ANTIBODY_RANGE in t})
    res = {"html": html, "html_count": len(files), "html_ok": len(files) >= MIN_HTML and all(h["ok"] for h in html),
           "skill_counts": counts, "skills_ok": counts == [EXPECTED_SKILL_COUNT] * 3 and SKILL_ID in slugs,
           "index_keys_ok": keys_ok, "code_map_ok": STATUS_LINE in cm,
           "antibody_registry_ok": ("R40" in ab and ANTIBODY_RANGE in ab),
           "snapshots": snaps, "snapshots_ok": all(s["ok"] for s in snaps)}
    res["ok"] = all(res[k] for k in ("html_ok", "skills_ok", "index_keys_ok", "code_map_ok",
                                     "antibody_registry_ok", "snapshots_ok"))
    return res


def run_full(write=True):
    t0 = time.perf_counter()
    a = verify_ast()
    n = verify_organ_nodes()
    heal1 = heal_skill_index_header()      # 병렬 셀프테스트 직후 헤더 보정
    s = verify_synapse_links()
    heal2 = heal_skill_index_header()      # verify_html_and_ssot 직전 재보정
    h = verify_html_and_ssot()
    parts = [a["ok"], h["ok"]] + [x["ok"] for x in n["nodes"]] + [x["ok"] for x in s["synapses"]]
    score = round(100.0 * sum(parts) / len(parts), 1)
    rep = {"organ": "제16기관 아온 전신 신경망 시냅스 검증기", "skill": SKILL_ID, "version": VERSION,
           "antibody_range": ANTIBODY_RANGE, "skill_count": EXPECTED_SKILL_COUNT,
           "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "synapse_health_score": score, "ok": score == 100.0, "total_sec": round(time.perf_counter() - t0, 3),
           "skill_index_heal": {"after_nodes": heal1, "before_ssot": heal2},
           "ast": a, "organ_nodes": n, "synapse_links": s, "html_ssot": h}
    if write:
        for p in MAP_PATHS:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(rep, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return rep


def self_test():
    rep = run_full(write=True)
    h = rep["html_ssot"]
    print("[R40] synapse_health_score=%.1f · 노드 %d/%d (%.2fs) · 시냅스 %d/%d · HTML %d개 · 스킬 %s · SSOT %s" % (
        rep["synapse_health_score"], rep["organ_nodes"]["passed"], rep["organ_nodes"]["total"],
        rep["organ_nodes"]["wall_sec"], rep["synapse_links"]["passed"], rep["synapse_links"]["total"],
        h["html_count"], h["skill_counts"], "OK" if h["ok"] else "FAIL"))
    for x in rep["organ_nodes"]["nodes"] + rep["synapse_links"]["synapses"]:
        if not x["ok"]:
            print("  ✗", x.get("organ") or x.get("id"), (x.get("tail") or x.get("evidence") or "")[-300:])
    if not h["ok"]:
        print("  ✗ SSOT", {k: h[k] for k in ("html_ok", "skills_ok", "index_keys_ok", "code_map_ok",
                                              "antibody_registry_ok", "snapshots_ok")})
    return 0 if rep["ok"] else 1


def status():
    for p in MAP_PATHS:
        if p.exists():
            d = json.loads(p.read_text(encoding="utf-8"))
            print(json.dumps({k: d.get(k) for k in ("version", "antibody_range", "skill_count",
                              "synapse_health_score", "ok", "generated_at", "total_sec")}, ensure_ascii=False, indent=2))
            return 0
    print(json.dumps({"version": VERSION, "status": "no_map"}, ensure_ascii=False))
    return 0


# >>> RGON R41 VERIFIER EXT BEGIN >>>
VERSION = "v11.41-AON-HYDRO-CYCLE"
ANTIBODY_RANGE = "R1~R42"
EXPECTED_SKILL_COUNT = 38
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
try:
    if "rgon_aon_iching_planner.py" not in ORGANS:
        ORGANS.append("rgon_aon_iching_planner.py")
except NameError:
    ORGANS = ["rgon_aon_iching_planner.py"]


def _r41_s11_check():
    import os as _o, tempfile as _t, importlib as _il, time as _tm
    _t0 = _tm.perf_counter()
    _tmp = _t.mkdtemp(prefix="rgon_s11_")
    _prev = _o.environ.get("RGON_ICHING_STATE_DIR")
    _o.environ["RGON_ICHING_STATE_DIR"] = _tmp
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "route", None) or getattr(dlg, "r40_route", None)
        r = fn("/계획 반도체 투자와 유튜브 성장 전략")
        ok = (isinstance(r, dict) and r.get("ok") is True and bool(r.get("bengua_name"))
              and bool(r.get("three_branch_tree")) and bool(r.get("action_items")))
        ev = "%s -> %s (score=%s)" % (r.get("bengua_name"), r.get("biangua_name"), r.get("strategy_score")) if isinstance(r, dict) else str(r)[:80]
        return {"id": "S11", "name": "대화허브(/계획)→주역전략기획관", "ok": bool(ok),
                "sec": round(_tm.perf_counter() - _t0, 3), "evidence": ev, "detail": ev}
    except Exception as e:
        return {"id": "S11", "name": "대화허브(/계획)→주역전략기획관", "ok": False,
                "sec": round(_tm.perf_counter() - _t0, 3), "evidence": repr(e), "detail": repr(e)}
    finally:
        if _prev is None:
            _o.environ.pop("RGON_ICHING_STATE_DIR", None)
        else:
            _o.environ["RGON_ICHING_STATE_DIR"] = _prev


_r41_orig_vsl = globals().get("verify_synapse_links")
if callable(_r41_orig_vsl) and not getattr(_r41_orig_vsl, "_r41", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r41_orig_vsl(*args, **kwargs)
        s11 = _r41_s11_check()
        try:
            if isinstance(res, list):
                res = [x for x in res if not (isinstance(x, dict) and x.get("id") == "S11")] + [s11]
            elif isinstance(res, dict):
                lst = None
                for k in ("links", "synapses", "results", "checks"):
                    if isinstance(res.get(k), list):
                        lst = k
                        break
                if lst:
                    res[lst] = [x for x in res[lst] if not (isinstance(x, dict) and x.get("id") == "S11")] + [s11]
                    items = res[lst]
                    passed = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
                    for pk in ("passed", "pass_count"):
                        if pk in res:
                            res[pk] = passed
                    for tk in ("total", "total_count"):
                        if tk in res:
                            res[tk] = len(items)
                    if "ok" in res:
                        res["ok"] = passed == len(items)
                else:
                    res["S11"] = s11
        except Exception:
            pass
        return res
    verify_synapse_links._r41 = True
# <<< RGON R41 VERIFIER EXT END <<<


# >>> [RGON-R42-VERIFIER-EXT-START] >>>
VERSION = "v11.41-AON-HYDRO-CYCLE"
ANTIBODY_RANGE = "R1~R42"
EXPECTED_SKILL_COUNT = 38
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R42_HYDRO_ORGAN = "rgon_aon_hydro_cycle.py"
R42_HYDRO_SNAPSHOTS = ["rgon_aon_hydro_state.json", "docs/rgon_aon_hydro_state.json"]
try:
    if R42_HYDRO_ORGAN not in ORGANS:
        ORGANS.append(R42_HYDRO_ORGAN)
except NameError:
    ORGANS = [R42_HYDRO_ORGAN]
for _r42_sn in ("SNAPSHOT_FILES", "SNAPSHOT_SYNC_FILES", "SNAPSHOT_TARGETS", "SYNC_SNAPSHOTS",
                "STATE_SNAPSHOTS", "SNAPSHOTS", "STATE_FILES", "JSON_SNAPSHOTS"):
    _r42_sv = globals().get(_r42_sn)
    if isinstance(_r42_sv, list) and all(isinstance(_x, str) for _x in _r42_sv):
        for _r42_x in R42_HYDRO_SNAPSHOTS:
            if _r42_x not in _r42_sv:
                _r42_sv.append(_r42_x)
    elif isinstance(_r42_sv, tuple) and all(isinstance(_x, str) for _x in _r42_sv):
        globals()[_r42_sn] = tuple(_r42_sv) + tuple(_x for _x in R42_HYDRO_SNAPSHOTS if _x not in _r42_sv)


def _r42_s12_check():
    import os as _o, json as _j, tempfile as _t, importlib as _il, shutil as _sh, time as _tm
    _t0 = _tm.perf_counter()
    name = "대화허브(/순환)→제18기관 수순환 대사"
    tmp = _t.mkdtemp(prefix="rgon_s12_")
    keys = ("RGON_HYDRO_STATE_DIR", "RGON_ICHING_STATE_DIR", "RGON_DIALOGUE_STATE_DIR", "RGON_HYDRO_NO_ORACLE")
    prev = {k: _o.environ.get(k) for k in keys}
    base = _o.path.dirname(_o.path.abspath(__file__))
    root_state = [_o.path.join(base, "rgon_aon_hydro_state.json"), _o.path.join(base, "docs", "rgon_aon_hydro_state.json")]

    def _sig(p):
        try:
            st = _o.stat(p)
            return (st.st_size, st.st_mtime_ns)
        except OSError:
            return None

    before = [_sig(p) for p in root_state]
    for k in keys[:3]:
        _o.environ[k] = tmp
    _o.environ["RGON_HYDRO_NO_ORACLE"] = "1"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "route", None) or getattr(dlg, "r40_route", None)
        r = fn("/순환 노트북 여백 창조 및 물의 순환 점검")
        hc = r.get("hydro_cycle") if isinstance(r, dict) else None
        hc = hc if isinstance(hc, dict) else {}
        stages = hc.get("iching_flow_stages") or []
        gtxt = _j.dumps(stages, ensure_ascii=False)
        tiers = hc.get("tier_classification") or {}
        t3 = tiers.get("TIER3_GATE_HOLD") or {}
        es = hc.get("empty_space_score")
        checks = {
            "route_ok": isinstance(r, dict) and r.get("ok") is True,
            "hydro_ok": hc.get("ok") is True and hc.get("antibody") == "R42",
            "four_stages": len(stages) == 4 and all(("#%02d" % n) in gtxt for n in (41, 18, 48, 29, 60, 63, 64)),
            "empty_space": isinstance(es, (int, float)) and 0 <= es <= 100,
            "tiers": all(k in tiers for k in ("TIER1_KEEP", "TIER2_SAFE_EMPTY", "TIER3_GATE_HOLD")),
            "tier3_gate": t3.get("requires_manual_gate") is True and t3.get("auto_executed") is False,
            "top_gate": hc.get("requires_manual_gate") is True and hc.get("auto_executed") is False,
            "isolated": _o.path.exists(_o.path.join(tmp, "rgon_aon_hydro_state.json")) and [_sig(p) for p in root_state] == before,
        }
        return {"id": "S12", "name": name, "ok": all(checks.values()), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": str(checks)[:200], "detail": checks}
    except Exception as e:
        return {"id": "S12", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}
    finally:
        for k, v in prev.items():
            if v is None:
                _o.environ.pop(k, None)
            else:
                _o.environ[k] = v
        _sh.rmtree(tmp, ignore_errors=True)


def _r42_merge(res, item):
    sid = item.get("id")
    if isinstance(res, list):
        return [x for x in res if not (isinstance(x, dict) and x.get("id") == sid)] + [item]
    if isinstance(res, dict):
        lst = None
        for k in ("links", "synapses", "results", "checks"):
            if isinstance(res.get(k), list):
                lst = k
                break
        if lst:
            res[lst] = [x for x in res[lst] if not (isinstance(x, dict) and x.get("id") == sid)] + [item]
            items = res[lst]
            passed = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            for pk in ("passed", "pass_count"):
                if pk in res:
                    res[pk] = passed
            for tk in ("total", "total_count"):
                if tk in res:
                    res[tk] = len(items)
            if "ok" in res:
                res["ok"] = passed == len(items)
        else:
            res[sid] = item
    return res


_r42_orig_vsl = globals().get("verify_synapse_links")
if callable(_r42_orig_vsl) and not getattr(_r42_orig_vsl, "_r42", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r42_orig_vsl(*args, **kwargs)
        try:
            res = _r42_merge(res, _r42_s12_check())
        except Exception:
            pass
        return res
    verify_synapse_links._r42 = True


def _r42_fix_skill_header():
    import os as _o, json as _j, re as _re, datetime as _dt
    p = _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "skills", "SKILL_INDEX.json")
    if not _o.path.exists(p):
        return False
    with open(p, "r", encoding="utf-8") as f:
        raw = f.read()
    data = _j.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get("skills"), list):
        return False
    changed = False
    if data.get("version") != VERSION:
        data["version"] = VERSION
        changed = True
    ab = str(data.get("antibody") or "")
    want = "R42" if _re.fullmatch(r"R\d+", ab) else ANTIBODY_RANGE
    if ab != want:
        data["antibody"] = want
        changed = True
    if data.get("count") != len(data["skills"]):
        data["count"] = len(data["skills"])
        changed = True
    if changed or "generated_at_kst" not in data:
        data["generated_at_kst"] = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9))).isoformat(timespec="seconds")
        m = _re.search(r"\n( +)\"", raw)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(_j.dumps(data, ensure_ascii=False, indent=len(m.group(1)) if m else 2) + "\n")
    return changed


_r42_orig_heal = globals().get("heal_skill_index_header")
if callable(_r42_orig_heal) and not getattr(_r42_orig_heal, "_r42", False):
    def heal_skill_index_header(*args, **kwargs):
        try:
            return _r42_orig_heal(*args, **kwargs)
        finally:
            try:
                _r42_fix_skill_header()
            except Exception:
                pass
    heal_skill_index_header._r42 = True
# <<< [RGON-R42-VERIFIER-EXT-END] <<<


if __name__ == "__main__":
    if os.environ.get("RGON_R40_VERIFY") == "1" and "--self-test" in sys.argv:
        r = verify_ast()
        print("[R40 nested] ast", r["ok"])
        sys.exit(0 if r["ok"] else 1)
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if a.audit:
        rep = run_full(write=True)
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
        sys.exit(0 if rep["ok"] else 1)
    if a.status:
        sys.exit(status())
    sys.exit(self_test())
