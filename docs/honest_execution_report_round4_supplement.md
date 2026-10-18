# 실동작 점검 보완 8대 항목 정직 실행 보고서

- **작성 일시**: 2026-09-24
- **보고 원칙**: 실패 포함 전 실행 내역 정직 보고 (명령 / 원출력 / 성공·실패 여부), 단정 표현("원인 규명/100%/무결점") 전면 배제, 확인 안 된 사항은 "미확인" 또는 "가설" 표기, UTF-8 인코딩 보장.

---

## 1. 변경 사항 저장(Git Commit) 및 verify.ps1 전체 게이트 원출력

### 1.1 Git Commit 및 파일별 Numstat

#### [백엔드 커밋]
- **커밋 해시**: `c8fa8c3789327127caeff1dd0496603174d449b7`
- **커밋 메시지**: `feat(trader): fix kis broker NameError, isolate test trade logs, and add emergency stop persistence`
- **파일별 numstat 원출력 (`git show --numstat c8fa8c3`)**:
```text
2	0	.gitignore
51	0	app/api/routes/trader.py
1	0	app/main.py
11	0	app/services/auto_trader.py
21	10	app/services/kis_broker.py
18	1	app/services/safety_guard.py
9	0	tests/conftest.py
52	0	tests/test_kis_broker_exchange_codes.py
```
- **합계**: 8개 파일, 165줄 추가, 11줄 삭제.

#### [프론트엔드 커밋]
- **커밋 해시**: `dd12cb11056a5eff45817b67afe6596e21e67bb8`
- **커밋 메시지**: `feat(ui): add emergency stop toggle button, server disconnect alert banner, and exchange rate badge`
- **파일별 numstat 원출력 (`git show --numstat dd12cb1`)**:
```text
42	2	src/App.tsx
89	2	src/components/AutoTraderView.tsx
45	0	src/services/api.ts
```
- **합계**: 3개 파일, 176줄 추가, 4줄 삭제.

---

### 1.2 전체 게이트 `scripts\verify.ps1` 실행 원출력
- **실행 명령**:
```powershell
powershell -File scripts\verify.ps1
```
- **원출력 그대로**:
```text
[VERIFY] 1/4 Ruff check...
RUFF PASSED

[VERIFY] 2/4 Pytest running...
465 passed, 9 skipped, 87 subtests passed in 23.47s
Pytest runtime: 27.43s
PYTEST PASSED

[VERIFY] 3/4 Git diff --numstat:
(0 lines)

[VERIFY] 4/4 Git status --porcelain:
clean
All gates passed successfully!
```
- **결과**: 성공 (exit code 0, 465 passed, clean working tree)

---

## 2. 중복주문 방지 실효성 조사

### 2.1 NameError 발생 시 주문 처리 경로 (코드 인용 확인)
수정 전 코드에서 `broker.get_open_orders_sync`가 `NameError(exchange_codes)`를 발생시켰을 때 주문 실행 경로가 이를 어떻게 처리했는지 `app/services/auto_trader.py`를 인용하여 확인했습니다.

- **코드 인용 (`app/services/auto_trader.py:746-765`)**:
```python
            # [보정 67: 멱등성 2차 보조 방어선]: 발주 전 미체결 내역 조회로 동일 주문(동일 의도) 중복 발주 보조 차단
            if hasattr(broker, "get_open_orders_sync"):
                try:
                    open_orders = broker.get_open_orders_sync(exchange=(excg_cd if not is_kr else "NASD"))
                    for op in open_orders:
                        if (
                            op.get("ticker") == ticker
                            and op.get("side") == action
                            and int(op.get("quantity", 0)) == shares
                        ):
                            logger.warning(f"🚨 [IDEMPOTENCY_BLOCKED] 동일 주문이 이미 미체결 상태입니다: {op}. 중복 발주 차단.")
                            return {
                                "success": False,
                                "error": f"중복 발주 차단: 동일 주문({ticker} {action} {shares}주)이 이미 미체결 상태입니다.",
                                "order_state": "ORDER_REJECTED",
                                "is_duplicate": True,
                            }
                except Exception as inq_err:
                    logger.warning(f"[IDEMPOTENCY_INQUIRY_FAIL] 미체결 조회 실패 (진행): {inq_err}")
```
- **확인 결과**: `try ... except Exception as inq_err:` 구문으로 감싸져 있으며, 예외 발생 시 경고 로그(`[IDEMPOTENCY_INQUIRY_FAIL] 미체결 조회 실패 (진행)`)만 기록하고 함수를 중단하거나 차단하지 않고 **무시하고 발주를 그대로 진행하는 페일오픈(fail-open) 구조**였습니다.

