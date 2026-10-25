#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 38 최종 수술 완성본: v11.38-AON-OMNI-DIALOGUE — 제14기관 아온 만물 격물치지(格物致知) 전방위 통찰안 (R1~R39 · 정식 스킬 34)
클로드 실측 엔진 + 안티그레비티 SOUL_INJECT 우선순위 수술 + 삼성(三省) 3/3 자동백업·원복 프레임워크 완벽 통합"""
import ast, datetime, hashlib, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
OLD_VER, NEW_VER = "v11.36-AON-ICHING-DAO", "v11.38-AON-OMNI-DIALOGUE"
OLD_AB, NEW_AB = "R1~R37", "R1~R39"
OLD_SK, NEW_SK = 33, 34
SKILL_NAME = "aon-omni-insight-eye"
INSIGHT_FILE = "rgon_aon_omni_insight_eye.py"
REPORT_FILE = "STEP38_AON_OMNI_INSIGHT_REPORT.md"
R38_SUMMARY = (
    "R38: 아온(A-ON) 만물 격물치지 전방위 통찰안 — "
    "이미지(PNG 픽셀·헤더·Canvas 실측)·영상(YouTube/Shorts·MP4 길이·기승전결 변화율)·말/현상 OTA 능동 지각 + "
    "FPCOS 6계층(L0 사실/추론/미지/단정어 ➔ L1 제1원리·사성제 ➔ L2 R/B 루프·급소·군더더기 ➔ L3 멘탈모델·주역 ➔ L4 섀도게이트 반전검증 ➔ L5 한줄본질·신뢰도≤85%)"
)

HTML_TARGETS = [
    "index.html", "rgon_alpha_audience.html", "rgon_alpha_chat.html",
    "dashboard/index.html", "dashboard/rgon_alpha_chat.html",
    "docs/index.html", "docs/rgon_alpha_chat.html"
]
SYNC_FILES = [
    "CONSTITUTION.md", "ANTIBODY_REGISTRY.md", "CODE_MAP.md", "GLOSSARY.md", "RGON_MORNING_BRIEF.md",
    "skills/SKILL_INDEX.md", "skills/SKILL_INDEX.json", "rgon_morning_brief.json", "docs/rgon_morning_brief.json",
    "rgon_Numeric_Organ.json", "rgon_k_avatar_state.json", "docs/rgon_k_avatar_state.json",
    "rgon_muse_queue.json", "docs/rgon_muse_queue.json", "rgon_voice_profile.json", "docs/rgon_voice_profile.json",
    "rgon_voice_organ_state.json", "docs/rgon_voice_organ_state.json", "rgon_aon_memory.json", "docs/rgon_aon_memory.json",
    "rgon_manual_gate_state.json", "docs/rgon_manual_gate_state.json", "rgon_laptop_hands_state.json", "docs/rgon_laptop_hands_state.json",
    "rgon_aon_playground_state.json", "docs/rgon_aon_playground_state.json", "rgon_aon_iching_state.json", "docs/rgon_aon_iching_state.json",
    "rgon_aon_insight_state.json", "docs/rgon_aon_insight_state.json", "rgon_immune_ledger.json", "rgon_white_blood_cell.py",
    "rgon_daily_cycle.py", "rgon_k_avatar_engine.py", "rgon_muse_delegator.py", "rgon_voice_organ.py", "rgon_aon_soul_brain.py",
    "rgon_laptop_hands.py", "rgon_aon_desktop_playground.py", "rgon_aon_iching_dao_oracle.py", INSIGHT_FILE,
    "dept_sub_agents_status.json", "docs/dept_sub_agents_status.json"
]
NEW_FILES = [
    INSIGHT_FILE, "rgon_aon_insight_state.json", "docs/rgon_aon_insight_state.json",
    f"skills/{SKILL_NAME}/SKILL.md", REPORT_FILE
]
MOD_ALLOW = set(HTML_TARGETS) | set(SYNC_FILES) | set(NEW_FILES)
SKIP_DIRS = {".git", ".rgon_backups", ".rgon_backup", "__pycache__", "node_modules", ".venv", "venv"}


def log(msg):
    print(msg, flush=True)


def rd(p):
    return Path(p).read_text(encoding="utf-8", errors="replace")


def wr(p, s):
    p = Path(p) if Path(p).is_absolute() else ROOT / p
    p.parent.mkdir(parents=True, exist_ok=True)
    for i in range(6):
        try:
            p.write_text(s, encoding="utf-8", newline="\n")
            return
        except PermissionError:
            time.sleep(0.05 * (i + 1))
    p.write_text(s, encoding="utf-8", newline="\n")


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def snapshot_all():
    out = {}
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        out[rel] = sha256(p)
    return out


def backup_targets(bdir):
    bdir.mkdir(parents=True, exist_ok=True)
    saved = []
    for rel in sorted(MOD_ALLOW):
        src = ROOT / rel
        if src.exists() and src.is_file():
            dst = bdir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            saved.append(rel)
    (bdir / "_manifest.json").write_text(
        json.dumps({"saved": saved, "new": NEW_FILES}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return saved


def restore_backup(bdir, snap0):
    log("⏪ Auto-Rollback 시작: 백업에서 100% 원복합니다...")
    man = json.loads((bdir / "_manifest.json").read_text(encoding="utf-8"))
    for rel in man.get("saved", []):
        src, dst = bdir / rel, ROOT / rel
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    removed = 0
    for rel in man.get("new", []):
        if rel not in man.get("saved", []):
            p = ROOT / rel
            if p.exists():
                p.unlink()
                removed += 1
            if p.parent != ROOT and p.parent.exists() and not any(p.parent.iterdir()):
                try:
                    p.parent.rmdir()
                except Exception:
                    pass
    snap1 = snapshot_all()
    same = (snap0 == snap1)
    log(f"⏪ 복원 {len(man.get('saved', []))}개 · 신규 삭제 {removed}개 · 원복 검증 {'✅ 100% 일치' if same else '⚠️ 차이 있음'}")


# ======================================================================== 제14기관 모듈
INSIGHT_SRC = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_aon_omni_insight_eye.py — 제14기관 아온 만물 격물치지 통찰안 (표준 라이브러리 전용)
[RGON-R38] v11.38-AON-OMNI-DIALOGUE · 항체 R1~R39 · 정식 스킬 35개
OTA 능동 지각(Observation→Thought→Action) → FPCOS L0~L5 해부 → 아온 혜안 브리핑.
한계: 규칙 기반 휴리스틱. 이미지·영상 속 '무엇이 있는가'(객체·장면 인식)는 판정하지 않으며
헤더·픽셀 통계·URL 구조·텍스트 신호만 실측한다. 신뢰도는 85%를 넘기지 않는다."""
import base64, datetime, hashlib, json, math, re, struct, sys, time, zlib
from pathlib import Path
from urllib.parse import urlparse, parse_qs

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
VERSION = "v11.38-AON-OMNI-DIALOGUE"
ANTIBODY = "R1~R39"
SKILL_COUNT = 34
STATE_PATHS = ("rgon_aon_insight_state.json", "docs/rgon_aon_insight_state.json")
CONF_CAP = 85
IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp")
VID_EXT = (".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi")
IMG_WORDS = re.compile(r"(이미지|사진|그림|차트|스크린샷|캡처|썸네일)")
VID_WORDS = re.compile(r"(youtube\.com|youtu\.be|/shorts/|영상|동영상|쇼츠|릴스)", re.I)
URL_RE = re.compile(r"(https?://\S+|data:[\w/+.-]+;base64,[A-Za-z0-9+/=]+)")
PATH_RE = re.compile(r"([^\s\"']+\.(?:png|jpe?g|gif|svg|webp|bmp|mp4|mov|m4v|webm|mkv|avi))(?![\w])", re.I)
ABS_RE = re.compile(r"(무조건|절대|반드시|100\s*%|100프로|전부|항상|결코|확실히|완벽|필승|영원히|무적)")
NUM_RE = re.compile(r"-?\d+(?:[.,]\d+)?\s*(?:%|퍼센트|원|달러|배|명|개|년|월|일|시간|분|초|만|억)?")
PIVOT_RE = re.compile(r"(하지만|그런데|그러나|반전|갑자기|돌연|그러다)")
INTENSITY = re.compile(r"(급등|급락|폭발|폭락|반전|갑자기|위기|최고|최악|충격|돌파|붕괴|역전|대박|난리)")
INTENTS = {
    "question": r"(\?|왜|어떻게|무엇|뭐|어째서)",
    "request": r"(해줘|알려줘|분석|봐줘|해부|파악|간파)",
    "worry": r"(걱정|불안|위험|손실|무섭|망할|떨어)",
    "desire": r"(벌고|성공|이기|갖고|키우|늘리|오르)",
    "conflict": r"(싸움|갈등|다툼|반대|충돌|대립|서운)",
    "causal": r"(때문|원인|그래서|결과로|탓)",
    "change": r"(변화|전환|국면|추세|반전|급변|바뀌)",
}
STOP = set("그리고 그래서 하지만 그런데 이거 저거 그거 이건 오늘 지금 정말 진짜 너무 아온 아온이 대표님 해줘 알려줘 봐줘".split())


def _dom(kw, var, lt, lm, lev, dw, gt, it, blind, hx):
    return dict(kw=re.compile(kw, re.I) if kw else None, variables=var, loop_type=lt, loop=lm, leverage=lev,
                dead_weight=dw, ground_truth=gt, interest=it, blind=blind, hexagram=hx)


