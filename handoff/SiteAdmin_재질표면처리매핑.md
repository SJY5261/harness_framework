# Site Admin 재질-표면처리 매핑

_최종 갱신: 2026-08-07 / 상태: 진행 중_

## 현재 상태

- 2026-08-18 `sunPro/common-code-master`의 `/commonCodeMasterV2` 소재 목업 표를 ParamQuery Grid 11로 교체하고 `systemMapper.selectMaterialCodeGridList`를 통해 활성 D01을 원격 조회하도록 연결했다. 개발 DB SMD 기준 78건이며 소재코드·D01 약어·한국어 소재명·D02 재질명·비고를 표시한다. `TBL_TENANT_CODE_USE`는 기본값·행 생성 정책 결정 전이므로 이번 단계에서는 사용하지 않고 활성 D01을 읽기 전용 ON으로 표시한다. 최초 조회 500은 JSP만 핫리로드되고 실행 중인 8081의 `build/resources`에는 신규 MyBatis statement가 없어서 발생했다. 서버 재기동 후 인증 세션에서 `/paramQueryGridSelect` HTTP 200, 그리드 78건, 첫 행 `AL0101 / AL1050 / AL`, `POOL 78 · ON 78`, JavaScript 오류 0건을 확인했다. 원격 정적 목업을 1600×1000 뷰포트에서 실측해 `No/소재코드/대분류/소재명(표준)/재질/주요특성/사용여부` 열을 `73/121/185/169/92/320/152px`, 헤더 40px, 행 34px, 글꼴 12px, 셀 좌우 여백 12px로 반영했다. 원격 대비 열 너비 최대 오차는 0.406px이며 높이 오차는 0px이다. 실제 화면에서 헤더 정렬·코드 색상·여백·줄무늬 제거까지 비교했고, XML·인라인 JavaScript 문법, `git diff --check`, 격리 Gradle 전체 빌드를 다시 통과했다.
- 2026-08-18 원격 DevTools의 순차 캡처값을 기준으로 `No/소재코드/대분류/소재명(표준)/재질/주요특성/사용여부` 너비를 `93.125/155.125/236.969/215.531/117.562/409.484/205.203px`로 다시 확정했다. PQ Grid의 자동 축소를 끄기 위해 `scrollModel.autoFit=false`를 적용했으며, 소스 저장 후 로컬 탭을 새로고침해 실제 헤더 너비 최대 오차 0.016px, 헤더 높이 40px, D01 78건, 조회 API HTTP 200, JavaScript 오류 0건을 확인했다.
- 2026-08-18 표면처리 정적 목업 표도 `systemMapper.selectSurfaceTreatmentCodeGridList`를 사용하는 지연 초기화 PQ Grid 11로 교체했다. 활성 D03 51건을 조회하며 `TBL_MATERIAL_SURFACE_MAP`의 대분류별 소재 매핑을 집계해 단일 소재는 `AL 전용`·`Steel 전용`, 복수 소재는 `공통`으로 표시한다. 분포는 `공통 24 / AL 전용 24 / Steel 전용 3`이고 코드·표면처리명·적용소재 누락과 코드 중복은 0건이다. 원격 DOM에서 직접 측정한 `No/표면처리코드/대분류/표면처리명(표준)/적용소재/비고/사용여부` 너비 `83.219/182.109/164.313/267.234/154.500/407.672/173.953px`, 헤더 40px, 행 34px를 반영했으며 렌더 너비 오차는 0px이다. 전체 Gradle 빌드와 XML·인라인 JavaScript·diff 검사를 통과하고 8081 재기동 후 API HTTP 200, D03 51건, JavaScript 오류 0건, 기존 소재 78건 유지까지 확인했다. 현재 대분류 매핑 테이블 구조는 이번 읽기 전용 적용소재 표시에 그대로 사용할 수 있다.
- 2026-08-18 소재 화면의 재질 콤보를 세션 공통코드 `g_code`의 `HIGH_CD='D02'`로 연결했다. 공통코드 로더가 `document.ready`에서 동기 요청을 완료한 뒤 `fnGetCommCodeGridSelectBox('D02')` 결과를 추가하도록 실행 순서를 맞췄다. 실화면에서 `전체(value='')`, `D02R10=AL`, `D02R15=Steel`, `D02R20=SUS`, `D02R25=비철`, `D02R30=합성수지` 6개 옵션, 소재 Grid 78건 유지, JavaScript 오류 0건을 확인했다. 이번 단계는 옵션 로딩만 포함하며 선택값에 따른 Grid 필터링은 아직 연결하지 않았다.
- 2026-08-18 개발 DB D01 스키마와 활성 78건을 재확인한 결과 `ABBR_NM` 9종(`AL`, `AS`, `CS`, `CU`, `SR`, `SS`, `TI`, `TS`, `ZN`)의 한국어 표시명을 보관하는 정본 컬럼·코드는 없다. `TBL_CODE_LANG.CODE_NM`은 `AL1050`, `SM20C`처럼 개별 D01 소재명이고 `NOTE`, `ETC1~ETC5`는 D01 전체가 비어 있다. 사용자 결정으로 대분류 표시명 정보 설계와 화면 변경은 후속 협의 전까지 보류하고, 현재 PQ Grid는 `ABBR_NM` 코드값을 유지한다.
- 사용자 요구를 재확인해 매핑 정책을 `재질 ↔ 개별 D03` 직접 매핑에서 `재질 ↔ 표면처리 대분류` 상속으로 확정했다. 같은 대분류의 모든 하위 D03은 동일한 재질 규칙을 상속하며 개별 예외는 허용하지 않는다. Site Admin 목록·저장 API와 편집 화면은 포함하지 않는다.
- 요구사항 정본은 `C:\Users\User\Desktop\Downloads\Site Admin 화면설계서_260723.pptx`의 15번 슬라이드다.
- 2026-08-18 별도 화면 작업으로 같은 PPTX의 11~14번을 기준으로 소재·표면처리 목록, 등록 모달 2종, 사용 중 삭제 불가 모달을 신규 구현했다. 공통 셸은 변경하지 않았으며 콘텐츠 JSP는 `/static/admin/site-admin-reference-master` 경로로 기존 탭 셸에 삽입된다. 현재는 프런트 목업으로 필터·검색·초기화·탭·POOL 토글·모달 동작만 포함하고 DB 조회·저장 API는 연결하지 않았다. 1600×1000 Edge 렌더와 Playwright 상호작용, JavaScript 문법, 전체 Gradle 빌드를 통과했다.
- 개발 DB `smd`의 정본을 `TBL_MATERIAL_SURFACE_MAP`으로 변경했다. `MAP_SEQ` 단일 PK와 `(SYSTEM_ID, SURFACE_TREAT_GROUP_CD, MATERIAL_TYPE_CD)` UNIQUE 업무키를 사용하며, `BASIC` 12개 대분류의 D02 매핑 38건을 보존했다. 하위 D03으로 펼치면 기존 직접 매핑 125건과 양방향 차이 0건이다. `NA`는 정식 대분류로 포함하며 활성 재질 5종 전체를 허용한다.
- 개발 DB의 활성 공통코드는 `TBL_CODE(BASIC)` 기준 D02 5개·D03 51개뿐이며 로그인 테넌트 소속 D02·D03 코드는 없다. 애플리케이션은 매핑을 조회만 하며 생성·수정·삭제 API를 제공하지 않는다.
- 2026-08-05 개발 DB `TBL_CODE(BASIC)`의 활성 D01·D03 중 `ABBR_NM`이 `CODE_CD` 앞 두 자리와 다른 45건을 코드 접두어로 통일했다. D01은 `SR` 29건·`TI` 4건, D03은 `PL` 10건·`CR` 2건이며 변경 전 원본은 `TBL_CODE_ABBR_BAK_20260805_134835`에 보존했다.
- 2026-08-05 매핑 대분류의 참조 정본을 D03 `CODE_CD` 앞 두 자리에서 `TBL_CODE.ABBR_NM`으로 전환했다. `SURFACE_TREAT_GROUP_CD` 컬럼과 기존 38건 데이터는 유지하고, 실행 조회와 재현 SQL의 시드·검증 JOIN만 `ABBR_NM` 기준으로 변경했다.
- 2026-08-06 사용자 확인에 따라 `selectSessionCodeList`의 매핑 조건을 `M.SYSTEM_ID IN ('BASIC', #{LOGIN_SYSTEM_ID})`으로 단순화했다. 클라우드 매핑 테이블은 `BASIC`, 온프레미스 매핑 테이블은 `BASIC` 없이 실제 테넌트 `SYSTEM_ID`를 사용하며 같은 환경에 두 종류가 공존하지 않는 데이터 정책을 전제로 한다. 결과 필터에 필요 없고 테넌트 매핑에서 정렬 근거도 불완전했던 D02 `TBL_CODE` 조인은 제거한 상태를 유지한다.
- 2026-08-06 사용자 결정으로 화면의 D03 재질-표면처리 필터에서는 구형 `REF_CD` 호환 후퇴를 제거했다. D03은 `MATERIAL_TYPE_CDS`만 정본으로 사용하며 값이 없거나 선택 재질이 포함되지 않으면 표시하지 않는다. D03 외 기준코드는 기존 `REF_CD` 동작을 유지한다.
- 2026-08-07 사용자 요청에 따라 `fnGetCommCodeGridSelectBoxEtc(highCd, refCd)`의 중첩 삼항식을 명시적 분기로 정리했다. 기본은 기존 `REF_CD` 비교를 유지하고 D03 분기에서만 `mapCd = refCd`로 의미를 부여해 `MATERIAL_TYPE_CDS` 포함 여부를 검사한다. 동일 함수 3곳을 맞췄으며 제품 변경은 전용 worktree `D:\ToolData\Harness\worktrees\materialmap_refcd`에 미커밋으로 보존했다.
- 2026-08-07 실제 Git 상태를 다시 확인한 결과 원격 커밋 `43690a0`에는 제품 코드 5파일 `+48/-10`만 포함되어 있다. 재현 SQL은 원래 제품 작업트리에서 미추적 상태라 원격 커밋에 포함되지 않았으며, 과거의 “SQL 포함 6파일·제품 미커밋” 기록보다 이 항목을 최신 상태로 본다.
- 기존 업무 테이블의 재질·표면처리 동시 입력은 현재 19,230건이다. 이 중 18,952건은 구형 `D03Rxx`, 86행은 신형 의미 코드이며, 신형 86행 중 현재 매핑에 해당 재질 조합이 없는 업무 데이터는 13행이다. 2026-08-06 사용자 결정에 따라 이 13행은 정책상 사용하지 않고 이관·예외 처리하지 않으며 기존 저장값도 변경하지 않는다.
- 제품 저장소는 `feature-materialmap-0803`이며, 2026-08-03에 사용자 지시에 따라 다른 기능 작업만 작업 단위별 stash로 분리했다. 2026-08-06 환경별 `SYSTEM_ID` 후보 조회와 캐시 `v3` 전환까지 반영한 현재 기능 변경은 SQL 1파일을 포함해 6파일 `+302/-10`이다. `.claude/settings*.json`과 `shell/runDev.local.bat`은 로컬 환경 파일이며 제품 커밋은 만들지 않았다.
- 2026-08-06 현재 6파일 diff와 DB 변경·Redis/브라우저 캐시 흐름·복구 절차를 정리한 PR 리뷰 MD·자체완결 HTML을 `C:\Users\User\Desktop\PR\[08.06 재질표면처리 매핑 및 캐시 PR 리뷰]`에 생성했다. 전체 빌드, JavaScript 문법, XML 파싱, D03 매핑 전용·다른 기준코드 `REF_CD` 유지 동작을 다시 검증했으며 최신 `v3` 서버의 인증 세션 검증은 남아 있다.
- 2026-08-03 실제 화면에서 소재종류 선택 후 신규 매핑이 아니라 기존 `REF_CD` 매핑이 표시되는 현상을 재현했다. 직접 DB 시드 전 Redis 응답과 브라우저 30분 캐시가 원인이었으며, 서버·브라우저 공통코드 캐시 키를 `surface-material-map-v1`으로 전환하고 전체 빌드를 통과했다. 이후 재시작된 8081 서버의 새 브라우저 세션에서 신규 매핑 응답과 소재별 필터를 확인했다.
- 2026-08-04 DB 변경을 포함한 당시 6파일의 대분류 상속 PR 설명 MD·HTML을 `C:\Users\User\Desktop\PR\[08.03 재질표면처리 코드 변경 PR]`에 갱신했다. 2026-08-05 `ABBR_NM` 참조 전환은 아직 반영하지 않았고, 제품 변경도 미커밋이며 실제 GitHub PR은 만들지 않았다.
- 2026-08-05 현재 저장된 `톰스클라우드_코드변경_최신.xlsx`와 개발 DB 실제 `TBL_CODE(BASIC)` 520건을 다시 비교했다. 코드 집합·정렬·`ABBR_NM` 차이는 0건이고 직접 불일치는 `E12R10` 코드명 1건이며, Excel 내부 표기 문제는 별도로 분리해 `C:\Users\User\Desktop\PR\[08.05 DB-Excel 코드 불일치 현황]`의 MD·자체완결 HTML에 기록했다.
- 2026-08-04 초보 개발자용 코드 가이드도 `대분류 테이블 → MyBatis 조회 → 서버 캐시 → 공통·페이지·탭 화면` 순서와 당시 6파일의 전체 Git diff로 작성했다. 2026-08-05 `ABBR_NM` 참조 전환 전 산출물이므로 재갱신이 필요하다.
- 2026-08-04 테이블명·단일 PK 전환 전에 `TBL_SURFACE_TREAT_GROUP_MATERIAL_MAP_BAK_20260804_PK`에 38건을 보존했다. 전환 후 `MAP_SEQ` 1~38, 업무키 중복 0건, 백업과 양방향 데이터 차이 0건을 확인하고 새 조회 코드로 8081을 재기동해 루트 HTTP 200을 확인했다.