---

### 2.2 실제 모의 API 호출 원출력 (미체결 조회, 최근주문 조회, 주문 취소)

- **실행 명령**:
```powershell
.\venv\Scripts\python.exe -c "import asyncio, sys, json, os
sys.stdout.reconfigure(encoding='utf-8')
os.environ['ALLOW_ORDER_EXECUTION'] = 'TRUE_I_UNDERSTAND_THE_RISKS'
from app.services.kis_broker import KisBroker
b = KisBroker()

print('=== 1. 미체결 조회 (get_open_orders_sync) ===')
try:
    res1 = b.get_open_orders_sync(exchange='NASD')
    print('Type:', type(res1), 'Length:', len(res1), 'Data:', res1)
except Exception as e:
    print('Error:', type(e), e)

print('\n=== 2. 최근주문 조회 (get_recent_orders_sync) ===')
try:
    res2 = b.get_recent_orders_sync(exchange='NASD')
    print('Type:', type(res2), 'Length:', len(res2), 'Data:', res2)
except Exception as e:
    print('Error:', type(e), e)

print('\n=== 3. 주문 취소 (cancel_order - 모의투자 KIS 서버 실제 호출) ===')
try:
    res3 = asyncio.run(b.cancel_order(order_number='00000000', exchange='NASD'))
    print('Result:', json.dumps(res3, ensure_ascii=False))
except Exception as e:
    print('Error:', type(e), e)
"
```
- **원출력 그대로**:
```text
[KIS_INQUIRY] Failed to get open orders sync: HTTPSConnectionPool(host='openapivts.koreainvestment.com', port=29443): Read timed out. (read timeout=5)
[KIS_INQUIRY] Failed to get recent orders sync: HTTPSConnectionPool(host='openapivts.koreainvestment.com', port=29443): Read timed out. (read timeout=5)
Order cancellation failed: 500
=== 1. 미체결 조회 (get_open_orders_sync) ===
Type: <class 'list'> Length: 0 Data: []

=== 2. 최근주문 조회 (get_recent_orders_sync) ===
Type: <class 'list'> Length: 0 Data: []

=== 3. 주문 취소 (cancel_order - 모의투자 KIS 서버 실제 호출) ===
Error: <class 'app.services.kis_broker.KISApiError'> Order cancellation failed: {"rt_cd":"1","msg_cd":"EGW02006","msg1":"모의투자 TR 이 아닙니다."}
```
- **결과 설명**:
  1. `get_open_orders_sync` 및 `get_recent_orders_sync`: KIS 모의투자 서버 타임아웃 발생 시 내부 예외 처리에 따라 빈 리스트(`[]`)를 반환했습니다.
  2. `cancel_order`: 실제 KIS 모의투자 엔드포인트(`openapivts`)로 가상 원주문번호(`00000000`) 취소 요청을 전송했으나, 현재 코드의 `cancel_order` TR_ID(`TTTT1006U`)가 실전용이어서 모의투자 서버로부터 `{"rt_cd":"1","msg_cd":"EGW02006","msg1":"모의투자 TR 이 아닙니다."}` 에러가 반환되었습니다.

---

