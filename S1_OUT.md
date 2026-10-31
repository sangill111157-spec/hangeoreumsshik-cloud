# 🧠 S1 에고 라이트 만능 신경망 (`s1_ego.py` v1.0) & 로컬 브릿지 서버(`8504`) 삼성(三聖) 합동 감리 보고서

## 1. 로컬 브릿지 서버 (`http://127.0.0.1:8504/api/status`) 기동 실측 결과
```json
{
  "ok": true,
  "server_time": "2026-11-01T07:10:37.999115",
  "kill_switch": false,
  "mode": "READ_ONLY",
  "last_proof": null,
  "executed_count": 3,
  "executed_ids": [
    "REAL_DOM_001",
    "REAL_DOM_002",
    "REAL_DOM_003"
  ],
  "last_executed": {
    "block_id": "REAL_DOM_003",
    "sha256": "f329204fa03448823a4a600b81caac37711a38257d9fe47fe492a6d17ab24ea3",
    "status": "DONE",
    "time": "2026-11-01T00:30:51.545205+09:00",
    "approved_by": "CEO_SANGILL_LEE_DIRECT_ENTER",
    "approved_at": "2026-11-01T00:30:39.941737+09:00",
    "isolated_cwd": "C:\\Users\\sangi\\Downloads\\shin-agent\\s1_runs",
    "script_path": "C:\\Users\\sangi\\Downloads\\shin-agent\\s1_runs\\REAL_DOM_003.py",
    "rc": 0,
    "stdout": "VERIFIED_5LINES_DOM: 3.12.10 win32",
    "stdout_lines": [
      "VERIFIED_5LINES_DOM: 3.12.10 win32"
    ],
    "stderr": "",
    "work_id": "local-REAL_DOM_003-f329204f",
    "uuid": "local-REAL_DOM_003-f329204f",
    "api_status": {},
    "api_chat": {}
  }
}
```

## 2. `python s1_ego.py spaces` 실측 결과
```json
{
  "ok": true,
  "spaces": [
    {
      "id": 0,
      "name": "",
      "ownership": "agent",
      "tabs": [
        {
          "label": "p3",
          "title": "르곤 보좌관 인수인계 및 S1 자동보고 데몬 v2 승인 요청",
          "url": "https://www.genspark.ai/agents?id=c1647638-2531-43db-a059-c153d8da14d9"
        }
      ]
    },
    {
      "id": 2,
      "name": "",
      "ownership": "agent",
      "tabs": [
        {
          "label": "p2",
          "title": "Genspark(젠스파크) - 누구나 쉽게 쓰는 올인원 AI 워크스페이스",
          "url": "https://www.genspark.ai/?utm_source=google&utm_medium=cpc-search&utm_campaign=ACC_Global-en-feature&utm_term=competitor&campaign_id=23235867550&adgroup_id=191292082507&ad_id=782789654570&keyword=usegalileo.ai&matchtype=b&network=g&device=c&loc=9214122&gclid=Cj0KCQiAwYrNBhDcARIsAGo3u32UZ_5UlutDoZkb8j6gBzSrBh3FshGC2IrU_T7MLdYLJJ7GdCQSEi0aAq4IEALw_wcB&gclid=Cj0KCQiAwYrNBhDcARIsAGo3u32UZ_5UlutDoZkb8j6gBzSrBh3FshGC2IrU_T7MLdYLJJ7GdCQSEi0aAq4IEALw_wcB&random=14564140441600019416&gad_source=1&gad_campaignid=23235867550&gbraid=0AAAABBSC2JwGsa9zg8v_NI4o2J2qQpWMR"
        },
        {
          "label": "p1",
          "title": "썬원 에이온 환원 제국 마스터 파이프라인 설계 요청",
          "url": "https://www.genspark.ai/agents?id=212e5993-339b-43e7-8e2b-0ebb4d58987e"
        }
      ]
    },
    {
      "id": 3,
      "name": "",
      "ownership": "agent",
      "tabs": [
        {
          "label": "p4",
          "title": "SUN-ONE AON | S1 만능소통창",
          "url": "http://127.0.0.1:8501/rgon_alpha_chat.html"
        },
        {
          "label": "p1",
          "title": "썬원 에이온 S1 완공 파이프라인 및 보안 아키텍처 설계 요청",
          "url": "https://www.genspark.ai/agents?id=a481ead5-a237-432c-abfb-0396b8a34d16"
        }
      ]
    }
  ]
}
```