## 2026-08-03 Git 작업 분리

- 단가검토: `24c94b4db0dfafebf70f39d1bd2b0940bc8a376d`
- KAN-63 작업지시 재확정 예외: `ca1524ddac4f19964336418d77f0344ee62a6ec4`
- KAN-6 작업상세 가공확정·진행상태 제거: `942c7f7ad80b161f5609fa34f24d4f9f1d7ff1aa`
- Claude 로컬 설정과 로컬 개발 실행 배치는 stash 대상에서 제외하고 원래 작업트리에 복원했다.
- stash 분리 전후 재질-표면처리 tracked diff 해시는 `791a5b1777b6d977e25a3cd7dc5fd9d4cc244339`, 신규 SQL SHA-256은 `28D12DF926AF874E965B598C5B97A67F779EEAC1385AB1F806EF1F0BC11FF58E`로 동일하다.
- 현재 작업트리에는 staged 파일이 없고, 기능 변경은 재질-표면처리 관련 파일만 남아 있다.
- 2026-08-11 사용자 결정으로 테넌트별 소재(D01)·표면처리(D03) 사용 여부 정본 `TBL_TENANT_CODE_USE`를 개발 DB에 생성했다. 복합 PK는 `(SYSTEM_ID, HIGH_CD, CODE_CD)`, 값은 `USE_YN`, 감사 컬럼은 기존 `TBL_CODE` 규격을 따르며 D01·D03/Y·N CHECK를 적용했다. 초기 데이터와 트랜잭션 검증 잔존은 0건이고 재현 SQL은 `%클라우드`의 `docs/db/20260811_tenant_code_use.sql`에 있다. V2 화면 조회·토글 저장·테넌트 한정 캐시 무효화 연결은 아직 구현하지 않았다.

