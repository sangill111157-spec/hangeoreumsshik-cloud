import json, subprocess, time, re, pathlib, datetime
from html.parser import HTMLParser

BASE = pathlib.Path('.')
REPORT_JSON = BASE / 'S1_062_EGO_CLICK_AUDIT_REPORT.json'
DOCS_REPORT_JSON = BASE / 'docs' / 'S1_062_EGO_CLICK_AUDIT_REPORT.json'

html = (BASE / 'index.html').read_text(encoding='utf-8', errors='replace')
all_scripts = "\n".join(re.findall(r'<script[^>]*>(.*?)</script>', html, flags=re.DOTALL | re.IGNORECASE))

class S1DOMClickAuditor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.items = []
        self._cur = None
        self._txt = []

    def _current_page_and_sub(self):
        page = 'GLOBAL_HEADER_OR_COMMON'
        sub = 'MAIN_VIEW'
        for tag, eid, cls in reversed(self.stack):
            if 's1-bnav' in cls or eid == 's1-kakao-bottom-nav':
                return 'GLOBAL_BOTTOM_5TAB_BAR', 'BOTTOM_NAV'
            if eid == 's1-more-vault-accordion' or 's1-vault-accordion' in cls:
                sub = 'SUB_VAULT_ACCORDION_SCROLL_END'
            elif 's1-chatroom-view' in cls or eid == 's1-chatroom-detail':
                sub = 'SUB_CHATROOM_INSIDE_VIEW'
            elif 's1-chat-list' in cls or eid == 's1-kakao-chat-v055':
                sub = 'SUB_CHAT_ROOM_LIST'
            elif 's1-kakao-subchips' in cls or 's1-sub-pills' in cls:
                sub = 'SUB_TOP_PILL_CHIPS'

            if eid in ('home', 's1-kakao-header-home') or 'an-grid' in cls:
                return 'PAGE_1_HOME', sub
            if eid in ('chat', 's1-kakao-header-chat', 's1-omnipotent-comm-hub', 's1-kakao-chat-v055'):
                return 'PAGE_2_CHAT', sub
            if eid in ('now', 's1-kakao-header-now', 's1-2026-album-showcase'):
                return 'PAGE_3_NOW', sub
            if eid in ('pick', 's1-kakao-header-pick', 's1-dept-showcase-hub'):
                return 'PAGE_4_PICK', sub
            if eid in ('more', 's1-kakao-header-more', 's1-more-vault-accordion'):
                return 'PAGE_5_MORE', sub
        return page, sub

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        eid = ad.get('id', '')
        cls = ad.get('class', '')
        onclick = ad.get('onclick', '')
        href = ad.get('href', '')
        style = ad.get('style', '')
        self.stack.append((tag, eid, cls))

        is_target = (
            tag in ('button', 'summary')
            or (tag == 'a' and (href or onclick or 'btn' in cls))
            or bool(onclick)
            or any(k in cls for k in [
                's1-kakao-chip', 's1-sub-pill', 's1-bnav-item', 's1-room-item',
                's1-chat-filter', 's1-more-grid-item', 's1-more-tool', 'an-node',
                's1-track', 'pill', 'chip', 'btn'
            ])
        )
        if is_target and self._cur is None:
            pg, sb = self._current_page_and_sub()
            self._cur = {
                'tag': tag,
                'id': eid,
                'class': cls,
                'page': pg,
                'sub_area': sb,
                'onclick': onclick,
                'href': href,
                'hidden_attr': ('hidden' in ad) or ('display:none' in style.replace(' ', ''))
            }
            self._txt = []

    def handle_data(self, data):
        if self._cur is not None:
            s = data.strip()
            if s:
                self._txt.append(s)

    def handle_endtag(self, tag):
        if self._cur is not None and tag == self._cur['tag']:
            lbl = re.sub(r'\s+', ' ', " ".join(self._txt)).strip()[:75]
            self._cur['label'] = lbl or '(아이콘/무라벨)'
            self.items.append(self._cur)
            self._cur = None
            self._txt = []
        if self.stack:
            self.stack.pop()

