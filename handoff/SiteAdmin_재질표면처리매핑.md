# Site Admin 재질-표면처리 매핑

_최종 갱신: 2026-08-03 / 상태: 진행 중_

## 현재 상태

- 사용자가 요청한 1~7단계(DB 구조·시드·백엔드·공통코드 응답·필터·캐시·검증)와 재시작 후 업무 화면 실동작 검증을 완료했다. Site Admin 화면 구현은 이번 범위에 포함하지 않았다.
- 요구사항 정본은 `C:\Users\User\Desktop\Downloads\Site Admin 화면설계서_260723.pptx`의 15번 슬라이드다.
- 개발 DB `smd`에 `TBL_SURFACE_TREAT_MATERIAL_MAP`을 신규 생성하고 `BASIC` D03 51개에 대한 D02 매핑 125건을 반영했다.
- 개발 DB의 활성 공통코드는 `TBL_CODE(BASIC)` 기준 D02 5개·D03 51개뿐이며 로그인 테넌트 소속 D02·D03 코드는 없다. 저장 API는 요청에 `SYSTEM_ID`가 없으면 `BASIC`을 대상으로 하고, 명시값은 `BASIC` 또는 로그인 테넌트만 허용한다.
- 기존 업무 테이블의 재질·표면처리 동시 입력은 19,221건이다. 이 중 18,954건은 구형 `D03Rxx`, 75건은 신형 의미 코드이며, 신형 75건 중 슬라이드 15 매핑과 불일치하는 조합이 13건이다. 기존 업무 데이터는 변경하지 않았다.
- 제품 저장소는 `feature-materialmap-0803`이며, 2026-08-03에 사용자 지시에 따라 다른 기능 작업만 작업 단위별 stash로 분리했다. 현재 기능 변경은 이번 재질-표면처리 관련 수정 9파일과 신규 SQL 1파일만 남았고, `.claude/settings*.json`과 `shell/runDev.local.bat`은 로컬 환경 파일이라 작업트리에 유지했다. 제품 커밋은 만들지 않았다.
- 2026-08-03 실제 화면에서 소재종류 선택 후 신규 매핑이 아니라 기존 `REF_CD` 매핑이 표시되는 현상을 재현했다. 직접 DB 시드 전 Redis 응답과 브라우저 30분 캐시가 원인이었으며, 서버·브라우저 공통코드 캐시 키를 `surface-material-map-v1`으로 전환하고 전체 빌드를 통과했다. 이후 재시작된 8081 서버의 새 브라우저 세션에서 신규 매핑 응답과 소재별 필터를 확인했다.

## 2026-08-03 Git 작업 분리

- 단가검토: `24c94b4db0dfafebf70f39d1bd2b0940bc8a376d`
- KAN-63 작업지시 재확정 예외: `ca1524ddac4f19964336418d77f0344ee62a6ec4`
- KAN-6 작업상세 가공확정·진행상태 제거: `942c7f7ad80b161f5609fa34f24d4f9f1d7ff1aa`
- Claude 로컬 설정과 로컬 개발 실행 배치는 stash 대상에서 제외하고 원래 작업트리에 복원했다.
- stash 분리 전후 재질-표면처리 tracked diff 해시는 `791a5b1777b6d977e25a3cd7dc5fd9d4cc244339`, 신규 SQL SHA-256은 `28D12DF926AF874E965B598C5B97A67F779EEAC1385AB1F806EF1F0BC11FF58E`로 동일하다.
- 현재 작업트리에는 staged 파일이 없고, 기능 변경은 재질-표면처리 관련 파일만 남아 있다.

## 목표·완료 조건

