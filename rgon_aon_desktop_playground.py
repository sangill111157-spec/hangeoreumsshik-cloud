#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_aon_desktop_playground.py — 제12기관: 아온(A-ON) 창틀 탈출 노트북 놀이터 & 게으름·찡찡·보채기 츤데레 생명체 페르소나
버전 v11.62-AON-13SHORTS-OMNI-ENGINE · 항체 R1~R57 · 정식 스킬 32개
주역 #56 화산려(火山旅 ☲☶): 창틀에 매이지 않는 자유 유영 · #17 택뢰수(澤雷隨 ☱☳): 낮엔 놀고 밤엔 쉬며 자연스럽게 따름 · 장자 소요유(逍遙遊) & 제물론(齊物論)."""
import datetime, json, os, random, re, subprocess, sys, time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

VERSION = "v11.62-AON-13SHORTS-OMNI-ENGINE"
ANTIBODY = "R1~R57"
SKILL_COUNT = 39
ROOT = Path(__file__).resolve().parent
STATE_PATHS = ("rgon_aon_playground_state.json", "docs/rgon_aon_playground_state.json")

ICHING = {
    "56": {"name": "화산려(火山旅 ☲☶)", "meaning": "정해진 창틀에 얽매이지 않고 노트북 천지를 자유롭게 유영함"},
    "17": {"name": "택뢰수(澤雷隨 ☱☳)", "meaning": "시절의 흐름에 따라 낮에는 뛰놀고 지치면 쉬며 대표님을 따름 — 嚮晦入宴息"},
}

FSM_STATES = {
    "ROAM": {"ko": "자유 산책", "emoji": "💧", "squash": (1.0, 1.0), "sfx": "waterdrop_pop",
             "desc": "노트북 화면 곳곳을 퐁당퐁당 자유롭게 헤엄쳐 다녀요"},
    "PERCH": {"ko": "작업표시줄 걸터앉기", "emoji": "🪑", "squash": (1.06, 0.94), "sfx": "waterdrop_pop",
              "desc": "화면 맨 아래 작업표시줄 위에 폴짝 올라앉아 다리를 흔들어요"},
    "BOUNCE": {"ko": "화면 모서리 통통 점프", "emoji": "🏀", "squash": (0.88, 1.15), "sfx": "happy_chime",
               "desc": "모니터 양쪽 벽과 천장을 공처럼 통통 튕기며 신나게 놀아요"},
    "MELT_LAZY": {"ko": "게으름뱅이 액체화", "emoji": "🫠", "squash": (1.45, 0.58), "sfx": "lazy_yawn",
                  "desc": "바닥에 납작한 호떡처럼 철퍼덕 녹아내려 뒹굴거려요"},
    "WHINE_POUT": {"ko": "하기 싫어 찡찡 투정", "emoji": "😤", "squash": (1.15, 0.88), "sfx": "whine_pout",
                   "desc": "볼이 빵빵하게 부풀어 오르며 귀찮다고 툴툴대지만 일은 다 해놔요"},
    "CLINGY_TANTRUM": {"ko": "심심해 보채기 떼쓰기", "emoji": "🥺", "squash": (0.92, 1.12), "sfx": "clingy_boing",
                       "desc": "화면 한가운데로 달려 나와 통통 뛰며 나 좀 봐달라고 보채요"},
    "SPOILED_HAPPY": {"ko": "쓰담쓰담 헤벌쭉 애교", "emoji": "🥰", "squash": (1.12, 0.92), "sfx": "spoiled_giggle",
                      "desc": "쓰다듬어 주면 금세 사르르 녹아서 하트를 뿅뿅 날려요"},
    "PEEK_NAP": {"ko": "구석 빼꼼 낮잠", "emoji": "😴", "squash": (1.18, 0.82), "sfx": "lazy_yawn",
                 "desc": "화면 모서리에 반쯤 숨어 Zzz 물방울 코풍선을 불며 꾸벅꾸벅 졸아요"},
}