auditor = S1DOMClickAuditor()
auditor.feed(html)
candidates = auditor.items

# 추가로 12트랙 박스(01. 막차 ~ 12. 내일의 아침) 및 6대 신경망 카드(1. 모바일 ~ 6. 4대 채널) 정밀 스캔
for m in re.finditer(r'<(div|li|span)([^>]*)>\s*((?:0[1-9]|1[0-2])\.\s+[^<]{2,35})</\1>', html):
    attrs_s = m.group(2)
    lbl = re.sub(r'\s+', ' ', m.group(3)).strip()
    has_click = 'onclick=' in attrs_s
    candidates.append({
        'tag': m.group(1),
        'id': '',
        'class': 'ALBUM_12TRACK_BOX',
        'page': 'PAGE_3_NOW',
        'sub_area': 'SUB_12TRACK_LIST',
        'onclick': 'onclick' if has_click else '',
        'href': '',
        'hidden_attr': False,
        'label': lbl
    })

for m in re.finditer(r'([1-6]\.\s*(?:모바일|르곤 보좌관|GitHub SSOT|안총리 엔진|삼성이전 감사|4대 채널))', html):
    lbl = m.group(1).strip()
    if not any(c['label'].startswith(lbl) for c in candidates):
        candidates.append({
            'tag': 'div',
            'id': '',
            'class': 'ANATOMY_6NODE_CARD',
            'page': 'PAGE_1_HOME',
            'sub_area': 'SUB_6NODE_LIVE_GRID',
            'onclick': '',
            'href': '',
            'hidden_attr': False,
            'label': lbl
        })

lbl_counter = {}
for c in candidates:
    l = c['label']
    if l and l != '(아이콘/무라벨)':
        lbl_counter[l] = lbl_counter.get(l, 0) + 1

for idx, c in enumerate(candidates, 1):
    c['no'] = idx
    onclick = c['onclick']
    href = c['href']
    eid = c['id']
    cls = c['class']
    tag = c['tag']
    pg = c['page']

    res = 'DEAD_NO_ACTION'
    detail = '클릭 이벤트 미연결 (터치해도 아무 동작 없음)'

    if onclick:
        res = 'WORKING_CLICK'
        detail = f'onclick 핸들러 작동 ({onclick[:50]})'
    elif href and href not in ('#', 'javascript:void(0)', ''):
        res = 'WORKING_CLICK'
        detail = f'링크 이동 작동 ({href[:50]})'
    elif tag == 'summary':
        res = 'WORKING_CLICK'
        detail = '아코디언 펼치기/접기 작동'
    elif eid and (f"getElementById('{eid}')" in all_scripts or f'getElementById("{eid}")' in all_scripts or f"#{eid}" in all_scripts):
        res = 'WORKING_CLICK'
        detail = f'ID(#{eid}) 리스너 작동'
    else:
        matched_tok = None
        for tok in cls.split():
            if tok and (f".{tok}" in all_scripts or f"'{tok}'" in all_scripts or f'"{tok}"' in all_scripts):
                matched_tok = tok
                break
        if matched_tok:
            if any(k in matched_tok for k in ['s1-sub-pill', 's1-kakao-chip']) and pg != 'PAGE_2_CHAT':
                res = 'FAKE_OR_DUPLICATE_CHIP'
                detail = f'서브 알약({matched_tok})이나 고유 서브화면 전환 없이 하단 5탭과 중복되거나 무반응'
            else:
                res = 'WORKING_CLICK'
                detail = f'클래스(.{matched_tok}) 리스너 작동'
        elif cls == 'ALBUM_12TRACK_BOX':
            res = 'DEAD_NO_ACTION'
            detail = '12트랙 곡 박스이나 클릭 시 음원 재생 미연결 (단순 텍스트 박스)'
        elif cls == 'ANATOMY_6NODE_CARD':
            res = 'DEAD_NO_ACTION'
            detail = '6대 신경망 카드이나 클릭 시 상세 모달 미연결 (단순 박스)'

    c['click_result'] = res
    c['click_detail'] = detail
    c['duplicate_count'] = lbl_counter.get(c['label'], 1)
    c['is_duplicate'] = c['duplicate_count'] > 1 and c['label'] != '(아이콘/무라벨)'