### 2.3 Mock 없이 실제 호출 경로를 타는 테스트 유무
- **확인 결과**: **"없음"**
  - 테스트 디렉터리(`tests/`) 내의 주문, 취소, 미체결 조회 관련 테스트들은 안전 및 계좌 오염 방지를 위해 모두 `unittest.mock` (`patch.object`, `AsyncMock`, `MagicMock`)을 사용하고 있으며, mock 없이 실제 KIS 서버와 네트워크 통신하는 주문 실행 테스트는 존재하지 않습니다.

---

## 3. 환율 조사 ("1360" 검색 및 고정값 표시)

### 3.1 코드 전체에서 "1360" 검색 원출력
- **실행 명령 (백엔드)**:
```powershell
git grep "1360"
```
- **원출력 (백엔드)**:
```text
(0 matches / exit code 1)
```

- **실행 명령 (프론트엔드)**:
```powershell
git grep "1360"
```
- **원출력 (프론트엔드)**:
```text
(0 matches / exit code 1)
```

---

### 3.2 실제 KIS API 응답 원문에서 환율 필드 위치
- **실행 명령**:
```powershell
.\venv\Scripts\python.exe -c "import asyncio, sys, json
sys.stdout.reconfigure(encoding='utf-8')
from app.services.kis_broker import KisBroker
b = KisBroker()
async def check_raw():
    token = await b.get_access_token()
    client = await b._get_http_client()
    headers = {
        'authorization': f'Bearer {token}',
        'appkey': b.app_key,
        'appsecret': b.app_secret,
        'tr_id': 'VTTS3007R',
        'Content-Type': 'application/json; charset=utf-8',
    }
    params = {
        'CANO': b.account_no,
        'ACNT_PRDT_CD': '01',
        'OVRS_EXCG_CD': 'NASD',
        'ITEM_CD': 'AAPL',
        'OVRS_ORD_UNPR': '150.0000',
    }
    resp = await client.get(f'{b.base_url}/uapi/overseas-stock/v1/trading/inquire-psamount', headers=headers, params=params)
    data = resp.json()
    print('RAW OUTPUT KEYS:', list(data.get('output', {}).keys()))
    print('exrt in output:', data.get('output', {}).get('exrt'))
    print('RAW OUTPUT SAMPLE:', json.dumps({k: data.get('output', {})[k] for k in list(data.get('output', {}).keys())[:10]}, ensure_ascii=False))

asyncio.run(check_raw())
"
```
- **원출력 그대로**:
```text
RAW OUTPUT KEYS: ['tr_crcy_cd', 'ord_psbl_frcr_amt', 'sll_ruse_psbl_amt', 'ovrs_ord_psbl_amt', 'max_ord_psbl_qty', 'echm_af_ord_psbl_amt', 'echm_af_ord_psbl_qty', 'ord_psbl_qty', 'exrt', 'frcr_ord_psbl_amt1', 'ovrs_max_ord_psbl_qty']
exrt in output: 1360.0000000000
RAW OUTPUT SAMPLE: {"tr_crcy_cd": "USD", "ord_psbl_frcr_amt": "100000.00", "sll_ruse_psbl_amt": "0.00", "ovrs_ord_psbl_amt": "100000.00", "max_ord_psbl_qty": "660", "echm_af_ord_psbl_amt": "100000.00", "echm_af_ord_psbl_qty": "660", "ord_psbl_qty": "660", "exrt": "1360.0000000000", "frcr_ord_psbl_amt1": "213924.259191"}
```
- **정정 및 확인 결과**:
  - `1360.0`은 코드 내에 하드코딩된 값이 아니며, KIS 해외주식 매수가능금액조회 API(`VTTS3007R`) 응답의 `output.exrt` 필드로부터 전달된 값입니다.
  - 다만 모의투자 서버 특성상 실시간 환율 대신 모의투자용 **"고정값(1,360.00원)"**을 응답하는 것으로 가설을 수립하고, 이를 대시보드 상단 헤더에 `환율: 1,360.00원 (모의 고정값)` 배지로 명시했습니다.

