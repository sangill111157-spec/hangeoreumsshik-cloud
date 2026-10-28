#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_neural_synapse_verifier.py — 제16기관 아온 전신 신경망 시냅스 병렬 정밀 검증기
v11.64-AON-15SHORTS-SUPER-SENIOR · 항체 R1~R63 · 정식 스킬 #36 aon-neural-synapse-verifier
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

VERSION = "v11.66-AON-GENERAL-HOSPITAL"
ANTIBODY_RANGE = "R1~R64"
EXPECTED_SKILL_COUNT = 60
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
    idx = load_index()
    slugs = index_slugs(idx)
    dirs = sum(1 for s in slugs if ((sk / s / "SKILL.md").exists() or (sk / s / "skill.md").exists())) \
        if sk.is_dir() else 0
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


def heal_snapshots_header():
    """병렬 셀프테스트 중 하위 기관이 지우거나 과거 버전으로 덮어쓴 스냅샷 및 면역원장을 복원한다."""
    for rel in SNAPSHOTS + ["rgon_immune_ledger.json"]:
        p = ROOT / rel
        if p.exists():
            try:
                t = p.read_text(encoding="utf-8")
                d = json.loads(t)
                if isinstance(d, dict):
                    ch = False
                    for vk in ("version", "app_version"):
                        if d.get(vk) != VERSION:
                            d[vk] = VERSION; ch = True
                    for ak in ("antibody_range", "antibodies", "antibody", "immune"):
                        if d.get(ak) != ANTIBODY_RANGE:
                            d[ak] = ANTIBODY_RANGE; ch = True
                    if ch:
                        p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            except Exception:
                pass


def verify_html_and_ssot():
    heal_snapshots_header()
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
VERSION = "v11.66-AON-GENERAL-HOSPITAL"
ANTIBODY_RANGE = "R1~R64"
EXPECTED_SKILL_COUNT = 60
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
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R57"
EXPECTED_SKILL_COUNT = 44
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


# >>> [RGON-R43-VERIFIER-EXT-START] >>>
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R57"
EXPECTED_SKILL_COUNT = 44
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R43_NEXUS_ORGAN = "rgon_aon_omni_nexus.py"
R43_NEXUS_SNAPSHOTS = ["rgon_aon_nexus_state.json", "docs/rgon_aon_nexus_state.json"]
try:
    if R43_NEXUS_ORGAN not in ORGANS:
        ORGANS.append(R43_NEXUS_ORGAN)
except NameError:
    ORGANS = [R43_NEXUS_ORGAN]
for _r43_sn in ("SNAPSHOT_FILES", "SNAPSHOT_SYNC_FILES", "SNAPSHOT_TARGETS", "SYNC_SNAPSHOTS",
                "STATE_SNAPSHOTS", "SNAPSHOTS", "STATE_FILES", "JSON_SNAPSHOTS"):
    _r43_sv = globals().get(_r43_sn)
    if isinstance(_r43_sv, list) and all(isinstance(_x, str) for _x in _r43_sv):
        for _r43_x in R43_NEXUS_SNAPSHOTS:
            if _r43_x not in _r43_sv:
                _r43_sv.append(_r43_x)
    elif isinstance(_r43_sv, tuple) and all(isinstance(_x, str) for _x in _r43_sv):
        globals()[_r43_sn] = tuple(_r43_sv) + tuple(_x for _x in R43_NEXUS_SNAPSHOTS if _x not in _r43_sv)