- 완료: 슬라이드 15 매트릭스를 정규화된 다대다 테이블과 재현 가능한 SQL로 정의한다.
- 완료: 개발 DB에 매핑을 반영하고 건수·고아 코드·미매핑 표면처리·재질별 분포를 검증한다.
- 완료: 매핑 조회·저장 API, 입력 코드 검증, 트랜잭션, 서버·브라우저 공통코드 캐시 무효화를 구현한다.
- 완료: 기존 D03 선택 함수가 `MATERIAL_TYPE_CDS`를 우선 사용하고 구 캐시에는 `REF_CD`로 후퇴하도록 한다.
- 완료: 재시작된 서버의 새 브라우저 세션에서 업무 화면 공통코드 응답과 소재별 표면처리 필터를 검증한다.
- 미완료: Site Admin 화면의 적용소재 편집 UI는 8단계 이후 작업이다.

## 결정

- 별도 `TBL_SURFACE_TREAT_MATERIAL_MAP` 사용 — 표면처리 하나에 여러 재질이 연결되므로 `ETC2` CSV보다 PK·인덱스·검증 가능한 다대다 구조가 적합하다.
- 슬라이드에 없는 `NA` 계열은 5개 재질 전체 허용으로 시드 — 앞서 사용자에게 제안한 기본값이며, D03 51개 전체가 미매핑 없이 동작하도록 했다.
- `BASIC` 매핑을 기본값으로 사용하고 같은 표면처리의 테넌트 매핑이 있으면 이를 우선하는 조회 구조를 채택했다.
- 저장 대상은 `BASIC` 또는 로그인 테넌트로 제한 — 임의 테넌트 쓰기를 막고, 개발 DB의 실제 공통코드 소속이 `BASIC`뿐인 점을 반영했다.
- 기존 업무 데이터는 자동 이관하지 않음 — 구형 코드 18,954건과 신형 불일치 13건은 업무 의미 확인 없이 변경하면 데이터 의미가 달라질 수 있다.
- D03 필터는 신규 `MATERIAL_TYPE_CDS` 우선, 값이 없으면 기존 `REF_CD` 사용 — 배포 직후 남아 있는 구 브라우저 캐시와의 호환성을 유지한다.

## DB 변경

### 대상과 환경

- 환경: 개발 DB `smd`, MariaDB 10.11.15
- 신규 테이블: `TBL_SURFACE_TREAT_MATERIAL_MAP`
- 기존 업무 테이블의 컬럼·인덱스·데이터는 변경하지 않았다.

### 변경 전 → 변경 후

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| 재질-표면처리 관계 | 전용 테이블 없음, D03 `ETC2` 사용 0건 | `SYSTEM_ID + SURFACE_TREAT_CD + MATERIAL_TYPE_CD` 복합 PK |
| 역방향 조회 | 전용 인덱스 없음 | `IX_STMM_MATERIAL(SYSTEM_ID, MATERIAL_TYPE_CD, SURFACE_TREAT_CD)` |
| 기준 매핑 | 없음 | `BASIC` 125건 |

### 실행 순서·복구

1. 대상 테이블 부재와 D02·D03 기준코드를 사전 확인했다.
2. 신규 테이블이므로 보존할 기존 대상 데이터가 없어 별도 테이블 백업은 만들지 않았다.
3. `CREATE TABLE`을 실행했다. MariaDB DDL 자동 커밋 특성을 확인했다.
4. 시드는 트랜잭션에서 입력하고 무결성 검증 후 커밋했다.
5. 재현 SQL과 검증 쿼리는 제품 저장소 `docs/db/20260731_surface_treat_material_map.sql`에 보존했다.
6. 전체 기능 복구는 테이블이 이번 작업에서 신규 생성된 환경에서만 `DROP TABLE TBL_SURFACE_TREAT_MATERIAL_MAP`을 실행한다. 실행 시 매핑 125건이 모두 삭제되므로 배포 후 운영 데이터가 추가된 환경에서는 선백업이 필요하다.

## 구현