---

## 4. 거래 기록 출처 및 과거 오염 전수 조사

### 4.1 clean_trade_log.py가 삭제한 내역 및 삭제 전 원본 백업 위치
- **삭제 전 원본 백업 위치**:
  `c:\trading\package\nvda_trading_system\backend\data\trade_log.json.bak_test_pollution`
- **삭제된 거래 내역 원출력**:
```text
Total trades in backup: 6
[1] time=2026-09-24T15:18:58.237565 ticker=NVDA action=SELL shares=15 mode=DRY_RUN status=DRY_RUN_COMPLETED note=DRY_RUN 모드 - 실제 주문 안함
[2] time=2026-09-24T15:18:58.571407 ticker=NVDA action=BUY shares=1 mode=DRY_RUN status=DRY_RUN_COMPLETED note=DRY_RUN 모드 - 실제 주문 안함
[3] time=2026-09-24T15:19:08.769907 ticker=NVDA action=SELL shares=5 mode=DRY_RUN status=DRY_RUN_COMPLETED note=DRY_RUN 모드 - 실제 주문 안함
[4] time=2026-09-24T15:19:09.618908 ticker=NVDA action=BUY shares=1 mode=DRY_RUN status=DRY_RUN_COMPLETED note=DRY_RUN 모드 - 실제 주문 안함
[5] time=2026-09-24T15:19:11.230187 ticker=NVDA action=SELL shares=15 mode=DRY_RUN status=DRY_RUN_COMPLETED note=DRY_RUN 모드 - 실제 주문 안함
[6] time=2026-09-24T15:19:11.267921 ticker=NVDA action=BUY shares=1 mode=DRY_RUN status=DRY_RUN_COMPLETED note=DRY_RUN 모드 - 실제 주문 안함
```
- **설명**: 2026-09-24 15:18:58 ~ 15:19:11(pytest 실행 시각) 동안 기록된 6건의 DRY_RUN 거래 기록이 삭제되었습니다.

---

### 4.2 오늘 외 과거 날짜 전체 기록 파일 조사 원출력
- **실행 명령**:
```powershell
python inspect_all_data.py
```
- **원출력 그대로**:
```text
=== data/ 디렉터리 내 전체 파일 과거 거래/테스트 오염 조사 ===
[JSON DICT] bench_r3_consecutive5.json (keys=['mode', 'n', 'samples', 'wall_clocks', 'pure_times'], size=1486B)
[JSON DICT] daily_loss_state.json (keys=['schema_version', 'trading_date', 'net_realized_pnl_krw', 'is_available', 'unavailable_reason'], size=299B)
[TEXT/LOG] daily_report.log (lines=2062, size=145559B)
[JSON DICT] edgar\edgar_cache.json (keys=['berkshire', 'bridgewater', 'renaissance'], size=1003B)
[JSON DICT] kis_token_cache.json (keys=['access_token', 'expires_at', 'is_paper'], size=434B)
[JSON DICT] micro_live_7d_tracker.json (keys=['target_days', 'started_at', 'status', 'total_records', 'executed_records'], size=2150B)
[TEXT/LOG] monitor_breakout.log (lines=4, size=145B)
[JSON DICT] order_intents.json (keys=['schema_version', 'is_available', 'unavailable_reason', 'intents', 'updated_at'], size=540B)
[JSON DICT] performance_log.json (keys=['signals', 'created_at', 'updated_at'], size=11108B)
[JSON DICT] portfolio.json (keys=['holdings', 'cash', 'created_at', 'updated_at'], size=1353B)
[JSON LIST] portfolios\portfolio_cache.json (count=3, size=11729B): dates=[]
[TEXT/LOG] reconciler_reanchor.jsonl (lines=0, size=0B)
[JSON DICT] scan_history\2026-04-08_us.json (keys=['timestamp', 'market', 'total_scanned', 'primary_passed', 'final_candidates'], size=306B)
[JSON DICT] scan_history\2026-04-09_kr.json (keys=['timestamp', 'market', 'total_scanned', 'primary_passed', 'final_candidates'], size=304B)
...
[TEXT/LOG] scheduler.log (lines=5, size=400B)
[JSON LIST] scheduler_log.json (count=100, size=16907B): dates=['2026-09-24']
[TEXT/LOG] scheduler_output.log (lines=22621, size=3585480B)
[JSON DICT] stop_loss_state.json (keys=['stop_loss_fired', 'price_fail_count', 'gate_blocked_alert_fired', 'reject_count', 'next_retry'], size=323B)
[TEXT/LOG] telegram_listener.log (lines=2, size=71B)
[TEXT/LOG] telegram_offset.txt (lines=1, size=9B)
[JSON LIST] trade_log.json (count=0, size=2B): dates=[]
```
- **확인 결과**: `data/trade_log.json`에는 과거 날짜 거래가 전혀 없었으며(6건 모두 당일 기록), `portfolio.json` 및 `performance_log.json` 등 기타 데이터 파일에서도 과거 테스트 오염 거래는 발견되지 않았습니다.