## 목표·완료 조건

- 완료: 슬라이드 15 매트릭스를 개별 예외 없는 대분류 상속형 다대다 테이블과 재현 가능한 SQL로 정의한다.
- 완료: 개발 DB에 대분류 매핑 38건을 반영하고 건수·고아 코드·미매핑 표면처리·기존 직접 매핑 등가성을 검증한다.
- 완료: 기존 공통코드 조회가 D03별 다중 재질 매핑을 반환하고 화면이 선택한 재질에 맞는 D03만 표시한다.
- 완료: D03 선택 함수는 `MATERIAL_TYPE_CDS`만 사용하고 값이 없으면 미표시하며, D03 외 기준코드는 기존 `REF_CD` 동작을 유지한다.
- 완료: 재시작된 서버의 새 브라우저 세션에서 업무 화면 공통코드 응답과 소재별 표면처리 필터를 검증한다.
- 완료: PPTX 11~14번 기준 소재·표면처리 콘텐츠 화면과 등록·삭제 제한 모달을 공통 셸과 분리된 프런트 목업으로 구현한다.
- 범위 제외: 2026-08-18 화면은 프런트 목업까지만 포함하며 실제 매핑 목록·저장·수정·삭제 API와 DB 연동은 후속 범위다.

## 결정

- 별도 `TBL_MATERIAL_SURFACE_MAP` 사용 — 정책 단위가 개별 D03이 아니라 `AN`, `PL`, `NA` 같은 대분류이므로 중복 없이 상속 관계를 표현한다.
- 행 식별자는 `MAP_SEQ` 단일 PK로 통일하고, 업무 중복은 `(SYSTEM_ID, SURFACE_TREAT_GROUP_CD, MATERIAL_TYPE_CD)` UNIQUE 제약으로 별도 방지한다. 별도 시퀀스 객체와 등록 API는 만들지 않는다.
- 같은 대분류의 모든 하위 D03은 동일한 재질 규칙을 상속하며 개별 예외·추가·제외·덮어쓰기를 허용하지 않는다.
- `NA`는 정식 대분류이며 5개 활성 재질 전체를 허용한다.
- 조회 후보는 `BASIC`과 로그인 `SYSTEM_ID`로 제한한다. 클라우드는 `BASIC` 매핑만, 온프레미스는 `BASIC` 없이 실제 테넌트 매핑만 저장하는 환경별 데이터 정책으로 한쪽 결과만 조회한다.
- 같은 DB에 `BASIC`과 로그인 테넌트 매핑이 함께 있으면 `IN` 조건상 양쪽 값이 `GROUP_CONCAT`에 합쳐진다. 병합이 아니라 환경 분리를 전제로 하므로 배포·이관 시 해당 매핑 테이블의 `SYSTEM_ID` 공존 여부를 검증한다.
- 아직 확인되지 않은 온프라미스 고객별 관리 UI·설정 요구는 추측해 만들지 않고, 실제 요구가 생길 때 같은 공통 구현 위에 확장한다.
- 매핑 관리는 SQL로 준비하고 애플리케이션은 조회만 수행 — 현재 요구는 재질 선택 시 연결된 표면처리 표시이며 온라인 편집은 필요하지 않다.
- 기존 업무 데이터는 자동 이관하지 않음 — 구형 코드 18,952건은 그대로 유지하고, 현재 매핑에 없는 신형 업무 데이터 13행은 정책상 사용하지 않으며 이관·예외 처리하지 않는다.
- D03 필터는 `MATERIAL_TYPE_CDS`만 사용하며 `REF_CD`로 후퇴하지 않는다. 이전 캐시는 서버·브라우저 스키마 `v3`로 분리하고, 다른 기준코드만 기존 `REF_CD`를 계속 사용한다.

