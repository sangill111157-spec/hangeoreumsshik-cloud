# -*- coding: utf-8 -*-
"""
Step 11 과제 A — 정적 HTML/JSON 정화
표준 라이브러리만 사용하며 외부 통신·후보 코드 실행·Git 작업을 수행하지 않습니다.

실시간 실행 상태를 검증할 수 없는 정적 자료에는 '실시간 미검증'을 표시합니다.
기존 HTML을 재직렬화하지 않고 승인된 텍스트 구간만 교체합니다.
HTML/JSON 전체를 메모리에서 검증한 다음 백업·원자적 교체·재검증합니다.
"""
import copy
import datetime
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile


ROOT = Path(r"C:\Users\sangi\Downloads\shin-agent")
HTML_FILES = (
    "rgon_alpha_chat.html",
    "dashboard/rgon_alpha_chat.html",
    "docs/rgon_alpha_chat.html",
)
JSON_FILES = ("rgon_brain_snapshot.json", "evolution_memory.json")
TARGETS = HTML_FILES + JSON_FILES
PROTECTED_IDS = (
    "rgon-step5-solo-panel",
    "rgon-step7-chat-zone",
    "rgon-step8-constitution-bar",
    "rgon-step9-aggregator-board",
    "rgon-step10-agency-awaken",
    "dokdae-feed",
)
DISPLAY_NAMES = {
    "R1": "PS 따옴표 함정 방지",
    "R2": "모바일 가로폭 보호",
    "R3": "체크박스 선택 보존",
    "R4": "정적 JSON 폴백",
    "R5": "서랍 빈여백 제거",
    "R6": "세로 글자 깨짐 방지",
    "R7": "배지 깜빡임 방지",
    "R8": "승인(Y) 전 코드 금지",
    "R9": "단일 코드블록 원칙",
    "R10": "자기참조 오판 방지",
    "R11": "최소 변경 Top1 선택",
    "R12": "중복 반복출력 금지",
    "R13": "0바이트 덮어쓰기 금지",
}
SUMMARY = " / ".join(
    "{}: {}".format(key, value) for key, value in DISPLAY_NAMES.items()
)
AGENCIES = (
    "알파-D1 퀀트",
    "알파-D2 바이럴",
    "알파-D3 미디어",
    "알파-D4 홍익",
    "알파-D5 가디언",
    "알파-D6 트레저리",
)
AGENCY_LINES = (
    "알파-D1 퀀트 · R&D·교차검증 담당 · 실시간 가동 미검증",
    "알파-D2 바이럴 · 홍보·BM·키워드 담당 · 실시간 연동 미검증",
    "알파-D3 미디어 · MP4·TTS 제작 담당 · 실시간 가동 미검증",
    "알파-D4 홍익 · 헌법 v1.0 수호 정책 · 실제 잠금 집행 미검증",
    "알파-D5 가디언 · 항체 R1~R13 수호 지표 · 실제 차단 집행 미검증",
    "알파-D6 트레저리 · 지출·금고 장부 점검 담당 · 잔액·무결성 미검증",
)
HEADING = "6대 청사 실시간 보좌 지표 보기"
R13_KEY = "R13_NO_ZERO_BYTE_OVERWRITE"
R13_DESCRIPTION = (
    "0바이트 덮어쓰기 금지: 원본 전체를 메모리에서 읽고 검증한 뒤 "
    "동일 디렉터리 임시 파일에 기록·동기화하고 원자적으로 교체한다."
)
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img",
    "input", "link", "meta", "param", "source", "track", "wbr",
}
OLD_BADGE = re.compile(
    r"(?:🛡(?:️)?\s*)?"
    r"R(?P<n>1[0-3]|[1-9])\s*[·ㆍ|]\s*"
    r"항체\s*R(?P=n)\s*[·ㆍ|]\s*활성"
)
OLD_SINGLE = re.compile(r"항체\s*R(1[0-3]|[1-9])\s*[·ㆍ|]\s*활성")
OLD_RANGE = re.compile(
    r"항체\s*R1\s*[~～]\s*R(?:1[012]|[1-9])(?!\d)"
    r"(?:\s*\(\s*(?:1[012]|[1-9])종\s*\))?"
)
PRICE = re.compile(
    r"\b(?P<symbol>NVDA|BTC|ETH|TSLA|AAPL|MSFT|GOOGL|AMZN|SOL)"
    r"\s*(?:[:：]\s*)?\$\s*"
    r"\d[\d,]*(?:\.\d+)?(?:\s*(?:USD|USDT))?",
    re.I,
)


class TaskError(RuntimeError):
    pass