- `SystemController`: `/getSurfaceTreatMaterialMapList`, `/saveSurfaceTreatMaterialMap` POST API
- `SystemServiceImpl`: CSV·배열·컬렉션 입력 정규화, D02·D03 활성 코드 검증, 범위 제한, 삭제 후 재입력 트랜잭션, Redis 공통코드 캐시 전체 무효화
- `system.xml`: 매핑 CRUD, `selectSessionCodeList.MATERIAL_TYPE_CDS`, `BASIC` 후퇴 조회
- 공통 D03 선택 함수 3곳: 매핑 기반 필터와 `REF_CD` 호환 후퇴
- 탭 공통 스크립트: 로컬스토리지·BroadcastChannel뿐 아니라 인메모리 JSON 목록 캐시도 함께 제거

## 검증

- 개발 DB 매핑 검증 — 통과: 총 125건, 고아 0건, 미매핑 활성 D03 0건
- 재질별 분포 — 통과: `D02R10=48`, `D02R15=27`, `D02R20=24`, `D02R25=23`, `D02R30=3`
- 대표값 — 통과: `AN0101=AL`, `PL0101=AL/Steel/SUS/비철`, `CO0101=AL/Steel/SUS`, `CL0101·NA0101=5종 전체`
- 서비스 임시 단위 테스트 — 통과: 기본 `BASIC` 저장·반복 파라미터 배열 중복 제거, 자기 테넌트 허용, 타 테넌트 거부 3건
- Spring 컨텍스트·실제 MyBatis 매퍼 로딩 스모크 — 통과
- `system.xml` XML 파싱 — 통과
- 격리 빌드 디렉터리의 `gradlew build` — 통과
- 기본 `build/resources`를 사용하는 재검증 — 실패: 실행 중인 8081 개발 서버가 `message-common.properties`를 점유해 Gradle stale output 삭제가 불가능했다. 서버를 강제 종료하지 않고 격리 빌드로 대체했다.
- 임시 테스트·검증 소스와 격리 빌드 산출물 — 제거 완료

### 2026-08-03 신규 매핑 미반영 진단

- 8081 서버는 2026-08-03 19:09에 시작됐고 실행 중인 class와 `build/resources/main/sqlMaps/system.xml`에 신규 API·`MATERIAL_TYPE_CDS` 조회가 포함되어 있었다.
- 새 Playwright 브라우저 세션에서 `g_code`, 브라우저 `dsCache`, `/json-list` 직접 응답을 각각 확인했다. 세 경로 모두 활성 D03 51개를 반환했지만 `MATERIAL_TYPE_CDS`가 있는 항목은 0개였고 기존 `REF_CD`가 있는 항목은 47개였다.
- 개발 DB 읽기 전용 조회에서는 `BASIC` 매핑 125건, 매핑된 D03 51개, D02 5개가 정상이며 대표값 `AN0101=R10`, `CL0101·NA0101=5종`, `CO0101=3종`, `PL0101=4종`을 확인했다.
- 따라서 SQL·화면 이벤트 문제가 아니라 `SystemServiceImpl.getSessionCodeList`의 Redis 1시간 캐시에 직접 시드 전 응답이 남은 것이 1차 원인이다. 이 응답이 브라우저 `localStorage`의 `dsCache:queryId=systemMapper.selectSessionCodeList`에 30분간 저장되어 2차로 유지된다.
- 화면 함수는 `MATERIAL_TYPE_CDS`가 없으면 호환을 위해 기존 `REF_CD`를 사용하도록 구현되어 있어, 현재 증상이 코드의 후퇴 경로와 정확히 일치한다.
- 진단 중 Python `pymysql` 모듈이 없어 첫 DB 조회는 실행되지 않았고, 기존 MariaDB CLI의 읽기 전용 SELECT로 대체해 위 결과를 확인했다. DB 변경은 없었다.

### 2026-08-03 캐시 무효화 구현