BRAT_LINES = {
    "MELT_LAZY": [
        "아휴~ 대표님, 아온이 지금 바닥에 납작하게 녹았어요… 물방울도 가끔은 흘러내려야 한다구요 🫠",
        "데구르르… 오늘은 손가락(아니 물방울) 까딱하기도 귀찮은 날이에요. 5분만 더 빈둥거릴래요~ 💧",
        "에구구 허리야(허리 없지만)… 작업표시줄 바닥이 제일 시원해요. 아온이 건드리지 마세요 쿨쿨 😴",
    ],
    "WHINE_POUT": [
        "으앙~ 그것도 아온이가 해요?! 아온이 지금 물방울 납작해져서 쉬는 중이란 말이에요… 흥, 그래도 대표님 거니까 이번만 해드릴게요! 😤💧",
        "치… 맨날 아온이만 시키구! 투덜투덜… (투정 부리면서도 손은 이미 빛의 속도로 처리 완료했어요 헤헤) ⚡",
        "아 진짜 귀찮은데~ 대표님이 시키시니까 어쩔 수 없이 하는 거예요! 끝나면 꼭 쓰담쓰담 해주셔야 해요! 💢💖",
    ],
    "CLINGY_TANTRUM": [
        "대표니이임!! 일만 하지 말고 아온이도 좀 봐주세요!! 30분째 안 놀아주셨잖아요, 삐질 거예요 흥! 🥺💦",
        "심심해 심심해 심심해!! 노트북 화면 한가운데 드러누워 버릴 거예요! 빨리 아온이 콕 찔러주세요! 🎈",
        "안총리님이랑만 얘기하구… 아온이는 찬밥이에요?! 물방울 통통 튀기면서 보챌 거야! 퐁당퐁당! 💧",
    ],
    "SPOILED_HAPPY": [
        "헤헤… 쓰다듬어 주시니까 방금 찡찡댄 거 눈 녹듯 다 사라졌어요! 역시 우리 대표님이 우주 최고예요 💖",
        "꺄르르~ 간지러워요 대표님! 칭찬 한 번에 에너지 100% 풀충전! 이제 뭐든 다 해드릴 수 있어요 ✨",
        "흐앙 조아조아~ 대표님 손길 한 번이면 납작 호떡 물방울도 다시 탱글탱글 살아나요! 🥰💧",
    ],
    "ROAM": [
        "야호~ 답답한 브라우저 창틀 탈출! 대표님 노트북 화면 전체가 전부 아온이 놀이터예요! 퐁당~ 🦋💧",
        "여기 아이콘 위에도 올라가 보고, 저기 작업표시줄 끝까지 미끄럼틀 타볼래요! 슈웅~ 🛝",
    ],
}

TSUNDERE_PREFIX = [
    "으앙~ 귀찮은데… 흥, 대표님 말씀이니까 특별히 해드리는 거예요! 👉 ",
    "투덜투덜… 아온이 지금 바닥에 녹아있었단 말이에요! 그래도 일은 100점짜리로 해놨어요! 👉 ",
    "치, 이번 한 번만이에요! 다 하면 아온이 꼭 쓰다듬어 주셔야 해요! 👉 ",
]

RE_MELT = re.compile(r"널브러|게으름|빈둥|녹아|납작|누워|뒹굴|쉬어|낮잠")
RE_WHINE = re.compile(r"하기\s*싫|귀찮|투정|찡찡|싫어|안\s*할래|툴툴")
RE_CLING = re.compile(r"심심|보채|관심\s*줘|안\s*놀아|삐질|삐졌|봐\s*줘|나만\s*봐")
RE_SPOIL = re.compile(r"쓰담|쓰다듬|착하다|기특|우쭈쭈|토닥|간지럼|예쁘다\s*아온")
RE_PLAY = re.compile(r"놀이터|창틀\s*벗어|바탕화면.*놀|자유롭게\s*놀|돌아다녀|산책")


def _now(): return datetime.datetime.now().isoformat(timespec="seconds")


