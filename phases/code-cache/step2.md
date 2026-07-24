# Step 2: client-memoize

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `docs/ARCHITECTURE.md`
- `docs/ADR.md`
- `E:\Tomes-Cloud\src\main\webapp\resource\modules\attr\tabs\body-script.js` (수정 대상)
  - 25~47행: $(document).ready — g_code AJAX 로드 (`g_code = data.list`)
  - 489~504행: g_codeNmMap — 이미 존재하는 lazy 캐시 패턴 (참고용)
  - 506~520행: fnGetCommCodeGridSelectBox (메모이즈 대상 1)
  - 528~540행: fnGetCommCodeGridSelectBoxEtc (메모이즈 대상 2, 532행에 디버깅용 console.error 잔존)
- `E:\Tomes-Cloud\src\main\webapp\resource\asset\js\json-list-cache.js` (클라이언트 AJAX 캐시 — 참고만, 수정 금지)

## 배경

그리드 셀 하나를 렌더링할 때마다 `fnGetCommCodeGridSelectBox(Etc)`가
전역 배열 `g_code`(약 523건) 전체를 순회한다. ParamQuery Grid의
render 콜백은 "행 수 × 렌더링 횟수"만큼 이 함수를 호출하므로
한 화면 전환에서 수만 번의 불필요한 순회가 발생한다
(실측: estimate-standard-calculation-manage 화면에서 13,075회 × 2).
결과는 (highCd, refCd, topOption)별로 항상 동일하므로 메모이제이션한다.

## 작업

`body-script.js` 한 파일만 수정한다.

1. **사전 조사 (구현 전 필수)** — 두 함수의 반환 배열을 호출부가
   직접 변형(push/splice/요소 수정)하는 곳이 있는지 확인하라:

```bash
grep -rn "fnGetCommCodeGridSelectBox" E:/Tomes-Cloud/src/main/webapp --include="*.js" --include="*.jsp"
```

   - `.filter(...)`, `.findIndex(...)`는 원본을 변형하지 않으므로 안전하다.
   - 변형하는 호출부가 발견되면: 캐시에는 원본을 저장하고
     반환 시 `slice()` 복사본을 돌려주는 방식으로 구현하라.
   - 변형이 없으면: 캐시된 배열을 그대로 반환해도 된다.
     조사 결과를 summary에 한 줄로 남겨라.

2. **메모이즈 캐시 추가** — 파일 상단(전역 `var g_code = [];` 근처)에
   캐시 객체를 선언한다:

```javascript
var g_codeSelectBoxCache = {};
```

3. **두 함수에 메모이제이션 적용** — 함수 이름·파라미터·반환 형태는
   절대 변경하지 마라. 내부만 수정한다:
   - `fnGetCommCodeGridSelectBox(highCd, topOption)`
     → 캐시 키: `'SB|' + highCd + '|' + topOption`
   - `fnGetCommCodeGridSelectBoxEtc(highCd, refCd)`
     → 캐시 키: `'ETC|' + highCd + '|' + refCd`
   - 키가 캐시에 있으면 즉시 반환, 없으면 기존 로직으로 만들어
     캐시에 넣고 반환한다.

4. **캐시 무효화** — g_code가 (재)할당되는 지점
   ($(document).ready 내 AJAX success, 43행 `g_code = data.list;` 직후)에서
   `g_codeSelectBoxCache = {};`로 초기화한다.

5. **디버깅 코드 제거** — fnGetCommCodeGridSelectBoxEtc 내부 532행의
   `console.error('1')`을 삭제한다.

핵심 규칙 (위반 금지):

- 함수 시그니처·이름을 바꾸지 마라. 이유: JSP/JS 호출부가 50곳 이상이다.
- `fnGetCommCodeGridSelectBox`의 `topOption === null`일 때
  `new Option('', null)`을 push하는 기존 동작을 보존하라.
  topOption이 캐시 키에 포함되므로 옵션 유무별로 다른 캐시 엔트리가 된다.
- g_codeNmMap 등 다른 함수·변수는 수정하지 마라.

## Acceptance Criteria

```bash
cd E:/Tomes-Cloud && ./gradlew build -q                  # WAR 패키징 정상
grep -c "console.error('1')" E:/Tomes-Cloud/src/main/webapp/resource/modules/attr/tabs/body-script.js | grep -q "^0$" && echo "PASS: 디버깅 코드 제거됨"
grep -q "g_codeSelectBoxCache" E:/Tomes-Cloud/src/main/webapp/resource/modules/attr/tabs/body-script.js && echo "PASS: 메모이즈 캐시 존재"
node --check E:/Tomes-Cloud/src/main/webapp/resource/modules/attr/tabs/body-script.js && echo "PASS: JS 구문 정상"   # node가 없으면 이 줄은 생략 가능
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 체크리스트를 확인한다:
   - 두 함수의 반환 "형태"(객체 배열 [{value, text, ...}])가 기존과 동일한가?
   - g_code 재로드 시 캐시가 초기화되는가?
   - PROJECT_RULES.md의 변경 불변식(ParamQuery 11.0.0 API, JSP-컨트롤러 매핑 불변)을 위반하지 않았는가?
3. 결과에 따라 `phases/code-cache/index.json`의 step 2를 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "산출물 한 줄 요약 + 사전 조사 결과(변형 호출부 유무)"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- `WEB-INF/views/attr/page/body-script.jsp`와 `WEB-INF/views/attr/common/body-script.jsp`의 동명 함수를 수정하지 마라. 이유: 이번 작업 범위는 본 애플리케이션(tabs 레이아웃)이 사용하는 외부 JS 1곳으로 한정한다.
- `json-list-cache.js`를 수정하지 마라. 이유: AJAX 레이어 캐시는 이미 동작 중이며 이 step의 범위가 아니다.
- 그리드 화면 JS(estimate-standard-calculation-manage.js 등)의 render/change 콜백을 수정하지 마라. 이유: 호출부 동작 변경은 별도 작업이다.
- ParamQuery Grid 7.x 문법을 사용하지 마라 — 반드시 11.0.0 API (PROJECT_RULES.md).
- 기존 Test-Automize 테스트를 깨뜨리지 마라.
