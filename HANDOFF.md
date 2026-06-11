# HANDOFF — 다음 세션 인수인계

_최종 갱신: 2026-06-11_

## [2026-06-11] code-cache step 0 완료 (server-cache)
- **완료**: `InnodaleServiceImpl.getList()`에 위임 분기 추가 — queryId가 `systemMapper.selectSessionCodeList`이고 LOGIN_SYSTEM_ID가 있으면 주입된 `SystemService.getSessionCodeList()`(기존 Redis @Cacheable, everyHour) 호출. 없으면 기존 DAO 경로 유지(멀티테넌트 안전). 순환 의존성 없음 확인(SystemServiceImpl은 DAO만 주입).
- **검증**: `gradlew build -q` 통과. 커밋: %클라우드 Sun-Pro 454d822, &하네스 feat-code-cache a701100(index.json step0=completed).
- **다음 단계**: step 1 cache-evict(commonCodeModifyGrid에 @CacheEvict), step 2 client-memoize. 완료 후 서버 재시작(startServer.local.bat) + 화면 확인.

## [2026-06-11] 공통코드 캐싱 task 생성 (code-cache)
- **목표**: 고정 기준코드의 반복 DB 조회·렌더링 순회 제거 (서버 Redis + 클라이언트 메모이즈)
- **핵심 발견**: `/json-list`(selectSessionCodeList)는 캐시를 안 타지만, 동일 쿼리를 감싼 `SystemServiceImpl.getSessionCodeList()`에 이미 Redis @Cacheable(everyHour) 존재 → 위임만 하면 됨. 클라이언트엔 json-list-cache.js(30분 메모리 캐시)도 이미 존재.
- **생성 파일**: `phases/index.json`, `phases/code-cache/index.json`, `phases/code-cache/step0~2.md`
  - step0 server-cache: InnodaleServiceImpl.getList → getSessionCodeList 위임 (LOGIN_SYSTEM_ID 없으면 우회)
  - step1 cache-evict: commonCodeModifyGrid에 @CacheEvict(allEntries, cacheManager="everyHour")
  - step2 client-memoize: body-script.js 두 함수 메모이즈 + console.error('1') 제거
- **다음 단계**: `python3 scripts/execute.py code-cache` 실행 → 완료 후 gradlew build + 서버 재시작(startServer.local.bat) + 화면 확인
- **주의**: 멀티테넌트 — 캐시 키에 SYSTEM_ID 필수. @Primary cacheManager가 every5Seconds라 evict에 everyHour 명시 필요.

## [2026-06-11] estimate-standard-calculation-manage 무한루프 디버깅
- **증상**: `fnGetCommCodeGridSelectBoxEtc`의 for문이 무한반복처럼 보임 + 심어둔 `console.error('1')`(body-script.js:532)가 반영 안 됨.
- **무한반복 원인(분석 완료, 수정 미적용)**: `estimate-standard-calculation-manage.js`의 change 핸들러(645행·2090행)가 source 필터에 `'update'`를 포함 → `updateRow` API가 다시 change를 발생시켜 재진입 + merge 범위 전파 + `refreshView` 중복 호출(660·683행)로 렌더 폭증. for문 자체는 무한 아님. 수정안: source 필터에서 `'update'` 제거(표면처리비 그리드 1331행은 이미 그렇게 되어 있음).
- **반영 안 된 원인(해결)**: 서버가 `java -jar build\libs\ROOT.war` 방식(shell\startServer.local.bat). 구 프로세스(9:38 시작)가 신규 WAR 빌드(9:43) 이전에 떠서 구버전 서빙 중이었음. PID 32788 종료 → bat 재실행 → HTTP로 `console.error('1')` 서빙 확인 완료.
- **워크플로우**: 소스 수정 → `gradlew build` → 서버 재시작 (이 순서 필수. 정적 리소스도 WAR에 포함됨).
- **주의**: 함수 정의가 3곳(tabs용 `resource/modules/attr/tabs/body-script.js:528`=본 앱 사용, `views/attr/page/body-script.jsp:593`, `views/attr/common/body-script.jsp:515`). 디버깅 끝나면 body-script.js:532의 `console.error('1')` 제거 필요.

---

## 작업 목표
- 직전 본 작업: **%테스트(E:\Test-Automize)를 사용해 "TBL_CODE1 영향 범위.xlsx" 기반으로 이전에 테스트했던 14개 쿼리를 다시 테스트**하기.
- 그 전에 환경/규칙 정비를 먼저 진행 중이었음.

