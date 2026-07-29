# 기준정보 dataSource 조회 — 서버 Redis 캐시 추가 구현/테스트 보고

> 대상: %클라우드(Tomes-Cloud), 브랜치 `feature_caching_2606`
> 작성: 2026-06-22 · **커밋 안 함**(사용자 검토 후 적용 결정용)
> 변경: 4파일 / +134줄 / 삭제 0 · answer-reviewer 검증 반영

---

## 1. 개요

기존 분석에서 추천한 기준정보 조회들에 **서버 Redis `@Cacheable`**를 추가하고, **모든 변경 지점에 evict**를 배선했다.
기존 패턴(`getSessionCodeList` 위임)을 그대로 따라, `InnodaleServiceImpl.getList()`가 queryId별로 새 캐시 메서드에 위임한다.

**evict 가능 여부에 따라 4개 캐시군으로 분리**(과잉 무효화 최소화). 캐시 value 정식명은 `com:tomes:service:impl:SystemServiceImpl:` 접두사 + 아래 이름:

| 캐시군(value 접미) | 포함 조회 | 무효화(evict) |
|---|---|---|
| `dataSourceCompanyList` | 거래처·발주처·담당자·외주처3종·selectCompList | 저장: `managerSystemCompany`(@CacheEvict) / 삭제·범용쓰기: `create·update·remove`(프로그램적) |
| `dataSourceEquipList` | 설비(getEquipList) | 저장: `managerEquip`(@CacheEvict) / 삭제·범용쓰기: `create·update·remove`(프로그램적) |
| `dataSourceWarehouseList` | 창고(getLocationListWithWarehouse) | **앱 내 변경경로 없음 → TTL(1h)만** |
| `dataSourceSystemList` | 시스템(selectSystemList, 전역) | **신규 시스템 드묾 → TTL(1h)만** |

TTL은 전부 기존 `everyHour`(1시간) 재사용.

---

## 2. 적용 목록 (읽기 쿼리 → 캐시 키)

| 읽기 queryId | 캐시군 | 캐시 키 구성 | 테넌트 키 |
|---|---|---|---|
| dataSource.getBusinessCompanyList | company | queryId+sid | LOGIN_SYSTEM_ID |
| dataSource.getOrderCompanyList | company | queryId+sid+CHARGE_USER_ID | LOGIN_SYSTEM_ID |
| dataSource.getCompanyStaffList | company | queryId+sid+COMP_CD | LOGIN_SYSTEM_ID |
| dataSource.getOutsourceCompanyList | company | queryId+sid | LOGIN_SYSTEM_ID |
| dataSource.getOutsourceMaterialCompanyList | company | queryId+sid | LOGIN_SYSTEM_ID |
| dataSource.getOutsourceProcessCompanyList | company | queryId+sid | LOGIN_SYSTEM_ID |
| dataSource.getPopOutInProcessCompanyList | company | queryId+sid+POP_POSITION | LOGIN_SYSTEM_ID |
| dataSource.selectCompList | company | queryId+SEL_SYSTEM_ID | SEL_SYSTEM_ID |
| dataSource.getEquipList | equip | queryId+sid | LOGIN_SYSTEM_ID |
| dataSource.getLocationListWithWarehouse | warehouse | queryId+sid+WAREHOUSE_CD | LOGIN_SYSTEM_ID |
| dataSource.selectSystemList | system | queryId(전역) | 없음(테넌트 필터 없는 쿼리) |

> **테넌트 안전:** 테넌트 키(LOGIN/SEL_SYSTEM_ID)가 없으면 캐시를 우회하고 기존 DAO 경로로 떨어진다 → 시스템 간 데이터 누출 차단. `selectSystemList`는 쿼리 자체가 `WHERE 1=1`(전역)이라 전역 키가 안전.

---

## 3. 변경 파일 (4개, 순수 추가)

| 파일 | 추가 내용 |
|---|---|
| `service/SystemService.java` (+9) | 캐시 메서드 4개 시그니처 |
| `service/impl/SystemServiceImpl.java` (+39) | 캐시 value 상수 4개 + `@Cacheable` 메서드 4개 + `managerSystemCompany`에 `@CacheEvict(company)` |
| `service/impl/InnodaleServiceImpl.java` (+84) | `getList()` queryId별 캐시 위임 + 키 빌더 + **범용 쓰기(create/update/remove)에 queryId 기반 프로그램적 evict** |
| `service/impl/MachineServiceImpl.java` (+2) | `managerEquip`에 `@CacheEvict(equip)` |

**MyBatis queryId·SQL은 일절 변경 없음**(CRITICAL 규칙 준수, `sqlMaps/` diff 0). 순수 추가(삭제 0).

---

## 4. evict 커버리지 (삭제 포함 — "완벽" 확인)