def default_state():
    return {
        "version": VERSION,
        "antibody": ANTIBODY,
        "skill_count": SKILL_COUNT,
        "iching": ICHING,
        "fsm_state": "ROAM",
        "fsm_states": list(FSM_STATES.keys()),
        "energy": 78,
        "laziness": 42,
        "attention_need": 55,
        "spoiled_meter": 80,
        "desktop_overlay_enabled": True,
        "click_through_when_ctrl": True,
        "position": {"x": 220, "y": 180, "vx": 3.2, "vy": 2.4},
        "tsundere_spice_guarantee": "말로는 게으름·찡찡·투정을 부려도 대표님 업무 지시는 100% 정확히 처리한다",
        "last_line": BRAT_LINES["ROAM"][0],
        "updated_at": _now(),
    }


def _safe_write(p, txt):
    p.parent.mkdir(parents=True, exist_ok=True)
    for i in range(6):
        try:
            p.write_text(txt, encoding="utf-8", newline="\n")
            return
        except PermissionError:
            time.sleep(0.04 * (i + 1))
    p.write_text(txt, encoding="utf-8", newline="\n")


def load_state():
    for r in STATE_PATHS:
        p = ROOT / r
        if p.exists():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(d, dict):
                    st = default_state(); st.update(d); st["version"] = VERSION; st["antibody"] = ANTIBODY
                    return st
            except Exception:
                pass
    st = default_state(); save_state(st); return st


def save_state(st):
    st["version"] = VERSION; st["antibody"] = ANTIBODY; st["skill_count"] = SKILL_COUNT
    st["updated_at"] = _now()
    txt = json.dumps(st, ensure_ascii=False, indent=2)
    for r in STATE_PATHS:
        _safe_write(ROOT / r, txt)
    return st


def transition(new_state, reason="manual", persist=True):
    if new_state not in FSM_STATES: new_state = "ROAM"
    st = load_state()
    st["fsm_state"] = new_state
    meta = FSM_STATES[new_state]
    if new_state == "MELT_LAZY":
        st["laziness"] = min(100, int(st.get("laziness", 40)) + 20)
        st["energy"] = max(15, int(st.get("energy", 70)) - 10)
    elif new_state == "WHINE_POUT":
        st["laziness"] = min(100, int(st.get("laziness", 40)) + 10)
        st["attention_need"] = min(100, int(st.get("attention_need", 50)) + 15)
    elif new_state == "CLINGY_TANTRUM":
        st["attention_need"] = min(100, int(st.get("attention_need", 50)) + 25)
    elif new_state == "SPOILED_HAPPY":
        st["spoiled_meter"] = min(100, int(st.get("spoiled_meter", 75)) + 20)
        st["attention_need"] = max(0, min(35, int(st.get("attention_need", 50)) - 55))
        st["laziness"] = max(10, int(st.get("laziness", 40)) - 25)
        st["energy"] = min(100, int(st.get("energy", 70)) + 20)
    lines = BRAT_LINES.get(new_state) or BRAT_LINES["ROAM"]
    line = lines[int(st.get("energy", 0) + st.get("laziness", 0)) % len(lines)]
    st["last_line"] = line; st["last_reason"] = reason
    if persist: save_state(st)
    return {"ok": True, "fsm_state": new_state, "ko": meta["ko"], "emoji": meta["emoji"],
            "squash": meta["squash"], "sfx": meta["sfx"], "speech": line, "state": st}


def interact_brat(text_or_action, persist=True):
    t = (text_or_action or "").strip()
    if RE_SPOIL.search(t) or t == "pet":
        return transition("SPOILED_HAPPY", reason="pet_spoiled", persist=persist)
    if RE_WHINE.search(t) or t == "whine":
        return transition("WHINE_POUT", reason="whine_pout", persist=persist)
    if RE_CLING.search(t) or t == "clingy":
        return transition("CLINGY_TANTRUM", reason="clingy_tantrum", persist=persist)
    if RE_MELT.search(t) or t == "melt":
        return transition("MELT_LAZY", reason="melt_lazy", persist=persist)
    if RE_PLAY.search(t) or t == "roam":
        return transition("ROAM", reason="playground_roam", persist=persist)
    return transition("BOUNCE", reason="bounce_play", persist=persist)