## 완료
- **프로젝트 약칭 규칙 확정**: `%클라우드`=E:\Tomes-Cloud, `%테스트`=E:\Test-Automize(최신), `&하네스`=E:\harness_framework. (CLAUDE.md + 메모리 반영) ※ 구버전 E:\Tomes-AutoTest는 사용자가 삭제함.
- **권한 모드 변경**: `&하네스\.claude\settings.local.json`의 `permissions.defaultMode` = `"bypassPermissions"` (자동 승인). 위험명령 차단 PreToolUse 훅·빌드/테스트 Stop 훅은 유지.
- **CLAUDE.md 규칙 추가**: (1) 민감 작업(설정 변경 등)은 yes/no 전 본문 상세 설명, (2) 세션 관리 규칙(HANDOFF 상시 갱신 + 컨텍스트 ~50% 사용자 주도 초기화).
- **상태줄 설정**: 컨텍스트 사용량 % 상시 표시(`[ctx 48% (96k/200k)]`), 50%↑면 `[!ctx ...]`. 스크립트 `C:\Users\USER\.claude\statusline-command.sh`, 설정 `C:\Users\USER\.claude\settings.json`.
- 메모리 파일: feedback_project_aliases / feedback_explain_before_sensitive / feedback_session_handoff 저장.

## 진행 중 · 미완
- **%테스트 프로젝트 파악(미완)**: README/CLAUDE.md/qa_agent 구조/테스트 실행 방식(`python -m qa_agent.agent_run --row N`)/시나리오 포맷(docs/scenarios의 CD-FT-BIZ-*.json) 등을 아직 못 읽음. 권한 프롬프트·사용자 인터럽트로 중단됨.
- **14개 쿼리 재테스트(미착수)**.

## 다음 단계
1. (재시작 후) bypassPermissions·상태줄 적용 확인.
2. **%테스트 파악 먼저**: README, CLAUDE.md(E:\Test-Automize\CLAUDE.md), HANDOFF_NEXT_SESSION.md, qa_agent/, test_auto/, docs/scenarios 샘플, config.py, requirements.txt 읽고 "아는 것/모르는 것" 정리해 사용자에게 보고.
3. 그 다음 14개 쿼리를 %테스트 방식으로 테스트.

## 14개 쿼리 (테스트 대상 — TBL_CODE1→TBL_CODE / TBL_CODE_LANG1→TBL_CODE_LANG 마이그레이션)
- `sqlMaps/v1/main.xml`: selectProcessHistoryList-mainV1 (메인 대시보드) — 1개
- `sqlMaps/v1/material.xml`: 12개 (소재 주문등록 / 보유 소재 관리 / 재고관리). 예: selectItemOrderRegisterListV1, selectInWarehouseManageListV1, selectInsideStockListV1 등
- `sqlMaps/material.xml`: selectInsideStockAbbrNm (line 2297, 소재 관리>내부 재고) — 1개
- 원본 영향범위 엑셀: `C:\Users\USER\Desktop\기준코드 관련\TBL_CODE1_영향범위.xlsx` (전체 112개 참조 중 위 14개가 실제 변경됨). 엑셀 덤프: `E:\harness_framework\logs\xlsx_dump.txt`
- 이전(구버전 Tomes-AutoTest) 테스트 결과: CD-MAIN-001, CD-MAT-001~009 = 10/10 통과. **단, %테스트엔 해당 시나리오(CD-MAT/CD-MAIN)가 없음** → 새로 매핑/작성 필요할 수 있음.

## 블로커 · 주의
- 로컬 서버 URL: `http://smd.localhost:8081/` (이전 확인 시 HTTP 302 = 가동 중). 개발서버는 `https://dev-smd.tomes.co.kr:8081`.
- gws(Google Sheets) OAuth 토큰 만료 이력 있음 — 시트 연동 테스트 시 재인증 필요할 수 있음.
- 재고관리 메뉴는 작업관리(MENU_SEQ 1058) 하위로 이동됨(SEQ=1061). 메뉴 Depth 판단은 [시스템][메뉴관리] 페이지(DEL_YN='N' 활성 메뉴) 기준.
- 3단계 이상(상세/팝업/탭) 쿼리는 추가 인터랙션 자동화 필요.
