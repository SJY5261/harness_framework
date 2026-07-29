# 기준정보 dataSource 조회 - 서버 Redis 캐시 추가 (커밋 반영본)

> 대상: %클라우드(Tomes-Cloud)
> 커밋: b504ace "Redis 캐시 쿼리 추가 반영" (sjy5261, 2026-06-23 10:17)
>   - 소속 브랜치: feature_caching_2606 + Danga_estimate (두 브랜치가 동일 HEAD).
>   - (정정) 이전 본문이 인용한 71f034b는 같은 내용의 dangling 커밋(어느 브랜치에도 미부착)이었음.
> 변경: service 계층 4파일 / +125줄 / 삭제 0 (순수 추가)
> 작성: 2026-06-23. 본 문서는 실제 커밋 diff 기준(2026-06-22 계획 리포트의 갱신본).
> 정정: 2026-06-23. 커밋 해시 + DS_WAREHOUSE/DS_SYSTEM "변경 경로 없음" 서술 교정(아래 3.2/8 참조).

---

## 1. 개요

기준정보 드롭다운/그리드용 dataSource 조회들에 서버 Redis `@Cacheable`를 추가하고,
변경 지점에 evict를 배선했다. 기존 패턴(getSessionUserList/getSessionCodeList 위임)을 따라
`InnodaleServiceImpl.getList()`가 queryId별로 `SystemService`의 캐시 메서드에 위임한다.

- TTL: 기존 `everyHour` CacheManager(1시간) 재사용.
- queryId/SQL(sqlMaps)은 일절 변경 없음(CRITICAL 규칙 준수). 순수 추가.

엔티티 그룹별로 캐시 value를 4개로 분리(evict 범위 최소화):

| 캐시 value 상수 | value 이름(접미) | 무효화(evict) |
|---|---|---|
| DS_COMPANY | dataSourceCompanyList | managerSystemCompany @CacheEvict + 범용쓰기 프로그램적 |
| DS_EQUIP | dataSourceEquipList | managerEquip @CacheEvict + 범용쓰기 프로그램적 |
| DS_WAREHOUSE | dataSourceWarehouseList | evict 미배선(누락) -> TTL(1h)만. **변경 경로는 있음**(3.2 참조) |
| DS_SYSTEM | dataSourceSystemList | evict 생략(변경 드물어) -> TTL(1h)만. 변경 경로는 있음 |

(접두사 전체: `com:tomes:service:impl:SystemServiceImpl:` + 위 접미)

---

## 2. 캐시 적용 대상 (커밋 실물 기준)

`InnodaleServiceImpl.getList()`가 아래 queryId일 때만 캐시 메서드로 위임, 그 외엔 기존 DAO 직조회.

### 2.1 거래처/외주처군 (DS_COMPANY) - 6개 queryId
`DS_COMPANY_QUERIES` Set에 포함된 것만:
- dataSource.getBusinessCompanyList
- dataSource.getOrderCompanyList
- dataSource.getOutsourceCompanyList
- dataSource.getOutsourceMaterialCompanyList
- dataSource.getOutsourceProcessCompanyList
- dataSource.getPopOutInProcessCompanyList

캐시 키: `queryId + "|sid=" + systemId + "|cu=" + CHARGE_USER_ID + "|pp=" + POP_POSITION`
조건: queryId가 위 집합에 속하고 systemId(LOGIN_SYSTEM_ID)가 비어있지 않을 때.

### 2.2 설비 (DS_EQUIP)
- dataSource.getEquipList
- 키: `"dataSource.getEquipList|sid=" + systemId` (systemId 필수)

### 2.3 창고 위치 (DS_WAREHOUSE)
- dataSource.getLocationListWithWarehouse
- 키: `"...|sid=" + systemId + "|wh=" + WAREHOUSE_CD` (systemId 필수)

### 2.4 시스템 목록 (DS_SYSTEM) - 전역
- dataSource.selectSystemList
- 키: `"dataSource.selectSystemList"` (고정, 테넌트 가드 없음 - 쿼리 자체가 전역 WHERE 1=1)

### 2.5 캐시 제외(의도적) - 06-22 계획 대비 차이
- dataSource.getCompanyStaffList(담당자): COMP_CD별로 키가 잘게 쪼개져 적중률 낮음 -> 제외(DB 직조회 유지).
- dataSource.selectCompList: 커밋본 DS_COMPANY_QUERIES에 미포함 -> 캐시 안 됨(기존 경로).

> 2026-06-22 계획 리포트는 위 둘을 company군에 넣었으나, 커밋본은 둘 다 제외했다(더 보수적).

---

## 3. 무효화(evict) 커버리지

| 변경 경로 | 동작 | evict 방식 | 대상 |
|---|---|---|---|
| 거래처 저장 | managerSystemCompany | @CacheEvict | DS_COMPANY |
| 설비 저장 | managerEquip | @CacheEvict | DS_EQUIP |
| 범용 쓰기 | create/update/remove | 프로그램적(queryId 검사) | DS_COMPANY / DS_EQUIP |

### 3.1 범용 쓰기 evict 로직 (InnodaleServiceImpl)
`create()/update()/remove()` 끝에서 `evictDataSourceCacheByWriteQueryId(queryId)` 호출:
- queryId에 `CompanyMaster` / `CompanyStaff` / `CompanyType` / `CompanyAllType` 포함 -> DS_COMPANY clear
- queryId에 `MachineMaster` 포함 && `History` 미포함 -> DS_EQUIP clear

이유: 회사/설비 삭제(deleteCompanyMaster/deleteMachineMaster)는 전용 메서드가 아니라
`/json-update` -> `update()` 경로를 타므로, 여기서 evict해야 stale을 막는다.
전용 저장의 @CacheEvict와 중복될 수 있으나 무해.

