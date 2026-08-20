# HANDOFF — 활성 작업 인덱스

_최종 갱신: 2026-08-20_

이 파일은 현재 작업을 찾기 위한 인덱스다. 운영 규칙은 `AGENTS.md`, 제품·안전 규칙은 `PROJECT_RULES.md`, 조건부 절차는 `docs/processes/`, 세부 경위는 연결된 `handoff/`, 완료 이력과 증적은 `logs/`에서 확인한다. 오래된 git·서버·DB 상태는 기록을 믿지 말고 다시 측정한다.

## 현재 환경

- 사용자 환경 맞춤 판단과 현재 PC·도구·작업 성향의 정본은 [`context/README.md`](context/README.md)에서 찾는다.
- 경로 정본은 `PATHS.md`, 작업별 변동 상태와 다음 행동은 아래 활성 작업과 연결된 handoff에서 확인한다. 오래된 git·프로세스·서버·DB 상태는 다시 측정한다.

## 활성 작업

- [KAN-44_소재표면처리기준정보] **D01 소재·D03 표면처리 PQ Grid 11 실조회·원격 목업 치수 반영 완료 / 대분류 표시명 설계·필터 대기·테넌트 사용여부 범위 제외** — `sunPro/common-code-master`의 `/commonCodeMasterV2`에서 소재 D01 활성 78건과 표면처리 D03 활성 51건을 원격 조회 그리드로 교체했다. 표면처리 7개 열은 원격 DOM 실측값 `83.219/182.109/164.313/267.234/154.500/407.672/173.953px`를 적용해 렌더 오차 0px이며, `TBL_MATERIAL_SURFACE_MAP` 집계로 적용소재를 `공통 24 / AL 전용 24 / Steel 전용 3`으로 표시한다. 소재 재질 콤보는 세션 공통코드의 D02 5종(`AL`, `Steel`, `SUS`, `비철`, `합성수지`)을 로딩한다. D01·D03 `ABBR_NM`의 한국어 표시명 정본이 없어 코드값을 유지하고 후속 협의 전까지 변경을 보류했다. 인증 화면에서 두 그리드 API 200·JavaScript 오류 0건을 확인했다. 책임자 검토에 따라 별도 `TBL_TENANT_CODE_USE` 방식은 미채택하고, 정식 처리를 위한 `TBL_CODE`·`SF_GET_CODE`의 `DEL_YN` 변경도 9월 클라우드 오픈 범위를 과도하게 확장하므로 이번 작업에서 제외한다 — [상세](handoff/SiteAdmin_재질표면처리매핑.md)
- [KAN-46_사이트설정부서종류] **추가·단일삭제 DB 연동·기본값 잠금·단일 체크·헤더 정렬 완료 / 제품 push·PR 자료 완료 / 사용여부 DB 연동 보류** — 공용 `selectCommonCodeList`·`commonCodeModifyGrid`·Java 계층은 변경하지 않고, 추가 팝업의 행 데이터가 인증 사용자 `SYSTEM_ID`를 기존 `insertCommonCode` 입력 형식으로 전달한다. 삭제 시에만 E04 전용 `selectDepartmentCodeUsageCount`를 기존 `/json-info`로 호출하고, 참조 0건이면 기존 `/paramQueryModifyGrid`의 `CODE` 처리와 `deleteCommonCodeLangAdmin`·`deleteCommonCodeAdmin`을 재사용한다. BASIC 행의 체크박스와 사용여부는 비활성화하고 직접추가 행은 한 번에 하나만 선택되며 컬럼 헤더는 가운데 정렬한다. 사용여부는 행 메모리 `DEL_YN`만 전환하고 DB 저장은 하지 않으며 직접추가 수정은 후속 대기다. 제품 `sunPro/KAN-46`의 커밋 `7c6a207`은 원격과 일치하고 PR MD·HTML을 생성했다 — [상세](handoff/SiteAdmin_재질표면처리매핑.md)
- [KAN-47_사이트설정Area구분] **E05 실조회·추가·단일삭제 연동 구현·기본값 잠금·단일 체크·목업 사용여부 완료 / 직접추가 수정·신규 삭제 매퍼 재기동 실호출 대기** — KAN-46 구조를 그대로 응용해 공용 `selectCommonCodeList`·`commonCodeModifyGrid`·`paramQueryModifyGrid`와 기존 Java 계층을 재사용한다. 삭제 시에만 E05 전용 `selectAreaCodeUsageCount`가 로그인 테넌트의 설비(`TBL_EQUIP.FACTORY_AREA`), POP 위치 연결(`TBL_CODE` E07 `REF_CD`), 생성자 소속으로 제한한 알람 Area 설정(`TBL_ALARM_DETAIL.FACTORY_AREA`)을 합산한다. BASIC 5건은 체크·사용여부가 잠기며 직접추가 행은 단일 선택과 행 메모리 `DEL_YN` ON/OFF만 동작한다. 인증 화면에서 E05 5건·헤더 중앙 정렬·폭 1419.9375px·추가 발번 `E05R51`·탭 왕복 상태 유지·추가 요청 0건·JavaScript 오류 0건을 확인했고 전체 빌드를 통과했다. 제품 브랜치는 `sunPro/KAN-47`이며 제품 변경은 미커밋이다 — [상세](handoff/SiteAdmin_재질표면처리매핑.md)
- [SiteAdmin_라벨프린터] **`TBL_SITE_PRINTER` 이관 확인 / 추가 팝업 설계 미제공으로 구현 보류** — 개발 DB에서 사이트별 활성 프린터 2건과 구 `E03R10` 접속값의 이관을 확인했다. 현재 제품의 출력 조회는 아직 `TBL_CODE.E03`에 남아 있고 V2 라벨프린터 화면은 정적 목업이지만, 추가 팝업 정본이 나오기 전에는 조회·등록·수정·삭제 및 출력 경로를 변경하지 않는다 — [상세](handoff/SiteAdmin_재질표면처리매핑.md)
- [노션작업일지자동화] **과거 누락분 백필·예약 경로 복구 완료 / 8/4 최종본 로컬 준비·인증 후 전송 대기** — 오전 백필은 실제 Notion 재조회까지 확인했다. 8/4 최종 작업 4건은 17:41 로컬 JSON으로 다시 생성해 이관 대기 목록에 보존했으며, 공식 Integration 토큰·DB ID가 없어 외부 전송은 하지 않았다. 사용자 계획에 따라 8/5 인증 복구 후 `--from-json` 전송과 재조회 검증을 진행한다 — [상세](handoff/토큰절감.md)
- [SiteAdmin_재질표면처리매핑] **환경별 매핑 조회·D03 REF_CD 후퇴 제거·대분류 상속 구현 커밋 완료 / refCd 분기 가독성 변경 미커밋·최신 v3 인증 세션 확인 대기** — 원격 `feature-materialmap-0803`의 `43690a0`은 코드 5파일 `+48/-10`이며, D03은 `MATERIAL_TYPE_CDS`, 다른 기준코드는 기존 `REF_CD`를 사용한다. 2026-08-07에는 별도 worktree에서 동일 함수 3곳을 기본 `refCd`·D03 `mapCd` 명시 분기로 정리해 문법·분기 단위 검증·전체 빌드를 통과했다. 재현 SQL은 원격 커밋에 포함되지 않은 미추적 파일이라 별도 결정이 필요하다 — [상세](handoff/SiteAdmin_재질표면처리매핑.md)
- [SiteAdmin_화면설계서11~14] **소재·표면처리 콘텐츠 목업 완료 / 백엔드 연동 대기** — 공통 셸 변경 없이 신규 JSP·전용 CSS·JavaScript로 목록, 필터, 등록 모달, 사용 중 삭제 제한을 구현해 Edge 렌더·Playwright 상호작용·전체 빌드를 통과했다 — [상세](handoff/SiteAdmin_재질표면처리매핑.md)
- [Codex주에이전트전환] **현재 PC `work` 프로필·핵심 개발·테스트 기능 호환 완료 / GUI 도구 데이터 이관 대기** — 저장소 밖 로컬 마커와 `scripts/pc_profile.ps1`로 PC를 구분하며, `%클라우드`의 Claude 로컬 설정과 개발 실행 배치는 기능 stash에서 제외해 작업트리에 유지한다. 프로필 테스트 4 PASS, 하네스 76 PASS이며 기존 개발·테스트 기능과 Git 원격·Gradle도 정상이다. VS Code·Codex 개인 홈·SourceTree·DBeaver·Git 전역 데이터 이관은 별도 대기 — [상세](handoff/Codex주에이전트전환.md)
- [업무PC복귀인계] **주요 복구·Codex 훅·실화면 재검증 완료 / 개발 DB TLS 결정·미전달 원본 대기·POP 실기기 보류** — 개발 런타임·경로·Windows `workspace` 샌드박스 복구와 Codex 훅 상태 전이 검증을 완료했다. 개발 DB 서버는 TLS가 비활성이고 Connector/J도 기본 비SSL 연결이며, 로컬 MariaDB 설정에는 존재하지 않는 `E:` 플러그인 경로가 남아 있어 적용 방침 결정이 필요하다. POP 바코드 스캐너 실기기 검증은 2026-07-29 사용자 결정으로 보류했다. 하네스 60 PASS, 제품 빌드 PASS, `%테스트` 191 PASS/기존 계획 불일치 3 FAIL — [상세](handoff/업무PC복귀인계.md)
- [%테스트현대화] **전체 205 PASS·OSR-173 실동작 PASS / GWS OAuth 인증 대기** — 결정론 우선 정책에 맞춰 자동 Stage4 heal을 제거하고 batch를 최대 20으로 제한했으며, 선택적 AI 설정·제품 경로·GWS 실행 경로를 중앙화했다. OSR-173은 현재 제품의 실제 SIZE_TYPE 옵션과 W/H/T/D/L 표시 계약으로 Stage4·시드·Sheet 쓰기 없이 PASS했다. GWS 0.22.5는 D:에 설치했지만 OAuth client/login이 없어 최신 Sheet 확인과 row 899 menu2 불일치 정정은 대기한다 — [상세](handoff/테스트현대화.md)
- [가공확정] **KAN-63 화면·기존 데이터 보존 / 메뉴·R14/R16 코드 비활성화 / 후속 판단 기준 S11 전환·최종 push 완료** — 작업지시 확정·취소의 기존 S53 생성은 유지하고 자재·POP·도면·MCT·검사의 판단 기준만 동시에 저장되는 S11으로 전환했다. V1 XML 보정 3파일을 포함한 최종 커밋 `fde3d05`를 원격에 반영했으며 전체 빌드·XML·JS·diff 검증을 통과했다 — [상세](handoff/가공확정.md)
- [단가검토] **변경 3파일 독립 stash 보관 / 사용자 결정 대기** — 단가입력 개편과 기록조회 변경을 별도 stash로 분리했다. 배송비 컬럼명·견적→주문 복사 여부 결정 후 DDL 및 후속 작업을 재개한다 — [상세](handoff/단가검토.md)
- [DB결함] **실동작 6 PASS·0 FAIL / 기능 검증 완료·커밋·push 취소 후 제품 변경 stash 보관** — 최초 신규 주문 FAIL은 시퀀스나 제품 변경이 아니라 8/7 Codex 테스트 잔존 12건의 고정 `ORDER_SEQ` 충돌이었다. 해당 주문·작업·검사·가공 참조만 정리한 뒤 단건과 동시 2건을 재실행해 `ORDER_SEQ`·접수번호 유일성과 락 해제, 테스트 잔존 0건을 확인했다. 제품 변경 4파일은 stash 객체 `b13cc5052ff392afa787eb3460fda103cc8058bf`로 분리 보관했다 — [상세](handoff/DB결함.md)
- [거래명세표] **보류** — 슬라이드36·라벨모달은 `stash@{0}`에 보관. 수량 의미와 라벨 보호 정책 결정 후 재개 — [상세](handoff/거래명세표.md)
- [테넌트기준코드사용여부] **구현 중단 / `TBL_TENANT_CODE_USE` 미사용·개발 DB 잔존 테이블 정리 결정 대기** — 책임자 검토 결과 테넌트별 D01·D03 사용 여부를 별도 테이블로 관리하는 설계를 채택하지 않기로 했다. 정식 처리는 `TBL_CODE`와 `SF_GET_CODE`의 `DEL_YN` 흐름을 함께 변경해야 하지만 9월 클라우드 오픈 범위를 과도하게 확장하므로 진행하지 않는다. 현재 제품 브랜치의 해당 테이블 참조는 0건이고, 개발 DB의 빈 테이블은 별도 삭제 승인 전까지 미사용 상태로 둔다 — [상세](handoff/SiteAdmin_재질표면처리매핑.md)
- [기타] **JUnit Platform 테스트 설정 stash 폐기 / 대기 항목 모음** — 관련 테스트 소스 삭제 후 사용자 지시에 따라 `%클라우드`의 JUnit Platform 활성화 stash 객체 `b75b9c07d25904b604ff6b4980860c28287b7816`를 삭제했다. 도면팝업 실화면 검증, 로컬 설정 복구 경위, 직원 목록 캐시 개선은 대기 중이다 — [상세](handoff/기타.md)

## 운영 문서

- Codex 진행 안내: [handoff/Codex진행안내.md](handoff/Codex진행안내.md)
- 세컨브레인 구조: [docs/SECOND_BRAIN.md](docs/SECOND_BRAIN.md)
- 완료 이력: [logs/HANDOFF_ARCHIVE.md](logs/HANDOFF_ARCHIVE.md)