- `SystemServiceImpl.getSessionCodeList`의 Redis 키 앞에 `surface-material-map-v1` 스키마 버전을 추가했다. 기존 Redis 값은 TTL까지 남더라도 새 서버가 읽지 않으며, 저장 API의 `allEntries=true` 무효화 범위는 그대로 유지된다.
- 탭 공통 스크립트의 `systemMapper.selectSessionCodeList` 브라우저 키에도 같은 스키마 버전을 추가하고, 새 스크립트 로드 시 버전 없는 구형 공통코드 `dsCache` 키만 제거하도록 했다.
- `attr/common`과 `attr/page` 변형은 `dsCache` 대상이 `dataSource.*` 쿼리로 한정되어 세션 공통코드를 브라우저 캐시에 보관하지 않으므로 서버 Redis 키 전환만 적용된다.
- `git diff --check`, `node --check body-script.js`, `gradlew build -q --no-daemon --max-workers=4`를 통과했다. 빌드된 `SystemServiceImpl.class`에도 새 Redis 키가 포함됐다.
- 캐시 키 적용 시점에는 8081 JVM이 변경 전인 19:09 시작 프로세스여서 재시작이 필요했다. 이후 사용자가 새 WAR로 서버를 재시작했다.

### 2026-08-03 서버 재시작 후 실화면 검증

- 8081 서버가 새 WAR 생성 시각 19:20:22 이후인 19:23:29에 시작된 프로세스로 교체된 것을 확인했다.
- 새 Playwright 로그인 세션에서 `g_code`, 버전이 적용된 브라우저 `dsCache`, `/json-list` 직접 응답이 모두 활성 D03 51개와 `MATERIAL_TYPE_CDS` 51개를 반환했다.
- 브라우저에는 `__schema=surface-material-map-v1` 공통코드 키가 생성됐고 버전 없는 기존 공통코드 키는 남지 않았다.
- 화면 필터 결과는 `D02R10=48`, `D02R15=27`, `D02R20=24`, `D02R25=23`, `D02R30=3`으로 DB 시드 검증값과 일치했다. 따라서 DB → MyBatis/서비스 → Redis 새 키 → `/json-list` → 브라우저 캐시/`g_code` → 소재별 D03 필터 연결은 완료됐다.

## 다음 행동

1. 신형 의미 코드 불일치 13건을 새 매핑으로 이관할지, 기존값 예외로 인정할지 결정한다.
2. Site Admin 화면이 참조하는 구형 `TBL_BASIC_CODE` D03 29개와 런타임 `TBL_CODE(BASIC)` D03 51개의 정본 불일치를 해소한다.
3. 8단계로 Site Admin 적용소재 편집 UI를 구현하고 저장 성공 시 브라우저 캐시 무효화를 호출한다.

## 블로커·위험

- 기존 19,221개 동시 입력 중 대부분이 구형 D03 코드이며, 신형 코드도 13건이 새 매핑과 불일치한다. UI 적용 전에 표시·수정 정책 결정이 필요하다.
- Site Admin 후보 코드 정본이 런타임 51개와 다르다. 이 상태에서 화면만 구현하면 일부 코드가 누락될 수 있다.
- 배포 환경에서는 애플리케이션보다 DB DDL·시드를 먼저 반영해야 한다. 테이블이 없으면 세션 공통코드 조회가 실패한다.
- Gradle 9 비호환 예정인 기존 deprecation 경고와 `EmailRequest` Lombok `@Builder` 경고가 남아 있다. 이번 기능과 직접 관련이 없어 수정하지 않았다.

## 관련 경로

- `Projects/Tomes-Cloud/docs/db/20260731_surface_treat_material_map.sql`
- `Projects/Tomes-Cloud/src/main/resources/sqlMaps/system.xml`
- `Projects/Tomes-Cloud/src/main/java/com/tomes/service/impl/SystemServiceImpl.java`
- `Projects/Tomes-Cloud/src/main/java/com/tomes/controller/SystemController.java`
- `Projects/Tomes-Cloud/src/main/webapp/resource/modules/attr/tabs/body-script.js`