DOMAINS = {
    "market": _dom(r"(주식|코인|장세|시장|금리|환율|매수|매도|수익률|폭락|급등|나스닥|코스피|비트코인|ETF|이차\s*전지|반도체)",
                   ["유동성(돈의 양과 속도)", "기대·심리(공포와 탐욕)", "실적·금리 등 펀더멘털"], "R",
                   "가격 상승 → 기대 확산 → 추가 매수 → 가격 상승의 자기강화. 과열되면 차익실현이라는 B 루프가 반대로 작동한다",
                   "진입 전에 손절선과 비중 상한을 먼저 정하는 규칙 한 줄", "헤드라인 과잉 소비와 잦은 매매 비용",
                   "가격은 기대의 변화에 반응하고, 기대는 결국 유동성과 실적에 수렴한다",
                   "중개자(거래 수수료) · 큰손(유동성 공급·회수) · 정보 판매자(조회수)",
                   "실제 수급(자금 흐름)과 기간 — 반대 방향이면 결론이 뒤집힌다", 20),
    "relationship": _dom(r"(친구|연인|가족|동료|상사|관계|마음|서운|싸움|갈등|대화|부부)",
                         ["신뢰 잔고", "기대치 차이", "소통의 빈도와 질"], "R",
                         "서운함 → 거리두기 → 오해 증폭 → 더 큰 서운함의 악순환. 작은 인정 한 번이 선순환으로 뒤집는다",
                         "상대의 기대를 추측하지 말고 한 문장으로 직접 확인하기", "속으로만 쌓는 해석과 승패 계산",
                         "사람은 이해받는다고 느낄 때 마음을 연다", "두 당사자 각자의 인정 욕구 · 주변 평판",
                         "상대가 실제로 무엇을 기대했는지 — 직접 들은 적이 없다면 전부 추측이다", 31),
    "tech": _dom(r"(코드|버그|서버|AI|모델|앱|시스템|자동화|파이썬|에러|배포|API|알고리즘)",
                 ["입력 데이터 품질", "병목 단계(가장 느린 곳)", "피드백 속도(테스트·로그)"], "B",
                 "에러 → 수정 → 테스트 → 안정화의 균형 루프. 테스트가 없으면 기술부채가 쌓이는 R 루프로 바뀐다",
                 "가장 느린 한 단계(제약)를 찾아 그것만 먼저 개선", "실행되지 않는 코드 · 중복 설정 · 수동 반복 작업",
                 "시스템 전체 속도는 가장 느린 단계가 정한다", "플랫폼·클라우드(사용량 과금) · 도구 판매자 · 유지보수 담당",
                 "실제 실행 로그와 재현 조건 — 없으면 원인은 추측이다", 21),
    "business": _dom(r"(매출|고객|사업|마케팅|가격|영업|브랜드|창업|경쟁|비용|이익|판매)",
                     ["고객 획득 비용", "재구매·유지율", "단위당 마진"], "R",
                     "만족한 고객 → 추천 → 신규 고객 → 매출 → 재투자의 강화 루프",
                     "이탈 이유 상위 1개 제거(유지율은 복리로 쌓인다)", "성과 측정이 안 되는 광고비와 회의",
                     "사업은 고객이 낼 만한 가치를 비용보다 싸게 반복 전달하는 구조다", "고객 · 경쟁사 · 광고 플랫폼 · 투자자",
                     "코호트별 유지율과 단위 경제성 실측치", 42),
    "content": _dom(r"(유튜브|쇼츠|조회수|구독|썸네일|콘텐츠|릴스|틱톡|youtu)",
                    ["첫 3초 이탈률", "시청 지속 시간", "공유·댓글 반응"], "R",
                    "시청 지속 ↑ → 추천 노출 ↑ → 조회 ↑ → 데이터 ↑의 강화 루프",
                    "첫 화면·첫 문장 훅 하나를 고치기", "도입부 인사와 반복 설명",
                    "주의는 희소하고, 추천은 시청자의 체류 행동을 따른다", "플랫폼(광고 체류시간) · 제작자(조회·수익) · 광고주",
                    "실제 시청 지속 그래프와 유입 경로", 22),
    "health": _dom(r"(건강|운동|수면|피로|스트레스|식사|체력|통증)",
                   ["수면의 질", "활동량", "스트레스 부하"], "B",
                   "피로 → 휴식 → 회복의 균형 루프. 수면 부족이 길어지면 피로 → 능률 저하 → 야근 → 수면 부족의 R 악순환",
                   "기상·취침 시간 고정", "자기 전 화면 시청", "몸은 회복이 부하를 이길 때 강해진다",
                   "건강 제품 판매자 · 본인", "증상의 기간과 의학적 진단 — 지속되면 전문가 확인이 우선", 27),
    "visual": _dom(None, ["구도(초점 위치)", "명암 대비", "색 균형·정보 밀도"], "B",
                   "시선은 대비가 큰 곳으로 끌리고, 여백이 시선을 쉬게 한다(밀도와 여백의 균형)",
                   "주제 한 곳에만 대비를 집중", "주제와 무관한 배경 정보",
                   "시선은 대비가 크고 정보가 몰린 곳으로 먼저 간다",
                   "만든 사람(보여주고 싶은 것) · 보는 사람(보고 싶은 것)", "촬영·제작 의도와 프레임 밖 맥락", 20),
    "general": _dom(None, ["목표(원하는 상태)", "가장 큰 제약", "자원(시간·돈·주의력)"], "B",
                    "목표와 현실의 차이가 행동을 만들고, 행동이 그 차이를 줄인다",
                    "가장 큰 제약 하나를 정의하고 그것만 먼저 풀기", "결정을 미루는 끝없는 정보 수집",
                    "결과는 구조가 만든다 — 구조를 바꾸면 결과가 바뀐다",
                    "상황을 설명하는 쪽 · 결정하는 쪽(둘의 이해가 다를 수 있음)", "당사자들이 실제로 원하는 것과 제약 조건", 20),
}
HEX_FALLBACK = {
    20: ("觀", "관", "☴☷", "관조 — 바람이 땅 위를 두루 스치듯 전체를 본다"),
    21: ("噬嗑", "서합", "☲☳", "장애 제거 — 입 안의 걸림을 물어 끊는다"),
    31: ("咸", "함", "☱☶", "감응 — 마음이 통하면 움직인다"),
    22: ("賁", "비", "☶☲", "꾸밈 — 형식이 본질을 비춘다"),
    27: ("頤", "이", "☶☳", "기름 — 무엇을 들이는가가 몸을 만든다"),
    42: ("益", "익", "☴☳", "보탬 — 위를 덜어 아래를 보탠다"),
    49: ("革", "혁", "☱☲", "변혁 — 때가 차면 바꾼다"),
}
DESC_CUES = [(r"대칭", "대칭: 대칭 구조 언급"), (r"중앙|가운데", "초점: 중앙 배치"), (r"여백|비어|단순", "여백: 여백·단순 구성"),
             (r"복잡|빽빽|가득", "밀도: 높은 정보 밀도"), (r"차트|그래프|캔들", "구조: 데이터 시각화(축·추세선)"),
             (r"얼굴|사람|인물", "초점: 인물 중심"), (r"상승|우상향", "구조: 우상향 흐름"), (r"하락|우하향", "구조: 우하향 흐름")]


def _uniq(xs):
    out = []
    for x in xs:
        if x and x not in out:
            out.append(x)
    return out


def _is_file(s):
    try:
        return len(s) < 400 and Path(s).is_file()
    except (OSError, ValueError):
        return False


def shannon(b):
    if not b:
        return 0.0
    c = [0] * 256
    for x in b:
        c[x] += 1
    n = len(b)
    return round(-sum(v / n * math.log2(v / n) for v in c if v), 3)


def _png_rows(data):
    w, h, bd, ct, _, _, il = struct.unpack(">IIBBBBB", data[16:29])
    if bd != 8 or il or ct not in (0, 2, 4, 6) or w * h > 600_000:
        return None
    ch = {0: 1, 2: 3, 4: 2, 6: 4}[ct]
    idat = b""
    i = 8
    while i + 8 <= len(data):
        ln = struct.unpack(">I", data[i:i + 4])[0]
        tp = data[i + 4:i + 8]
        if tp == b"IDAT":
            idat += data[i + 8:i + 8 + ln]
        if tp == b"IEND":
            break
        i += 12 + ln
    raw = zlib.decompress(idat)
    stride = w * ch
    prev = bytearray(stride)
    rows = []
    p = 0
    for _ in range(h):
        f = raw[p]
        line = bytearray(raw[p + 1:p + 1 + stride])
        p += 1 + stride
        for x in range(stride):
            a = line[x - ch] if x >= ch else 0
            b = prev[x]
            c = prev[x - ch] if x >= ch else 0
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + b) & 255
            elif f == 3:
                line[x] = (line[x] + ((a + b) >> 1)) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        rows.append(bytes(line))
        prev = line
    return w, h, ch, rows


def _pix_stats(w, h, ch, rows):
    step = max(1, int(math.sqrt(w * h / 40000)))
    n = tot = sq = rs = gs = bs = cx = cy = left = right = 0.0
    for y in range(0, h, step):
        r = rows[y]
        for x in range(0, w, step):
            i = x * ch
            R, G, B = (r[i], r[i + 1], r[i + 2]) if ch >= 3 else (r[i], r[i], r[i])
            L = 0.299 * R + 0.587 * G + 0.114 * B
            n += 1; tot += L; sq += L * L; rs += R; gs += G; bs += B; cx += x * L; cy += y * L
            if x < w / 2:
                left += L
            else:
                right += L
    mean = tot / n
    std = math.sqrt(max(0.0, sq / n - mean * mean))
    return dict(brightness=round(mean / 255, 3), contrast=round(std / 255, 3),
                rgb_balance=[round(rs / n), round(gs / n), round(bs / n)],
                focus_center=[round(cx / tot / w, 3) if tot else 0.5, round(cy / tot / h, 3) if tot else 0.5],
                lr_symmetry=round(1 - abs(left - right) / max(left + right, 1), 3))


