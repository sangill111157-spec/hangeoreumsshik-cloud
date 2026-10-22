# -*- coding: utf-8 -*-
"""
step10_awaken_6agencies_and_clean_r12.py
Python 3.9+ / 표준 라이브러리 / Node.js / Git

- 기존 R2~R7 정식 이름·설명은 기존 장부에서 조회하며 임의로 창작하지 않습니다.
- 정식 항체 정의 충돌·누락·알 수 없는 항체 구조는 원본을 변경하지 않고 중단합니다.
- 로컬 JSON은 읽기만 합니다. file:// fetch 실패 시 설치 시점 스냅샷으로 표시합니다.
- JSON의 immutable=true는 선언이며 OS 불변 잠금·보안 차단의 작동 증거가 아닙니다.
- 지출·금고 무결성·서비스 가동 상태를 근거 없이 정상이라고 표시하지 않습니다.
- git add -A는 독립 인덱스에서 승인된 대상 경로로만 제한합니다.
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
import subprocess
import sys
import tempfile


ROOT = r"C:\Users\sangi\Downloads\shin-agent"
BASE = Path(ROOT)
VERSION = "v6.1.0-step10"
MESSAGE = (
    "feat(v6.1.0-step10): awaken 6 agencies D1-D6 with live data & clean R1-R12 antibodies"
)
HTMLS = (
    "rgon_alpha_chat.html",
    "dashboard/rgon_alpha_chat.html",
    "docs/rgon_alpha_chat.html",
)
MEMORIES = ("evolution_memory.json", "rgon_brain_snapshot.json")
JSONS = tuple(
    prefix + name
    for name in MEMORIES
    for prefix in ("", "dashboard/", "docs/")
)
TARGETS = JSONS + HTMLS
PROTECTED = (
    "rgon-step5-solo-panel",
    "rgon-step7-chat-zone",
    "rgon-step8-constitution-bar",
    "rgon-step9-aggregator-board",
    "dokdae-feed",
)
BEGIN = "<!-- RGON_STEP10_AGENCY_BEGIN -->"
END = "<!-- RGON_STEP10_AGENCY_END -->"
R12_KEY = "R12_SINGLE_FINAL_OUTPUT_ONLY"
R12_TEXT = "중복 인사말·반복 설명 금지, 깊이 사고 후 최종 1회만 단순 요약 보고"


JS_TEMPLATE = r"""
(() => {
    "use strict";
    const DATA = __STEP10_DATA__;
    const KEY = "__RGON_STEP10_AGENCY_V1__";
    if (window[KEY]) return;
    window[KEY] = true;

    const NAMES = [
        "알파-퀀트", "알파-바이럴", "알파-미디어",
        "알파-홍익", "알파-가디언", "알파-트레저리"
    ];
    const PATHS = {
        constitution: "rgon_constitution.json",
        brain: "rgon_brain_snapshot.json",
        schedule: "brain_basket/master_schedule.json",
        treasury: "treasury_ledger.json"
    };
    const state = {};
    const cards = new Map();
    let busy = false;
    let scheduled = false;
    let refreshPromise = null;
    let lastRefresh = 0;

    function node(tag, text) {
        const n = document.createElement(tag);
        if (text !== undefined) n.textContent = String(text);
        return n;
    }

    function clock() {
        return new Date().toLocaleTimeString("ko-KR", {hour12: false});
    }

    function validObject(value) {
        return value && typeof value === "object" && !Array.isArray(value);
    }

    function antibodyCount(value) {
        const found = [];
        function walk(item, depth) {
            if (depth > 16 || !item || typeof item !== "object") return;
            if (Array.isArray(item)) {
                for (const child of item) walk(child, depth + 1);
                return;
            }
            for (const [key, child] of Object.entries(item)) {
                if (["antibodies", "antibody", "antibody_rules", "verified_antibodies"]
                    .includes(key.toLowerCase()) && validObject(child)) {
                    found.push(child);
                } else walk(child, depth + 1);
            }
        }
        walk(value, 0);
        if (found.length !== 1) return null;
        const keys = Object.keys(found[0]);
        const numbers = keys.map(key => {
            const match = key.match(/^R(\d+)_/);
            return match ? Number(match[1]) : 0;
        });
        return keys.length === 12 &&
            Array.from({length: 12}, (_, i) => i + 1)
                .every(number => numbers.filter(n => n === number).length === 1)
            ? 12 : null;
    }

    function source(name) {
        const record = state[name];
        if (!record || !record.data) return "자료 없음";
        return record.live ? "로컬 JSON 확인" : "설치 스냅샷 · 실시간 아님";
    }

    function briefing(index) {
        const constitution = state.constitution && state.constitution.data;
        const brain = state.brain && state.brain.data;
        const schedule = state.schedule && state.schedule.data;
        const treasury = state.treasury && state.treasury.data;
        const count = antibodyCount(brain);
        switch (index) {
            case 0:
                return "🟢 R&D 장부 " + (brain ? "연결" : "미확인") +
                    " · 진화단계 " + String(
                        brain && (brain.generation || brain.evolution_stage) || "GEN-1(설정)"
                    ) +
                    " · 4대 AI 전광판 " +
                    (document.getElementById("rgon-step9-aggregator-board")
                        ? "UI 확인" : "아직 미확인") +
                    " · " + source("brain");
            case 1:
                return "🟢 홍보·BM 대기 · 두뇌장바구니 " +
                    (schedule ? "일정 JSON 확인" : "시트·일정 연동 미확인") +
                    " · 일일 키워드 수확 준비(실행 미검증) · " + source("schedule");
            case 2:
                return "🟢 미디어 스튜디오 · STUDIO v5 MP4 & 청년보이스 TTS 대기" +
                    " · 가동 여부는 장부만으로 검증 불가";
            case 3:
                return "🟢 제0조 홍익인간 헌법 " +
                    (constitution ? String(constitution.version || "버전 미상") : "미확인") +
                    " · immutable 선언 " +
                    (constitution && constitution.immutable === true ? "true 확인" : "미확인") +
                    " · OS 잠금 미검증 · " + source("constitution");
            case 4:
                return (count === 12 ? "🟢" : "🟠") +
                    " 5-Gate 보안 감찰 · " +
                    (count === 12 ? "항체 R1~R12(12종) 확인" : "항체 12종 정합성 미확인") +
                    " · R2/R3 차단 정책 선언(집행 미검증) · " + source("brain");
            case 5: {
                let expense = null;
                if (validObject(treasury)) {
                    for (const key of ["api_spend_krw", "api_expense_krw", "api_cost_krw"]) {
                        if (typeof treasury[key] === "number" &&
                            Number.isFinite(treasury[key]) && treasury[key] >= 0) {
                            expense = treasury[key];
                            break;
                        }
                    }
                }
                return "🟢 무자본 레버리지 정산 · API 지출 " +
                    (expense === null ? "자료 미확인" : expense.toLocaleString("ko-KR") + "원(장부값)") +
                    " · 금고 무결성 " +
                    (treasury ? "JSON 해석 확인 · 회계 감사 미실시" : "미확인") +
                    " · " + source("treasury");
            }
            default:
                return "점검 대상 미확인";
        }
    }

    async function fetchJSON(name, relative) {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), 3500);
        try {
            const url = new URL(relative, location.href);
            if (url.origin !== location.origin) throw new Error("교차 출처 금지");
            const response = await fetch(url.href, {
                cache: "no-store", credentials: "same-origin",
                redirect: "error", signal: controller.signal
            });
            if (!response.ok) throw new Error("HTTP " + response.status);
            const content = await response.text();
            if (content.length > 2000000) throw new Error("JSON 크기 제한");
            const parsed = JSON.parse(content);
            if (!validObject(parsed)) throw new Error("JSON 객체 필요");
            state[name] = {data: parsed, live: true, checkedAt: Date.now()};
        } catch (_) {
            const fallback = DATA.snapshots[name];
            state[name] = {
                data: fallback || null,
                live: false,
                checkedAt: Date.now()
            };
        } finally {
            clearTimeout(timer);
        }
    }

    async function refresh(force) {
        if (refreshPromise) return refreshPromise;
        if (!force && Date.now() - lastRefresh < 10000) return;
        refreshPromise = (async () => {
            await Promise.all(Object.entries(PATHS).map(
                ([name, path]) => fetchJSON(name, path)
            ));
            lastRefresh = Date.now();
            updateCards();
        })();
        try { await refreshPromise; }
        finally { refreshPromise = null; }
    }

    function excluded(textNode) {
        const p = textNode.parentElement;
        return !p || !!p.closest(
            "script,style,pre,code,textarea,input,[contenteditable=true]," +
            "#rgon-step9-aggregator-board,#rgon-step9-modal," +
            "[data-rgon-step10-owned]"
        );
    }

    function tidyLabels() {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        const changes = [];
        while (walker.nextNode()) {
            const textNode = walker.currentNode;
            if (excluded(textNode)) continue;
            const old = textNode.nodeValue;
            if (!old || old.length > 600) continue;
            let value = old;
            if (/항체\s*R1\s*[~～]\s*R7/.test(value)) {
                value = value.replace(
                    /항체\s*R1\s*[~～]\s*R7(?:\s*\(\s*7종\s*\))?/g,
                    "항체 R1~R12 (12종)"
                );
            }
            value = value.replace(/\bv6\.0\.[78]\b/g, "v6.1.0");
            value = value.replace(
                /독대실에서\s*바로\s*분배하기\s*\(\s*Claude\s*\/\s*GPT\s*\/\s*Grok\s*\)/g,
                "독대실에서 바로 분배하기 (👑르곤 / 🧠Claude / ⚡GPT / 🎯Grok)"
            );
            if (value !== old) changes.push([textNode, value]);
        }
        for (const [textNode, value] of changes) textNode.nodeValue = value;
    }

    function locateCard(name) {
        const leaves = Array.from(document.querySelectorAll(
            "h1,h2,h3,h4,h5,h6,strong,b,span,div"
        )).filter(element =>
            !element.closest("[data-rgon-step10-owned],script,style,pre,code") &&
            element.children.length === 0 &&
            (element.textContent || "").trim().includes(name) &&
            (element.textContent || "").length < 150
        );
        const matches = new Set();
        for (const leaf of leaves) {
            let parent = leaf.parentElement;
            for (let depth = 0; parent && depth < 7; depth++, parent = parent.parentElement) {
                if (parent === document.body || parent === document.documentElement) break;
                const content = parent.textContent || "";
                if (NAMES.filter(item => content.includes(item)).length !== 1) continue;
                if (content.includes("정상 상주 중 (점검 대기)") ||
                    Array.from(parent.querySelectorAll("button,[role=button]")).some(
                        button => /점검.*직보/.test(button.textContent || "")
                    )) {
                    matches.add(parent);
                    break;
                }
            }
        }
        return matches.size === 1 ? Array.from(matches)[0] : null;
    }

    function locateStatus(card) {
        const walker = document.createTreeWalker(card, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
            const item = walker.currentNode;
            if (item.parentElement &&
                !item.parentElement.closest("script,style,button,pre,code")) {
                const old = item.nodeValue;
                if (old.includes("정상 상주 중 (점검 대기)")) return item;
            }
        }
        return null;
    }

    function discoverCards() {
        NAMES.forEach((name, index) => {
            const old = cards.get(index);
            if (old && old.card.isConnected && old.status.isConnected) return;
            const card = locateCard(name);
            if (!card) return;
            const existing = card.querySelector('[data-rgon-step10-status="' + index + '"]');
            if (existing) {
                cards.set(index, {card, status: existing, time: ""});
                return;
            }
            const original = locateStatus(card);
            const status = node("span");
            status.setAttribute("data-rgon-step10-owned", "status");
            status.setAttribute("data-rgon-step10-status", String(index));
            status.style.whiteSpace = "pre-wrap";
            if (original) {
                const phrase = "정상 상주 중 (점검 대기)";
                const position = original.nodeValue.indexOf(phrase);
                const before = original.nodeValue.slice(0, position);
                const after = original.nodeValue.slice(position + phrase.length);
                const fragment = document.createDocumentFragment();
                if (before) fragment.appendChild(document.createTextNode(before));
                fragment.appendChild(status);
                if (after) fragment.appendChild(document.createTextNode(after));
                original.replaceWith(fragment);
            } else {
                card.appendChild(status);
            }
            cards.set(index, {card, status, time: ""});
        });
    }

    function updateCards() {
        for (const [index, record] of cards) {
            const content = briefing(index) +
                (record.time ? " · 점검 " + record.time : "");
            if (record.status.textContent !== content) record.status.textContent = content;
        }
    }

    function report(indices, time) {
        const feed = document.getElementById("dokdae-feed");
        if (!feed) return;
        const article = node("article");
        article.setAttribute("data-rgon-step10-owned", "report");
        Object.assign(article.style, {
            margin: "8px 0", padding: "12px", borderRadius: "10px",
            background: "#10213a", color: "#e5efff",
            border: "1px solid #3b5578", whiteSpace: "pre-wrap",
            font: "13px/1.6 system-ui,sans-serif"
        });
        article.appendChild(node("strong", "📡 6대 청사 장부 점호 · " + time));
        const summary = node("div");
        summary.textContent = indices.map(index =>
            "D" + (index + 1) + " " + NAMES[index] + " — " +
            (cards.has(index) ? briefing(index) : "카드 DOM 식별 실패 · 확인 필요")
        ).join("\n");
        article.appendChild(summary);
        article.appendChild(node(
            "small",
            "\n읽기 전용 장부 점검입니다. 실제 서브 에이전트 실행·보안 차단·금고 감사를 수행하지 않았습니다."
        ));
        feed.appendChild(article);
        // 기존 피드 항목은 삭제·이동하지 않는다.
    }

    function handleClick(event) {
        const target = event.target instanceof Element
            ? event.target.closest("button,[role=button],a") : null;
        if (!target || target.closest("[data-rgon-step10-owned]")) return;
        const label = (target.textContent || "").trim();
        const all = /6대\s*청사/.test(label) &&
            /점검|소집/.test(label) && /전원|일제/.test(label);
        const single = /점검.*직보/.test(label);
        if (!all && !single) return;

        discoverCards();
        let indices = [];
        if (all) indices = NAMES.map((_, index) => index);
        else {
            for (const [index, record] of cards) {
                if (record.card.contains(target)) indices.push(index);
            }
        }
        if (!indices.length) return;
        // 원래 버튼의 핸들러·기본 동작은 변경하거나 차단하지 않는다.
        (async () => {
            await refresh(true);
            const time = clock();
            discoverCards();
            for (const index of indices) {
                const record = cards.get(index);
                if (record) record.time = time;
            }
            updateCards();
            report(indices, time);
        })().catch(error => console.warn("[RGON Step10]", error));
    }

    function scan() {
        scheduled = false;
        if (busy || !document.body) return;
        busy = true;
        try {
            tidyLabels();
            discoverCards();
            updateCards();
        } finally {
            busy = false;
        }
    }

    function schedule() {
        if (scheduled) return;
        scheduled = true;
        setTimeout(scan, 150);
    }

    function start() {
        for (const name of Object.keys(PATHS)) {
            state[name] = {
                data: DATA.snapshots[name] || null,
                live: false,
                checkedAt: DATA.installedAt
            };
        }
        document.addEventListener("click", handleClick, false);
        const observer = new MutationObserver(schedule);
        observer.observe(document.body, {childList: true, subtree: true});
        scan();
        refresh(true).catch(console.warn);
        setInterval(() => {
            if (!document.hidden) refresh(false).catch(console.warn);
        }, 15000);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start, {once: true});
    } else start();
})();
"""


class InstallError(RuntimeError):
    pass


def fail(message):
    raise InstallError(message)


def json_load(raw, label):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                fail("{}: 중복 JSON 키 {}".format(label, key))
            value[key] = item
        return value

    try:
        return json.loads(
            raw.decode("utf-8-sig"),
            object_pairs_hook=pairs,
            parse_constant=lambda token: fail(label + ": 비표준 JSON 상수 " + token),
        )
    except (ValueError, UnicodeError) as exc:
        fail("{}: JSON 해석 실패: {}".format(label, exc))


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def fixed_run(command, env=None, check=True, timeout=120, data=None):
    try:
        result = subprocess.run(
            [str(part) for part in command],
            cwd=str(BASE), env=env, input=data,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        fail("고정 명령 실행 실패: {}: {}".format(command[0], exc))
    if check and result.returncode:
        detail = (result.stdout + result.stderr).decode("utf-8", errors="replace")
        fail("명령 실패: {}\n{}".format(" ".join(map(str, command)), detail[-8000:]))
    return result


def result_text(result):
    return result.stdout.decode("utf-8").strip()


def safe_path(relative, required=False):
    path = BASE / relative
    current = BASE
    if BASE.is_symlink():
        fail("루트 심볼릭 링크 금지")
    for part in Path(relative).parts:
        current = current / part
        if current.is_symlink():
            fail("심볼릭 링크 금지: " + relative)
        if hasattr(os.path, "isjunction") and os.path.isjunction(str(current)):
            fail("정션 금지: " + relative)
    if path.exists():
        if not path.is_file() or path.stat().st_nlink > 1:
            fail("일반 단독 파일이 아닙니다: " + relative)
    elif required:
        fail("필수 파일 누락: " + relative)
    return path


def atomic_write(path, raw, mode=None):
    descriptor, temporary = tempfile.mkstemp(prefix=".rgon-step10-", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        if mode is not None:
            os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def merge_preserving(left, right, path=""):
    if left == right:
        return copy.deepcopy(left)
    if isinstance(left, dict) and isinstance(right, dict):
        result = copy.deepcopy(left)
        for key, value in right.items():
            if key in result:
                result[key] = merge_preserving(result[key], value, path + "/" + key)
            else:
                result[key] = copy.deepcopy(value)
        return result
    fail("복사본의 기존 자료가 충돌합니다. 임의 소실 방지를 위해 중단: " + path)


def antibody_location(document, label):
    found = []

    def walk(value, path):
        if isinstance(value, dict):
            for key, child in value.items():
                next_path = path + [key]
                if key.lower() in {
                    "antibodies", "antibody", "antibody_rules", "verified_antibodies"
                }:
                    if not isinstance(child, dict):
                        fail(label + ": 항체 저장소는 객체형이어야 합니다.")
                    found.append(next_path)
                elif isinstance(child, (dict, list)):
                    walk(child, next_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, path + [index])

    walk(document, [])
    if len(found) != 1:
        fail(label + ": 항체 저장소를 정확히 하나 식별해야 합니다.")
    return found[0]


def at_path(document, path):
    value = document
    for key in path:
        value = value[key]
    return value


def description(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("description", "rule", "content", "text", "message"):
            if isinstance(value.get(key), str):
                return value[key]
    return None


def normalize_family(name, originals):
    combined = None
    common_path = None
    canonical = {}
    short_archived = {}

    for prefix in ("", "dashboard/", "docs/"):
        relative = prefix + name
        raw = originals[relative]
        if raw is None:
            continue
        document = json_load(raw, relative)
        if not isinstance(document, dict):
            fail(relative + ": 최상위 객체 필요")
        location = antibody_location(document, relative)
        if common_path is None:
            common_path = location
        elif common_path != location:
            fail(name + ": 복사본별 항체 저장 경로가 다릅니다.")
        container = at_path(document, location)
        for key, value in container.items():
            short = re.fullmatch(r"R([1-7])", key)
            full = re.fullmatch(r"R(\d+)_[A-Z0-9_]+", key)
            if short:
                short_archived[relative + ":" + key] = copy.deepcopy(value)
                continue
            if not full or not 1 <= int(full.group(1)) <= 12:
                fail(relative + ": 자동 삭제할 수 없는 항체 키 " + key)
            number = int(full.group(1))
            old = canonical.get(number)
            if old and old[0] != key:
                fail("R{} 정식 식별자 충돌: {} / {}".format(number, old[0], key))
            if old:
                canonical[number] = (key, merge_preserving(old[1], value, "/" + key))
            else:
                canonical[number] = (key, copy.deepcopy(value))

        cleaned = copy.deepcopy(document)
        at_path(cleaned, location).clear()
        cleaned["version"] = VERSION
        combined = cleaned if combined is None else merge_preserving(
            combined, cleaned, "/" + name
        )

    if combined is None or common_path is None:
        fail(name + ": 기존 장부가 없습니다.")
    for number in range(1, 12):
        if number not in canonical:
            fail(
                "{}: R{} 정식 정의 누락. 특히 R2~R7 이름을 임의 창작하지 않습니다."
                .format(name, number)
            )
    if canonical[1][0] != "R1_NO_POWERSHELL_QUOTE_TRAP":
        fail(name + ": R1 정식 식별자가 요청과 다릅니다.")
    if 12 in canonical:
        if canonical[12][0] != R12_KEY:
            fail(name + ": R12 식별자 충돌")
        existing = description(canonical[12][1])
        if existing is not None and existing != R12_TEXT:
            fail(name + ": R12 설명 충돌")
        if existing is None:
            if not isinstance(canonical[12][1], dict):
                fail(name + ": R12 설명을 병합할 수 없습니다.")
            canonical[12][1]["description"] = R12_TEXT
    else:
        canonical[12] = (R12_KEY, R12_TEXT)

    target = at_path(combined, common_path)
    target.clear()
    for number in range(1, 13):
        key, value = canonical[number]
        target[key] = value
    if len(target) != 12:
        fail(name + ": 항체 12종 검증 실패")
    combined["version"] = VERSION
    return combined, short_archived


class Audit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.ids = {}

    def handle_starttag(self, tag, attrs):
        identifier = dict(attrs).get("id")
        if identifier:
            self.ids[identifier] = self.ids.get(identifier, 0) + 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


def ids_of(source):
    parser = Audit()
    parser.feed(source)
    parser.close()
    return parser.ids


def inject(source, block):
    if source.count(BEGIN) != source.count(END) or source.count(BEGIN) > 1:
        fail("Step 10 마커 중복/손상")
    if BEGIN in source:
        left = source.index(BEGIN)
        right = source.index(END) + len(END)
        if right <= left:
            fail("Step 10 마커 순서 오류")
        result = source[:left] + block + source[right:]
        if result[:left] != source[:left] or result[left + len(block):] != source[right:]:
            fail("기존 소유 블록 외 변경")
        proof = {"mode": "replace-own-step10-only", "outside_unchanged": True}
    else:
        matches = list(re.finditer(r"</body\s*>", source, re.I))
        if not matches:
            fail("HTML </body> 누락")
        position = matches[-1].start()
        result = source[:position] + block + source[position:]
        if result[:position] + result[position + len(block):] != source:
            fail("Minimal Diff 원문 재구성 실패")
        proof = {"mode": "insert-only", "original_reconstruction": True}
    before, after = ids_of(source), ids_of(result)
    proof["actual_id_attributes"] = {}
    for identifier in PROTECTED:
        if before.get(identifier, 0) != after.get(identifier, 0):
            fail("보호 ID 속성 개수 변경: " + identifier)
        proof["actual_id_attributes"][identifier] = before.get(identifier, 0)
    if after.get("rgon-step10-agency-awaken") != 1:
        fail("Step 10 런타임 ID 중복/누락")
    return result, proof


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not BASE.is_dir():
        fail("ROOT 폴더 없음: " + ROOT)
    node = shutil.which("node")
    git_program = shutil.which("git")
    if not node or not git_program:
        fail("Node.js와 Git이 필요합니다.")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup = BASE / "backups" / ("step10_" + timestamp)
    lock = BASE / ".rgon-step10-install.lock"
    lock_fd = None
    originals, modes, plan, proofs = {}, {}, {}, {}
    applied, changed = [], []
    initial_head = None
    own_commit = None
    push_uncertain = False

    with tempfile.TemporaryDirectory(prefix="rgon-step10-") as temp:
        temp_path = Path(temp)
        hook_dir = temp_path / "disabled-hooks"
        hook_dir.mkdir()
        environment = os.environ.copy()
        for key in list(environment):
            if key.startswith("GIT_CONFIG_KEY_") or key.startswith("GIT_CONFIG_VALUE_"):
                environment.pop(key, None)
        environment.pop("GIT_INDEX_FILE", None)
        environment["GIT_CONFIG_COUNT"] = "1"
        environment["GIT_CONFIG_KEY_0"] = "core.hooksPath"
        environment["GIT_CONFIG_VALUE_0"] = str(hook_dir)

        def git(*args, check=True, env=None, timeout=120, data=None):
            return fixed_run(
                [git_program, *args], env=env or environment,
                check=check, timeout=timeout, data=data,
            )

        def remote():
            fields = result_text(git(
                "ls-remote", "--exit-code", "origin", "refs/heads/main", timeout=90
            )).split()
            if len(fields) != 2 or fields[1] != "refs/heads/main":
                fail("origin/main 확인 실패")
            return fields[0]

        def restore():
            errors = []
            if own_commit:
                try:
                    git("update-ref", "refs/heads/main", initial_head, own_commit)
                except BaseException as exc:
                    errors.append("Git HEAD: " + str(exc))
            for relative in reversed(applied):
                try:
                    path = safe_path(relative)
                    current = path.read_bytes() if path.exists() else None
                    if current not in (plan[relative], originals[relative]):
                        fail("다른 프로세스 수정 감지: 자동 덮어쓰기 금지")
                    if originals[relative] is None:
                        if path.exists():
                            path.unlink()
                    else:
                        atomic_write(path, originals[relative], modes[relative])
                        if path.read_bytes() != originals[relative]:
                            fail("복원 검증 실패")
                except BaseException as exc:
                    errors.append(relative + ": " + str(exc))
            print(
                "[ROLLBACK VERIFIED]" if not errors else
                "[수동 복구 필요]\n" + "\n".join(errors),
                file=sys.stderr,
            )
            print("백업: " + str(backup), file=sys.stderr)

        try:
            try:
                lock_fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(lock_fd, str(os.getpid()).encode("ascii"))
            except FileExistsError:
                fail("설치 잠금 존재: " + str(lock))

            actual_root = Path(result_text(git("rev-parse", "--show-toplevel"))).resolve()
            if os.path.normcase(str(actual_root)) != os.path.normcase(str(BASE.resolve())):
                fail("ROOT 자체가 저장소 루트여야 합니다.")
            if result_text(git("branch", "--show-current")) != "main":
                fail("main 브랜치에서만 설치합니다.")
            initial_head = result_text(git("rev-parse", "HEAD"))
            for marker in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD"):
                if git("rev-parse", "--verify", marker, check=False).returncode == 0:
                    fail("진행 중인 Git 작업: " + marker)
            for marker in ("rebase-merge", "rebase-apply", "sequencer"):
                raw = Path(result_text(git("rev-parse", "--git-path", marker)))
                if (raw if raw.is_absolute() else BASE / raw).exists():
                    fail("진행 중인 Git 작업: " + marker)
            if remote() != initial_head:
                fail("로컬 main과 origin/main이 다릅니다. 자동 병합하지 않습니다.")

            git_modes = {}
            for relative in TARGETS:
                path = safe_path(
                    relative, required=relative in HTMLS or relative in MEMORIES
                )
                originals[relative] = path.read_bytes() if path.exists() else None
                modes[relative] = stat.S_IMODE(path.stat().st_mode) if path.exists() else None
                tracked = git(
                    "ls-files", "--error-unmatch", "--", relative, check=False
                ).returncode == 0
                if tracked:
                    if (
                        git("diff", "--quiet", "--", relative, check=False).returncode or
                        git("diff", "--cached", "--quiet", "--", relative, check=False).returncode
                    ):
                        fail("대상에 기존 tracked 수정이 있습니다: " + relative)
                    record = git("ls-files", "--stage", "-z", "--", relative).stdout
                    metadata = record.split(b"\t", 1)[0].split()
                    if len(metadata) != 3 or metadata[2] != b"0":
                        fail("Git 대상 인덱스 상태 오류: " + relative)
                    git_modes[relative] = metadata[0].decode("ascii")
                else:
                    git_modes[relative] = "100644"

            normalized = {}
            archived = {}
            for name in MEMORIES:
                document, removed = normalize_family(name, originals)
                normalized[name] = document
                archived.update(removed)
                serialized = json_bytes(document)
                for prefix in ("", "dashboard/", "docs/"):
                    plan[prefix + name] = serialized

            # 두 장부의 정식 항체 정의도 대조한다.
            first = normalized[MEMORIES[0]]
            second = normalized[MEMORIES[1]]
            a = at_path(first, antibody_location(first, MEMORIES[0]))
            b = at_path(second, antibody_location(second, MEMORIES[1]))
            if set(a) != set(b):
                fail("두 장부의 정식 R1~R12 식별자가 다릅니다.")
            for key in a:
                if description(a[key]) != description(b[key]):
                    fail("두 장부의 항체 설명 충돌: " + key)

            snapshots = {"brain": normalized["rgon_brain_snapshot.json"]}
            for label, relative in (
                ("constitution", "rgon_constitution.json"),
                ("schedule", "brain_basket/master_schedule.json"),
                ("treasury", "treasury_ledger.json"),
            ):
                path = safe_path(relative)
                if path.exists():
                    raw = path.read_bytes()
                    if len(raw) > 2000000:
                        fail("스냅샷 JSON 크기 제한: " + relative)
                    value = json_load(raw, relative)
                    if not isinstance(value, dict):
                        fail("스냅샷 JSON 객체 필요: " + relative)
                    snapshots[label] = value
                else:
                    snapshots[label] = None

            payload = json.dumps({
                "installedAt": int(datetime.datetime.now().timestamp() * 1000),
                "snapshots": snapshots,
            }, ensure_ascii=False, separators=(",", ":"))
            for character, escaped in (
                ("<", r"\u003c"), (">", r"\u003e"), ("&", r"\u0026"),
                ("\u2028", r"\u2028"), ("\u2029", r"\u2029"),
            ):
                payload = payload.replace(character, escaped)
            javascript = JS_TEMPLATE.replace("__STEP10_DATA__", payload)
            if len(javascript) > 6000000:
                fail("주입 스냅샷 크기 제한 초과")
            check_file = temp_path / "step10-runtime.js"
            check_file.write_text(javascript, encoding="utf-8")
            fixed_run([node, "--check", check_file], env=environment, timeout=60)

            for relative in HTMLS:
                source = originals[relative].decode("utf-8")
                newline = "\r\n" if "\r\n" in source else "\n"
                runtime = javascript.replace("\r\n", "\n").replace("\n", newline)
                block = (
                    BEGIN + newline
                    + '<script id="rgon-step10-agency-awaken">' + newline
                    + runtime + newline + "</script>" + newline + END
                )
                if BEGIN not in source:
                    block = newline + block + newline
                patched, proof = inject(source, block)
                plan[relative] = patched.encode("utf-8")
                proofs[relative] = proof

            changed = [relative for relative in TARGETS if plan[relative] != originals[relative]]
            if not changed:
                print("[STEP 10 6-AGENCIES AWAKEN COMPLETE]")
                return

            backup.mkdir(parents=True, exist_ok=False)
            report = {
                "version": VERSION,
                "original_head": initial_head,
                "minimal_diff": proofs,
                "removed_short_aliases_archived": archived,
                "files": {},
                "runtime_notes": [
                    "file:// fetch 실패 시 설치 스냅샷 표시",
                    "소스 파일 보호 블록 원문은 변경하지 않음",
                    "런타임 텍스트 교정과 상태 UI 추가만 수행",
                    "immutable는 선언이며 OS 잠금 확인 아님",
                    "에이전트 실행·회계 감사·보안 집행은 수행하지 않음",
                    "브라우저 DOM 통합 동작은 설치 후 확인 필요",
                ],
            }
            for relative in TARGETS:
                path = safe_path(relative)
                actual = path.read_bytes() if path.exists() else None
                if actual != originals[relative]:
                    fail("백업 전 동시 변경: " + relative)
                if actual is not None:
                    destination = backup / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, destination)
                    if destination.read_bytes() != actual:
                        fail("백업 검증 실패: " + relative)
                report["files"][relative] = {
                    "existed": actual is not None,
                    "before_sha256": digest(actual) if actual is not None else None,
                    "after_sha256": digest(plan[relative]),
                }
            atomic_write(backup / "verification.json", json_bytes(report))

            if result_text(git("rev-parse", "HEAD")) != initial_head:
                fail("적용 전 HEAD 동시 변경")
            for relative in TARGETS:
                path = safe_path(relative)
                actual = path.read_bytes() if path.exists() else None
                if actual != originals[relative]:
                    fail("적용 전 파일 동시 변경: " + relative)

            for relative in changed:
                applied.append(relative)
                atomic_write(safe_path(relative), plan[relative], modes[relative])

            for relative in TARGETS:
                if safe_path(relative, True).read_bytes() != plan[relative]:
                    fail("적용 결과 바이트 불일치: " + relative)
            for name in MEMORIES:
                values = [
                    json_load(safe_path(prefix + name, True).read_bytes(), prefix + name)
                    for prefix in ("", "dashboard/", "docs/")
                ]
                if not all(value == values[0] for value in values):
                    fail("루트/dashboard/docs 동기화 실패: " + name)

            alternate = environment.copy()
            alternate["GIT_INDEX_FILE"] = str(temp_path / "install-index")
            git("read-tree", initial_head, env=alternate)
            # 관련 없는 미추적 파일과 다른 파일의 기존 staged 변경은 포함하지 않는다.
            git("add", "-A", "--", *changed, env=alternate)
            for relative in changed:
                blob = result_text(git(
                    "hash-object", "-w", "--stdin", data=plan[relative]
                ))
                git(
                    "update-index", "--add", "--cacheinfo",
                    git_modes[relative], blob, relative, env=alternate,
                )
            staged = {
                item.decode("utf-8")
                for item in git(
                    "diff", "--cached", "--name-only", "-z", env=alternate
                ).stdout.split(b"\0") if item
            }
            if staged != set(changed):
                fail("Git 변경 범위 검증 실패")
            for relative in changed:
                if git("show", ":" + relative, env=alternate).stdout != plan[relative]:
                    fail("Git staged 바이트 불일치: " + relative)
            if result_text(git("rev-parse", "HEAD")) != initial_head:
                fail("커밋 직전 HEAD 변경")

            committed = git(
                "commit", "-m", MESSAGE, env=alternate, check=False, timeout=180
            )
            current = result_text(git("rev-parse", "HEAD"))
            if current != initial_head:
                own_commit = current
            if committed.returncode or not own_commit:
                fail(
                    "Git commit 실패:\n" +
                    (committed.stdout + committed.stderr).decode("utf-8", errors="replace")
                )
            if result_text(git("rev-parse", "HEAD^")) != initial_head:
                fail("커밋 부모 검증 실패")
            committed_paths = {
                item.decode("utf-8")
                for item in git(
                    "diff-tree", "--no-commit-id", "--name-only", "-r", "-z", own_commit
                ).stdout.split(b"\0") if item
            }
            if committed_paths != set(changed):
                fail("커밋 파일 범위 불일치")
            for relative in changed:
                if git("show", own_commit + ":" + relative).stdout != plan[relative]:
                    fail("커밋 산출물 바이트 불일치: " + relative)
                if safe_path(relative, True).read_bytes() != plan[relative]:
                    fail("커밋 중 파일 동시 변경: " + relative)
            if remote() != initial_head:
                fail("푸시 직전 원격 변경")
            if result_text(git("rev-parse", "HEAD")) != own_commit:
                fail("푸시 직전 로컬 HEAD 변경")

            push_uncertain = True
            pushed = git("push", "origin", "main", check=False, timeout=180)
            remote_after = remote()
            if remote_after == initial_head:
                push_uncertain = False
                fail(
                    "원격에 푸시가 반영되지 않았습니다:\n" +
                    (pushed.stdout + pushed.stderr).decode("utf-8", errors="replace")
                )
            if remote_after != own_commit:
                fail("원격 상태가 예상과 다릅니다. 자동 이력 되감기 금지.")

            # 실제 인덱스에서는 이번 파일 엔트리만 새 HEAD와 맞춘다.
            for relative in changed:
                blob = result_text(git("rev-parse", own_commit + ":" + relative))
                git(
                    "update-index", "--add", "--cacheinfo",
                    git_modes[relative], blob, relative,
                )

            report["commit"] = own_commit
            report["remote_main_verified"] = remote_after
            report["result"] = "COMPLETE"
            atomic_write(backup / "verification.json", json_bytes(report))
            print("[검증] node --check / 원문 보존 / 실제 ID 속성 / 항체 12종 동기화 PASS")
            print("[백업·Minimal Diff 증거] " + str(backup / "verification.json"))
            print("[Git] " + own_commit + " → origin/main 확인")
            print("[주의] immutable 선언은 OS 잠금이 아니며, 미확인 가동·지출·무결성은 미확인으로 표시합니다.")
            print("[주의] file://에서는 설치 스냅샷일 수 있습니다. 페이지 새로고침 후 점검하세요.")
            print("[STEP 10 6-AGENCIES AWAKEN COMPLETE]")

        except BaseException:
            if applied and not push_uncertain:
                restore()
            elif push_uncertain:
                print(
                    "[자동 롤백 보류] 원격 반영 또는 반영 여부 불확실. 원격 확인 후 판단하세요.",
                    file=sys.stderr,
                )
                print("백업: " + str(backup), file=sys.stderr)
                if own_commit:
                    print("설치 커밋: " + own_commit, file=sys.stderr)
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
        print("[STEP 10 INTERRUPTED] 복구·원격 확인 안내를 확인하세요.", file=sys.stderr)
        sys.exit(130)
    except BaseException as exc:
        print("[STEP 10 FAILED] " + str(exc), file=sys.stderr)
        sys.exit(1)
Copy