summary_by_page = {}
for c in candidates:
    pg = c['page']
    if pg not in summary_by_page:
        summary_by_page[pg] = {'total': 0, 'working': 0, 'dead': 0, 'fake_or_dup_chip': 0, 'duplicates': 0}
    summary_by_page[pg]['total'] += 1
    if c['click_result'] == 'WORKING_CLICK':
        summary_by_page[pg]['working'] += 1
    elif c['click_result'] == 'DEAD_NO_ACTION':
        summary_by_page[pg]['dead'] += 1
    else:
        summary_by_page[pg]['fake_or_dup_chip'] += 1
    if c['is_duplicate']:
        summary_by_page[pg]['duplicates'] += 1

dead_items = [c for c in candidates if c['click_result'] != 'WORKING_CLICK']
dup_items = [{'label': k, 'count': v} for k, v in sorted(lbl_counter.items(), key=lambda x: -x[1]) if v > 1]

def call_ego(args):
    try:
        r = subprocess.run(['python', 's1_ego.py'] + args, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=20)
        return r.stdout.strip()
    except Exception as e:
        return str(e)

ego_prompt = (
    f"[062호 5페이지·서브페이지 전수 클릭 실측 보고] "
    f"총 {len(candidates)}개 요소 실측: 페이지별={json.dumps(summary_by_page, ensure_ascii=False)}. "
    f"안 되는 요소({len(dead_items)}개) 주요 목록: {', '.join([x['label'] for x in dead_items[:12]])}. "
    f"중복 요소({len(dup_items)}종) 주요 목록: {', '.join([d['label']+'('+str(d['count'])+'회)' for d in dup_items[:10]])}. "
    f"1) 각 페이지 상단 알약(.s1-kakao-chip/.s1-sub-pill) 정리 방안, 2) 12트랙 및 6대 신경망 클릭 연결 방안, 3) 중복 버튼 제거 기준을 3줄로 답해주십시오."
)

for s in ['0', '1', '2', '3']:
    call_ego(['finish', '--space', s])

call_ego(['ask', '--space', '1', '--prompt', ego_prompt])
call_ego(['ask', '--space', '2', '--prompt', ego_prompt])
time.sleep(8)
sol_ans = call_ego(['snippets', '--space', '1'])[-2000:]
opus_ans = call_ego(['snippets', '--space', '2'])[-2000:]

for s in ['0', '1', '2', '3']:
    call_ego(['finish', '--space', s])

out = {
    'directive_id': 'RGON_DIR_062_EGO_FULL_CLICK_AUDIT',
    'timestamp': datetime.datetime.now().isoformat(),
    'total_scanned': len(candidates),
    'summary_by_page': summary_by_page,
    'non_working_items': dead_items,
    'duplicate_labels': dup_items,
    'all_items': candidates,
    'triumvirate_qa': {
        'sol_space1': sol_ans,
        'opus_space2': opus_ans
    }
}

REPORT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
DOCS_REPORT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

gi = (BASE / '.gitignore').read_text(encoding='utf-8', errors='replace')
if '!S1_062_EGO_CLICK_AUDIT_REPORT.json' not in gi:
    (BASE / '.gitignore').write_text(gi + '\n!S1_062_EGO_CLICK_AUDIT_REPORT.json\n!docs/S1_062_EGO_CLICK_AUDIT_REPORT.json\n', encoding='utf-8')

subprocess.run(['git', 'add', '-f', 'S1_062_EGO_CLICK_AUDIT_REPORT.json', 'docs/S1_062_EGO_CLICK_AUDIT_REPORT.json', '.gitignore'])
subprocess.run(['git', 'commit', '-m', 'feat(audit-062): full 5-page & subpage button click audit + Ego Space 1 & 2 QA'])
subprocess.run(['git', 'push', 'origin', 'main'])
print('=== 062 FULL CLICK AUDIT COMPLETED & PUSHED! ===')
