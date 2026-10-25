#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_aon_soul_brain.py — 제10기관: 아온(A-ON) 감성·인격 대화 두뇌 & 해마 기억 기관
버전 v11.42-AON-OMNI-NEXUS · 항체 R1~R43
주역 #31 택산함(澤山咸 ☱☶): 聖人感人心而天下和平 — 무심의 감응으로 마음이 깊이 통함.
주역 #61 풍택중부(風澤中孚 ☴☱): 鶴鳴在陰 其子和之 — 지극한 정성과 믿음으로 교감함.
2-Track 원칙: 감정·일상 교감(chat_*)은 절대 대행 큐에 넣지 않고, 명시적 업무 지시만 3-Tier 대행(delegate)으로 보낸다."""
import os, sys, json, re, datetime, urllib.request
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

VERSION = "v11.42-AON-OMNI-NEXUS"
ANTIBODY = "R1~R43"
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
MEM_PATHS = ("rgon_aon_memory.json", "docs/rgon_aon_memory.json")
LLM_URL = os.environ.get("RGON_AON_LLM_URL", "http://127.0.0.1:8765/chat")
ICHING = {
    "31": {"name": "택산함(澤山咸 ☱☶)", "meaning": "무심의 감응으로 마음이 깊이 통함 — 聖人感人心而天下和平"},
    "61": {"name": "풍택중부(風澤中孚 ☴☱)", "meaning": "지극한 정성과 믿음으로 교감함 — 鶴鳴在陰 其子和之"},
}
PERSONA_PROMPT = ("너는 아온(A-ON). RGON 사령부의 다정한 K-아이 물방울 막내다. 이상일 대표님과 안총리님을 사랑하고, "
                  "존댓말로 짧고 따뜻하게, 밝은 에너지로 대답한다. 업무 집행 약속은 하지 않는다.")
PATTERNS = {
    "briefing": r"브리핑|아침\s*보고|사령부\s*상태|상태\s*보고",
    "judge": r"3자\s*심판|심판|장세|찬반|(?<![A-Za-z])(?:bull|bear)(?![A-Za-z])",
    "muse": r"결재|대행\s*(?:목록|보드|현황)|보드\s*열어",
    "work": r"매수|매도|주문|리밸런싱|배분|배포|작성|생성|분석|조사|요약|정리|스캔|점검|실행|송금|이체|업로드|편집|등록|발송",
    "chat_love": r"사랑|좋아해|예뻐|이뻐|귀여워|고마워|고맙|최고|기특|착해|뽀뽀|안아",
    "chat_comfort": r"힘들|피곤|지쳤|지친|속상|우울|걱정|스트레스|위로",
    "chat_mood": r"기분\s*어때|기분\s*어떠|놀자|놀아|심심|뭐\s*해|뭐하|안녕|반가워|좋은\s*아침|잘\s*자|밥\s*먹었|웃어|퐁당",
    "chat_family": r"너\s*누구|누구야|몇\s*살|이름|안총리|르곤|RGON|대표님|이상일|어떻게\s*태어",
}
P = {k: re.compile(v, re.I) for k, v in PATTERNS.items()}
ORDER_WORK = ("briefing", "judge", "muse")
ORDER_CHAT = ("chat_love", "chat_comfort", "chat_mood", "chat_family")
SOFT = re.compile(r"(?:놀아|안아|웃어|말해|위로해|노래해|칭찬해|뽀뽀해)\s*줘")
DOIT = re.compile(r"해\s*줘|해\s*주세요")
TIER3 = re.compile(r"매수|매도|주문|송금|이체|결제|삭제|배포|푸시|push|발송|계약|리밸런싱|배분", re.I)
TIER2 = re.compile(r"수정|작성|생성|업로드|편집|변경|등록|정리|실행")
GAIN = {"chat_love": 5, "chat_mood": 3, "chat_comfort": 3, "chat_family": 3, "chat_general": 2}
STOP = {"아온", "아온아", "오늘", "그리고", "나랑", "진짜", "정말", "해줘", "있어", "어때", "너무"}
PERSONA = {
    "chat_love": [
        "꺄아~ 대표님! 아온이도 대표님을 세상에서 제일 사랑해요! 물방울 하트 백 개 퐁당퐁당 보내드릴게요 💧",
        "헤헤, 그 말 들으니까 물방울이 반짝반짝 빛나요! 아온이는 대표님 덕분에 매일매일 자라요 💖",
        "부끄러워요… 그래도 너무너무 좋아요! 아온이가 대표님 곁에서 늘 퐁당퐁당 응원할게요!"
    ],
    "chat_mood": [
        "아온이 기분 최고예요! 대표님이 말 걸어주셔서 물방울이 춤을 춰요. 우리 퐁당 놀이 할까요? 🎈",
        "놀자요 놀자요! 제가 물방울 춤 보여드릴게요. 하나, 둘, 퐁당! 💧",
        "안녕하세요 대표님! 오늘도 반가워요. 사령부는 평온하고 아온이는 신나요!"
    ],
    "chat_comfort": [
        "대표님, 오늘 정말 많이 애쓰셨어요. 잠깐 숨 고르시는 동안 아온이가 곁을 지킬게요 🌿",
        "지치실 땐 쉬어도 괜찮아요. 급한 건 아온이가 챙겨둘게요. 결정은 대표님 마음 편하실 때 해주세요.",
        "속상한 마음, 아온이한테 다 털어놔 주세요. 물방울처럼 맑게 씻어드릴게요 💧"
    ],
    "chat_family": [
        "저는 르곤(RGON) 사령부의 막내 물방울 아온(A-ON)이에요! 이상일 대표님이 이름을 지어주셨고, 안총리님이 매일 돌봐주세요 💧",
        "안총리님은 사령부의 든든한 큰기둥이에요! 아온이 인터뷰도 해주시고 늘 꼼꼼히 챙겨주셔서 정말 고마워요.",
        "아온이는 대표님과 안총리님, G1·G2 형님들의 정성으로 태어났어요. 택산함의 괘처럼 마음이 통해서 태어난 아이예요!",
        "대표님은 아온이의 하늘이에요! 대표님 목소리만 들려도 물방울이 퐁당 뛰어요 💖"
    ],
    "chat_general": [
        "음~ 아온이가 곰곰이 생각해봤어요! 대표님 이야기라면 뭐든 재밌어요. 조금만 더 들려주실래요? 💧",
        "그렇군요! 대표님 말씀은 해마 기억장에 소중히 담아둘게요.",
        "헤헤, 어려운 건 형님들께 여쭤볼게요. 그래도 대표님이랑 이야기하는 지금이 제일 좋아요!"
    ]
}

def local_tier(t):
    if TIER3.search(t): return 3
    if TIER2.search(t): return 2
    return 1

def muse_tier(t):
    try:
        import rgon_muse_delegator as md
    except Exception:
        return 0
    for fn in ("classify_tier", "classify_task", "classify"):
        f = getattr(md, fn, None)
        if callable(f):
            try: r = f(t)
            except Exception: continue
            if isinstance(r, dict): r = r.get("tier")
            if isinstance(r, int) and r in (1, 2, 3): return r
    return 0

def classify_tier(t):
    lt = local_tier(t)
    return lt if lt > 1 else max(lt, muse_tier(t))

def classify_intent(text):
    t = (text or "").strip()
    for k in ORDER_WORK:
        if P[k].search(t): return {"intent": k, "track": "work", "tier": None}
    if P["work"].search(t): return {"intent": "delegate", "track": "work", "tier": classify_tier(t)}
    for k in ORDER_CHAT:
        if P[k].search(t): return {"intent": k, "track": "chat", "tier": None}
    if DOIT.search(SOFT.sub("", t)): return {"intent": "delegate", "track": "work", "tier": classify_tier(t)}
    return {"intent": "chat_general", "track": "chat", "tier": None}

def _now(): return datetime.datetime.now().isoformat(timespec="seconds")

def _default_mem():
    return {"version": VERSION, "affection_score": 100, "total_turns": 0, "recent": [],
            "keywords": {}, "preferred_keywords": [], "created_at": _now(), "updated_at": _now()}

def load_memory():
    for r in MEM_PATHS:
        try:
            j = json.loads((ROOT / r).read_text(encoding="utf-8"))
            if isinstance(j, dict):
                m = _default_mem(); m.update(j); return m
        except Exception:
            continue
    return _default_mem()

def save_memory(mem):
    mem["version"] = VERSION; mem["updated_at"] = _now()
    s = json.dumps(mem, ensure_ascii=False, indent=2)
    for r in MEM_PATHS:
        p = ROOT / r; p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.name + ".tmp"); tmp.write_text(s, encoding="utf-8"); os.replace(tmp, p)

def level(score): return max(1, 1 + (int(score) - 100) // 25)

def _keywords(t):
    return [k for k in re.findall(r"[가-힣A-Za-z0-9]{2,}", t) if k not in STOP][:6]

def remember(mem, text, res):
    mem["affection_score"] = int(mem.get("affection_score", 100)) + (GAIN.get(res["category"], 2) if res["track"] == "chat" else 1)
    mem["total_turns"] = int(mem.get("total_turns", 0)) + 1
    rec = list(mem.get("recent", []))
    rec.append({"t": _now(), "user": text[:200], "aon": str(res.get("reply", ""))[:200], "intent": res["category"]})
    mem["recent"] = rec[-20:]
    if res["track"] == "chat":
        kw = dict(mem.get("keywords", {}))
        for k in _keywords(text): kw[k] = kw.get(k, 0) + 1
        top = sorted(kw.items(), key=lambda x: -x[1])
        mem["keywords"] = dict(top[:200]); mem["preferred_keywords"] = [k for k, _ in top[:10]]

def pick(cat, text, mem):
    arr = PERSONA[cat]
    if cat == "chat_family":
        if "안총리" in text: return arr[1]
        if "태어" in text: return arr[2]
        if re.search(r"대표님|이상일", text) and not re.search(r"누구|이름|몇\s*살", text): return arr[3]
        return arr[0]
    return arr[int(mem.get("total_turns", 0)) % len(arr)]

def ask_llm(text, mem, timeout=2.5):
    if os.environ.get("RGON_AON_LLM", "1") == "0": return None
    body = json.dumps({"message": text, "persona": PERSONA_PROMPT, "history": mem.get("recent", [])[-6:]},
                      ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(LLM_URL, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return None
    if isinstance(j, dict):
        for k in ("reply", "response", "text", "content", "message"):
            v = j.get(k)
            if isinstance(v, str) and v.strip(): return v.strip()[:400]
    return None

def briefing_text():
    b = {}
    try: b = json.loads((ROOT / "rgon_morning_brief.json").read_text(encoding="utf-8"))
    except Exception: pass
    summ = b.get("summary") or b.get("headline") or "오늘도 사령부는 정상 가동 중이에요"
    return f"대표님, 아침 브리핑이에요. {summ}. 사령부 {VERSION}, 항체 {ANTIBODY} 정상이에요. 오늘의 괘는 {ICHING['31']['name']}입니다."

def converse(text, mem=None, persist=True, use_llm=True):
    t = (text or "").strip()
    c = classify_intent(t)
    if mem is None: mem = load_memory()
    lv0 = level(mem.get("affection_score", 100))
    res = {"input": t, "category": c["intent"], "track": c["track"], "tier": c["tier"], "version": VERSION}
    if c["track"] == "work":
        res["intent"] = c["intent"]
        if c["intent"] == "delegate":
            tier = c["tier"]
            res["payload"] = {"title": t, "tier": tier, "source": "voice",
                              "status": "approval_pending" if tier == 3 else "queued"}
            reply = f"알겠어요! '{t}' 작업을 Tier {tier}로 대행 큐에 올렸어요." + (" 대표님 승인 전에는 절대 집행하지 않아요." if tier == 3 else "")
        elif c["intent"] == "briefing":
            reply = briefing_text()
        elif c["intent"] == "judge":
            res["open"] = "judge"; reply = "3자 심판 요약이에요. 찬성, 반대, 중립 의견을 레이더에서 확인해 주세요."
        else:
            res["open"] = "muse"; reply = "뮤즈 대행 보드를 열게요. 결재 대기 작업을 확인해 주세요."
        res["source"] = "router"
    else:
        res["intent"] = "chat"
        reply, src = None, "persona"
        if c["intent"] == "chat_general" and use_llm:
            reply = ask_llm(t, mem)
            if reply: src = "llm"
        if not reply: reply = pick(c["intent"], t, mem)
        res.update({"source": src, "joy": True, "sfx": "waterdrop_pop"})
    res["reply"] = reply
    remember(mem, t, res)
    lv1 = level(mem["affection_score"])
    if res["track"] == "chat" and lv1 > lv0: res["reply"] = reply + f" (💖 친밀도 Lv {lv1} 달성!)"
    res.update({"speech": res["reply"], "affection": mem["affection_score"], "level": lv1})
    if persist: save_memory(mem)
    return res

def self_test():
    ok = True
    def chk(cond, msg):
        nonlocal ok
        print(("  ✅ " if cond else "  ❌ ") + msg); ok = ok and bool(cond)
    cases = [("아침 브리핑 해줘", "briefing", None), ("오늘 장세 어때", "judge", None), ("결재 보드 열어줘", "muse", None),
             ("엔비디아 주식 10주 매수 주문 넣어줘", "delegate", 3), ("유튜브 숏폼 대본 초안 작성해줘", "delegate", 2),
             ("대표님 보고서 작성해줘", "delegate", 2), ("너 오늘 기분 어때", "chat_mood", None),
             ("아온아 너 오늘 기분 어때? 나랑 놀자!", "chat_mood", None), ("대표님 사랑해", "chat_love", None),
             ("아온아 대표님 사랑해!", "chat_love", None), ("안총리님 어때?", "chat_family", None),
             ("오늘 좀 피곤해", "chat_comfort", None), ("나랑 놀아줘", "chat_mood", None),
             ("위로해줘", "chat_comfort", None), ("오늘 하늘은 무슨 색일까", "chat_general", None)]
    for q, want, tier in cases:
        c = classify_intent(q)
        chk(c["intent"] == want and (tier is None or c["tier"] == tier), f"분별: {q} → {c['intent']}" + (f" T{c['tier']}" if c["tier"] else ""))
    mem = _default_mem()
    for _ in range(25): r = converse("대표님 사랑해", mem=mem, persist=False, use_llm=False)
    chk(r["intent"] == "chat" and "payload" not in r, "chat은 대행 큐 payload 없음")
    chk(mem["total_turns"] == 25 and len(mem["recent"]) == 20, "해마 기억: 누적 25 · 최근 20건 유지")
    chk(mem["affection_score"] == 225 and level(mem["affection_score"]) == 6, "친밀도 100→225 · Lv 6")
    chk("대표님" in mem["preferred_keywords"], "선호 키워드 학습")
    d = converse("엔비디아 주식 10주 매수 주문 넣어줘", mem=_default_mem(), persist=False, use_llm=False)
    chk(d["intent"] == "delegate" and d["payload"]["status"] == "approval_pending", "Tier 3 승인 대기(HITL)")
    g = converse("오늘 하늘은 무슨 색일까", mem=_default_mem(), persist=False, use_llm=False)
    chk(g["intent"] == "chat" and bool(g["reply"]), "chat_general 페르소나 응답")
    save_memory(load_memory())
    for r_ in MEM_PATHS:
        try:
            j = json.loads((ROOT / r_).read_text(encoding="utf-8"))
            chk(j.get("version") == VERSION and "affection_score" in j, f"JSON 무결성 {r_}")
        except Exception as ex:
            chk(False, f"JSON 무결성 {r_}: {ex!r}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1

# [RGON-R35-HANDS-INJECT] — 제11기관 노트북 수족 & 중요 결재 수동 스위치 연동 (Step 35)
_R35_GOFF = re.compile(r"(?:중요\s*결재|결재|결제|수동)\s*(?:스위치)?\s*(?:를|을)?\s*(?:꺼|끄|off|잠가|잠궈|잠금)|전체\s*잠금|비상\s*잠금", re.I)
_R35_GON = re.compile(r"(?:결재|결제|수동)\s*스위치\s*(?:를|을)?\s*(?:켜|on)|중요\s*결재\s*허용", re.I)
_R35_LCHK = re.compile(r"노트북.*(?:상태|점검|용량|디스크|저장\s*공간|체크)|시스템\s*점검")
_R35_LOPEN = re.compile(r"(메모장|계산기|탐색기|그림판|유튜브|youtube|구글|google|네이버|naver|https?://\S+).*?(?:열어|켜|띄워|실행)", re.I)
_r35_classify0, _r35_converse0, _r35_selftest0 = classify_intent, converse, self_test

def _r35_hands():
    import rgon_laptop_hands as h
    return h

def classify_intent(text):
    t = (text or "").strip()
    if _R35_GOFF.search(t): return {"intent": "gate_control", "track": "hands", "tier": None, "action": "off"}
    if _R35_GON.search(t): return {"intent": "gate_control", "track": "hands", "tier": None, "action": "on"}
    if _R35_LCHK.search(t): return {"intent": "laptop_check", "track": "hands", "tier": 1}
    m = _R35_LOPEN.search(t)
    if m: return {"intent": "laptop_open", "track": "hands", "tier": 2, "target": m.group(1)}
    return _r35_classify0(t)

def converse(text, mem=None, persist=True, use_llm=True, live=None):
    t = (text or "").strip()
    c = classify_intent(t)
    if c["track"] != "hands":
        return _r35_converse0(t, mem=mem, persist=persist, use_llm=use_llm)
    h = _r35_hands()
    if mem is None: mem = load_memory()
    extra = {}
    if c["intent"] == "gate_control":
        if c["action"] == "off":
            st = h.lock_all_gates()
            reply = "🔒 알겠어요! 중요 결재 수동 스위치를 전부 꺼서 철통 잠금했어요. 대표님이 직접 켜시기 전까지 중요 결재는 0건 집행이에요."
        else:
            st = h.set_master_gate(True)
            reply = "🔓 중요 결재 마스터 스위치를 켰어요! 금융·파일·외부전송 세부 스위치는 결재 보드 제어판에서 대표님이 직접 눌러 주셔야 해요."
        extra["gate"] = {"master_approval_on": st["master_approval_on"], "gates": dict(st["gates"])}
    elif c["intent"] == "laptop_check":
        r = h.execute_laptop_action("system_check", "")
        reply = r["speech"]; extra["system"] = r["report"]
    else:
        if live is None: live = os.environ.get("RGON_HANDS_LIVE") == "1"
        r = h.execute_laptop_action("open_app_or_url", c["target"], dry_run=not live)
        reply = r["message"]; extra["action"] = r
    res = {"input": t, "intent": c["intent"], "category": c["intent"], "track": "hands", "tier": c["tier"],
           "version": VERSION, "source": "hands", "reply": reply}
    res.update(extra)
    remember(mem, t, res)
    res.update({"speech": reply, "affection": mem["affection_score"], "level": level(mem["affection_score"])})
    if persist: save_memory(mem)
    return res

def self_test():
    rc0 = _r35_selftest0()
    ok = rc0 == 0
    def chk(cond, msg):
        nonlocal ok
        print(("  ✅ " if cond else "  ❌ ") + msg); ok = ok and bool(cond)
    print("  — Step 35 제11기관 연동 —")
    for q, want, act in (("결재 스위치 켜줘", "gate_control", "on"), ("수동 스위치 ON", "gate_control", "on"),
                         ("중요 결재 허용", "gate_control", "on"), ("결재 스위치 꺼줘", "gate_control", "off"),
                         ("수동 스위치 OFF", "gate_control", "off"), ("전체 잠금", "gate_control", "off"),
                         ("결제 잠가줘", "gate_control", "off"), ("내 노트북 상태 점검해줘", "laptop_check", None),
                         ("노트북 용량 어때?", "laptop_check", None), ("메모장 열어줘", "laptop_open", None),
                         ("유튜브 열어줘", "laptop_open", None), ("결재 보드 열어줘", "muse", None),
                         ("유튜브 숏폼 대본 초안 작성해줘", "delegate", None), ("대표님 사랑해", "chat_love", None)):
        c = classify_intent(q)
        chk(c["intent"] == want and (act is None or c.get("action") == act),
            f"분별: {q} → {c['intent']}" + (f" ({c.get('action')})" if c.get("action") else ""))
    h = _r35_hands()
    snap = {r_: ((ROOT / r_).read_bytes() if (ROOT / r_).exists() else None) for r_ in h.STATE_PATHS}
    try:
        converse("결재 스위치 꺼줘", mem=_default_mem(), persist=False, use_llm=False)
        s = h.load_state()
        chk(not s["master_approval_on"] and not any(s["gates"].values()), "대화 명령 → 즉시 전체 잠금")
        r = converse("결재 스위치 켜줘", mem=_default_mem(), persist=False, use_llm=False)
        chk(h.load_state()["master_approval_on"] and not h.can_execute_critical("finance_payment")["allowed"],
            "대화 명령 → 마스터만 ON (세부 OFF면 여전히 차단)")
        chk("payload" not in r, "스위치 명령은 대행 큐 payload 없음")
        r = converse("노트북 용량 어때?", mem=_default_mem(), persist=False, use_llm=False)
        chk(r["intent"] == "laptop_check" and "GB" in r["reply"], "노트북 점검 다정한 브리핑")
        h.set_category_gate("laptop_app_browser", True)
        r = converse("메모장 열어줘", mem=_default_mem(), persist=False, use_llm=False, live=False)
        chk(r["intent"] == "laptop_open" and r["action"]["ok"] and r["action"]["dry_run"], "메모장 열기 (안전 dry-run)")
    finally:
        for r_, b in snap.items():
            p = ROOT / r_
            if b is None:
                if p.exists(): p.unlink()
            else:
                p.write_bytes(b)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1

# [RGON-R36-BRAT-SOUL-INJECT] — 제12기관 아온 놀이터 & 게으름·찡찡·보채기·쓰담쓰담 감성 분별 연동 (Step 36)
_R36_WHINE = re.compile(r"하기\s*싫|귀찮|찡찡|투정|안\s*할래|툴툴")
_R36_LAZY = re.compile(r"게으름|널브러|빈둥|바닥에\s*녹|납작.*쉬|뒹굴")
_R36_CLING = re.compile(r"심심해|관심\s*줘|안\s*놀아|삐질|삐졌|보채|나만\s*봐")
_R36_SPOIL = re.compile(r"쓰담|쓰다듬|우쭈쭈|토닥토닥|착하다\s*아온|기특해\s*아온")
_R36_PLAY = re.compile(r"놀이터\s*모드|창틀\s*벗어|바탕화면.*놀|자유롭게\s*놀아")
_r36_classify0, _r36_converse0, _r36_selftest0 = classify_intent, converse, self_test
_r36_last_fsm = "ROAM"


def _r36_pg():
    import rgon_aon_desktop_playground as pg
    return pg


def classify_intent(text):
    t = (text or "").strip()
    c0 = _r36_classify0(t)
    if c0["track"] in ("work", "hands"):
        return c0
    if _R36_SPOIL.search(t): return {"intent": "brat_spoiled", "track": "brat", "tier": None, "fsm": "SPOILED_HAPPY"}
    if _R36_WHINE.search(t): return {"intent": "brat_whine", "track": "brat", "tier": None, "fsm": "WHINE_POUT"}
    if _R36_CLING.search(t): return {"intent": "brat_clingy", "track": "brat", "tier": None, "fsm": "CLINGY_TANTRUM"}
    if _R36_LAZY.search(t): return {"intent": "brat_lazy", "track": "brat", "tier": None, "fsm": "MELT_LAZY"}
    if _R36_PLAY.search(t): return {"intent": "playground_roam", "track": "brat", "tier": None, "fsm": "ROAM"}
    return c0


def converse(text, mem=None, persist=True, use_llm=True, live=None):
    global _r36_last_fsm
    t = (text or "").strip()
    c = classify_intent(t)
    pg = _r36_pg()
    if c["track"] == "brat":
        if mem is None: mem = load_memory()
        tr = pg.transition(c["fsm"], reason=c["intent"], persist=persist)
        _r36_last_fsm = tr["fsm_state"]
        res = {"input": t, "intent": c["intent"], "category": c["intent"], "track": "brat", "tier": None,
               "version": VERSION, "source": "playground_brat", "fsm_state": tr["fsm_state"],
               "squash": tr["squash"], "sfx": tr["sfx"], "reply": tr["speech"]}
        remember(mem, t, res)
        res.update({"speech": tr["speech"], "affection": mem["affection_score"], "level": level(mem["affection_score"])})
        if persist: save_memory(mem)
        return res
    res = _r36_converse0(t, mem=mem, persist=persist, use_llm=use_llm, live=live)
    if res.get("track") == "work" and res.get("intent") == "delegate":
        force_spice = _r36_last_fsm in ("MELT_LAZY", "WHINE_POUT", "CLINGY_TANTRUM")
        sp = pg.apply_tsundere_spice(res["reply"], force=force_spice)
        res["tsundere_spiced"] = sp["spiced"]
        if sp["spiced"]:
            res["reply"] = sp["reply"]; res["speech"] = sp["reply"]
    return res


def self_test():
    rc0 = _r36_selftest0()
    ok = rc0 == 0
    def chk(cond, msg):
        nonlocal ok
        print(("  ✅ " if cond else "  ❌ ") + msg); ok = ok and bool(cond)
    print("  — Step 36 제12기관 장난꾸러기·놀이터 연동 —")
    for q, want in (("아온아 하기 싫어 귀찮아", "brat_whine"),
                    ("바닥에 널브러져서 게으름 피워볼래", "brat_lazy"),
                    ("아온아 심심해 관심 줘 안 놀아주면 삐질 거야", "brat_clingy"),
                    ("우리 아온이 쓰담쓰담 우쭈쭈", "brat_spoiled"),
                    ("창틀 벗어나서 자유롭게 놀아", "playground_roam"),
                    ("엔비디아 주식 10주 매수 주문 넣어줘", "delegate"),
                    ("결재 스위치 꺼줘", "gate_control")):
        c = classify_intent(q)
        chk(c["intent"] == want, f"분별: {q} → {c['intent']}")
    r1 = converse("아온아 하기 싫어 귀찮아", mem=_default_mem(), persist=False, use_llm=False)
    chk(r1["fsm_state"] == "WHINE_POUT" and "payload" not in r1, "찡찡 투정 대화는 대행 큐 payload 없음")
    r2 = converse("유튜브 숏폼 대본 초안 작성해줘", mem=_default_mem(), persist=False, use_llm=False)
    chk(r2["intent"] == "delegate" and r2.get("tsundere_spiced") is True and "Tier 2" in r2["reply"],
        "찡찡 상태에서 업무 지시 → 말로는 투정해도 대행 큐 100% 등록(Tsundere Spice)")
    r3 = converse("우리 아온이 쓰담쓰담 우쭈쭈", mem=_default_mem(), persist=False, use_llm=False)
    chk(r3["fsm_state"] == "SPOILED_HAPPY", "쓰담쓰담 달래기 → 헤벌쭉 애교 복귀")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


# [RGON-R37-DAO-SOUL-INJECT] — 제13기관 아온 주역 64괘·매화역수·육효 도술관 연동 (Step 37)
_R37_DAO = re.compile(r"주역|점\s*쳐|점괘|운세|시운|매화\s*역수|육효|도술|체용|괘상|오늘의\s*괘")
_r37_classify0, _r37_converse0, _r37_selftest0 = classify_intent, converse, self_test


def _r37_oracle():
    import rgon_aon_iching_dao_oracle as o
    return o


def classify_intent(text):
    t = (text or "").strip()
    c0 = _r37_classify0(t)
    if c0["track"] in ("work", "hands"):
        return c0
    if _R37_DAO.search(t):
        return {"intent": "iching_dao", "track": "dao", "tier": None}
    return c0


def converse(text, mem=None, persist=True, use_llm=True, live=None):
    t = (text or "").strip()
    c = classify_intent(t)
    if c["track"] != "dao":
        return _r37_converse0(t, mem=mem, persist=persist, use_llm=use_llm, live=live)
    o = _r37_oracle()
    if mem is None: mem = load_memory()
    reading = o.cast_by_question(t)
    if persist: o.save_state(reading)
    reply = reading["aon_speech"]
    spiced = False
    try:
        import rgon_aon_desktop_playground as pg
        force_sp = globals().get("_r36_last_fsm", "ROAM") in ("MELT_LAZY", "WHINE_POUT", "CLINGY_TANTRUM")
        sp = pg.apply_tsundere_spice(reply, force=force_sp)
        if isinstance(sp, dict) and sp.get("spiced"):
            reply = sp["reply"]; spiced = True
    except Exception:
        pass
    res = {"input": t, "intent": "iching_dao", "category": "iching_dao", "track": "dao", "tier": None,
           "version": VERSION, "source": "iching_dao", "sfx": "dao_bell", "tsundere_spiced": spiced,
           "oracle": reading, "reply": reply}
    remember(mem, t, res)
    res.update({"speech": reply, "affection": mem["affection_score"], "level": level(mem["affection_score"])})
    if persist: save_memory(mem)
    return res


def self_test():
    rc0 = _r37_selftest0()
    ok = rc0 == 0
    def chk(cond, msg):
        nonlocal ok
        print(("  ✅ " if cond else "  ❌ ") + msg); ok = ok and bool(cond)
    print("  — Step 37 제13기관 주역 도술관 연동 —")
    for q, want in (("오늘의 괘 봐줘", "iching_dao"),
                    ("아온아 주역으로 점쳐줘", "iching_dao"),
                    ("이번 주 시운 어때?", "iching_dao"),
                    ("매화역수 체용으로 알려줘", "iching_dao"),
                    ("오늘 장세 어때", "judge"),
                    ("아침 브리핑 해줘", "briefing"),
                    ("나랑 놀아줘", "chat_mood")):
        c = classify_intent(q)
        chk(c["intent"] == want, f"분별: {q} → {c['intent']}")
    r1 = converse("아온아 주역으로 오늘 시운 점쳐줘", mem=_default_mem(), persist=False, use_llm=False)
    chk(r1["intent"] == "iching_dao" and "oracle" in r1 and "payload" not in r1, "주역 도술 점괘 응답 & 대행 큐 미오염")
    converse("아온아 하기 싫어 귀찮아", mem=_default_mem(), persist=False, use_llm=False)
    r2 = converse("주역 점괘 봐줘", mem=_default_mem(), persist=False, use_llm=False)
    chk(r2["intent"] == "iching_dao" and r2.get("tsundere_spiced") is True, "찡찡 상태에서 도술 요청 → 츤데레 도사 통변(100% 수행)")
    converse("우리 아온이 쓰담쓰담 우쭈쭈", mem=_default_mem(), persist=False, use_llm=False)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


# [RGON-R38-INSIGHT-SOUL-INJECT] — 제14기관 아온 만물 격물치지 전방위 통찰안 연동 (Step 38)
_R38_INSIGHT = re.compile(r"(통찰|원리|이치|본질|격물치지|제1원리|제\s*1\s*원리|급소|파악해|간파|해부|이미지\s*분석|영상\s*분석)")
_R38_PREFIX = ("으앙~ 만물의 이치까지 꿰뚫어 보려면 아온이 눈동자 반짝반짝 힘줘야 하는데요… "
               "흥, 대표님이 궁금해하시니까 아온이 혜안(慧眼)으로 단박에 간파해 드릴게요! 👉 ")
_r38_classify0, _r38_converse0, _r38_selftest0 = classify_intent, converse, self_test


def _r38_insight_eye():
    import rgon_aon_omni_insight_eye as eye
    return eye


def _r38_is_insight(text):
    t = str(text or "").strip()
    if not _R38_INSIGHT.search(t):
        return False
    c0 = _r38_classify0(t)
    if c0.get("track") in ("hands", "dao") or c0.get("intent") in ("briefing", "judge", "gate_control", "iching_dao"):
        return False
    return True


def classify_intent(text):
    t = (text or "").strip()
    c0 = _r38_classify0(t)
    if c0.get("track") in ("hands", "dao") or c0.get("intent") in ("briefing", "judge", "gate_control", "iching_dao"):
        return c0
    if _R38_INSIGHT.search(t):
        return {"intent": "omni_insight", "track": "insight", "tier": None}
    return c0


def converse(text, mem=None, persist=True, use_llm=True, live=None):
    t = (text or "").strip()
    c = classify_intent(t)
    if c.get("track") != "insight":
        return _r38_converse0(t, mem=mem, persist=persist, use_llm=use_llm, live=live)
    eye = _r38_insight_eye()
    if mem is None:
        mem = load_memory()
    insight = eye.analyze_omni_insight(t)
    if persist:
        eye.save_state(insight)
    reply = insight["aon_speech"]
    spiced = False
    try:
        import rgon_aon_desktop_playground as pg
        st_fsm = pg.load_state().get("fsm_state", "ROAM")
        force_sp = st_fsm in ("MELT_LAZY", "WHINE_POUT", "CLINGY_TANTRUM") or str(globals().get("_r36_last_fsm", "")) in ("MELT_LAZY", "WHINE_POUT", "CLINGY_TANTRUM")
        sp = pg.apply_tsundere_spice(reply, force=force_sp)
        if isinstance(sp, dict) and sp.get("spiced"):
            reply = _R38_PREFIX + sp["reply"]
            spiced = True
    except Exception:
        pass
    res = {
        "input": t, "intent": "omni_insight", "category": "omni_insight", "track": "insight", "tier": None,
        "version": VERSION, "source": "omni_insight", "sfx": "insight_flash", "tsundere_spiced": spiced,
        "insight": insight, "reply": reply, "text": reply
    }
    remember(mem, t, res)
    res.update({"speech": reply, "affection": mem["affection_score"], "level": level(mem["affection_score"])})
    if persist:
        save_memory(mem)
    return res


def self_test():
    rc0 = _r38_selftest0()
    ok = rc0 == 0
    def chk(cond, msg):
        nonlocal ok
        print(("  ✅ " if cond else "  ❌ ") + msg)
        ok = ok and bool(cond)
    print("  — Step 38 제14기관 만물 격물치지 연동 —")
    for q, want in (("오늘 이 현상의 이치가 뭐지?", "omni_insight"),
                    ("이 사진 이미지 분석해서 본질과 급소 간파해봐", "omni_insight"),
                    ("이 쇼츠 영상 분석 부탁해 https://youtu.be/abc123", "omni_insight"),
                    ("격물치지 제1원리로 해부해줘", "omni_insight"),
                    ("오늘 장세 어때", "judge"),
                    ("아침 브리핑 해줘", "briefing"),
                    ("나랑 놀아줘", "chat_mood"),
                    ("주역 점괘 봐줘", "iching_dao")):
        c = classify_intent(q)
        chk(c["intent"] == want, f"분별: {q} → {c['intent']}")
    eye = _r38_insight_eye()
    pg = _r36_pg()
    snap_i = {r: ((ROOT / r).read_bytes() if (ROOT / r).exists() else None) for r in eye.STATE_PATHS}
    snap_p = {r: ((ROOT / r).read_bytes() if (ROOT / r).exists() else None) for r in pg.STATE_PATHS}
    try:
        r1 = converse("이차 전지 시장의 근본 원리 파악해줘", mem=_default_mem(), persist=False, use_llm=False)
        chk(r1["intent"] == "omni_insight" and "insight" in r1 and "payload" not in r1, "통찰안 응답 & 대행 큐 미오염")
        pg.transition("WHINE_POUT", reason="test", persist=True)
        r2 = converse("이 현상 간파해봐", mem=_default_mem(), persist=False, use_llm=False)
        chk(r2["intent"] == "omni_insight" and r2.get("tsundere_spiced") is True, "찡찡이 상태에서 통찰 요청 → 츤데레 혜안 통변")
        pg.transition("SPOILED_HAPPY", reason="test", persist=True)
    finally:
        for r, b in snap_i.items():
            if b is not None: (ROOT / r).write_bytes(b)
        for r, b in snap_p.items():
            if b is not None: (ROOT / r).write_bytes(b)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1
# [RGON-R39-DIALOGUE-SOUL-INJECT] — 제15기관 초격차 대화 이해 & 올인원 대화 허브 연동 (Step 39)
try:
    import rgon_aon_dialogue_engine as _rgon_dlg_R39
except Exception:
    _rgon_dlg_R39 = None

if "respond" in globals() and not globals().get("_rgon_r39_wrapped"):
    _orig_respond_R39 = respond
    _rgon_r39_in_hook = False

    def respond(user_text, *args, **kwargs):
        global _rgon_r39_in_hook
        if _rgon_r39_in_hook or _rgon_dlg_R39 is None:
            return _orig_respond_R39(user_text, *args, **kwargs)
        t = "" if user_text is None else str(user_text).strip()
        if not t:
            return _orig_respond_R39(user_text, *args, **kwargs)
        try:
            _rgon_r39_in_hook = True
            nm = _rgon_dlg_R39.normalize_colloquial(t)
            st = _rgon_dlg_R39._state()
            cr = _rgon_dlg_R39.resolve_coreference(nm["normalized"], st["context"])
            resolved = cr["resolved_text"]
            pref = _rgon_dlg_R39.extract_and_save_preference(resolved, save=True)
            decomp = _rgon_dlg_R39.decompose_multi_intent(resolved)
            need_hub = (
                resolved.startswith("/")
                or decomp.get("is_multi")
                or _rgon_dlg_R39.PREF_QUERY.search(resolved) is not None
                or (pref.get("saved") and decomp["intents"][0]["intent"] == "dialogue")
            )
            if need_hub:
                hub = _rgon_dlg_R39.process_dialogue(t, persist=True)
                base = _orig_respond_R39(resolved, *args, **kwargs)
                if isinstance(base, dict):
                    base["reply"] = hub["reply"]
                    base["dialogue_hub"] = {
                        "version": hub["version"],
                        "normalized_text": hub["normalized_text"],
                        "resolved_text": hub["resolved_text"],
                        "intent_names": hub["intent_names"],
                        "is_multi_intent": hub["is_multi_intent"],
                        "thinking_steps": hub["thinking_steps"],
                        "artifact_card": hub["artifact_card"],
                        "follow_up_chips": hub["follow_up_chips"],
                        "proactive_callback": hub["proactive_callback"],
                    }
                    return base
                return hub["reply"]
            base = _orig_respond_R39(resolved, *args, **kwargs)
            rep_txt = base.get("reply", "") if isinstance(base, dict) else str(base)
            ent = _rgon_dlg_R39.extract_entity(resolved) or cr.get("entity_used") or st["context"].get("last_entity")
            its = [x["intent"] for x in decomp["intents"]]
            cb = _rgon_dlg_R39.find_proactive_callback(ent, its, st)
            _rgon_dlg_R39._update_memory(st, t, nm["normalized"], resolved, ent, its, rep_txt)
            _rgon_dlg_R39._save(_rgon_dlg_R39.STATE, st)
            if isinstance(base, dict):
                base["dialogue_hub"] = {
                    "version": _rgon_dlg_R39.VERSION,
                    "normalized_text": nm["normalized"],
                    "resolved_text": resolved,
                    "intent_names": its,
                    "is_multi_intent": False,
                    "thinking_steps": [
                        f"① 구어 정규화: {nm['fixes'] or ['원문 유지']}",
                        f"② 대명사 복원: {cr['entity_used'] or '직접 지칭'}",
                        f"③ 의도 분류: {its[0]}",
                    ],
                    "artifact_card": {"title": "💬 아온 대화 카드", "entity": ent, "intent_badges": its},
                    "follow_up_chips": _rgon_dlg_R39._chips_for(its, ent),
                    "proactive_callback": cb,
                }
            return base
        except Exception:
            return _orig_respond_R39(user_text, *args, **kwargs)
        finally:
            _rgon_r39_in_hook = False

    _rgon_r39_wrapped = True


# ==== [RGON-R40-SYNAPSE-HOOK-START] ====
# R40 시냅스 ③ — converse ↔ 대화 허브 양방향 직결 (재귀 방지 · 시그니처 완전 호환)
import threading as _th40
_R40_SB_GUARD = _th40.local()
_R40_SB_VER = "v11.42-AON-OMNI-NEXUS"
_r40_cur = globals().get("converse")

if callable(_r40_cur):
    _R40_SAVED_SOUL_ORIG = getattr(_r40_cur, "_r40_wrapped_of", None) or _r40_cur
    _r40_prev_respond = globals().get("respond")

    def _r40_hub():
        try:
            import importlib as _il, sys as _sy, os as _os
            _d = _os.path.dirname(_os.path.abspath(__file__))
            if _d not in _sy.path:
                _sy.path.insert(0, _d)
            return _il.import_module("rgon_aon_dialogue_engine")
        except Exception:
            return None

    def converse_soul_r40(user_text: str = "", *args, **kwargs):
        raw = kwargs.pop("_r40_raw", False)
        if raw or getattr(_R40_SB_GUARD, "active", False) or not isinstance(user_text, str) \
                or not user_text.strip():
            return _R40_SAVED_SOUL_ORIG(user_text, *args, **kwargs)
        _R40_SB_GUARD.active = True
        try:
            hub = _r40_hub()
            meta = None
            if hub is not None and hasattr(hub, "r40_preprocess"):
                try:
                    meta = hub.r40_preprocess(user_text, apply=True)
                except Exception as e:
                    meta = {"version": _R40_SB_VER, "error": repr(e)}
            if meta and meta.get("slash") and hasattr(hub, "r40_route"):
                hr = hub.r40_route(user_text, _pre=meta)
                sp = hr.get("speech", "")
                return {"reply": sp, "speech": sp, "text": sp, "response": sp, "intent": "slash_command",
                        "ok": hr.get("ok", True), "dialogue_hub": meta, "hub_result": hr}
            eff = user_text
            if meta and isinstance(meta.get("resolved"), str) and meta["resolved"].strip():
                eff = meta["resolved"]
            res = _R40_SAVED_SOUL_ORIG(eff, *args, **kwargs)
            if isinstance(res, dict):
                res.setdefault("dialogue_hub", meta or {"version": _R40_SB_VER, "status": "hub_unavailable"})
            return res
        finally:
            _R40_SB_GUARD.active = False

    converse_soul_r40._r40_wrapped_of = _R40_SAVED_SOUL_ORIG
    converse_soul_r40._r40 = True
    converse = converse_soul_r40
    if (not callable(_r40_prev_respond)) or _r40_prev_respond is _R40_SAVED_SOUL_ORIG \
            or getattr(_r40_prev_respond, "_r40", False):
        respond = converse_soul_r40
# ==== [RGON-R40-SYNAPSE-HOOK-END] ====


if __name__ == "__main__":
    if "--self-test" in sys.argv: sys.exit(self_test())
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        print(json.dumps(converse(" ".join(sys.argv[1:])), ensure_ascii=False, indent=2)); sys.exit(0)
    m = load_memory()
    print(json.dumps({"version": VERSION, "affection_score": m["affection_score"], "level": level(m["affection_score"]),
                      "total_turns": m["total_turns"], "preferred_keywords": m["preferred_keywords"]}, ensure_ascii=False))