### 3.2 evict 없는 그룹 (정정 - 둘 다 "변경 경로 없음"이 아님)

원래 코드 주석/이전 본문은 창고를 "앱 내 변경 경로 없음"이라 했으나 **부정확**하다. 둘 다 변경 경로는 존재하고, evict만 안 걸려 있다.

- **DS_WAREHOUSE (실제 결함):**
  - 변경 경로 존재: `material.xml`의 `insertUpdateCommonWarehouseManage`(INSERT ... ON DUPLICATE KEY UPDATE),
    `deleteCommonWarehouseManage`(DELETE). 공통 창고 관리 화면(`webapp/resource/modules/attr/tabs/bottom.js` 2534/2545행)에서 사용.
  - 이 경로는 범용 쓰기(create/update/remove)를 타므로 `evictDataSourceCacheByWriteQueryId`가 호출되나,
    패턴이 `Company*`/`Machine*`만 매칭 -> **창고 queryId는 안 잡혀 DS_WAREHOUSE evict가 건너뛰어짐.**
  - 결과: 창고 위치 추가/수정/삭제 후 `getLocationListWithWarehouse` 드롭다운이 **최대 1시간 stale.**
  - (참고) 화면의 `fnClearDataSourceCache`는 클라이언트 localStorage만 비우고 서버 Redis는 안 건드림.
  - 권고: `evictDataSourceCacheByWriteQueryId`에 창고 패턴(예: queryId에 `WarehouseManage` 포함 시 DS_WAREHOUSE clear)
    추가, 또는 창고 저장/삭제 경로에 `@CacheEvict(DS_WAREHOUSE)`.

- **DS_SYSTEM (의도적 트레이드오프):**
  - 변경 경로 존재: `updateSystem`(SystemController), `updateSystemType`(CustomerController),
    `insertMainSystem`(CustomerServiceImpl, 신규 시스템 등록).
  - evict 미배선은 "시스템 변경이 드물어서"의 의식적 선택. 시스템 추가/수정 후 admin 시스템 목록이 최대 1시간 stale.
    신선도가 중요하면 `updateSystem` 등에 `@CacheEvict(DS_SYSTEM)` 추가 가능.

---

## 4. 멀티테넌트 안전

- 캐시 키에 테넌트 식별자(SYSTEM_ID) 포함. systemId가 비어있으면 캐시를 우회하고
  기존 DAO 경로로 떨어져 시스템 간 데이터 누출 차단.
- selectSystemList만 예외(전역 쿼리, WHERE 1=1)라 전역 키 안전.
- `@Cacheable(unless = "#result == null")` 로 null 결과는 캐싱하지 않음.

---

## 5. 변경 파일 (4개, 순수 추가)

| 파일 | 추가 내용 |
|---|---|
| service/SystemService.java (+9) | 캐시 위임 메서드 4개 시그니처 |
| service/impl/SystemServiceImpl.java (+39) | 캐시 value 상수 4개 + @Cacheable 메서드 4개 + managerSystemCompany에 @CacheEvict(DS_COMPANY) |
| service/impl/InnodaleServiceImpl.java (+75) | getList queryId별 위임 + 키 빌더(nz) + create/update/remove 프로그램적 evict |
| service/impl/MachineServiceImpl.java (+2) | managerEquip에 @CacheEvict(DS_EQUIP) |

---

## 6. 검증 상태

- 컴파일/빌드: 기존 리포트(2026-06-22) 시점 gradlew build PASS 확인됨(이후 동일 로직 커밋).
- 런타임 캐시 적중/evict 실측: getUserList/selectSessionCodeList 계열은 과거 세션에서 bo.log로
  적중/무효화 end-to-end 검증됨(HANDOFF 2026-06-18/19). 이번 dataSource 4군의 적중/evict
  런타임 실측은 별도 수행 권장(7번 절차).

---

## 7. 런타임 수동 검증 절차

1. 로그인(세션에 LOGIN_SYSTEM_ID 확보).
2. 드롭다운 화면 진입 후 새로고침 -> 2회차에 해당 /json-list(예: getEquipList) DB 쿼리가
   안 나가면 서버 캐시 적중.
3. Redis 키 확인(value명 + "::" + key):
   `com:tomes:service:impl:SystemServiceImpl:dataSourceEquipList::dataSource.getEquipList|sid=...`
4. 거래처 저장/삭제 -> DS_COMPANY evict, 설비 캐시는 유지 확인.
5. 설비 저장/삭제 -> DS_EQUIP evict 확인.

---

## 8. 잔존 리스크

1. 창고/시스템은 evict 미배선이라 TTL(1h)만 - **앱 내 변경(창고 위치 관리, 시스템 등록/수정)** 후에도
   최대 1시간 stale. 특히 DS_WAREHOUSE는 변경 경로가 있는데 패턴 미일치로 evict가 빠진 결함(3.2 참조).
2. 타입 round-trip(서버 Redis 한정): JSON 직렬화로 CAST 안 한 숫자 CODE_CD의 타입이
   히트/미스 간 달라질 수 있음(Long/Integer). 드롭다운은 문자열 value/text를 주로 써 영향 낮을
   것으로 추정되나 QA 권장.
3. evict 타이밍: @CacheEvict는 트랜잭션 커밋 직전 실행(기본). 동시성 극단의 미세 race(일반 비용).

---

## 9. 참고

- 이 캐시는 메인 로드 "체감 속도"와는 사실상 무관(HANDOFF 측정 결론). 실익은
  다사용자 DB 부하 분산/동시성 보호.
- 메인 로드 체감은 별건 "정적 리소스 캐시"(static_resource_cache_2026-06-23.md) 수정이 담당.
