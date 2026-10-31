import os, json
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
LEDGER_JSON = 'S1_BRAIN_CIRCUIT_DAILY.json'
LEDGER_MD = 'S1_DAILY_CHRONICLE.md'

def record_event(category, task, status, cause, result, commit_ref='HEAD'):
    now = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')
    day = datetime.now(KST).strftime('%Y-%m-%d')
    data = {'project': 'S1_SUN_ONE_AON', 'updated_at': now, 'days': {}}
    if os.path.exists(LEDGER_JSON):
        try:
            with open(LEDGER_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            pass
    if day not in data.get('days', {}):
        data.setdefault('days', {})[day] = []
    entry = {
        'timestamp': now,
        'category': category,
        'task': task,
        'status': status,
        'cause': cause,
        'result': result,
        'commit': commit_ref
    }
    data['days'][day].append(entry)
    data['updated_at'] = now
    with open(LEDGER_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    md_lines = [
        '# 🧠 S1 두뇌회로 일일 기록서기 원장 (S1 Daily Chronicle)',
        f'> 최종 갱신: `{now}` | 전담: **S1 기록서기 에이전트 (Scribe Agent v1.0)**',
        ''
    ]
    for d in sorted(data['days'].keys(), reverse=True):
        md_lines.append(f'## 📅 {d} 일과 및 작업 정밀 기록')
        md_lines.append('| 시각 | 구분 | 작업 내용 | 상태 | 실패/성공 원인 분석 | 최종 결과 및 대책 |')
        md_lines.append('|---|---|---|---|---|---|')
        for e in data['days'][d]:
            md_lines.append(f"| {e['timestamp']} | **{e['category']}** | {e['task']} | `{e['status']}` | {e['cause']} | {e['result']} |")
        md_lines.append('')
    with open(LEDGER_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    return entry

if __name__ == '__main__':
    record_event('SYSTEM', '기록서기 에이전트 가동 점검', 'SUCCESS', '두뇌회로 상시 기록 아키텍처 수립', 'JSON 및 Markdown 이중 원장 동기화 완료')