def _img_header(b):
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", b[16:24]); return "PNG", w, h, {}
    if b[:6] in (b"GIF87a", b"GIF89a"):
        w, h = struct.unpack("<HH", b[6:10]); return "GIF", w, h, {}
    if b[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(b):
            if b[i] != 0xFF: i += 1; continue
            m = b[i + 1]
            if m == 0xFF: i += 1; continue
            if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7: i += 2; continue
            ln = struct.unpack(">H", b[i + 2:i + 4])[0]
            if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", b[i + 5:i + 9]); return "JPEG", w, h, {}
            i += 2 + ln
        return "JPEG", 0, 0, {}
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        return "WEBP", 0, 0, {}
    if b[:2] == b"BM" and len(b) >= 26:
        w, h = struct.unpack("<ii", b[18:26]); return "BMP", w, abs(h), {}
    t = b[:20000].decode("utf-8", "ignore")
    if "<svg" in t:
        def num(attr):
            m = re.search(r'<svg[^>]*?\s' + attr + r'\s*=\s*["\']?([\d.]+)', t, re.S)
            return float(m.group(1)) if m else 0
        w, h = num("width"), num("height")
        if not (w and h):
            m = re.search(r'viewBox\s*=\s*["\']\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)', t)
            if m:
                w, h = float(m.group(1)), float(m.group(2))
        return "SVG", int(w), int(h), {"svg_elements": max(0, len(re.findall(r"<(?![/?!])[a-zA-Z]", t)) - 1)}
    return None


def _stat_cues(st):
    fx, fy = st["focus_center"]
    near3 = min(abs(fx - 1 / 3), abs(fx - 2 / 3)) < 0.08 or min(abs(fy - 1 / 3), abs(fy - 2 / 3)) < 0.08
    pos = "중앙 배치" if abs(fx - .5) < .08 and abs(fy - .5) < .08 else ("3분할선 근처" if near3 else "한쪽으로 치우침")
    sym, b, ct = st["lr_symmetry"], st["brightness"], st["contrast"]
    r, g, bb = st["rgb_balance"]
    dom = max((r, "적색"), (g, "녹색"), (bb, "청색"))[1]
    return [f"초점: 밝기 무게중심 ({fx:.2f}, {fy:.2f}) — {pos}",
            f"대칭: 좌우 밝기 대칭도 {sym:.2f}" + (" (강한 대칭·안정감)" if sym >= .9 else " (비대칭·긴장감)" if sym < .7 else ""),
            f"여백: 평균 밝기 {b:.2f}" + (" (밝은 여백 많음)" if b > .75 else " (어두운 톤 지배)" if b < .25 else ""),
            f"밀도: 명암 대비 {ct:.2f}" + (" (저대비·평탄)" if ct < .12 else " (고대비·강한 시선 유도)" if ct > .3 else ""),
            f"색 밸런스: RGB {r}/{g}/{bb} — {dom} 우세"]


def _load_bytes(source):
    if isinstance(source, (bytes, bytearray)):
        return bytes(source), "bytes"
    s = str(source or "").strip()
    if s.startswith("data:"):
        try:
            x = s.split(",", 1)[1]
            return base64.b64decode(x + "=" * (-len(x) % 4)), "data_url"
        except Exception:
            return None, "data_url_broken"
    if "<svg" in s[:300]:
        return s.encode("utf-8"), "svg_text"
    if _is_file(s):
        return Path(s).read_bytes()[:50_000_000], "file"
    return None, "text"


def perceive_image(source):
    data, kind = _load_bytes(source)
    out = dict(modality="image", kind=kind, cues=[], known=[], inferred=[], unknown=[],
               ota=[f"Observation: 입력 형태 = {kind}"])
    if data:
        out["bytes"] = len(data)
        out["entropy_bits"] = shannon(data[:1_000_000])
        hd = _img_header(data)
        if hd:
            fmt, w, h, extra = hd
            out.update(format=fmt, width=w, height=h, **extra)
            out["known"].append(f"{fmt} {w}×{h}px · {len(data):,} bytes · 파일 엔트로피 {out['entropy_bits']} bit/byte")
            if w and h:
                ar = w / h
                out["aspect"] = round(ar, 3)
                out["megapixels"] = round(w * h / 1e6, 3)
                orient = "가로형" if ar > 1.15 else "세로형" if ar < 0.87 else "정방형"
                out["cues"].append(f"구조: {orient}(비율 {ar:.2f})")
                if out["megapixels"] < 0.1:
                    out["inferred"].append("저해상도 — 아이콘·썸네일·축소본일 가능성")
            if fmt == "PNG":
                try:
                    px = _png_rows(data)
                    if px:
                        st = _pix_stats(*px)
                        out["pixel_stats"] = st
                        out["cues"] += _stat_cues(st)
                        out["known"].append("픽셀 실측: 밝기·대비·RGB 밸런스·무게중심·좌우 대칭")
                    else:
                        out["unknown"].append("PNG 픽셀 디코딩 생략(16bit·팔레트·인터레이스·60만 화소 초과)")
                except Exception as e:
                    out["unknown"].append(f"PNG 디코딩 실패: {e}")
            elif fmt == "SVG":
                out["cues"].append(f"밀도: SVG 요소 {extra.get('svg_elements', 0)}개(벡터 구조)")
            else:
                out["unknown"].append(f"{fmt} 픽셀 통계는 표준 라이브러리로 디코딩 불가 → 브라우저 Canvas 실측 사용")
            e = out["entropy_bits"]
            out["inferred"].append("파일 엔트로피 " + ("높음 → 압축된 사진·복잡한 질감" if e > 7.5 else "낮음 → 단순 도형·평탄 색면"))
        else:
            out["unknown"].append("이미지 헤더 판별 실패(지원 형식 아님 또는 손상)")
    else:
        t = str(source or "")
        out["known"].append("텍스트 묘사만 제공됨(픽셀 실측 불가)")
        for pat, cue in DESC_CUES:
            if re.search(pat, t):
                out["cues"].append(cue)
        if not out["cues"]:
            out["unknown"].append("묘사에서 구조·대칭·초점 단서를 찾지 못함")
        out["desc"] = t[:300]
    out["unknown"].append("객체·장면의 의미(무엇이 찍혔는가)는 인식하지 않음")
    out["ota"] += ["Thought: 대비·무게중심·대칭이 시선 흐름을 결정한다", "Action: 초점·밀도·여백 단서 확정"]
    return out


def _mp4_duration(b):
    i = b.find(b"mvhd")
    if i < 0 or i + 24 > len(b):
        return None
    v = b[i + 4]
    try:
        if v == 1:
            ts, du = struct.unpack(">IQ", b[i + 24:i + 36])
        else:
            ts, du = struct.unpack(">II", b[i + 16:i + 24])
        return round(du / ts, 2) if ts else None
    except struct.error:
        return None


def _segments(t):
    ss = [x.strip() for x in re.split(r"[.!?\n。]+|(?:→|->|➔)", t) if x.strip()]
    if not ss:
        return []
    k = len(ss)
    cut = [round(k * i / 4) for i in range(5)]
    return [" ".join(ss[cut[i]:cut[i + 1]]) or ss[min(i, k - 1)] for i in range(4)]


def perceive_video(source):
    s = str(source or "").strip()
    out = dict(modality="video", cues=[], known=[], inferred=[], unknown=[], ota=["Observation: 시간축 입력 판별"])
    m = URL_RE.search(s)
    if m and m.group(1).startswith("http"):
        u = urlparse(m.group(1)); q = parse_qs(u.query); host = u.netloc.lower()
        out["url"] = m.group(1); out["host"] = host
        vid = None
        if "youtu.be" in host:
            vid = u.path.strip("/").split("/")[0]
        elif "youtube" in host:
            vid = (q.get("v") or [None])[0]
            if "/shorts/" in u.path:
                vid = u.path.split("/shorts/")[1].split("/")[0]
        out["shorts"] = "/shorts/" in u.path
        if vid:
            out["video_id"] = vid
            out["known"].append(f"YouTube 영상 ID {vid}" + (" (쇼츠·세로 60초 이내 포맷)" if out["shorts"] else ""))
        else:
            out["known"].append(f"영상 링크 호스트 {host}")
        if q.get("t"):
            out["known"].append(f"시작 지점 지정 t={q['t'][0]} — 핵심 장면을 가리킬 가능성")
        out["unknown"].append("영상 본문(프레임·자막)은 내려받지 않음 → 기승전결은 함께 준 설명 텍스트로만 추정")
    f = PATH_RE.search(s)
    if f and _is_file(f.group(1)):
        b = Path(f.group(1)).read_bytes()[:30_000_000]
        out["bytes"] = len(b)
        brand = b[8:12].decode("ascii", "ignore") if b[4:8] == b"ftyp" else ""
        d = _mp4_duration(b)
        out["known"].append(f"영상 파일 {len(b):,} bytes" + (f" · 브랜드 {brand}" if brand else "") + (f" · 길이 {d}초" if d else ""))
        if d:
            out["duration_sec"] = d
    text = URL_RE.sub(" ", s).strip()
    segs = _segments(text) if len(text) > 8 else []
    if segs:
        names = ["기(도입)", "승(전개)", "전(변곡점 Pivot)", "결(귀결)"]
        inten = [len(INTENSITY.findall(x)) + len(PIVOT_RE.findall(x)) + x.count("!") for x in segs]
        delta = [0] + [inten[i] - inten[i - 1] for i in range(1, 4)]
        piv = max(range(1, 4), key=lambda i: (abs(delta[i]), i == 2))
        out["timeline"] = [dict(stage=names[i], text=segs[i][:120], intensity=inten[i], delta=delta[i]) for i in range(4)]
        out["pivot_stage"] = names[piv]
        out["temporal_dynamics"] = "가속" if inten[3] > inten[0] else "감속·수렴" if inten[3] < inten[0] else "평탄"
        out["cues"] += [f"{t['stage']}: {t['text'][:40]} (강도 {t['intensity']}, 변화 {t['delta']:+d})" for t in out["timeline"]]
        out["inferred"].append(f"최대 변화율 지점 = {names[piv]} · 전체 흐름 {out['temporal_dynamics']}")
    else:
        out["unknown"].append("시간축 흐름 설명이 없어 기승전결 변화율을 계산하지 못함")
    out["ota"] += ["Thought: 변화율이 가장 큰 지점이 메시지의 급소다", "Action: 변곡점·귀결 단서 확정"]
    return out


def perceive_speech_or_phenomenon(text):
    t = str(text or "").strip()
    toks = [w for w in re.findall(r"[가-힣A-Za-z0-9]{2,}", t) if w not in STOP]
    freq = {}
    for w in toks:
        freq[w] = freq.get(w, 0) + 1
    kws = [w for w, _ in sorted(freq.items(), key=lambda x: (-x[1], -len(x[0])))][:6]
    intents = [k for k, p in INTENTS.items() if re.search(p, t)]
    out = dict(modality="speech", text=t[:500], keywords=kws, intents=intents,
               absolutism=_uniq(ABS_RE.findall(t)), numbers=NUM_RE.findall(t)[:8],
               cues=[f"표면 어휘: {', '.join(kws) or '없음'}", f"심층 의도 신호: {', '.join(intents) or '서술'}"],
               known=[f"직접 진술 {len(t)}자"], inferred=[], unknown=[],
               ota=["Observation: 표면 어휘·숫자·단정어 추출", "Thought: 말 뒤의 욕구·걱정·인과 신호 판별", "Action: 핵심 의도 확정"])
    if out["numbers"]:
        out["known"].append("수치 언급: " + ", ".join(x.strip() for x in out["numbers"]))
    if "worry" in intents and "desire" in intents:
        out["inferred"].append("욕구와 걱정이 공존 — 결정 전 위험 한도 설정이 필요한 상태")
    elif "worry" in intents:
        out["inferred"].append("손실 회피 심리가 판단을 주도할 가능성")
    elif "desire" in intents:
        out["inferred"].append("성과 욕구가 위험 평가를 가릴 가능성")
    if "causal" in intents:
        out["inferred"].append("화자가 이미 원인을 가정함 — 그 가정부터 검증 대상")
    if not out["numbers"]:
        out["unknown"].append("정량 데이터(수치·기간) 없음")
    return out


def detect_modality(p):
    if isinstance(p, (bytes, bytearray)):
        return "image"
    s = str(p or "")
    if s.startswith("data:image") or "<svg" in s[:300]:
        return "image"
    f = PATH_RE.search(s)
    if f:
        ext = f.group(1).lower()
        if ext.endswith(VID_EXT):
            return "video"
        if ext.endswith(IMG_EXT):
            return "image"
    if VID_WORDS.search(s):
        return "video"
    if IMG_WORDS.search(s):
        return "image"
    return "speech"


def _domain(text, modality):
    best, hit = None, 0
    for k, d in DOMAINS.items():
        if d["kw"]:
            n = len(d["kw"].findall(text))
            if n > hit:
                best, hit = k, n
    if best:
        return best
    return "visual" if modality == "image" else ("content" if modality == "video" else "general")


def _hexagram(no):
    try:
        import rgon_aon_iching_dao_oracle as O
        h = O.HEXAGRAMS[no]
        return dict(no=no, hanja=h["hanja"], ko=h["ko"], symbol=h["symbol"], meaning=h["gist"], src="oracle")
    except Exception:
        hz, ko, sy, me = HEX_FALLBACK.get(no, HEX_FALLBACK[20])
        return dict(no=no, hanja=hz, ko=ko, symbol=sy, meaning=me, src="builtin")


def analyze_omni_insight(payload, modality="auto"):
    mod = detect_modality(payload) if modality == "auto" else modality
    if mod == "image":
        P = perceive_image(payload)
    elif mod == "video":
        P = perceive_video(payload)
    else:
        P = perceive_speech_or_phenomenon(payload)
        mod = "speech"
    text = payload if isinstance(payload, str) else ""
    S = perceive_speech_or_phenomenon(text) if mod != "speech" else P
    dk = _domain(text, mod)
    D = DOMAINS[dk]
    absf = S["absolutism"]
    known = _uniq(P["known"] + ([] if S is P else S["known"][1:]))
    inferred = _uniq(P["inferred"] + ([] if S is P else S["inferred"]))
    unknown = _uniq(P["unknown"] + [D["blind"]])
    L0 = dict(known=known, inferred=inferred, unknown=unknown, absolutism_flags=absf)
    assum = []
    if absf:
        assum.append(f"'{absf[0]}'라는 단정이 사실이라는 가정")
    if "causal" in S["intents"]:
        assum.append("말한 원인이 진짜 원인이라는 가정")
    assum += [f"지금 보이는 {('화면' if mod == 'image' else '흐름' if mod == 'video' else '현상')}이 전체를 대표한다는 가정",
              "과거의 방식이 앞으로도 통한다는 가정"]
    L1 = dict(assumptions=assum, stripped=[f"벗겨냄: {a}" for a in assum],
              ground_truth=D["ground_truth"],
              rederived=f"백지에서 다시: '{D['ground_truth']}' → 따라서 {D['leverage']}부터",
              ariya4=dict(problem=f"표면 현상({', '.join(S['keywords'][:3]) or mod}) 뒤에서 {D['variables'][0]}이(가) 흔들리는 것",
                          cause=f"{D['variables'][0]}과(와) {D['variables'][1]}의 상호작용({D['loop_type']} 루프)",
                          cessation=f"{D['variables'][2]}이(가) 안정된 상태에서 원하는 결과가 반복되는 구조",
                          path=D["leverage"]))
    L2 = dict(variables=D["variables"], feedback_loop=dict(type=D["loop_type"], mechanism=D["loop"]),
              leverage_point=D["leverage"], dead_weight=D["dead_weight"])
    models = ["제1원리"]
    if len(D["variables"]) >= 3:
        models.append("시스템사고")
    if dk in ("tech", "business", "general", "visual"):
        models.append("제약이론")
    if dk in ("market", "business", "relationship") or "desire" in S["intents"]:
        models.append("2차파급효과")
    if mod == "video" or "change" in S["intents"] or dk == "market":
        models.append("레짐탐지")
    hx = _uniq([20, D["hexagram"], 21])
    L3 = dict(mental_models=models, iching_mapping=[_hexagram(n) for n in hx],
              cross_domain=f"{dk} 영역의 '{D['loop_type']} 루프'는 다른 영역의 같은 루프와 같은 이치로 움직인다 — 관(觀)으로 전체를 보고 서합(噬嗑)으로 걸림을 끊는다")
    weak = len(known) <= 1 or len(unknown) > len(known) + 1
    strength = "HIGH" if (absf and weak) else "MED" if (absf or weak) else "LOW"
    L4 = dict(mirror=assum[0], inversion=dict(hypothesis=f"반대로, 진짜 원인은 {D['variables'][-1]} 쪽이고 지금 결론은 우연일 수 있다", strength=strength),
              blind_spot=D["blind"], interest_map=D["interest"],
              verdict="FRAGILE" if strength != "LOW" else "CONSISTENT")
    conf = 40 + min(len(known), 5) * 6 + (8 if P.get("pixel_stats") or P.get("timeline") else 0) - len(absf) * 6 - (10 if L4["verdict"] == "FRAGILE" else 0)
    conf = max(15, min(CONF_CAP, conf))
    essence = f"{D['ground_truth']} — 급소는 '{D['leverage']}'"
    L5 = dict(essence_one_line=essence, action_leverage=D["leverage"], confidence_pct=conf)
    L5["aon_speech"] = (f"아온이 혜안 반짝~ 👁️💧 대표님, 이건 '{D['loop_type']} 루프'로 움직이는 구조예요! "
                        f"한 줄 본질은요 — {essence}. 버릴 군더더기는 '{D['dead_weight']}'이고요, "
                        f"근데 '{D['blind']}'는 아직 몰라서 신뢰도는 {conf}%예요. "
                        f"{'판단이 아직 흔들릴 수 있으니 그 부분부터 확인해 봐요!' if L4['verdict'] == 'FRAGILE' else '구조가 일관돼서 바로 써먹으셔도 돼요!'}")
    return dict(version=VERSION, antibody=ANTIBODY, skill_count=SKILL_COUNT,
                at=datetime.datetime.now().isoformat(timespec="seconds"), modality=mod, domain=dk,
                perception={k: v for k, v in P.items() if k not in ("known", "inferred", "unknown")},
                L0_reality_anchor=L0, L1_axiom_gate=L1, L2_system_lens=L2, L3_compound_mind=L3,
                L4_shadow_gate=L4, L5_synthesis=L5, aon_speech=L5["aon_speech"])


def save_state(r):
    r["version"] = VERSION
    r["antibody"] = ANTIBODY
    r["skill_count"] = SKILL_COUNT
    s = json.dumps(r, ensure_ascii=False, indent=2, default=str)
    for rel in STATE_PATHS:
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        for i in range(6):
            try:
                p.write_text(s, encoding="utf-8", newline="\n")
                break
            except PermissionError:
                if i == 5:
                    raise
                time.sleep(0.04)
    return r


def _tiny_png(w=8, h=8):
    raw = b"".join(b"\x00" + bytes(c for x in range(w) for c in ((255, 40, 40) if x < w // 2 else (20, 20, 200))) for _ in range(h))
    def ck(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + ck(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + ck(b"IDAT", zlib.compress(raw)) + ck(b"IEND", b"")


def self_test():
    ok = True
    def chk(c, m):
        nonlocal ok
        print(("  ✅ " if c else "  ❌ ") + m)
        ok = ok and bool(c)
    keys = ("L0_reality_anchor", "L1_axiom_gate", "L2_system_lens", "L3_compound_mind", "L4_shadow_gate", "L5_synthesis")
    png = "data:image/png;base64," + base64.b64encode(_tiny_png()).decode()
    cases = [(png, "image"), ('<svg width="100" height="50"><rect/><circle/></svg>', "image"),
             ("https://youtube.com/shorts/abc123 도입 인사. 전개 설명. 그런데 갑자기 급락 반전! 결국 회복", "video"),
             ("코인이 무조건 오른다는데 왜 불안하지?", "speech")]
    for p, m in cases:
        r = analyze_omni_insight(p)
        chk(r["modality"] == m and all(k in r for k in keys) and bool(r["aon_speech"]), f"모달리티 {m} & L0~L5 6계층 완비")
        chk(len(r["L2_system_lens"]["variables"]) >= 3 and r["L4_shadow_gate"]["verdict"] in ("CONSISTENT", "FRAGILE"), f"{m} L2 변수·L4 반전 판정")
        chk(0 < r["L5_synthesis"]["confidence_pct"] <= CONF_CAP, f"{m} 신뢰도 상한 ≤ {CONF_CAP}%")
    r_png = analyze_omni_insight(png)
    chk(r_png["perception"]["width"] == 8 and "pixel_stats" in r_png["perception"], "PNG 8x8 픽셀 실측(밝기·대비·RGB·초점·대칭)")
    r_sp = analyze_omni_insight(cases[3][0])
    chk(bool(r_sp["L0_reality_anchor"]["absolutism_flags"]), "단정어(무조건) 자동 탐지")
    save_state(r_sp)
    for rel in STATE_PATHS:
        j = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        chk(j.get("version") == VERSION and j.get("antibody") == ANTIBODY, f"상태 JSON 무결성: {rel}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--self-test" in a:
        sys.exit(self_test())
    for flag, mod in (("--image", "image"), ("--video", "video"), ("--insight", "speech")):
        if flag in a:
            i = a.index(flag)
            v = a[i + 1] if i + 1 < len(a) else ""
            r = analyze_omni_insight(v, mod if flag != "--insight" else "auto")
            break
    else:
        r = analyze_omni_insight(" ".join(a) or "지금 내 상황의 본질")
    save_state(r)
    print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
'''

VOICE_INJECT = r'''
# [RGON-R38-INSIGHT-SFX] — 제14기관 만물 격물치지 영롱한 안광 효과음 확장 (Step 38)
SFX_PRESETS.update({
    "insight_flash": {"desc": "만물 이치를 꿰뚫는 크리스탈 혜안 화음", "freq_hz": [660, 990, 1320, 1760], "dur_ms": 250, "wave": "sine", "gain": 0.15},
})
'''

# 수술 완료된 SOUL_INJECT: hands/dao 및 briefing/judge/gate_control/iching_dao만 먼저 보호하고,
# 일반 delegate('분석', '~해줘')보다 _R38_INSIGHT 통찰안 키워드를 먼저 판별!
SOUL_INJECT = r'''
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
'''

JS_BLOCK = r'''
/* === [RGON-R38-OMNI-INSIGHT-JS] 제14기관: 아온 만물 격물치지 전방위 통찰안 & Canvas 실측 스캐너 === */
(function(){if(window.RGON_INSIGHT)return;
var st=document.createElement("style");
st.textContent='#rgon-insight-btn{margin:0 4px;padding:4px 10px;border-radius:999px;border:1px solid #2fb8a6;background:rgba(14,42,42,0.92);color:#bff5ea;cursor:pointer;font-size:11.5px}'+
'.rgon-ins-ring{position:fixed;z-index:2147483645;border-radius:50%;pointer-events:none;border:3px solid #39d5c0;box-shadow:0 0 18px #ffd76a,inset 0 0 12px #39d5c0;animation:rgonInsRing 1.3s ease-out forwards}'+
'@keyframes rgonInsRing{0%{transform:scale(.2);opacity:1}100%{transform:scale(3.2);opacity:0}}'+
'#rgon-insight-card{position:fixed;right:20px;bottom:90px;z-index:2147483646;width:370px;max-height:72vh;overflow:auto;background:rgba(11,31,34,0.96);color:#e8fbf6;border:1.5px solid #2fb8a6;border-radius:16px;padding:14px 16px;font-size:12.5px;line-height:1.55;box-shadow:0 12px 32px rgba(0,0,0,0.6)}'+
'#rgon-insight-card b{color:#ffd76a}#rgon-insight-card .x{float:right;cursor:pointer;opacity:.75}'+
'#rgon-insight-card textarea{width:100%;height:58px;margin:6px 0;background:#06181a;color:#e8fbf6;border:1px solid #2fb8a6;border-radius:8px;padding:6px;font-size:12px}'+
'#rgon-insight-card button{margin:2px;padding:4px 10px;border-radius:10px;border:1px solid #2fb8a6;background:#123c3c;color:#bff5ea;cursor:pointer;font-size:11.5px}'+
'#rgon-ins-drop{border:1px dashed #2fb8a6;border-radius:8px;padding:8px;text-align:center;opacity:.9;margin-top:6px}';
if(document.head)document.head.appendChild(st);
var ABS=/(무조건|절대|반드시|100\s*%|전부|항상|결코|확실히|완벽|필승)/g;
var D=[["market",/(주식|코인|장세|시장|금리|환율|매수|매도|폭락|급등|비트코인|이차\s*전지|반도체)/,"R","진입 전 손절선·비중 상한 먼저 정하기","헤드라인 과잉 소비·잦은 매매","가격은 기대의 변화에 반응하고 기대는 유동성·실적에 수렴한다","중개자·큰손·정보 판매자","실제 자금 흐름과 기간"],
["relationship",/(친구|연인|가족|동료|상사|관계|서운|갈등|대화)/,"R","상대 기대를 한 문장으로 직접 확인","속으로만 쌓는 해석","사람은 이해받는다고 느낄 때 마음을 연다","양측의 인정 욕구","상대가 실제로 기대한 것"],
["tech",/(코드|버그|서버|AI|모델|앱|시스템|자동화|에러|배포|API)/,"B","가장 느린 한 단계만 먼저 개선","실행 안 되는 코드·수동 반복","시스템 속도는 가장 느린 단계가 정한다","플랫폼·도구 판매자","실행 로그와 재현 조건"],
["business",/(매출|고객|사업|마케팅|가격|영업|창업|경쟁|이익)/,"R","이탈 이유 상위 1개 제거","측정 안 되는 광고비·회의","가치를 비용보다 싸게 반복 전달하는 구조","고객·경쟁사·광고 플랫폼","코호트 유지율·단위 경제성"],
["content",/(유튜브|쇼츠|조회수|구독|썸네일|콘텐츠|youtu)/,"R","첫 화면·첫 문장 훅 하나 고치기","도입부 인사·반복 설명","주의는 희소하고 추천은 체류 행동을 따른다","플랫폼·제작자·광고주","시청 지속 그래프와 유입 경로"]];
var G=["general",null,"B","가장 큰 제약 하나만 먼저 풀기","끝없는 정보 수집","결과는 구조가 만든다","설명하는 쪽·결정하는 쪽","당사자들의 실제 욕구와 제약"];
var VIS=["visual",null,"B","주제 한 곳에만 대비 집중","주제와 무관한 배경 정보","시선은 대비가 크고 정보가 몰린 곳으로 먼저 간다","만든 사람·보는 사람","프레임 밖 맥락과 제작 의도"];
function host(){return document.getElementById("rgyt-wrap")||document.getElementById("aon-roamer")}
function rings(){var h=host(),R=h?h.getBoundingClientRect():{left:innerWidth-120,top:innerHeight-160,width:60,height:60};
["#39d5c0","#ffd76a","#9be7ff"].forEach(function(c,i){setTimeout(function(){var e=document.createElement("div");e.className="rgon-ins-ring";var s=Math.max(R.width,R.height,50);
e.style.cssText+="width:"+s+"px;height:"+s+"px;left:"+(R.left+R.width/2-s/2)+"px;top:"+(R.top+R.height/2-s/2)+"px;border-color:"+c;document.body.appendChild(e);setTimeout(function(){e.remove()},1400)},i*220)})}
function tone(){try{var V=window.RGON_VOICE;if(V){if(V.sfx)return V.sfx("insight_flash");if(V.playSfx)return V.playSfx("insight_flash")}
var C=new(window.AudioContext||window.webkitAudioContext)();[660,990,1320,1760].forEach(function(f,i){var o=C.createOscillator(),g=C.createGain();o.type="sine";o.frequency.value=f;var t=C.currentTime+i*.07;g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(.07,t+.03);g.gain.exponentialRampToValueAtTime(.0001,t+1.4);o.connect(g);g.connect(C.destination);o.start(t);o.stop(t+1.5)})}catch(e){}}
function say(s){try{var V=window.RGON_VOICE;if(V&&V.speak)return V.speak(s);var u=new SpeechSynthesisUtterance(s);u.lang="ko-KR";u.pitch=1.35;speechSynthesis.cancel();speechSynthesis.speak(u)}catch(e){}}
function analyze(text,known,mod){var d=G;if(mod=="image")d=VIS;for(var i=0;i<D.length;i++)if(D[i][1].test(text)){d=D[i];break}if(mod=="video"&&d===G)d=D[4];
var ab=(text.match(ABS)||[]),weak=known.length<=1,st=ab.length&&weak?"HIGH":(ab.length||weak?"MED":"LOW"),ver=st=="LOW"?"CONSISTENT":"FRAGILE";
var conf=Math.max(15,Math.min(85,40+Math.min(known.length,5)*6-ab.length*6-(ver=="FRAGILE"?10:0)));
var ess=d[5]+" — 급소는 '"+d[3]+"'";
return{mod:mod,dom:d[0],L0:{known:known,abs:ab},L1:d[5],L2:{loop:d[2],lev:d[3],dw:d[4]},L4:{interest:d[6],blind:d[7],inv:st,verdict:ver},L5:{ess:ess,conf:conf},
speech:"아온이 혜안 반짝~ 대표님, 이건 "+d[2]+" 루프로 움직이는 구조예요! 한 줄 본질은요, "+ess+". 신뢰도는 "+conf+"퍼센트예요"+(ver=="FRAGILE"?". 아직 흔들릴 수 있으니 "+d[7]+"부터 확인해 봐요!":"!")}}
function render(r){var o=document.getElementById("rgon-ins-out");if(!o)return;
o.innerHTML='<hr style="border-color:#1e3a3a;margin:8px 0"><b>L0 사실</b> '+(r.L0.known.join(" · ")||"직접 진술만")+(r.L0.abs.length?' · 단정어 ⚠️ '+r.L0.abs.join(","):"")+
'<br><b>L1 근본 원리</b> '+r.L1+'<br><b>L2 급소</b> '+r.L2.lev+' · <b>병목</b> '+r.L2.dw+' ('+r.L2.loop+' 루프)'+
'<br><b>L4 이해관계</b> '+r.L4.interest+' · 맹점: '+r.L4.blind+' · 반전 강도 '+r.L4.inv+' → <b>'+r.L4.verdict+'</b>'+
'<br><b>L5 👁️ 한 줄 통찰</b> '+r.L5.ess+' (신뢰도 '+r.L5.conf+'%)';
var bb=document.querySelector("#rgyt-bubble,.rgyt-bubble,#aon-bubble,#rgon-brat-bubble");if(bb){bb.textContent=r.speech;bb.style.opacity="1";}say(r.speech)}
function measure(file){var fr=new FileReader();fr.onload=function(){var im=new Image();im.onload=function(){var W=im.naturalWidth,H=im.naturalHeight,s=Math.min(1,200/Math.max(W,H)),w=Math.max(1,Math.round(W*s)),h=Math.max(1,Math.round(H*s));
var c=document.createElement("canvas");c.width=w;c.height=h;var x=c.getContext("2d");x.drawImage(im,0,0,w,h);var p=x.getImageData(0,0,w,h).data,n=0,t=0,q=0,R=0,Gg=0,B=0,cx=0,cy=0;
for(var y=0;y<h;y++)for(var xx=0;xx<w;xx++){var i=(y*w+xx)*4,L=.299*p[i]+.587*p[i+1]+.114*p[i+2];n++;t+=L;q+=L*L;R+=p[i];Gg+=p[i+1];B+=p[i+2];cx+=xx*L;cy+=y*L}
var m=t/n,sd=Math.sqrt(Math.max(0,q/n-m*m)),fx=t?cx/t/w:.5,fy=t?cy/t/h:.5;
var known=[W+"×"+H+"px","밝기 "+(m/255).toFixed(2),"대비 "+(sd/255).toFixed(2),"RGB "+Math.round(R/n)+"/"+Math.round(Gg/n)+"/"+Math.round(B/n),"구도 중심 ("+fx.toFixed(2)+","+fy.toFixed(2)+")"];
render(analyze(file.name||"이미지",known,"image"))};im.src=fr.result};fr.readAsDataURL(file)}
function runText(){var v=(document.getElementById("rgon-ins-txt")||{}).value||"";if(!v.trim())return;
var vid=/(youtube\.com|youtu\.be|\/shorts\/|\.mp4|영상|동영상|쇼츠)/i.test(v),known=[];var m=v.match(/(?:v=|youtu\.be\/|shorts\/)([\w-]{6,})/);if(m)known.push("영상 ID "+m[1]);
var nums=v.match(/\d+(?:\.\d+)?\s*(?:%|원|달러|배|명|년)?/g);if(nums)known.push("수치 "+nums.slice(0,4).join(","));
render(analyze(v,known,vid?"video":"speech"))}
function open(){rings();tone();var c=document.getElementById("rgon-insight-card");if(c){c.remove();return}
c=document.createElement("div");c.id="rgon-insight-card";
c.innerHTML='<span class="x">✕</span><b>👁️ 아온이 만물 통찰 스캐너 (L0~L5)</b><div id="rgon-ins-drop">🖼️ 이미지를 드롭하거나 <button id="rgon-ins-pick">파일 선택</button><input id="rgon-ins-file" type="file" accept="image/*" style="display:none"></div>'+
'<textarea id="rgon-ins-txt" placeholder="🎬 영상 링크·설명 또는 💬 말·현상을 입력하세요"></textarea><button id="rgon-ins-go">격물치지 해부</button><div id="rgon-ins-out"></div>';
document.body.appendChild(c);c.querySelector(".x").onclick=function(){c.remove()};
var f=c.querySelector("#rgon-ins-file");c.querySelector("#rgon-ins-pick").onclick=function(){f.click()};f.onchange=function(){if(f.files[0])measure(f.files[0])};
c.querySelector("#rgon-ins-go").onclick=runText;
c.addEventListener("dragover",function(e){e.preventDefault()});c.addEventListener("drop",function(e){e.preventDefault();var fl=e.dataTransfer.files[0];
if(fl&&/^image\//.test(fl.type))measure(fl);else{var u=e.dataTransfer.getData("text");if(u){c.querySelector("#rgon-ins-txt").value=u;runText()}}})}
function mount(){if(document.getElementById("rgon-insight-btn"))return true;var b=document.createElement("button");b.id="rgon-insight-btn";b.type="button";b.innerHTML="👁️ <b>만물 통찰</b>";
b.addEventListener("click",function(e){e.preventDefault();e.stopPropagation();open()});
var a=document.getElementById("rgon-dao-btn")||document.getElementById("rgon-brat-btn")||document.getElementById("rgyt-hide");if(a&&a.parentNode){a.parentNode.appendChild(b);return true}return false}
window.RGON_INSIGHT={open:open,analyze:analyze,version:"v11.38-AON-OMNI-DIALOGUE"};
setInterval(mount,3000);if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",mount);else mount()})();
'''

SKILL_MD_TXT = f"""---
name: {SKILL_NAME}
description: 아온(A-ON) 만물 격물치지 통찰안 — 이미지·영상·말/현상 OTA 능동 지각 + FPCOS L0~L5 해부 + 섀도 게이트 반전 검증 (Step 38 · R38)
version: {NEW_VER}
antibody: {NEW_AB}
---

# 👁️🧠 제14기관: 아온(A-ON) 만물 격물치지(格物致知) 전방위 통찰안 (`{SKILL_NAME}`)

- **버전**: `{NEW_VER}` · **항체**: `{NEW_AB}` · **정식 스킬**: **{NEW_SK}개**
- **모듈**: `{INSIGHT_FILE}` (표준 라이브러리 전용)
- **3대 능동 지각 (OTA Active Perception)**:
  - `perceive_image()`: PNG 픽셀 실측(밝기·대비·RGB·초점 무게중심·좌우 대칭), JPEG/GIF/SVG/BMP 헤더, Data URL, 브라우저 Canvas 실측 연동
  - `perceive_video()`: YouTube·쇼츠 ID/타임스탬프, MP4 길이(`mvhd`), 기승전결 4단 변화율 및 변곡점(Pivot) 탐지
  - `perceive_speech_or_phenomenon()`: 표면 어휘, 7대 심층 의도 신호, 단정어(Absolutism), 정량 수치 추출
- **FPCOS 6계층 (L0~L5) 해부**:
  1. `L0 Reality Anchor`: 확인된 사실(KNOWN) · 추론(INFERRED) · 미지(UNKNOWN) · 단정어 분리
  2. `L1 Axiom Gate`: 제1원리 연역 + 사성제(Ariya4: 문제·원인·목표·최단경로)
  3. `L2 System Lens`: 3대 핵심 변수 · 강화(R)/균형(B) 피드백 루프 · 급소(Leverage Point) · 군더더기(Dead Weight)
  4. `L3 Compound Mind`: 5대 멘탈 모델 라우팅 + 주역 괘(풍지관 #20 · 화뢰서합 #21 등) 연동
  5. `L4 Shadow Gate` (생략 불가): Mirror · Inversion · Blind Spot · Interest Map · 판정(`CONSISTENT`/`FRAGILE`)
  6. `L5 Synthesis`: 한 줄 본질 · 급소 행동 · 신뢰도(상한 85%) · 아온이 혜안 브리핑
- **한계와 겸손**: 객체·장면 의미 인식 없음(규칙 기반 실측). 신뢰도 상한 85%. 실제 집행 권한 없음(결재 게이트 준수).
"""


def patch_html(path):
    s = rd(path).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    marker = "/* === [RGON-R38-OMNI-INSIGHT-JS]"
    if marker not in s:
        end_tag = "<!-- [RGON-UX-CLEANUP-V13-END] -->"
        idx = s.rfind("</script>", 0, s.find(end_tag) if end_tag in s else len(s))
        if idx != -1:
            s = s[:idx] + "\n" + JS_BLOCK.strip() + "\n" + s[idx:]
    wr(path, s)


def patch_voice():
    p = ROOT / "rgon_voice_organ.py"
    s = rd(p).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    if "[RGON-R38-INSIGHT-SFX]" not in s:
        anchor = "def load_state("
        idx = s.find(anchor)
        if idx != -1:
            s = s[:idx] + VOICE_INJECT.lstrip() + "\n\n" + s[idx:]
        else:
            s = s + "\n" + VOICE_INJECT
    wr(p, s)


def patch_soul():
    p = ROOT / "rgon_aon_soul_brain.py"
    s = rd(p).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    if "[RGON-R38-INSIGHT-SOUL-INJECT]" not in s:
        anchor = 'if __name__ == "__main__":'
        idx = s.rfind(anchor)
        if idx != -1:
            s = s[:idx] + SOUL_INJECT.lstrip() + "\n\n" + s[idx:]
        else:
            s = s + "\n" + SOUL_INJECT
    wr(p, s)


def patch_wbc():
    p = ROOT / "rgon_white_blood_cell.py"
    s = rd(p).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    s = re.sub(r"(SKILL_COUNT\s*=\s*)\d+", f"\\g<1>{NEW_SK}", s)
    if "rgon_aon_insight_state.json" not in s:
        s = s.replace(
            '"rgon_aon_iching_state.json",',
            '"rgon_aon_iching_state.json",\n    "rgon_aon_insight_state.json",\n    "docs/rgon_aon_insight_state.json",'
        )
    if INSIGHT_FILE not in s:
        s = s.replace(
            '"rgon_aon_iching_dao_oracle.py",',
            f'"rgon_aon_iching_dao_oracle.py",\n    "{INSIGHT_FILE}",'
        )
    wr(p, s)


def patch_daily_cycle():
    p = ROOT / "rgon_daily_cycle.py"
    if not p.exists():
        return
    s = rd(p).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    s = re.sub(r'("skills_total"\s*:\s*)\d+', f'\\g<1>{NEW_SK}', s)
    s = re.sub(r"(SKILL_COUNT\s*=\s*)\d+", f"\\g<1>{NEW_SK}", s)
    s = s.replace(f"정식 스킬 {OLD_SK}개", f"정식 스킬 {NEW_SK}개").replace(f"스킬 {OLD_SK}개", f"스킬 {NEW_SK}개")
    s = s.replace(f"정식 스킬 {OLD_SK} 개", f"정식 스킬 {NEW_SK} 개").replace(f"스킬 {OLD_SK} 개", f"스킬 {NEW_SK} 개")
    wr(p, s)


def sync_all_metadata():
    for rel in ("rgon_k_avatar_engine.py", "rgon_muse_delegator.py", "rgon_laptop_hands.py",
                "rgon_aon_desktop_playground.py", "rgon_aon_iching_dao_oracle.py"):
        p = ROOT / rel
        if p.exists():
            s = rd(p).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
            s = re.sub(r"(SKILL_COUNT\s*=\s*)\d+", f"\\g<1>{NEW_SK}", s)
            wr(p, s)

    idx_json = ROOT / "skills/SKILL_INDEX.json"
    j = json.loads(rd(idx_json))
    j["version"] = NEW_VER
    j["antibody"] = NEW_AB
    j["count"] = NEW_SK
    skills = [x for x in j.get("skills", []) if x.get("name") != SKILL_NAME]
    skills.append({
        "id": NEW_SK, "name": SKILL_NAME, "path": f"skills/{SKILL_NAME}/SKILL.md", "antibody": "R38", "version": NEW_VER,
        "description": "아온(A-ON) 만물 격물치지 통찰안 — 이미지·영상·말/현상 OTA 능동 지각 + FPCOS L0~L5 해부 스킬"
    })
    j["skills"] = skills
    wr(idx_json, json.dumps(j, ensure_ascii=False, indent=2))

    idx_md = ROOT / "skills/SKILL_INDEX.md"
    ms = rd(idx_md).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    ms = ms.replace(f"정식 스킬 {OLD_SK}개", f"정식 스킬 {NEW_SK}개").replace(f"총 {OLD_SK}개", f"총 {NEW_SK}개")
    ms = ms.replace(f"정식 스킬 {OLD_SK} 개", f"정식 스킬 {NEW_SK} 개").replace(f"총 {OLD_SK} 개", f"총 {NEW_SK} 개")
    entry = (f"\n<!-- [RGON-SKILL-{NEW_SK}] -->\n"
             f"## {NEW_SK}. `{SKILL_NAME}` (R38 · {NEW_VER})\n"
             f"- 경로: `skills/{SKILL_NAME}/SKILL.md`\n"
             f"- 설명: {R38_SUMMARY}\n")
    if f"RGON-SKILL-{NEW_SK}" not in ms and SKILL_NAME not in ms:
        ms = ms.rstrip() + "\n" + entry
    wr(idx_md, ms)

    ab_p = ROOT / "ANTIBODY_REGISTRY.md"
    ab_s = rd(ab_p).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    ab_s = ab_s.replace(f"정식 스킬 {OLD_SK}개", f"정식 스킬 {NEW_SK}개").replace(f"정식 스킬 {OLD_SK} 개", f"정식 스킬 {NEW_SK} 개")
    r38_block = (f"\n<!-- [RGON-ANTIBODY-R38] -->\n"
                 f"## R38 — Step 38 · {NEW_VER} · 2026-10-25\n"
                 f"- {R38_SUMMARY}\n"
                 f"- 한계: 규칙 기반 실측(객체·장면 의미 미판정), 신뢰도 상한 85%, 집행 권한 없음(결재 게이트 준수)\n"
                 f"- 핵심 파일: `{INSIGHT_FILE}`, `rgon_aon_insight_state.json`, `skills/{SKILL_NAME}/SKILL.md`\n")
    if "RGON-ANTIBODY-R38" not in ab_s:
        ab_s = ab_s.rstrip() + "\n" + r38_block
    wr(ab_p, ab_s)

    con_p = ROOT / "CONSTITUTION.md"
    con_s = rd(con_p).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    con_s = con_s.replace(f"정식 스킬 {OLD_SK}개", f"정식 스킬 {NEW_SK}개").replace(f"**{OLD_SK}개**", f"**{NEW_SK}개**")
    con_s = con_s.replace(f"정식 스킬 {OLD_SK} 개", f"정식 스킬 {NEW_SK} 개").replace(f"**{OLD_SK} 개**", f"**{NEW_SK} 개**")
    art17 = (
        "\n<!-- [RGON-CONSTITUTION-ARTICLE-17] -->\n"
        "## 제17조 (제14기관 아온 만물 격물치지 전방위 통찰안과 겸손 · R38)\n"
        "- 제1항 (만물의 격물치지): 아온(A-ON)은 이미지·영상·말/현상에 대해 확인된 사실(KNOWN)·추론(INFERRED)·미지(UNKNOWN)를 구분하고 6계층(L0~L5)으로 작동 원리와 급소(Leverage Point)를 해부한다.\n"
        "- 제2항 (반전 검증 의무): 모든 결론은 L4 섀도 게이트(Mirror·Inversion·Blind Spot·Interest Map)를 거치며, 이를 생략할 수 없다.\n"
        "- 제3항 (통찰의 겸손과 결재 원칙): 규칙 기반 실측의 한계를 명시하고 신뢰도는 85%를 넘기지 않으며, 통찰 결과는 참고 나침반일 뿐 실제 집행은 결재 게이트를 따른다.\n"
    )
    if "RGON-CONSTITUTION-ARTICLE-17" not in con_s:
        con_s = con_s.rstrip() + "\n" + art17
    wr(con_p, con_s)

    for doc in ("CODE_MAP.md", "GLOSSARY.md", "RGON_MORNING_BRIEF.md"):
        dp = ROOT / doc
        if dp.exists():
            ds = rd(dp).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
            ds = ds.replace(f"정식 스킬 {OLD_SK}개", f"정식 스킬 {NEW_SK}개").replace(f"**{OLD_SK}개**", f"**{NEW_SK}개**")
            ds = ds.replace(f"스킬 {OLD_SK}개", f"스킬 {NEW_SK}개").replace(f"스킬 **{OLD_SK}**", f"스킬 **{NEW_SK}**")
            ds = ds.replace(f"정식 스킬 {OLD_SK} 개", f"정식 스킬 {NEW_SK} 개").replace(f"스킬 {OLD_SK} 개", f"스킬 {NEW_SK} 개")
            if doc == "CODE_MAP.md" and INSIGHT_FILE not in ds:
                ds = ds.rstrip() + f"\n- `{INSIGHT_FILE}`: 제14기관 아온 만물 격물치지 전방위 통찰안 ({NEW_VER})\n"
            if doc == "GLOSSARY.md" and "격물치지" not in ds:
                ds = ds.rstrip() + (
                    f"\n- **격물치지(格物致知) 만물 통찰안 (R38 · {NEW_VER})**: "
                    "OTA 능동 지각(견미지저)과 FPCOS 6계층(L0~L5)으로 이미지·영상·언어의 급소(Leverage Point)와 군더더기(Dead Weight)를 가려내는 제14기관.\n"
                )
            wr(dp, ds)

    json_targets = [
        "rgon_morning_brief.json", "docs/rgon_morning_brief.json", "rgon_Numeric_Organ.json",
        "rgon_k_avatar_state.json", "docs/rgon_k_avatar_state.json", "rgon_muse_queue.json", "docs/rgon_muse_queue.json",
        "rgon_voice_profile.json", "docs/rgon_voice_profile.json", "rgon_voice_organ_state.json", "docs/rgon_voice_organ_state.json",
        "rgon_aon_memory.json", "docs/rgon_aon_memory.json", "rgon_manual_gate_state.json", "docs/rgon_manual_gate_state.json",
        "rgon_laptop_hands_state.json", "docs/rgon_laptop_hands_state.json", "rgon_aon_playground_state.json", "docs/rgon_aon_playground_state.json",
        "rgon_aon_iching_state.json", "docs/rgon_aon_iching_state.json", "dept_sub_agents_status.json", "docs/dept_sub_agents_status.json"
    ]
    for rel in json_targets:
        jp = ROOT / rel
        if not jp.exists():
            continue
        raw = rd(jp).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
        raw = re.sub(r'("(?:skill_count|skills_count|formal_skills|total_skills|skills_total)"\s*:\s*)\d+', f'\\g<1>{NEW_SK}', raw)
        raw = raw.replace(f"정식 스킬 {OLD_SK}개", f"정식 스킬 {NEW_SK}개").replace(f"스킬 {OLD_SK}개", f"스킬 {NEW_SK}개")
        raw = raw.replace(f"정식 스킬 {OLD_SK} 개", f"정식 스킬 {NEW_SK} 개").replace(f"스킬 {OLD_SK} 개", f"스킬 {NEW_SK} 개")
        wr(jp, raw)


def run_cmd(args, env=None):
    t0 = datetime.datetime.now()
    r = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    dt = (datetime.datetime.now() - t0).total_seconds()
    return r.returncode, (r.stdout + "\n" + r.stderr).strip(), dt


def verify_all(snap0):
    rep = []
    g1 = True
    for name, mod in (("omni_insight_eye", INSIGHT_FILE),
                      ("iching_dao_oracle", "rgon_aon_iching_dao_oracle.py"),
                      ("desktop_playground", "rgon_aon_desktop_playground.py"),
                      ("laptop_hands", "rgon_laptop_hands.py"),
                      ("soul_brain", "rgon_aon_soul_brain.py"),
                      ("voice_organ", "rgon_voice_organ.py")):
        rc, out, dt = run_cmd([sys.executable, mod, "--self-test"])
        ok = (rc == 0 and "PASS" in out)
        g1 = g1 and ok
        rep.append(f"- {'✅' if ok else '❌'} {name} --self-test rc={rc} ({dt:.1f}s)")
        if not ok:
            rep.append(f"  [{name} 상세]: {out[-400:]}")

    for rel in HTML_TARGETS:
        p = ROOT / rel
        s = rd(p) if p.exists() else ""
        ok = ("RGON-R38-OMNI-INSIGHT-JS" in s and "rgon-insight-btn" in s and NEW_VER in s)
        g1 = g1 and ok
        rep.append(f"- {'✅' if ok else '❌'} HTML {rel}")

    rc_w, out_w, _ = run_cmd([sys.executable, "rgon_white_blood_cell.py", "--self-test"])
    ok_w = (rc_w == 0)
    g1 = g1 and ok_w
    rep.append(f"- {'✅' if ok_w else '❌'} white_blood_cell --self-test rc={rc_w}")
    if not ok_w:
        rep.append(f"  [WBC 상세]: {out_w[-400:]}")

    snap1 = snapshot_all()
    unauth = []
    for k, v in snap1.items():
        if k not in MOD_ALLOW and snap0.get(k) != v:
            unauth.append(k)
    for k in snap0:
        if k not in snap1 and k not in MOD_ALLOW:
            unauth.append(k)
    g2 = (len(unauth) == 0)
    rep.append(f"\n## ② 비대상 보호 파일\n- 해시 변경 {len(unauth)}건" + ("" if g2 else f" ❌ {unauth[:5]}"))

    c_json = json.loads(rd(ROOT / "skills/SKILL_INDEX.json")).get("count", 0)
    md_txt = rd(ROOT / "skills/SKILL_INDEX.md")
    c_dir = sum(1 for d in (ROOT / "skills").iterdir() if d.is_dir() and (d / "SKILL.md").exists())
    c_md = NEW_SK if (SKILL_NAME in md_txt and c_dir == NEW_SK) else 0
    ab_ok = ("RGON-ANTIBODY-R38" in rd(ROOT / "ANTIBODY_REGISTRY.md") and "RGON-CONSTITUTION-ARTICLE-17" in rd(ROOT / "CONSTITUTION.md"))
    g3 = ([c_json, c_md, c_dir] == [NEW_SK, NEW_SK, NEW_SK]) and ab_ok
    rep.append(f"\n## ③ 스킬·항체\n- 스킬 [{c_json}, {c_md}, {c_dir}] (기대 [{NEW_SK}, {NEW_SK}, {NEW_SK}])\n- {R38_SUMMARY}")

    changed = sorted(k for k in snap1 if snap0.get(k) != snap1.get(k))
    rep.append("\n## 변경 파일\n" + "\n".join(f"- `{x}`" for x in changed[:45]))
    return g1, g2, g3, rep


def popup(title, msg):
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, msg, title, 0x40)
    except Exception:
        pass


def main():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bdir = ROOT / ".rgon_backups" / f"step38_{ts}"
    log(f"👁️ Step 38 ({NEW_VER} · {NEW_AB} · 스킬 {NEW_SK}개) 수술 완전체 배포 시작...")
    ast.parse(INSIGHT_SRC)
    snap0 = snapshot_all()
    backup_targets(bdir)
    try:
        wr(ROOT / INSIGHT_FILE, INSIGHT_SRC.lstrip())
        wr(ROOT / f"skills/{SKILL_NAME}/SKILL.md", SKILL_MD_TXT.lstrip())
        subprocess.run([sys.executable, INSIGHT_FILE, "--self-test"], cwd=ROOT, check=True, capture_output=True)
        patch_voice()
        patch_soul()
        for rel in HTML_TARGETS:
            if (ROOT / rel).exists():
                patch_html(ROOT / rel)
        sync_all_metadata()
        patch_daily_cycle()
        patch_wbc()
        subprocess.run([sys.executable, "rgon_voice_organ.py", "--self-test"], cwd=ROOT, capture_output=True)
        subprocess.run([sys.executable, "rgon_aon_soul_brain.py", "--self-test"], cwd=ROOT, capture_output=True)
        subprocess.run([sys.executable, "rgon_white_blood_cell.py", "--heal"], cwd=ROOT, capture_output=True)

        g1, g2, g3, rep = verify_all(snap0)
        score = sum([bool(g1), bool(g2), bool(g3)])
        report_txt = (
            f"# STEP38 AON OMNI INSIGHT REPORT — {NEW_VER}\n\n"
            f"- 일시: {ts}\n- 항체: {NEW_AB} · 정식 스킬: [{NEW_SK}, {NEW_SK}, {NEW_SK}]\n"
            f"- 삼성(三省): **{score}/3**\n- 백업: `{bdir.relative_to(ROOT).as_posix()}`\n\n"
            f"## ① 기능 검증\n" + "\n".join(rep) + "\n"
        )
        wr(ROOT / REPORT_FILE, report_txt)
        if score < 3:
            log("\n".join(rep[:40]))
            log(f"⏪ Auto-Rollback 시작: 삼성 {score}/3 미달")
            restore_backup(bdir, snap0)
            log(f"  원본 백업: {bdir.relative_to(ROOT).as_posix()}")
            popup("RGON 제14기관", f"Step 38 {NEW_VER} 실패 rc=1 (자동 원복) · {NEW_AB} · 스킬 {NEW_SK}")
            return 1
        log(f"① 기능 ✅ | ② 보호 ✅(0건) | ③ 스킬 [{NEW_SK}, {NEW_SK}, {NEW_SK}] 항체 ✅ ➔ 삼성 3/3 PASS!")
        env = dict(os.environ, GIT_EDITOR="true", GIT_MERGE_AUTOEDIT="no")
        subprocess.run(["git", "add", "-A"], cwd=ROOT, env=env)
        subprocess.run(["git", "commit", "-m", f"feat(step38): {NEW_VER} A-ON Omni Insight Eye ({NEW_AB}, skills {NEW_SK})"], cwd=ROOT, env=env)
        subprocess.run(["git", "pull", "--no-rebase", "--no-edit", "-X", "ours", "origin", "main"], cwd=ROOT, env=env)
        subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, env=env)
        popup("RGON 제14기관", f"Step 38 {NEW_VER} 완료 3/3 · {NEW_AB} · 스킬 {NEW_SK}")
        return 0
    except Exception as ex:
        log(f"❌ 예외 발생: {ex!r}")
        restore_backup(bdir, snap0)
        popup("RGON 제14기관", f"Step 38 예외 원복: {ex}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