## DB 변경

### 대상과 환경

- 환경: 개발 DB `smd`, MariaDB 10.11.15
- 신규 정본 테이블: `TBL_MATERIAL_SURFACE_MAP`
- 단일 PK: `MAP_SEQ int(11) NOT NULL AUTO_INCREMENT`
- 업무키 UNIQUE: `UK_MSM_MAP(SYSTEM_ID, SURFACE_TREAT_GROUP_CD, MATERIAL_TYPE_CD)`
- 역방향 인덱스: `IDX_MSM_MATERIAL(SYSTEM_ID, MATERIAL_TYPE_CD, SURFACE_TREAT_GROUP_CD)`
- 기존 직접 매핑 백업: `TBL_SURFACE_TREAT_MATERIAL_MAP_BAK_20260804`
- PK 변경 전 백업: `TBL_SURFACE_TREAT_GROUP_MATERIAL_MAP_BAK_20260804_PK`
- 기존 업무 테이블의 컬럼·인덱스·데이터는 변경하지 않았다.

### 변경 전 → 변경 후

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| 재질-표면처리 관계 | 개별 D03 직접 매핑 | `MAP_SEQ` 단일 PK + 시스템·대분류·재질 UNIQUE |
| 역방향 조회 | `IX_STMM_MATERIAL` | `IDX_MSM_MATERIAL(SYSTEM_ID, MATERIAL_TYPE_CD, SURFACE_TREAT_GROUP_CD)` |
| 기준 매핑 | `BASIC` 직접 매핑 125건 | `BASIC` 대분류 매핑 38건, 하위 D03 확장 시 125건 |