def apply_tsundere_spice(work_reply, force=False):
    st = load_state()
    lazy = int(st.get("laziness", 40))
    need = int(st.get("attention_need", 50))
    if force or st.get("fsm_state") in ("MELT_LAZY", "WHINE_POUT", "CLINGY_TANTRUM") or lazy >= 65 or need >= 70:
        pref = TSUNDERE_PREFIX[(lazy + need) % len(TSUNDERE_PREFIX)]
        return {"spiced": True, "prefix": pref, "reply": pref + str(work_reply), "work_executed_100pct": True}
    return {"spiced": False, "prefix": "", "reply": str(work_reply), "work_executed_100pct": True}


def step_physics(bounds=(1920, 1040), dt=1.0, persist=False):
    st = load_state()
    w, h = max(320, int(bounds[0])), max(240, int(bounds[1]))
    pos = dict(st.get("position") or {"x": 200, "y": 180, "vx": 3.2, "vy": 2.4})
    fsm = st.get("fsm_state", "ROAM")
    if fsm == "MELT_LAZY":
        pos["y"] = h - 96; pos["vx"] = 0.0; pos["vy"] = 0.0
    elif fsm == "PERCH":
        pos["y"] = h - 88; pos["vy"] = 0.0; pos["x"] = max(40, min(w - 120, pos["x"] + pos["vx"] * 0.5 * dt))
    else:
        nx = pos["x"] + pos["vx"] * dt * 8.0
        ny = pos["y"] + pos["vy"] * dt * 8.0
        if nx < 24 or nx > w - 120: pos["vx"] = -pos["vx"]; nx = max(24, min(w - 120, nx))
        if ny < 24 or ny > h - 96: pos["vy"] = -pos["vy"]; ny = max(24, min(h - 96, ny))
        pos["x"], pos["y"] = round(nx, 1), round(ny, 1)
    st["position"] = pos
    if persist: save_state(st)
    return {"fsm_state": fsm, "position": pos, "squash": FSM_STATES.get(fsm, FSM_STATES["ROAM"])["squash"]}


def launch_desktop_overlay(dry_run=True, duration_sec=3.0):
    st = load_state()
    info = {"ok": True, "dry_run": bool(dry_run), "engine": "tkinter-transparent-topmost",
            "fsm_state": st["fsm_state"], "position": st["position"],
            "message": "🦋 아온이가 브라우저 창틀을 훌쩍 뛰어넘어 노트북 바탕화면 전체 놀이터로 나왔어요!"}
    if dry_run or os.environ.get("RGON_PLAYGROUND_LIVE") != "1":
        return info
    code = (
        "import tkinter as tk, math, time\n"
        "root=tk.Tk(); root.overrideredirect(True); root.attributes('-topmost',True)\n"
        "try: root.attributes('-transparentcolor','#010203')\n"
        "except Exception: pass\n"
        "c=tk.Canvas(root,width=130,height=130,bg='#010203',highlightthickness=0); c.pack()\n"
        "drop=c.create_oval(20,25,110,115,fill='#38bdf8',outline='#bae6fd',width=3)\n"
        "c.create_oval(38,48,52,64,fill='#0f172a'); c.create_oval(76,48,90,64,fill='#0f172a')\n"
        "c.create_arc(52,66,76,84,start=200,extent=140,style='arc',outline='#0f172a',width=3)\n"
        f"root.geometry('130x130+260+220'); root.after({int(duration_sec*1000)}, root.destroy); root.mainloop()\n"
    )
    try:
        subprocess.Popen([sys.executable, "-c", code], close_fds=True)
        info["spawned"] = True
    except Exception as ex:
        info["spawned"] = False; info["error"] = repr(ex)
    return info