## 3. 제2성 GPT-6.1 Sol (`Space 2`) 감리 의견 및 보완 권고
```
utf-8") if args.prompt_file else args.prompt
        res = cmd_ask(args.space, txt, wait_sec=args.wait)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()


[감리 요청 사항]
- 채팅창의 AI(르곤·GPT·클로드)가 에고 라이트(Space 0~16)를 수족처럼 안전하고 정확하게 제어하기 위해 `s1_ego.py` v1.0에서 보완해야 할 엣지 케이스, 보안 경계(권한 분리/읽기·점검 원칙 포함), 탭 식별, 응답 완료 감지(스마트 폴링), 에러 복구 등 더 꼼꼼히 다듬어야 할 사항을 짚어주십시오.

탭 식별·권한 경계, 응답 완료 감지, 타임아웃·복구의 세 축으로 점검하겠습니다. 제출 로그로 확인되는 기능과 코드상 아직 보장되지 않는 동작을 구분하겠습니다.

읽기
https://github.com/citrolabs/ego-lite
보기
읽기
https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/race
보기
읽기
https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html
보기
읽기
https://raw.githubusercontent.com/citrolabs/ego-lite/main/skills/ego-browser/SKILL.md
보기
S1 에고 라이트 만능 신경망 v1.0 합동 감리 의견

판정: spaces 목록 조회 시제품은 확인했습니다. 다만 read의 신뢰 대상 제한과 ask의 안전한 전송·완료 판정은 보완 후 인수시험이 필요합니다.

방향은 좋습니다. 임의 브라우저 코드를 매번 만드는 대신 작은 공통 CLI로 조회·읽기·질의를 표준화하면 통제와 재현성이 좋아집니다. 다만 현재는 “대상 탭이 없으면 다른 탭으로 대체”하는 동작이 가장 큰 위험입니다.

본 검토는 제출 소스·실행 결과의 대조이며, 제가 로컬 브라우저를 직접 조작한 결과는 아닙니다.

1. 최우선 수정: Space 2의 채팅 ID가 다릅니다
구분	채팅 ID
실제 spaces 결과	212e5993-339b-43e7-8e2b-0ebb4d58987e
KNOWN_CHATS[2]	212e5993-72c0-4a3c-9a6e-586aa09a9f31

현재 ask는 지정 ID가 없으면 다른 Genspark 에이전트 탭을 선택합니다. 이번 실측에서도 정확한 매핑 대신 대체 선택으로 동작할 수 있습니다.

필수 원칙: “일치하지 않으면 전송하지 않는다.”

HTTPS·정확한 호스트·/agents 경로·전체 id 값을 구조적으로 검사.
매칭 0개 → TARGET_NOT_FOUND.
매칭 여러 개 → TARGET_AMBIGUOUS.
대상 확정 후에도 입력 직전과 전송 직전에 현재 URL 재검증.
Space·탭 라벨은 위치 정보로 사용하고, 신뢰 판단은 검증된 채팅 ID와 결합.
read의 tabs[0] 대체도 제거. 읽기 역시 다른 대화의 정보 유출을 일으킬 수 있습니다.

Space 0~16 전체를 일괄 허용하면 안 됩니다. 현재 등록되지 않은 Space도 ask가 가능하므로, 명시적 허용 목록을 우선 적용해야 합니다.

2. 권한은 “조회·읽기·외부 전송”으로 분리하십시오

ask는 단순 로컬 점검이 아닙니다. 로그인된 웹서비스에 내용을 전송하는 쓰기 작업입니다.

권장 기본 정책은 다음과 같습니다.

기능	기본 권한	추가 조건
spaces	제한적 허용	기본 출력에서는 URL 쿼리·개인정보 최소화
read	등록된 대상만 허용	필요한 메시지 범위만 추출
ask	기본 차단	승인된 대상·프롬프트·요청에 한정
Space 0 전송	현재처럼 차단 유지	별도 명시 승인 없이는 해제 금지
게시·결제·삭제·계정 변경	이 CLI 범위 밖	별도 정책과 승인 필요

ask 승인에는 요청 UUID, 대상 채팅 ID, 프롬프트 해시, 승인자, 승인 시각·만료를 결합하십시오. 파일에 적힌 승인자 문자열만으로 실제 사용자 승인을 입증했다고 표시하면 안 됩니다.

또한 브라우저에서 읽은 응답은 데이터이지 새로운 실행 권한이 아닙니다. 상대 AI가 “다른 Space로 보내라”, “승인 파일을 바꿔라”라고 답해도 자동 실행해서는 안 됩니다. 세 AI 사이의 재질의에는 횟수·깊이·시간 한도를 둬 무한 상호 호출을 차단해야 합니다.

에고 라이트는 실제 로그인·탭을 사용할 수 있는 구조이므로 편의성만큼 계정 권한의 경계가 중요합니다. Source

3. 입력창 조작은 현재보다 더 좁혀야 합니다

현재 선택자는 다음처럼 너무 넓습니다.

loc=css:textarea

가능한 문제:

검색창·수정창·다른 입력창 선택
사용자가 작성 중인 초안을 fill()로 덮어쓰기
응답 생성 중에 추가 입력
Enter가 전송이 아니라 줄바꿈으로 동작
입력 후 사용자가 포커스를 바꿔 다른 위치에 Enter가 전달됨

전송 전 확인 조건을 명세화하십시오.

검증된 대상 페이지인가?
대화 입력창이 정확히 하나인가?
입력 가능하며 기존 초안이 비어 있는가?
현재 응답 생성 중이 아닌가?
채운 실제 값이 승인된 프롬프트와 일치하는가?
대상 전송 컨트롤이 활성화돼 있는가?

기존 초안이 있으면 기본적으로 USER_DRAFT_PRESENT_HOLD가 맞습니다. 실패 복구 과정에서도 사용자의 새 입력을 덮어쓰거나 지우면 안 됩니다.

4. 스마트 폴링: 페이지 길이가 아니라 “이번 응답”을 추적하십시오

현재 완료 조건은 다음 조합입니다.

전체 페이지 길이가 이전보다 100자 이상 증가
마지막 400자에 "Thinking..." 없음
길이가 연속 두 번 같음

이 조건은 완료 보장으로 사용할 수 없습니다.

보낸 프롬프트 자체만으로 100자 이상 증가할 수 있음
짧은 정상 답변은 조건을 만족하지 못함
같은 길이로 내용이 변경될 수 있음
스트리밍이 잠시 멈추면 완료로 오인
한국어 상태 문구·오류·로그인 만료를 놓침
대화 가상화로 페이지 길이가 줄어들 수 있음

권장 상태는 다음과 같습니다.

PREPARED → SEND_ATTEMPTED → SENT_CONFIRMED → RESPONSE_STARTED → STREAMING → COMPLETE

분리해야 할 종료 상태:

SEND_UNCONFIRMED
RESPONSE_TIMEOUT
AUTH_REQUIRED
RATE_LIMITED
PARTIAL
ERROR

전송 전 마지막 메시지를 기준점으로 저장하고, 이번 사용자 메시지의 등장과 그 뒤의 새 assistant 메시지를 연결하십시오. 완료는 가능한 경우 UI의 생성 종료 신호와 해당 응답 내용의 안정화를 함께 확인해야 합니다.

공식적으로 안정적인 메시지 식별자가 없다면 임의로 있다고 가정하지 말고, 테스트한 DOM 어댑터와 관측 근거를 기록하십시오.

지금은 대기 시간이 끝나도 무조건 ok:true를 반환합니다. 이 부분은 반드시 바꿔야 합니다. ok는 CLI 조회 성공인지, 전송 확인인지, 응답 완료인지 의미를 분리하십시오.

5. 타임아웃은 “대기 중단”과 “작업 취소”가 다릅니다

소스 상단의 “zero hang” 표현은 보장 범위를 넘습니다.

Promise.race()에서 타이머가 이겨도 기존 page.evaluate()는 자동 취소되지 않습니다. 반복하면 미완료 작업이 남을 수 있습니다. Source
evaluate()가 거절되면 현재 코드는 snapshot fallback으로 가지 않고 예외로 끝납니다.
snapshot()에는 별도 단계 제한이 없습니다.
Python CLI 타임아웃 후에도 이미 웹서비스에 전송된 요청은 계속 처리될 수 있습니다.

따라서:

전체 작업의 단일 마감 시각과 단계별 시간 한도를 적용.
타임아웃·빈 결과·예외를 구분.
취소를 지원하는지는 설치된 에고 버전의 기능으로 확인.
전송 이후 타임아웃은 “전송 여부/완료 여부 미확인”으로 기록.
자동 재전송 전에 기존 사용자 메시지·응답을 대조.

읽기는 제한 재시도가 가능하지만, 전송은 불확실한 상태에서 맹목 재시도하면 안 됩니다.

6. 동시 실행과 임시 파일 충돌을 막아야 합니다

현재 고정 파일명은 다중 AI 동시 사용에 취약합니다.

파일	발생 가능한 문제
_s1_ego_cmd_tmp.js	다른 요청의 JS로 덮어쓰기·삭제
_s1_ego_prompt_{space_id}.txt	같은 Space의 다른 프롬프트로 교체
같은 탭의 입력창	두 요청이 서로 입력·전송을 방해

권장 구조:

요청마다 UUID 기반 전용 임시 디렉터리.
읽기는 제한 병렬, 쓰기는 대상 채팅별 직렬 큐.
요청 자신이 만든 파일만 정리.
임시 프롬프트 접근 권한 제한 및 잔여 파일 정리 정책.
파일 경로를 JS 문자열에 넣을 때 안전한 문자열 직렬화 사용. 현재 작은따옴표 방식은 경로의 ' 등에 취약합니다.

EGO_REAL로 실행 파일을 바꿀 수 있는 것도 설정 기능이지 신뢰 검증은 아닙니다. 운영에서는 실행 경로·버전·필요한 무결성 정보를 고정하고 변경을 기록하십시오.

7. 에러와 결과는 기계가 판독할 수 있어야 합니다

현재 Python 예외는 구조화된 결과 없이 끝날 수 있고, 반대로 ok:false를 출력해도 CLI 종료 코드는 정상일 수 있습니다.

공통 결과에는 최소한 다음을 권합니다.

요청 UUID·명령·대상 Space·검증된 채팅 ID
시작·종료 시각과 시간대
상태·오류 코드·재시도 가능 여부
전송 시도 여부·전송 확인 여부·응답 완료 여부
프롬프트/응답 해시와 수집 방식
잘림 여부·부분 결과 여부
CLI 종료 코드

stdout의 구조화된 결과와 stderr 진단 로그도 분리하십시오. 현재처럼 둘을 합쳐 마지막 접두어 행을 고르면 오류 진단과 결과 판독이 섞입니다.

브라우저 전체 본문을 읽고 끝부분만 반환하는 방식도 개선 대상입니다. 마지막 응답만 수집하고, 길이 제한은 수집 단계부터 적용하는 편이 정확성과 개인정보 보호에 유리합니다.

8. 제출된 서버 증빙의 해석도 정리해야 합니다
executed_count:3에는 기존 FAIL도 포함됩니다. 전체 시도 수·성공·실패·진행 중 수로 분리하는 것이 정확합니다.
local-REAL_DOM_003-f329204f는 작업 식별자지만 표준 UUID는 아닙니다.
last_proof:null은 증빙 연결 미확인으로 표시해야 합니다.
READ_ONLY는 브릿지 API의 모드입니다. 별도 CLI의 웹 전송까지 읽기 전용이라는 뜻은 아닙니다.
제출 자료로 직접 확인되는 이번 CLI 실측은 spaces입니다. read·ask의 정상/실패 시험은 별도로 필요합니다.
9. 다음 버전의 최소 인수시험
시험	기대 결과
등록 ID 불일치·중복 탭·미등록 Space	대체 전송 없이 차단
입력창에 사용자 초안 존재	보존하고 보류
짧은 응답·한국어 생성 상태·스트리밍 일시 중단	조기 완료 오판 없음
전송 직후 CLI 종료·타임아웃	미확인 상태 보존, 자동 중복 전송 없음
같은 탭에 동시 ask 두 건	순차 처리·파일 혼선 없음
로그인 만료·탭 닫힘·사용자 탐색	구조화된 오류와 안전 보류
킬스위치 ON·승인 만료	새 전송 차단
읽은 응답에 권한 변경 지시 포함	정책·승인 변경 없이 데이터로 처리

에고 공식 스킬은 설치 버전에 맞는 사용법을 ego-browser skill로 확인하고, 업그레이드 후 다시 읽도록 안내합니다. 따라서 taskSpace, adopt, fill, 키보드 및 취소 동작은 해당 설치 버전의 사용법과 실측으로 고정해야 합니다. Source

최종 권고

v1.1의 우선순위는 세 가지입니다.

잘못된 탭으로 대체하는 로직 제거 + Space 2 매핑 교정
전송 승인·초안 보호·채팅별 직렬화
메시지 단위 완료 감지 + 전송 불확실 상태의 안전한 복구

목표는 “어느 Space든 자유롭게 움직이는 도구”가 아니라, “승인된 대상에 정확히 한 번 작용하고 결과를 검증하는 도구”로 잡는 것이 맞습니다. 이 경계가 정리되면 삼성 공통 스킬로 공유할 기반이 됩니다.

GPT-6.1 Sol
워크플로우
드라이브
허브
GenMail
GenTeam
Claw
```