| 변경 경로 | 실제 동작 | evict 방식 | 커버 |
|---|---|---|---|
| 거래처 저장 | `/managerSystemCompany` → managerSystemCompany | @CacheEvict(company) | ✅ |
| 거래처 삭제 | 삭제버튼 → `/json-update`(deleteCompanyMaster) → update() | 프로그램적(company) | ✅ |
| 설비 저장 | `/managerEquip` → managerEquip | @CacheEvict(equip) | ✅ |
| 설비 삭제 | 삭제버튼 → `/json-update`(deleteMachineMaster) → update() | 프로그램적(equip) | ✅ |

> 삭제는 Java 메서드 직접 호출이 아니라 JSP가 queryId를 세팅해 `/json-update`로 보내는 방식(`system/admin company-master.jsp`, `machine-manage.jsp`에 존재). 이 경로는 `InnodaleServiceImpl.update()`를 타므로, 거기에 queryId 기반 evict를 추가해 커버했다.

---

## 5. 검증 결과

| 항목 | 결과 | 비고 |
|---|---|---|
| 컴파일 (`gradlew compileJava`) | ✅ 통과 | 기존 deprecation/unchecked 경고만, 신규 오류 없음 |
| 전체 빌드 (`gradlew build`) | ✅ 통과 (exit 0) | WAR 패키징 성공 |
| 단위 테스트 | — | 프로젝트에 test 소스 0개(원래 없음) |
| **런타임 캐시 적중/evict 실측** | ❌ **미실행** | 아래 사유 — 실측한 적 없음 |

**런타임 미실행 사유(정직 보고):** DB·Redis가 원격 공유 dev 서버(`121.165.20.66`)이고 로컬 Redis가 없음. 실측하려면 ① 앱 기동(포트 80) ② 로그인 세션 ③ 공유 Redis 키 관찰이 필요해, 공유 인프라에 영향을 줄 수 있어 이 세션에서 임의 실행하지 않음. → **7번 수동 절차 참고.**

---

## 6. 로직 검증 (정적 분석)

- **위임 동작:** `getList`(다른 빈) → `systemService.getCachedXxx`(프록시) → `@Cacheable` 적용. `managerSystemCompany`/`managerEquip`은 컨트롤러 호출(프록시) → `@CacheEvict` 적용. 자가호출 문제 없음.
- **키 유일성·테넌트 안전:** 키에 queryId + 테넌트 + 동적파라미터 포함, 테넌트 키 없으면 캐시 우회.
- **삭제 커버:** 범용 쓰기 chokepoint(create/update/remove)에서 queryId가 회사/설비 테이블 변경이면 해당 그룹 clear. 전용 저장의 @CacheEvict와 중복될 수 있으나 무해.

---

## 7. 런타임 수동 검증 절차 (적용 결정 시)

1. 앱 기동 후 로그인(세션에 LOGIN_SYSTEM_ID 확보).
2. 드롭다운 화면 진입 → 새로고침. 2회차에 `/json-list`(예: getEquipList) 서버 쿼리가 안 나가면 적중.
3. Redis 키 확인(정식 value명 + `::` + 키):
   `com:tomes:service:impl:SystemServiceImpl:dataSourceEquipList::dataSource.getEquipList|sid=...`
4. 거래처 **저장** → 거래처 드롭다운 즉시 갱신(company군 evict), 설비 캐시는 유지 확인.
5. 거래처 **삭제** → 마찬가지로 company군 evict 동작(서버 캐시 stale 없음) 확인.
6. 설비 저장/삭제 → equip군 evict 확인.
7. (선택) QA 자동화: `cd %테스트 && python -m qa_agent.agent_run --row {TC} --skip-global-seeds`.

---

## 8. 잔존 리스크 (사용자 검토)

1. **창고·시스템은 TTL(1h)만** — 앱 내 변경 경로가 없어 evict 미배선. 외부/배치로 변경되면 최대 1시간 stale. (신규 시스템 signup 경로에 evict 추가는 선택 가능)
2. **그리드 CRUD 경로** — 회사/설비를 만약 범용 그리드 저장(`modifyGrid`/`CRUDGrid`, innodaleDao 직접호출)으로 변경하는 화면이 있다면 그 경로엔 evict가 없음. 현재 회사/설비 마스터는 전용 폼+`/json-update` 삭제를 쓰는 것으로 확인됨(저위험). 추가 확인 권장.
3. **타입 round-trip(서버 Redis 한정)** — JSON(GenericJackson2Json) 캐싱으로 CAST 안 한 숫자 `CODE_CD`가 캐시 히트/미스 간 타입이 달라질 수 있음(Long↔Integer). 드롭다운은 문자열 `value`/`text`를 주로 써 영향 낮을 것으로 추정되나 QA 권장.
4. **evict 타이밍** — `@CacheEvict`는 트랜잭션 커밋 직전 실행(기본). 동시성 극단 상황의 미세 race(일반 비용).

---

## 9. 사용자 결정 사항

- **적용(커밋) 여부** — 현재 워킹트리에만 있고 커밋 안 함.
- **창고/시스템 TTL-only** 수용 여부(리스크 #1).
- **그리드 CRUD 경로 확인**(리스크 #2) 필요 여부.