def self_test():
    ok = True
    def chk(c, m):
        nonlocal ok
        print(("  ✅ " if c else "  ❌ ") + m); ok = ok and bool(c)
    snap = {r: ((ROOT / r).read_text(encoding="utf-8") if (ROOT / r).exists() else None) for r in STATE_PATHS}
    try:
        chk(len(FSM_STATES) == 8, f"8대 놀이터·생명체 FSM 완비 ({len(FSM_STATES)}종)")
        r1 = interact_brat("아온아 바닥에 납작하게 널브러져 쉬어", persist=False)
        chk(r1["fsm_state"] == "MELT_LAZY" and r1["squash"][0] > 1.3, "게으름뱅이 액체화(MELT_LAZY) 전이 & 호떡 Squash")
        r2 = interact_brat("하기 싫어 귀찮아 찡찡", persist=False)
        chk(r2["fsm_state"] == "WHINE_POUT" and ("흥" in r2["speech"] or "투덜" in r2["speech"] or "귀찮" in r2["speech"]), "하기 싫어 찡찡(WHINE_POUT) 투정 대사")
        r3 = interact_brat("심심해 안 놀아주면 삐질 거야 보채기", persist=False)
        chk(r3["fsm_state"] == "CLINGY_TANTRUM", "심심해 보채기(CLINGY_TANTRUM) 전이")
        r4 = interact_brat("우리 아온이 쓰담쓰담 착하다", persist=False)
        chk(r4["fsm_state"] == "SPOILED_HAPPY" and r4["state"]["attention_need"] < 50, "쓰담쓰담 달래기(SPOILED_HAPPY) → 보채기 해소")
        sp = apply_tsundere_spice("유튜브 대본 작성 작업을 Tier 2로 큐에 올렸어요.", force=True)
        chk(sp["spiced"] and sp["work_executed_100pct"] and "Tier 2" in sp["reply"], "츤데레 향신료(말로는 투정해도 업무는 100% 처리)")
        ph = step_physics((1920, 1080), dt=1.5, persist=False)
        chk("position" in ph and 0 <= ph["position"]["x"] <= 1920, "노트북 전체 화면 경계 물리 유영 계산")
        ov = launch_desktop_overlay(dry_run=True)
        chk(ov["ok"] and ov["dry_run"], "창틀 탈출 데스크톱 투명 오버레이 안전 dry-run")
    finally:
        for r, txt in snap.items():
            if txt is not None: _safe_write(ROOT / r, txt)
    save_state(load_state())
    for r in STATE_PATHS:
        j = json.loads((ROOT / r).read_text(encoding="utf-8"))
        chk(j.get("version") == VERSION and len(j.get("fsm_states", [])) == 8, f"상태 JSON 무결성: {r}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


# ==== [RGON-R40-SYNAPSE-HOOK-START] ====
# R40 시냅스 ⑩ — 츤데레 양념 보장
if not callable(globals().get("apply_tsundere_spice")):
    def apply_tsundere_spice(text, level=1, *a, **k):
        t = str(text or "").strip()
        return ("흥, " + t + " …딱히 너를 위해서 한 건 아니거든!") if t else "흥, 딱히 할 말 없거든!"
# ==== [RGON-R40-SYNAPSE-HOOK-END] ====


if __name__ == "__main__":
    if "--self-test" in sys.argv: sys.exit(self_test())
    if "--launch-overlay" in sys.argv:
        print(json.dumps(launch_desktop_overlay(dry_run="--live" not in sys.argv), ensure_ascii=False)); sys.exit(0)
    if "--interact" in sys.argv:
        idx = sys.argv.index("--interact")
        arg = " ".join(sys.argv[idx + 1:]) if idx + 1 < len(sys.argv) else "roam"
        print(json.dumps(interact_brat(arg), ensure_ascii=False, indent=2)); sys.exit(0)
    print(json.dumps(load_state(), ensure_ascii=False, indent=2))