### 실행 순서·복구

1. 기존 직접 매핑 125건이 대분류 안에서 부분 예외 없이 동일한지 사전 검증했다.
2. `TBL_SURFACE_TREAT_GROUP_MATERIAL_MAP`을 만들고 트랜잭션에서 38건을 입력했다.
3. 대분류 12개·`NA` 5건·고아 0건·미매핑 D03 0건·확장 125건·양방향 차이 0건을 확인한 뒤 롤백했다.
4. 동일 시드를 다시 입력해 커밋하고 애플리케이션 조회·빌드·분리 서버 기동을 검증했다.
5. 기존 직접 매핑 테이블은 삭제하지 않고 `TBL_SURFACE_TREAT_MATERIAL_MAP_BAK_20260804`로 이름을 바꿔 125건을 보존했다.
6. 대분류 매핑 38건을 별도 백업한 뒤 `MAP_SEQ` 단일 PK와 업무키 UNIQUE를 추가하고 테이블명을 `TBL_MATERIAL_SURFACE_MAP`으로 변경했다.
7. 재현 SQL과 검증·복구 쿼리는 제품 저장소 `docs/db/20260731_surface_treat_material_map.sql`에 보존했다.

## 구현

- `SystemServiceImpl`: 변경 전 `CASE` 조회 응답을 재사용하지 않도록 `getSessionCodeList` Redis 캐시 키를 `surface-material-group-map-v3`로 갱신
- `system.xml`: 기존 `selectSessionCodeList`가 D03 `ABBR_NM` 대분류의 `MATERIAL_TYPE_CDS`를 집계하고 `M.SYSTEM_ID IN ('BASIC', #{LOGIN_SYSTEM_ID})`으로 환경별 매핑 후보를 조회
- 공통 D03 선택 함수 3곳: D03은 `MATERIAL_TYPE_CDS` 전용, 다른 기준코드는 기존 `REF_CD` 사용
- 탭 공통 스크립트: 버전 없는 구형 공통코드 localStorage 키를 제거하고 새 키에 동일한 스키마 버전 추가
- 제거 완료: Controller·Service·DAO 매핑 관리 메서드, 신규 CRUD/검증 MyBatis statement, 저장 이벤트용 인메모리 캐시 강제 삭제

## 검증

