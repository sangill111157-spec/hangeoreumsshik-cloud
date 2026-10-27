#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rgon_iching_64_engine.py  (RGON v6.3.0-step17)
주역(周易) 64괘 6비트(6-Bit) 상태전이 & AI 의사결정 엔진

6효 매핑 (초효=아래 → 상효=위, 양(陽)=1=정상 / 음(陰)=0=막힘)
  제1효 기반   : Git/해시 무결성
  제2효 소통   : 독대실/브리지 연결
  제3효 자동화 : 클라우드 스케줄러 (workflows + restore_secrets 자가치유)
  제4효 트렌드 : 유튜브 스킬 레이더 (rgon_skill_radar.json 카드)
  제5효 콘텐츠 : 3채널/틱톡 성장 (RGON_EVOLUTION_LOG.md 최신성)
  제6효 시장   : NVDA/자산 모멘텀 (rgon_brain_snapshot.json 최신성)

窮則變 變則通 通則久 (계사전) — 막히면 변하고, 변하면 통하고, 통하면 오래간다.
"""
import os
import sys
import json
import hashlib
import argparse
import datetime
from pathlib import Path

ENGINE_VERSION = "v11.60-AON-EMPIRE-ASSETS"
OUTPUT_NAME = "rgon_today_hexagram.json"
BASELINE_NAME = "rgon_integrity_baseline.json"
LOG_FRESH_DAYS = 7
SNAP_FRESH_DAYS = 3
EXCLUDE_DIRS = {".git", "node_modules", ".rgon_backup", "rgon_backups", "_rgon_backups", "__pycache__", ".venv", "venv", "env", ".idea", ".vscode"}

TRIGRAMS = {
    "天": ("건", "乾", "111", "하늘"),
    "澤": ("태", "兌", "110", "못"),
    "火": ("리", "離", "101", "불"),
    "雷": ("진", "震", "100", "우레"),
    "風": ("손", "巽", "011", "바람"),
    "水": ("감", "坎", "010", "물"),
    "山": ("간", "艮", "001", "산"),
    "地": ("곤", "坤", "000", "땅"),
}

HEXAGRAMS = [
    (1, "중천건", "重天乾", "元亨利貞 · 天行健 君子以自强不息", "하늘의 굳셈 — 주도적으로 전진하되 항룡유회(亢龍有悔)를 경계, 정점일수록 백업과 겸손."),
    (2, "중지곤", "重地坤", "元亨 利牝馬之貞 · 地勢坤 君子以厚德載物", "땅의 포용 — 새 기능 금지, 기반(1효)부터 한걸음씩 받들어 복구."),
    (3, "수뢰둔", "水雷屯", "元亨利貞 勿用有攸往 利建侯", "초창기의 험난 — 구조부터 세우고 서두르지 말 것, 작은 기반 작업부터."),
    (4, "산수몽", "山水蒙", "亨 匪我求童蒙 童蒙求我", "어림과 배움 — 문서·학습 먼저, 모르면 추측 말고 질문(존심)."),
    (5, "수천수", "水天需", "有孚 光亨 貞吉 利涉大川", "기다림 — API/네트워크 지연 시 백오프 재시도, 조급한 패치 금지."),
    (6, "천수송", "天水訟", "有孚窒惕 中吉 終凶", "다툼 — 머지 충돌·의견 충돌은 끝까지 다투지 말고 중도에서 정리."),
    (7, "지수사", "地水師", "貞 丈人吉 无咎", "군대와 규율 — 역할 분담과 지휘 체계 확립, 의장 승인 후 실행."),
    (8, "수지비", "水地比", "吉 原筮 元永貞 无咎", "친밀과 연대 — 4대 AI 협업 브리지 강화."),
    (9, "풍천소축", "風天小畜", "亨 密雲不雨 自我西郊", "작은 축적 — 큰 변경 대신 소규모 개선을 쌓을 때."),
    (10, "천택리", "天澤履", "履虎尾 不咥人 亨", "예를 밟음 — 위험 작업(배포·push)은 규칙대로 조심스럽게."),
    (11, "지천태", "地天泰", "小往大來 吉亨", "소통·태평 — 상하가 통한다: 확장의 적기, 그러나 비(否)로의 반전을 대비."),
    (12, "천지비", "天地否", "否之匪人 不利君子貞 大往小來", "막힘 — 궁변통구 발동: 막힌 경로를 버리고 Fallback으로 변통."),
    (13, "천화동인", "天火同人", "同人于野 亨 利涉大川", "사람들과 함께 — 오픈소스·커뮤니티와 공개적으로 협력."),
    (14, "화천대유", "火天大有", "元亨", "크게 소유함 — 자산·기능이 풍부할수록 겸손하게 관리."),
    (15, "지산겸", "地山謙", "亨 君子有終", "겸손 — 과잉 기능 금지(안분), 낮출수록 끝이 좋다."),
    (16, "뇌지예", "雷地豫", "利建侯行師", "기쁨과 예비 — 사전 백업·체크리스트로 미리 준비."),
    (17, "택뢰수", "澤雷隨", "元亨利貞 无咎", "따름 — 시대 변화(최신 트렌드)에 바르게 순응."),
    (18, "산풍고", "山風蠱", "元亨 利涉大川 先甲三日 後甲三日", "부패를 바로잡음 — 레거시 정리는 앞뒤를 살피며 신중히(보호 파일 제외)."),
    (19, "지택림", "地澤臨", "元亨利貞 至于八月有凶", "다가감 — 사용자에게 다가가는 성장기, 쇠퇴 시기를 미리 대비."),
    (20, "풍지관", "風地觀", "盥而不薦 有孚顒若", "관찰 — 실행보다 로그·지표 관찰과 성찰이 먼저."),
    (21, "화뢰서합", "火雷噬嗑", "亨 利用獄", "깨물어 합함 — 가로막는 버그를 정확히 물어 제거."),
    (22, "산화비", "山火賁", "亨 小利有攸往", "꾸밈 — UI 장식은 작게, 본질(기능·무결성)이 먼저."),
    (23, "산지박", "山地剝", "不利有攸往", "깎여나감 — 손실 진행 중: 새 시도 금지, 백업·보존에 집중."),
    (24, "지뢰복", "地雷復", "亨 出入无疾 朋來无咎 反復其道 七日來復", "회복 — 한 양이 돌아온다: 롤백·복원 후 바른 길로 재출발."),
    (25, "천뢰무망", "天雷无妄", "元亨利貞 其匪正有眚", "거짓 없음 — 환각·추측 보고 금지, 검증된 사실만."),
    (26, "산천대축", "山天大畜", "利貞 不家食吉 利涉大川", "크게 쌓음 — 지식·스킬을 축적해 큰 도약 준비."),
    (27, "산뢰이", "山雷頤", "貞吉 觀頤 自求口實", "기름 — 리소스(토큰·API 쿼터·메모리)를 바르게 관리."),
    (28, "택풍대과", "澤風大過", "棟橈 利有攸往 亨", "크게 지나침 — 대들보가 휜다: 과부하·과잉 설계 경계."),
    (29, "중수감", "重水坎", "習坎 有孚 維心亨 行有尙", "거듭된 험난 — 연속 오류 속에서도 원칙을 지키며 예외 처리로 통과."),
    (30, "중화리", "重火離", "利貞 亨 畜牝牛吉", "붙음과 밝음 — 명확한 문서·로그로 밝게 드러내라."),
    (31, "택산함", "澤山咸", "亨 利貞 取女吉", "감응 — 사용자 피드백에 민감하게 공명."),
    (32, "뇌풍항", "雷風恒", "亨 无咎 利貞 利有攸往", "항구함 — 일관된 규칙과 꾸준한 루틴 유지."),
    (33, "천산돈", "天山遯", "亨 小利貞", "물러남 — 무리한 진격 대신 전략적 후퇴(롤백)."),
    (34, "뇌천대장", "雷天大壯", "利貞", "큰 힘 — 강할 때 힘을 남용하지 말고 바름을 지켜라."),
    (35, "화지진", "火地晉", "康侯用錫馬蕃庶 晝日三接", "나아감 — 해 뜨듯 성장: 성과를 공개하고 전진."),
    (36, "지화명이", "地火明夷", "利艱貞", "밝음이 상함 — 어려울 땐 드러내지 말고 조용히 내실 수리."),
    (37, "풍화가인", "風火家人", "利女貞", "가정 — 내부(폴더·문서·역할) 질서부터 정돈."),
    (38, "화택규", "火澤睽", "小事吉", "어긋남 — 큰 통합 대신 작은 일부터 맞춰 나가라."),
    (39, "수산건", "水山蹇", "利西南 不利東北 利見大人", "절름발이 어려움 — 정면 돌파 대신 우회 경로·조력자를 찾아라."),
    (40, "뇌수해", "雷水解", "利西南 无所往 其來復吉", "풀림 — 문제가 풀리는 때: 신속히 정리하고 일상 복귀."),
    (41, "산택손", "山澤損", "有孚 元吉 无咎 可貞", "덜어냄 — 불필요한 코드·의존성을 덜어 본질을 살려라."),
    (42, "풍뢰익", "風雷益", "利有攸往 利涉大川", "더함 — 이로움을 더할 때: 검증된 기능 추가 적기."),
    (43, "택천쾌", "澤天夬", "揚于王庭 孚號有厲", "결단 — 남은 문제를 공개적으로 결단해 제거."),
    (44, "천풍구", "天風姤", "女壯 勿用取女", "뜻밖의 만남 — 예기치 않은 입력·의존성은 경계하고 검증."),
    (45, "택지췌", "澤地萃", "亨 王假有廟 利見大人", "모임 — 흩어진 모듈·데이터를 하나로 통합."),
    (46, "지풍승", "地風升", "元亨 用見大人 勿恤 南征吉", "오름 — 나무가 자라듯 점진적 상승."),
    (47, "택수곤", "澤水困", "亨 貞大人吉 无咎 有言不信", "곤궁 — 자원이 말라도 근본(무결성)을 지키면 형통."),
    (48, "수풍정", "水風井", "改邑不改井 无喪无得", "우물 — 공용 인프라(스케줄러·시크릿)를 꾸준히 관리."),
    (49, "택화혁", "澤火革", "已日乃孚 元亨利貞 悔亡", "변혁 — 때가 무르익으면 구조 개혁, 신뢰를 얻은 뒤 실행."),
    (50, "화풍정", "火風鼎", "元吉 亨", "솥 — 개혁 후 새 체제(헌법·엔진)를 정립하고 안착."),
    (51, "중뢰진", "重雷震", "亨 震來虩虩 笑言啞啞", "우레 — 충격(장애) 발생: 놀라되 침착히 대응하면 웃게 된다."),
    (52, "중산간", "重山艮", "艮其背 不獲其身", "멈춤 — 멈출 때 멈춰라: 변경 동결·점검."),
    (53, "풍산점", "風山漸", "女歸吉 利貞", "점진 — 한걸음씩(천리행시어족하) 순서대로 나아가라."),
    (54, "뇌택귀매", "雷澤歸妹", "征凶 无攸利", "순서의 어긋남 — 절차를 건너뛴 배포는 흉: 순서 준수."),
    (55, "뇌화풍", "雷火豐", "亨 王假之 勿憂 宜日中", "풍성 — 정점의 시기: 해가 기울기 전 기록·백업."),
    (56, "화산려", "火山旅", "小亨 旅貞吉", "나그네 — 낯선 환경(새 API·클라우드)에서는 신중하고 겸손하게."),
    (57, "중풍손", "重風巽", "小亨 利有攸往 利見大人", "바람의 스며듦 — 비파괴적으로 부드럽게 침투(상선약수)."),
    (58, "중택태", "重澤兌", "亨 利貞", "기쁨 — 즐겁게 소통하되 바름을 잃지 말라."),
    (59, "풍수환", "風水渙", "亨 王假有廟 利涉大川", "흩어짐 — 흩어진 것을 정리하고 중심(철학서)으로 모아라."),
    (60, "수택절", "水澤節", "亨 苦節不可貞", "절제 — 적절한 한도(레이트 리밋·범위) 설정, 지나친 절제도 금물."),
    (61, "풍택중부", "風澤中孚", "豚魚吉 利涉大川", "진실한 믿음 — 정직한 보고로 신뢰를 쌓아라."),
    (62, "뇌산소과", "雷山小過", "亨 利貞 可小事 不可大事", "작은 지나침 — 작은 일엔 좋으나 큰 일은 삼가라."),
    (63, "수화기제", "水火旣濟", "亨小 利貞 初吉終亂 · 君子以思患而豫防之", "이미 건넘 — 완성의 순간: 사환예방(思患豫防), 백업·해시 검증."),
    (64, "화수미제", "火水未濟", "亨 小狐汔濟 濡其尾 无攸利", "아직 건너지 못함 — 끝은 새 시작: 다음 진화를 신중히 준비."),
]

LINES = [
    {"pos": 1, "name": "기반", "domain": "Git/해시 무결성",
     "fallback": "git status 확인 → rgon_integrity_baseline.json 대조 → .rgon_backup 에서 복원 후 재검증"},
    {"pos": 2, "name": "소통", "domain": "독대실/브리지 연결",
     "fallback": "독대실 HTML 존재·경로 확인 (원본 HTML 수정 금지, 경로만 점검)"},
    {"pos": 3, "name": "자동화", "domain": "클라우드 스케줄러",
     "fallback": "restore_secrets.py 자가치유판 확인 → .github/workflows 점검 → Actions 재실행"},
    {"pos": 4, "name": "트렌드", "domain": "유튜브 스킬 레이더",
     "fallback": "rgon_skill_radar.json 카드 갱신 (레이더 스크립트 재실행)"},
    {"pos": 5, "name": "콘텐츠", "domain": "3채널/틱톡 성장",
     "fallback": "RGON_EVOLUTION_LOG.md 에 최근 7일 이내 진화 기록 추가"},
    {"pos": 6, "name": "시장", "domain": "NVDA/자산 모멘텀",
     "fallback": "rgon_brain_snapshot.json 최신화 (3일 이내)"},
]


def _build_table():
    table, by_key, by_no = [], {}, {}
    for no, ko, hz, judgment, action in HEXAGRAMS:
        if hz.startswith("重"):
            up, lo = hz[1], hz[1]
        else:
            up, lo = hz[0], hz[1]
        key = TRIGRAMS[lo][2] + TRIGRAMS[up][2]
        entry = {
            "number": no,
            "name": "%d. %s(%s)" % (no, ko, hz),
            "name_ko": ko,
            "name_hanja": hz,
            "upper": "%s(%s·%s)" % (TRIGRAMS[up][3], TRIGRAMS[up][1], TRIGRAMS[up][0]),
            "lower": "%s(%s·%s)" % (TRIGRAMS[lo][3], TRIGRAMS[lo][1], TRIGRAMS[lo][0]),
            "key": key,
            "judgment": judgment,
            "ai_action": action,
        }
        table.append(entry)
        by_key[key] = entry
        by_no[no] = entry
    if len(table) != 64 or len(by_key) != 64:
        raise RuntimeError("64괘 테이블 무결성 오류: 괘 %d개 / 고유키 %d개" % (len(table), len(by_key)))
    return table, by_key, by_no


TABLE, BY_KEY, BY_NUMBER = _build_table()


def get_by_key(key):
    return BY_KEY.get(key)


def get_by_number(no):
    return BY_NUMBER.get(int(no))


def _walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            yield Path(dirpath) / fn


def _protected(p):
    return p.suffix.lower() in (".html", ".js") or p.name.lower() == "manifest.json"


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _age_days(p):
    return (datetime.datetime.now().timestamp() - p.stat().st_mtime) / 86400.0


def _parse_dt(s):
    try:
        s = str(s).strip().replace("Z", "")
        dt = datetime.datetime.fromisoformat(s)
        return dt.replace(tzinfo=None)
    except Exception:
        return None


def check_line1(root):
    git_ok = (root / ".git").exists()
    html = [p for p in _walk(root) if p.suffix.lower() == ".html"]
    base = root / BASELINE_NAME
    mismatch, checked, base_state = 0, 0, "없음"
    if base.exists():
        data = json.loads(base.read_text(encoding="utf-8"))
        for rel, h in (data.get("hashes") or {}).items():
            p = root / rel
            checked += 1
            if not p.exists() or _sha(p) != h:
                mismatch += 1
        base_state = "일치" if mismatch == 0 else "불일치"
    ok = git_ok and len(html) > 0 and mismatch == 0
    return ok, "git=%s, html=%d개, baseline=%s(%d/%d)" % ("O" if git_ok else "X", len(html), base_state, checked - mismatch, checked)


def check_line2(root):
    keys = ("dokdae", "독대", "audience", "council", "chamber")
    hits = []
    for p in _walk(root):
        if p.suffix.lower() != ".html":
            continue
        name = p.name.lower()
        hit = any(k in name for k in keys)
        if not hit:
            try:
                if p.stat().st_size <= 3 * 1024 * 1024:
                    hit = "독대" in p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                hit = False
        if hit:
            hits.append(p.relative_to(root).as_posix())
    return len(hits) > 0, ("독대실 HTML %d개: %s" % (len(hits), ", ".join(hits[:3]))) if hits else "독대실 HTML 미발견"


def check_line3(root):
    wf_dir = root / ".github" / "workflows"
    wfs = []
    if wf_dir.is_dir():
        wfs = sorted(list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml")))
    rs = root / "restore_secrets.py"
    rs_ok, rs_state = False, "없음"
    if rs.exists():
        src = rs.read_text(encoding="utf-8", errors="replace")
        try:
            compile(src, str(rs), "exec")
            healed = "RGON-SELF-HEAL" in src
            rs_ok = healed
            rs_state = "자가치유판" if healed else "구버전(자가치유 마커 없음)"
        except SyntaxError:
            rs_state = "문법 오류"
    ok = len(wfs) > 0 and rs_ok
    return ok, "workflows=%d개, restore_secrets=%s" % (len(wfs), rs_state)


def check_line4(root):
    p = root / "rgon_skill_radar.json"
    if not p.exists():
        return False, "rgon_skill_radar.json 없음"
    data = json.loads(p.read_text(encoding="utf-8-sig"))
    cards = []
    if isinstance(data, list):
        cards = data
    elif isinstance(data, dict):
        for k in ("cards", "skills", "items", "radar", "results"):
            v = data.get(k)
            if isinstance(v, list):
                cards = v
                break
    return len(cards) > 0, "스킬 카드 %d장" % len(cards)


def check_line5(root):
    p = root / "RGON_EVOLUTION_LOG.md"
    if not p.exists():
        return False, "RGON_EVOLUTION_LOG.md 없음"
    age = _age_days(p)
    return age <= LOG_FRESH_DAYS, "진화 로그 %.1f일 전 갱신 (기준 %d일)" % (age, LOG_FRESH_DAYS)


def check_line6(root):
    p = root / "rgon_brain_snapshot.json"
    if not p.exists():
        return False, "rgon_brain_snapshot.json 없음"
    age = _age_days(p)
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
        dt = _parse_dt(data.get("updated_at") or data.get("generated_at_kst")) if isinstance(data, dict) else None
        if dt:
            age = (datetime.datetime.now() - dt).total_seconds() / 86400.0
    except Exception:
        pass
    return age <= SNAP_FRESH_DAYS, "스냅샷 %.1f일 전 갱신 (기준 %d일)" % (age, SNAP_FRESH_DAYS)


CHECKS = [check_line1, check_line2, check_line3, check_line4, check_line5, check_line6]


def _draw(key):
    out = []
    for i in range(5, -1, -1):
        bar = "▅▅▅▅▅▅▅▅▅" if key[i] == "1" else "▅▅▅▅   ▅▅▅▅"
        out.append("   %s  제%d효 %s" % (bar.ljust(11), i + 1, LINES[i]["name"]))
    return "\n".join(out)


def run(root=None, save=True, verbose=True):
    root = Path(root).resolve() if root else Path(__file__).resolve().parent
    now = datetime.datetime.now()
    lines, bits = [], ""
    for spec, fn in zip(LINES, CHECKS):
        try:
            ok, detail = fn(root)
        except Exception as e:
            ok, detail = False, "점검 예외(궁변통구로 음효 처리): %s" % type(e).__name__
        item = dict(spec)
        item.update({"ok": bool(ok), "bit": 1 if ok else 0, "detail": detail})
        lines.append(item)
        bits += "1" if ok else "0"
    hexa = BY_KEY[bits]
    fails = [l for l in lines if not l["ok"]]
    prescription = ["오늘의 괘 %s — %s" % (hexa["name"], hexa["ai_action"])]
    next_step = None
    if fails:
        for l in fails:
            prescription.append("궁변통구: 제%d효(%s·%s) 막힘 → %s" % (l["pos"], l["name"], l["domain"], l["fallback"]))
        first = fails[0]
        nb = list(bits)
        nb[first["pos"] - 1] = "1"
        nxt = BY_KEY["".join(nb)]
        next_step = {
            "fix_line": first["pos"],
            "fix_action": first["fallback"],
            "next_hexagram": nxt["name"],
            "next_key": nxt["key"],
            "principle": "천리지행 시어족하 — 가장 아래(기반)의 막힌 효부터 한걸음씩 통하게 한다.",
        }
    else:
        prescription.append("6효 모두 양(陽): 수화기제의 사환예방(思患豫防) — 완성의 순간에도 백업·해시 검증을 멈추지 말고, 화수미제처럼 다음 진화를 준비하라(항룡유회 경계).")
    result = {
        "engine_version": ENGINE_VERSION,
        "generated_at": now.isoformat(timespec="seconds"),
        "root": str(root),
        "key": bits,
        "key_order": "제1효(초효)→제6효(상효), 1=양(정상) 0=음(막힘)",
        "yang_count": bits.count("1"),
        "hexagram": hexa,
        "lines": lines,
        "prescription": prescription,
        "next_step": next_step,
        "maxim": "窮則變 變則通 通則久 — 막히면 변하고, 변하면 통하고, 통하면 오래간다.",
    }
    if save:
        out = root / OUTPUT_NAME
        tmp = root / (OUTPUT_NAME + ".rgon_tmp")
        tmp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(str(tmp), str(out))
    if verbose:
        print("\n☯ RGON 주역 64괘 엔진 %s — 오늘의 괘" % ENGINE_VERSION)
        print(_draw(bits))
        print("   ▶ %s  [6비트 %s]  상괘 %s / 하괘 %s" % (hexa["name"], bits, hexa["upper"], hexa["lower"]))
        print("   ▶ 괘사: %s" % hexa["judgment"])
        for l in lines:
            print("   %s 제%d효 %s(%s): %s" % ("●" if l["ok"] else "○", l["pos"], l["name"], l["domain"], l["detail"]))
        print("   ── AI 전략 처방 ──")
        for p in prescription:
            print("   · " + p)
        if next_step:
            print("   · 다음 한걸음: 제%d효 복구 시 → %s" % (next_step["fix_line"], next_step["next_hexagram"]))
        if save:
            print("   저장: %s" % (root / OUTPUT_NAME))
    return result


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="RGON 주역 64괘 6비트 의사결정 엔진")
    ap.add_argument("--root", default=None)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--no-save", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.list:
        for e in TABLE:
            print("%-22s %s  %s" % (e["name"], e["key"], e["ai_action"]))
        return 0
    try:
        run(a.root, save=not a.no_save, verbose=not a.quiet)
    except Exception as e:
        print("[iching] 판독 예외 %s — 궁변통구: 정상 종료" % type(e).__name__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