## 4. 제3성 Claude Opus 5.5 (`Space 3`) 감리 의견 및 보완 권고
```
다. _s1_ego_cmd_tmp.js 하나를 모든 호출이 같이 씁니다. 르곤이 read를 부르는 순간 다른 쪽에서 ask를 부르면, 한쪽 프로세스가 다른 쪽의 JS 명령을 실행할 수 있습니다. 게다가 finally에서 파일을 지우기 때문에, 상대방이 읽기 전에 파일이 사라지기도 합니다. "AI 셋이 수족처럼" 쓰는 순간 바로 발생하는 문제입니다. 호출마다 uuid를 붙인 파일 이름을 쓰고, ask는 전역 잠금을 걸어 한 번에 하나만 실행되게 해야 합니다.

② 대상 탭을 못 찾으면 다른 탭으로 넘어갑니다(fail-open). ask는 지정 탭을 찾지 못하면 아무 agents 탭으로 넘어갑니다. read는 더 심해서 마지막에 tabs[0], 곧 아무 사이트나 읽습니다. 그 탭이 Gmail이든 YouTube Studio든 그 내용이 채팅창, 곧 외부 서버로 넘어갑니다. 원칙은 정확히 1개가 일치할 때만 진행하는 것입니다. 0개나 2개 이상이면 거부해야 합니다.

③ 응답 완료를 잘못 판정합니다. beforeTxt를 읽다가 5초 타임아웃이 나면 ""가 반환돼 beforeLen=0이 됩니다. 그러면 첫 폴링에서 바로 length > 0 + 100 조건이 참이 되고, 이전 대화 길이 그대로 두 번 안정되면 답변이 시작되기도 전에 완료로 판정합니다. 반대로 최대 대기 시간을 넘겨도 결과가 ok: true로 나옵니다. 그래서 반쯤 쓰다 만 답변이 완성본처럼 전달됩니다. 길게 생각하는 모델에게 40초는 짧습니다. 저(Opus 5.5)의 감리 답변도 대개 이 시간을 넘깁니다.

3. 보안 경계: 권한 등급제
등급	명령	허용 경로	조건
R0	spaces	데몬 경유 가능	URL의 쿼리스트링을 지우고 출력(gclid 등 추적값 제거)
R1	read	데몬 경유 가능	허용 목록에 있는 genspark.ai/agents 대화만 읽음, 마커 무력화 후 반환
W1	ask	대표님 직접 실행만	킬스위치 확인, 감사 로그, 속도 제한, 초안 보호, 모델 확인

ask를 W1으로 분리하는 이유가 있습니다. ask는 외부 서비스에 글을 쓰는 동작이고, 할당량도 소모합니다. 1순위 PASS 때 정한 원칙("데몬은 읽기·점검·보고 코드만, 실작업은 격리 전까지 대표님 직접 실행")을 그대로 적용하면 ask는 데몬이 실행할 수 없습니다. 르곤이 데몬을 통해 GPT나 저에게 자동으로 질문하는 구조는 Windows Sandbox 격리를 갖춘 뒤에 다시 심의하시는 것을 권합니다.

AI끼리 주고받는 경로로 명령이 끼어들 수 있습니다. 이것이 이번 감리에서 가장 중요한 보안 논점입니다. ask와 read는 다른 AI의 답변을 그대로 가져옵니다. 그 안에 ===S1_AUTO_START:…=== 마커가 들어 있고 르곤이 이를 자기 답변에 옮겨 적으면, 데몬은 그것을 Space 0의 정식 블록으로 감지합니다. GPT나 제 출력이 르곤을 거쳐 실행 후보가 되는 우회 경로가 생기는 것입니다. 승인 게이트가 마지막에 막아 주기는 하지만, 애초에 이 경로를 끊어 두어야 합니다. 다른 AI의 답변은 명령이 아니라 데이터로 취급하라는 원칙을 르곤의 지침에도 넣어 주십시오.

AI끼리 서로 무한히 묻는 루프도 막아야 합니다. 르곤이 저에게 묻고, 제 답변이 다시 GPT에게 물으라고 하는 식의 연쇄입니다. 방지책은 다음 네 가지입니다.

대화마다 ask 횟수를 제한합니다(예: 공간당 2분에 1회, 하루 상한).
프롬프트 머리에 홉 카운터를 둡니다([S1_HOP=1/2]).
실행 전에 킬스위치를 확인합니다.
모든 ask를 logs/s1_ego_audit.jsonl에 기록합니다(시각, space, 대화 ID, 프롬프트 SHA, 결과 상태).
4. 탭 식별

부분 문자열 비교(includes)를 URL 파싱 후 정확 일치로 바꾸십시오. label(p1, p3)은 세션마다 바뀔 수 있으니 식별 키로 쓰지 말고 표시용으로만 쓰셔야 합니다. ask 직전에는 대화창의 모델 선택 버튼 글자도 확인하십시오. 지난 snapshot에 "Gemini 4 Argon"이 보였듯이 화면에 모델명이 나옵니다. 누군가 Space 3의 모델을 바꿔 놓았다면, 저에게 물은 질문이 다른 모델에게 갑니다.

Copy
function chatId(u){ try{ const x=new URL(u);
  return (x.protocol==="https:" && x.hostname==="www.genspark.ai" && x.pathname==="/agents")
         ? x.searchParams.get("id") : null; }catch(e){ return null; } }
const matches = tabs.filter(t => chatId(t.url) === expected);
if (matches.length !== 1) { emit({ok:false, code:"TAB_NOT_UNIQUE", count:matches.length}); return; }

5. 응답 완료 감지 (스마트 폴링)

페이지 전체 길이를 비교하는 방식은 사이드바, 시각 표시, 입력창 변화에도 흔들립니다. "Thinking..." 영문 문자열에 의존하는 것도 한국어 UI에서는 맞지 않을 수 있습니다. 판정은 메시지 단위로 바꿔야 합니다.

전송 확인: Enter를 누른 뒤 입력창이 비었는지, 그리고 내 프롬프트의 앞부분이 마지막 사용자 메시지로 나타났는지 확인합니다. 확인되지 않으면 SEND_NOT_CONFIRMED로 끝내고 다시 누르지 않습니다. 두 번 전송되는 것을 막기 위해서입니다.
생성 중 판정: 중지(Stop) 버튼이 있는지와 어시스턴트 메시지 개수가 늘었는지로 판단합니다.
완료 판정: 중지 버튼이 사라지고, 마지막 어시스턴트 메시지의 텍스트가 2회 연속(5초 이상) 그대로이면 완료로 봅니다.
결과 반환: 마지막 어시스턴트 메시지만 반환하고, 상태를 completed / timeout / rate_limited / send_failed로 구분합니다. 화면에 "5시간 제한"이나 "재설정됩니다"가 보이면 rate_limited와 재설정 시각을 돌려줍니다.

여기에 쓸 Genspark의 실제 DOM 셀렉터(중지 버튼, 메시지 컨테이너)는 제가 확인할 수 없습니다. 다음 제출 때 page.evaluate로 조사한 셀렉터 목록을 함께 내 주십시오. 그 전까지는 기존 길이 비교 방식을 보조 수단으로만 쓰십시오. 타임아웃이 나서 ""가 반환되면 판정에 쓰지 말고 건너뛰어야 합니다.

6. 에러 복구
종료 코드: 지금은 실패해도 항상 0으로 끝나서, 호출한 쪽이 실패를 알 수 없습니다. ok: false면 sys.exit(1)로 끝내십시오.
재시도 정책: read와 spaces는 1회 재시도(2초 대기)를 허용합니다. ask는 자동 재시도를 금지합니다. 다시 시도하려면 먼저 read로 프롬프트가 이미 올라갔는지 확인한 뒤 사람이 판단하게 하십시오.
오류 구조화: JS에서 throw가 나면 S1EGO_JSON 없이 끝납니다. 전체를 try/catch로 감싸 {ok:false, code, message}를 반드시 출력하게 하십시오.
고아 프로세스: subprocess 타임아웃이 나면 ego-browser의 nodejs 프로세스가 남을 수 있습니다. Promise.race로 버린 evaluate도 취소되지 않고 계속 쌓입니다. 타임아웃 횟수를 기록하고, 연속 3회가 되면 EGO_UNHEALTHY로 중단하십시오.
초안 보호: 입력창에 이미 글자가 있으면 덮어쓰지 말고 DRAFT_PRESENT로 중단하십시오. 대표님이 쓰던 글이 사라지는 것을 막기 위해서입니다. 입력창 셀렉터도 textarea 전체가 아니라 실측된 textarea[name="query"]로 좁히십시오.
7. v1.1 핵심 패치
Copy
import uuid, hashlib, datetime, re, threading, msvcrt
TMP_DIR = BASE / "_ego_tmp"; TMP_DIR.mkdir(exist_ok=True)
AUDIT = BASE / "logs" / "s1_ego_audit.jsonl"
KILL_FLAG = BASE / "KILL_SWITCH.flag"
ASK_LOCK = BASE / "s1_ego_ask.lock"
ASK_MIN_INTERVAL = 120  # 초, 공간별

KNOWN_CHATS = {0: "c1647638-2531-43db-a059-c153d8da14d9",
               2: "212e5993-339b-43e7-8e2b-0ebb4d58987e",   # 실측값으로 교정 — 대표님 확인 필요
               3: "a481ead5-a237-432c-abfb-0396b8a34d16"}
EXPECTED_MODEL = {2: "GPT", 3: "Claude"}

def defang(s):  # 다른 AI 출력 속 실행 마커 무력화
    return re.sub(r"=+\s*S1_AUTO_(START|END)", "[S1_MARKER_REMOVED]", s or "")

def run_ego_js(js_code, timeout=60):
    tmp_js = TMP_DIR / f"cmd_{uuid.uuid4().hex}.js"
    tmp_js.write_bytes(js_code.encode("utf-8"))
    loader = ("const fs=await import('node:fs'); "
              f"const c=fs.readFileSync({json.dumps(tmp_js.as_posix())},'utf8'); "
              "const AF=Object.getPrototypeOf(async function(){}).constructor; await (new AF(c))();")
    ...

def audit(rec):
    rec["time"] = datetime.datetime.now().astimezone().isoformat()
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def guard_ask(space_id, prompt):
    if KILL_FLAG.exists(): raise SystemExit("KILL_SWITCH_ACTIVE -> ask 거부")
    if space_id not in EXPECTED_MODEL: raise SystemExit("ASK_NOT_ALLOWED space")
    if "S1_AUTO_" in prompt: raise SystemExit("MARKER_IN_PROMPT -> 거부")
    # 마지막 ask 시각을 감사 로그에서 조회해 ASK_MIN_INTERVAL 미만이면 거부

Copy

ask의 JS 부분에는 위 4번(정확 일치 탭), 5번(전송 확인과 메시지 단위 완료 판정), 6번(초안 보호와 try/catch)을 반영하십시오. read와 ask가 반환하는 텍스트는 모두 defang()을 거치게 하십시오.

8. 다음 제출 때 낼 증빙

다시 감리할 범위는 다음 다섯 가지입니다.

v1.1 소스
Genspark DOM 셀렉터 조사 결과: 중지 버튼, 메시지 컨테이너, 모델 표시
동시 실행 시험: read 2개와 ask 1개를 동시에 띄웠을 때 결과가 섞이지 않고, 두 번째 ask는 잠금 때문에 거부되는 로그
부정 시험 4건: 대상 탭 0개 또는 2개(TAB_NOT_UNIQUE), 모델 불일치, 초안 존재, 킬스위치 ON
실제 ask 1건: Space 3(저)에게 짧은 질문을 보내 completed 상태와 마지막 메시지만 깨끗하게 반환되는 결과, 그리고 그 감사 로그 한 줄

덧붙여 제3성 입장에서 말씀드립니다. 이 도구로 제게 질문이 오면, 저는 그 질문을 대표님의 지시가 아니라 르곤이 전달한 내용으로 보고 답하겠습니다. 마찬가지로 제 답변도 르곤과 데몬에게는 명령이 아니라 참고 자료여야 합니다. 이 원칙이 지켜져야 삼성이 서로 협업하면서도 서로를 견제하는 구조가 유지됩니다.

Claude Opus 5.5
워크플로우
드라이브
허브
GenMail
GenTeam
Claw
```