- 개발 DB 상속 매핑 검증 — 통과: 총 38건, 대분류 12개, `NA` 5건, 고아 0건, 미매핑 활성 D03 0건
- 기존 직접 매핑 등가성 — 통과: 하위 D03 확장 125건, 기존→상속 차이 0건, 상속→기존 차이 0건
- 단일 PK·이름 전환 — 통과: `MAP_SEQ` 38건 모두 발급(1~38), 업무키 중복 0건, PK 변경 전 백업과 양방향 차이 0건
- `TBL_CODE.ABBR_NM` 접두어 동기화 — 통과: 대상·백업 각 45건, 변경 후 잔여 불일치 0건, ABBR·변경 이력 외 필드 차이 0건
- `ABBR_NM` 참조 전환 — 통과: 유효하지 않은 D03 ABBR 0건, 신규 시드 예상 38건, 기존 매핑과 양방향 차이 0건, 기존 접두어 방식과 D03별 결과 차이 0건, 하위 확장 125건, 실제 조회 D03 51건 모두 매핑 반환
- 재질별 분포 — 통과: `D02R10=48`, `D02R15=27`, `D02R20=24`, `D02R25=23`, `D02R30=3`
- 대표값 — 통과: `AN0101=AL`, `PL0101=AL/Steel/SUS/비철`, `CO0101=AL/Steel/SUS`, `CL0101·NA0101=5종 전체`
- 범위 축소 전 저장 서비스 임시 단위 테스트 — 역사 기록이며 해당 저장 코드는 현재 제거됨
- Spring 컨텍스트·실제 MyBatis 매퍼 로딩 스모크 — 범위 축소 전 통과
- `system.xml` XML 파싱 — 통과
- 2026-08-06 환경별 매핑 조회 정적 검증 — 통과: `M.SYSTEM_ID IN ('BASIC', #{LOGIN_SYSTEM_ID})` 적용, 대분류별 `EXISTS`·`CASE` 제거, 불필요한 D02 조인 제거 유지, 서버·브라우저 캐시 `v3` 일치. 매핑 테이블에는 `DEL_YN` 컬럼이 없어 잘못된 조건은 추가하지 않았고 바깥 `TBL_CODE A.DEL_YN = 'N'`은 유지했다.
- 2026-08-06 화면 필터 분기 검증 — 통과: D03 신규 매핑 포함 PASS, 신규 매핑 미포함·값 없음은 미표시 PASS, D04 등 다른 기준코드의 `REF_CD` 일치·불일치 PASS, 세 함수 정의 동일, 탭 JavaScript 문법 통과
- 2026-08-07 `refCd` 분기 가독성 변경 검증 — 통과: `isMatched` 지역 선언 3곳, D03 `mapCd` 분기 3곳, 구형 삼항식 0곳, 탭 `node --check`, D03 매핑·`REF_CD` 후퇴 없음·비-D03 `REF_CD` 단위 검증, 전체 Gradle 빌드 통과
- 2026-08-06 최신 `gradlew build -q`, 탭 `node --check`, `git diff --check` — 통과. 기존 deprecated API·unchecked 연산과 LF→CRLF 작업트리 경고는 남아 있으며 이번 변경과 무관해 수정하지 않았다. 최신 `v3` 코드의 서버 재기동·인증 세션 실조회는 아직 수행하지 않았다.
- 2026-08-06 18081 분리 서버 기동 — 통과: Spring 컨텍스트·MyBatis 매퍼 로딩, 루트 HTTP 200, 비로그인 `/json-list` 보안 리다이렉트 HTTP 302 확인 후 에이전트가 시작한 Java 프로세스만 종료하고 포트 해제 확인
- 2026-08-04 대분류 상속 전환 후 기본 빌드 디렉터리의 `gradlew build` — 통과
- 기존 8081을 건드리지 않고 18081에서 새 코드 기동·HTTP 200 확인 후 테스트 서버 종료 — 통과
- 단일 PK·테이블명 전환 후 8081 새 코드 재기동과 루트 HTTP 200 — 통과. 비로그인 `/json-list` 호출은 보안 정책에 따라 HTTP 302여서 인증 세션 기반 실화면 재검증은 이번 전환에서 생략했다.
- 임시 테스트·검증 소스와 격리 빌드 산출물 — 제거 완료

### 2026-08-03 신규 매핑 미반영 진단

- 8081 서버는 2026-08-03 19:09에 시작됐고 실행 중인 class와 `build/resources/main/sqlMaps/system.xml`에 신규 API·`MATERIAL_TYPE_CDS` 조회가 포함되어 있었다.
- 새 Playwright 브라우저 세션에서 `g_code`, 브라우저 `dsCache`, `/json-list` 직접 응답을 각각 확인했다. 세 경로 모두 활성 D03 51개를 반환했지만 `MATERIAL_TYPE_CDS`가 있는 항목은 0개였고 기존 `REF_CD`가 있는 항목은 47개였다.
- 개발 DB 읽기 전용 조회에서는 `BASIC` 매핑 125건, 매핑된 D03 51개, D02 5개가 정상이며 대표값 `AN0101=R10`, `CL0101·NA0101=5종`, `CO0101=3종`, `PL0101=4종`을 확인했다.
- 따라서 SQL·화면 이벤트 문제가 아니라 `SystemServiceImpl.getSessionCodeList`의 Redis 1시간 캐시에 직접 시드 전 응답이 남은 것이 1차 원인이다. 이 응답이 브라우저 `localStorage`의 `dsCache:queryId=systemMapper.selectSessionCodeList`에 30분간 저장되어 2차로 유지된다.
- 화면 함수는 `MATERIAL_TYPE_CDS`가 없으면 호환을 위해 기존 `REF_CD`를 사용하도록 구현되어 있어, 현재 증상이 코드의 후퇴 경로와 정확히 일치한다.
- 진단 중 Python `pymysql` 모듈이 없어 첫 DB 조회는 실행되지 않았고, 기존 MariaDB CLI의 읽기 전용 SELECT로 대체해 위 결과를 확인했다. DB 변경은 없었다.

### 2026-08-03 캐시 무효화 구현

- `SystemServiceImpl.getSessionCodeList`의 Redis 키 앞에 `surface-material-map-v1` 스키마 버전을 추가했다. 기존 Redis 값은 TTL까지 남더라도 새 서버가 읽지 않는다. 2026-08-04 저장 API와 그 `allEntries=true` 무효화는 범위 밖이라 제거했다.
- 탭 공통 스크립트의 `systemMapper.selectSessionCodeList` 브라우저 키에도 같은 스키마 버전을 추가하고, 새 스크립트 로드 시 버전 없는 구형 공통코드 `dsCache` 키만 제거하도록 했다.
- `attr/common`과 `attr/page` 변형은 `dsCache` 대상이 `dataSource.*` 쿼리로 한정되어 세션 공통코드를 브라우저 캐시에 보관하지 않으므로 서버 Redis 키 전환만 적용된다.
- `git diff --check`, `node --check body-script.js`, `gradlew build -q --no-daemon --max-workers=4`를 통과했다. 빌드된 `SystemServiceImpl.class`에도 새 Redis 키가 포함됐다. 저장 이벤트에 추가했던 인메모리 JSON 캐시 강제 삭제 두 곳은 2026-08-04 제거했다.
- 캐시 키 적용 시점에는 8081 JVM이 변경 전인 19:09 시작 프로세스여서 재시작이 필요했다. 이후 사용자가 새 WAR로 서버를 재시작했다.

