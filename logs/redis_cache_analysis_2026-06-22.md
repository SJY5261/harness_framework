# Redis 캐시 도입 분석 — 기준정보 조회 쿼리

> 대상: `data_source.xml`의 기준정보 조회 8개 (`common.selectCodeList` 제외)
> 작성: 2026-06-22 · answer-reviewer 검증 완료(REVIEW-VERIFIED)
> 질문 범위: **서버 Redis 캐시** 추가 시 개선/개악 + 추천

---

## 1. 먼저 — "적중률(hit rate)"이란

전체 조회 요청 중 **DB까지 안 가고 캐시에서 응답한 비율**.

- **적중(hit):** 캐시에 값 있음 → 빠름, DB 부하 0
- **미스(miss):** 캐시에 없음 → DB 조회 후 적재 → 느림 + DB 부하
- **핵심:** 캐시 키가 **적을수록 적중률↑**, 파라미터로 **잘게 쪼갤수록 적중률↓**

---

## 2. 현재 캐시 구조 (이미 깔린 것)

질문의 "캐시 추가" = 아래 **서버 Redis 층 추가**를 의미. 브라우저 층은 이미 존재.

| 층 | 구현 | 대상 | TTL |
|----|------|------|-----|
| 브라우저 ① | `json-list-cache.js` (`$.ajax` 래핑) | `dataSource.*`, `selectSessionCodeList`, `systemMapper.*` | 기본 1분 / 일부 30분 |
| 브라우저 ② | `body-script.js` `dsCache` (localStorage+BroadcastChannel) | `dataSource.*` 만 | 30분 |
| 서버 | Redis `@Cacheable` | **공통코드·사용자목록·이미지정보만** (이 8개는 미적용) | everyHour(1시간) |

→ **8개 항목은 브라우저 캐시는 되지만 서버 Redis는 아직 안 됨.** 서버 캐시의 추가 이득은 속도보다 **다사용자 DB 부하 분산**.

---

## 3. 항목별 Redis 캐시 분석

| 항목(한글) | 테이블 / 조건 | 파라미터 | 캐시 이득 | 주요 개악 |
|------------|---------------|----------|-----------|-----------|
| getBusinessCompanyList (거래처) | TBL_COMPANY, FAMILY='Y' | systemId | 키 1개, 적중률 최상 | 거래처 자주 추가 시 stale |
| getOrderCompanyList (발주처) | TBL_COMPANY, ORDER='Y' | systemId + (CHARGE_USER_ID) | 적중률 좋음 | 담당자별 키 증가, 배정변경 stale |
| getCompanyStaffList (담당자) | TBL_COMPANY+STAFF | systemId + (COMP_CD) | — | **키 카디널리티 폭증**, 변경잦음, 무효화 까다로움 |
| 외주처 3종 (+팝업) | TBL_COMPANY+TYPE (Process/Pop은 +TBL_CODE EXISTS) | systemId (+POP_POSITION) | **쿼리 무거워 절감 최대** | 코드체계 변경 시 옛 분류 캐싱 |
| getEquipList (설비) | TBL_EQUIP 단일 | systemId | 단순+무효화 훅 이미 존재 | 서버 evict 누락 시 미반영 |
| getLocationListWithWarehouse (창고) | TBL_WAREHOUSE_LOCATION | systemId + (WAREHOUSE_CD) | 거의 불변, 적중률 좋음 | 위치 추가 시 stale |
| selectCompList | TBL_COMPANY 전체 | **SEL_SYSTEM_ID**(admin) | — | 결과셋 큼, 관리화면이라 stale 체감 |
| selectSystemList | TBL_SYSTEM | 없음(전역) | **거의 불변·키 1개, 위험 0** | 거의 없음 |

> 괄호 파라미터 = 선택(동적). *(변경 빈도 관련 서술은 추론)*

---

## 4. Evict를 변경 지점마다 다 걸어도 남는 부작용

| # | 부작용 | 핵심 | 성격 |
|---|--------|------|------|
| ① | 쓰기 경로 누락 | 배치·직접 UPDATE·DB 수동수정은 evict 안 탐 → 조용히 stale | 전제 충족 문제 |
| ② | **클라 1분 시차** | 서버 즉시 비워도 브라우저 캐시는 남음 → 다른 사용자 최대 1분 옛 목록 | 구조상 잔존 |
| ③ | **타입 변형(서버 Redis만)** | JSON 직렬화 round-trip서 숫자 CODE_CD 타입 변할 수 있음 → 프론트 `===` 어긋남 | 구조상 잔존 |
| ④ | **키 딜레마** | 잘게 쪼갠 키는 정밀 evict 어려움 → 통째 비우면 적중률 급락 | 구조상 잔존 |
| ⑤ | 커밋 vs evict 타이밍 | 커밋 전 evict 시 옛 값 재캐싱 → 또 stale | 전제 충족 문제 |
| ⑥ | Redis 의존 | 장애·지연 영향 확대(폴백 없으면 조회 실패 전파) | 캐시 기본 비용 |

> ③ 보충: 같은 행에 `CAST(..AS CHAR) AS value`=문자열, `COMP_CD AS CODE_CD`(CAST 없음)=숫자로 이원화. 직렬화기=`GenericJackson2JsonRedisSerializer`. **클라이언트 캐시는 JS 객체 그대로 저장하므로 해당 없음** — 서버 Redis 도입 시 새로 생기는 위험. *(JDBC 숫자 매핑은 추론)*
>
> **진짜 신경 쓸 건 ②·③·④.** ①·⑤는 "evict를 제대로 걸었나"의 문제, ⑥은 일반 비용.

---

## 5. 추천 — "전부"가 아니라 선별 추가

| 등급 | 항목 | 이유 |
|------|------|------|
| ✅ 추가 추천 | selectSystemList | 거의 불변·키 1개, 위험 0 |
| ✅ 추가 추천 | getEquipList | 단순 + 무효화 훅(`fnClearDataSourceCache`) 이미 존재 |
| ✅ 추가 추천 | 외주처 3종 | EXISTS 서브쿼리로 무거움 → 다사용자 DB 절감 최대 |
| 🔸 조건부 | 거래처·발주처·창고 | 좋은 후보, 단 변경 시 evict 확실히 |
| ⚠️ 후순위 | getCompanyStaffList | COMP_CD별 키 쪼개짐 → 적중률 낮고 무효화 까다로움 |
| ⚠️ 후순위 | selectCompList | 관리화면 stale 체감 → 짧은 TTL 권장 |

**한 줄 요약**
- 무겁거나(외주처) 거의 안 변하는(시스템·설비) 쿼리 → **추가**
- 키가 잘게 쪼개지는(담당자) 건 효과 작고 손 많이 감 → **후순위**
- 이미 브라우저 1분~30분 캐시가 있으니, 가벼운 단일테이블 쿼리는 서버 캐시까지 안 넣어도 됨

---

## 6. (참고) 동료 PR과의 관계 — 영향 없음

- 그 PR(`g_code`·`common.selectCodeList` localStorage 적재)은 **브라우저 캐시 층** → 이 분석(서버 Redis)과 **다른 층, 독립**.
- PR 적용 여부와 무관하게 위 분석·추천은 그대로 유효.
- 참고: 해당 PR 커밋(`d5a94ee`,`7809da1`)은 **현재 로컬 저장소엔 미적용**(이전 작업 `b0270a1`만 존재).