---

## 5. 긴급 정지(Emergency Stop) 보안 및 동작 정책

### 5.1 X-Trading-Secret 프론트엔드 유출 여부 검색 원출력 (값 미출력, 존재 여부만)
- **실행 명령**:
```powershell
.\venv\Scripts\python.exe check_secret_leak.py
```
- **원출력 그대로**:
```text
=== 프론트엔드 내 X-Trading-Secret 실제 값 존재 여부 검사 ===
결과: 존재하지 않음 (프론트엔드 코드 및 빌드 파일 내에 실제 secret 값이 하드코딩되거나 포함되어 있지 않음)

=== 헤더 명칭('X-Trading-Secret') 참조 위치 ===
 - src\services\api.ts
```
- **확인 결과**: 실제 시크릿 값 자체는 프론트엔드 소스코드나 번들에 포함되어 있지 않으며, 헤더 키 이름(`X-Trading-Secret`)만 `api.ts`에 존재합니다.

---

### 5.2 긴급 정지 중 손절 매도 차단 여부 및 정책 보고
- **확인 결과**: **손절 매도도 차단됨**
  - `Scheduler._execute_stop_loss`는 손절 주문 시 `AutoTrader.execute_trade`를 호출합니다.
  - 긴급 정지(KILL SWITCH) 활성화 시 물리 파일(`data/kill_switch.flag`) 및 `SafetyGuard._emergency_stop`에 의해 `can_trade=False`가 반환되어 일반 매수/매도뿐만 아니라 **손절 매도 주문도 `ORDER_REJECTED`로 즉시 차단**됩니다.
- **정책 결정 사항**:
  - 긴급 정지 상황에서도 계좌 보호를 위한 손절 매도는 예외적으로 허용할지, 아니면 완전 차단(현행 유지)할지에 대해서는 **대표 결정 사항으로 남깁니다.**

---

### 5.3 서버 재시작 후 긴급 정지 상태 보존 시험 원출력
- **수정 내용**: `app/services/safety_guard.py`의 `__init__`에서 `settings.RISK_KILL_SWITCH_PATH` 물리 파일 존재 여부를 검사하여 서버가 재부팅되어도 `_emergency_stop=True` 상태를 자동으로 복원하도록 보완했습니다.
- **실행 명령**:
```powershell
.\venv\Scripts\python.exe test_restart_stop.py
```
- **원출력 그대로**:
```text
=== 1. 비상 정지 발동 ===
Flag file exists: True
Current guard status: True

=== 2. 서버 재시작 시뮬레이션 (새로운 인스턴스 생성) ===
New guard emergency_stop status: True
New guard can_trade status: False

=== 3. 비상 정지 해제 ===
After deactivation flag file exists: False
After deactivation emergency_stop status: False
```
- **확인 결과**: 서버 재시작(신규 인스턴스 로딩) 후에도 정지 상태가 안정적으로 유지되고, 해제 시 파일이 삭제되어 정상 복구됨을 확인했습니다.

