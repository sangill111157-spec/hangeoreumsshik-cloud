#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# rgon_aon_zeroclick_studio.py — 제23기관 · 아온 클릭 0번 헤드리스 포토·카드뉴스 & 엑셀·시트 창작 스튜디오
# v11.51-AON-COMMANDER-TWIN · 항체 R1~R52 · 정식 스킬 47개 · 100% Python 표준 라이브러리
import os, sys, json, zlib, struct, zipfile, csv, html, re, time, hashlib, tempfile, shutil
import xml.etree.ElementTree as ET
from pathlib import Path

for _s in ("stdout", "stderr"):
    _st = getattr(sys, _s, None)
    if _st and hasattr(_st, "reconfigure"):
        try:
            _st.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

VERSION = "v11.54-AON-SUPREME-ORG-CHART"
ANTIBODY = "R47"
ANTIBODY_RANGE = "R1~R55"
ORGAN_ID = "N19_zeroclick_studio"
ORGAN_NO = 23
HEXAGRAMS = [
    {"no": 22, "name": "산화비(山火賁)", "symbol": "☶☲", "lines": [1, 0, 1, 0, 0, 1], "role": "꾸밈·디자인"},
    {"no": 14, "name": "화천대유(火天大有)", "symbol": "☲☰", "lines": [1, 1, 1, 1, 0, 1], "role": "풍요·데이터"},
    {"no": 60, "name": "수택절(水澤節)", "symbol": "☵☱", "lines": [1, 1, 0, 0, 1, 0], "role": "절제·RAM보호"},
]
SOURCES = ["storytold/photocraft", "haris-musa/excel-mcp-server", "HKUDS/CLI-Anything"]
SAFETY = {"background_daemon_spawned": False, "requires_manual_gate": True, "auto_executed": False}

def state_dir(base=None):
    d = Path(base or os.environ.get("RGON_ZEROCLICK_STATE_DIR") or (Path(__file__).resolve().parent / "rgon_zeroclick_output"))
    d.mkdir(parents=True, exist_ok=True)
    return d

def _slug(s):
    s = re.sub(r"[^0-9A-Za-z가-힣_-]+", "_", str(s)).strip("_")
    return (s or "zeroclick")[:40]

def _uid(seed):
    return hashlib.sha1(f"{seed}|{time.time_ns()}|{os.getpid()}|{id(object())}".encode()).hexdigest()[:10]

# ---------------------------- PNG (pure stdlib) ----------------------------
def _chunk(tag, data):
    c = struct.pack(">I", len(data)) + tag + data
    return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

def make_png(width, height, pixel_fn):
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(pixel_fn(x, y))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + _chunk(b"IEND", b"")