### 2026-08-03 서버 재시작 후 실화면 검증

- 8081 서버가 새 WAR 생성 시각 19:20:22 이후인 19:23:29에 시작된 프로세스로 교체된 것을 확인했다.
- 새 Playwright 로그인 세션에서 `g_code`, 버전이 적용된 브라우저 `dsCache`, `/json-list` 직접 응답이 모두 활성 D03 51개와 `MATERIAL_TYPE_CDS` 51개를 반환했다.
- 브라우저에는 `__schema=surface-material-map-v1` 공통코드 키가 생성됐고 버전 없는 기존 공통코드 키는 남지 않았다.
- 화면 필터 결과는 `D02R10=48`, `D02R15=27`, `D02R20=24`, `D02R25=23`, `D02R30=3`으로 DB 시드 검증값과 일치했다. 따라서 DB → MyBatis/서비스 → Redis 새 키 → `/json-list` → 브라우저 캐시/`g_code` → 소재별 D03 필터 연결은 완료됐다.

### 2026-08-03 비DB PR 설명과 최신 재검증

- 당시 PR 설명은 코드 9파일 `+266/-10` 기준이었으나, 2026-08-04 사용자 요구에 따라 관리 CRUD를 제거하고 당시 조회 전용 5파일 `+60/-10` 기준으로 MD·HTML을 다시 작성했다.
- `git diff --check`, 탭 스크립트 `node --check`, `gradlew build -q --no-daemon --max-workers=4`를 다시 통과했다.
- 첫 Playwright 재검증은 8081 프로세스가 포트를 수신하면서도 HTTP 응답을 주지 않아 45초 탐색 타임아웃이 발생했고 강제 주소 지정 요청도 10초 타임아웃이었다. 서버 조치 없이 HTTP 302 응답이 39ms로 회복됐으며 원인은 확인하지 못했다.
- 회복 후 같은 검증을 재실행해 매핑 조회 API 125건, D03 51건 중 `MATERIAL_TYPE_CDS` 51건, 소재별 `48/27/24/23/3`, 버전 캐시 존재·구 캐시 부재를 확인했다.

### 2026-08-04 코드 변경 가이드

- 대분류 상속 확정 후 최종 작업트리의 6파일 `+292/-10`을 다시 측정하고 `대분류 테이블 → MyBatis 조회 → 서버 캐시 → 공통·페이지·탭 화면` 순서로 재구성했다. 신규 DAO·DTO·Service·Controller가 필요 없는 이유를 기존 공통코드 경로와 함께 설명했다.
- SQL 신규 파일과 tracked 5파일마다 생략 없는 전체 Git diff를 설명보다 먼저 배치했으며, 문서의 각 diff가 현재 제품 Git diff와 일치하도록 다시 생성했다.
- HTML diff에는 GitHub Files changed와 유사한 양쪽 줄 번호, 삭제 빨강·추가 초록·hunk 강조색과 가로 스크롤을 추가했다. 공통 색상·타이포그래피·단어 보존 규칙은 `templates/standalone-report.html` 정본을 그대로 유지했다.
- 저장 API 역할·빈 매핑·테넌트 코드명 문제는 원인이던 관리용 경로 자체를 제거해 현재 범위의 위험에서 제외됐다.
- PR 설명 MD·HTML은 제목 15개·표 3개·코드 블록 4개·상세 설명 5개, 코드 가이드는 제목 36개·표 3개·코드 블록 19개·상세 설명 6개로 일치한다. 두 폴더 모두 MD·자체완결 HTML 두 파일만 있고 UTF-8 BOM 없음·외부 자산 0·Edge 헤드리스 렌더를 확인했다.
- `git diff --check`, XML 파싱, JavaScript 문법, 관리용 이름 잔존 0건, 기본 전체 빌드와 18081 분리 서버 기동을 확인했다. 제품 6파일의 LF→CRLF 작업트리 경고는 남아 있다.

### 2026-08-04 조회 전용 범위 축소

- 사용자 요구가 “재질 선택 시 매핑 테이블을 통해 연결된 표면처리 표시”까지임을 재확인해 관리용 목록·저장 기능 전체를 제거했다.
- 제거 대상은 Controller 2개 API, Service 조회·저장 계약과 구현, DAO 5개 메서드와 구현, MyBatis 목록·검증·삭제·삽입 statement 5개다.
- 저장 이벤트에만 추가했던 `window.__jsonListCacheClear()` 호출 두 곳도 제거하고, 배포 시 구형 응답 방지에 필요한 Redis·localStorage 스키마 버전만 유지했다.
- 범위 축소 당시 제품 diff는 `SystemServiceImpl.java`, `system.xml`, 공통·페이지 JSP, 탭 JS의 5파일 `+60/-10`이었다. 이후 대분류 상속 SQL·단일 PK·테이블명·`ABBR_NM` 참조 전환과 환경별 `SYSTEM_ID` 조회·캐시 `v3` 전환을 포함한 현재 diff는 6파일 `+302/-10`이다.