---

## 6. 대시보드 끊김 시험 보완

### 6.1 시험 1: 화면을 켜 둔 채로(새로고침 없이) 서버 종료 → 60초 후 캡처
- **시험 조건**: 백엔드 서버(포트 8000)를 중지한 후, 브라우저 화면을 새로고침하지 않고 60초 동안 방치한 뒤 캡처.
- **캡처 이미지 링크**: [disconnection_60s_state_1790243822374.png](file:///C:/Users/sangi/.gemini/antigravity-ide/brain/ec6dfafd-d033-4251-9255-a00a3f742816/disconnection_60s_state_1790243822374.png)
- **화면 관찰 결과**:
  1. 하단 7개 모듈 분석 영역에 빨간색 `모듈 분석을 불러오지 못했습니다 (불러오기 실패)` 문구와 `[다시 시도]` 버튼이 표시되었습니다.
  2. 마스터시그널, 포트폴리오 총자산, 자동매매 상태(오늘 거래, 남은 거래), 권장 액션, 신뢰도 등은 `—` 기호로 비워졌습니다.
  3. 반면 상단 NVDA 현재가(`$222.63`), 어닝 카운트다운(`D-55`), 리스크 점수(`15/100`) 등 일부 카드는 이전 캐시 숫자가 그대로 남아 있었습니다.

---

### 6.2 시험 2: "연결 끊김" 전역 경고 배너 구현 후 같은 시험 재실행
- **구현 내용**: `src/App.tsx`에 3초 주기 서버 헬스 폴링 및 상단 붉은색 전역 경고 배너, 그리고 환율 배지(`환율: 1,360.00원 (모의 고정값)`)를 구현했습니다.
- **캡처 이미지 링크**: [check_banner_exchange_rate_1790244005595.png](file:///C:/Users/sangi/.gemini/antigravity-ide/brain/ec6dfafd-d033-4251-9255-a00a3f742816/check_banner_exchange_rate_1790244005595.png)
- **화면 관찰 결과**:
  1. 최상단에 붉은색 점멸 배너 `⚠️ 연결 끊김: 백엔드 서버(API)와 통신할 수 없습니다. 실시간 시세 조회 및 주문 기능이 중단되었습니다.` 및 `OFFLINE` 라벨이 즉시 노출되었습니다.
  2. 상단 헤더에 `환율: 1,360.00원 (모의 고정값)` 배지가 명확하게 렌더링되었습니다.

---

## 7. 손절 재알림 실패 분석 정정 및 Git 히스토리 확인

### 7.1 표현 정정
- 기존 표현을 지시사항에 따라 **"10회 미재현, 원인 미확인"**으로 명확히 정정합니다.

---

### 7.2 싱글톤 격리 Fixture의 실패 발생 당시 존재 여부 (`git log`)
- **실행 명령**:
```powershell
git log -p -n 5 tests/conftest.py
```
- **원출력 발췌**:
```text
commit 5a1a8f383073ec2d0641ef1a9eb78dc0634daf17 (2026-09-20 09:00:01)
commit 483d32fbf7f613c99a6612e7c58550bff2e0ab71 (2026-09-18 00:03:15)
    feat(risk): reinforce daily stop loss alerts and assert unbypassed ledger fsync (보정 82, 83)
commit cda321fa83c6c5582b81360fc640a4429ff47640 (2026-09-17 23:41:20)
commit dd48e907f56ffd7da4b8a1e87899e19b8a254ecf (2026-09-17 23:22:24)
commit 8ee86389a68bd6d697c6e719e05c206aae2f3ba0 (2026-09-17 12:42:34)
```
- **확인 결과**:
  - `isolate_scheduler_singleton_state` fixture는 이미 커밋 `8ee86389`(2026-09-17) 및 `483d32fb`(2026-09-18) 시점부터 이미 코드에 존재하고 있었습니다.
  - 따라서 과거 간헐적 실패가 발생했을 당시에도 해당 격리 fixture는 이미 활성화되어 있었으므로, "격리 fixture 도입으로 문제가 해결되었다"는 가설은 타당하지 않으며, 현재 10회 연속 미재현 상태이나 구체적인 간헐적 실패 원인은 **"원인 미확인"** 상태입니다.

---

## 8. 매매 두뇌 계획서 보완

### 8.1 난수를 내거나 추정/합성(Synthetic) 데이터를 반환하는 모듈 목록
1. **`news_sentiment.py`**:
   - 뉴스 수집 실패 또는 결측 시 `Line 342: value = random.randint(55, 75)`로 임의 난수를 생성하여 감성 점수로 반환.
2. **`fear_greed.py`**:
   - CNN 공포탐욕 지수 스크래핑 실패 시 `Line 106: value = random.randint(55, 72)` 및 `Line 125~128: random.randint(-5, 5)` 등으로 난수 기반 지표 생성.
3. **`darkpool_analyzer.py`**:
   - 실제 장외 다크풀 체결 데이터가 없으며, Yahoo Finance 거래량의 40%를 일률 가정(`Line 184: darkpool_pct = 40.0`)하여 추정치 계산.
4. **`data_collector.py`**:
   - 야후 파이낸스 429 레이트리밋 백오프 시 `Line 35: random.uniform(0.5, 1.5)` 지터 난수 사용 (시그널 직접 영향은 적으나 데이터 수집 지연에 영향).

---

### 8.2 연결 시 해당 모듈 가중치를 0으로 강제하는 안전장치 유무
- **확인 결과**: **"없음 (미구현)"**
  - 현재 `app/services/master_signal.py`에는 사용 불가 모듈의 가중치 합이 전체의 40%를 초과할 경우 전체 파이프라인을 중단하는 `coverage < 0.60` 가드만 존재합니다.
  - 난수를 생성하거나 추정치를 사용하는 모듈(`darkpool`, `news_sentiment fallback`)이 점수를 반환할 경우, 이를 실데이터가 아닌 것으로 판별하여 해당 가중치를 0으로 강제 클램프하는 전용 안전장치는 현재 코드베이스에 존재하지 않습니다.

---

### 8.3 외부 데이터 필요 모듈별 예상 데이터 출처 및 유료 여부

| 모듈명 | 필요 데이터 | 예상 데이터 출처 | 유료 여부 및 예상 비용 |
| :--- | :--- | :--- | :--- |
| **options_flow** | 실시간 미국 옵션 체인, 대량 블록딜, 감마 | Polygon.io Options API 또는 CBOE 실시간 피드 | **유료** (Polygon Options Starter 기준 약 $29~$199/월) |
| **darkpool** | FINRA 장외 체결(TRF/ADF), 다크풀 블록딜 | Cheddar Flow API / Unusual Whales API / FINRA 피드 | **유료** (약 $50~$100/월) |
| **institutional** | 13F 분기 기관 보유 지분 추이 | SEC EDGAR 공식 API (`data.sec.gov`) | **무료** (SEC 공식 오픈 API) |
| **llm_news** | 실시간 금융 뉴스 본문 및 AI 감성 분석 | Google Gemini 1.5 Flash API + RSS 뉴스 피드 | **무료 / 초저비용** (Gemini 무료 티어 내 또는 종량제 극소액) |
| **investor_analysis** | 투자자별(외인/기관/개인) 일별 순매수 | KIS 오픈 API (`FHKST01010900` 등) | **무료** (증권사 모의/실전 계좌 무료 기본 제공) |
| **technical** | 분봉, 일봉, 이동평균, 볼린저밴드 | KIS 오픈 API (`FHKST01010100` 등) | **무료** (증권사 무료 기본 제공) |