def fail(message):
    raise TaskError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def loads(raw, label):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                fail("{}: 중복 JSON 키 {}".format(label, key))
            result[key] = value
        return result

    try:
        return json.loads(
            raw.decode("utf-8-sig"),
            object_pairs_hook=pairs,
            parse_constant=lambda value: fail(label + ": 비표준 JSON 상수 " + value),
        )
    except (ValueError, UnicodeError) as exc:
        fail("{}: JSON 해석 실패: {}".format(label, exc))


def dumps(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def safe_path(relative):
    current = ROOT
    if ROOT.is_symlink():
        fail("루트 심볼릭 링크는 허용하지 않습니다.")
    for component in Path(relative).parts:
        current = current / component
        if current.is_symlink():
            fail("심볼릭 링크 대상 금지: " + relative)
        if hasattr(os.path, "isjunction") and os.path.isjunction(str(current)):
            fail("정션 대상 금지: " + relative)
    if not current.is_file():
        fail("필수 파일 누락: " + relative)
    if current.stat().st_nlink > 1:
        fail("하드 링크 파일 수정 금지: " + relative)
    return current


def atomic_write(path, data, mode=None):
    if not data:
        fail("R13: 빈 바이트 기록 차단: " + str(path))
    descriptor, temporary = tempfile.mkstemp(
        prefix=".rgon-step11-", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if Path(temporary).read_bytes() != data:
            fail("임시 파일 바이트 검증 실패")
        if mode is not None:
            os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def clean_text(value):
    value = OLD_BADGE.sub(
        lambda match: "🛡️ R{} · {} · 활성".format(
            match.group("n"), DISPLAY_NAMES["R" + match.group("n")]
        ),
        value,
    )
    value = OLD_SINGLE.sub(
        lambda match: "R{} · {} · 활성".format(
            match.group(1), DISPLAY_NAMES["R" + match.group(1)]
        ),
        value,
    )
    return OLD_RANGE.sub("항체 R1~R13 (13종)", value)


def transform_values(value):
    if isinstance(value, str):
        return clean_text(value)
    if isinstance(value, list):
        return [transform_values(item) for item in value]
    if isinstance(value, dict):
        return {key: transform_values(item) for key, item in value.items()}
    return value


def register_r13(document, label):
    locations = []

    def visit(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key.lower() in {
                    "antibodies", "antibody", "antibody_rules", "verified_antibodies"
                }:
                    if not isinstance(child, dict):
                        fail(label + ": 항체 저장소 객체형 스키마가 필요합니다.")
                    locations.append(child)
                else:
                    visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(document)
    if len(locations) != 1:
        fail(label + ": 정식 항체 저장소를 정확히 하나 식별해야 합니다.")
    container = locations[0]
    r13_keys = [key for key in container if re.match(r"^R13(?:_|$)", key)]
    if len(r13_keys) > 1:
        fail(label + ": R13 중복 정의는 자동 삭제하지 않습니다.")
    if not r13_keys:
        container[R13_KEY] = R13_DESCRIPTION
    display = document.get("antibody_display_names")
    if display is not None and not isinstance(display, dict):
        fail(label + ": 기존 antibody_display_names 자료형 충돌")
    document["antibody_display_names"] = dict(DISPLAY_NAMES)
    return document


class SourceHTML(HTMLParser):
    """태그·텍스트의 원문 오프셋만 수집하며 HTML을 재직렬화하지 않는다."""

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.line_starts = [0]
        self.line_starts.extend(
            match.end() for match in re.finditer("\n", source)
        )
        self.stack = []
        self.nodes = []
        self.texts = []
        self.ids = {pid: 0 for pid in PROTECTED_IDS}
        self.feed(source)
        self.close()
        for index in self.stack:
            if self.nodes[index]["end"] is None:
                self.nodes[index]["end"] = len(source)

    def offset(self):
        line, column = self.getpos()
        return self.line_starts[line - 1] + column

    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text()
        start = self.offset()
        # 요청한 정규식을 실제 시작 태그에만 적용한다.
        # script 본문이나 JS 문자열은 여기에 들어오지 않는다.
        for pid in PROTECTED_IDS:
            pattern = r'\bid\s*=\s*["\']' + re.escape(pid) + r'["\']'
            self.ids[pid] += len(re.findall(pattern, raw, flags=re.I))
        item = {
            "tag": tag.lower(),
            "start": start,
            "open_end": start + len(raw),
            "end": start + len(raw) if tag.lower() in VOID_TAGS else None,
            "parent": self.stack[-1] if self.stack else None,
            "attrs": dict(attrs),
        }
        self.nodes.append(item)
        index = len(self.nodes) - 1
        if tag.lower() not in VOID_TAGS:
            self.stack.append(index)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_TAGS:
            index = self.stack.pop()
            self.nodes[index]["end"] = self.nodes[index]["open_end"]

    def handle_endtag(self, tag):
        tag = tag.lower()
        for position in range(len(self.stack) - 1, -1, -1):
            if self.nodes[self.stack[position]]["tag"] == tag:
                end_start = self.offset()
                end_close = self.source.find(">", end_start)
                end = end_close + 1 if end_close >= 0 else end_start
                for index in self.stack[position:]:
                    self.nodes[index]["end"] = end
                del self.stack[position:]
                break

    def handle_data(self, data):
        start = self.offset()
        ancestors = list(self.stack)
        self.texts.append({
            "start": start,
            "end": start + len(data),
            "text": data,
            "ancestors": ancestors,
        })


def apply_edits(source, edits):
    edits = sorted(edits, key=lambda item: item[0])
    previous = 0
    pieces = []
    for start, end, replacement in edits:
        if start < previous or end < start:
            fail("텍스트 수정 구간 중첩")
        pieces.append(source[previous:start])
        pieces.append(replacement)
        previous = end
    pieces.append(source[previous:])
    result = "".join(pieces)
    # 모든 수정 밖의 원문은 위 슬라이스를 그대로 사용한다.
    return result


def clean_embedded_json(text):
    """JSON script 또는 const DATA = {...} 형식만 파싱하여 정화한다."""
    stripped = text.lstrip()
    offset = len(text) - len(stripped)
    starts = []
    if stripped.startswith(("{", "[")):
        starts.append(offset)
    for match in re.finditer(
        r"\b(?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=\s*(?=[{\[])",
        text,
    ):
        starts.append(match.end())
    decoder = json.JSONDecoder()
    edits = []
    consumed = -1
    for start in sorted(set(starts)):
        if start < consumed:
            continue
        try:
            value, end = decoder.raw_decode(text, start)
        except ValueError:
            continue
        consumed = end
        updated = transform_values(value)
        if updated != value:
            serialized = json.dumps(updated, ensure_ascii=False, separators=(",", ":"))
            for char, escape in (
                ("<", r"\u003c"), (">", r"\u003e"), ("&", r"\u0026"),
                ("\u2028", r"\u2028"), ("\u2029", r"\u2029"),
            ):
                serialized = serialized.replace(char, escape)
            edits.append((start, end, serialized))
    result = apply_edits(text, edits) if edits else text
    # 좁은 고정 표기만 변경하며 JS 키·함수·템플릿 동작은 수정하지 않는다.
    return clean_text(result)


def find_agency_region(parser, label):
    headings = [
        item for item in parser.texts
        if HEADING in item["text"]
        and not any(
            parser.nodes[index]["tag"] in {"script", "style", "pre", "code"}
            for index in item["ancestors"]
        )
    ]
    if not headings:
        return None
    regions = set()
    for heading in headings:
        for index in reversed(heading["ancestors"]):
            item = parser.nodes[index]
            if item["tag"] in {"body", "html"}:
                break
            content = parser.source[item["start"]:item["end"]]
            if PRICE.search(content) or sum(
                name in content for name in AGENCIES
            ) >= 2 or "알파-퀀트" in content:
                regions.add(index)
                break
    if len(regions) > 1:
        fail(label + ": 미니카드 영역이 모호합니다.")
    return next(iter(regions)) if regions else None


def agency_for_text(parser, item, region_index, fallback_index):
    for index in reversed(item["ancestors"]):
        if index == region_index:
            break
        region = parser.nodes[index]
        content = parser.source[region["start"]:region["end"]]
        hits = []
        for number, name in enumerate(AGENCIES):
            short = ("알파-퀀트", "알파-바이럴", "알파-미디어",
                     "알파-홍익", "알파-가디언", "알파-트레저리")[number]
            if name in content or short in content or re.search(
                r"알파[\s-]*D" + str(number + 1) + r"(?!\d)", content
            ):
                hits.append(number)
        if len(hits) == 1:
            return hits[0]
    # 소속을 모르면 임의로 D1~D6에 배정하지 않는다.
    return None


def clean_html(source, label):
    parser = SourceHTML(source)
    region = find_agency_region(parser, label)
    edits = []
    price_count = 0
    badge_count = 0
    for item in parser.texts:
        tags = [parser.nodes[index]["tag"] for index in item["ancestors"]]
        old = item["text"]
        if any(tag in {"style", "textarea", "pre", "code"} for tag in tags):
            continue
        if "script" in tags:
            new = clean_embedded_json(old)
        else:
            new = clean_text(old)
            if region is not None and region in item["ancestors"]:
                if PRICE.search(new):
                    agency = agency_for_text(parser, item, region, price_count)
                    replacement = (
                        AGENCY_LINES[agency] if agency is not None else
                        "6대 청사 장부 지표 · 헌법 v1.0 / 항체 R1~R13 · 실시간 시세·가동 미검증"
                    )
                    new, count = PRICE.subn(lambda match: replacement, new)
                    price_count += count
                if "정상 상주 중 (점검 대기)" in new:
                    agency = agency_for_text(parser, item, region, price_count)
                    replacement = (
                        AGENCY_LINES[agency] if agency is not None else
                        "헌법 v1.0 / 항체 R1~R13 · 장부 점검 대기 · 실제 가동 미검증"
                    )
                    new = new.replace("정상 상주 중 (점검 대기)", replacement)
        if new != old:
            badge_count += len(OLD_BADGE.findall(old)) + len(OLD_SINGLE.findall(old))
            edits.append((item["start"], item["end"], new))

    patched = apply_edits(source, edits)
    after = SourceHTML(patched)
    if parser.ids != after.ids:
        fail(label + ": 보호 ID 실제 태그 속성 개수 변경")
    for item in after.texts:
        if OLD_BADGE.search(item["text"]) or OLD_SINGLE.search(item["text"]):
            tags = [after.nodes[index]["tag"] for index in item["ancestors"]]
            if not any(tag in {"pre", "code", "textarea", "style"} for tag in tags):
                fail(label + ": 구형 항체 표기가 남아 있습니다.")
    return patched, {
        "protected_id_counts_before": parser.ids,
        "protected_id_counts_after": after.ids,
        "edit_count": len(edits),
        "legacy_badge_matches": badge_count,
        "dummy_price_replacements": price_count,
        "agency_region_identified": region is not None,
        "outside_edit_ranges_preserved": True,
        "javascript_runtime_executed": False,
    }


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not ROOT.is_dir():
        fail("ROOT 경로가 없습니다.")
    lock = ROOT / ".rgon-step11-a.lock"
    lock_fd = None
    applied = []
    originals, modes, planned, proofs = {}, {}, {}, {}
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique = datetime.datetime.now().strftime("%f")
    backup = ROOT / "backups" / ("step11_A_" + timestamp + "_" + unique)

    try:
        try:
            lock_fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(lock_fd, str(os.getpid()).encode("ascii"))
        except FileExistsError:
            fail("다른 Step 11 작업이 실행 중이거나 잠금 파일이 남아 있습니다.")

        for relative in TARGETS:
            path = safe_path(relative)
            raw = path.read_bytes()
            if not raw:
                fail("R13: 원본이 이미 0바이트입니다: " + relative)
            originals[relative] = raw
            modes[relative] = stat.S_IMODE(path.stat().st_mode)

        for relative in JSON_FILES:
            document = loads(originals[relative], relative)
            if not isinstance(document, dict):
                fail(relative + ": 최상위 JSON 객체 필요")
            updated = register_r13(transform_values(copy.deepcopy(document)), relative)
            planned[relative] = (
                originals[relative] if updated == document else dumps(updated)
            )
            if loads(planned[relative], relative).get("antibody_display_names") != DISPLAY_NAMES:
                fail(relative + ": R1~R13 실명 검증 실패")

        for relative in HTML_FILES:
            try:
                source = originals[relative].decode("utf-8")
            except UnicodeError:
                fail(relative + ": UTF-8 원문만 안전하게 처리합니다.")
            patched, proof = clean_html(source, relative)
            planned[relative] = patched.encode("utf-8")
            proofs[relative] = proof
            if not planned[relative]:
                fail("R13: HTML 빈 결과 차단")

        # 최초 대상 수정 전에 모든 원본을 백업한다.
        backup.mkdir(parents=True, exist_ok=False)
        report = {
            "task": "Step 11 과제 A",
            "created_at": timestamp,
            "display_names": DISPLAY_NAMES,
            "html_proofs": proofs,
            "files": {},
            "limits": [
                "정적 HTML/JSON 정화이며 실제 에이전트 가동 확인이 아님",
                "실시간 검증되지 않은 가동·시세·보안 집행을 정상으로 단정하지 않음",
                "다른 과거 설치기의 스냅샷 구조는 유지하고 인식 가능한 JSON 값만 정화",
                "JSON 내부 비표준 JavaScript 객체는 파싱 대상으로 삼지 않음",
                "HTML 보호 ID는 실제 시작 태그에 요청 정규식을 적용하여 검사",
            ],
        }
        for relative in TARGETS:
            path = safe_path(relative)
            if path.read_bytes() != originals[relative]:
                fail("백업 전 동시 변경 감지: " + relative)
            if relative in HTML_FILES:
                destination = backup / Path(relative).parent / (
                    "rgon_alpha_chat_step11_bak_" + timestamp + ".html"
                )
            else:
                destination = backup / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
            if destination.read_bytes() != originals[relative]:
                fail("백업 바이트 검증 실패: " + relative)
            report["files"][relative] = {
                "backup": str(destination.relative_to(backup)),
                "before_sha256": digest(originals[relative]),
                "after_sha256": digest(planned[relative]),
                "changed": originals[relative] != planned[relative],
            }
        atomic_write(backup / "verification.json", dumps(report))

        for relative in TARGETS:
            if safe_path(relative).read_bytes() != originals[relative]:
                fail("적용 전 동시 변경 감지: " + relative)

        for relative in TARGETS:
            if planned[relative] == originals[relative]:
                continue
            path = safe_path(relative)
            if path.read_bytes() != originals[relative]:
                fail("원자적 교체 직전 동시 변경 감지: " + relative)
            applied.append(relative)
            atomic_write(path, planned[relative], modes[relative])

        for relative in TARGETS:
            actual = safe_path(relative).read_bytes()
            if not actual or actual != planned[relative]:
                fail("적용 후 바이트 검증 실패: " + relative)
            if relative in HTML_FILES:
                before = SourceHTML(originals[relative].decode("utf-8")).ids
                after = SourceHTML(actual.decode("utf-8")).ids
                if before != after:
                    fail("R10: 보호 ID 검증 실패: " + relative)
            else:
                document = loads(actual, relative)
                if document.get("antibody_display_names") != DISPLAY_NAMES:
                    fail("R1~R13 실명 장부 검증 실패: " + relative)

        report["result"] = "COMPLETE"
        report["post_write_verification"] = "PASS"
        atomic_write(backup / "verification.json", dumps(report))
        print("[백업·Minimal Diff 증거] " + str(backup / "verification.json"))
        for relative in HTML_FILES:
            proof = proofs[relative]
            if not proof["agency_region_identified"]:
                print(
                    "[확인] {}: 대상 미니카드 영역을 식별하지 못해 임의 영역은 변경하지 않았습니다."
                    .format(relative)
                )
            print(
                "[검증] {}: 텍스트 수정 {}곳 / 더미 시세 정화 {}곳 / 보호 ID 동일"
                .format(
                    relative, proof["edit_count"], proof["dummy_price_replacements"]
                )
            )
        print("[주의] 정적 장부 정화입니다. 실제 실시간 가동·시세·금고 무결성을 검증하지 않았습니다.")
        print("[OK] Step 11 과제 A 정화 및 3곳 동기화 완료 (보호 ID 100% 무결)")

    except BaseException:
        errors = []
        for relative in reversed(applied):
            try:
                path = safe_path(relative)
                current = path.read_bytes()
                if current not in (originals[relative], planned[relative]):
                    fail("외부 동시 수정이 있어 자동 덮어쓰기 금지")
                # 백업 원본과 최초 메모리 원본의 동일성을 다시 확인한다.
                record_path = None
                if relative in HTML_FILES:
                    record_path = backup / Path(relative).parent / (
                        "rgon_alpha_chat_step11_bak_" + timestamp + ".html"
                    )
                else:
                    record_path = backup / relative
                restored = record_path.read_bytes()
                if restored != originals[relative] or not restored:
                    fail("백업 원본 무결성 불일치")
                atomic_write(path, restored, modes[relative])
                if path.read_bytes() != originals[relative]:
                    fail("롤백 검증 실패")
            except BaseException as exc:
                errors.append(relative + ": " + str(exc))
        if applied:
            if errors:
                print("[ROLLBACK 수동 확인 필요]\n" + "\n".join(errors), file=sys.stderr)
            else:
                print("[ROLLBACK VERIFIED] 백업본으로 원본 복원 완료", file=sys.stderr)
            print("백업: " + str(backup), file=sys.stderr)
        raise
    finally:
        if lock_fd is not None:
            os.close(lock_fd)
            try:
                lock.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[중단] 사용자 중단. 복구 결과를 확인하세요.", file=sys.stderr)
        sys.exit(130)
    except BaseException as error:
        print("[STEP 11 과제 A FAILED] " + str(error), file=sys.stderr)
        sys.exit(1)
Copy