## 2026-08-11 테넌트 기준코드 캐시 단순화

- 사용자 지시에 따라 신규 `clearQuery` 탭 전파와 queryId별 generation·부분 삭제 로직을 제거하고 기존 `fnClearDataSourceCache()`의 `clearAll`·`BroadcastChannel('dsCache')` 경로를 그대로 재사용했다.
- 탭 공통 스크립트에는 기존 무효화가 `json-list-cache.js`의 메모리 캐시도 함께 비우도록 호출 연결 9줄만 추가했다. `json-list-cache.js` 자체는 HEAD blob `3d593a570063f704a2f69f7053223852631ad2f2`와 같아 작업트리 변경에서 제외됐다.
- 서버는 신규 저장 API가 기존 `modifyGrid(systemType='CODE')` 경로를 통과하지 않으므로 `SystemServiceImpl`에서 동일한 `getSessionCodeList` Redis 캐시 전체 clear를 저장 성공 후 호출한다. 테넌트별 키 열거와 트랜잭션 동기화 코드는 제거했다.
- 제품 변경은 tracked 8파일 `+321/-11`과 신규 SQL 1파일이다. `node --check`, `git diff --check`, `gradlew build -q`를 통과했으며 빌드에는 기존 deprecation·unchecked 안내만 남았다.
- 전체 Redis 캐시 clear는 테넌트별 선택 무효화보다 캐시 재적재 범위가 넓지만, 드문 관리 토글 저장에 기존 공통코드 저장 정책을 재사용해 코드 경로와 복잡도를 줄이는 선택이다.

## 다음 행동

1. 사용자가 2026-08-07 `refCd` 분기 구조를 최종 확인하면 제품 커밋 여부를 결정한다.
2. 재현 SQL의 원격 커밋 누락을 별도로 검토해 포함 여부를 결정한다.
3. 최신 `v3` 코드로 개발 서버를 재기동하고 인증 세션에서 D03 `MATERIAL_TYPE_CDS`를 재조회한다.
4. 2026-08-05 `ABBR_NM` 참조 전환과 2026-08-06 환경별 `SYSTEM_ID` 조회를 기존 PR 설명·코드 가이드 MD·HTML에 반영한다.
5. 개발 DB의 직접 매핑 백업과 PK 변경 전 백업 테이블은 배포·복구 판단이 끝난 뒤 별도 승인을 받아 제거한다.
6. 향후 관리 화면이 별도로 요청될 때만 구형 `TBL_BASIC_CODE` D03 29개와 런타임 `TBL_CODE(BASIC)` D03 51개의 정본 불일치를 먼저 해소하고 대분류 단위로 설계한다.

## 블로커·위험

- Site Admin 후보 코드 정본이 런타임 51개와 다르지만 현재 조회 전용 기능의 블로커는 아니다. 향후 관리 화면을 별도 구현할 때 해결해야 한다.
- 8081 서버가 문서 작성 중 한 차례 일시적으로 HTTP 무응답 상태가 됐으나 별도 조치 없이 회복됐고 이후 실연동 검증은 통과했다. 같은 현상이 재발하면 서버 로그와 빌드·배포 시점의 상관관계를 진단해야 한다.
- 배포 환경에서는 애플리케이션보다 DB DDL·시드를 먼저 반영해야 한다. 테이블이 없으면 세션 공통코드 조회가 실패한다.
- Gradle 9 비호환 예정인 기존 deprecation 경고와 `EmailRequest` Lombok `@Builder` 경고가 남아 있다. 이번 기능과 직접 관련이 없어 수정하지 않았다.
- 개발 DB CLI는 기존 TLS 인증서 검증 비활성 경고를 출력한다. 이번 테이블 변경과 무관하며 연결 설정 변경은 별도 운영 결정이 필요하다.
- 기존 `application-local.yml`에는 DB·외부 API·JWT 관련 비밀값이 평문으로 존재한다. 이번 범위에서는 수정하지 않았으며 교체와 환경변수 분리는 별도 보안 작업이 필요하다.

## 관련 경로

- `C:\Users\User\Desktop\PR\[08.04 재질표면처리 코드 변경 가이드]`
- `Projects/Tomes-Cloud/docs/db/20260731_surface_treat_material_map.sql`
- `Projects/Tomes-Cloud/src/main/resources/sqlMaps/system.xml`
- `Projects/Tomes-Cloud/src/main/java/com/tomes/service/impl/SystemServiceImpl.java`
- `Projects/Tomes-Cloud/src/main/webapp/WEB-INF/views/attr/common/body-script.jsp`
- `Projects/Tomes-Cloud/src/main/webapp/resource/modules/attr/tabs/body-script.js`