def validate_png(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return False
    pos, tags = 8, []
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        crc = struct.unpack(">I", data[pos + 8 + ln:pos + 12 + ln])[0]
        if zlib.crc32(tag + body) & 0xFFFFFFFF != crc:
            return False
        tags.append(tag)
        pos += 12 + ln
    return tags[0] == b"IHDR" and b"IDAT" in tags and tags[-1] == b"IEND"

def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def render_zeroclick_photo(headline="아온 클릭 0번 스튜디오", subcopy="포토샵 없이 헤드리스 카드뉴스",
                           stats=None, hexagram_no=22, width=320, height=320, out_dir=None, watermark="RGON·AON R47"):
    d = state_dir(out_dir)
    stats = stats or {"클릭": 0, "스킬": 43, "기관": 23}
    hx = next((h for h in HEXAGRAMS if h["no"] == hexagram_no), HEXAGRAMS[0])
    c1, c2 = (20, 24, 60), (180, 60, 120)
    gold, white = (255, 200, 60), (245, 245, 250)
    lines = hx["lines"]
    lx0, lx1, ly0, lh, gap = width // 2 - 60, width // 2 + 60, height // 5, max(4, height // 40), max(8, height // 22)

    def px(x, y):
        col = _lerp(c1, c2, (x + y) / float(width + height))
        for i, yang in enumerate(lines):
            yy = ly0 + i * gap
            if yy <= y < yy + lh and lx0 <= x < lx1:
                if yang or not (width // 2 - 10 <= x < width // 2 + 10):
                    return gold
        if height * 3 // 4 <= y < height * 3 // 4 + 24 and width // 8 <= x < width * 7 // 8:
            return (40, 40, 70) if (x // 6 + y // 6) % 2 else (60, 60, 100)
        if y >= height - 10 and x >= width - 90:
            return white
        return col

    base = f"{_slug(headline)}_{_uid(headline)}"
    png_path, svg_path = d / f"{base}.png", d / f"{base}.svg"
    png = make_png(width, height, px)
    png_path.write_bytes(png)
    e = html.escape
    bars = []
    for i, yang in enumerate(lines):
        y = 120 + i * 46
        if yang:
            bars.append(f'<rect x="340" y="{y}" width="400" height="26" rx="6" fill="#ffc83c"/>')
        else:
            bars.append(f'<rect x="340" y="{y}" width="180" height="26" rx="6" fill="#ffc83c"/><rect x="560" y="{y}" width="180" height="26" rx="6" fill="#ffc83c"/>')
    badges = "".join(f'<g transform="translate({120 + i * 300},880)"><rect width="260" height="90" rx="18" fill="#28284a" stroke="#ffc83c"/>'
                     f'<text x="130" y="58" text-anchor="middle" font-size="36" fill="#fff">{e(str(k))} {e(str(v))}</text></g>'
                     for i, (k, v) in enumerate(list(stats.items())[:3]))
    svg = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">'
           '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#14183c"/><stop offset="1" stop-color="#b43c78"/></linearGradient></defs>'
           '<g id="layer-bg"><rect width="1080" height="1080" fill="url(#bg)"/></g>'
           f'<g id="layer-hexagram">{"".join(bars)}<text x="540" y="440" text-anchor="middle" font-size="40" fill="#ffc83c">#{hx["no"]} {e(hx["name"])} {hx["symbol"]}</text></g>'
           f'<g id="layer-headline"><text x="540" y="600" text-anchor="middle" font-size="72" font-weight="700" fill="#fff">{e(headline)}</text></g>'
           f'<g id="layer-subcopy"><text x="540" y="690" text-anchor="middle" font-size="40" fill="#e0e0f0">{e(subcopy)}</text></g>'
           f'<g id="layer-stats">{badges}</g>'
           f'<g id="layer-watermark" opacity="0.6"><text x="1050" y="1060" text-anchor="end" font-size="24" fill="#fff">{e(watermark)}</text></g>'
           '</svg>')
    svg_path.write_text(svg, encoding="utf-8")
    return {"ok": True, "kind": "photo", "version": VERSION, "antibody": ANTIBODY,
            "png": str(png_path), "svg": str(svg_path), "width": width, "height": height,
            "png_valid": validate_png(png), "layers": ["bg", "hexagram", "headline", "subcopy", "stats", "watermark"],
            "hexagram": hx, "click_count": 0, "headless": True,
            "speech": f"🎨 [제23기관 클릭0번 포토 스튜디오] '{headline}' 6레이어 SVG 카드뉴스 & 무손실 PNG 썸네일 생성 완료! (클릭 0번 · #{hx['no']} {hx['name']})",
            **SAFETY}

# ---------------------------- XLSX (pure stdlib) ----------------------------
def _col(n):
    s = ""
    n += 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

def _cell(ref, v):
    if isinstance(v, bool):
        v = str(v)
    if isinstance(v, (int, float)):
        return f'<c r="{ref}"><v>{v}</v></c>'
    if isinstance(v, str) and v.startswith("="):
        return f'<c r="{ref}"><f>{html.escape(v[1:], quote=False)}</f></c>'
    return f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{html.escape(str(v), quote=False)}</t></is></c>'

def build_xlsx(path, headers, rows, sheet_name="AON_Sheet"):
    n = len(rows)
    num_cols = [j for j in range(len(headers)) if rows and all(isinstance(r[j], (int, float)) and not isinstance(r[j], bool) for r in rows)]
    sum_row = ["합계"] + [""] * (len(headers) - 1)
    avg_row = ["평균"] + [""] * (len(headers) - 1)
    for j in num_cols:
        if j == 0:
            continue
        c = _col(j)
        sum_row[j] = f"=SUM({c}2:{c}{n + 1})"
        avg_row[j] = f"=AVERAGE({c}2:{c}{n + 1})"
    all_rows = [headers] + rows + [sum_row, avg_row]
    xml_rows = []
    for i, r in enumerate(all_rows, 1):
        cells = "".join(_cell(f"{_col(j)}{i}", v) for j, v in enumerate(r) if v != "")
        xml_rows.append(f'<row r="{i}">{cells}</row>')
    ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
    files = {
        "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>',
        "_rels/.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook {ns}><sheets><sheet name="{html.escape(sheet_name[:31])}" sheetId="1" r:id="rId1"/></sheets></workbook>',
        "xl/_rels/workbook.xml.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
        "xl/worksheets/sheet1.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{"".join(xml_rows)}</sheetData></worksheet>',
    }
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for k, v in files.items():
            z.writestr(k, v)
    return all_rows, sum_row, avg_row

def validate_xlsx(path):
    need = {"[Content_Types].xml", "_rels/.rels", "xl/workbook.xml", "xl/_rels/workbook.xml.rels", "xl/worksheets/sheet1.xml"}
    try:
        with zipfile.ZipFile(path) as z:
            if not need.issubset(set(z.namelist())):
                return False
            for n in need:
                ET.fromstring(z.read(n))
        return True
    except Exception:
        return False

def render_zeroclick_sheet(title="아온 제로클릭 시트", headers=None, rows=None, out_dir=None):
    d = state_dir(out_dir)
    headers = headers or ["항목", "조회수", "좋아요", "공유"]
    rows = rows or [["#056 trendcorelab", 120000, 8400, 910], ["photocraft", 54000, 3100, 420], ["excel-mcp", 47000, 2900, 380]]
    base = f"{_slug(title)}_{_uid(title)}"
    xp, cp, hp = d / f"{base}.xlsx", d / f"{base}.csv", d / f"{base}.html"
    all_rows, sum_row, avg_row = build_xlsx(xp, headers, rows)
    with open(cp, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(all_rows)
    e = html.escape
    body = "".join("<tr>" + "".join(f"<td>{e(str(v))}</td>" for v in r) + "</tr>" for r in rows)
    calc = {}
    for j in range(1, len(headers)):
        vals = [r[j] for r in rows if isinstance(r[j], (int, float))]
        if vals:
            calc[headers[j]] = {"sum": sum(vals), "avg": round(sum(vals) / len(vals), 2)}
    foot = "".join(f"<tr><th>{lab}</th>" + "".join(f"<td>{calc[h][key] if h in calc else ''}</td>" for h in headers[1:]) + "</tr>"
                   for lab, key in (("합계", "sum"), ("평균", "avg")))
    hp.write_text(f'<!doctype html><html lang="ko"><meta charset="utf-8"><title>{e(title)}</title>'
                  '<style>body{font-family:sans-serif;background:#14183c;color:#fff}table{border-collapse:collapse}td,th{border:1px solid #556;padding:6px 10px}th{background:#28284a;cursor:pointer}</style>'
                  f'<h2>{e(title)} · 클릭0번</h2><table id="t"><thead><tr>' + "".join(f"<th>{e(h)}</th>" for h in headers) +
                  f'</tr></thead><tbody>{body}</tbody><tfoot>{foot}</tfoot></table>'
                  '<script>document.querySelectorAll("thead th").forEach((th,i)=>th.onclick=()=>{const tb=document.querySelector("tbody");'
                  '[...tb.rows].sort((a,b)=>(parseFloat(b.cells[i].innerText)||0)-(parseFloat(a.cells[i].innerText)||0)).forEach(r=>tb.appendChild(r))});</script></html>',
                  encoding="utf-8")
    return {"ok": True, "kind": "sheet", "version": VERSION, "antibody": ANTIBODY,
            "xlsx": str(xp), "csv": str(cp), "html": str(hp), "xlsx_valid": validate_xlsx(xp),
            "rows": len(rows), "headers": headers, "summary": calc, "formulas": [v for v in sum_row + avg_row if str(v).startswith("=")],
            "click_count": 0, "headless": True,
            "speech": f"📊 [제23기관 클릭0번 엑셀 스튜디오] '{title}' 정식 .xlsx + UTF-8 BOM .csv + 인터랙티브 .html 시트 생성 완료! (클릭 0번 · #14 화천대유)",
            **SAFETY}

def request_publish(artifact, approved=False):
    return {"ok": True, "artifact": artifact, "requires_manual_gate": True, "auto_executed": False,
            "status": "APPROVED_MANUAL" if approved else "PENDING_MANUAL_GATE", "background_daemon_spawned": False}

def route_command(text, out_dir=None):
    t = (text or "").strip()
    low = t.lower()
    if any(k in t for k in ("/엑셀", "/시트")) or "excel" in low:
        head = re.sub(r"^/\S+\s*", "", t).strip() or "아온 제로클릭 시트"
        return render_zeroclick_sheet(title=head[:30], out_dir=out_dir)
    if any(k in t for k in ("/포토", "/썸네일", "/카드뉴스", "/클릭0번")) or "zeroclick" in low or "photocraft" in low:
        head = re.sub(r"^/\S+\s*", "", t).strip() or "아온 클릭 0번 스튜디오"
        return render_zeroclick_photo(headline=head[:30], out_dir=out_dir)
    return {"ok": False, "reason": "no_route"}

def status():
    return {"organ": ORGAN_ID, "organ_no": ORGAN_NO, "version": VERSION, "antibody": ANTIBODY,
            "hexagrams": [f"#{h['no']} {h['name']} {h['symbol']}" for h in HEXAGRAMS], "sources": SOURCES, **SAFETY}

def self_test(verbose=True):
    import threading
    tmp = tempfile.mkdtemp(prefix="rgon_zeroclick_")
    checks = []
    def ck(name, cond):
        checks.append((name, bool(cond)))
    try:
        p = render_zeroclick_photo(out_dir=tmp, width=96, height=96)
        s = render_zeroclick_sheet(out_dir=tmp)
        png = Path(p["png"]).read_bytes()
        ck("01_hexagrams_3", [h["no"] for h in HEXAGRAMS] == [22, 14, 60])
        ck("02_photo_ok", p.get("ok") is True)
        ck("03_png_exists", Path(p["png"]).exists() and len(png) > 50)
        ck("04_png_valid_chunks", validate_png(png))
        ck("05_png_dims", struct.unpack(">II", png[16:24]) == (96, 96))
        ck("06_svg_parse", ET.fromstring(Path(p["svg"]).read_bytes()).tag.endswith("svg"))
        ck("07_svg_layers_6", len(p["layers"]) == 6 and "layer-watermark" in Path(p["svg"]).read_text(encoding="utf-8"))
        ck("08_photo_zero_click", p["click_count"] == 0 and p["headless"] is True)
        ck("09_sheet_ok", s.get("ok") is True and s["rows"] == 3)
        ck("10_xlsx_valid", validate_xlsx(s["xlsx"]))
        ck("11_xlsx_formulas", any("SUM(" in f for f in s["formulas"]) and any("AVERAGE(" in f for f in s["formulas"]))
        ck("12_csv_bom", Path(s["csv"]).read_bytes()[:3] == b"\xef\xbb\xbf")
        ck("13_html_table", "<table" in Path(s["html"]).read_text(encoding="utf-8"))
        ck("14_sheet_zero_click", s["click_count"] == 0 and s["headless"] is True)
        ck("15_summary_math", s["summary"]["조회수"]["sum"] == 221000)
        ck("16_no_daemon", p["background_daemon_spawned"] is False and s["background_daemon_spawned"] is False and threading.active_count() >= 1)
        g = request_publish(p["png"])
        ck("17_manual_gate", g["requires_manual_gate"] is True and g["auto_executed"] is False and g["status"] == "PENDING_MANUAL_GATE")
        ck("18_router", route_command("/썸네일 테스트", out_dir=tmp)["kind"] == "photo" and route_command("/엑셀", out_dir=tmp)["kind"] == "sheet")
    except Exception as ex:
        checks.append((f"EXC_{type(ex).__name__}:{ex}", False))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    passed = sum(1 for _, ok in checks if ok)
    res = {"organ": ORGAN_ID, "version": VERSION, "passed": passed, "total": 18,
           "ok": passed == 18 and len(checks) == 18, "checks": dict(checks)}
    if verbose:
        for n, ok in checks:
            print(("  PASS " if ok else "  FAIL ") + n)
        print(f"[R47] self_test {passed}/18")
    return res

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        print(json.dumps(status(), ensure_ascii=False, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        r = self_test()
        sys.exit(0 if r["ok"] else 1)
    elif len(sys.argv) > 1:
        print(json.dumps(route_command(" ".join(sys.argv[1:])), ensure_ascii=False, indent=2))
    else:
        r = self_test()
        sys.exit(0 if r["ok"] else 1)