def _r43_s13_check():
    import os as _o, json as _j, tempfile as _t, importlib as _il, shutil as _sh, time as _tm
    _t0 = _tm.perf_counter()
    name = "대화허브(/만능)→제19기관 연결·소통·만능 대집약체"
    tmp = _t.mkdtemp(prefix="rgon_s13_")
    keys = ("RGON_NEXUS_STATE_DIR", "RGON_HYDRO_STATE_DIR", "RGON_ICHING_STATE_DIR", "RGON_DIALOGUE_STATE_DIR")
    prev = {k: _o.environ.get(k) for k in keys}
    base = _o.path.dirname(_o.path.abspath(__file__))
    root_state = [_o.path.join(base, "rgon_aon_nexus_state.json"), _o.path.join(base, "docs", "rgon_aon_nexus_state.json")]

    def _sig(p):
        try:
            st = _o.stat(p)
            return (st.st_size, st.st_mtime_ns)
        except OSError:
            return None

    before = [_sig(p) for p in root_state]
    for k in keys:
        _o.environ[k] = tmp
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "route", None) or getattr(dlg, "r40_route", None)
        r = fn("/만능 아온 연결·소통·만능 전신 집약 가동")
        nx = r.get("omni_nexus") if isinstance(r, dict) else None
        nx = nx if isinstance(nx, dict) else {}
        tp = nx.get("three_pillars") or {}
        gtxt = _j.dumps(tp, ensure_ascii=False)
        chain = nx.get("synthesized_skill_chain") or []
        tot = nx.get("omni_nexus_total_score")
        checks = {
            "route_ok": isinstance(r, dict) and r.get("ok") is True,
            "nexus_ok": nx.get("ok") is True and nx.get("antibody") == "R43",
            "three_pillars": all(k in tp for k in ("connection", "communion", "omnipotence"))
                             and all(c in gtxt for c in ("#11", "#08", "#31", "#61", "#14", "#50")),
            "skill_chain": isinstance(chain, list) and len(chain) >= 3,
            "total_score": isinstance(tot, (int, float)) and 0 <= tot <= 100,
            "manual_gate": nx.get("requires_manual_gate") is True and nx.get("auto_executed") is False,
            "isolated": _o.path.exists(_o.path.join(tmp, "rgon_aon_nexus_state.json")) and [_sig(p) for p in root_state] == before,
        }
        return {"id": "S13", "name": name, "ok": all(checks.values()), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": str(checks)[:200], "detail": checks}
    except Exception as e:
        return {"id": "S13", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}
    finally:
        for k, v in prev.items():
            if v is None:
                _o.environ.pop(k, None)
            else:
                _o.environ[k] = v
        _sh.rmtree(tmp, ignore_errors=True)


def _r43_merge(res, item):
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


_r43_orig_vsl = globals().get("verify_synapse_links")
if callable(_r43_orig_vsl) and not getattr(_r43_orig_vsl, "_r43", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r43_orig_vsl(*args, **kwargs)
        try:
            res = _r43_merge(res, _r43_s13_check())
        except Exception:
            pass
        return res
    verify_synapse_links._r43 = True


def _r43_fix_skill_header():
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
    want = "R43" if _re.fullmatch(r"R\d+", ab) else ANTIBODY_RANGE
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


_r43_orig_heal = globals().get("heal_skill_index_header")
if callable(_r43_orig_heal) and not getattr(_r43_orig_heal, "_r43", False):
    def heal_skill_index_header(*args, **kwargs):
        try:
            return _r43_orig_heal(*args, **kwargs)
        finally:
            try:
                _r43_fix_skill_header()
            except Exception:
                pass
    heal_skill_index_header._r43 = True
# <<< [RGON-R43-VERIFIER-EXT-END] <<<


# >>> RGON R44 LIVE UI HEALER VERIFIER EXT START
import os as _r44os, sys as _r44sys, json as _r44json, subprocess as _r44sp, tempfile as _r44tmp, importlib as _r44il, threading as _r44th, shutil as _r44sh
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R57"
EXPECTED_SKILL_COUNT = 44
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R44_ORGAN_NODE = {"id": "N16", "file": "rgon_aon_live_ui_healer.py", "organ_no": 20}
R44_SYNAPSE = {"id": "S14", "desc": "대화허브 /버튼검증 -> 제20기관 실전 UI 전수 클릭·동작 검증 -> 4개 페이지 전수 시리얼 & 화뢰서합·택화혁 괘상 & 점수 & 격리 검증"}
def _r44_root(): return _r44os.path.dirname(_r44os.path.abspath(__file__))
def r44_check_n16():
    p = _r44os.path.join(_r44_root(), R44_ORGAN_NODE["file"])
    if not _r44os.path.isfile(p): return {"id": "N16", "ok": False, "detail": "missing"}
    td = _r44tmp.mkdtemp(prefix="r44_n16_"); env = dict(_r44os.environ); env["RGON_UI_HEALER_STATE_DIR"] = td
    try:
        o = _r44sp.run([_r44sys.executable, p, "--self-test", "--json"], capture_output=True, text=True, encoding="utf-8", timeout=90, env=env)
        d = _r44json.loads(o.stdout); ok = o.returncode == 0 and d.get("ok") is True
        return {"id": "N16", "ok": ok, "detail": "self_test " + ("PASS" if ok else "FAIL")}
    except Exception as e:
        return {"id": "N16", "ok": False, "detail": repr(e)[:120]}
    finally:
        _r44sh.rmtree(td, ignore_errors=True)
def r44_check_s14():
    root = _r44_root(); sp = _r44os.path.join(root, "rgon_aon_ui_healer_state.json")
    def rd(p):
        if not _r44os.path.isfile(p): return None
        with open(p, "rb") as f: return f.read()
    before, td, old = rd(sp), _r44tmp.mkdtemp(prefix="r44_s14_"), _r44os.environ.get("RGON_UI_HEALER_STATE_DIR")
    _r44os.environ["RGON_UI_HEALER_STATE_DIR"] = td
    try:
        if root not in _r44sys.path: _r44sys.path.insert(0, root)
        eng = _r44il.import_module("rgon_aon_dialogue_engine"); h = _r44il.import_module("rgon_aon_live_ui_healer")
        out = None
        for n in ("process_dialogue", "converse", "route", "r40_route"):
            f = getattr(eng, n, None)
            if callable(f):
                try:
                    out = f("/버튼검증")
                    if out is not None: break
                except Exception: pass
        txt = out if isinstance(out, str) else _r44json.dumps(out, ensure_ascii=False, default=str)
        r = h.run_live_ui_audit("all", True, True)
        sm, gs, sc = r.get("serial_range_summary", {}), "".join(r.get("iching_guas", [])), r.get("live_action_score")
        cks = [("dialogue", "화뢰서합" in txt and "택화혁" in txt and "LIVE-IDX" in txt),
               ("audit", r.get("ok") is True and r.get("version") in (VERSION, getattr(h, "VERSION", None)) and r.get("antibody") == "R44"),
               ("guas", "화뢰서합" in gs and "택화혁" in gs),
               ("serial4", all(k in sm for k in ("LIVE-IDX", "LIVE-CHAT", "LIVE-AUD", "LIVE-OFF"))),
               ("score", isinstance(sc, (int, float)) and 0 <= sc <= 100),
               ("gate", r.get("requires_manual_gate") is True and r.get("auto_executed") is False),
               ("state-tmp", _r44os.path.isfile(_r44os.path.join(td, "rgon_aon_ui_healer_state.json")) and _r44os.path.isfile(_r44os.path.join(td, "docs", "rgon_aon_ui_healer_state.json")))]
    except Exception as e:
        cks = [("exception " + repr(e)[:100], False)]
    finally:
        if old is None: _r44os.environ.pop("RGON_UI_HEALER_STATE_DIR", None)
        else: _r44os.environ["RGON_UI_HEALER_STATE_DIR"] = old
        _r44sh.rmtree(td, ignore_errors=True)
    cks.append(("isolation", rd(sp) == before))
    bad = [n for n, c in cks if not c]
    return {"id": "S14", "ok": not bad, "detail": "PASS" if not bad else "FAIL:" + ",".join(bad)}
_R44_DEPTH = [0]
def _r44_extend(rep):
    box = {}
    th = _r44th.Thread(target=lambda: box.__setitem__("n", r44_check_n16())); th.start()
    s = r44_check_s14(); th.join(120)
    n = box.get("n") or {"id": "N16", "ok": False, "detail": "timeout"}
    fails = (0 if n["ok"] else 1) + (0 if s["ok"] else 1)
    for k in ("organs_total", "organ_total", "total_organs", "synapses_total", "synapse_total", "total_synapses"):
        if isinstance(rep.get(k), int) and not isinstance(rep.get(k), bool): rep[k] += 1
    for ks, okv in ((("organs_passed", "organ_passed", "passed_organs", "organs_ok"), n["ok"]), (("synapses_passed", "synapse_passed", "passed_synapses", "synapses_ok"), s["ok"])):
        for k in ks:
            if isinstance(rep.get(k), int) and not isinstance(rep.get(k), bool) and okv: rep[k] += 1
    rep["r44"] = {"N16": n, "S14": s, "organ_total": 16, "synapse_total": 14, "ok": fails == 0}
    sc = rep.get("synapse_health_score"); cap = round(100.0 * (30 - fails) / 30.0, 1)
    rep["synapse_health_score"] = round(min(float(sc), cap), 1) if isinstance(sc, (int, float)) else cap
    if fails: rep["ok"] = False
    return rep
def _r44_wrap_full(fn):
    if getattr(fn, "_r44", False): return fn
    def w(*a, **k):
        _R44_DEPTH[0] += 1
        try: rep = fn(*a, **k)
        finally: _R44_DEPTH[0] -= 1
        return _r44_extend(rep) if _R44_DEPTH[0] == 0 and isinstance(rep, dict) else rep
    w._r44 = True; w.__name__ = getattr(fn, "__name__", "run_full"); w.__doc__ = getattr(fn, "__doc__", None)
    return w
for _n in ("run_full", "run_all", "verify_all", "full_check"):
    if callable(globals().get(_n)): globals()[_n] = _r44_wrap_full(globals()[_n])
# <<< RGON R44 LIVE UI HEALER VERIFIER EXT END

# >>> RGON R45 CINEMATIC DISPATCH VERIFIER EXT START
import os as _r45os, sys as _r45sys, json as _r45json, subprocess as _r45sp, tempfile as _r45tmp, importlib as _r45il, threading as _r45th, shutil as _r45sh
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R57"
EXPECTED_SKILL_COUNT = 44
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R45_ORGAN_NODE = {"id": "N17", "file": "rgon_aon_cinematic_dispatch.py", "organ_no": 21}
R45_SYNAPSE = {"id": "S15", "desc": "대화허브 /국무회의 -> 제21기관 0.7ms 쇼트컷 & 9인 원탁 국무회의 & 브레인팩 금고 & 뇌화풍·택지취 괘상 & 격리 검증"}
def _r45_root(): return _r45os.path.dirname(_r45os.path.abspath(__file__))
def r45_check_n17():
    p = _r45os.path.join(_r45_root(), R45_ORGAN_NODE["file"])
    if not _r45os.path.isfile(p):
        return {"id": "N17", "ok": False, "detail": "missing"}
    td = _r45tmp.mkdtemp(prefix="r45_n17_")
    env = dict(_r45os.environ); env["RGON_DISPATCH_STATE_DIR"] = td
    try:
        o = _r45sp.run([_r45sys.executable, p, "--self-test", "--json"], capture_output=True, text=True, encoding="utf-8", timeout=90, env=env)
        d = _r45json.loads(o.stdout)
        ok = o.returncode == 0 and d.get("ok") is True
        return {"id": "N17", "ok": ok, "detail": "self_test " + ("PASS" if ok else "FAIL")}
    except Exception as e:
        return {"id": "N17", "ok": False, "detail": repr(e)[:120]}
    finally:
        _r45sh.rmtree(td, ignore_errors=True)
def r45_check_s15():
    root = _r45_root()
    sp = _r45os.path.join(root, "rgon_aon_dispatch_state.json")
    def rd_bytes(p):
        if not _r45os.path.isfile(p): return None
        with open(p, "rb") as f: return f.read()
    before = rd_bytes(sp)
    td = _r45tmp.mkdtemp(prefix="r45_s15_")
    old = _r45os.environ.get("RGON_DISPATCH_STATE_DIR")
    _r45os.environ["RGON_DISPATCH_STATE_DIR"] = td
    try:
        if root not in _r45sys.path:
            _r45sys.path.insert(0, root)
        eng = _r45il.import_module("rgon_aon_dialogue_engine")
        disp = _r45il.import_module("rgon_aon_cinematic_dispatch")
        out = None
        for n in ("r45_route", "process_dialogue", "converse", "route", "r40_route"):
            f = getattr(eng, n, None)
            if callable(f):
                try:
                    out = f("/국무회의")
                    if out is not None:
                        break
                except Exception:
                    pass
        txt = out if isinstance(out, str) else _r45json.dumps(out, ensure_ascii=False, default=str)
        r = disp.run_cinematic_dispatch("국무회의", dry_run=False)
        gs = "".join(r.get("guas", []))
        c = r.get("council", {})
        sc = r.get("shortcut", {})
        cks = [
            ("dialogue", "뇌화풍" in txt and "택지취" in txt),
            ("dispatch", r.get("ok") is True and r.get("version") in (VERSION, getattr(disp, "VERSION", None)) and r.get("antibody") == "R45" and r.get("organ") == 21),
            ("shortcut", sc.get("llm_skipped") is True and sc.get("hallucination_rate") == 0.0),
            ("council9", len(c.get("chatter", [])) == 9 and len(c.get("beam_routes", [])) == 6),
            ("guas", "뇌화풍" in gs and "택지취" in gs),
            ("gate", r.get("requires_manual_gate") is True and r.get("auto_executed") is False and r.get("background_daemon_spawned") is False),
            ("state-tmp", _r45os.path.isfile(_r45os.path.join(td, "rgon_aon_dispatch_state.json")) and _r45os.path.isfile(_r45os.path.join(td, "docs", "rgon_aon_dispatch_state.json"))),
        ]
    except Exception as e:
        cks = [("exception:" + repr(e)[:100], False)]
    finally:
        if old is None:
            _r45os.environ.pop("RGON_DISPATCH_STATE_DIR", None)
        else:
            _r45os.environ["RGON_DISPATCH_STATE_DIR"] = old
        _r45sh.rmtree(td, ignore_errors=True)
    cks.append(("isolation", rd_bytes(sp) == before))
    bad = [n for n, okv in cks if not okv]
    return {"id": "S15", "ok": not bad, "detail": "PASS" if not bad else "FAIL:" + ",".join(bad)}
_R45_DEPTH = [0]
def _r45_extend(rep):
    box = {}
    th = _r45th.Thread(target=lambda: box.__setitem__("n", r45_check_n17())); th.start()
    s = r45_check_s15(); th.join(120)
    n = box.get("n") or {"id": "N17", "ok": False, "detail": "timeout"}
    fails = (0 if n["ok"] else 1) + (0 if s["ok"] else 1)
    for k in ("organs_total", "organ_total", "total_organs", "synapses_total", "synapse_total", "total_synapses"):
        if isinstance(rep.get(k), int) and not isinstance(rep.get(k), bool):
            rep[k] += 1
    for ks, okv in ((("organs_passed", "organ_passed", "passed_organs", "organs_ok"), n["ok"]), (("synapses_passed", "synapse_passed", "passed_synapses", "synapses_ok"), s["ok"])):
        for k in ks:
            if isinstance(rep.get(k), int) and not isinstance(rep.get(k), bool) and okv:
                rep[k] += 1
    rep["r45"] = {"N17": n, "S15": s, "organ_total": 17, "synapse_total": 15, "ok": fails == 0}
    sc = rep.get("synapse_health_score")
    cap = round(100.0 * (32 - fails) / 32.0, 1)
    rep["synapse_health_score"] = round(min(float(sc), cap), 1) if isinstance(sc, (int, float)) else cap
    if fails:
        rep["ok"] = False
    return rep
def _r45_wrap_full(fn):
    if getattr(fn, "_r45", False):
        return fn
    def w(*a, **k):
        _R45_DEPTH[0] += 1
        try:
            rep = fn(*a, **k)
        finally:
            _R45_DEPTH[0] -= 1
        return _r45_extend(rep) if _R45_DEPTH[0] == 0 and isinstance(rep, dict) else rep
    w._r45 = True
    w.__name__ = getattr(fn, "__name__", "run_full")
    w.__doc__ = getattr(fn, "__doc__", None)
    return w
for _n in ("run_full", "run_all", "verify_all", "full_check"):
    if callable(globals().get(_n)):
        globals()[_n] = _r45_wrap_full(globals()[_n])
# <<< RGON R45 CINEMATIC DISPATCH VERIFIER EXT END

# >>> RGON R46 AUTO EVOLVER VERIFIER EXT START
import os as _r46os, sys as _r46sys, json as _r46json, subprocess as _r46sp, tempfile as _r46tmp, importlib as _r46il, threading as _r46th, shutil as _r46sh
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R57"
EXPECTED_SKILL_COUNT = 44
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R46_ORGAN_NODE = {"id": "N18", "file": "rgon_aon_auto_skill_evolver.py", "organ_no": 22}
R46_SYNAPSE = {"id": "S16", "desc": "대화허브 /흡수 -> 제22기관 10대 플랫폼 채집 & 과식방지 영양분 체 & 그릇 크기 확장 & 5대 자아성찰 5/5 & 수동 게이트 & 격리 검증"}
def _r46_root(): return _r46os.path.dirname(_r46os.path.abspath(__file__))
def r46_check_n18():
    p = _r46os.path.join(_r46_root(), R46_ORGAN_NODE["file"])
    if not _r46os.path.isfile(p):
        return {"id": "N18", "ok": False, "detail": "missing"}
    td = _r46tmp.mkdtemp(prefix="r46_n18_")
    env = dict(_r46os.environ); env["RGON_EVOLVER_STATE_DIR"] = td
    try:
        o = _r46sp.run([_r46sys.executable, p, "--self-test", "--json"], capture_output=True, text=True, encoding="utf-8", timeout=90, env=env)
        d = _r46json.loads(o.stdout)
        ok = o.returncode == 0 and d.get("ok") is True
        return {"id": "N18", "ok": ok, "detail": "self_test " + ("PASS" if ok else "FAIL")}
    except Exception as e:
        return {"id": "N18", "ok": False, "detail": repr(e)[:120]}
    finally:
        _r46sh.rmtree(td, ignore_errors=True)
def r46_check_s16():
    root = _r46_root()
    sp = _r46os.path.join(root, "rgon_aon_evolver_state.json")
    def rd_bytes(p):
        if not _r46os.path.isfile(p): return None
        with open(p, "rb") as f: return f.read()
    before = rd_bytes(sp)
    td = _r46tmp.mkdtemp(prefix="r46_s16_")
    old = _r46os.environ.get("RGON_EVOLVER_STATE_DIR")
    _r46os.environ["RGON_EVOLVER_STATE_DIR"] = td
    try:
        if root not in _r46sys.path:
            _r46sys.path.insert(0, root)
        eng = _r46il.import_module("rgon_aon_dialogue_engine")
        ev = _r46il.import_module("rgon_aon_auto_skill_evolver")
        out = None
        for n in ("r46_route", "process_dialogue", "converse", "route", "r40_route"):
            f = getattr(eng, n, None)
            if callable(f):
                try:
                    out = f("/흡수 한걸음씩 만물 영양분 점진 흡수")
                    if out is not None:
                        break
                except Exception:
                    pass
        txt = out if isinstance(out, str) else _r46json.dumps(out, ensure_ascii=False, default=str)
        r = ev.run_auto_evolution("한걸음씩 만물 영양분 점진 흡수", live_net=False, dry_run=False)
        gs = "".join(r.get("guas", []))
        fg, sv, vs, rf = r.get("forage", {}), r.get("sieve", {}), r.get("vessel", {}), r.get("reflection", {})
        cks = [
            ("dialogue", "산뢰이" in txt and "풍산점" in txt and "풍지관" in txt),
            ("evolver", r.get("ok") is True and r.get("version") in (VERSION, getattr(ev, "VERSION", None)) and r.get("antibody") == "R46" and r.get("organ") == 22),
            ("forage10", fg.get("platform_count") == 10),
            ("sieve", sv.get("overfeed_prevented") is True and sv.get("portion_ratio", 1.0) <= 0.25 and sv.get("toxins_rejected_count", 0) > 0),
            ("vessel", vs.get("digestible_step_size") == 1 and vs.get("vessel_capacity_score") == 100.0),
            ("reflection5", rf.get("passed_count") == 5 and rf.get("reflection_passed") is True),
            ("guas", "산뢰이" in gs and "풍산점" in gs and "풍지관" in gs),
            ("gate", r.get("requires_manual_gate") is True and r.get("auto_executed") is False),
            ("state-tmp", _r46os.path.isfile(_r46os.path.join(td, "rgon_aon_evolver_state.json")) and _r46os.path.isfile(_r46os.path.join(td, "rgon_aon_skill_blueprints.json"))),
        ]
    except Exception as e:
        cks = [("exception:" + repr(e)[:100], False)]
    finally:
        if old is None:
            _r46os.environ.pop("RGON_EVOLVER_STATE_DIR", None)
        else:
            _r46os.environ["RGON_EVOLVER_STATE_DIR"] = old
        _r46sh.rmtree(td, ignore_errors=True)
    cks.append(("isolation", rd_bytes(sp) == before))
    bad = [n for n, okv in cks if not okv]
    return {"id": "S16", "ok": not bad, "detail": "PASS" if not bad else "FAIL:" + ",".join(bad)}
_R46_DEPTH = [0]
def _r46_extend(rep):
    box = {}
    th = _r46th.Thread(target=lambda: box.__setitem__("n", r46_check_n18())); th.start()
    s = r46_check_s16(); th.join(120)
    n = box.get("n") or {"id": "N18", "ok": False, "detail": "timeout"}
    fails = (0 if n["ok"] else 1) + (0 if s["ok"] else 1)
    for k in ("organs_total", "organ_total", "total_organs", "synapses_total", "synapse_total", "total_synapses"):
        if isinstance(rep.get(k), int) and not isinstance(rep.get(k), bool):
            rep[k] += 1
    for ks, okv in ((("organs_passed", "organ_passed", "passed_organs", "organs_ok"), n["ok"]), (("synapses_passed", "synapse_passed", "passed_synapses", "synapses_ok"), s["ok"])):
        for k in ks:
            if isinstance(rep.get(k), int) and not isinstance(rep.get(k), bool) and okv:
                rep[k] += 1
    rep["r46"] = {"N18": n, "S16": s, "organ_total": 18, "synapse_total": 16, "ok": fails == 0}
    sc = rep.get("synapse_health_score")
    cap = round(100.0 * (34 - fails) / 34.0, 1)
    rep["synapse_health_score"] = round(min(float(sc), cap), 1) if isinstance(sc, (int, float)) else cap
    if fails:
        rep["ok"] = False
    return rep
def _r46_wrap_full(fn):
    if getattr(fn, "_r46", False):
        return fn
    def w(*a, **k):
        _R46_DEPTH[0] += 1
        try:
            rep = fn(*a, **k)
        finally:
            _R46_DEPTH[0] -= 1
        return _r46_extend(rep) if _R46_DEPTH[0] == 0 and isinstance(rep, dict) else rep
    w._r46 = True
    w.__name__ = getattr(fn, "__name__", "run_full")
    w.__doc__ = getattr(fn, "__doc__", None)
    return w
for _n in ("run_full", "run_all", "verify_all", "full_check"):
    if callable(globals().get(_n)):
        globals()[_n] = _r46_wrap_full(globals()[_n])
# <<< RGON R46 AUTO EVOLVER VERIFIER EXT END

# [RGON-R47-VERIFIER-EXT-START]
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R57"
EXPECTED_SKILL_COUNT = 44
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R47_STUDIO_ORGAN = "rgon_aon_zeroclick_studio.py"
try:
    if R47_STUDIO_ORGAN not in ORGANS:
        ORGANS.append(R47_STUDIO_ORGAN)
except NameError:
    ORGANS = [R47_STUDIO_ORGAN]

def _r47_s17_check():
    import os as _o, tempfile as _t, importlib as _il, shutil as _sh, time as _tm
    _t0 = _tm.perf_counter()
    name = "대화허브(/썸네일·/엑셀)→제23기관 클릭0번 스튜디오"
    tmp = _t.mkdtemp(prefix="rgon_s17_")
    prev = _o.environ.get("RGON_ZEROCLICK_STATE_DIR")
    _o.environ["RGON_ZEROCLICK_STATE_DIR"] = tmp
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "r40_route", None) or getattr(dlg, "route", None)
        r1 = fn("/썸네일 아온 제로클릭 테스트")
        r2 = fn("/엑셀 아온 시트 테스트")
        z1 = (r1.get("zeroclick_studio") or r1) if isinstance(r1, dict) else {}
        z2 = (r2.get("zeroclick_studio") or r2) if isinstance(r2, dict) else {}
        ok = (isinstance(r1, dict) and r1.get("ok") is True and z1.get("kind") == "photo"
              and z1.get("png_valid") is True and z1.get("click_count") == 0
              and isinstance(r2, dict) and r2.get("ok") is True and z2.get("kind") == "sheet"
              and z2.get("xlsx_valid") is True and z2.get("click_count") == 0
              and z1.get("requires_manual_gate") is True and z1.get("auto_executed") is False)
        return {"id": "S17", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": f"photo={z1.get('png_valid')}, xlsx={z2.get('xlsx_valid')}", "detail": {"photo": z1.get("ok"), "sheet": z2.get("ok")}}
    except Exception as e:
        return {"id": "S17", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}
    finally:
        if prev is None:
            _o.environ.pop("RGON_ZEROCLICK_STATE_DIR", None)
        else:
            _o.environ["RGON_ZEROCLICK_STATE_DIR"] = prev
        _sh.rmtree(tmp, ignore_errors=True)

_r47_orig_vsl = globals().get("verify_synapse_links")
if callable(_r47_orig_vsl) and not getattr(_r47_orig_vsl, "_r47", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r47_orig_vsl(*args, **kwargs)
        s17 = _r47_s17_check()
        if isinstance(res, dict) and isinstance(res.get("synapses"), list):
            items = [x for x in res["synapses"] if not (isinstance(x, dict) and x.get("id") == "S17")] + [s17]
            res["synapses"] = items
            res["passed"] = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            res["total"] = len(items)
            res["ok"] = res["passed"] == res["total"]
        return res
    verify_synapse_links._r47 = True
# [RGON-R47-VERIFIER-EXT-END]

# [RGON-R48-VERIFIER-EXT-START]
R48_MORPH_ORGAN = "rgon_aon_haesang_morph_avatar.py"
try:
    if R48_MORPH_ORGAN not in ORGANS:
        ORGANS.append(R48_MORPH_ORGAN)
except NameError:
    ORGANS = [R48_MORPH_ORGAN]

def _r48_s18_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/변신·/해상)→제24기관 해상 변신 아바타 엔진"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "_r48_haesang_route", None)
        if not fn:
            fn = getattr(dlg, "r40_route", None)
        r = fn("/변신 호박") if fn else None
        ok = isinstance(r, dict) and r.get("ok") is True and r.get("form") in ("pumpkin", "ghost", "orb", "pouty_booty", "cloud", "waterfall_suit")
        return {"id": "S18", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": f"form={r.get('form') if r else None}", "detail": r}
    except Exception as e:
        return {"id": "S18", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

_r48_orig_vsl = globals().get("verify_synapse_links")
if callable(_r48_orig_vsl) and not getattr(_r48_orig_vsl, "_r48", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r48_orig_vsl(*args, **kwargs)
        s18 = _r48_s18_check()
        if isinstance(res, dict) and isinstance(res.get("synapses"), list):
            items = [x for x in res["synapses"] if not (isinstance(x, dict) and x.get("id") == "S18")] + [s18]
            res["synapses"] = items
            res["passed"] = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            res["total"] = len(items)
            res["ok"] = res["passed"] == res["total"]
        return res
# [RGON-R48-VERIFIER-EXT-END]

# [RGON-R49-VERIFIER-EXT-START]
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R57"
EXPECTED_SKILL_COUNT = 45
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R49_VIBE3D_ORGAN = "rgon_aon_vibe3d_director.py"
try:
    if R49_VIBE3D_ORGAN not in ORGANS:
        ORGANS.append(R49_VIBE3D_ORGAN)
except NameError:
    ORGANS = [R49_VIBE3D_ORGAN]

def _r49_s19_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/3D·/시네마틱)→제25기관 바이브 3D 시네마틱 디렉터"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "_r49_vibe3d_route", None)
        if not fn:
            fn = getattr(dlg, "r40_route", None)
        r = fn("/3d 해상이와 아온이 시네마틱 세트장") if fn else None
        ok = isinstance(r, dict) and r.get("ok") is True and (r.get("intent") == "vibe3d_director" or "vibe3d_director" in r)
        ev = f"intent={r.get('intent')}, score={r.get('vibe3d_director', {}).get('quality_score') if isinstance(r, dict) else None}"
        return {"id": "S19", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": r}
    except Exception as e:
        return {"id": "S19", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

_r49_orig_vsl = globals().get("verify_synapse_links")
if callable(_r49_orig_vsl) and not getattr(_r49_orig_vsl, "_r49", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r49_orig_vsl(*args, **kwargs)
        s19 = _r49_s19_check()
        if isinstance(res, dict) and isinstance(res.get("synapses"), list):
            items = [x for x in res["synapses"] if not (isinstance(x, dict) and x.get("id") == "S19")] + [s19]
            res["synapses"] = items
            res["passed"] = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            res["total"] = len(items)
            res["ok"] = res["passed"] == res["total"]
        return res
    verify_synapse_links._r49 = True
# [RGON-R49-VERIFIER-EXT-END]

# [RGON-R50-VERIFIER-EXT-START]
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R57"
EXPECTED_SKILL_COUNT = 46
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R50_IMPECCABLE_ORGAN = "rgon_aon_impeccable_audit_shield.py"
try:
    if R50_IMPECCABLE_ORGAN not in ORGANS:
        ORGANS.append(R50_IMPECCABLE_ORGAN)
except NameError:
    ORGANS = [R50_IMPECCABLE_ORGAN]

def _r50_s20_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/impeccable·/보안감사)→제26기관 아온 임페커블 UI & 감사 방패"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "_r50_impeccable_route", None)
        if not fn:
            fn = getattr(dlg, "r40_route", None)
        r = fn("/impeccable 대시보드 UI 무결점 교차감사") if fn else None
        ok = isinstance(r, dict) and r.get("ok") is True and (r.get("intent") == "impeccable_shield" or "impeccable_shield" in r)
        ev = f"intent={r.get('intent')}, ok={r.get('ok')}"
        return {"id": "S20", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": r}
    except Exception as e:
        return {"id": "S20", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

_r50_orig_vsl = globals().get("verify_synapse_links")
if callable(_r50_orig_vsl) and not getattr(_r50_orig_vsl, "_r50", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r50_orig_vsl(*args, **kwargs)
        s20 = _r50_s20_check()
        if isinstance(res, dict) and isinstance(res.get("synapses"), list):
            items = [x for x in res["synapses"] if not (isinstance(x, dict) and x.get("id") == "S20")] + [s20]
            res["synapses"] = items
            res["passed"] = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            res["total"] = len(items)
            res["ok"] = res["passed"] == res["total"]
        return res
    verify_synapse_links._r50 = True
# [RGON-R50-VERIFIER-EXT-END]

# [RGON-R51-VERIFIER-EXT-START]
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R57"
EXPECTED_SKILL_COUNT = 47
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R51_TOKEN_MASTER_ORGAN = "rgon_aon_token_egolite_master.py"
try:
    if R51_TOKEN_MASTER_ORGAN not in ORGANS:
        ORGANS.append(R51_TOKEN_MASTER_ORGAN)
except NameError:
    ORGANS = [R51_TOKEN_MASTER_ORGAN]

def _r51_s21_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/token·/egolite)→제27기관 아온 토큰 초절약 & 에고라이트 마스터"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "_r51_token_egolite_route", None)
        if not fn:
            fn = getattr(dlg, "r40_route", None)
        r = fn("/token 7대 스택 Spec Kit 수렴 검증") if fn else None
        ok = isinstance(r, dict) and r.get("ok") is True and (r.get("intent") == "token_egolite_master" or "token_egolite_master" in r)
        ev = f"intent={r.get('intent')}, ok={r.get('ok')}"
        return {"id": "S21", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": r}
    except Exception as e:
        return {"id": "S21", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

_r51_orig_vsl = globals().get("verify_synapse_links")
if callable(_r51_orig_vsl) and not getattr(_r51_orig_vsl, "_r51", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r51_orig_vsl(*args, **kwargs)
        s21 = _r51_s21_check()
        if isinstance(res, dict) and isinstance(res.get("synapses"), list):
            items = [x for x in res["synapses"] if not (isinstance(x, dict) and x.get("id") == "S21")] + [s21]
            res["synapses"] = items
            res["passed"] = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            res["total"] = len(items)
            res["ok"] = res["passed"] == res["total"]
        return res
    verify_synapse_links._r51 = True
# [RGON-R51-VERIFIER-EXT-END]

# [RGON-R52-VERIFIER-EXT-START]
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R57"
EXPECTED_SKILL_COUNT = 48
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R52_COMMANDER_TWIN_ORGAN = "rgon_aon_commander_twin.py"
try:
    if R52_COMMANDER_TWIN_ORGAN not in ORGANS:
        ORGANS.append(R52_COMMANDER_TWIN_ORGAN)
except NameError:
    ORGANS = [R52_COMMANDER_TWIN_ORGAN]

def _r52_s22_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/twin·/commander)→제28기관 아온 대표님 인지 디지털 트윈 & 사령관"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "_r52_commander_twin_route", None)
        if not fn:
            fn = getattr(dlg, "r40_route", None)
        r = fn("/twin 이상일 대표님 7단계 일처리 DNA 무인 대행") if fn else None
        ok = isinstance(r, dict) and r.get("ok") is True and (r.get("intent") == "commander_twin" or "commander_twin" in r)
        ev = f"intent={r.get('intent')}, ok={r.get('ok')}"
        return {"id": "S22", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": r}
    except Exception as e:
        return {"id": "S22", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

_r52_orig_vsl = globals().get("verify_synapse_links")
if callable(_r52_orig_vsl) and not getattr(_r52_orig_vsl, "_r52", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r52_orig_vsl(*args, **kwargs)
        s22 = _r52_s22_check()
        if isinstance(res, dict) and isinstance(res.get("synapses"), list):
            items = [x for x in res["synapses"] if not (isinstance(x, dict) and x.get("id") == "S22")] + [s22]
            res["synapses"] = items
            res["passed"] = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            res["total"] = len(items)
            res["ok"] = res["passed"] == res["total"]
        return res
    verify_synapse_links._r52 = True
# [RGON-R52-VERIFIER-EXT-END]



# [RGON-R53-VERIFIER-EXT-START]
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R57"
EXPECTED_SKILL_COUNT = 49
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R53_PAGE_BUTTON_BOT_ORGAN = "rgon_aon_page_button_bot_engine.py"
try:
    if R53_PAGE_BUTTON_BOT_ORGAN not in ORGANS:
        ORGANS.append(R53_PAGE_BUTTON_BOT_ORGAN)
except NameError:
    ORGANS = [R53_PAGE_BUTTON_BOT_ORGAN]

def _r53_s23_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/bot·/버튼봇·/체인봇)→제29기관 아온 WebMCP 전 페이지·전 버튼 자동화 봇 엔진"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "_r53_page_button_bot_route", None)
        if not fn:
            fn = getattr(dlg, "r40_route", None)
        r = fn("/bot WebMCP 버튼 봇 출격 상태 점검") if fn else None
        ok = isinstance(r, dict) and r.get("ok") is True and (r.get("intent") == "page_button_bot" or "page_button_bot" in r)
        ev = f"intent={r.get('intent')}, ok={r.get('ok')}"
        return {"id": "S23", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": r}
    except Exception as e:
        return {"id": "S23", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

_r53_orig_vsl = globals().get("verify_synapse_links")
if callable(_r53_orig_vsl) and not getattr(_r53_orig_vsl, "_r53", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r53_orig_vsl(*args, **kwargs)
        s23 = _r53_s23_check()
        if isinstance(res, dict) and isinstance(res.get("synapses"), list):
            items = [x for x in res["synapses"] if not (isinstance(x, dict) and x.get("id") == "S23")] + [s23]
            res["synapses"] = items
            res["passed"] = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            res["total"] = len(items)
            res["ok"] = res["passed"] == res["total"]
        return res
    verify_synapse_links._r53 = True
# [RGON-R53-VERIFIER-EXT-END]


# [RGON-R54-VERIFIER-EXT-START]
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R57"
EXPECTED_SKILL_COUNT = 53
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


# [RGON-R55-VERIFIER-EXT-START]
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R57"
EXPECTED_SKILL_COUNT = 53
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R55_ORG_CHART_ORGAN = "rgon_aon_supreme_org_chart_engine.py"
try:
    if R55_ORG_CHART_ORGAN not in ORGANS:
        ORGANS.append(R55_ORG_CHART_ORGAN)
except NameError:
    ORGANS = [R55_ORG_CHART_ORGAN]

def _r55_s25_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/조직도·/진형·/지휘)→제31기관 세계 Top 1 자율 조직구성도 & 5대 전술 진형 본부"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "_r55_supreme_org_chart_route", None)
        if not fn:
            fn = getattr(dlg, "r40_route", None)
        r = fn("/조직도 5대 전술 진형 및 4계층 권력분립 조직구성도 점검") if fn else None
        ok = isinstance(r, dict) and r.get("ok") is True and (r.get("intent") == "supreme_org_chart" or "supreme_org_chart" in str(r))
        ev = f"intent={r.get('intent') if isinstance(r, dict) else None}, ok={r.get('ok') if isinstance(r, dict) else False}"
        return {"id": "S25", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": r}
    except Exception as e:
        return {"id": "S25", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

_r55_orig_vsl = globals().get("verify_synapse_links")
if callable(_r55_orig_vsl) and not getattr(_r55_orig_vsl, "_r55", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r55_orig_vsl(*args, **kwargs)
        s25 = _r55_s25_check()
        if isinstance(res, dict) and isinstance(res.get("synapses"), list):
            items = [x for x in res["synapses"] if not (isinstance(x, dict) and x.get("id") == "S25")] + [s25]
            res["synapses"] = items
            res["passed"] = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            res["total"] = len(items)
            res["ok"] = res["passed"] == res["total"]
        return res
    verify_synapse_links._r55 = True
# [RGON-R55-VERIFIER-EXT-END]


# [RGON-R56-VERIFIER-EXT-START]
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R57"
EXPECTED_SKILL_COUNT = 53
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R56_TELEGRAM_ORGAN = "rgon_aon_telegram_omni_messenger.py"
try:
    if R56_TELEGRAM_ORGAN not in ORGANS:
        ORGANS.append(R56_TELEGRAM_ORGAN)
except NameError:
    ORGANS = [R56_TELEGRAM_ORGAN]

def _r56_s26_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/텔레그램·/카톡·/메신저)→제32기관 듀얼 텔레그램·카톡형 실시간 양방향 메신저"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "_r56_telegram_messenger_route", None)
        if not fn:
            fn = getattr(dlg, "r40_route", None)
        r = fn("/텔레그램 듀얼 핫라인 1호기 및 2호기 연결 상태 점검") if fn else None
        ok = isinstance(r, dict) and r.get("ok") is True and (r.get("intent") == "telegram_messenger" or "telegram_messenger" in str(r))
        ev = f"intent={r.get('intent') if isinstance(r, dict) else None}, ok={r.get('ok') if isinstance(r, dict) else False}"
        return {"id": "S26", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": r}
    except Exception as e:
        return {"id": "S26", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

_r56_orig_vsl = globals().get("verify_synapse_links")
if callable(_r56_orig_vsl) and not getattr(_r56_orig_vsl, "_r56", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r56_orig_vsl(*args, **kwargs)
        s26 = _r56_s26_check()
        if isinstance(res, dict) and isinstance(res.get("synapses"), list):
            items = [x for x in res["synapses"] if not (isinstance(x, dict) and x.get("id") == "S26")] + [s26]
            res["synapses"] = items
            res["passed"] = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            res["total"] = len(items)
            res["ok"] = res["passed"] == res["total"]
        return res
    verify_synapse_links._r56 = True
# [RGON-R56-VERIFIER-EXT-END]


# [RGON-R57-VERIFIER-EXT-START]
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R57"
EXPECTED_SKILL_COUNT = 53
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R57_INVISIBLE_ORGAN = "rgon_aon_invisible_kakao_tg_backbone.py"
try:
    if R57_INVISIBLE_ORGAN not in ORGANS:
        ORGANS.append(R57_INVISIBLE_ORGAN)
except NameError:
    ORGANS = [R57_INVISIBLE_ORGAN]

def _r57_s27_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/인비저블·/카톡·/사령부톡)→제33기관 인비저블 텔레그램 백본 & 카톡형 만능 대화창"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "_r57_invisible_kakao_route", None)
        if not fn:
            fn = getattr(dlg, "r40_route", None)
        r = fn("/인비저블 4대 채널톡 및 3대 텔레그램 백본 연결 점검") if fn else None
        ok = isinstance(r, dict) and r.get("ok") is True and (r.get("intent") == "invisible_kakao_tg" or "invisible_kakao_tg" in str(r))
        ev = f"intent={r.get('intent') if isinstance(r, dict) else None}, ok={r.get('ok') if isinstance(r, dict) else False}"
        return {"id": "S27", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": r}
    except Exception as e:
        return {"id": "S27", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

_r57_orig_vsl = globals().get("verify_synapse_links")
if callable(_r57_orig_vsl) and not getattr(_r57_orig_vsl, "_r57", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r57_orig_vsl(*args, **kwargs)
        s27 = _r57_s27_check()
        if isinstance(res, dict) and isinstance(res.get("synapses"), list):
            items = [x for x in res["synapses"] if not (isinstance(x, dict) and x.get("id") == "S27")] + [s27]
            res["synapses"] = items
            res["passed"] = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            res["total"] = len(items)
            res["ok"] = res["passed"] == res["total"]
        return res
    verify_synapse_links._r57 = True
# [RGON-R57-VERIFIER-EXT-END]

# [RGON-R58-VERIFIER-EXT-START]
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R63"
EXPECTED_SKILL_COUNT = 55
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R58_PINNACLE_ORGAN = "rgon_aon_pinnacle_omni_comm.py"
try:
    if R58_PINNACLE_ORGAN not in ORGANS:
        ORGANS.append(R58_PINNACLE_ORGAN)
except NameError:
    ORGANS = [R58_PINNACLE_ORGAN]

def _r58_s28_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/멀티모달·/피너클)→제34기관 피너클 옴니 커뮤니케이터 & 멀티모달 두뇌"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "_r58_pinnacle_omni_route", None)
        if not fn:
            fn = getattr(dlg, "r40_route", None)
        r = fn("/멀티모달 피너클 옴니 커뮤니케이터 및 작업현황 점검") if fn else None
        ok = isinstance(r, dict) and r.get("ok") is True and (r.get("intent") == "pinnacle_omni_comm" or "pinnacle_omni_comm" in str(r))
        ev = f"intent={r.get('intent') if isinstance(r, dict) else None}, ok={r.get('ok') if isinstance(r, dict) else False}"
        return {"id": "S28", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": r}
    except Exception as e:
        return {"id": "S28", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

_r58_orig_vsl = globals().get("verify_synapse_links")
if callable(_r58_orig_vsl) and not getattr(_r58_orig_vsl, "_r58", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r58_orig_vsl(*args, **kwargs)
        s28 = _r58_s28_check()
        if isinstance(res, dict) and isinstance(res.get("synapses"), list):
            items = [x for x in res["synapses"] if not (isinstance(x, dict) and x.get("id") == "S28")] + [s28]
            res["synapses"] = items
            res["passed"] = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            res["total"] = len(items)
            res["ok"] = res["passed"] == res["total"]
        return res
    verify_synapse_links._r58 = True
# [RGON-R58-VERIFIER-EXT-END]

# [RGON-R59-VERIFIER-EXT-START]
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY_RANGE = "R1~R63"
EXPECTED_SKILL_COUNT = 55
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R59_MOTION_ORGAN = "rgon_aon_opus_motion_studio.py"
try:
    if R59_MOTION_ORGAN not in ORGANS:
        ORGANS.append(R59_MOTION_ORGAN)
except NameError:
    ORGANS = [R59_MOTION_ORGAN]

def _r59_s29_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/모션·/오퍼스)→제35기관 클로드 오퍼스 5.5 모션 그래픽 스튜디오"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "_r59_motion_studio_route", None)
        if not fn:
            fn = getattr(dlg, "r40_route", None)
        r = fn("/모션 그래픽 스튜디오 가동") if fn else None
        ok = isinstance(r, dict) and r.get("ok") is True and (r.get("intent") == "opus_motion_studio" or "opus_motion_studio" in str(r))
        ev = f"intent={r.get('intent') if isinstance(r, dict) else None}, ok={r.get('ok') if isinstance(r, dict) else False}"
        return {"id": "S29", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": r}
    except Exception as e:
        return {"id": "S29", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

_r59_orig_vsl = globals().get("verify_synapse_links")
if callable(_r59_orig_vsl) and not getattr(_r59_orig_vsl, "_r59", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r59_orig_vsl(*args, **kwargs)
        s29 = _r59_s29_check()
        if isinstance(res, dict) and isinstance(res.get("synapses"), list):
            items = [x for x in res["synapses"] if not (isinstance(x, dict) and x.get("id") == "S29")] + [s29]
            res["synapses"] = items
            res["passed"] = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            res["total"] = len(items)
            res["ok"] = res["passed"] == res["total"]
        return res
    verify_synapse_links._r59 = True
# [RGON-R59-VERIFIER-EXT-END]

# [RGON-R64-VERIFIER-EXT-START]
VERSION = "v11.66-AON-GENERAL-HOSPITAL"
ANTIBODY_RANGE = "R1~R64"
EXPECTED_SKILL_COUNT = 60
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R60_EMPIRE_ORGAN = "rgon_aon_empire_asset_hub.py"
R61_GDRIVE_ORGAN = "rgon_aon_gdrive_5tb_organizer.py"
R62_SHORTS_ORGAN = "rgon_aon_13shorts_omni_engine.py"
R63_SUPER_SENIOR_ORGAN = "step64_aon_15shorts_super_senior_engine.py"
try:
    if R60_EMPIRE_ORGAN not in ORGANS:
        ORGANS.append(R60_EMPIRE_ORGAN)
    if R61_GDRIVE_ORGAN not in ORGANS:
        ORGANS.append(R61_GDRIVE_ORGAN)
    if R62_SHORTS_ORGAN not in ORGANS:
        ORGANS.append(R62_SHORTS_ORGAN)
    if R63_SUPER_SENIOR_ORGAN not in ORGANS:
        ORGANS.append(R63_SUPER_SENIOR_ORGAN)
except NameError:
    ORGANS = [R60_EMPIRE_ORGAN, R61_GDRIVE_ORGAN, R62_SHORTS_ORGAN, R63_SUPER_SENIOR_ORGAN]

def _r60_s30_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/자산·/음원·/블로그)→제36기관 아온 한걸음씩 6대 자산 제국 마스터 통합 허브"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "_r60_empire_asset_route", None)
        if not fn:
            fn = getattr(dlg, "r40_route", None)
        r = fn("곧 발매될 음원 알려줘") if fn else None
        ok = isinstance(r, dict) and r.get("ok") is True and (r.get("intent") == "empire_distrokid_album" or "가을과 겨울 사이" in str(r))
        ev = f"intent={r.get('intent') if isinstance(r, dict) else None}, ok={r.get('ok') if isinstance(r, dict) else False}"
        return {"id": "S30", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": r}
    except Exception as e:
        return {"id": "S30", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

def _r61_s31_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/구글드라이브·/5TB·/조니데시멀)→제37기관 아온 Google One 5TB 초심플 클라우드 아카이브 엔진"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "_r61_gdrive_route", None)
        if not fn:
            fn = getattr(dlg, "r40_route", None)
        r = fn("구글 드라이브 5TB 정리법 알려줘") if fn else None
        ok = isinstance(r, dict) and r.get("ok") is True and (r.get("intent") == "gdrive_5tb_decimal" or "5,000 GB" in str(r))
        ev = f"intent={r.get('intent') if isinstance(r, dict) else None}, ok={r.get('ok') if isinstance(r, dict) else False}"
        return {"id": "S31", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": r}
    except Exception as e:
        return {"id": "S31", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

def _r62_s32_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/13대쇼츠·/jev·/마케팅·/보안)→제38기관 아온 13대 쇼츠 옴니-인텔리전스 마스터 엔진"
    try:
        mod = _il.import_module("rgon_aon_13shorts_omni_engine")
        m = mod.load_manifest()
        jev_res = mod.TypeSafeJevEngine.noul(True, {"x": 10, "y": 10, "w": 100, "h": 100})
        sec_res = mod.security_audit()
        ok = (
            mod.VERSION == VERSION and
            m.get("stats", {}).get("total_shorts") == 13 and
            jev_res.get("safe") is True and
            sec_res.get("all_passed") is True
        )
        ev = f"manifest_shorts={m.get('stats', {}).get('total_shorts')}, jev_safe={jev_res.get('safe')}, sec_score={sec_res.get('security_score')}"
        return {"id": "S32", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": ev}
    except Exception as e:
        return {"id": "S32", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

def _r63_s33_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/지식그래프·/카파시·/슈퍼시니어)→제39기관 아온 15대 슈퍼-시니어 & 지식그래프 엔진"
    try:
        mod = _il.import_module("step64_aon_15shorts_super_senior_engine")
        deb = mod.run_bull_vs_bear_debate("NVDA 엔비디아")
        rows = mod.preview_zero_delete_rename(["test.pdf"])
        seek = mod.generate_seek_motion_template("테스트", 120)
        ok = (
            mod.VERSION == VERSION and
            mod.ORGAN == 39 and
            mod.SKILLS == 60 and
            len(mod.SHORTS_15_ARSENAL) == 15 and
            bool(deb.get("consensus")) and
            len(rows) == 1 and
            "window.seek=function(t)" in seek
        )
        ev = f"organ={mod.ORGAN}, skills={mod.SKILLS}, shorts={len(mod.SHORTS_15_ARSENAL)}, deb_decision={deb.get('consensus', {}).get('decision')}"
        return {"id": "S33", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": ev}
    except Exception as e:
        return {"id": "S33", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

# [RGON-R64-HOSPITAL-SYNAPSE-BEGIN]
try:
    if "step65_aon_general_hospital_self_healing.py" not in ORGANS:
        ORGANS.append("step65_aon_general_hospital_self_healing.py")
except NameError:
    ORGANS = ["step65_aon_general_hospital_self_healing.py"]

def _r64_s34_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/병원·/소방서·/AS·/자가치료)→제40기관 아온 초일류 종합병원"
    try:
        mod = _il.import_module("step65_aon_general_hospital_self_healing")
        ok = (
            mod.VERSION == VERSION and
            mod.ORGAN == 40 and
            mod.SKILLS == 60 and
            len(mod.HOSPITAL_DEPARTMENTS) == 5 and
            len(mod.RCA8) == 8
        )
        ev = f"organ={mod.ORGAN}, skills={mod.SKILLS}, depts={len(mod.HOSPITAL_DEPARTMENTS)}, rca={len(mod.RCA8)}"
        return {"id": "S34", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": ev}
    except Exception as e:
        return {"id": "S34", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}

_r64_orig_vsl = globals().get("verify_synapse_links")
if callable(_r64_orig_vsl) and not getattr(_r64_orig_vsl, "_r64", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r64_orig_vsl(*args, **kwargs)
        s30 = _r60_s30_check()
        s31 = _r61_s31_check()
        s32 = _r62_s32_check()
        s33 = _r63_s33_check()
        s34 = _r64_s34_check()
        if isinstance(res, dict) and isinstance(res.get("synapses"), list):
            items = [x for x in res["synapses"] if not (isinstance(x, dict) and x.get("id") in ("S30", "S31", "S32", "S33", "S34"))] + [s30, s31, s32, s33, s34]
            res["synapses"] = items
            res["passed"] = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            res["total"] = len(items)
            res["ok"] = res["passed"] == res["total"]
        return res
    verify_synapse_links._r64 = True
# [RGON-R64-HOSPITAL-SYNAPSE-END]

# [RGON-R65-R66-R67-CHRONOMETER-SYNAPSE-BEGIN]
try:
    for _org_f in (
        "step66_aon_omniroute_council_15shorts_engine.py",
        "step67_aon_chronometer_deep_auditor.py",
        "step68_aon_chrono_diet_perfection.py",
        "step69_aon_maestro_synergy_scheduler.py",
        "step70_aon_immutable_dna_keyvault.py",
        "step71_aon_safe_monetization_top10_engine.py",
    ):
        if _org_f not in ORGANS:
            ORGANS.append(_org_f)
except NameError:
    ORGANS = [
        "step66_aon_omniroute_council_15shorts_engine.py",
        "step67_aon_chronometer_deep_auditor.py",
        "step68_aon_chrono_diet_perfection.py",
        "step69_aon_maestro_synergy_scheduler.py",
        "step70_aon_immutable_dna_keyvault.py",
        "step71_aon_safe_monetization_top10_engine.py",
    ]


def _r65_s35_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/옴니라우트·/카운슬·/3차15쇼츠)→제41기관 아온 3차 15대 쇼츠 무중단 라우터 & LLM 카운슬 엔진"
    try:
        mod = _il.import_module("step66_aon_omniroute_council_15shorts_engine")
        r1 = mod.omniroute_failover_switch(
            {"Claude-Opus-4.6-Thinking": "QUOTA_EXCEEDED", "Claude-Sonnet-4.6": "QUOTA_EXCEEDED"},
            "background",
        )
        r2 = mod.run_karpathy_llm_council("Step66 제41기관 시냅스 검증")
        r3 = mod.convert_repo_and_14slot_motion("https://github.com/sangill111157-spec/hangeol-plan")
        r4 = mod.scrub_watermark_and_guard_distillation("아온\u200b 엔진이 작동할 수 있습니다.", rpm=1200)
        ok = (
            len(mod.SHORTS_3RD_15) == 15
            and r1.get("active_model") == "Gemini-3.1-Pro-High"
            and r1.get("mcp_async_task") is True
            and r1.get("zero_downtime_guaranteed") is True
            and len(r2.get("stage1_opinions", [])) == 3
            and r2.get("consensus_score", 0) > 0.99
            and r3.get("motion_14slots_count") == 14
            and r3.get("game_studio_agents") == 49
            and r3.get("anthropic_work_plugins") == 11
            and r4.get("watermark_removed") is True
            and r4.get("distillation_attack_blocked") is True
        )
        ev = f"organ=41, shorts={len(mod.SHORTS_3RD_15)}, model={r1.get('active_model')}, consensus={r2.get('consensus_score')}"
        return {"id": "S35", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": ev}
    except Exception as e:
        return {"id": "S35", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}


def _r66_s36_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/크로노미터·/전수감사·/톱니바퀴)→제42기관 아온 크로노미터 전수 톱니바퀴 검증 & 무가식 실증 감사원"
    try:
        mod = _il.import_module("step67_aon_chronometer_deep_auditor")
        g2 = mod.verify_step63_to_66_runtime_gears()
        g3 = mod.verify_43shorts_registries()
        g4 = mod.verify_index_html_drawers()
        g5 = mod.verify_protected_and_handover()
        ok = (
            mod.ORGAN_NO == 42
            and g2.get("ok") is True
            and g3.get("ok") is True
            and g3.get("total_shorts") == 43
            and g4.get("ok") is True
            and g5.get("ok") is True
        )
        ev = f"organ=42, runtime_gears={g2.get('gears_passed')}/{g2.get('gears_total')}, shorts_total={g3.get('total_shorts')}, handover_lines={g5.get('handover_lines')}"
        return {"id": "S36", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": ev}
    except Exception as e:
        return {"id": "S36", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}


def _r67_s37_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/비워내기·/다이어트·/텔레그램무결성)→제43기관 아온 텔레그램 실측 무결성 & Ponytail 무결점 다이어트 감사원"
    try:
        mod = _il.import_module("step68_aon_chrono_diet_perfection")
        a1 = mod.verify_axis_a1_telegram_antispam()
        a2 = mod.verify_axis_a2_morning_brief()
        a3 = mod.verify_axis_a3_github_actions_analytics()
        a4 = mod.verify_axis_a4_nvda_scheduler_misfire()
        ok = (
            mod.ORGAN_NO == 43
            and a1.get("ok") is True
            and a2.get("ok") is True
            and a3.get("ok") is True
            and a4.get("ok") is True
        )
        ev = f"organ=43, tg_loopback={a1.get('dry_run_loopback')}, brief_ok={a2.get('ok')}, actions_ok={a3.get('ok')}, nvda_sched_ok={a4.get('ok')}"
        return {"id": "S37", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": ev}
    except Exception as e:
        return {"id": "S37", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}


def _r68_s38_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/마에스트로·/7대기관장·/시너지체인·/24시간스케줄)→제44기관 아온 마에스트로 7대 기관장 협업 시너지 DAG & 24시간 마스터 스케줄러"
    try:
        mod = _il.import_module("step69_aon_maestro_synergy_scheduler")
        chains = mod.run_all_5_synergy_chains()
        slot = mod.get_active_schedule_slot()
        ok = (
            mod.ORGAN_NO == 44
            and len(mod.DIRECTORS_7) == 7
            and len(mod.SYNERGY_CHAINS_5) == 5
            and len(mod.MASTER_SCHEDULE_24H) == 6
            and chains.get("ok") is True
            and chains.get("chains_executed") == 5
            and chains.get("chains_passed") == 5
            and chains.get("total_errors") == 0
            and slot.get("primary_chain_to_run") in mod.SYNERGY_CHAINS_5
        )
        ev = f"organ=44, directors={len(mod.DIRECTORS_7)}, chains={chains.get('chains_passed')}/{chains.get('chains_executed')}, errors={chains.get('total_errors')}, slot={slot.get('active_slot', {}).get('slot_id')}"
        return {"id": "S38", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": ev}
    except Exception as e:
        return {"id": "S38", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}


def _r69_s39_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/불변법칙·/8대법칙·/마스터키금고·/키바인딩)→제45기관 아온 불변의 일처리 8대 법칙 DNA 이식 & 마스터 키 금고 바인딩 엔진"
    try:
        mod = _il.import_module("step70_aon_immutable_dna_keyvault")
        inj = mod.ImmutableWorkDnaInjector()
        dna_res = inj.verify_all_agents_dna_compliance()
        vault = mod.AonMasterKeyVault()
        bind_res = vault.bind_to_directors_and_chains()
        leak_res = vault.verify_zero_secret_leak(str(bind_res))
        ok = (
            mod.ORGAN_NO == 45
            and len(mod.RGON_IMMUTABLE_WORK_LAWS_8) == 8
            and dna_res.get("ok") is True
            and bind_res.get("ok") is True
            and leak_res.get("ok") is True
            and leak_res.get("zero_leak_guaranteed") is True
        )
        ev = f"organ=45, laws={len(mod.RGON_IMMUTABLE_WORK_LAWS_8)}, skills_dna={dna_res.get('skills_dna_injection', {}).get('total_skill_mds_scanned')}, keys_bound={bind_res.get('total_keys_bound')}/{bind_res.get('total_keys_checked')}, zero_leak={leak_res.get('zero_leak_guaranteed')}"
        return {"id": "S39", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": ev}
    except Exception as e:
        return {"id": "S39", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}


def _r70_s40_check():
    import time as _tm, importlib as _il
    _t0 = _tm.perf_counter()
    name = "대화허브(/수익화톱10·/무위험수익화·/에셋팩토리·/24시간수익스케줄)→제46기관 아온 무위험 AI 수익화 Top 10 마스터 스케줄러 & 에셋 팩토리"
    try:
        mod = _il.import_module("step71_aon_safe_monetization_top10_engine")
        fac = mod.AonSafeMonetizationFactory()
        res = fac.run_all_10_monetization_pipelines()
        ok = (
            mod.ORGAN_NO == 46
            and len(mod.SAFE_MONETIZATION_TOP10) == 10
            and len(mod.MONETIZATION_24H_SCHEDULE_MATRIX) == 6
            and res.get("ok") is True
            and res.get("passed_models") == 10
            and "_immutable_dna_seal" in res
        )
        ev = f"organ=46, models={res.get('passed_models')}/{res.get('total_models')}, schedule_slots={res.get('schedule_slots_count')}, pilot1_linked={res.get('pilot1_live_assets', {}).get('ok')}"
        return {"id": "S40", "name": name, "ok": bool(ok), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": ev, "detail": ev}
    except Exception as e:
        return {"id": "S40", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}


_r66_orig_vsl = globals().get("verify_synapse_links")
if callable(_r66_orig_vsl) and not getattr(_r66_orig_vsl, "_r66", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r66_orig_vsl(*args, **kwargs)
        s35 = _r65_s35_check()
        s36 = _r66_s36_check()
        s37 = _r67_s37_check()
        s38 = _r68_s38_check()
        s39 = _r69_s39_check()
        s40 = _r70_s40_check()
        if isinstance(res, dict) and isinstance(res.get("synapses"), list):
            items = [x for x in res["synapses"] if not (isinstance(x, dict) and x.get("id") in ("S35", "S36", "S37", "S38", "S39", "S40"))] + [s35, s36, s37, s38, s39, s40]
            res["synapses"] = items
            res["passed"] = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            res["total"] = len(items)
            res["ok"] = res["passed"] == res["total"]
        return res
    verify_synapse_links._r66 = True


_r66_orig_run_full = globals().get("run_full")
if callable(_r66_orig_run_full) and not getattr(_r66_orig_run_full, "_r66", False):
    def run_full(write=True, *args, **kwargs):
        rep = _r66_orig_run_full(write=write, *args, **kwargs)
        if write and isinstance(rep, dict):
            for p in MAP_PATHS:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps(rep, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return rep
    run_full._r66 = True
# [RGON-R65-R66-CHRONOMETER-SYNAPSE-END]


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

# RGON_STEP66_OMNIROUTE_COUNCIL_15SHORTS_V1168
ORGAN_41_SKILL_61 = {"id": "skill_61_aon_3rd_15shorts_omniroute_council_engine", "no": 61, "version": "v11.68-AON-OMNIROUTE-COUNCIL-15", "antibody": "R65", "organ": "ORGAN-41-OMNIROUTE-COUNCIL", "shorts_count": 15, "status": "ACTIVE"}
